import json
import os
import re
from datetime import datetime
from typing import Dict, Tuple

import numpy as np
import pandas as pd
# Figure generation libraries
import plotly.graph_objs as go
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
    fig.update_xaxes(
        title=dict(text="Time", standoff=0),
        ticktext=[" ", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"],
        tickvals=[h * 120 * 60 * 2 for h in range(13)],
    )
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

    def __init__(self, power_domain: PowerDomain):
        self.power_domain = power_domain
        self.creation_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = self.create_results_dir()

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

    def write_out_results(self, dir_path: str = None, filename: str = "output.json"):
        """ Allows user to write raw data to file, allows for a desired filepath and filename
            if either are absent the missing aspects are defaulted, """
        if not self.is_valid_filename(filename):
            filename = "output.json"

        if dir_path is None or not os.path.exists(dir_path):
            dir_path = self.results_dir

        filepath = os.path.join(dir_path, filename)

        # Convert dictionary to JSON format
        json_data = json.dumps(self.power_domain.captured_data, indent=2)

        # Write JSON data to a file
        with open(filepath, 'w') as json_file:
            json_file.write(json_data)
        return filepath, json_data

    def is_valid_filename(self, filename):
        pattern = re.compile(r'^[a-zA-Z0-9_-]+\.json$')
        return bool(pattern.match(filename))

    def test(self):
        global n
        keys = self.power_domain.captured_data.keys()
        start_time = self.power_domain.get_current_time(list(keys)[0])
        end_time = self.power_domain.get_current_time(list(keys)[-1])
        offset = start_time
        time, data = self.return_data(self.power_domain.captured_data, self.power_domain.powered_entities)
        fig = subplot_figure()

        # Go through each node and add its trace to the same subplot
        for node_index, node in enumerate(data.keys()):
            x = time
            y = data[node]["Carbon Released"]
            # Add the trace to the subplot
            fig.add_trace(go.Scatter(x=x, y=y, name=f"{node}", line=dict(width=1)))
            n = 6
        # Update layout and show the figure
        fig.update_layout(
            showlegend=True,
            xaxis=dict(
                ticktext= [self.power_domain.convert_to_time_string(int(value)) for value in np.linspace(start_time, end_time, n)],
                tickvals=[int(value) - offset for value in np.linspace(start_time, end_time, n)],
            ),
        )        # Update the layout and show the figure
        if os.path.exists(self.results_dir):
            fig.write_image(os.path.join(self.results_dir, "fig.pdf"), "pdf")



    def return_data(self, time_series, desired_nodes: ["Node"]):
        nodes = {}
        for node in desired_nodes:
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
