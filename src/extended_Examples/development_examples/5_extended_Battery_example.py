import logging
import simpy
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain, Event
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, \
    GridPower, PowerDomain, PoweredInfrastructureDistributor, BatteryPower, PowerModelLink, SolarPower

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    """
    Log Output:
        INFO	Placing Application(tasks=3):
        INFO	- SourceTask(id=0, cu=0.4) on Node('node1', cu=0/10).
        INFO	- ProcessingTask(id=1, cu=5) on Node('node2', cu=0/40).
        INFO	- SinkTask(id=2, cu=1) on Node('node3', cu=0/20).
        INFO	- DataFlow(bit_rate=1000) on [Link('node1' -> 'node2', bandwidth=0/30000000.0, latency=10)].
        INFO	- DataFlow(bit_rate=300) on [Link('node2' -> 'node3', bandwidth=0/50000000.0, latency=12)].
        DEBUG	0: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        DEBUG	1: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        DEBUG	2: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	2: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        ...
        DEBUG	47: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	47: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        DEBUG	48: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	48: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        DEBUG	49: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	49: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        INFO	Total application power usage: 1536.5209999999997 Ws
        INFO	Total infrastructure power usage: 8036.499999999993 Ws
        INFO	Total carbon emitted: 12.021292868666656 gCo2

    """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    node1 = Node("node1", cu=10, power_model=PowerModelNode(max_power=30, static_power=3))  # source
    node2 = Node("node2", cu=40, power_model=PowerModelNode(max_power=70, static_power=10))  # processing task
    node3 = Node("node3", cu=20, power_model=PowerModelNode(max_power=50, static_power=7))  # sink
    node4 = Node("node4", cu=100, power_model=PowerModelNode(max_power=130, static_power=20))
    # three nodes 1,2,3
    # #two Wi-Fi links between 1 -> 2 and 2 -> 3
    wifi_link_from_source = Link(name="Link1", src=node1, dst=node2, latency=10, bandwidth=30e6, power_model=PowerModelLink(300e-9))
    wifi_link_to_sink = Link(name="Link2", src=node2, dst=node3, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    wifi_link_to_node4 = Link(name="Link3", src=node2, dst=node4, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    infrastructure.add_link(wifi_link_to_sink)
    infrastructure.add_link(wifi_link_from_source)
    infrastructure.add_link(wifi_link_to_node4)

    entities = infrastructure.nodes()+infrastructure.links()

    power_domain = PowerDomain(env, name="Power Domain 1", powered_infrastructure=entities,
                               start_time_str="10:00:00", update_interval=1, powered_infrastructure_distributor=PoweredInfrastructureDistributor())
    battery_power = BatteryPower(env, power_domain=power_domain, priority=0, total_power_available=100)
    grid1 = GridPower(env, power_domain=power_domain, priority=5)
    sol = SolarPower(env, power_domain=power_domain, priority=1)
    power_domain.add_power_source(battery_power)
    power_domain.add_power_source(sol)
    event_domain = EventDomain(env, update_interval=1, start_time_str="10:00:00")
    event_domain.add_event(
        Event(event=battery_power.recharge_battery, args=[sol], time_str="10:40:00", repeat=False))

    # Initialise three tasks
    source_task = SourceTask(cu=0.4, bound_node=node1)
    processing_task = ProcessingTask(cu=5)
    sink_task = SinkTask(cu=1, bound_node=node3)

    # Initialise and allocate a separate task for Node 4
    task = Task(cu=100)
    task.allocate(node4)

    # Build Application
    application = Application()
    application.add_task(source_task)
    application.add_task(processing_task, incoming_data_flows=[(source_task, 1000)])
    application.add_task(sink_task, incoming_data_flows=[(processing_task, 300)])

    # Place over Infrastructure
    orchestrator = SimpleOrchestrator(infrastructure, power_domain)
    orchestrator.place(application)

    # Early power meters when exploring isolated power measurements
    application_pm = PowerMeter(application, name="application_meter")
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    env.process(power_domain.run(env))  # registering power metering process 2
    env.process(event_domain.run())  # registering power metering process 2

    # Run simulation
    env.process(application_pm.run(env))  # registering power metering process 2
    env.process(infrastructure_pm.run(env))  # registering power metering process 2
    env.run(until=50)  # run simulation for 10 seconds

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("node2")

if __name__ == '__main__':
    main()
