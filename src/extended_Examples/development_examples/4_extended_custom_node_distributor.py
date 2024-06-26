import logging
import simpy
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain, Event
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, PowerSource, PoweredInfrastructureDistributor

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
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	1: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        ...
        DEBUG	118: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	118: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        DEBUG	119: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	119: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        DEBUG	120: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	120: infrastructure_meter: PowerMeasurement(dynamic=120.73W, static=40.00W)
        INFO	Total application power usage: 3718.380820000001 Ws
        INFO	Total infrastructure power usage: 7618.329999999999 Ws
        INFO	Total carbon emitted: 25.4386033 gCo2
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
    entities.remove(node4)

    power_domain = PowerDomain(env, name="Power Domain 1", powered_infrastructure=entities,
                               start_time_str="19:00:00", update_interval=1, powered_infrastructure_distributor=
                               PoweredInfrastructureDistributor(custom_distribution_method))
    solar_power = SolarPower(env, power_domain=power_domain, priority=0)
    grid1 = GridPower(env, power_domain=power_domain, priority=5)
    wind_power = WindPower(env, power_domain=power_domain, priority=0)
    power_domain.add_power_source(wind_power)
    power_domain.add_power_source(grid1)

    event_domain = EventDomain(env, update_interval=1, start_time_str="19:00:00")
    event_domain.add_event(Event(event=power_domain.remove_power_source, args=[wind_power], time_str="19:20:00", repeat=False))
    event_domain.add_event(Event(event=power_domain.add_power_source, args=[solar_power], time_str="19:40:00", repeat=False))
    event_domain.add_event(Event(event=power_domain.add_entity, args=[node4], time_str="20:30:00", repeat=False))

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

    env.process(power_domain.run(env))
    env.process(event_domain.run())

    # Run simulation
    env.process(application_pm.run(env))  # registering power metering process 2
    env.process(infrastructure_pm.run(env))  # registering power metering process 2
    env.run(until=121)  # run simulation for 10 seconds

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")


def custom_distribution_method(current_power_source: PowerSource, power_domain):
    """Update renewable sources"""

    for entity in power_domain.powered_infrastructure:
        current_entity_power_requirement = float(entity.power_model.update_sensitive_measure(power_domain.update_interval))

        """Check if entity is currently being powered by the desired power source"""
        if entity.power_model.power_source == current_power_source:
            if current_power_source.get_current_power() < current_entity_power_requirement:
                entity.power_model.power_source = None
                current_power_source.remove_entity(entity)
            else:
                current_power_source.consume_power(current_entity_power_requirement)
            continue

        """Check if entity is currently unpowered"""
        if entity.power_model.power_source is None and current_entity_power_requirement < current_power_source.get_current_power():
            current_power_source.add_entity(entity)
            entity.power_model.power_source = current_power_source
            current_power_source.consume_power(current_entity_power_requirement)
            continue


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("node2")

if __name__ == '__main__':
    main()
