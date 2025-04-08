from mlx90640_evb9064x import *
from mlx90640 import *
from calibration_class import *
import numpy as np
import cv2
from scipy.optimize import curve_fit


class PowerMeter:
    def __init__(self, buffer_size=32):
        # Initialisation de la caméra
        self.camera_available = False

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
            print(f" Erreur: Initialisation de la caméra impossible --> {e}.")

        # Initialisation de la structure de données
        self.rows, self.cols = 24, 32
        self.buffer_size = buffer_size
        self.temp_arrays = np.zeros((self.buffer_size, self.rows, self.cols), dtype=np.float32)
        try:
            self.coeffs_array = np.load("coeffs_range20.0-150.0_jump5.0.npy")
        except FileNotFoundError as e:
            self.coeffs_array = np.zeros((5, self.rows, self.cols))
            self.coeffs_array[-2,:,:] = 1.0
            print(f"Erreur: Coefficients de calibration non trouvés --> {e}.")

    def get_temp(self) -> np.ndarray:
        self.dev.get_frame_data()
        temp_amb = self.dev.get_ta() # Compensation de la température ambiante
        emissivity = 1.0
        temp_array = self.dev.calculate_to(emissivity, temp_amb)  # Conversion en températures
        return np.array(temp_array).reshape((self.rows, self.cols))

    def update_temperature(self, temp_array: np.ndarray = None):
        # Catch error
        if temp_array is None:
            temp_array = self.get_temp()
        if temp_array.shape != (self.rows, self.cols):
            raise ValueError("The shape of the temperature array is not correct")
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

    def checkers_grid(self, sq_size: int, odd_even):
        if odd_even not in (0, 1):
            raise ValueError('odd_even must be 0 or 1')
        grid = np.empty((self.rows, self.cols))
        grid[:,:] = np.nan
        ind = np.indices(grid.shape)
        grid[(ind[0] // sq_size + ind[1] // sq_size) % 2 == odd_even] = 1
        return grid

    def gaussian2D(xy, h_1, h_2, amp, k, sigma):
        x_1, x_2 = xy
        return (amp * np.exp(-((x_1 - h_1) ** 2 + (x_2 - h_2) ** 2) / (2 * (sigma ** 2)))+k).ravel()

    def fit_2Dgauss(self, grid: np.ndarray):
        a, b = self.find_max_temp_index()
        x, y = np.indices(grid.shape)
        to_fit = grid[x, y]
        params, cov = curve_fit(lambda i, j, k, amp, sigma: 
                                k+ amp*np.exp(-((i-a)**2 + (j-b)**2) / (sigma**2))
                                ,x
                                ,y
                                ,to_fit
                                ,p0=[1, 1, 1])
        return params, cov

    def get_gaussian_params(self) -> float:
        temp = self.get_moy_temp()
        grid1 = self.checkers_grid(temp, 2, 0)
        grid2 = self.checkers_grid(temp, 2, 1)
        params1, cov1 = self.fit_2Dgauss(grid1)
        params2, cov2 = self.fit_2Dgauss(grid2)
        c_1, c_2 = params1[:2], params2[:2]
        amp1, amp2 = params1[3], params2[3]
        sigma1, sigma2 = params1[4], params2[4]
        k_1, k_2 = params1[2], params2[2]
        return (c_1, amp1, sigma1, k_1), (c_2, amp2, sigma2, k_2)

    def get_center(self, params: tuple) -> tuple:
        c_1, c_2 = params[0][0], params[1][0]
        if c_1 == c_2:
            return c_1
        else:
            return (c_1[0] + c_2[0]) / 2, (c_1[1] + c_2[1]) / 2

    def get_power(self, params: tuple, plaque: int) -> float:
        if plaque not in (0, 1):
            raise ValueError('plaque must be 0 or 1')
        p_max = params[plaque][1]
        p_min = params[plaque][3]
        p_diff = p_max - p_min
        pass

    def get_wavelength(self, params: tuple) -> float:
        pass
