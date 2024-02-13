import networkx as nx
import numpy as np

from src.extendedLeaf.application import Application, ProcessingTask
from src.extended_Examples.main_examples.example7.infrastructure import Cloud
from src.extended_Examples.main_examples.example7.settings import FOG_UTILIZATION_THRESHOLD
from src.extendedLeaf.infrastructure import Infrastructure, Node
from src.extendedLeaf.orchestrator import Orchestrator


class FarmOrchestrator(Orchestrator):

    def __init__(self, infrastructure: Infrastructure, power_domain, utilization_threshold: float = FOG_UTILIZATION_THRESHOLD):
        super().__init__(infrastructure, power_domain)
        self.utilization_threshold = utilization_threshold

    def _processing_task_placement(self, processing_task: ProcessingTask, application) -> Node:
        dest_node = application.sink_node
        source_node = application.source_node
        paths = list(nx.all_simple_paths(self.infrastructure.graph, source=source_node.name, target=dest_node.name))
        # iterate through all the potential nodes
        current_best_carbon_intensity = np.inf
        return_node = None
        for path in paths:
            for i, node in enumerate(path):
                node = self.infrastructure.node(node)
                remaining_path = path[i:]
                if len(application.get_application_paths(processing_task)[0]) == len(remaining_path):
                    if node.paused is False:
                        power_source = node.power_model.power_source
                        carbon_intensity = power_source.get_current_carbon_intensity(0)
                        if carbon_intensity < current_best_carbon_intensity:
                            return_node = node
                            current_best_carbon_intensity = carbon_intensity


        if return_node is None:
            return_node = self.infrastructure.nodes(type_filter=Cloud)[0]
        return return_node
