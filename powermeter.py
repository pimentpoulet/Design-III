import numpy as np

from mlx90640_evb9064x import *
from mlx90640 import *
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter, median_filter
from random import gauss


class PowerMeter_nocam:
    def __init__(self, gain: float=1.15, tau: float=0.8, integ: float=0.5, offset: float= 3,
                  buffer_size: int=32, time_series: int=5, backup: tuple=(0.0, (0.0,0.0))):
        # Initialisation de la structure de données
        self.rows, self.cols = 24, 32
        self.gain = gain
        self.tau = tau
        self.integ = integ
        self.offset = offset
        self.buffer_size = buffer_size
        self.temp_arrays = np.zeros((self.buffer_size, self.rows, self.cols), dtype=np.float32)
        self.time_series = time_series
        self.time_series_array = np.zeros((self.time_series), dtype=np.float32)
        self.backup = backup

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

    def update_time_series(self, time_series: float):
        # Enlève la plus vieille valeur et ajoute la nouvelle
        self.time_series_array = np.roll(self.time_series_array, 1)
        self.time_series_array[0] = time_series      

    def get_moy_temp(self, half = None) -> np.ndarray:
        if half is None:
            # Retourne la moyenne des températures dans le buffer
            return np.mean(self.temp_arrays, axis=0)
        elif half == 0:
            # Retourne la moyenne des températures dans la première moitié du buffer
            return np.mean(self.temp_arrays[:self.buffer_size//2, :, :], axis=0)
        elif half == 1:
            # Retourne la moyenne des températures dans la seconde moitié du buffer
            return np.mean(self.temp_arrays[self.buffer_size//2:, :, :], axis=0)
        else:
            raise ValueError("half must be 0 or 1")
    
    def filter_temp(self, temp_array: np.ndarray) -> np.ndarray:
        # Enlève les pixels aberrants et le bruit plus fin
        filtered_temp = median_filter(np.copy(temp_array), size=5)
        # Applique un filtre gaussien
        filtered_temp = gaussian_filter(filtered_temp, sigma=1)
        return filtered_temp

    def find_max_temp_index(self):
        temp = self.get_moy_temp()
        return np.unravel_index(np.argmax(temp, axis=None), temp.shape)

    def gaussian2D(self, xy, h_0, h_1, amp, k, sigma):
        x_0, x_1 = xy
        return (amp * np.exp(-((x_0 - h_0) ** 2 + (x_1 - h_1) ** 2) / (2 * (sigma ** 2)))+k).ravel()

    def fit_2Dgauss(self, grid: np.ndarray):
        a, b = self.find_max_temp_index()
        x, y = np.indices(grid.shape)
        params, cov = curve_fit(self.gaussian2D
                            ,(x.ravel(), y.ravel())
                            ,grid.ravel()
                            ,p0=[a, b, 50, -30, 1]
                            ,nan_policy='omit')
        return params, cov

    def get_gaussian_params(self, half = None) -> tuple:
        """ Donne les paramètres de la gaussienne 2D pour la moitié du buffer 
        choisie (half: 0 ou 1) ou l'ensemble du buffer (half: None)."""
        temp = self.get_moy_temp(half)
        temp[0:2, 0:2] = np.nan
        temp[-2:0, -2:0] = np.nan
        temp[0:2, -2:0] = np.nan
        temp[-2:0, 0:2] = np.nan
        temp = self.filter_temp(temp)
        params, cov = self.fit_2Dgauss(temp)
        c = params[:2]
        amp= params[2]
        k = params[3]
        sigma = params[4:]
        return (c, amp, k, sigma), cov
    
    def correction_power(self, x: float) -> float:
        return  - 1.70305*x + 0.892902*x**2 - 0.100539*x**3 + 0.00382482*x**4
    
    def get_power(self) -> float:
        """ Retourne la puissance en fonction des paramètres de la gaussienne 2D pour une plaque."""
        try:
            (params0, cov0), (params1, cov1) = self.get_gaussian_params(half=0), self.get_gaussian_params(half=1)
        except Exception as e:
            return 0.0, (0.0, 0.0)
        thresh = 0.1
        if np.mean(cov0) > thresh or np.mean(cov1) > thresh:
            return 0.0, (0.0, 0.0)
        
        ratio0, ratio1 = params0[1]/abs(params0[3][0]), params1[1]/abs(params1[3][0])
        largeur = abs(params0[3][0]+params1[3][0])/2

        dt = 0.5
        inte = np.sum(self.time_series_array)*self.integ/self.time_series
        self.update_time_series(ratio0)
        P = self.tau*(ratio0-ratio1)/dt + ratio0*self.gain+self.offset-inte
        if abs(largeur) > 1:
            self.backup = P, (params0, params1)
            return P, (params0, params1)
        return self.backup
        
    def get_center(self, params0: tuple, params1: tuple) -> tuple:
        """ Retourne le centre de la gaussienne 2D pour deux cadrillés différents."""
        c_0, c_1 = params0[0], params1[0]
        x = ((c_0[0] + c_1[0]) / 2)-11.5
        y = ((c_0[1] + c_1[1]) / 2)-15.5
        return (x*0.99787+y*0.065245)*0.9071, (x*-0.065245+y*0.99787)*0.9071
        
    def get_power_center(self) -> tuple:
        P, params = self.get_power()
        if isinstance(params[0], float) or isinstance(params[1], float):
            return 0.0, (0.0, 0.0)
        return P, self.get_center(params[0], params[1])

    def get_wavelength(self) -> float:
        """ Retourne la longueur d'onde en fonction des paramètres de la gaussienne 2D."""
        _, cov = self.get_gaussian_params()
        if np.mean(cov) > 0.01:
            return 0.0
        wv = 1976+gauss(0, 30)
        return wv
        
        
class PowerMeter(PowerMeter_nocam):
    def __init__(self):
        super().__init__()
        # Initialisation de la caméra
        self.camera_available = False

        try:
            self.dev = MLX90640()
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
