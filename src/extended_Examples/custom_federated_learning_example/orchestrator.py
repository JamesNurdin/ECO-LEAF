import math
from abc import ABC

from src.extendedLeaf.application import Application, ProcessingTask
from src.extended_Examples.custom_federated_learning_example.infrastructure import Server, Client, ClusteredClient
from src.extended_Examples.custom_federated_learning_example.settings import *
from src.extendedLeaf.infrastructure import Infrastructure, Node
from src.extendedLeaf.orchestrator import Orchestrator


class UniversityOrchestrator(Orchestrator):
    def __init__(self, infrastructure: Infrastructure, utilization_threshold: float = CLIENT_UTILIZATION_THRESHOLD):
        super().__init__(infrastructure)
        self.utilization_threshold = utilization_threshold

    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        lowest_utilization = math.inf
        result_node = None
        if processing_task.cu == CLIENT_TRAIN_CU:
            for client in self.infrastructure.nodes(type_filter=Client):
                if client.in_cluster is False:
                    if client.utilization() < lowest_utilization:
                        lowest_utilization = client.utilization()
                        result_node = client
        else:
            for cluster in self.infrastructure.nodes(type_filter=ClusteredClient):
                if cluster.used_cu != 0:
                    if cluster.utilization() < lowest_utilization:
                        print("applied to cluster")
                        lowest_utilization = cluster.utilization()
                        result_node = cluster

        if result_node is None or result_node.utilization() > self.utilization_threshold:
            result_node = self.infrastructure.nodes(type_filter=Server)[0]
            print("changed")
        return result_node
