from mlx90640_evb9064x import *
from mlx90640 import *
from calibration_class import *
import numpy as np
from powermeter import PowerMeter


class PowerMeter_calibration(PowerMeter):
    def __init__(self, current_temp: float, calibration_time: int, refresh_rate=6):
        # Catch error
        if refresh_rate < 1 or refresh_rate > 7:
            raise ValueError("Refresh rate invalide")
        # Initialisation de la caméra
        super().__init__()
        self.dev.set_refresh_rate(refresh_rate)
        self.dev.dump_eeprom()
        self.dev.extract_parameters()
        # Initialisation des paramètres de calibration
        self.temp = current_temp
        self.refresh_rate = refresh_rate
        self.remove_frames = 2**(refresh_rate-1)
        self.number_of_frames = calibration_time*refresh_rate

    # def get_diff(self, data, wanted_temp):
    #     diff = data - np.ones_like(data) * wanted_temp
    #     return diff

    # def update_moy_diff(self, moy_diff, data, filename):
    #     # Add new data array to the 3rd dimension
    #     moy_diff = np.concatenate((moy_diff, data[:, :, np.newaxis]), axis=2)
    #     print(moy_diff.shape)
    #     # Calculate the mean value element-wise along the 3rd dimension, ignoring the initialisation array

    #     if moy_diff.shape[2] > self.number_of_frames+self.remove_frames:
    #         mean_moy_diff = np.mean(moy_diff[:, :, self.remove_frames: self.remove_frames+self.number_of_frames], axis=2)*-1+self.temp
            
    #         # Save the mean_moy_diff to a file
    #         np.savetxt(filename, mean_moy_diff, fmt='%.6f')
    #         #exit()
    #         return moy_diff, mean_moy_diff
    #     return moy_diff, np.zeros((self.rows, self.cols))




