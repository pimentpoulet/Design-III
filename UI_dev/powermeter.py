import numpy as np
import cv2

from mlx90640_evb9064x import *
from mlx90640 import *
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter, median_filter, uniform_filter
from scipy.signal import savgol_filter


class PowerMeter_nocam:
    def __init__(self, gain: float=0.5, tau: float=0.1, buffer_size: int=32, time_series: int=16):
        # Initialisation de la structure de données
        self.rows, self.cols = 24, 32
        self.gain = gain
        self.tau = tau
        self.buffer_size = buffer_size
        self.temp_arrays = np.zeros((self.buffer_size, self.rows, self.cols), dtype=np.float32)
        self.time_series = time_series
        self.time_series_array = np.zeros((self.time_series), dtype=np.float32)
        try:
            self.coeffs_array = np.load("coeffs_range20.0-150.0_jump5.0.npy")
        except FileNotFoundError as e:
            self.coeffs_array = np.zeros((5, self.rows, self.cols))
            self.coeffs_array[-2,:,:] = 1.0
            print(f"Erreur: Coefficients de calibration non trouvés --> {e}.")

    def get_temp(self, data: np.ndarray , i: int) -> np.ndarray:
        # Retourne la température à partir des données
        return data[i,:,:]

    def update_temperature(self, temp_array: np.ndarray = None):
        # Catch error
        if temp_array is None:
            temp_array = self.get_temp()
        if temp_array.shape != (self.rows, self.cols):
            raise ValueError("The shape of the temperature array is not correct")
        # Enlève la plus vieille valeur et ajoute la nouvelle
        self.temp_arrays = np.roll(self.temp_arrays, 1, axis=0)
        self.temp_arrays[0,:,:] = temp_array

    def update_time_series(self, time_series: int):
        # Enlève la plus vieille valeur et ajoute la nouvelle
        self.time_series_array = np.roll(self.time_series_array, 1)
        self.time_series_array[0] = time_series

    def filter_time_series(self, time_series: None) -> np.ndarray:
        if time_series is not None:
            self.update_time_series(time_series)
        return savgol_filter(self.time_series_array, 8, 3, mode='nearest')[-1]

    def get_moy_temp(self, half = None) -> np.ndarray:
        if half is None:
            # Retourne la moyenne des températures dans le buffer
            return self.calibrate_temp(np.mean(self.temp_arrays, axis=0))
        elif half == 0:
            # Retourne la moyenne des températures dans la première moitié du buffer
            return self.calibrate_temp(np.mean(self.temp_arrays[:self.buffer_size//2, :, :], axis=0))
        elif half == 1:
            # Retourne la moyenne des températures dans la seconde moitié du buffer
            return self.calibrate_temp(np.mean(self.temp_arrays[self.buffer_size//2:, :, :], axis=0))
        else:
            raise ValueError("half must be 0 or 1")

    def calibrate_temp(self, temp_array: np.ndarray) -> np.ndarray:
        # Retourne la température corrigée
        corrected_temp = np.zeros_like(temp_array)
        powers = np.array([temp_array**i for i in range(4, -1, -1)])
        corrected_temp = np.sum(powers * self.coeffs_array, axis=0)
        return corrected_temp
    
    def filter_temp(self, temp_array: np.ndarray) -> np.ndarray:
        # Enlève les pixels aberrants et le bruit plus fin
        filtered_temp = np.copy(temp_array)
        # filtered_temp = median_filter(np.copy(temp_array), size=3)

        mean_local = uniform_filter(filtered_temp, size=3)
        diff = filtered_temp - mean_local
        std_local = np.sqrt(uniform_filter(diff**2, size=3))
        z_score = np.abs(diff) / (std_local+1e-6)
        filtered_temp[z_score > 2.4] = np.nan

        # Applique un filtre gaussien
        # filtered_temp = gaussian_filter(filtered_temp, sigma=1.5)
        return filtered_temp

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

    def checkers_grid(self, sq_size: int, odd_even: int) -> np.ndarray:
        if odd_even not in (0, 1):
            raise ValueError('odd_even must be 0 or 1')
        grid = np.empty((self.rows, self.cols))
        grid[:,:] = np.nan
        ind = np.indices(grid.shape)
        grid[((ind[0]) // sq_size + (ind[1]) // sq_size) % 2 == odd_even] = 1
        return grid

    def gaussian2D(self, xy, h_0, h_1, amp, k, sigma):
        x_0, x_1 = xy
        return (amp * np.exp(-((x_0 - h_0) ** 2 + (x_1 - h_1) ** 2) / (2 * (sigma ** 2)))+k).ravel()

    def fit_2Dgauss(self, grid: np.ndarray):
        a, b = self.find_max_temp_index()
        x, y = np.indices(grid.shape)
        params, cov = curve_fit(self.gaussian2D
                            ,(x.ravel(), y.ravel())
                            ,grid.ravel()
                            ,p0=[a, b, 50, 24, 1]
                            ,nan_policy='omit')
        return params, cov

    def get_gaussian_params(self, odd_even: int, half = None) -> tuple:
        """ Donne les paramètres de la gaussienne 2D pour un cadrillé qui dépend de
        odd_even et pour la moitié du buffer choisie (half: 0 ou 1) ou l'ensemble du
         buffer (half: None)."""
        temp = self.filter_temp(self.get_moy_temp(half))
        # grid = self.checkers_grid(4, odd_even)*temp
        params, cov = self.fit_2Dgauss(temp)
        c = params[:2]
        amp= params[2]
        k = params[3]
        sigma = params[4]
        return (c, amp, k, sigma), cov
    
    def get_power(self, plaque: int = 0) -> float:
        """ Retourne la puissance en fonction des paramètres de la gaussienne 2D pour une plaque."""
        params0, cov1, params1, cov2 = self.get_gaussian_params(plaque, 0), self.get_gaussian_params(plaque, 1)
        p_diff0, p_diff1 = params0[1], params1[1]
        refresh = 6
        dt = self.buffer_size /2 / (2**(refresh-1))
        P = (self.tau*(p_diff1-p_diff0) / dt + p_diff1)*self.gain
        return P
        
    def get_center(self, params0: tuple, params1: tuple) -> tuple:
        """ Retourne le centre de la gaussienne 2D pour deux cadrillés différents."""
        c_0, c_1 = params0[0], params1[0]
        if c_0 == c_1:
            return c_0
        else:
            return (c_0[0] + c_1[0]) / 2, (c_0[1] + c_1[1]) / 2

    def get_wavelength(self, params: tuple) -> float:
        pass


class PowerMeter(PowerMeter_nocam):
    def __init__(self, gain: float=0.5, tau: float=0.1, buffer_size: int = 32):
        super().__init__(gain, tau, buffer_size)
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

    def get_power(self, plaque: int = 0) -> float:
        """ Retourne la puissance en fonction des paramètres de la gaussienne 2D pour une plaque."""
        params0, params1 = self.get_gaussian_params(plaque, 0), 
        p_diff0, p_diff1 = params0[1]-params0[2], params1[1]-params1[2]
        refresh = self.dev._get_refresh_rate()
        dt = self.buffer_size /2 / (2**(refresh-1))
        P = (self.tau*(p_diff1-p_diff0) / dt + p_diff1)*self.gain
        return P
