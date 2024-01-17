import simpy

from src.extended_Examples.precision_agriculture.infrastructure import Drone
from src.extended_Examples.precision_agriculture.settings import UPDATE_MOBILITY_INTERVAL, DRONE_BATTERY_THRESHOLD, \
    CARBON_AWARE


class MobilityManager:

    def __init__(self):
        pass

    def run(self, env: simpy.Environment, farm):
        while True:
            for plot in farm.plots:
                drone = plot.drone
                if drone.battery_power.get_current_power() > drone.battery_power.total_power * DRONE_BATTERY_THRESHOLD:
                    self.move_drone(drone, plot, location=plot.recharge_station.location)
                    # # check carbon state
                    if CARBON_AWARE:
                        # TODO Make carbon aware
                        pass
                    else:
                        drone.battery_power.recharge_battery(drone.power_model.power_source)

                else:
                    self.move_drone(drone, plot, self.get_next_location(drone, plot))
                if drone.power_model.location == plot.recharge_station.location:
                    drone.application.dealocate()

            yield env.timeout(UPDATE_MOBILITY_INTERVAL)

    def move_drone(self, drone, plot, location=None):
        if location is None:
            location = self.get_next_location(drone, plot)
            # move to next location
        drone.power_model.location = location

    def get_next_location(self, drone, plot):
        try:
            return next(drone.locations_iterator)
        except StopIteration:
            # Reset the iterator if it reaches the end of the list
            drone.locations_iterator = iter(plot.get_drone_path())
            return next(drone.locations_iterator)

