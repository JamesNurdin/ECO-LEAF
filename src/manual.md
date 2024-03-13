# User manual 

To Create a new simulation model the user should create a new file within the `examples` directory, 
within the file the user should import the necessary classes and methods from the necessary extendedLeaf files.

The user should then proceed to initialise the simulation variable from the simp.Environment() class.
Following this the user should define instances of `applications`, `infrastructure`, `power sources` and `power domains`.
The user may optionally may define any events they want to occur through the `event domain` and `event` classes.

Finally, the user should pass the power domains' `run` command through the simulation variable to execute run the simulation.

An example demonstration follows:
```python
env = simpy.Environment()

""" Infrastructure """
infrastructure = Infrastructure()
node = Node("node3", power_model=PowerModelNode(power_per_cu=20e-3, static_power=20))

""" Power """
power_domain = PowerDomain(env, name="Power Domain 1",
                           powered_infrastructure_distributor=PoweredInfrastructureDistributor(),
                           start_time_str="19:00:00", update_interval=1)
grid = GridPower(env, power_domain=power_domain, priority=5, powered_infrastructure=node, static=True)
power_domain.add_power_source(grid)

""" Application"""
task = SinkTask(cu=10, bound_node=node)
# Place application task
task.allocate(node)

""" Record Power Measurements"""
application_pm = PowerMeter(task, name="application_meter")

# Run simulation
env.process(power_domain.run(env))
env.process(application_pm.run(env))
env.run(until=10)  # run simulation for 10 seconds

logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

```