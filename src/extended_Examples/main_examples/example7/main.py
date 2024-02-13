import simpy

from src.extendedLeaf.events import EventDomain, PowerDomainEvent
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extended_Examples.main_examples.example7.farm import Farm
from src.extended_Examples.main_examples.example7.mobility import MobilityManager
from src.extended_Examples.main_examples.example7.settings import START_TIME


def main():
    # ----------------- Set up experiment -----------------
    env = simpy.Environment()
    farm = Farm(env)
    farm.run(env)

    # run any drone cycles
    mobility_model = MobilityManager()
    env.process(mobility_model.run(env, farm))

    event_domain = EventDomain(env, update_interval=1, start_time_str=START_TIME)

    event_domain.add_event(
        PowerDomainEvent(event=farm.deploy_sensor_applications, args=[], time_str="12:00:00", repeat=True, repeat_counter= 120))
    event_domain.add_event(
        PowerDomainEvent(event=farm.terminate_sensor_applications, args=[], time_str="13:00:00", repeat=True, repeat_counter= 120))

    env.process(event_domain.run())



    # Run simulation
    env.run(until=2800)  # run simulation for 2 days.

    # Plot results
    file_handler = FileHandler()
    for plot in farm.plots:
        filename = f"Plot_Results_{plot.plot_index}"
        file_handler.write_out_results(filename=filename, power_domain=plot.power_domain)
        figure_plotter = FigurePlotter(plot.power_domain)

        fig1 = figure_plotter.subplot_time_series_entities("Carbon Released", entities=plot.all_entities)
        fig2 = figure_plotter.subplot_time_series_entities("Power Used", entities=plot.all_entities)
        fig3 = figure_plotter.subplot_time_series_power_sources("Power Used", power_sources=plot.power_sources)
        fig4 = figure_plotter.subplot_time_series_power_sources("Power Available", power_sources=plot.power_sources)
        figs = [fig1, fig2, fig3, fig4]
        main_fig = figure_plotter.aggregate_subplots(figs)
        file_handler.write_figure_to_file(main_fig, len(figs), filename)
        main_fig.show()


if __name__ == '__main__':
    main()
