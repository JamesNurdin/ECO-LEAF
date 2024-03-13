import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from src.extendedLeaf.events import EventDomain
from src.extendedLeaf.power import PowerDomain, PowerMeter
import tkinter as tk
ExperimentResults = Dict[str, Tuple[pd.DataFrame, pd.DataFrame]]


def base_figure(fig: go.Figure = None) -> go.Figure:
    if not fig:
        fig = go.Figure()
    fig.update_layout(template="plotly_white",
                      legend_orientation="h",
                      legend=dict(x=0, y=1.1),
                      xaxis=dict(mirror=True, linewidth=1, linecolor='black', ticks='', showline=True),
                      yaxis=dict(mirror=True, linewidth=1, linecolor='black', ticks='', showline=True))
    return fig


def timeline_figure(fig: go.Figure = None) -> go.Figure:
    fig = base_figure(fig)
    fig.update_yaxes(
        rangemode="nonnegative",
    )
    fig.update_layout(
        height=370,
        width=500,
        font=dict(size=9),
        legend=dict(x=0, y=1.16),
    )
    return fig

def subplot_figure():
    fig = timeline_figure(go.Figure())
    fig.update_layout(
        height=320,
        width=1000,
        font=dict(size=9),
        legend=dict(x=0, y=1.215),
    )
    fig.update_yaxes(title_text=None)

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    return fig

class FileHandler:

    def __init__(self):
        self.creation_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = None
        main_module_name = sys.argv[0]
        self.filename = os.path.basename(main_module_name)[:-3]
        self.repeated_files = 0
        self.repeated_figures = 0

    def create_results_dir(self) -> str:
        """ Creates a directory for the results. """
        results_dir = self.get_results_dir()
        dir_name = f"{self.filename}_{self.creation_time}"
        absolute_path = os.path.join(results_dir, dir_name)
        if os.path.exists(absolute_path):
            return absolute_path
        os.makedirs(absolute_path)
        return absolute_path

    def get_results_dir(self) -> str:
        """ Returns the filepath to the results' directory. """
        current_script_path = os.path.abspath(__file__)
        target_directory = "src"
        dir_path = current_script_path

        while not dir_path.endswith(target_directory):
            dir_path = os.path.dirname(dir_path)
        filepath = os.path.join(dir_path, "results")
        return filepath

    def write_out_results(self, power_domain: PowerDomain, dir_path: str = None, filename: str = "output"):
        """ Allows user to write raw data to file, allows for a desired filepath and filename
            if either are absent the missing aspects are defaulted, """
        if self.results_dir is None:
            self.results_dir = self.create_results_dir()
        if not self.is_valid_filename(filename):
            filename = "output_" + str(self.repeated_files)
            self.repeated_files = self.repeated_files + 1

        if dir_path is None or not os.path.exists(dir_path):
            dir_path = self.results_dir

        filepath = os.path.join(dir_path, f"{filename}.json",)

        # Convert dictionary to JSON format
        json_data = json.dumps(power_domain.captured_data, indent=2)
        import csv

        # Write JSON data to a file
        with open(filepath, 'w') as json_file:
            json_file.write(json_data)
        return filepath, json_data

    def is_valid_filename(self, filename):
        pattern = re.compile(r'^[a-zA-Z0-9_-]+(?!\.)$')
        return bool(pattern.match(filename))

    def write_figure_to_file(self, figure, number_of_figs, filename="figure"):
        # Set the size of the PDF dynamically based on the number of plots
        pdf_height = 300 + (100 * number_of_figs)  # Adjust the multiplier as needed
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        root.destroy()
        pdf_width = screen_width
        if not self.is_valid_filename(filename):
            filename = "figure_" + str(self.repeated_figures)
            self.repeated_figures = self.repeated_figures + 1
        # Create and save the figure as a PDF
        figure.update_layout(height=pdf_height, width=pdf_width)
        figure.update_layout(showlegend=True)
        if self.results_dir is None:
            self.results_dir = self.create_results_dir()
        if os.path.exists(self.results_dir):
            figure.write_image(os.path.join(self.results_dir, f"{filename}.pdf"), "pdf")


class FigurePlotter:
    def __init__(self, power_domain: PowerDomain = None, event_domain: EventDomain = None, show_event_lines=False,
                 number_of_divisions: int = 6, title=""):
        if power_domain is None:
            raise ValueError(f"Error: No power domain was provided.")
        else:
            self.power_domain = power_domain
        if event_domain is None:
            self.event_domain = None
            if show_event_lines is True:
                raise ValueError(f"Error: No event domain was provided.")
            else:
                self.show_event_lines = False
        else:
            self.event_domain = event_domain
            self.events = self.event_domain.event_history
            self.show_event_lines = show_event_lines
            if self.show_event_lines:
                if event_domain.event_history:
                    self.unique_event_times = self.get_unique_event_times(self.events)
                    self.unique_events = self.get_unique_events(self.events)
                else:
                    raise AttributeError(f"Error: No event history was provided in event domain.")
        self.number_of_divisions = number_of_divisions
        self.title = title

    def get_unique_events(self, events) -> dict:
        sorted_events = {}
        for event in events:
            event_name = f"{event.event.__name__}({', '.join(arg.name if hasattr(arg, 'name') else 'arg' for arg in event.args)})"
            if event_name in sorted_events.keys():
                sorted_events[event_name].append(event)
            else:
                sorted_events[event_name] = [event]
        return sorted_events

    def get_unique_event_times(self, events) -> dict:
        event_times = {}
        for event in events:
            event_time = event.time_int
            if event_time in event_times.keys():
                event_times[event_time].append(event)
            else:
                event_times[event_time] = [event]
        return event_times
    @classmethod
    def aggregate_subplots(cls, plots, title="") -> go.Figure:
        # Create a subplot with one column and as many rows as the number of plots
        main_fig = make_subplots(rows=len(plots),
                                 cols=1,
                                 subplot_titles=[fig.layout.title.text for fig in plots],
                                 shared_xaxes=True)
        # Iterate through the plots and add traces to the main subplot
        for plot_index, (plot, layout) in enumerate(zip(plots, [fig.layout for fig in plots])):
            figure_data = plot.to_dict()['data']
            # Add traces to the main subplot
            for trace in figure_data:
                main_fig.add_trace(trace, row=plot_index + 1, col=1)

            main_fig.update_xaxes(title_text=layout.xaxis.title.text, row=plot_index+1, col=1)
            main_fig.update_yaxes(title_text=layout.yaxis.title.text, row=plot_index+1, col=1)
            xaxis_ticks = layout.xaxis.tickvals
            xaxis_ticktext = layout.xaxis.ticktext

            main_fig.update_xaxes(tickvals=xaxis_ticks, ticktext=xaxis_ticktext, row=plot_index+1, col=1)
            for shape in layout.shapes:
                main_fig.add_shape(shape, row=plot_index+1, col=1)

            main_fig.update_layout(title_text=title)
        return main_fig

    def add_events_updated(self, fig, offset) -> go.Figure:
        for name, unique_events in self.unique_events.items():
            x_values = []
            middle_value = 0
            y_values = []
            scaling_factor = 0.3
            for event in unique_events:
                event_time = event.time_int
                x_values.append(event_time - offset)
                if len(self.unique_event_times[event_time]) == 1:
                    y_values.append(middle_value)
                else:
                    total_events = len(self.unique_event_times[event_time])
                    index = self.unique_event_times[event_time].index(event)
                    normalized_index = (index + 0.5) / total_events * scaling_factor
                    y_values.append(middle_value - (normalized_index - 0.5* scaling_factor))

            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                marker=dict(size=5),
                name=name)
                )
        return fig

    def add_events(self, fig, offset) -> go.Figure:
        max_y = 0
        for data in fig.data:
            if max(data.y) > max_y:
                max_y = max(data.y)

        for name, unique_events in self.unique_events.items():
            x_values = [event_time.time_int - offset for event_time in unique_events]
            middle_value = max_y / 2
            y_values = [middle_value for i in range(len(unique_events))]
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                marker=dict(size=5),
                name=name)
            )

        return fig

    def add_event_lines(self, fig, offset):
        if self.show_event_lines:
            if self.show_event_lines:
                for time, events in self.unique_event_times.items():
                    time_x_value = events[0].time_int
                    fig.add_vrect(
                        x0=time_x_value - offset,
                        x1=time_x_value - offset,
                        xref='x',
                        fillcolor="red", opacity=0.3,
                        layer="above", line_width=1,
                        row="all"
                    )
        return fig

    def subplot_events(self, events) -> go.Figure:

        fig = subplot_figure()
        keys = self.power_domain.captured_data.keys()
        start_time = int(list(keys)[0])
        end_time = int(list(keys)[-1])
        if end_time < start_time:
            end_time += 1440
        offset = start_time

        fig = self.add_events_updated(fig, offset)

        fig = self.add_event_lines(fig, offset)

        fig.update_layout(
            showlegend=True,
            xaxis=dict(
                title=dict(text="Time", standoff=0),
                ticktext=[self.power_domain.convert_to_time_string(int(value)) for value in
                          np.linspace((start_time), end_time, self.number_of_divisions)],
                tickvals=[int(value) - offset for value in np.linspace(start_time, end_time-1, self.number_of_divisions)]),
        )

        fig.update_layout(
            title_text=f"Timeseries of events.",
            title_x=0.5,
            title_font=dict(size=16),
        )
        return fig

    def subplot_time_series_entities(self, captured_attribute="Carbon Released",
                                     entities=None, axis_label="Carbon Released (gC02/kWh)",
                                     title_attribute="Carbon Released",
                                     title=None) -> go.Figure:
        if title is None:
            title = f"Timeseries of {title_attribute} for Powered Infrastructure."
        if entities is None:
            raise ValueError(f"Error: No entities provided to plot.")

        fig = subplot_figure()

        keys = self.power_domain.captured_data.keys()
        start_time = int(list(keys)[0])
        end_time = int(list(keys)[-1])
        if end_time < start_time:
            end_time += 1440
        offset = start_time
        data = self.retrieve_select_data_entities(self.power_domain.captured_data, entities)
        time = list(range(end_time-start_time))

        for node_index, node in enumerate(data.keys()):
            x = time
            y = data[node][captured_attribute]

            fig.add_trace(go.Scatter(x=x, y=y, name=f"{node}", line=dict(width=1)))

        fig = self.add_event_lines(fig, offset)

        fig.update_layout(
            showlegend=True,
            xaxis=dict(
                title=dict(text="Time", standoff=0),
                ticktext=[self.power_domain.convert_to_time_string(int(value)) for value in np.linspace((start_time), end_time, self.number_of_divisions)],
                tickvals=[int(value) - offset for value in np.linspace(start_time, end_time-1, self.number_of_divisions)]),
            yaxis=dict(
                title=dict(text=axis_label, standoff=0))
        )

        fig.update_layout(
            title_text=title,
            title_x=0.5,
            title_font=dict(size=16),
        )
        return fig

    def subplot_time_series_power_sources(self, captured_attribute="Carbon Released", power_sources=None,
                                          axis_label="Carbon Released (gC02/kWh)",
                                          title_attribute="Carbon Released", title= None) -> go.Figure:
        if title is None:
            title = f"Timeseries Of {title_attribute} For Power Sources."
        if power_sources is None:
            raise ValueError(f"Error: No power sources were provided.")

        fig = subplot_figure()

        keys = self.power_domain.captured_data.keys()
        start_time = int(list(keys)[0])
        end_time = int(list(keys)[-1])
        if end_time < start_time:
            end_time += 1440

        offset = start_time
        data = self.retrieve_select_data_power_sources(self.power_domain.captured_data, power_sources)
        time = list(range(end_time-start_time))

        for node_index, node in enumerate(data.keys()):
            x = time
            y = data[node][captured_attribute]
            fig.add_trace(go.Scatter(x=x, y=y, name=f"{node}", line=dict(width=1)))

        fig = self.add_event_lines(fig, offset)

        fig.update_layout(
            showlegend=True,
            xaxis=dict(
                title=dict(text="Time", standoff=0),
                ticktext=[self.power_domain.convert_to_time_string(int(value)) for value in np.linspace((start_time), end_time, self.number_of_divisions)],
                tickvals=[int(value) - offset for value in np.linspace(start_time, end_time-1, self.number_of_divisions)]),
            yaxis=dict(
                title=dict(text=axis_label, standoff=0))
        )

        fig.update_layout(
            title_text= title,
            title_x=0.5,
            title_font=dict(size=16),
        )
        return fig

    def subplot_time_series_power_meter(self, power_meters: [PowerMeter]) -> go.Figure:
        if power_meters is None:
            raise ValueError(f"Error, no power meter was provided")

        fig = subplot_figure()

        keys = self.power_domain.captured_data.keys()
        start_time = int(list(keys)[0])
        end_time = int(list(keys)[-1])
        if end_time < start_time:
            end_time += 1440

        offset = start_time

        for power_meter in power_meters:
            y = [float(measurement) for measurement in power_meter.measurements[1:-1]]
            x = list(range(end_time-start_time))
            fig.add_trace(go.Scatter(x=x, y=y, name=f"{power_meter.name}", line=dict(width=1)))

        fig = self.add_event_lines(fig, offset)

        fig.update_layout(
            showlegend=True,
            xaxis=dict(
                title=dict(text="Time", standoff=0),
                ticktext=[self.power_domain.convert_to_time_string(int(value)) for value in np.linspace((start_time), end_time, self.number_of_divisions)],
                tickvals=[int(value) - offset for value in np.linspace(start_time, end_time-1, self.number_of_divisions)]),
            yaxis=dict(
                title=dict(text="Energy Used (Wh)", standoff=0))
        )

        fig.update_layout(
            title_text=f"Timeseries of power used for Power Meters.",
            title_x=0.5,
            title_font=dict(size=16),
        )
        return fig

    def retrieve_select_data_entities(self, time_series, desired_nodes: ["Node"]):
        nodes = {}
        for node in desired_nodes:
            if node is not None:
                nodes[node.name] = {"Power Used": [None] * len(list(time_series.keys())),
                                    "Carbon Intensity": [None] * len(list(time_series.keys())),
                                    "Carbon Released": [None] * len(list(time_series.keys())),
                                    "Total Carbon Released": [None] * len(list(time_series.keys()))}
        for time_index, (time, power_sources) in enumerate(time_series.items()):
            for power_source_index, power_source in enumerate(power_sources):
                for node_index, node in enumerate(power_sources[power_source]):
                    if node in list(nodes.keys()):
                        for attribute_index, (attribute, values) in enumerate(
                                power_sources[power_source][node].items()):

                            nodes[node][attribute][time_index] = values
        return nodes

    def retrieve_select_data_power_sources(self, time_series, desired_power_sources: ["PowerSource"]):
        power_source_results = {}
        for power_source in desired_power_sources:
            if power_source is not None:
                power_source_results[power_source.name] = {"Power Used": [None] * len(list(time_series.keys())),
                                    "Carbon Intensity": [power_source.get_carbon_intensity_at_time(time) for time in range(len(list(time_series.keys())))],
                                    "Power Available": [None] * len(list(time_series.keys())),
                                    "Carbon Released": [None] * len(list(time_series.keys())),
                                    "Total Carbon Released": [None] * len(list(time_series.keys()))}
        running_carbon_released_totals = [0] * len(list(power_source_results.keys()))
        for time_index, (time, power_sources) in enumerate(time_series.items()):
            for power_source_index, power_source in enumerate(power_sources):
                if power_source in list(power_source_results.keys()):
                    power_used: float = 0
                    carbon_released: float = 0
                    for node_index, node in enumerate(power_sources[power_source]):
                        if node != "Total Carbon Released" and node != "Power Available":
                            power_used = power_used + power_sources[power_source][node]["Power Used"]
                            carbon_released = carbon_released + power_sources[power_source][node]["Carbon Released"]
                    power_source_results[power_source]["Power Used"][time_index] = power_used
                    power_source_results[power_source]["Carbon Released"][time_index] = carbon_released
                    if power_source_index in running_carbon_released_totals:
                        running_carbon_released_totals[power_source_index] = running_carbon_released_totals[power_source_index] + carbon_released
                        power_source_results[power_source]["Total Carbon Released"][time_index] = running_carbon_released_totals[power_source_index]
                    power_source_results[power_source]["Power Available"][time_index] = float(power_sources[power_source]["Power Available"])
        return power_source_results
