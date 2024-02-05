import logging

import networkx as nx
import matplotlib
matplotlib.use('TkAgg')  # You can replace 'TkAgg' with another backend that works for you
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from src.extendedLeaf.power import PowerDomain, validate_str_time


class Animation:
    def __init__(self, power_domains, env):

        self.power_domains: [PowerDomain] = power_domains
        self.env = env
        self.time_series_data = self.power_domains[0].captured_data

        self.g = nx.DiGraph()
        self.fig, self.ax = plt.subplots()
        self.pos = nx.spring_layout(self.g)
        nx.draw(self.g, self.pos, with_labels=True, font_weight='bold', node_size=700,
                                       node_color='skyblue', font_size=8, arrowsize=15)
        self.start_time_increment = self.power_domains[0].start_time_index
        self.current_time_increment = self.start_time_increment
        self.is_playing = False

        # Slider for controlling time steps
        slider_ax = self.fig.add_axes([0.15, 0.01, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        self.slider = Slider(slider_ax, 'Time Step', 0, len(self.time_series_data) - 1, valinit=0, valstep=1)
        self.slider.on_changed(self.update_time_step)

        self.play_pause_ax = self.fig.add_axes([0.85, 0.01, 0.1, 0.03])
        self.play_pause_button = Button(self.play_pause_ax, 'Play')
        self.play_pause_button.on_clicked(self.toggle_play_pause)

        # Create a logger
        logger = logging.getLogger('matplotlib')

        # Set the logging level to DEBUG
        logger.setLevel(logging.DEBUG)

        # Create a handler and set the formatter
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)

        # Add the filter to the handler
        filter_allow_certain_debug = AllowCertainDebugFilter()
        handler.addFilter(filter_allow_certain_debug)

        # Add the handler to the logger
        logger.addHandler(handler)


    def update_time_step(self, val):
        new_time_increment = self.start_time_increment + val
        if new_time_increment != self.current_time_increment:
            self.current_time_increment = new_time_increment
            self.update(self.current_time_increment)
            self.fig.canvas.draw_idle()

    def toggle_play_pause(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_pause_button.label.set_text('Pause')
            self.update(self.current_time_increment)
        else:
            self.play_pause_button.label.set_text('Play')

    def update(self, frame):
        plt.sca(self.ax)
        if self.is_playing and self.current_time_increment < (len(self.time_series_data) + self.start_time_increment - 1):
            self.ax.clear()
            self.g.clear()
            # Move nodes between power sources (simplified for demonstration)
            data = self.time_series_data[str(self.current_time_increment)]
            for power_source_key, power_source_values in data.items():
                self.g.add_node(power_source_key)
                for node in data[power_source_key]:
                    if node == "Total Carbon Released":
                        continue
                    self.g.add_node(node)
                    self.g.add_edge(power_source_key, node)
            self.pos = nx.spring_layout(self.g)
            nx.draw(self.g, self.pos, with_labels=True, font_weight='bold', node_size=700,
                                           node_color='skyblue', font_size=8, arrowsize=15)
            self.ax.set_title(f'Time Step: {PowerDomain.convert_to_time_string(self.current_time_increment)}')

            self.current_time_increment += 1
            self.slider.set_val(self.current_time_increment-self.start_time_increment)
            self.fig.canvas.manager.window.after(2500, self.update, frame + 1)
        else:
            self.play_pause_button.label.set_text('Play')

    def run_animation(self):
        plt.show()

class AllowCertainDebugFilter(logging.Filter):
    def filter(self, record):
        not_allowed = ["TkAgg", "findfont", "STREAM b'IHDR'", "STREAM b'sBIT'", "b'sBIT'",
                       "STREAM b'pHYs'", "STREAM b'IDAT'"]
        for avoid in not_allowed:
            if avoid in record.getMessage():
                return False
        return True
