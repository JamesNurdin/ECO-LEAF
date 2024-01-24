import logging

import simpy

from src.extended_Examples.custom_smart_city_traffic.city import City
from src.extendedLeaf.file_handler import FileHandler
from src.extended_Examples.custom_smart_city_traffic.mobility import MobilityManager
from src.extendedLeaf.infrastructure import Infrastructure

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

    fig1 = file_handler.subplot_time_series_entities("Carbon Released", events=None, entities=city.infrastructure.nodes())
    fig2 = file_handler.subplot_time_series_power_sources("Power Available", events=None,
                                                          power_sources=city.power_domains[0].power_sources)
    main_fig = file_handler.aggregate_subplots([fig1, fig2])
    main_fig.show()

if __name__ == '__main__':
    main()
