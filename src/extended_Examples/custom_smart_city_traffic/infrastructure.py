from typing import List

import simpy

from src.extendedLeaf.application import Application, SourceTask, ProcessingTask, SinkTask
from src.extended_Examples.custom_smart_city_traffic.power import PowerDomain, NodeDistributor, BatteryPower
from src.extended_Examples.custom_smart_city_traffic.settings import *
from src.extendedLeaf.infrastructure import Link, Node
from src.extendedLeaf.power import PowerModelLink, PowerModelNode, PowerMeasurement

"""Counter for incrementally naming nodes"""
_fog_nodes_created = 0
_traffic_lights_created = 0
_taxis_created = 0


class Cloud(Node):
    def __init__(self):
        super().__init__("cloud", cu=CLOUD_CU, power_model=PowerModelNode(power_per_cu=CLOUD_WATT_PER_CU))

    def distribute_training_model_application(self):
        pass
        # select the desired fog nodes to send task


class FogNode(Node):
    def __init__(self, location: "Location"):
        # TODO Shutdown!
        global _fog_nodes_created
        super().__init__(f"fog_{_fog_nodes_created}", cu=FOG_CU,
                         power_model=PowerModelNode(max_power=FOG_MAX_POWER, static_power=FOG_STATIC_POWER),
                         location=location)
        _fog_nodes_created += 1
        self.shutdown = FOG_IDLE_SHUTDOWN

    def measure_power(self) -> PowerMeasurement:
        if self.shutdown:
            return PowerMeasurement(0, 0)
        else:
            return super().measure_power()

    def add_task(self, task: "Task"):
        if self.shutdown:
            self.shutdown = False
        super().add_task(task)

    def remove_task(self, task: "Task"):
        super().remove_task(task)
        if FOG_IDLE_SHUTDOWN and self.used_cu == 0:
            self.shutdown = True

class RechargeStation(Node):
    def __init__(self, location: "Location", application_sink: Node, _recharge_station_counter):
        super().__init__(name=f"Recharge Station {_recharge_station_counter}", location=location,
                         power_model=PowerModelNode(power_per_cu=0, static_power=RECHARGE_STATION_STATIC_POWER))
        self.application = self._create_recharge_station_application(application_sink)

    def _create_recharge_station_application(self, application_sink):
        pass


class TrafficLight(Node):
    def __init__(self, location: "Location", application_sink: Node):
        global _traffic_lights_created
        super().__init__(f"traffic_light_{_traffic_lights_created}", location=location, power_model=PowerModelNode(power_per_cu = 0, static_power=TRAFFIC_LIGHT_STATIC_POWER))
        _traffic_lights_created += 1
        self.application = self._create_cctv_application(application_sink)

    def _create_cctv_application(self, application_sink: Node):
        application = Application()
        source_task = SourceTask(cu=0, bound_node=self)
        application.add_task(source_task)
        processing_task = ProcessingTask(cu=CCTV_PROCESSOR_CU)
        application.add_task(processing_task, incoming_data_flows=[(source_task, CCTV_SOURCE_TO_PROCESSOR_BIT_RATE)])
        sink_task = SinkTask(cu=0, bound_node=application_sink)
        application.add_task(sink_task, incoming_data_flows=[(processing_task, CCTV_PROCESSOR_TO_SINK_BIT_RATE)])
        return application


class Taxi(Node):
    def __init__(self, env: simpy.Environment, mobility_model: "TaxiMobilityModel", application_sinks: List[Node],battery_size):
        global _taxis_created
        super().__init__(f"taxi_{_taxis_created}")
        _taxis_created += 1
        self.env = env
        # self.application = self._create_v2i_application(application_sinks)
        self.mobility_model = mobility_model
        self.power_per_unit_traveled = POWER_PER_UNIT_TRAVELLED
        self.power_domain = PowerDomain(env, name="Power Domain 1", associated_nodes=[self],
                                   start_time_str="19:00:00", update_interval=1, node_distributor=NodeDistributor())
        battery_power = BatteryPower(env, power_domain=self.power_domain, priority=0, total_power_available=TAXI_BATTERY_SIZE)
        self.power_domain.add_power_source(battery_power)

    def power_used(self, distance_traveled, elapsed_time): # distance in meters, time in baseline units of time
        return self.power_per_unit_traveled * distance_traveled * elapsed_time

    @property
    def location(self) -> "Location":
        return self.mobility_model.location(self.env.now)

    @location.setter
    def location(self, value):
        pass  # only for initialization, locations of this node is managed by the TaxiMobilityModel

    def _create_v2i_application(self, application_sinks: List[Node]) -> Application:
        application = Application()
        source_task = SourceTask(cu=0, bound_node=self)
        application.add_task(source_task)
        processing_task = ProcessingTask(cu=V2I_PROCESSOR_CU)
        application.add_task(processing_task, incoming_data_flows=[(source_task, V2I_SOURCE_TO_PROCESSOR_BIT_RATE)])
        for application_sink in application_sinks:
            sink_task = SinkTask(cu=0, bound_node=application_sink)
            application.add_task(sink_task, incoming_data_flows=[(processing_task, V2I_PROCESSOR_TO_SINK_BIT_RATE)])
        return application


class LinkEthernet(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=ETHERNET_BANDWIDTH,
                         latency=ETHERNET_LATENCY,
                         power_model=PowerModelLink(ETHERNET_WATT_PER_BIT))


class LinkWanUp(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WAN_BANDWIDTH,
                         latency=WAN_LATENCY,
                         power_model=PowerModelLink(WAN_WATT_PER_BIT_UP))


class LinkWanDown(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WAN_BANDWIDTH,
                         latency=WAN_LATENCY,
                         power_model=PowerModelLink(WAN_WATT_PER_BIT_DOWN))


class LinkWifiBetweenTrafficLights(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WIFI_BANDWIDTH,
                         latency=WIFI_LATENCY,
                         power_model=PowerModelLink(WIFI_TL_TO_TL_WATT_PER_BIT))


class LinkWifiTaxiToTrafficLight(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WIFI_BANDWIDTH,
                         latency=WIFI_LATENCY,
                         power_model=PowerModelLink(WIFI_TAXI_TO_TL_WATT_PER_BIT))
