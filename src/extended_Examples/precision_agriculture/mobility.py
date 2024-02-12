import simpy

from src.extended_Examples.precision_agriculture.infrastructure import Drone
from src.extended_Examples.precision_agriculture.power import PowerDomain
from src.extended_Examples.precision_agriculture.settings import *


class MobilityManager:

    def __init__(self):
        pass

    def run(self, env: simpy.Environment, farm):
        while True:
            for plot in farm.plots:
                if plot.drone is not None:
                    if (env.now % 1440) >= PowerDomain.get_current_time(DRONE_RUN_TIMES[plot.plot_index]):
                        if plot.drone.last_execution_time != env.now // 1440:
                            print(f"Running drone path at {PowerDomain.convert_to_time_string(env.now)}")
                            env.process(self.run_drone(env, plot))
                            plot.drone.last_execution_time = env.now // 1440
            yield env.timeout(1)

    def run_drone(self, env: simpy.Environment, plot):
        """
        GENERAL PATH
            drone moves throughout the plot
            at each location on travel path the application is placed signaling that a reading is occuring
            before each traversal to the next location a check occurs to ensure that their is enough power
                if theres enough continue
                else return back to the recharge point
            once at the end of the path:
                return to the recharge point
                recharge if available option
                deallocate application
        """
        drone = plot.drone
        while (env.now % 1440) < PowerDomain.get_current_time(END_OF_DAY):
            if drone.battery_power.get_current_power() < drone.battery_power.total_power * DRONE_BATTERY_THRESHOLD:
                self.move_drone(drone, plot, location=plot.recharge_station.location)
                # # check carbon state
                if CARBON_AWARE:
                    # TODO Make carbon aware choice
                    recharge_time = drone.battery_power.find_and_recharge_battery()
                else:
                    recharge_time = drone.battery_power.find_and_recharge_battery()
                yield env.timeout(recharge_time)
            else:
                self.move_drone(drone, plot, self.get_next_location(drone, plot))

                yield env.timeout(UPDATE_MOBILITY_INTERVAL)

    def move_drone(self, drone, plot, location=None):
        if location is None:
            location = self.get_next_location(drone, plot)
            # move to next location
        distance = drone.location.distance(location)
        drone.battery_power.consume_battery_power(distance * drone.power_per_unit_traveled)
        drone.location = location

    def get_next_location(self, drone, plot):
        try:
            return next(drone.locations_iterator)
        except StopIteration:
            # Reset the iterator if it reaches the end of the list
            drone.locations_iterator = iter(plot.get_drone_path())
            return next(drone.locations_iterator)

