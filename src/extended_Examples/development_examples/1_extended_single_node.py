import logging
import simpy

from src.extendedLeaf.application import Task
from src.extendedLeaf.infrastructure import Node
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, SolarPower
from src.extendedLeaf.power import PowerDomain

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    """Simple example that adds and removes a task from a single node

    Log Output:
        DEBUG	0: PowerMeter1: PowerMeasurement(dynamic=0.00W, static=10.00W)
        DEBUG	1: PowerMeter1: PowerMeasurement(dynamic=0.00W, static=10.00W)
        DEBUG	2: PowerMeter1: PowerMeasurement(dynamic=0.00W, static=10.00W)
        INFO	task has been added at 3
        DEBUG	3: PowerMeter1: PowerMeasurement(dynamic=20.00W, static=10.00W)
        DEBUG	4: PowerMeter1: PowerMeasurement(dynamic=20.00W, static=10.00W)
        DEBUG	5: PowerMeter1: PowerMeasurement(dynamic=20.00W, static=10.00W)
        DEBUG	6: PowerMeter1: PowerMeasurement(dynamic=20.00W, static=10.00W)
        DEBUG	7: PowerMeter1: PowerMeasurement(dynamic=20.00W, static=10.00W)
        INFO	task has been removed at 8
        DEBUG	8: PowerMeter1: PowerMeasurement(dynamic=0.00W, static=10.00W)
        DEBUG	9: PowerMeter1: PowerMeasurement(dynamic=0.00W, static=10.00W)
        INFO	Total power usage: 200.0 Ws
        INFO	Total carbon emitted: 0.1533333333333333 gCo2
    """
    # Initializing infrastructure and workload
    node = Node("node1", cu=100, power_model=PowerModelNode(max_power=30, static_power=10))
    task = Task(cu=100)

    power_meter = PowerMeter(node, name="PowerMeter1")

    env = simpy.Environment()  # creating SimPy simulation environment

    power_domain = PowerDomain(env, name="Power Domain 1", powered_infrastructure=[node], start_time_str="19:00:00",
                               update_interval=1)  # Creating Power domain to run at 7pm
    solar_power = SolarPower(env, name="Solar", power_domain=power_domain,
                             priority=0)  # Solar power with the highest priority
    power_domain.add_power_source(solar_power)  # Attaching solar power to power domain

    env.process(placement(env, node, task))  # registering workload placement process
    env.process(power_meter.run(env))  # registering power metering process
    env.process(power_domain.run(env))  # registering power domain process

    env.run(until=10)  # run simulation for 10 seconds

    logger.info(f"Total power usage: {float(PowerMeasurement.sum(power_meter.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")


def placement(env, node, task):
    """Places the task after 3 seconds and removes it after 8 seconds."""
    yield env.timeout(3)
    task.allocate(node)
    logger.info(f'task has been added at {env.now}')
    yield env.timeout(5)
    task.deallocate()
    logger.info(f'task has been removed at {env.now}')


if __name__ == '__main__':
    main()
