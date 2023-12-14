import json
import os
import re
from datetime import datetime
from typing import Dict, Tuple

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
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, horizontal_spacing=0.01)
    fig.update_layout(
        height=320,
        width=1000,
        font=dict(size=9),
        legend=dict(x=0, y=1.215),
    )
    fig.update_yaxes(title_text=None)
    fig.update_yaxes(title=dict(text="Power Usage (Watt)", standoff=0), row=1, col=1)

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
        print(10)
        keys = self.power_domain.captured_data.keys()
        print(self.power_domain.get_current_time(list(keys)[0]))
        start_time_index = self.power_domain.get_current_time(list(keys)[0])
        x = [1,2,3]
        y = [1,2,3]
        fig = subplot_figure()
        fig.write_image("fig1.pdf")

