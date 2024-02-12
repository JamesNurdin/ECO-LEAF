import logging
import simpy

from src.extendedLeaf.events import PowerDomainEvent, EventDomain
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extended_Examples.precision_agriculture.farm import Farm
from src.extended_Examples.precision_agriculture.mobility import MobilityManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:\t%(message)s')


def main():
    # ----------------- Set up experiment -----------------
    env = simpy.Environment()
    farm = Farm(env)
    farm.run(env)
    # run any drone cycles
    mobility_model = MobilityManager()

    # Early power meters when exploring isolated power measurements
    for plot in farm.plots:
        env.process(plot.power_domain.run(env))

    env.process(mobility_model.run(env, farm))
    event_domain = EventDomain(env, update_interval=1, start_time_str="15:00:00")

    """event_domain.add_event(
        PowerDomainEvent(event=orchestrator.place, args=[application1], time_str="15:10:00", repeat=False))"""

    # Run simulation
    env.run(until=1400)  # run simulation for 10 seconds

    file_handler = FileHandler()
    for plot in farm.plots:
        filename = f"Plot_Results_{plot.plot_index}"
        file_handler.write_out_results(filename=filename, power_domain=plot.power_domain)
        figure_plotter = FigurePlotter(plot.power_domain)

        fig1 = figure_plotter.subplot_time_series_entities("Carbon Released", entities=plot.all_entities)
        fig2 = figure_plotter.subplot_time_series_power_sources("Power Used", power_sources=plot.power_sources)
        fig3 = figure_plotter.subplot_time_series_power_sources("Power Available", power_sources=plot.power_sources)
        figs = [fig1, fig2, fig3]
        main_fig = figure_plotter.aggregate_subplots(figs)
        file_handler.write_figure_to_file(main_fig, len(figs), filename)
        main_fig.show()


if __name__ == '__main__':
    main()
