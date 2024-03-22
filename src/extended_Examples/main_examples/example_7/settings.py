import numpy as np

from src.extendedLeaf.power import WindPower, GridPower, SolarPower

"""Simulation duration and intervals in simulated seconds"""
UPDATE_MOBILITY_INTERVAL = 3

START_TIME = "11:00:00"

""" Farm scenario parameters """
NUMBER_OF_PLOTS = 4
PLOT_NAMES = ["Plot_1", "Plot_2", "Plot_3", "Plot_4"]
PLOT_SIZES = [(500, 500), (500, 500), (500, 500), (500, 500)]   # (Width, Height) in meters.
POWER_SOURCES_AVAILABLE = [[SolarPower, WindPower, GridPower],
                           [SolarPower, GridPower],
                           [WindPower],
                           [GridPower]]
STATIC_CONFIG = [False, False, False, True]
DRONE_DISTRIBUTION = [True, True, True, True]
DRONE_RUN_TIMES = ["12:00:00", "12:00:00", "12:00:00", "12:00:00"]
SENSORS_PER_AXIS = [5, 5, 5, 5]  # Accounts for scrutiny of measurements, more sensors = more detail, more power

""" Drone Configurations """
END_OF_DAY = "16:00:00" #  time in which drones will stop carrying out applications

""" Plot Infrastructure """

SENSOR_CU = 10
SENSOR_MAX_POWER = 0.15
SENSOR_STATIC_POWER = 0.007

FOG_CU = 1500
FOG_MAX_POWER = 200
FOG_STATIC_POWER = 25
FOG_UTILIZATION_THRESHOLD = 0.85

CLOUD_CU = np.inf
CLOUD_WATT_PER_CU = 700e-6

DRONE_CU = 30
DRONE_MAX_POWER = 270
DRONE_STATIC_POWER = 5  # for flying the drone
DRONE_SPEED = 5  # m/s
DRONE_BATTERY_THRESHOLD = 0.2  # battery percent before recharging
DRONE_MEASURE_DENSITY = 1
POWER_PER_UNIT_TRAVELLED = 0.02
DRONE_BATTERY_SIZE = 35

WAN_BANDWIDTH = np.inf
WAN_LATENCY = 10
WAN_WATT_PER_BIT_UP = 6658e-9

ETHERNET_BANDWIDTH = 50e6
ETHERNET_LATENCY = 0
ETHERNET_WATT_PER_BIT = 0

""" Sensor Application"""
SENSOR_SOURCE_TASK_CU = 9
SENSOR_SOURCE_TO_FOG_BIT_RATE = 10e6

SENSOR_FOG_PROCESSOR_CU = 50
SENSOR_FOG_TO_CLOUD_BIT_RATE = 200e3

SENSOR_CLOUD_TASK_CU = 150

""" Drone Application"""
DRONE_SOURCE_TASK_CU = 2
DRONE_SOURCE_TO_FOG_BIT_RATE = 5e6

DRONE_FOG_PROCESSOR_CU = 200
DRONE_FOG_TO_CLOUD_BIT_RATE = 200e3

DRONE_CLOUD_TASK_CU = 400
