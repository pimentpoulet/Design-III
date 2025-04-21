import numpy as np

from mlx90640_evb9064x import *
from mlx90640 import *
from powermeter import PowerMeter


class PowerMeter_test(PowerMeter):

    def __init__(self):
        super().__init__()

    def get_test_moy_temp(self):
        """
        Retourne une valeur moyenne de températures aléatoires
        """
        return np.mean(25.0 + 20 * np.random.rand(self.rows, self.cols))
