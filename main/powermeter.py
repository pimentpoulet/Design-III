from mlx90640_evb9064x import *
from mlx90640 import *
import numpy as np
import cv2


class PowerMeter:
    def __init__(self, buffer_size=32, emissivity=1.0):

        # Initialisation de la caméra si indisponible
        self.camera_available = False
        self.emissivity = emissivity

        # Initialisation de la caméra si disponible
        try:
            self.dev = MLX90640()
            try:
                self.dev.set_debug(False)
            except:
                pass
            self.dev.i2c_init(evb9064x_get_i2c_comport_url('auto'))
            self.dev.set_refresh_rate(6)
            self.dev.dump_eeprom()
            self.dev.extract_parameters()
            self.camera_available = True
        except Exception as e:
            self.dev = None
            # print(f" Erreur: Initialisation de la caméra impossible --> Le capteur n'est pas branché.")

        # Initialisation de la structure de données
        self.rows, self.cols = 24, 32
        self.buffer_size = buffer_size
        self.temp_arrays = np.zeros((self.buffer_size, self.rows, self.cols), dtype=np.float32)
        self.coeffs_array = np.ones((5, self.rows, self.cols), dtype=np.float32)

    def get_temp(self) -> np.ndarray:
        """
        Retourne une matrice de températures si la caméra est disponible
        """
        if not self.camera_available:
            print(" La caméra n'est pas disponible.")
            return np.zeros((self.rows, self.cols), dtype=np.float32)

        self.dev.get_frame_data()
        temp_amb = self.dev.get_ta()    # Compensation de la température ambiante
        self.emissivity = 1.0
        temp_array = self.dev.calculate_to(self.emissivity, temp_amb)    # Conversion en températures
        return np.array(temp_array).reshape((self.rows, self.cols))

    def update_temperature(self, temp_array: np.ndarray):
        """
        Ajoute une nouvelle température dans le buffer et enlève la plus vieille
        """
        if temp_array.shape != (self.rows, self.cols):
            raise ValueError(" The shape of the temperature array is not correct")
        self.temp_arrays = np.roll(self.temp_arrays, 1, axis=0)
        self.temp_arrays[0,:,:] = temp_array

    def get_moy_temp(self) -> np.ndarray:
        """
        Retourne la moyenne des températures dans le buffer
        """
        return np.mean(self.temp_arrays, axis=0)

    def calibrate_temp(self, temp_array: np.ndarray) -> np.ndarray:
        """
        Retourne la température corrigée
        """
        corrected_temp = np.zeros_like(temp_array)
        powers = np.array([temp_array**i for i in range(4, -1, -1)])
        corrected_temp = np.sum(powers * self.coeffs_array, axis=0)
        return corrected_temp

    def calc_centroid(self) -> tuple:
        """
        Calcule le centre de masse des températures
        """
        temp = self.get_moy_temp()
        moy_temp = np.mean(temp)
        delta_temp = temp - moy_temp
        total_temp = np.sum(delta_temp)

        x_coords, y_coords = np.meshgrid(np.arange(self.cols), np.arange(self.rows))
        x_centroid = np.sum(x_coords * delta_temp) / total_temp
        y_centroid = np.sum(y_coords * delta_temp) / total_temp

        return (x_centroid, y_centroid)

    def find_circle(self):
        """
        To be defined
        """
        temp = self.get_moy_temp()
        circles = cv2.HoughCircles(temp, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=2, maxRadius=16)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            return circles[0,0]
        else:
            return self.calc_centroid()

    def temp_gradient(self):
        """
        Calcule le gradient de température
        """
        temp = self.get_moy_temp()
        dx, dy = np.gradient(temp)
        return dx, dy

    def find_max_temp_index(self):
        """
        To be defined
        """
        temp = self.get_moy_temp()
        return np.unravel_index(np.argmax(temp, axis=None), temp.shape)

    def extrapolate_temp(self, temp) -> np.ndarray:
        """
        Extrapolation de la température
        """
        grad = self.temp_gradient()
        pass

    def checkers_grid(self, temp, sq_size, odd_even):
        """
        To be defined
        """
        if odd_even not in (0, 1):
            raise ValueError(' odd_even must be 0 or 1')
        grid = np.zeroslike(temp)
        ind = np.indices(temp.shape)
        grid[(ind[0] // sq_size + ind[1] // sq_size) % 2 == odd_even] = temp
        return grid

    def get_wavelength(self) -> float:
        """
        Calcule la longueur d'onde
        """
        temp = self.get_moy_temp()
        grid1 = self.checkers_grid(temp, 2, 0)
        grid2 = self.checkers_grid(temp, 2, 1)
        pass

    def get_power(self) -> float:
        """
        Calcule la puissance
        """
        temp = self.get_moy_temp()
        diff = np.max(temp) - np.min(temp)
        pass

    def cleanup(self):
        """
        Termine la communication I2C
        """
        if self.dev is not None:
            try:
                self.dev.i2c_tear_down()
            except Exception as e:
                print(f" Erreur lors de la fermeture de la connexion I2C : {e}")

    def get_test_moy_temp(self):
        """
        Retourne une valeur moyenne de températures aléatoires
        """
        return np.mean(25.0 + 20 * np.random.rand(self.rows, self.cols))
