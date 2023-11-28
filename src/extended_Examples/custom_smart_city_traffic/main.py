import logging

import simpy

from extendedLeaf.power import NodeDistributor
from extended_Examples.custom_smart_city_traffic.city import City
from extended_Examples.custom_smart_city_traffic.infrastructure import Cloud, FogNode, Taxi, LinkWanDown, LinkWanUp, \
    LinkWifiTaxiToTrafficLight, LinkWifiBetweenTrafficLights, TrafficLight
from extended_Examples.custom_smart_city_traffic.mobility import MobilityManager
from extended_Examples.custom_smart_city_traffic.settings import POWER_MEASUREMENT_INTERVAL
from extendedLeaf.infrastructure import Infrastructure
from extended_Examples.custom_smart_city_traffic.power import PowerMeter, PowerDomain, SolarPower, GridPower, \
    BatteryPower

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:\t%(message)s')


def main(count_taxis: bool, measure_infrastructure: bool, measure_applications: bool):
    # ----------------- Set up experiment -----------------
    env = simpy.Environment()
    city = City(env)
    mobility_manager = MobilityManager(city)
    env.process(mobility_manager.run(env))

    power_domain = PowerDomain(env, name="Traffic Light Power Domain", associated_nodes=city.infrastructure.nodes(type_filter=TrafficLight),
                               start_time_str="12:00:00",
                               update_interval=1)
    power_domain2 = PowerDomain(env, name="Taxi Power Domain",
                               associated_nodes=city.infrastructure.nodes(type_filter=TrafficLight),
                               start_time_str="12:00:00",
                               update_interval=1)
    grid_power = GridPower(env, power_domain=power_domain,
                           data_set_filename="08-08-2023 national carbon intensity.csv", priority=5)

    for counter in range(len(city.infrastructure.nodes(type_filter=Taxi))):
        taxi = city.infrastructure.nodes(type_filter=TrafficLight)[counter]
        car_battery = BatteryPower(env, name=f"Taxi{counter} Battery", power_domain=power_domain,
                                   priority=5, nodes_being_powered=taxi)
        #env.process(car_battery.run(env,power_domain.update_interval))
    power_domain.add_power_source(grid_power)

    # ----------------- Initialize meters -----------------
    if count_taxis:
        # Measures the amount of taxis on the map
        taxi_counter = TaxiCounter(env, city.infrastructure)
    if measure_infrastructure:
        # Measures the power usage of cloud and fog nodes as well as WAN and WiFi links
        pm_cloud = PowerMeter(entities=city.infrastructure.nodes(type_filter=Cloud), name="cloud", measurement_interval=POWER_MEASUREMENT_INTERVAL)
        pm_fog = PowerMeter(entities=city.infrastructure.nodes(type_filter=FogNode), name="fog", measurement_interval=POWER_MEASUREMENT_INTERVAL)
        pm_wan_up = PowerMeter(entities=city.infrastructure.links(type_filter=LinkWanUp), name="wan_up", measurement_interval=POWER_MEASUREMENT_INTERVAL)
        pm_wan_down = PowerMeter(entities=city.infrastructure.links(type_filter=LinkWanDown), name="wan_down", measurement_interval=POWER_MEASUREMENT_INTERVAL)
        pm_wifi = PowerMeter(entities=lambda: city.infrastructure.links(type_filter=(LinkWifiBetweenTrafficLights, LinkWifiTaxiToTrafficLight)), name="wifi", measurement_interval=POWER_MEASUREMENT_INTERVAL)

        env.process(pm_cloud.run(env))
        env.process(pm_fog.run(env))
        env.process(pm_wan_up.run(env))
        env.process(pm_wan_down.run(env))
        env.process(pm_wifi.run(env))
        env.process(power_domain.run(env))  # registering power metering process 2

    if measure_applications:
        # Measures the power usage of the V2I and CCTV applications
        pm_v2i = PowerMeter(entities=lambda: [taxi.application for taxi in city.infrastructure.nodes(type_filter=Taxi)], name="v2i", measurement_interval=POWER_MEASUREMENT_INTERVAL)
        pm_cctv = PowerMeter(entities=lambda: [tl.application for tl in city.infrastructure.nodes(type_filter=TrafficLight)], name="cctv", measurement_interval=POWER_MEASUREMENT_INTERVAL)
        env.process(pm_v2i.run(env))
        env.process(pm_cctv.run(env))

    # ------------------ Run experiment -------------------
    env.run(until=360)
    logger.info(f"Total carbon emitted for {power_domain.name}: {power_domain.return_total_carbon_emissions()} gCo2")

class TaxiCounter:
    def __init__(self, env: simpy.Environment, infrastructure: Infrastructure):
        self.env = env
        self.measurements = []
        self.process = env.process(self._run(infrastructure))

    def _run(self, infrastructure: Infrastructure):
        yield self.env.timeout(0.01)
        while True:
            self.measurements.append(len(infrastructure.nodes(type_filter=Taxi)))
            yield self.env.timeout(1)


if __name__ == '__main__':
    main(count_taxis=True, measure_infrastructure=True, measure_applications=True)
