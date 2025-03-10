from mlx90640_evb9064x import *
from mlx90640 import *
from calibration_class import *
import numpy as np
import cv2


class PowerMeter:
    def __init__(self, buffer_size=32):
        # Initialisation de la caméra
        self.dev = MLX90640()
        self.dev.i2c_init(evb9064x_get_i2c_comport_url('auto'))
        self.dev.set_refresh_rate(6)
        self.dev.dump_eeprom()
        self.dev.extract_parameters()
        #Initialisation de la structure de données
        self.rows, self.cols = 24, 32
        self.buffer_size = buffer_size
        self.temp_arrays = np.zeros((self.buffer_size, self.rows, self.cols), dtype=np.float32)
        self.coeffs_array = np.ones((5, self.rows, self.cols), dtype=np.float32)

    
    def get_temp(self) -> np.ndarray:
        self.dev.get_frame_data()
        temp_amb = self.dev.get_ta() # Compensation de la température ambiante
        emissivity = 1.0
        temp_array = self.dev.calculate_to(emissivity, temp_amb)  # Conversion en températures
        return np.array(temp_array).reshape((self.rows, self.cols))


    def update_temperature(self, temp_array: np.ndarray):
        # Catch error
        if temp_array.shape != (self.rows, self.cols):
            raise ValueError("The shape of the temperature array is not correct")
        if temp_array.dtype != np.float32:
            raise ValueError("The type of the temperature array is not correct")
        # Enlève la plus vieille valeur et ajoute la nouvelle
        self.temp_arrays = np.roll(self.temp_arrays, 1, axis=0)
        self.temp_arrays[0,:,:] = temp_array
    
    
    def get_moy_temp(self) -> np.ndarray:
        # Retourne la moyenne des températures dans le buffer
        return np.mean(self.temp_arrays, axis=0)
    

    def calibrate_temp(self, temp_array: np.ndarray) -> np.ndarray:
        # Retourne la température corrigée
        corrected_temp = np.zeros_like(temp_array)
        powers = np.array([temp_array**i for i in range(4, -1, -1)])
        corrected_temp = np.sum(powers * self.coeffs_array, axis=0)
        return corrected_temp


    def calc_centroid(self) -> tuple:
        temp = self.get_moy_temp()
        moy_temp = np.mean(temp)
        delta_temp = temp - moy_temp
        total_temp = np.sum(delta_temp)
        
        x_coords, y_coords = np.meshgrid(np.arange(self.cols), np.arange(self.rows))
        x_centroid = np.sum(x_coords * delta_temp) / total_temp
        y_centroid = np.sum(y_coords * delta_temp) / total_temp
        
        return (x_centroid, y_centroid)
    

    def find_circle(self):
        temp = self.get_moy_temp()
        circles = cv2.HoughCircles(temp, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=2, maxRadius=16)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            return circles[0,0]
        else:
            return self.calc_centroid()
        
    def temp_gradient(self):
        temp = self.get_moy_temp()
        dx, dy = np.gradient(temp)
        return dx, dy


    def find_max_temp_index(self):
        temp = self.get_moy_temp()
        return np.unravel_index(np.argmax(temp, axis=None), temp.shape)
    

    def extrapolate_temp(self, temp) -> np.ndarray:
        grad = self.temp_gradient()
        pass


    def checkers_grid(self, temp, sq_size, odd_even):
        if odd_even not in (0, 1):
            raise ValueError('odd_even must be 0 or 1')
        grid = np.zeroslike(temp)
        ind = np.indices(temp.shape)
        grid[(ind[0] // sq_size + ind[1] // sq_size) % 2 == odd_even] = temp
        return grid


    def get_wavelength(self) -> float:
        temp = self.get_moy_temp()
        grid1 = self.checkers_grid(temp, 2, 0)
        grid2 = self.checkers_grid(temp, 2, 1)
        pass


    def get_power(self) -> float:
        temp = self.get_moy_temp()
        diff = np.max(temp) - np.min(temp)
        pass