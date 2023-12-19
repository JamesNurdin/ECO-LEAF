import logging

import simpy

from src.extendedLeaf.power import EntityDistributor
from src.extended_Examples.custom_smart_city_traffic.city import City
from src.extendedLeaf.file_handler import FileHandler
from src.extended_Examples.precision_agriculture.infrastructure import Cloud, Taxi, LinkWanDown, LinkWanUp, \
    LinkWifiTaxiToTrafficLight, LinkWifiBetweenTrafficLights, TrafficLight, RechargeStation
from src.extended_Examples.precision_agriculture.mobility import MobilityManager
from src.extended_Examples.precision_agriculture.settings import POWER_MEASUREMENT_INTERVAL
from src.extendedLeaf.infrastructure import Infrastructure
from src.extended_Examples.precision_agriculture.power import PowerMeter, PowerDomain, SolarPower, GridPower, \
    BatteryPower
from src.extended_Examples.precision_agriculture.farm import Farm

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:\t%(message)s')


def main():
    # ----------------- Set up experiment -----------------
    env = simpy.Environment()
    farm = Farm(env)
    #env.process(farm.run(env))
    mobility_manager = MobilityManager(farm)
    env.process(mobility_manager.run(env))
    file_reader = FileHandler()
    #env.run(until=360)


if __name__ == '__main__':
    main()
