import logging

import networkx as nx
import simpy
import random as rnd
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain
from src.extendedLeaf.file_handler import FileHandler
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, BatteryPower, PoweredInfrastructureDistributor, PowerDomainEvent
from src.extended_Examples.main_examples.medium_2_example.settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')
rnd.seed(100)

""""""

def create_sensors():
    sensors = []
    for current_sensor_index in range(NO_SENSORS):
        max_power = rnd.gauss(SENSOR_MAX_POWER_MEAN, SENSOR_MAX_POWER_STD_DEVIATION)
        static_power = rnd.gauss(SENSOR_STATIC_POWER_MEAN, SENSOR_STATIC_POWER_STD_DEVIATION)
        cu = rnd.gauss(SENSOR_CU_POWER_MEAN, SENSOR_CU_STD_DEVIATION)
        sensors.append(Node(f"Sensor{current_sensor_index}", cu=cu,
                            power_model=PowerModelNode(max_power=max_power, static_power=static_power)))
    return sensors

def create_microprocessors():
    microprocessors = []
    for current_sensor_index in range(NO_MICROPROCESSORS):
        max_power = rnd.gauss(MICROPROCESSORS_MAX_POWER_MEAN, MICROPROCESSORS_MAX_POWER_STD_DEVIATION)
        static_power = rnd.gauss(MICROPROCESSORS_STATIC_POWER_MEAN, MICROPROCESSORS_STATIC_POWER_STD_DEVIATION)
        cu = rnd.gauss(MICROPROCESSORS_CU_POWER_MEAN, MICROPROCESSORS_CU_STD_DEVIATION)
        microprocessors.append(Node(f"Microprocessor{current_sensor_index}", cu=cu,
                            power_model=PowerModelNode(max_power=max_power, static_power=static_power)))
    return microprocessors

def create_links_from_sensors(sensors, microprocessors):
    links = []
    for sensor in sensors:
        microprocessor = rnd.choice(microprocessors)
        bandwidth = rnd.gauss(WIRED_BANDWIDTH_MEAN, WIRED_BANDWIDTH_STD_DEVIATION)
        energy_per_bit = rnd.gauss(WIRED_ENERGY_PER_BIT_MEAN, WIRED_ENERGY_PER_BIT_STD_DEVIATION)
        links.append(Link(name=f"Link_from{sensor.name}_to_{microprocessor.name}", src=sensor, dst=microprocessor,
                          latency=0, bandwidth=bandwidth, power_model=PowerModelLink(energy_per_bit)))
    return links

def create_links_to_server(microprocessors, server):
    links = []
    for microprocessor in microprocessors:
        bandwidth = rnd.gauss(WIRELESS_BANDWIDTH_MEAN, WIRELESS_BANDWIDTH_STD_DEVIATION)
        energy_per_bit = rnd.gauss(WIRELESS_ENERGY_PER_BIT_MEAN, WIRELESS_ENERGY_PER_BIT_STD_DEVIATION)
        links.append(Link(name=f"Link_from{microprocessor.name}_to_{server.name}", src=microprocessor,
                          dst=server, latency=0, bandwidth=bandwidth, power_model=PowerModelLink(energy_per_bit)))
    return links

def create_applications(sensors, server):
    applications = []
    for sensor in sensors:
        app1_source_task = SourceTask(cu=0.9*sensor.power_model.max_power, bound_node=sensor)
        app1_processing_task = ProcessingTask(cu=3)
        app1_sink_task = SinkTask(cu=12, bound_node=server)

        application = Application(name=f"Application{sensor.name}")

        application.add_task(app1_source_task)
        application.add_task(app1_processing_task, incoming_data_flows=[(app1_source_task, 1000)])
        application.add_task(app1_sink_task, incoming_data_flows=[(app1_processing_task, 300)])

        applications.append(application)
    return applications


def main():
    """

    """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    sensors = create_sensors()
    microprocessors = create_microprocessors()
    server = Node("Server", power_model=PowerModelNode(power_per_cu=SERVER_POWER_PER_CU, static_power=SERVER_STATIC_POWER))  # sink

    links_from_sensors = create_links_from_sensors(sensors, microprocessors)
    links_to_server = create_links_to_server(microprocessors, server)
    for link in links_from_sensors + links_to_server:
        infrastructure.add_link(link)
    entities = sensors + microprocessors + links_from_sensors + links_to_server

    power_domain = PowerDomain(env, name="Power Domain 1",
                               start_time_str="10:00:00", update_interval=1, powered_infrastructure_distributor=
                               PoweredInfrastructureDistributor(static_powered_infrastructure=True))
    solar_power = SolarPower(env, power_domain=power_domain, priority=1, powered_infrastructure=[])
    grid_power = GridPower(env, power_domain=power_domain, priority=5, powered_infrastructure=[server]+links_to_server)
    battery_power = BatteryPower(env, power_domain=power_domain, priority=0, total_power_available=30,
                                 powered_infrastructure=sensors+microprocessors+links_from_sensors)
    power_domain.add_power_source(battery_power)
    power_domain.add_power_source(solar_power)
    power_domain.add_power_source(grid_power)

    applications = create_applications(sensors, server)

    orchestrator = CustomOrchestrator(infrastructure, power_domain)
    for application in applications:
        orchestrator.place(application)

    events = [
        PowerDomainEvent(event=battery_power.recharge_battery, args=[solar_power], time="10:30:00", repeat=True, repeat_counter=500)]



    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    # Run simulation
    env.process(power_domain.run(env))

    env.process(infrastructure_pm.run(env))



    env.run(until=600)

    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    fig2 = file_handler.subplot_time_series_entities(power_domain, "Power Used", events=events, entities=entities)
    fig3 = file_handler.subplot_time_series_power_sources(power_domain, "Power Used", events=events, power_sources=[solar_power, battery_power])
    fig3 = file_handler.subplot_time_series_power_sources(power_domain, "Power Available", events=events, power_sources=[battery_power])
    figs = [fig2, fig3]
    main_fig = file_handler.aggregate_subplots(figs)
    file_handler.write_figure_to_file(main_fig, len(figs))
    main_fig.show()


class CustomOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        source_node = application.tasks(type_filter=SourceTask)[0].node
        dest_node = self.infrastructure.node("Server")
        paths = list(nx.all_simple_paths(self.infrastructure.graph, source=source_node.name, target=dest_node.name))

        return self.infrastructure.node(paths[0][1])


if __name__ == '__main__':
    main()
