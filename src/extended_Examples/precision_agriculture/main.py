import logging

import simpy

from src.extendedLeaf.application import Application
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import EntityDistributor
from src.extended_Examples.custom_smart_city_traffic.city import City
from src.extendedLeaf.file_handler import FileHandler
from src.extended_Examples.precision_agriculture.application import ProcessingTask
from src.extended_Examples.precision_agriculture.infrastructure import Cloud, LinkWanDown, LinkWanUp, \
    LinkWifiTaxiToTrafficLight, LinkWifiBetweenTrafficLights, RechargeStation
from src.extended_Examples.precision_agriculture.mobility import MobilityManager
from src.extended_Examples.precision_agriculture.orchestrator import FarmOrchestrator
from src.extended_Examples.precision_agriculture.settings import POWER_MEASUREMENT_INTERVAL, FOG_UTILIZATION_THRESHOLD
from src.extendedLeaf.infrastructure import Infrastructure, Node
from src.extended_Examples.precision_agriculture.power import PowerMeter, PowerDomain, SolarPower, GridPower, \
    BatteryPower
from src.extended_Examples.precision_agriculture.farm import Farm

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:\t%(message)s')


def main():
    # ----------------- Set up experiment -----------------
    env = simpy.Environment()
    farm = Farm(env)
    farm.run(env)

    # Early power meters when exploring isolated power measurements
    for plot in farm.plots:
        env.process(plot.power_domain.run(env))  # registering power metering process 2

    # Run simulation
    env.run(until=121)  # run simulation for 10 seconds
    for plot in farm.plots:
        file_handler = FileHandler()
        filename = f"Results_{plot.plot_index}.Json"
        file_handler.write_out_results(filename=filename, power_domain=plot.power_domain)

        fig1 = file_handler.subplot_time_series_entities(plot.power_domain, "Carbon Released", events=None,
                                                         entities=plot.all_entities)
        fig2 = file_handler.subplot_time_series_power_sources(plot.power_domain, "Power Used", events=None,
                                                              power_sources=plot.power_sources)
        fig3 = file_handler.subplot_time_series_power_sources(plot.power_domain, "Power Available", events=None,
                                                              power_sources=plot.power_sources)
        figs = [fig1, fig2, fig3]
        main_fig = file_handler.aggregate_subplots(figs)
        file_handler.write_figure_to_file(main_fig, len(figs))
        main_fig.show()

    #env.run(until=360)

if __name__ == '__main__':
    main()
