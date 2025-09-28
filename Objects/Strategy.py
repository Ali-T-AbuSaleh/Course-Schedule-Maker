from enum import Enum


class Strategy(Enum):
    SIMULATED_ANNEALING = 1
    STEEPEST_AHC = 2
    EVALUATE_GIVEN_SCHEDULE = 3
