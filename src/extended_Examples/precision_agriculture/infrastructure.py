from typing import List

import simpy

from src.extendedLeaf.application import Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.mobility import Location
from src.extended_Examples.precision_agriculture.power import PowerDomain, PoweredInfrastructureDistributor, BatteryPower
from src.extended_Examples.precision_agriculture.settings import *
from src.extendedLeaf.infrastructure import Link, Node
from src.extendedLeaf.power import PowerModelLink, PowerModelNode, PowerMeasurement


class Cloud(Node):
    def __init__(self):
        super().__init__("cloud", cu=CLOUD_CU, power_model=PowerModelNode(power_per_cu=CLOUD_WATT_PER_CU))


class CropSensor(Node):
    def __init__(self, infrastructure, plot, sensor_index, location):
        super().__init__(name=f"{plot.name}_Crop_Sensor_{sensor_index}",
                         cu=SENSOR_CU,
                         power_model=PowerModelNode(max_power=SENSOR_MAX_POWER, static_power=SENSOR_STATIC_POWER),
                         location=location)
        infrastructure.add_node(self)
        cloud = infrastructure.nodes(type_filter=Cloud)[0]
        self.application = self._create_sensor_node_application(cloud)

    def _create_sensor_node_application(self, application_sink) -> Application:
        application = Application()
        source_task = SourceTask(cu=SENSOR_TASK_CU, bound_node=self)
        application.add_task(source_task)
        processing_task = ProcessingTask(cu=FOG_PROCESSOR_CU)
        application.add_task(processing_task, incoming_data_flows=[(source_task, SENSOR_SOURCE_TO_FOG_BIT_RATE)])
        sink_task = SinkTask(cu=0, bound_node=application_sink)
        application.add_task(sink_task, incoming_data_flows=[(processing_task, FOG_TO_CLOUD_BIT_RATE)])
        return application

class FogNode(Node):
    def __init__(self, plot, location):
        super().__init__(name=f"{plot.name}_FogNode",
                         cu=FOG_CU,
                         power_model=PowerModelNode(max_power=FOG_MAX_POWER, static_power=SENSOR_STATIC_POWER),
                         location=location)


class Drone(Node):
    def __init__(self, plot, location, env, power_domain, infrastructure, drone_path):
        super().__init__(name=f"{plot.name}_Drone",
                         cu=DRONE_CU,
                         power_model=PowerModelNode(max_power=DRONE_MAX_POWER, static_power=DRONE_STATIC_POWER),
                         location=location)
        cloud = infrastructure.nodes(type_filter=Cloud)[0]
        self.application = self._create_drone_application(cloud)
        print(self.application)
        self.power_per_unit_traveled = POWER_PER_UNIT_TRAVELLED
        self.battery_power = BatteryPower(env, power_domain=power_domain, priority=1,
                                          total_power_available=TAXI_BATTERY_SIZE)
        power_domain.add_power_source(self.battery_power)
        self.locations_iterator = drone_path

    # TODO properly create application
    def _create_drone_application(self, cloud) -> Application:
        # Initialise three tasks
        source_task = SourceTask(cu=9, bound_node=self)
        processing_task = ProcessingTask(cu=5)
        sink_task = SinkTask(cu=10, bound_node=cloud)
        print(source_task.node)

        # Build Application
        application = Application()
        application.add_task(source_task)
        application.add_task(processing_task, incoming_data_flows=[(source_task, 100)])
        application.add_task(sink_task, incoming_data_flows=[(processing_task, 500)])

        return application



class RechargeStation(Node):
    def __init__(self, location: Location, application_sink: Node, _recharge_station_counter):
        super().__init__(name=f"Recharge Station {_recharge_station_counter}", location=location,
                         power_model=PowerModelNode(power_per_cu=0, static_power=RECHARGE_STATION_STATIC_POWER))
        self.application = self._create_recharge_station_application(application_sink)

    def _create_recharge_station_application(self, application_sink):
        pass

class LinkEthernet(Link):
    def __init__(self, src: Node, dst: Node, name: str):
        super().__init__(src=src,
                         dst=dst,
                         bandwidth=ETHERNET_BANDWIDTH,
                         latency=ETHERNET_LATENCY,
                         power_model=PowerModelLink(ETHERNET_WATT_PER_BIT),
                         name=name)


class LinkWanUp(Link):
    def __init__(self, src: Node, dst: Node, name: str):
        super().__init__(src=src,
                         dst=dst,
                         bandwidth=WAN_BANDWIDTH,
                         latency=WAN_LATENCY,
                         power_model=PowerModelLink(WAN_WATT_PER_BIT_UP),
                         name=name)


class LinkWanDown(Link):
    def __init__(self, src: Node, dst: Node, name: str):
        super().__init__(src=src,
                         dst=dst,
                         bandwidth=WAN_BANDWIDTH,
                         latency=WAN_LATENCY,
                         power_model=PowerModelLink(WAN_WATT_PER_BIT_DOWN),
                         name=name)


class LinkWifiBetweenTrafficLights(Link):
    def __init__(self, src: Node, dst: Node, name: str):
        super().__init__(src=src,
                         dst=dst,
                         bandwidth=WIFI_BANDWIDTH,
                         latency=WIFI_LATENCY,
                         power_model=PowerModelLink(WIFI_TL_TO_TL_WATT_PER_BIT),
                         name=name)


class LinkWifiTaxiToTrafficLight(Link):
    def __init__(self, src: Node, dst: Node, name: str):
        super().__init__(src=src,
                         dst=dst,
                         bandwidth=WIFI_BANDWIDTH,
                         latency=WIFI_LATENCY,
                         power_model=PowerModelLink(WIFI_TAXI_TO_TL_WATT_PER_BIT),
                         name=name)
