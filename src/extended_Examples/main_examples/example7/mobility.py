import simpy

from src.extendedLeaf.power import PowerDomain
from src.extended_Examples.main_examples.example7.settings import *


class MobilityManager:

    def __init__(self):
        pass

    def run(self, env: simpy.Environment, farm):
        while True:
            for plot in farm.plots:
                if plot.drone is not None:
                    if ((env.now + plot.power_domain.start_time_index) % 1440) >= PowerDomain.get_current_time(DRONE_RUN_TIMES[plot.plot_index]):
                        if plot.drone.application.last_execution_time != (env.now + plot.power_domain.start_time_index) // 1440:
                            env.process(self.run_drone(env, plot))
                            plot.drone.application.last_execution_time = (env.now + plot.power_domain.start_time_index) // 1440
            yield env.timeout(1)

    def run_drone(self, env: simpy.Environment, plot):
        """
        GENERAL PATH
            drone moves throughout the plot
            at each location on travel path the application is placed signaling that a reading is occuring
            before each traversal to the next location a check occurs to ensure that their is enough power
                if there's enough continue
                else return back to the recharge point
            once at the end of the path:
                return to the recharge point
                recharge if available option
                deallocate application
        """
        drone = plot.drone
        while ((env.now + plot.power_domain.start_time_index) % 1440) < PowerDomain.get_current_time(END_OF_DAY):
            if drone.battery_power.get_current_power() < drone.battery_power.get_total_power() * DRONE_BATTERY_THRESHOLD:
                self.move_drone(drone, plot, location=plot.recharge_station_location)
                recharge_time = drone.battery_power.find_and_recharge_battery()
                yield env.timeout(recharge_time)
            else:
                self.move_drone(drone, plot, self.get_next_location(drone, plot))
                plot.orchestrator.place(drone.application)
                yield env.timeout(UPDATE_MOBILITY_INTERVAL)
                drone.application.deallocate()

    def move_drone(self, drone, plot, location=None):
        if location is None:
            location = self.get_next_location(drone, plot)
            # move to next location
        distance = drone.location.distance(location)
        drone.battery_power.consume_power(distance * drone.power_per_unit_traveled)
        plot.power_domain.record_power_consumption(drone, drone.battery_power, distance * drone.power_per_unit_traveled)
        drone.location = location

    def get_next_location(self, drone, plot):
        try:
            return next(drone.locations_iterator)
        except StopIteration:
            # Reset the iterator if it reaches the end of the list
            drone.locations_iterator = iter(plot.get_drone_path())
            return next(drone.locations_iterator)

