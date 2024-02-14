import numpy as np

from src.extendedLeaf.power import WindPower, GridPower, SolarPower

RNG = np.random.default_rng(seed=0)  # Random Number Generator

"""The following two parameters were altered in the different experiments"""
FOG_DCS = 0
FOG_IDLE_SHUTDOWN = False

MEASURE_INFRASTRUCTURE = True
MEASURE_APPLICATIONS = True

"""Simulation duration and intervals in simulated seconds"""
SIMULATION_TIME = 360
CARBON_AWARE = True
UPDATE_MOBILITY_INTERVAL = 3
POWER_MEASUREMENT_INTERVAL = 1
UPDATE_WIFI_CONNECTIONS_INTERVAL = 60

START_TIME = "11:00:00"

""" Farm scenario parameters """
NUMBER_OF_PLOTS = 4
PLOT_NAMES = ["Plot_1", "Plot_2", "Plot_3", "Plot_4"]
PLOT_SIZES = [(500, 500), (1500, 1500), (500, 500), (500, 500)]   # (Width, Height) in meters.
POWER_SOURCES_AVAILABLE = [[SolarPower, WindPower, GridPower],
                           [SolarPower, GridPower],
                           [WindPower, GridPower],
                           [SolarPower]]
STATIC_CONFIG = [False, False, False, True]
DRONE_DISTRIBUTION = [True, True, False, False]
DRONE_RUN_TIMES = ["12:00:00", "13:00:00", None, None]
SENSORS_PER_AXIS = [5, 5, 5, 5]  # Accounts for scrutiny of measurements, more sensors = more detail, more power

""" Drone Configurations """
END_OF_DAY = "19:00:00" #  time in which drones will stop carrying out applications

""" Plot Infrastructure """

SENSOR_CU = 30000  # TODO CHECK
SENSOR_MAX_POWER = 50  # TODO CHECK
SENSOR_STATIC_POWER = 30  # TODO CHECK

FOG_CU = 5000000  # TODO CHECK
FOG_MAX_POWER = 200  # TODO CHECK
FOG_STATIC_POWER = 25  # TODO CHECK
FOG_UTILIZATION_THRESHOLD = 0.85

CLOUD_CU = np.inf
CLOUD_WATT_PER_CU = 700e-6

DRONE_CU = 9000000
DRONE_MAX_POWER = 270
DRONE_STATIC_POWER = 5  # for flying the drone
DRONE_SPEED = 5  # m/s
DRONE_BATTERY_THRESHOLD = 0.2  # battery percent before recharging
DRONE_MEASURE_DENSITY = 1
POWER_PER_UNIT_TRAVELLED = 0.0046 # watts TODO CHECK
DRONE_BATTERY_SIZE = 500

RECHARGE_STATION_STATIC_POWER = 300

"""Network (Latency is only used for determining shortest paths in the routing)"""
WAN_BANDWIDTH = np.inf
WAN_LATENCY = 100
WAN_WATT_PER_BIT_UP = 6658e-9
WAN_WATT_PER_BIT_DOWN = 20572e-9

WIFI_BANDWIDTH = 1.6e9
WIFI_LATENCY = 10
WIFI_TAXI_TO_TL_WATT_PER_BIT = 300e-9
WIFI_TL_TO_TL_WATT_PER_BIT = 100e-9
WIFI_RANGE = 300  # e.g. Cisco Aironet 1570 Series

ETHERNET_BANDWIDTH = 1e9
ETHERNET_LATENCY = 1
ETHERNET_WATT_PER_BIT = 0

""" Sensor Application"""
SENSOR_SOURCE_TASK_CU = 15000
SENSOR_SOURCE_TO_FOG_BIT_RATE = 10e6

SENSOR_FOG_PROCESSOR_CU = 30000
SENSOR_FOG_TO_CLOUD_BIT_RATE = 200e3

SENSOR_CLOUD_TASK_CU = 0

""" Drone Application"""
DRONE_SOURCE_TASK_CU = 900000
DRONE_SOURCE_TO_FOG_BIT_RATE = 5e6

DRONE_FOG_PROCESSOR_CU = 30000
DRONE_FOG_TO_CLOUD_BIT_RATE = 200e3

DRONE_CLOUD_TASK_CU = 0
