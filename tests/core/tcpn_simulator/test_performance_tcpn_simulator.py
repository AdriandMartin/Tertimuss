import sys
import time

import scipy

import scipy.linalg

from core.tcpn_simulator.TcpnSimulator import TcpnSimulator
from core.tcpn_simulator.TcpnSimulatorOptimized import TcpnSimulatorOptimized


def test_performance_petri_net_with_control():
    # Petri net size
    petri_net_size = 300

    # Petri net replications
    # petri_net_replications = 1

    # Simulation steps
    simulation_steps = 100

    # Transitions to P1
    pre_p1 = scipy.asarray(petri_net_size * [1, 0, 0]).reshape((1, -1))
    post_p1 = scipy.asarray(petri_net_size * [1, 0, 0]).reshape((1, -1))

    # Other transitions
    pre = scipy.linalg.block_diag(
        *(petri_net_size * [scipy.asarray([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ])]))

    pre = scipy.concatenate([pre_p1, pre], axis=0)

    post = scipy.linalg.block_diag(
        *(petri_net_size * [scipy.asarray([
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
        ])]))

    post = scipy.concatenate([post_p1, post], axis=0)

    lambda_vector = scipy.asarray(petri_net_size * [1, 1, 1])

    mo = scipy.asarray([1] + (petri_net_size * [3, 0, 0])).reshape((-1, 1))

    tcpn_simulator: TcpnSimulatorOptimized = TcpnSimulatorOptimized(pre, post, lambda_vector)

    # Array where t 3*n + 1 are disabled
    control_model_array = scipy.asarray(petri_net_size * [0, 1, 1])

    # Actual transition enabled
    actual_transition_enabled = 0

    time1 = time.time()
    for _ in range(simulation_steps):
        # Apply control action
        control = scipy.copy(control_model_array)
        control[3 * actual_transition_enabled] = 1
        tcpn_simulator.apply_control(control)

        # Simulate step
        mo = tcpn_simulator.simulate_step(mo, 1)

        # Next transition enabled
        actual_transition_enabled = (actual_transition_enabled + 1) % petri_net_size

    time2 = time.time()

    print("Time taken:", time2 - time1, "s,", "Size of pre:", sys.getsizeof(pre) / 1000000, "MB")
    print("Simulation dimensions:", 3 * petri_net_size, "transitions,", 3 * petri_net_size + 1, "places,",
          simulation_steps, "simulation steps")

    """
    Performance history:
    Version 1: 16 jun, 18:05 -> Time taken: 24.094393014907837 s, Size of pre: 6.487312 MB
                                Simulation dimensions: 900 transitions, 901 places, 100 simulation steps
                                
    Version 2 (Optimized): 17 jun, 12:39 -> Time taken: 1.0696501731872559 s, Size of pre: 6.487312 MB
                                            Simulation dimensions: 900 transitions, 901 places, 100 simulation steps
    """


if __name__ == '__main__':
    test_performance_petri_net_with_control()
