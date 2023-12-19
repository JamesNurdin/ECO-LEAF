import json
import os
import re
from datetime import datetime
from typing import Dict, Tuple

import numpy as np
import pandas as pd
# Figure generation libraries
import plotly.graph_objs as go
from plotly.graph_objs import Figure
from plotly.subplots import make_subplots
from src.extendedLeaf.power import PowerDomain

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


def timeline_figure(fig: go.Figure = None, y_axes_title: str = "Power Usage (Watt)") -> go.Figure:
    fig = base_figure(fig)
    fig.update_yaxes(
        title=dict(text=y_axes_title, standoff=0),
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
    def create_results_dir(self) -> str:
        """ Creates a directory for the results. """
        results_dir = self.get_results_dir()
        dir_name = f"{self.creation_time}_results"
        absolute_path = os.path.join(results_dir, dir_name)
        if os.path.exists(absolute_path):
            raise FileExistsError(f"Error: directory {dir_name} exists")
        os.makedirs(absolute_path)
        return absolute_path

    def get_results_dir(self) -> str:
        """ Returns the filepath to the results' directory. """
        current_script_path = os.path.abspath(__file__)
        target_directory = "project-carbon-emissions-estimation-in-edge-cloud-computing-simulations"
        dir_path = current_script_path

        while not dir_path.endswith(target_directory):
            dir_path = os.path.dirname(dir_path)
        filepath = os.path.join(dir_path, "src", "results")
        return filepath

    def write_out_results(self, power_domain: PowerDomain, dir_path: str = None, filename: str = "output.json"):
        """ Allows user to write raw data to file, allows for a desired filepath and filename
            if either are absent the missing aspects are defaulted, """
        if self.results_dir is None:
            self.results_dir = self.create_results_dir()
        if not self.is_valid_filename(filename):
            filename = "output.json"

        if dir_path is None or not os.path.exists(dir_path):
            dir_path = self.results_dir

        filepath = os.path.join(dir_path, filename)

        # Convert dictionary to JSON format
        json_data = json.dumps(power_domain.captured_data, indent=2)

        # Write JSON data to a file
        with open(filepath, 'w') as json_file:
            json_file.write(json_data)
        return filepath, json_data

    def is_valid_filename(self, filename):
        pattern = re.compile(r'^[a-zA-Z0-9_-]+\.json$')
        return bool(pattern.match(filename))

    def write_figure_to_file(self, fig):
        if self.results_dir is None:
            self.results_dir = self.create_results_dir()
        if os.path.exists(self.results_dir):
            fig.write_image(os.path.join(self.results_dir, "fig.pdf"), "pdf")

    def aggregate_subplots(self, plots) -> go.Figure:
        # Create a subplot with one column and as many rows as the number of plots
        main_fig = make_subplots(rows=len(plots), cols=1, subplot_titles=[fig.layout.title.text for fig in plots])

        # Iterate through the plots and add traces to the main subplot
        for plot_index, (plot, layout) in enumerate(zip(plots, [fig.layout for fig in plots])):
            figure_data = plot.to_dict()['data']
            # Add traces to the main subplot
            for trace in figure_data:
                main_fig.add_trace(trace, row=plot_index + 1, col=1,)

            # Update xaxis properties
            main_fig.update_xaxes(title_text=layout.xaxis.title.text, row=plot_index+1, col=1)
            main_fig.update_yaxes(title_text=layout.yaxis.title.text, row=plot_index+1, col=1)
            xaxis_ticks = layout.xaxis.tickvals
            xaxis_ticktext = layout.xaxis.ticktext

            # Apply xaxis tick information to the main subplot
            main_fig.update_xaxes(tickvals=xaxis_ticks, ticktext=xaxis_ticktext, row=plot_index+1, col=1)
            for shape in layout.shapes:
                main_fig.add_shape(shape, row=plot_index+1, col=1)

            # Update layout of the main subplot based on the individual layout of each subplot

        # Update layout of the main subplot
        main_fig.update_layout(title_text="Results:")

        return main_fig
    def subplot_time_series_entities(self, power_domain: PowerDomain, captured_attribute="Carbon Released", events=None, entities=None) -> go.Figure:
        if entities is None:
            entities = power_domain.powered_entities

        global n
        fig = subplot_figure()

        keys = power_domain.captured_data.keys()
        start_time = power_domain.get_current_time(list(keys)[0])
        end_time = power_domain.get_current_time(list(keys)[-1])

        offset = start_time
        time, data = self.retrieve_select_data_entities(power_domain.captured_data, entities)

        # Go through each node and add its trace to the same subplot
        for node_index, node in enumerate(data.keys()):
            x = time
            y = data[node][captured_attribute]
            # Add the trace to the subplot
            fig.add_trace(go.Scatter(x=x, y=y, name=f"{node}", line=dict(width=1)))
            n = 6

        # Update layout and show the figure
        fig.update_layout(
            showlegend=True,
            xaxis=dict(
                title=dict(text="Time", standoff=0),
                ticktext=[power_domain.convert_to_time_string(int(value)) for value in np.linspace((start_time-1), end_time, n)],
                tickvals=[int(value) - offset for value in np.linspace(start_time, end_time, n)]),
            yaxis=dict(
                title=dict(text=captured_attribute, standoff=0))
        )

        # add event lines
        if events is not None:
            for (time, _, (event, args)) in events:
                time_x_value = power_domain.get_current_time(time)
                fig.add_vrect(
                    x0=time_x_value - offset,
                    x1=time_x_value - offset,
                    fillcolor="red", opacity=0.5,
                    layer="above", line_width=1,
                    label=dict(text=f"{event.__name__}({', '.join(arg.name for arg in args)})")
                )
        # Update layout to add a title
        fig.update_layout(
            title_text=f"Timeseries of {captured_attribute} for Entities.",
            title_x=0.5,  # Adjust the horizontal position of the title
            title_font=dict(size=16),  # Adjust the font size of the title
        )
        return fig


    def subplot_time_series_power_sources(self, power_domain: PowerDomain, captured_attribute="Carbon Released", events=None, power_sources=None) -> go.Figure:
        if power_sources is None:
            power_sources = power_domain.power_sources

        global n
        fig = subplot_figure()

        keys = power_domain.captured_data.keys()
        start_time = power_domain.get_current_time(list(keys)[0])
        end_time = power_domain.get_current_time(list(keys)[-1])

        offset = start_time
        time, data = self.retrieve_select_data_power_sources(power_domain.captured_data, power_sources)

        # Go through each node and add its trace to the same subplot
        for node_index, node in enumerate(data.keys()):
            x = time
            y = data[node][captured_attribute]
            # Add the trace to the subplot
            fig.add_trace(go.Scatter(x=x, y=y, name=f"{node}", line=dict(width=1)))
            n = 6

        # Update layout and show the figure
        fig.update_layout(
            showlegend=True,
            xaxis=dict(
                title=dict(text="Time", standoff=0),
                ticktext=[power_domain.convert_to_time_string(int(value)) for value in np.linspace((start_time-1), end_time, n)],
                tickvals=[int(value) - offset for value in np.linspace(start_time, end_time, n)]),
            yaxis=dict(
                title=dict(text=captured_attribute, standoff=0))
        )

        # add event lines
        if events is not None:
            for (time, _, (event, args)) in events:
                time_x_value = power_domain.get_current_time(time)
                fig.add_vrect(
                    x0=time_x_value - offset,
                    x1=time_x_value - offset,
                    fillcolor="red", opacity=0.5,
                    layer="above", line_width=1,
                    label=dict(text=f"{event.__name__}({', '.join(arg.name for arg in args)})")
                )
        # Update layout to add a title
        fig.update_layout(
            title_text=f"Timeseries of {captured_attribute} for Entities.",
            title_x=0.5,  # Adjust the horizontal position of the title
            title_font=dict(size=16),  # Adjust the font size of the title
        )
        return fig

    def retrieve_select_data_entities(self, time_series, desired_nodes: ["Node"]):
        nodes = {}
        for node in desired_nodes:
            if node is not None:
                nodes[node.name] = {"Power Used": [None] * len(list(time_series.keys())),
                                    "Carbon Intensity": [None] * len(list(time_series.keys())),
                                    "Carbon Released": [None] * len(list(time_series.keys()))}
        # Go through each time series
        for time_index, (time, power_sources) in enumerate(time_series.items()):
            # Go through each power source to isolate nodes
            for power_source_index, power_source in enumerate(power_sources):
                # Go through nodes
                for node_index, node in enumerate(power_sources[power_source]):
                    if node in list(nodes.keys()):
                        # Go through node details and append each attribute value to the corresponding list
                        for attribute_index, (attribute, values) in enumerate(
                                power_sources[power_source][node].items()):

                            nodes[node][attribute][time_index] = values
        times = [i for i in range(len(list(time_series.keys())))]
        return times, nodes

    def retrieve_select_data_power_sources(self, time_series, desired_power_sources: ["PowerSource"]):
        power_source_results = {}
        for power_source in desired_power_sources:
            if power_source is not None:
                power_source_results[power_source.name] = {"Power Used": [None] * len(list(time_series.keys())),
                                    "Carbon Intensity": [power_source.get_carbon_intensity_at_time(time) for time in range(len(list(time_series.keys())))],
                                    "Power Available": [power_source.get_power_at_time(time) for time in range(len(list(time_series.keys())))],
                                    "Carbon Released": [None] * len(list(time_series.keys()))}
        # Go through each time series
        for time_index, (time, power_sources) in enumerate(time_series.items()):
            # Go through each power source to isolate nodes
            for power_source_index, power_source in enumerate(power_sources):
                if power_source in list(power_source_results.keys()):
                    power_used: float = 0
                    carbon_released: float = 0
                    # Go through nodes
                    for node_index, node in enumerate(power_sources[power_source]):
                        if node != "Total Carbon Released":
                            power_used = power_used + power_sources[power_source][node]["Power Used"]
                            carbon_released = carbon_released + power_sources[power_source][node]["Carbon Released"]
                    power_source_results[power_source]["Power Used"][time_index] = power_used
                    power_source_results[power_source]["Carbon Released"][time_index] = carbon_released
        times = [i for i in range(len(list(time_series.keys())))]
        return times, power_source_results
