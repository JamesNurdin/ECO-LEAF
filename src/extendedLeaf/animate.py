import networkx as nx
import matplotlib
matplotlib.use('TkAgg')  # You can replace 'TkAgg' with another backend that works for you
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from src.extendedLeaf.power import PowerDomain, validate_str_time


class Animation:
    def __init__(self, power_domains, env):
        self.power_domains: [PowerDomain] = power_domains
        self.env = env
        self.time_series_data = self.power_domains[0].captured_data

        g = nx.DiGraph()
        self.fig, ax = plt.subplots()
        pos = nx.spring_layout(g)
        nx.draw(g, pos, with_labels=True, font_weight='bold', node_size=700, node_color='skyblue', font_size=8,
                arrowsize=15)
        self.time_increment = self.power_domains[0].start_time_index

        # Animation update function
        def update(frame):
            ax.clear()
            g.clear()
            # Move nodes between power sources (simplified for demonstration)
            data = self.time_series_data[str(self.time_increment)]
            for power_source_key, power_source_values in data.items():
                g.add_node(power_source_key)
                for node in data[power_source_key]:
                    if node == "Total Carbon Released":
                        continue
                    g.add_node(node)
                    g.add_edge(power_source_key, node)
            new_pos = nx.spring_layout(g)
            nx.draw(g, new_pos, with_labels=True, font_weight='bold', node_size=700, node_color='skyblue', font_size=8,
                    arrowsize=15)
            ax.set_title(f'Time Step: {PowerDomain.convert_to_time_string(self.time_increment)}')
            self.time_increment = self.time_increment + 1
            return []

        self.update = update

    def run_animation(self):
        anim = FuncAnimation(fig=self.fig, func=self.update, interval=2500, repeat=False)
        plt.show()
