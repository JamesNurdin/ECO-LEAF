import logging

import networkx as nx
import matplotlib
import numpy as np

matplotlib.use('TkAgg')  # You can replace 'TkAgg' with another backend that works for you
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from src.extendedLeaf.power import PowerDomain, validate_str_time


class Animation:
    def __init__(self, power_domains, env, speed_sec: float = 2.5):

        self.power_domains: [PowerDomain] = power_domains
        self.env = env
        self.speed = int(speed_sec * 1000)
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
        slider_ax = self.fig.add_axes([0.15, 0.065, 0.65, 0.03])
        self.slider = Slider(slider_ax, 'Time Step', 0, len(self.time_series_data) - 1, valinit=0, valstep=1)
        self.slider.on_changed(self.update_time_step)
        self.slider.valtext.set_text("")  # Set initial tick label

        self.fig.add_axes([0.15, 0.05, 0.65, 0.02])
        self.tick_labels, self.tick_positions = self.get_axis_labels()
        for i, (position, label) in enumerate(zip(self.tick_positions, self.tick_labels)):
            plt.annotate(label, xy=(position, -0.1), xytext=(position, -0.2), ha='center', va='center', color='blue',
                         arrowprops=dict(arrowstyle='->', color='blue'))
        plt.xticks(self.tick_positions, self.tick_labels)
        plt.gca().axes.get_yaxis().set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)

        self.play_pause_ax = self.fig.add_axes([0.85, 0.065, 0.1, 0.03])
        self.play_pause_button = Button(self.play_pause_ax, 'Play')
        self.play_pause_button.on_clicked(self.toggle_play_pause)

    def get_axis_labels(self) -> [str]:
        label_list = []
        if len(self.time_series_data) % 2 == 0:
            num_ticks = min(5, len(self.time_series_data))
            tick_pos = np.linspace(0, num_ticks-1, num_ticks)
            print(tick_pos)
        else:
            num_ticks = min(6, len(self.time_series_data))
            tick_pos = np.linspace(0, num_ticks, num_ticks)

        indexes = np.linspace(0, len(self.time_series_data) - 1, num_ticks, dtype=int)
        for index in indexes:
            time_index = list(self.time_series_data.keys())[index]
            label_list.append(PowerDomain.convert_to_time_string(int(time_index)))
        return label_list, tick_pos

    def update_time_step(self, val):
        self.current_time_increment = self.start_time_increment + val
        self.slider.valtext.set_text("")  # Set initial tick label
        self.update(self.current_time_increment)
        self.fig.canvas.draw_idle()

    def toggle_play_pause(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_pause_button.label.set_text('Pause')
            self.play()
        else:
            self.play_pause_button.label.set_text('Play')

    def play(self):
        if self.is_playing and self.current_time_increment < (len(self.time_series_data) + self.start_time_increment - 1):
            self.update(self.current_time_increment)
            self.current_time_increment = self.current_time_increment + 1
            self.fig.canvas.manager.window.after(self.speed, self.play)
            self.slider.set_val(self.current_time_increment - self.start_time_increment)

        else:
            self.play_pause_button.label.set_text('Play')

    def update(self, frame):
        plt.sca(self.ax)
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
