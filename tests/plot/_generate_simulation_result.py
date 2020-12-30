"""
This file pretends to define an example simulation result that can be used to test the plotting packages
"""
import os
import pickle
from typing import Optional, Tuple, List

from tertimuss.simulation_lib.simulator import RawSimulationResult
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, TaskSet, Job


def create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
                                                period: float, priority: Optional[int]) -> PeriodicTask:
    # Create implicit deadline task with priority equal to identification id
    return PeriodicTask(identification=task_id,
                        worst_case_execution_time=worst_case_execution_time,
                        relative_deadline=period,
                        best_case_execution_time=None,
                        execution_time_distribution=None,
                        memory_footprint=None,
                        priority=priority,
                        preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                        deadline_criteria=Criticality.HARD,
                        energy_consumption=None,
                        phase=None,
                        period=period)


def get_simulation_result() -> Tuple[TaskSet, List[Job], RawSimulationResult]:
    periodic_tasks = [
        create_implicit_deadline_periodic_task_h_rt(3, 3000, 7.0, 3),
        create_implicit_deadline_periodic_task_h_rt(2, 4000, 7.0, 2),
        create_implicit_deadline_periodic_task_h_rt(1, 4000, 14.0, 1),
        create_implicit_deadline_periodic_task_h_rt(0, 3000, 14.0, 0)
    ]

    jobs_list = [
        # Task 3
        Job(identification=0, activation_time=0.0, task=periodic_tasks[0]),
        Job(identification=1, activation_time=7.0, task=periodic_tasks[0]),

        # Task 2
        Job(identification=2, activation_time=0.0, task=periodic_tasks[1]),
        Job(identification=3, activation_time=7.0, task=periodic_tasks[1]),

        # Task 1
        Job(identification=4, activation_time=0.0, task=periodic_tasks[2]),

        # Task 0
        Job(identification=5, activation_time=0.0, task=periodic_tasks[3]),
    ]

    tasks = TaskSet(
        periodic_tasks=periodic_tasks,
        aperiodic_tasks=[],
        sporadic_tasks=[]
    )

    with open(os.path.dirname(os.path.realpath(__file__)) + '/simulation_result.pyobj', 'rb') as simulation_result_file:
        simulation_result = pickle.load(simulation_result_file)

    return tasks, jobs_list, simulation_result
