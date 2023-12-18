import logging

import simpy

from src.extendedLeaf.power import EntityDistributor
from src.extended_Examples.custom_smart_city_traffic.city import City
from src.extended_Examples.custom_smart_city_traffic.file_handler import FileHandler
from src.extended_Examples.custom_smart_city_traffic.infrastructure import Cloud, Taxi, LinkWanDown, LinkWanUp, \
    LinkWifiTaxiToTrafficLight, LinkWifiBetweenTrafficLights, TrafficLight, RechargeStation
from src.extended_Examples.custom_smart_city_traffic.mobility import MobilityManager
from src.extended_Examples.custom_smart_city_traffic.settings import POWER_MEASUREMENT_INTERVAL
from src.extendedLeaf.infrastructure import Infrastructure
from src.extended_Examples.custom_smart_city_traffic.power import PowerMeter, PowerDomain, SolarPower, GridPower, \
    BatteryPower


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:\t%(message)s')


def main():
    # ----------------- Set up experiment -----------------
    env = simpy.Environment()
    city = City(env)
    for power_domain in city.power_domains:
        env.process(power_domain.run(env))
    mobility_manager = MobilityManager(city)
    env.process(mobility_manager.run(env))
    env.run(until=360)
    print(city.power_domains[0].power_sources)
    file_handler = FileHandler(city.power_domains[0])
    file_handler.time_series_entities("Carbon Released", events=None, entities=city.infrastructure.nodes())
    file_handler.time_series_power_sources("Power Available", events=None,
                                           power_sources=city.power_domains[0].power_sources)


if __name__ == '__main__':
    main()
