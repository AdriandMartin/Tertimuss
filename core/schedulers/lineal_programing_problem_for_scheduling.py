import scipy.optimize

import numpy as np

from core.kernel_generator.thermal_model import ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


def solve_lineal_programing_problem_for_scheduling(tasks_specification: TasksSpecification,
                                                   cpu_specification: CpuSpecification,
                                                   environment_specification: EnvironmentSpecification,
                                                   simulation_specification: SimulationSpecification,
                                                   thermal_model: ThermalModel) -> [np.ndarray, np.ndarray, float,
                                                                                    np.ndarray]:
    h = tasks_specification.h
    ti = np.asarray(list(map(lambda task: task.t, tasks_specification.tasks)))
    cci = np.asarray(list(map(lambda task: task.c, tasks_specification.tasks)))
    ia = h / ti
    n = len(tasks_specification.tasks)
    m = cpu_specification.number_of_cores

    # Inequality constraint
    # Create matrix diag([cc1/H ... ccn/H cc1/H .....]) of n*m
    ch_vector = np.asarray(m * list(map(lambda task: task.c / h, tasks_specification.tasks)))

    c_h = np.diag(ch_vector)

    a_int = - ((thermal_model.s_t.dot(np.linalg.inv(thermal_model.a_t))).dot(thermal_model.ct_exec)).dot(c_h)
    b_int = environment_specification.t_max * np.ones((m, 1)) + (
        (thermal_model.s_t.dot(np.linalg.inv(thermal_model.a_t))).dot(
            thermal_model.b_ta.reshape((len(thermal_model.a_t), 1)))) * environment_specification.t_env

    au = np.zeros((m, m * n))

    a_eq = np.tile(np.eye(n), m)

    for j in range(0, m):
        for i in range(0, n):
            au[j, i + j * n] = tasks_specification.tasks[i].c / h

    beq = np.transpose(ia)
    bu = np.ones((m, 1))

    # Initial condition
    x0 = np.zeros((n * m, 1))

    # Variable bounds
    bounds = (n * m) * [(0, None)]

    # Objective function
    objetive = np.ones(n * m)

    # Optimization
    a = np.concatenate((a_int, au))
    b = np.concatenate((b_int.transpose(), bu.transpose()), axis=1)

    res = scipy.optimize.linprog(c=objetive, A_ub=a, b_ub=b, A_eq=a_eq,
                                 b_eq=beq, bounds=bounds, method='interior-point')

    if not res.success:
        # No solution found
        print("No solution")
        # TODO: Return error or throw exception
        return None

    jBi = res.x

    jFSCi = jBi * ch_vector

    walloc = jFSCi

    # Solve differential equation to get a initial condition
    theta = scipy.linalg.expm(thermal_model.a_t * h)

    beta_1 = (scipy.linalg.inv(thermal_model.a_t)).dot(
        theta - np.identity(len(thermal_model.a_t)))
    beta_2 = beta_1.dot(thermal_model.b_ta.reshape((len(thermal_model.a_t), 1)))
    beta_1 = beta_1.dot(thermal_model.ct_exec)

    # TODO: Revisar a partir de aqui [8,20;32,20]

    # Inicializa la condicion inicial en ceros para obtener una condicion inicial=final SmT(0)=Y(H)
    mT0 = np.zeros((len(thermal_model.a_t), 1))
    mT = theta.dot(mT0) + beta_1.dot(walloc) + beta_2 * environment_specification.t_env
    temp = thermal_model.s_t.dot(mT)

    # Quantum calc
    jobs = ia
    diagonal = np.zeros((len(tasks_specification.tasks), int(jobs.max())))

    for i in range(0, len(tasks_specification.tasks)):
        diagonal[i, 0: int(jobs[i])] = list(range(ti[i], h + 1, ti[i]))

    # TODO: Revisar
    sd = diagonal[0, 0:int(jobs[0])]

    for i in range(2, n + 1):
        sd = np.union1d(sd, diagonal[i - 1, 0:int(jobs[i - 1])])

    sd = np.union1d(sd, 0)

    quantum = 0.0

    for i in range(2, len(sd)):
        rounded = np.round([quantum] + sd[i] * jFSCi, 4)
        quantum = np.gcd.reduce(rounded.transpose())

    if quantum < simulation_specification.step:
        quantum = simulation_specification.step

    walloc_Max = jFSCi / quantum
    mT_max = theta * mT0 + beta_1 * walloc_Max + beta_2 * environment_specification.t_env
    temp_max = thermal_model.s_t * mT_max

    if temp_max / m > environment_specification.t_max:
        print("No solution...")
        # TODO: Return error or throw exception
        return None

    return jBi, jFSCi, quantum, mT
