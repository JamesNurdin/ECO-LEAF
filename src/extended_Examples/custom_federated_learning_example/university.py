from typing import Tuple, List

import networkx as nx

from src.extended_Examples.custom_federated_learning_example.infrastructure import *
from src.extended_Examples.custom_federated_learning_example.settings import *
from src.extended_Examples.custom_federated_learning_example.orchestrator import UniversityOrchestrator
from src.extendedLeaf.infrastructure import Infrastructure


class City:
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.local_site_graph, self.entry_point_locations, self.traversable_locations = _create_city_graph()
        # nx.draw(self.local_site_graph)
        # set up infrastructure
        self.infrastructure = Infrastructure()
        self.infrastructure.add_node(Server())

        # place the clusters
        for location in RNG.choice(self.traversable_locations, NUMBER_CLUSTERED_CLIENTS):
            self._add_clustered_client_node(location)

        self.orchestrator = UniversityOrchestrator(self.infrastructure,
                                                   utilization_threshold=CLIENT_UTILIZATION_THRESHOLD)


        """orchestrator = SimpleOrchestrator(self.infrastructure)

        work_stations: [WorkStationNode] = self.infrastructure.nodes(type_filter=WorkStationNode)
        for work_station in work_stations:
            orchestrator.place(work_station.application)
        caches: [CacheNode] = self.infrastructure.nodes(type_filter=CacheNode)"""

    def _add_clustered_client_node(self, location: Location):
        """clustered nodes are connected by WI-FI and are powered by the clusters source
        They will hold the client for the round if at the node before the round starts"""
        server: Server = self.infrastructure.nodes(type_filter=Server)[0]
        clustered_client = ClusteredClient(location, server)
        self.infrastructure.add_link(LinkEthernet(server, clustered_client))
        self.infrastructure.add_link(LinkEthernet(clustered_client, server))

    def _add_client_node(self, location: Location):
        """clients are connected to the server through WI-FI."""
        server: Server = self.infrastructure.nodes(type_filter=Server)[0]
        client = Client(self.infrastructure)
        self.infrastructure.add_link(LinkCellularFromServer(server, client))
        self.infrastructure.add_link(LinkCellularToServer(client, server))
        for cluster in self.infrastructure.nodes(type_filter=ClusteredClient):
            # client is in range of the cluster
            if cluster.location == location:
                print(client.name + " joined " + cluster.name + " at location ("
                      + str(location.x) + "," + str(location.y) + ")")
                self.infrastructure.add_link(LinkEthernet(cluster, server))
                self.infrastructure.add_link(LinkEthernet(server, cluster))
                client.in_cluster = True
                cluster.add_client(client)

    def remove_client_app(self, client: Client):
        client.application.deallocate()
        self.infrastructure.remove_node(client)

    def remove_cluster_app(self, cluster: ClusteredClient):
        cluster.application.deallocate()

    """def run(self, env: simpy.Environment):
        while True:
            for taxi in self._create_taxis(env):
                self.city.add_taxi_and_start_v2i_app(taxi)
                env.process(self._remove_taxi_process(env, taxi))
            yield env.timeout(UPDATE_MOBILITY_INTERVAL)"""


def _create_city_graph() -> Tuple[nx.Graph, List[Location], List[Location]]:
    graph = nx.Graph()
    n_points = STREETS_PER_AXIS + 2  # crossings + entry points
    step_size_x = CITY_WIDTH / (n_points - 1)
    step_size_y = CITY_HEIGHT / (n_points - 1)

    entry_point_locations = []
    traversable_locations = []
    locations = [[None for _ in range(n_points)] for _ in range(n_points)]
    for x in range(n_points):
        for y in range(n_points):
            location = Location(x * step_size_x, y * step_size_y)
            if x == 0 or x == n_points - 1 or y == 0 or y == n_points - 1:
                entry_point_locations.append(location)
            else:
                traversable_locations.append(location)
            locations[x][y] = location
            graph.add_node(location)
            if x > 0 and y > 0:
                if y < n_points - 1:
                    graph.add_edge(location, locations[x - 1][y])
                if x < n_points - 1:
                    graph.add_edge(location, locations[x][y - 1])

    for corner_location in [locations[0][0],
                            locations[n_points - 1][0],
                            locations[0][n_points - 1],
                            locations[n_points - 1][n_points - 1]]:
        graph.remove_node(corner_location)
        entry_point_locations.remove(corner_location)

    return graph, entry_point_locations, traversable_locations
