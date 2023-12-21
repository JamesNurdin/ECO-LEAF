import math

from src.extendedLeaf.application import Application, ProcessingTask
from src.extended_Examples.precision_agriculture.infrastructure import Cloud, RechargeStation
from src.extended_Examples.precision_agriculture.settings import FOG_UTILIZATION_THRESHOLD, FOG_DCS, FOG_IDLE_SHUTDOWN
from src.extendedLeaf.infrastructure import Infrastructure, Node
from src.extendedLeaf.orchestrator import Orchestrator


class FarmOrchestrator(Orchestrator):

    def __init__(self, infrastructure: Infrastructure, plots, utilization_threshold: float = FOG_UTILIZATION_THRESHOLD):
        super().__init__(infrastructure)
        self.utilization_threshold = utilization_threshold
        self.plots = plots

    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        result_node = None

        if FOG_DCS > 0:
            lowest_utilization = math.inf
            for fog_node in self.infrastructure.nodes(type_filter=RechargeStation):
                if fog_node.utilization() < lowest_utilization:
                    lowest_utilization = fog_node.utilization()
                    result_node = fog_node

        if result_node is None:
            result_node = self.infrastructure.nodes(type_filter=Cloud)[0]

        return result_node
