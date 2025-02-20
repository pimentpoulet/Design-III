from mlx90640_evb9064x import *
from mlx90640 import *
from calibration_class import *
import numpy as np
import cv2


class PowerMeter:
    def __init__(self):
        # Initialisation de la caméra
        self.dev = MLX90640()
        self.dev.i2c_init(evb9064x_get_i2c_comport_url('auto'))
        self.dev.set_refresh_rate(6)
        self.dev.dump_eeprom()
        self.dev.extract_parameters()
        #Initialisation de la structure de données
        self.rows, self.cols = 24, 32
        self.temperature_array = np.zeros((self.rows, self.cols, 1))
        #Initialisation de l'image

    
    def get_temperature(self):
        pass






