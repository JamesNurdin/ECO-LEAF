from typing import List, Optional

import networkx as nx
import simpy

from examples.practise_examples.custom_CDNcache_example.settings import UPDATE_MOBILITY_INTERVAL
from extended_Examples.custom_federated_learning_example.infrastructure import Client, Server, LinkCellularFromServer, \
    ClusteredClient, LinkCellularToServer, LinkEthernet
from extended_Examples.custom_federated_learning_example.settings import CLIENT_COUNT_DISTRIBUTION, CLIENT_SPEED_DISTRIBUTION, \
    RNG, MAX_CLIENTS_PER_MINUTE, NUMBER_CLIENTS
from extended_Examples.custom_federated_learning_example.university import City
from extendedLeaf.mobility import Location


class MobilityManager:

    def __init__(self, uni: City):
        self.uni = uni

    def run(self, env: simpy.Environment, uni: City):
        server = uni.infrastructure.nodes(type_filter=Server)[0]

        for client in self._create_clients(env, uni):
            for cluster in uni.infrastructure.nodes(type_filter=ClusteredClient):
                # client is in range of the cluster
                if cluster.location == client.location:
                    print(client.name + " joined " + cluster.name)
                    uni.infrastructure.add_link(LinkEthernet(cluster, server))
                    uni.infrastructure.add_link(LinkEthernet(server, cluster))
                    client.in_cluster = True
                    cluster.add_client(client)

        for client in uni.infrastructure.nodes(type_filter=Client):
            uni.orchestrator.place(client.application)
        for cluster in uni.infrastructure.nodes(type_filter=ClusteredClient):
            uni.orchestrator.place(cluster.application)

    def _remove_client_process(self, env: simpy.Environment, client: Client):
        yield env.timeout(client.mobility_model.life_time)
        self.uni.remove_client_app(client)

    def _create_clients(self, env: simpy.Environment, uni: City) -> List[Client]:
        avg_client_speed = _avg_client_speed(env.now)
        avg_client_count = _avg_client_count(env.now)
        client_count = RNG.poisson(avg_client_count)
        return [self._create_client(env=env, speed=avg_client_speed, uni=uni) for _ in range(NUMBER_CLIENTS)]

    def _create_client(self, env: simpy.Environment, speed: float, uni: City) -> Client:
        """clients are connected to the server through Celluar data."""
        start = self._random_gate_location()
        dst = self._random_gate_location()
        while not start.distance(dst) > 0.5:
            dst = self._random_gate_location()
        path = nx.shortest_path(self.uni.local_site_graph, source=start, target=dst)
        mobility_model = ClientMobilityModel(path, speed=speed, start_time=env.now)

        server: Server = uni.infrastructure.nodes(type_filter=Server)[0]
        client = Client(uni.infrastructure, env, mobility_model)
        uni.infrastructure.add_link(LinkCellularFromServer(server, client))
        uni.infrastructure.add_link(LinkCellularToServer(client, server))
        return client

    def _random_gate_location(self) -> Location:
        return RNG.choice(self.uni.traversable_locations)

    def _clusters_in_client_path(self, path: List) -> List[ClusteredClient]:
        return [cl for cl in self.uni.infrastructure.nodes(type_filter=ClusteredClient) if cl.location in path]


class ClientMobilityModel:
    def __init__(self, path: List[Location], speed: float, start_time: float):
        self.start_time = start_time
        self._location_dict, self.life_time = self._create_location_dict(path, speed, interval=UPDATE_MOBILITY_INTERVAL)

    def location(self, time: float) -> Optional[Location]:
        try:
            return self._location_dict[self._time_to_map_key(time - self.start_time)]
        except KeyError:
            print(f"Error: {time}")
            return self._location_dict[max(self._location_dict.keys())]

    def _create_location_dict(self, path: List[Location], speed: float, interval: float):
        """Computes the random path of the taxi and precomputes its location at specific time steps."""
        distance_per_interval = speed * UPDATE_MOBILITY_INTERVAL

        last_location: Location = None
        remaining_meters_from_last_path = 0
        time = 0

        time_location_dict = {}
        for next_location in path:
            if last_location is not None:
                distance = next_location.distance(last_location)
                for fraction in self._get_fractions(distance, remaining_meters_from_last_path, distance_per_interval):
                    new_x = last_location.x + fraction * (next_location.x - last_location.x)
                    new_y = last_location.y + fraction * (next_location.y - last_location.y)
                    time_location_dict[self._time_to_map_key(time)] = Location(new_x, new_y)
                    time += interval
                remaining_meters_from_last_path = distance % distance_per_interval
            last_location = next_location
        return time_location_dict, time - interval  # TODO Check if this is correct

    @staticmethod
    def _get_fractions(path_distance: float, remaining_last_path_distance: float, distance_per_step: float):
        total_distance = path_distance + remaining_last_path_distance
        n_steps = int(total_distance / distance_per_step)
        fractions = []
        for i in range(n_steps):
            distance_on_path = i * distance_per_step - remaining_last_path_distance
            fractions.append(distance_on_path / path_distance)
        return fractions

    @staticmethod
    def _time_to_map_key(time: float) -> int:
        return int(round(time * 100) / 100)


def _avg_client_count(time: float):
    """Returns the average number of taxis that should be generated at this time step.
    The result will be passed to a Poisson distribution to determine the actual number.
    """
    # TODO Check int
    steps_per_minute = 60 / UPDATE_MOBILITY_INTERVAL
    minute = (time / steps_per_minute) % len(CLIENT_COUNT_DISTRIBUTION)
    return CLIENT_COUNT_DISTRIBUTION[int(minute)] / steps_per_minute * MAX_CLIENTS_PER_MINUTE


def _avg_client_speed(time: float):
    """Returns the average speed of taxis at the time of the day."""
    # TODO Check int
    steps_per_minute = 60 / UPDATE_MOBILITY_INTERVAL
    minute = (time / steps_per_minute) % len(CLIENT_SPEED_DISTRIBUTION)
    return CLIENT_SPEED_DISTRIBUTION[int(minute)]
