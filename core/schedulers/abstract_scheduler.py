import abc
from typing import Optional

import scipy

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from output_generation.abstract_progress_bar import AbstractProgressBar


class SchedulerResult(object):
    def __init__(self, m: scipy.ndarray, mo: scipy.ndarray, timez: scipy.ndarray, sch_oldtfs: scipy.ndarray,
                 mexec: scipy.ndarray, mexec_tcpn: scipy.ndarray, time_step: scipy.ndarray, time_temp: scipy.ndarray,
                 temperature_cont: scipy.ndarray, temperature_disc: scipy.ndarray, quantum:float):
        self.m = m
        self.mo = mo
        self.timez = timez
        self.sch_oldtfs = sch_oldtfs
        self.mexec = mexec
        self.mexec_tcpn = mexec_tcpn
        self.time_step = time_step
        self.time_temp = time_temp
        self.temperature_cont = temperature_cont
        self.temperature_disc = temperature_disc
        self.quantum = quantum


class AbstractScheduler(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def simulate(self, global_specification: GlobalSpecification,
                 simulation_kernel: SimulationKernel, progress_bar: Optional[AbstractProgressBar]) -> SchedulerResult:
        pass
