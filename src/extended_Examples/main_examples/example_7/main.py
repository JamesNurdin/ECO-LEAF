import simpy

from src.extendedLeaf.events import EventDomain, Event
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extended_Examples.main_examples.example_7.farm import Farm
from src.extended_Examples.main_examples.example_7.mobility import MobilityManager
from src.extended_Examples.main_examples.example_7.settings import START_TIME


def main():
    # ----------------- Set up experiment -----------------
    env = simpy.Environment()
    farm = Farm(env)
    farm.run(env)

    # run any drone cycles
    mobility_model = MobilityManager()

    event_domain = EventDomain(env, update_interval=1, start_time_str=START_TIME)

    event_domain.add_event(
        Event(event=farm.deploy_sensor_applications, args=[], time_str="12:00:00", repeat=True, repeat_counter= 120))
    event_domain.add_event(
        Event(event=farm.terminate_sensor_applications, args=[], time_str="13:00:00", repeat=True, repeat_counter= 120))

    env.process(event_domain.run())
    env.process(mobility_model.run(env, farm))


    # Run simulation
    env.run(until=2880)  # run simulation for 2 days.

    # Plot results
    total_carbon_consumed_list = []
    file_handler = FileHandler()
    for i, plot in enumerate(farm.plots):
        filename = f"Plot_Results_{plot.plot_index}"
        file_handler.write_out_results(filename=filename, power_domain=plot.power_domain)
        figure_plotter = FigurePlotter(plot.power_domain,event_domain, show_event_lines=True)

        fig0 = figure_plotter.subplot_events(event_domain.event_history,
                                             title=f"(7.{i+1}.1) Time Series of Events.")
        fig1 = figure_plotter.subplot_time_series_entities("Power Used",
                                                           entities=plot.all_entities,
                                                           axis_label="Energy Consumed (Wh)",
                                                           title=f"(7.{i+1}.2) Time Series of Energy Consumed for Infrastructure.")
        fig2 = figure_plotter.subplot_time_series_power_sources("Power Used",
                                                                power_sources=plot.power_sources,
                                                                axis_label="Energy Consumed (Wh)",
                                                                title=f"(7.{i+1}.3) Time Series of Energy Provided by Power Sources.")
        fig3 = figure_plotter.subplot_time_series_entities("Carbon Released",
                                                           entities=plot.all_entities,
                                                           axis_label="Carbon Released (gC02eq)",
                                                           title=f"(7.{i+1}.4) Time Series of Carbon Released for Infrastructure.")
        fig4 = figure_plotter.subplot_time_series_power_sources("Carbon Released",
                                                                power_sources=plot.power_sources,
                                                                axis_label="Carbon Released (gC02eq)",
                                                                title=f"(7.{i+1}.5) Time Series of Carbon Released for Power Sources.")
        fig5 = figure_plotter.subplot_time_series_power_sources("Power Available",
                                                                power_sources=plot.power_sources,
                                                                axis_label="Energy Available (Wh)",
                                                                title=f"(7.{i+1}.2) Time Series of Power Available for Power Sources.")
        fig6 = figure_plotter.subplot_time_series_power_sources("Total Carbon Released",
                                                                power_sources=plot.power_sources,
                                                                axis_label="(gC02eq)",
                                                                title_attribute=f"Total Carbon Released",
                                                                title=f"(7.0.{i+1}) Timeseries for Total Carbon Released for Power Sources.")

        figs = [fig0, fig1, fig2, fig3, fig4, fig5]
        for j, fig in enumerate(figs):
            main_fig = FigurePlotter.aggregate_subplots([fig], title="")
            file_handler.write_figure_to_file(main_fig, 1, filename=f"example_pd{plot.plot_index}_7-{j}")

        total_carbon_consumed_list.append(fig6)
        print(f"{plot.name} Total carbon emitted: {plot.power_domain.return_total_carbon_emissions()} gCo2eq")

        main_fig = FigurePlotter.aggregate_subplots(figs, title=f"Results for Scenario 7 Plot {i+1}.")
        file_handler.write_figure_to_file(main_fig, len(figs), filename=f"plot{plot.plot_index}")

    main_fig = FigurePlotter.aggregate_subplots(total_carbon_consumed_list, title="Summative Graphs for Example 7.")
    file_handler.write_figure_to_file(main_fig, len(total_carbon_consumed_list), filename=f"Main_results")


if __name__ == '__main__':
    main()
