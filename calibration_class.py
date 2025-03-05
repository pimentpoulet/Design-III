from mlx90640_evb9064x import *
from mlx90640 import *
import numpy as np
from powermeter import PowerMeter


class PowerMeter_calibration(PowerMeter):
    def __init__(self, reference_temp: float, calibration_time: int,
                 refresh_rate: int =6):
        # Catch error
        if refresh_rate < 1 or refresh_rate > 7:
            raise ValueError("Refresh rate invalide")
        # Initialisation de la caméra
        fps = 2**(refresh_rate-1)
        super().__init__(fps*calibration_time)
        self.dev.set_refresh_rate(refresh_rate)
        self.dev.dump_eeprom()
        self.dev.extract_parameters()
        # Initialisation des paramètres de calibration
        self.ref_temp = reference_temp
        self.refresh_rate = refresh_rate
        self.remove_frames = fps
        self.number_of_frames = calibration_time*fps


    def temp_diff(self) -> np.ndarray:
        # Retourne la différence de température par rapport à la température de référence)
        temp = self.get_temperature()
        return np.ones_like(temp) * self.ref_temp - temp




