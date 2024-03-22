from src.extendedLeaf.mobility import Location
from src.extended_Examples.main_examples.example_7.application import SensorApplication, DroneApplication
from src.extended_Examples.main_examples.example_7.settings import *
from src.extendedLeaf.infrastructure import Link, Node
from src.extendedLeaf.power import PowerModelLink, PowerModelNode, BatteryPower


class Cloud(Node):
    def __init__(self):
        super().__init__("cloud", cu=CLOUD_CU, power_model=PowerModelNode(power_per_cu=CLOUD_WATT_PER_CU))


class CropSensor(Node):
    def __init__(self, infrastructure, plot, sensor_index, location):
        super().__init__(name=f"CropSensor_{plot.name}__{sensor_index}",
                         cu=SENSOR_CU,
                         power_model=PowerModelNode(max_power=SENSOR_MAX_POWER, static_power=SENSOR_STATIC_POWER),
                         location=location)
        infrastructure.add_node(self)
        cloud = infrastructure.nodes(type_filter=Cloud)[0]
        self.application = SensorApplication(f"Plot_{plot.plot_index}_Sensor_Application", self, cloud)


class FogNode(Node):
    def __init__(self, plot, location):
        super().__init__(name=f"FogNode_{plot.name}",
                         cu=FOG_CU,
                         power_model=PowerModelNode(max_power=FOG_MAX_POWER, static_power=SENSOR_STATIC_POWER),
                         location=location)


class Drone(Node):
    def __init__(self, plot, location, env, power_domain, infrastructure):
        super().__init__(name=f"Drone_{plot.name}",
                         cu=DRONE_CU,
                         power_model=PowerModelNode(max_power=DRONE_MAX_POWER, static_power=DRONE_STATIC_POWER),
                         location=location)
        cloud = infrastructure.nodes(type_filter=Cloud)[0]
        self.application = DroneApplication(f"Plot_{plot.plot_index}_Drone_Application", self, cloud)
        self.power_per_unit_traveled = POWER_PER_UNIT_TRAVELLED
        self.battery_power = BatteryPower(env, name=f"Battery_{plot.name}", power_domain=power_domain, priority=1,
                                          total_power_available=DRONE_BATTERY_SIZE, static=True, powered_infrastructure=[self],
                                          charge_rate=DRONE_BATTERY_SIZE/120)
        self.locations_iterator = plot.get_drone_path()


class LinkEthernet(Link):
    def __init__(self, src: Node, dst: Node, name: str):
        super().__init__(src=src,
                         dst=dst,
                         bandwidth=ETHERNET_BANDWIDTH,
                         latency=ETHERNET_LATENCY,
                         power_model=PowerModelLink(ETHERNET_WATT_PER_BIT),
                         name=name)


class LinkWanUp(Link):
    def __init__(self, src: Node, dst: Node, name: str):
        super().__init__(src=src,
                         dst=dst,
                         bandwidth=WAN_BANDWIDTH,
                         latency=WAN_LATENCY,
                         power_model=PowerModelLink(WAN_WATT_PER_BIT_UP),
                         name=name)

