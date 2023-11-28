import logging

from extended_Examples.custom_federated_learning_example.infrastructure import *
from extended_Examples.custom_federated_learning_example.mobility import MobilityManager
from extended_Examples.custom_federated_learning_example.university import City
import simpy
from extended_Examples.custom_federated_learning_example.settings import *
from extendedLeaf.power import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')

"""A Global business has many sites across the world, a local site exists in
 Glasgow and it's employees frequently require access to various data throughout the day in particular 
 they often want to access the same files and websites. To accommodate this local 
 caches are set up in the server room to reduce repeated network traffic, over time
 requests that are repeatedly made are added to the site to reduce outside network traffic.
 At the end of the day the cache's are cleared to make space for the next day."""


def main():
    env = simpy.Environment()
    local_site = City(env)
    mobility_manager = MobilityManager(local_site)
    mobility_manager.run(env, local_site)

    power_domain = PowerDomain(env, name="Power Domain1", associated_nodes=local_site.infrastructure.nodes(), start_time_str="11:00:00",
                               update_interval=1)
    solar_power1 = SolarPower(env,name="sol1", power_domain=power_domain,
                             data_set_filename="08-08-2020 Glasgow pv data.csv", priority=0)
    solar_power2 = SolarPower(env,name="sol2", power_domain=power_domain,
                             data_set_filename="08-08-2020 Glasgow pv data.csv", priority=1)
    solar_power3 = SolarPower(env,name="sol3", power_domain=power_domain,
                              data_set_filename="08-08-2020 Glasgow pv data.csv", priority=2)
    grid_power = GridPower(env, power_domain=power_domain,
                           data_set_filename="08-08-2023 national carbon intensity.csv", priority=5)
    power_domain.add_power_source(solar_power1)
    power_domain.add_power_source(solar_power2)
    power_domain.add_power_source(solar_power3)
    power_domain.add_power_source(grid_power)

    client_application_pm = PowerMeter(lambda: [client.application for client in local_site.infrastructure.nodes(type_filter=Client)],
                                name="Client Application Meter", measurement_interval=POWER_MEASUREMENT_INTERVAL)
    cluster_application_pm = PowerMeter(lambda: [cluster.application for cluster in local_site.infrastructure.nodes(type_filter=ClusteredClient)],
                                name="Cluster Application Meter", measurement_interval=POWER_MEASUREMENT_INTERVAL)
    infrastructure_pm = PowerMeter(local_site.infrastructure, name="infrastructure_meter", measurement_interval=1)
    server_pm = PowerMeter(entities=local_site.infrastructure.nodes(type_filter=Server)[0], name="Server")
    client_pm = PowerMeter(lambda: [client for client in local_site.infrastructure.nodes(type_filter=Client)],
                           name="Client meter", measurement_interval=POWER_MEASUREMENT_INTERVAL)
    clustered_client_pm = PowerMeter(lambda: [cluster for cluster in local_site.infrastructure.nodes
    (type_filter=ClusteredClient)], name="Clustered Client meter", measurement_interval=POWER_MEASUREMENT_INTERVAL)


    if MEASURE_ISOLATED_INFRASTRUCTURE:
        env.process(infrastructure_pm.run(env))  # registering power metering process 2
        env.process(clustered_client_pm.run(env))  # registering power metering process 2
        env.process(client_pm.run(env))  # registering power metering process 2
        env.process(server_pm.run(env))  # registering power metering process 2
        env.process(power_domain.run(env))  # registering power metering process 2

    if MEASURE_APPLICATIONS:
        env.process(client_application_pm.run(env))  # registering power metering process 2
        env.process(cluster_application_pm.run(env))  # registering power metering process 2

    env.run(until=SIMULATION_TIME)
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")


if __name__ == '__main__':
    main()
