import math
from typing import List, Optional, Type, TypeVar, Iterator, Union, Tuple

import networkx as nx

from src.extendedLeaf.power import PowerAware, PowerMeasurement
from src.extendedLeaf.mobility import Location

class Node(PowerAware):
    def __init__(self, name: str,
                 cu: Optional[float] = None,
                 power_model: Optional["PowerModelNode"] = None,
                 location: Optional[Location] = None):
        """A compute node in the infrastructure graph.

        This can represent any kind of node, e.g.
        - simple sensors without processing capabilities
        - resource constrained nodes fog computing nodes
        - mobile nodes like cars or smartphones
        - entire data centers with virtually unlimited resources

        Args:
            name: Name of the node. This is used to refer to nodes when defining links.
            cu: Maximum processing power the node provides in "compute units", a imaginary unit for computational power
                to express differences between hardware platforms. If None, the node has unlimited processing power.
            power_model: Power model which determines the power usage of the node.
            location: The (x,y) coordinates of the node
        """
        self.name = name
        if cu is None:
            self.cu = math.inf
        else:
            self.cu = cu
        self.used_cu = 0
        self.tasks: List["Task"] = []

        if power_model:
            if cu is None and power_model.max_power is not None:
                raise ValueError("Cannot use PowerModelNode with `max_power` on a compute node with unlimited "
                                 "processing power")
            self.power_model = power_model
            self.power_model.set_parent(self)

        self.location = location

        self.paused = True
        self.recover_task_power = 0

    def __repr__(self):
        cu_repr = self.cu if self.cu is not None else "∞"
        return f"{self.__class__.__name__}('{self.name}', cu={self.used_cu}/{cu_repr})"

    def utilization(self) -> float:
        """Return the current utilization of the resource in the range [0, 1]."""
        try:
            return self.used_cu / self.cu
        except ZeroDivisionError:
            assert self.used_cu == 0
            return 0

    def _add_task(self, task: "Task"):
        """Add a task to the node.

        Private as this is only called by leaf.application.Task and not part of the public interface.
        """
        self._reserve_cu(task.cu)
        self.tasks.append(task)

    def _remove_task(self, task: "Task"):
        """Remove a task from the node.

        Private as this is only called by leaf.application.Task and not part of the public interface.
        """
        self._release_cu(task.cu)
        self.tasks.remove(task)

    def measure_power(self) -> PowerMeasurement:
        try:
            if self.paused:
                return PowerMeasurement(0, 0)
            return self.power_model.measure()
        except AttributeError:
            return PowerMeasurement(0, 0)

    def _reserve_cu(self, cu: float):
        new_used_cu = self.used_cu + cu
        if new_used_cu > self.cu:
            raise ValueError(f"Cannot reserve {cu} CU on compute node {self}.")
        self.used_cu = new_used_cu

    def _release_cu(self, cu: float):
        new_used_cu = self.used_cu - cu
        if new_used_cu < 0:
            raise ValueError(f"Cannot release {cu} CU on compute node {self}.")
        self.used_cu = new_used_cu

    def pause(self):
        if self.paused:
            raise ValueError(f"Error, node already paused")
        self.recover_task_power = self.power_model.update_sensitive_measure(1)
        self.paused = True
        for current_task in self.tasks:
            application = current_task.application
            paths = application.get_application_paths(current_task)
            for path in paths:
                if application.graph.nodes[path[0]]["data"].paused is False:
                    application.graph.nodes[path[0]]["data"].pause()
                for i in range(1, len(path)):
                    if application.graph.nodes[path[i]]["data"].paused is False:
                        application.graph.nodes[path[i]]["data"].pause()
                    if application.graph[path[i-1]][path[i]]["data"].paused is False:
                        application.graph[path[i-1]][path[i]]["data"].pause()

    def unpause(self):
        if not self.paused:
            raise ValueError(f"Error, node not paused")
        self.recover_task_power = 0
        self.paused = False
        for current_task in self.tasks:
            application = current_task.application
            paths = application.get_application_paths(current_task)
            for path in paths:
                if application.graph.nodes[path[0]]["data"].paused is True:
                    application.graph.nodes[path[0]]["data"].unpause()
                for i in range(1, len(path)):
                    if application.graph.nodes[path[i]]["data"].paused is True:
                        application.graph.nodes[path[i]]["data"].unpause()
                    if application.graph[path[i - 1]][path[i]]["data"].paused is True:
                        application.graph[path[i - 1]][path[i]]["data"].unpause()

    def check_if_paused(self) -> bool:
        return self.paused

    def check_power_needed_to_unpause(self):
        if not self.paused:
            raise AttributeError(f"Error, node {self.name} is not paused")
        return self.recover_task_power

class Link(PowerAware):
    def __init__(self, src: Node, dst: Node, bandwidth: float, power_model: "PowerModelLink", latency: float = 0, name: str = None):
        """A network link in the infrastructure graph.

        This can represent any kind of network link, e.g.

        - direct cable connections
        - wireless connections such as WiFi, Bluetooth, LoRaWAN, 4G LTE, 5G, ...
        - entire wide area network connections that incorporate different networking equipment you do not want to
          model explicitly.

        Args:
            src: Source node of the network link.
            dst: Target node of the network link.
            bandwidth: Bandwidth provided by the network link.
            power_model: Power model which determines the power usage of the link.
            latency: Latency of the network link which can be used to implement routing policies.
        """
        if name is None:
            raise ValueError(f"Error: No name for the link was supplied.")
        self.name = name
        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth
        self.latency = latency
        self.used_bandwidth = 0
        self.power_model = power_model
        self.power_model.set_parent(self)
        self.data_flows: List["DataFlow"] = []

        self.paused = True
        self.recover_task_power = 0

    def __repr__(self):
        latency_repr = f", latency={self.latency}" if self.latency else ""
        return f"{self.__class__.__name__}('{self.src.name}' -> '{self.dst.name}', bandwidth={self.used_bandwidth}/{self.bandwidth}{latency_repr})"

    def _add_data_flow(self, data_flow: "DataFlow"):
        """Add a data flow to the link.

        Private as this is only called by leaf.application.DataFlow and not part of the public interface.
        """
        self._reserve_bandwidth(data_flow.bit_rate)
        self.data_flows.append(data_flow)

    def _remove_data_flow(self, data_flow: "DataFlow"):
        """Remove a data flow from the link.

        Private as this is only called by leaf.application.DataFlow and not part of the public interface.
        """
        self._release_bandwidth(data_flow.bit_rate)
        self.data_flows.remove(data_flow)

    def measure_power(self) -> PowerMeasurement:
        try:
            if self.paused:
                return PowerMeasurement(0, 0)
            return self.power_model.measure()
        except AttributeError:
            return PowerMeasurement(0, 0)

    def _reserve_bandwidth(self, bandwidth):
        new_used_bandwidth = self.used_bandwidth + bandwidth
        if new_used_bandwidth > self.bandwidth:
            raise ValueError(f"Cannot reserve {bandwidth} bandwidth on network link {self}.")
        self.used_bandwidth = new_used_bandwidth

    def _release_bandwidth(self, bandwidth):
        new_used_bandwidth = self.used_bandwidth - bandwidth
        if new_used_bandwidth < 0:
            raise ValueError(f"Cannot release {bandwidth} bandwidth on network link {self}.")
        self.used_bandwidth = new_used_bandwidth

    def pause(self):
        if self.paused:
            raise ValueError(f"Error, link already paused")
        self.recover_task_power =  self.power_model.update_sensitive_measure(1)
        self.paused = True
        for current_data_flow in self.data_flows:
            if current_data_flow.paused is False:
                current_data_flow.pause()
            application = current_data_flow.application
            desired_task = None
            for task in self.dst.tasks:
                if task.application == application:
                    desired_task = task
            paths = application.get_application_paths(desired_task)
            for path in paths:
                if application.graph.nodes[path[0]]["data"].paused is False:
                    application.graph.nodes[path[0]]["data"].pause()
                for i in range(1, len(path)):
                    if application.graph.nodes[path[i]]["data"].paused is False:
                        application.graph.nodes[path[i]]["data"].pause()
                    if application.graph[path[i - 1]][path[i]]["data"].paused is False:
                        application.graph[path[i - 1]][path[i]]["data"].pause()


    def unpause(self):
        if not self.paused:
            raise ValueError(f"Error, link not paused")
        self.recover_task_power = 0
        self.paused = False
        for current_data_flow in self.data_flows:
            if current_data_flow.paused is True:
                current_data_flow.unpause()
            application = current_data_flow.application
            desired_task = None
            for task in self.dst.tasks:
                if task.application == application:
                    desired_task = task
            paths = application.get_application_paths(desired_task)
            for path in paths:
                if application.graph.nodes[path[0]]["data"].paused is True:
                    application.graph.nodes[path[0]]["data"].unpause()
                for i in range(1, len(path)):
                    if application.graph.nodes[path[i]]["data"].paused is True:
                        application.graph.nodes[path[i]]["data"].unpause()
                    if application.graph[path[i - 1]][path[i]]["data"].paused is True:
                        application.graph[path[i - 1]][path[i]]["data"].unpause()

    def check_if_paused(self) -> bool:
        return self.paused

    def check_power_needed_to_unpause(self):
        if not self.paused:
            raise AttributeError(f"Error, link {self.name} is not paused")
        return self.recover_task_power


class Infrastructure(PowerAware):
    _TNode = TypeVar("_TNode", bound=Node)  # Generics
    _TLink = TypeVar("_TLink", bound=Link)  # Generics
    _NodeTypeFilter = Union[Type[_TNode], Tuple[Type[_TNode], ...]]
    _LinkTypeFilter = Union[Type[_TLink], Tuple[Type[_TLink], ...]]

    def __init__(self):
        """Infrastructure graph of the simulated scenario.

        The infrastructure is a weighted, directed multigraph where every node contains a :class:`Node` and every edge
        between contains a :class:`Link`.
        """
        self.graph = nx.MultiDiGraph()

    def node(self, node_name: str) -> Node:
        """Return a specific node by name."""
        return self.graph.nodes[node_name]["data"]

    # TODO link()

    def add_link(self, link: Link):
        """Add a link to the infrastructure. Missing nodes will be added automatically."""
        self.add_node(link.src)
        self.add_node(link.dst)
        self.graph.add_edge(link.src.name, link.dst.name, data=link, latency=link.latency)

    def add_node(self, node: Node):
        """Adds a node to the infrastructure."""
        if node.name not in self.graph:
            self.graph.add_node(node.name, data=node)

    def remove_node(self, node: Node):
        """Removes a node from the infrastructure."""
        self.graph.remove_node(node.name)

    def nodes(self, type_filter: Optional[_NodeTypeFilter] = None) -> List[_TNode]:
        """Return all nodes in the infrastructure, optionally filtered by class."""
        nodes: Iterator[Node] = (v for _, v in self.graph.nodes.data("data"))
        if type_filter is not None:
            nodes = (node for node in nodes if isinstance(node, type_filter))
        return list(nodes)

    def links(self, type_filter: Optional[_LinkTypeFilter] = None) -> List[_TLink]:
        """Return all links in the infrastructure, optionally filtered by class."""
        links: Iterator[Link] = (v for _, _, v in self.graph.edges.data("data"))
        if type_filter is not None:
            links = (link for link in links if isinstance(link, type_filter))
        return list(links)

    def measure_power(self) -> PowerMeasurement:
        measurements = [node.measure_power() for node in self.nodes()] + [link.measure_power() for link in self.links()]
        return PowerMeasurement.sum(measurements)

