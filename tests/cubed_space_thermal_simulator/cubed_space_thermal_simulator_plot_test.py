import unittest

from cubed_space_thermal_simulator import UnitDimensions, UnitLocation, \
    ExternalEnergyLocatedCube, InternalEnergyLocatedCube, CubedSpace, ThermalUnits, SolidMaterialLocatedCube, \
    obtain_min_temperature, obtain_max_temperature, plot_3d_heat_map_temperature_located_cube_list

from cubed_space_thermal_simulator.materials_pack import CooperSolidMaterial, SiliconSolidMaterial, \
    AirFreeEnvironmentProperties, AirForcedEnvironmentProperties


class CubedSpaceThermalSimulatorPlotTest(unittest.TestCase):
    def test_processor_heat_generation_plot(self):
        # Dimensions of the core
        core_dimensions = UnitDimensions(x=3, z=1, y=3)

        # Material of the core
        core_material = SiliconSolidMaterial()

        # Material of the board
        board_material = CooperSolidMaterial()

        # Core initial temperature
        # core_initial_temperature = 273.15 + 65
        core_0_initial_temperature = 273.15 + 65
        core_1_initial_temperature = 273.15 + 25
        core_2_initial_temperature = 273.15 + 25
        core_3_initial_temperature = 273.15 + 25

        # Board initial temperature
        board_initial_temperature = 273.15 + 25

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Min simulation value
        min_simulation_value = board_initial_temperature - 10
        max_simulation_value = core_0_initial_temperature + 10

        # Definition of the CPU shape and materials
        cpu_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=1, z=2, y=1),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            1: SolidMaterialLocatedCube(
                location=UnitLocation(x=6, z=2, y=1),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            2: SolidMaterialLocatedCube(
                location=UnitLocation(x=1, z=2, y=6),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),
            3: SolidMaterialLocatedCube(
                location=UnitLocation(x=6, z=2, y=6),
                dimensions=core_dimensions,
                solidMaterial=core_material
            ),

            # Board
            4: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=UnitDimensions(x=10, z=2, y=10),
                solidMaterial=board_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = AirFreeEnvironmentProperties()

        # CPU energy consumption configuration
        #  Dynamic power = dynamic_alpha * F^3 + dynamic_beta
        #  Leakage power = current temperature * 2 * leakage_delta + leakage_alpha
        leakage_alpha: float = 0.001
        leakage_delta: float = 0.1
        dynamic_alpha: float = 1.52
        dynamic_beta: float = 0.08

        cpu_frequency: float = 1000

        # External heat generators
        external_heat_generators = {
            # Dynamic power
            0: ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=1),
                dimensions=core_dimensions,
                energy=dynamic_alpha * (cpu_frequency ** 3) + dynamic_beta,
                period=1
            ),

            # Leakage power
            1: ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=1),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            2: ExternalEnergyLocatedCube(
                location=UnitLocation(x=6, z=2, y=1),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            3: ExternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=6),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            ),
            4: ExternalEnergyLocatedCube(
                location=UnitLocation(x=6, z=2, y=6),
                dimensions=core_dimensions,
                energy=1,
                period=leakage_alpha
            )
        }

        # Internal heat generators
        internal_heat_generators = {
            0: InternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=1),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            1: InternalEnergyLocatedCube(
                location=UnitLocation(x=6, z=2, y=1),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            2: InternalEnergyLocatedCube(
                location=UnitLocation(x=1, z=2, y=6),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            ),
            3: InternalEnergyLocatedCube(
                location=UnitLocation(x=6, z=2, y=6),
                dimensions=core_dimensions,
                temperatureFactor=2,
                period=leakage_delta
            )
        }

        # Generate cubed space
        cubed_space = CubedSpace(
            material_cubes=cpu_definition,
            cube_edge_size=cube_edge_size,
            fixed_external_energy_application_points=external_heat_generators,
            fixed_internal_energy_application_points=internal_heat_generators,
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            material_cubes_temperatures={
                0: core_0_initial_temperature,
                1: core_1_initial_temperature,
                2: core_2_initial_temperature,
                3: core_3_initial_temperature,
                4: board_initial_temperature
            },
            environment_temperature=environment_temperature
        )

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[0, 1, 2, 3, 4],
                                                 internal_energy_application_points=[0, 1, 2, 3], amount_of_time=0.5)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[0, 1, 2, 3, 4],
                                                 internal_energy_application_points=[0, 1, 2, 3], amount_of_time=0.5)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            units=ThermalUnits.CELSIUS)

        # Zero seconds
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_zero_seconds,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)

        print("Temperature before 0 seconds: min", min_temperature, ", max", max_temperature)

        # Half second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_half_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature = obtain_max_temperature(temperature_over_before_half_second)

        print("Temperature before 0.5 seconds: min", min_temperature, ", max", max_temperature)

        # One second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_one_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature = obtain_max_temperature(temperature_over_before_one_second)

        print("Temperature before 1 second: min", min_temperature, ", max", max_temperature)

    def test_external_conduction_plot(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=4, z=4, y=4)

        # Cube 0 material
        cube_0_material = SiliconSolidMaterial()

        # Cube 1 material
        cube_1_material = CooperSolidMaterial()

        # Core initial temperature
        cube_0_initial_temperature = 273.15 + 65
        cube_1_initial_temperature = 273.15 + 25

        # Board initial temperature
        environment_temperature = 273.15 + 15

        # Min simulation value
        min_simulation_value = cube_1_initial_temperature - 10
        max_simulation_value = cube_0_initial_temperature + 10

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cube_0_material
            ),
            1: SolidMaterialLocatedCube(
                location=UnitLocation(x=cubes_dimensions.x, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cube_1_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = AirForcedEnvironmentProperties()

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            fixed_external_energy_application_points={},
            fixed_internal_energy_application_points={},
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            material_cubes_temperatures={
                0: cube_0_initial_temperature,
                1: cube_1_initial_temperature
            },
            environment_temperature=environment_temperature
        )

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.1)
        temperature_over_before_point_one_seconds = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                                   units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.1)
        temperature_over_before_point_two_seconds = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                                   units=ThermalUnits.CELSIUS)

        # Zero seconds
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_zero_seconds,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)

        print("Temperature before 0 seconds: min", min_temperature, ", max", max_temperature)

        # Half second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_point_one_seconds,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_point_one_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_point_one_seconds)

        print("Temperature before 0.1 seconds: min", min_temperature, ", max", max_temperature)

        # One second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_point_two_seconds,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_point_two_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_point_two_seconds)

        print("Temperature before 0.2 second: min", min_temperature, ", max", max_temperature)

    def test_internal_conduction_plot(self):
        # Dimensions of the cubes
        cubes_dimensions = UnitDimensions(x=2, z=2, y=2)

        # Cube 0 material
        cube_0_material = CooperSolidMaterial()

        # Core initial temperature
        cube_0_initial_temperature = 273.15 + 65

        # Board initial temperature
        environment_temperature = 273.15 + 25

        # Min simulation value
        min_simulation_value = cube_0_initial_temperature - 10
        max_simulation_value = cube_0_initial_temperature + 10

        # Definition of the CPU shape and materials
        scene_definition = {
            # Cores
            0: SolidMaterialLocatedCube(
                location=UnitLocation(x=0, z=0, y=0),
                dimensions=cubes_dimensions,
                solidMaterial=cube_0_material
            )
        }

        # Edge size pf 1 mm
        cube_edge_size = 0.001

        # Environment properties
        environment_properties = AirForcedEnvironmentProperties()

        cubed_space = CubedSpace(
            material_cubes=scene_definition,
            cube_edge_size=cube_edge_size,
            fixed_external_energy_application_points={},
            fixed_internal_energy_application_points={},
            environment_properties=environment_properties,
            simulation_precision="HIGH")

        initial_state = cubed_space.create_initial_state(
            default_temperature=environment_temperature,
            material_cubes_temperatures={
                0: cube_0_initial_temperature
            },
            environment_temperature=environment_temperature
        )

        # Initial temperatures
        temperature_over_before_zero_seconds = cubed_space.obtain_temperature(
            actual_state=initial_state,
            units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.9)
        temperature_over_before_half_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                             units=ThermalUnits.CELSIUS)

        # Apply energy over the cubed space
        initial_state = cubed_space.apply_energy(actual_state=initial_state,
                                                 external_energy_application_points=[],
                                                 internal_energy_application_points=[], amount_of_time=0.9)
        temperature_over_before_one_second = cubed_space.obtain_temperature(actual_state=initial_state,
                                                                            units=ThermalUnits.CELSIUS)

        # Zero seconds
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_zero_seconds,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_zero_seconds)
        max_temperature = obtain_max_temperature(temperature_over_before_zero_seconds)

        print("Temperature before 0 seconds: min", min_temperature, ", max", max_temperature)

        # Half second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_half_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_half_second)
        max_temperature = obtain_max_temperature(temperature_over_before_half_second)

        print("Temperature before 0.5 seconds: min", min_temperature, ", max", max_temperature)

        # One second
        plot_3d_heat_map_temperature_located_cube_list(temperature_over_before_one_second,
                                                       min_temperature=min_simulation_value,
                                                       max_temperature=max_simulation_value)

        min_temperature = obtain_min_temperature(temperature_over_before_one_second)
        max_temperature = obtain_max_temperature(temperature_over_before_one_second)

        print("Temperature before 1 second: min", min_temperature, ", max", max_temperature)


if __name__ == '__main__':
    unittest.main()
