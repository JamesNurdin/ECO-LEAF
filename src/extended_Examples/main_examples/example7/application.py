from src.extendedLeaf.application import Application, ProcessingTask, SourceTask, SinkTask
from src.extended_Examples.main_examples.example7.settings import *


class SensorApplication(Application):

    def __init__(self, name, source_node, sink_node):
        super().__init__(name)
        self.source_node = source_node
        print(source_node)
        self.sink_node = sink_node

        source_task = SourceTask(cu=SENSOR_SOURCE_TASK_CU, bound_node=self.source_node)
        self.add_task(source_task)
        processing_task = ProcessingTask(cu=SENSOR_FOG_PROCESSOR_CU)
        self.add_task(processing_task, incoming_data_flows=[(source_task, SENSOR_SOURCE_TO_FOG_BIT_RATE)])
        sink_task = SinkTask(cu=SENSOR_CLOUD_TASK_CU, bound_node=self.sink_node)
        self.add_task(sink_task, incoming_data_flows=[(processing_task, SENSOR_FOG_TO_CLOUD_BIT_RATE)])


class DroneApplication(Application):

    def __init__(self, name, source_node, sink_node):
        super().__init__(name)
        self.source_node = source_node
        self.sink_node = sink_node
        source_task = SourceTask(cu=DRONE_SOURCE_TASK_CU, bound_node=self.source_node)
        self.add_task(source_task)
        processing_task = ProcessingTask(cu=DRONE_FOG_PROCESSOR_CU)
        self.add_task(processing_task, incoming_data_flows=[(source_task, DRONE_SOURCE_TO_FOG_BIT_RATE)])
        sink_task = SinkTask(cu=DRONE_CLOUD_TASK_CU, bound_node=self.sink_node)
        self.add_task(sink_task, incoming_data_flows=[(processing_task, DRONE_FOG_TO_CLOUD_BIT_RATE)])
        self.last_execution_time = -1
