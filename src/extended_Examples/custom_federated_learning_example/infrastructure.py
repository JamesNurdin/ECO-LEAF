import simpy

from src.extended_Examples.custom_federated_learning_example.settings import *
from src.extendedLeaf.application import Application, SourceTask, ProcessingTask, SinkTask, Task
from src.extendedLeaf.infrastructure import Link, Node, Infrastructure
from src.extendedLeaf.mobility import Location
from src.extendedLeaf.power import PowerModelLink, PowerModelNode, PowerMeasurement

"""Counter for incrementally naming nodes"""
_clients_created = 0
_clustered_clients_created = 0
_servers_created = 0


class Server(Node):
    def __init__(self):
        super().__init__("Server", cu=SERVER_CU, power_model=PowerModelNode(power_per_cu=SERVER_WATT_PER_CU))


class Client(Node):
    def __init__(self, infrastructure, env, mobility_model):
        self.shutdown = CLIENT_IDLE_SHUTDOWN
        self.env = env
        global _clients_created
        super().__init__(f"Client{_clients_created}", cu=CLIENT_CU,
                         power_model=PowerModelNode(max_power=CLIENT_MAX_POWER, static_power=CLIENT_STATIC_POWER))
        _clients_created += 1
        application_sink = infrastructure.nodes(type_filter=Server)[0]
        self.mobility_model = mobility_model
        self.application = self._create_client_application(application_sink)
        self.in_cluster = False

    @property
    def location(self) -> Location:
        return self.mobility_model.location(self.env.now)

    @location.setter
    def location(self, value):
        pass  # only for initialization, locations of this node is managed by the TaxiMobilityModel

    def _create_client_application(self, sink: Node) -> Application:
        # build application
        application = Application()
        # client receives model
        source_task = SourceTask(cu=0, bound_node=self)
        application.add_task(source_task)
        # allow for client to train model
        processing_send_task = ProcessingTask(cu=CLIENT_TRAIN_CU)
        application.add_task(processing_send_task,
                             incoming_data_flows=[(source_task, SERVER_TO_CLIENT_BIT_RATE)])
        # Send updates to server
        sink_return_task = SinkTask(cu=CLIENT_RETURN_SERVER_CU, bound_node=sink)
        application.add_task(sink_return_task,
                             incoming_data_flows=[(processing_send_task, CLIENT_TO_SERVER_BIT_RATE)])
        return application

    def measure_power(self) -> PowerMeasurement:
        if self.shutdown:
            return PowerMeasurement(0, 0)
        else:
            return super().measure_power()

    @property
    def location(self) -> Location:
        return self.mobility_model.location(self.env.now)

    @location.setter
    def location(self, value):
        pass  # only for initialization, locations of this node is managed by the ClientMobilityModel


class ClusteredClient(Node):
    """clustered clients should have their power model overwritten to accommodate the change and utilise a shared power
    resource"""
    def __init__(self, location: Location, application_sink: Node):
        global _clustered_clients_created
        super().__init__(f"Cluster{_clustered_clients_created}", cu=0,
                         power_model=PowerModelNode(max_power=0, static_power=0),
                         location=location)
        _clustered_clients_created += 1
        self._number_local_clients = 0
        self.location = location
        self.clients = []
        self.shutdown = True
        self.application = self._create_clustered_client_application(application_sink)

    def add_client(self, client: Client):
        self.clients.append(client)
        self._number_local_clients += 1
        if (self._number_local_clients > 0) and self.shutdown is True:
            self.shutdown = False
        self.update_power_model()

    def remove_client(self, client: Client) -> Client:
        self.clients.remove(client)
        self._number_local_clients -= 1
        if self._number_local_clients == 0:
            self.shutdown = True
        self.update_power_model()
        return client

    def update_power_model(self):
        self.power_model.max_power=CLIENT_MAX_POWER * self._number_local_clients
        self.power_model.static_power=CLIENT_STATIC_POWER * self._number_local_clients
        self.cu = CLIENT_CU * self._number_local_clients

    def _create_clustered_client_application(self, sink: Node) -> Application:
        # build application
        application = Application()
        # cluster receives model
        source_task = SourceTask(cu=0, bound_node=self)
        application.add_task(source_task)
        # allow for cluster to train model
        processing_send_task = ProcessingTask(cu=CLUSTERED_CLIENT_TRAIN_CU)
        application.add_task(processing_send_task,
                             incoming_data_flows=[(source_task, CLUSTERED_SERVER_TO_CLIENT_BIT_RATE)])
        # Send updates to server
        sink_return_task = SinkTask(cu=CLUSTERED_CLIENT_RETURN_SERVER_CU, bound_node=sink)
        application.add_task(sink_return_task,
                             incoming_data_flows=[(processing_send_task, CLIENT_TO_CLUSTERED_SERVER_BIT_RATE)])
        return application

    def measure_power(self) -> PowerMeasurement:
        if self.shutdown:
            return PowerMeasurement(0, 0)
        else:
            return super().measure_power()

    def add_task(self, task: Task):
        if self.shutdown:
            self.shutdown = False
        super().add_task(task)

    def remove_task(self, task: Task):
        super().remove_task(task)
        if CLUSTERED_CLIENT_IDLE_SHUTDOWN and self.used_cu == 0:
            self.shutdown = True

# Links


class LinkWIFItoServer(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WIFI_BANDWIDTH,
                         latency=WIFI_LATENCY,
                         power_model=PowerModelLink(WIFI_WORKSTATION_TO_MAIN_SERVER_WATT_PER_BIT))


class LinkWIFIfromServer(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WIFI_BANDWIDTH,
                         latency=WIFI_LATENCY,
                         power_model=PowerModelLink(WIFI_MAIN_SERVER_TO_WORKSTATION_WATT_PER_BIT))


class LinkCellularToServer(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=CELLULAR_BANDWIDTH,
                         latency=CELLULAR_LATENCY,
                         power_model=PowerModelLink(CELLULAR_TO_SERVER_WATT_PER_BIT))


class LinkCellularFromServer(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WIFI_BANDWIDTH,
                         latency=CELLULAR_LATENCY,
                         power_model=PowerModelLink(CELLULAR_FROM_SERVER_WATT_PER_BIT))


class LinkEthernet(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=ETHERNET_BANDWIDTH,
                         latency=ETHERNET_LATENCY,
                         power_model=PowerModelLink(ETHERNET_WATT_PER_BIT))


class LinkWanUp(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WAN_BANDWIDTH,
                         latency=WAN_LATENCY,
                         power_model=PowerModelLink(WAN_WATT_PER_BIT_UP))


class LinkWanDown(Link):
    def __init__(self, src: Node, dst: Node):
        super().__init__(src, dst,
                         bandwidth=WAN_BANDWIDTH,
                         latency=WAN_LATENCY,
                         power_model=PowerModelLink(WAN_WATT_PER_BIT_DOWN))