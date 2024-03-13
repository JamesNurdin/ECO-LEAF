import simpy

from src.extendedLeaf.events import EventDomain, Event
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extended_Examples.main_examples.example7.farm import Farm
from src.extended_Examples.main_examples.example7.mobility import MobilityManager
from src.extended_Examples.main_examples.example7.settings import START_TIME


def main():
    """
    Printed Output:
        Plot_1 Total carbon emitted: 47.513345375535216 gCo2
        Plot_2 Total carbon emitted: 93.50254168220009 gCo2
        Plot_3 Total carbon emitted: 35.18273642840013 gCo2
        Plot_4 Total carbon emitted: 4.856636146666527 gCo2
    """
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
    env.run(until=2800)  # run simulation for 2 days.

    # Plot results
    total_carbon_consumed_list = []
    file_handler = FileHandler()
    for plot in farm.plots:
        filename = f"Plot_Results_{plot.plot_index}"
        file_handler.write_out_results(filename=filename, power_domain=plot.power_domain)
        figure_plotter = FigurePlotter(plot.power_domain,event_domain, show_event_lines=True)

        fig0 = figure_plotter.subplot_events(event_domain.event_history)
        fig1 = figure_plotter.subplot_time_series_entities("Carbon Released",
                                                           entities=plot.all_entities,
                                                           axis_label="Carbon Released (gC02eq/kWh)",
                                                           title_attribute="Carbon Released")
        fig2 = figure_plotter.subplot_time_series_entities("Power Used",
                                                           entities=plot.all_entities,
                                                           axis_label="Energy Consumed (Wh)",
                                                           title_attribute="Energy Consumed")
        fig3 = figure_plotter.subplot_time_series_power_sources("Power Used",
                                                                power_sources=plot.power_sources,
                                                                axis_label="Energy Consumed (Wh)",
                                                                title_attribute="Energy Consumed")
        fig4 = figure_plotter.subplot_time_series_power_sources("Carbon Released",
                                                                power_sources=plot.power_sources,
                                                                axis_label="Carbon Released (gC02eq/kWh)",
                                                                title_attribute="Carbon Released")
        fig5 = figure_plotter.subplot_time_series_power_sources("Power Available",
                                                                power_sources=plot.power_sources,
                                                                axis_label="Energy Available (Wh)",
                                                                title_attribute="Energy Available")

        fig6 = figure_plotter.subplot_time_series_power_sources("Total Carbon Released",
                                                                power_sources=plot.power_sources,
                                                                axis_label="(gC02/kWh)",
                                                                title_attribute=f"Total Carbon Released",
                                                                title=f"Plot {plot.plot_index+1} Timeseries for Total Carbon Released.")

        figs = [fig0, fig1, fig2, fig3, fig4, fig5]
        for i, fig in enumerate(figs):
            main_fig = FigurePlotter.aggregate_subplots([fig], title="")
            file_handler.write_figure_to_file(main_fig, 1, filename=f"example_pd{plot.plot_index}_7-{i}")

        total_carbon_consumed_list.append(fig6)
        print(f"{plot.name} Total carbon emitted: {plot.power_domain.return_total_carbon_emissions()} gCo2eq")

        main_fig = FigurePlotter.aggregate_subplots(figs, title="General Results for Scenario 7.")
        file_handler.write_figure_to_file(main_fig, len(figs), filename=f"plot{plot.plot_index}")

    main_fig = FigurePlotter.aggregate_subplots(total_carbon_consumed_list, title="Summative Graphs for Example 7.")
    file_handler.write_figure_to_file(main_fig, len(total_carbon_consumed_list), filename=f"Main_results")


    #total_carbon_consumed_figures = FigurePlotter.aggregate_subplots(total_carbon_consumed_list, title="Graph Showing Carbon Released For Power Sources.")
    #file_handler.write_figure_to_file(total_carbon_consumed_figures, len(total_carbon_consumed_list), filename="total_carbon_results")
    #total_carbon_consumed_figures.show()





if __name__ == '__main__':
    main()
