import logging

import numpy as np
import simpy
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain, PowerDomainEvent
from src.extendedLeaf.file_handler import FileHandler
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, BatteryPower, PoweredInfrastructureDistributor, PowerSource

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    """

    """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    sensor = Node("node1", cu=10, power_model=PowerModelNode(max_power=0.5e-3, static_power=0.1e-3))  # source
    microprocessor = Node("node2", cu=40,
                          power_model=PowerModelNode(max_power=2.5, static_power=0.5))  # processing task
    server = Node("node3", power_model=PowerModelNode(power_per_cu=5e-3, static_power=5))  # sink

    # #two Wi-Fi links between 1 -> 2 and 2 -> 3
    wired_link_from_source = Link(name="Link1", src=sensor, dst=microprocessor, latency=0, bandwidth=10e6,
                                  power_model=PowerModelLink(200e-6))
    wifi_link_to_server = Link(name="Link2", src=microprocessor, dst=server, latency=10, bandwidth=5e6,
                               power_model=PowerModelLink(200e-9))
    infrastructure.add_link(wifi_link_to_server)
    infrastructure.add_link(wired_link_from_source)
    entities = infrastructure.nodes() + infrastructure.links()

    power_domain = PowerDomain(env, name="Power Domain 1", powered_infrastructure=entities,powered_infrastructure_distributor=PoweredInfrastructureDistributor(custom_distribution_method),
                               start_time_str="11:00:00", update_interval=1)
    event_domain = EventDomain(env, update_interval=2, start_time_str="11:00:00")
    grid = GridPower(env, power_domain=power_domain, priority=5)
    solar_power = SolarPower(env, power_domain=power_domain, priority=0)
    battery_power = BatteryPower(env, power_domain=power_domain, priority=1)
    power_domain.add_power_source(solar_power)
    power_domain.add_power_source(battery_power)
    power_domain.add_power_source(grid)

    # Initialise three tasks
    source_task = SourceTask(cu=9, bound_node=sensor)
    processing_task = ProcessingTask(cu=5)
    sink_task = SinkTask(cu=10, bound_node=server)

    # Build Application
    application = Application()
    application.add_task(source_task)
    application.add_task(processing_task, incoming_data_flows=[(source_task, 100)])
    application.add_task(sink_task, incoming_data_flows=[(processing_task, 500)])

    # Place over Infrastructure
    orchestrator = SimpleOrchestrator(infrastructure, power_domain)
    event_domain.add_event(PowerDomainEvent(event=battery_power.recharge_battery, args=[solar_power], time_str="11:00:00", repeat=True,
                         repeat_counter=1440))
    event_domain.add_event(PowerDomainEvent(event=orchestrator.place, args=[application], time_str="12:00:00", repeat=True,
                         repeat_counter=60))
    event_domain.add_event(PowerDomainEvent(event=application.deallocate, args=[], time_str="12:30:00", repeat=True,
                         repeat_counter=60))

    # Early power meters when exploring isolated power measurements
    application_pm = PowerMeter(application, name="application_meter")
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    source_task_pm = PowerMeter(source_task, name="Source Task")
    processing_task_pm = PowerMeter(processing_task, name="Processing Task")
    sink_task_pm = PowerMeter(sink_task, name="Sink Task")

    # Run simulation
    env.process(power_domain.run(env))
    env.process(event_domain.run())

    env.process(application_pm.run(env))
    env.process(infrastructure_pm.run(env))

    env.process(source_task_pm.run(env))
    env.process(processing_task_pm.run(env))
    env.process(sink_task_pm.run(env))

    env.run(until=1500)

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    fig2 = file_handler.subplot_time_series_entities(power_domain, "Power Used", entities=entities, events=event_domain.event_history)
    fig3 = file_handler.subplot_time_series_power_sources(power_domain, "Power Used", power_sources=[solar_power, battery_power])
    fig4 = file_handler.subplot_time_series_power_meter(power_domain, power_meters=[source_task_pm, processing_task_pm, sink_task_pm])
    figs = [fig2, fig3, fig4]
    main_fig = file_handler.aggregate_subplots(figs)
    file_handler.write_figure_to_file(main_fig, len(figs))
    main_fig.show()

def custom_distribution_method(current_power_source: PowerSource, power_domain):
    """Update renewable sources"""
    for entity in power_domain.powered_infrastructure:
        if entity.power_model.power_source == current_power_source:
            current_entity_power_requirement = float(entity.power_model.update_sensitive_measure(
                power_domain.update_interval))
            if current_power_source.get_current_power() < current_entity_power_requirement:
                current_power_source.remove_entity(entity)
            else:
                current_power_source.consume_power(current_entity_power_requirement)

    """Check if any unpowered infrastructure is able to be powered"""
    for entity in power_domain.powered_infrastructure:
        if entity.power_model.power_source is None:
            current_entity_power_requirement = float(entity.power_model.update_sensitive_measure(
                power_domain.update_interval))
            if current_entity_power_requirement < current_power_source.get_current_power():
                if isinstance(entity.power_model, PowerModelNode) and entity.power_model.max_power is None:
                    if current_power_source.remaining_power == np.inf:
                        current_power_source.add_entity(entity)
                        current_power_source.consume_power(current_entity_power_requirement)
                        continue  # Skip the rest of the loop for this entity
                    else:
                        continue  # Skip the rest of the loop for this entity

                # If not an infinite power source or not a node with unlimited power, continue here
                current_power_source.add_entity(entity)
                current_power_source.consume_power(current_entity_power_requirement)

    """Check if any entities in lower priority power sources can move up if excess energy is available"""
    for entity in power_domain.powered_infrastructure:
        if entity.power_model.power_source is not None \
                and entity.power_model.power_source.priority > current_power_source.priority:
            current_entity_power_requirement = float(entity.power_model.update_sensitive_measure(
                power_domain.update_interval))

            if current_entity_power_requirement < current_power_source.get_current_power():
                if isinstance(entity.power_model, PowerModelNode) and entity.power_model.max_power is None:
                    if current_power_source.remaining_power == np.inf:
                        entity.power_model.power_source.remove_entity(entity)
                        current_power_source.add_entity(entity)
                        current_power_source.consume_power(current_entity_power_requirement)
                        continue  # Skip the rest of the loop for this entity
                    else:
                        continue  # Skip the rest of the loop for this entity

                # If not an infinite power source or not a node with unlimited power, continue here
                entity.power_model.power_source.remove_entity(entity)
                current_power_source.add_entity(entity)
                current_power_source.consume_power(current_entity_power_requirement)


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("node2")


if __name__ == '__main__':
    main()
