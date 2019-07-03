import hashlib
import time
import unittest

from core.kernel_generator.thermal_model import generate_thermal_model, ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask


class TestThermalModel(unittest.TestCase):

    def test_basic_thermal_model(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8),
                                                                      PeriodicTask(3, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1)

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        thermal_model: ThermalModel = generate_thermal_model(tasks_specification, cpu_specification,
                                                             environment_specification,
                                                             simulation_specification)

        # Test with hashes, the probability of collision is low
        self.assertEqual(hashlib.md5(thermal_model.a_t).hexdigest(), "5bcfdc9c7a849c0935c9ae822a7c9e32")
        self.assertEqual(hashlib.md5(thermal_model.s_t).hexdigest(), "a85eecf3696207bab2885c80afe431ed")
        self.assertEqual(hashlib.md5(thermal_model.b_ta).hexdigest(), "823913eb86ac188e94da606c19275e62")
        self.assertEqual(hashlib.md5(thermal_model.ct_exec).hexdigest(), "3ebb3fc4224b5dd3e3b6ec4f9fe1faee")
        self.assertEqual(hashlib.md5(thermal_model.lambda_gen).hexdigest(), "1c507ed6c044af516be945b78605f1d2")

    def test_basic_thermal_model_performance(self):

        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8),
                                                                      PeriodicTask(3, 12, 9.6),
                                                                      PeriodicTask(4, 16, 6.1),
                                                                      PeriodicTask(2, 10, 12)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=80, y=80, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               4, 1)

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        print("Generating thermal mode")
        time_1 = time.time()
        thermal_model: ThermalModel = generate_thermal_model(tasks_specification, cpu_specification,
                                                             environment_specification,
                                                             simulation_specification)
        time_2 = time.time()

        print(time_2 - time_1)


if __name__ == '__main__':
    unittest.main()
