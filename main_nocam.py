from powermeter import PowerMeter_nocam
import numpy as np
import os
import time
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, median_filter
from matplotlib.widgets import Slider


def time_delay(func):
    def wrapper(*args, **kwargs):
        begin = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return result, end-begin
    return wrapper

def main_nocam():
    powers = np.load("test_data/test_973nm_0W-20W_step2.5W_pows.npy")
    temps = np.load("test_data/test_973nm_0W-20W_step2.5W_temps_pow.npy")
    pm = PowerMeter_nocam(0.05, 10, buffer_size=64)
    for i in range(temps.shape[0]):
        pm.update_temperature( pm.get_temp(temps, i))
        if i % 64 == 0 and i != 0:
            try:
                power = pm.get_power()
                print(power)
            except Exception as e:
                # print(f"Erreur: {e}.")
                # print(pm.get_moy_temp())
                continue

def plateau(x, li, value):
    for i in range(len(x)//9):
        li.append(value)
    return li

def affiche_graphique(x, y, xlabel, ylabel):
    # power = plateau(x, [], 0)
    # power = plateau(x, power, 2.42)
    # power = plateau(x, power, 5.02)
    # power = plateau(x, power, 7.6)
    # power = plateau(x, power, 10.1)
    # power = plateau(x, power, 7.6)
    # power = plateau(x, power, 5.02)
    # power = plateau(x, power, 2.42)
    # power = plateau(x, power, 0)
    # power = plateau(x, [], 0)
    # power = plateau(x, power, 4.25)
    # power = plateau(x, power, 5.9)
    # power = plateau(x, power, 7.9)
    # power = plateau(x, power, 10.1)
    # power = plateau(x, power, 7.9)
    # power = plateau(x, power, 5.9)
    # power = plateau(x, power, 4.25)
    # power = plateau(x, power, 0)
    # diff = len(x)-len(power)
    # power = power+[0]*diff
    plt.plot(x, y, linewidth=4)
    # plt.plot(x, power, linewidth=2, color='red')
    # plt.title(titre, fontsize=16)
    plt.xlabel(xlabel, fontsize=28)
    plt.ylabel(ylabel, fontsize=28)
    plt.tick_params(axis='both', which='major', labelsize=24)  # Increase font size of axis ticks
    plt.grid()
    plt.show()
    return


def afficher_delta_T():
    temps = np.load("test_data/test_973nm_0W-20W_step2.5W_temps_pow.npy")
    max_temp = np.nanmax(temps, axis=(1, 2))
    min_temp = np.nanmin(temps, axis=(1, 2))
    affiche_graphique(np.arange(temps.shape[0]),
                       max_temp - min_temp,
                       "Temps (s)",
                       "Différence de température (°C)"
                     )

 
def afficher_delta_Gauss():
    temps = np.load("test_data/test_973nm_0W-20W_step2.5W_temps_pow.npy")
    pm = PowerMeter_nocam(0.05, 10, buffer_size=32)
    temp_diff = []
    for i in range(temps.shape[0]):
        pm.update_temperature(pm.get_temp(temps, i))
        if i % 32 == 0 and i != 0:
            try:
                params, cov = pm.get_gaussian_params()
                if 0 < np.mean(cov) < 0.5:
                    temp_diff.append(pm.filter_time_series(params[1]-params[2]+26))
                    # temp_diff.append(params[1]-params[2])
                    # print(params[1])
                else:
                    temp_diff.append(0.0)
            except Exception as e:
                print(f"Erreur: {e}")
                # print(pm.get_moy_temp())
                continue
    affiche_graphique(np.arange(len(temp_diff)),
                       temp_diff,
                       "Temps (s)",
                       "Différence de température (°C)"
                     )
    

def gaussian2D(xy, h_0, h_1, amp, k, sigma):
        x_0, x_1 = xy
        return (amp * np.exp(-((x_0 - h_0) ** 2 + (x_1 - h_1) ** 2) / (2 * (sigma ** 2)))+k).ravel()


def gaussian2D_radial(r_0, amp, k, sigma):
    return gaussian2D((r_0, 0), 0, 0, amp, k, sigma)


def afficher_delta_Gauss_sigma():
    temps = np.load("test_data/test_973nm_0W-20W_step2.5W_temps_pow.npy")
    pm = PowerMeter_nocam(0.05, 10, buffer_size=32)
    temp_diff = []
    for i in range(temps.shape[0]):
        pm.update_temperature(pm.get_temp(temps, i))
        if i % 32 == 0 and i != 0:
            try:
                params, cov = pm.get_gaussian_params(0)
                if 0 < params[1] < 100:
                    temp_diff.append(params[1]-gaussian2D_radial(16, params[1], params[2], params[3]))
                    print(params[4])
            except Exception as e:
                # print(f"Erreur: {e}.")
                # print(pm.get_moy_temp())
                continue
    affiche_graphique(np.arange(len(temp_diff)),
                       temp_diff,
                       "Temps (s)",
                       "Différence de température (°C)"
                     )
    

def afficher_profil_temp():
    temps = np.load("test_data/test_973nm_0W-20W_step2.5W_temps_pow.npy")
    pm = PowerMeter_nocam(0.05, 10, buffer_size=64)
    for i in range(temps.shape[0]):
        pm.update_temperature(pm.get_temp(temps, i))
        if i % 64 == 0 and i != 0:
            try:
                frame = pm.calibrate_temp(pm.get_moy_temp())
                arg_max = np.argmax(frame)
                affiche_graphique(np.arange(frame.shape[1]),
                                  frame[arg_max%24, :],
                                  "Temps (s)",
                                  "Différence de température (°C)"
                                 )
                affiche_graphique(np.arange(frame.shape[0]),
                                  frame[:, arg_max%32],
                                  "Temps (s)",
                                  "Différence de température (°C)"
                                 )
            except Exception as e:
                print(f"Erreur: {e}")
                # print(pm.get_moy_temp())
                continue

    
def integrer_power(pm: PowerMeter_nocam):
    temp1, temp2 = pm.get_moy_temp(0), pm.get_moy_temp(1)
    deltaE_1, deltaE_2 = np.sum(temp1-20), np.sum(temp2-20)
    deltaE = deltaE_2 - deltaE_1
    return deltaE
    

def afficher_integration():
    temps = np.load("test_data/test_973nm_0W-20W_step2.5W_temps_pow.npy")
    pm = PowerMeter_nocam(0.05, 10, buffer_size=64)
    diff = []
    for i in range(temps.shape[0]):
        pm.update_temperature(pm.get_temp(temps, i))
        if i % 64 == 0 and i != 0:
            try:
                deltaE = integrer_power(pm)
                if not np.isnan(deltaE):
                    diff.append(deltaE)
                    # print(deltaE)
            except Exception as e:
                print(f"Erreur: {e}")
                # print(pm.get_moy_temp())
                continue
    affiche_graphique(np.arange(len(diff)),
                       diff,
                       "Temps (s)",
                       "Différence de température (°C)"
                     )


def afficher_3D_temp():
    temps = np.load("test_data_ref/test_973_0W-20W_step2.5W_temps_pow.npy")
    pm = PowerMeter_nocam(0.05, 10, buffer_size=64)
    for i in range(temps.shape[0]):
        pm.update_temperature(pm.get_temp(temps, i))
        if i % 64 == 0 and i != 0:
            try:
                # frame = pm.get_moy_temp()
                frame = pm.calibrate_temp(pm.get_moy_temp())
                x = np.arange(frame.shape[1])
                y = np.arange(frame.shape[0])
                X, Y = np.meshgrid(x, y)
                Z = frame

                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                ax.plot_surface(X, Y, Z, cmap='viridis')
                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                ax.set_zlabel("Température (°C)")
                plt.show()
            except Exception as e:
                print(f"Erreur: {e}")
                continue


def afficher_puissance_serie_t():
    temps = np.load("test_data_ref/test_973_0W-20W_step2.5W_temps_pow.npy")
    pm = PowerMeter_nocam(0.05, 10, buffer_size=32)
    diff_series = []
    min_series = []
    for i in range(temps.shape[0]):
        pm.update_temperature(pm.get_temp(temps, i))
        if i % 32 == 0 and i != 0:
            try:
                temp = pm.get_moy_temp()
                temp_lisse = pm.filter_temp(temp)
                x_max, y_max = np.unravel_index(np.argmax(temp_lisse), temp_lisse.shape)
                temp_max = np.mean(temp_lisse[x_max-1:x_max+2, y_max-1:y_max+2])
                # x_min, y_min = np.unravel_index(np.argmin(temp_lisse), temp_lisse.shape)
                # temp_min = np.mean(temp_lisse[x_min-1:x_min+2, y_min-1:y_min+2])
                temp_min = np.amin(temp_lisse)
                # temp_max = np.amax(temp_lisse)
                deltaE = temp_max - temp_min
                print(temp_min)
                diff_series.append(temp_max)
                min_series.append(temp_min)
                    # print(deltaE)
            except Exception as e:
                print(f"Erreur: {e}")
                # print(pm.get_moy_temp())
                continue
    affiche_graphique(np.arange(len(diff_series)),
                       diff_series,
                       "Temps (s)",
                       "Différence de température (°C)"
                     )
    affiche_graphique(np.arange(len(min_series)),
                       min_series,
                       "Temps (s)",
                       "Différence de température (°C)"
                     )
    

def afficher_power():
    temps = np.load("test_data_ref/test_973_0W-20W_step2.5W_temps_pow.npy")
    # pm = PowerMeter_nocam(gain=1.15, tau=0.8, offset=3, integ=0.5, time_series=5, buffer_size=32)
    pm=PowerMeter_nocam()
    power_series = []
    for i in range(temps.shape[0]):
        pm.update_temperature(pm.get_temp(temps, i))
        if i % 32 == 0 and i != 0:
            try:
                power, centre = pm.get_power_center()
                print(centre)
                # power, center = pm.get_power_sigmas()
                # power, center = pm.get_power_center()
                # power, center = pm.get_power_zones()
                # if power is None:
                #     power_series.append(0.0)
                # elif 0.1 < power < 5:
                #     power_series.append(power*0.57)
                # elif 5 < power < 7.5:
                #     power_series.append(power*0.85)
                # elif 7.5 < power < 9.5:
                #     power_series.append(power*0.96)
                # else:
                #     power_series.append(power)
                power_series.append(pm.correction_power(power))
                # print(center)
            except Exception as e:
                print(f"Erreur: {e}")
            #     # # print(pm.get_moy_temp())
                continue
    print(len(power_series))
    affiche_graphique(np.arange(len(power_series)),
                       power_series,
                       "Temps (s)",
                       "Puissance (W)"
                     )
    

def afficher_wv():
    # temps = np.load("test_data_ref/test_450_0W-5W_step5W_temps_pow.npy")

    temps = np.load("test_data_ref/test_973_0W-20W_step2.5W_temps_pow.npy")
    pm = PowerMeter_nocam()
    wv_series = []
    for i in range(temps.shape[0]):
        pm.update_temperature(pm.get_temp(temps, i))
        if i % 32 == 0 and i != 0:
            try:
                wv = pm.get_wavelength()
                # power, center = pm.get_power_sigmas()
                # if abs(wv) <2:
                wv_series.append(wv)
                # print(center)
            except Exception as e:
                print(f"Erreur: {e}")
                # print(pm.get_moy_temp())
                wv_series.append(0.0)
                continue
    affiche_graphique(np.arange(len(wv_series)),
                       wv_series,
                       "Temps (s)",
                       "Puissance (W)"
                     )


if __name__ == "__main__":
    # main_nocam()

    # afficher_delta_T()
    # afficher_delta_Gauss()
    # afficher_delta_Gauss_sigma()
    # afficher_profil_temp()
    # afficher_integration()
    # afficher_3D_temp()
    # afficher_puissance_serie_t()
    # afficher_power()
    afficher_wv()
    # affiche_graphique(np.load("wv_6.npy"),
    #                   np.load("Ratios_2_6.npy"),
    #                   "Longueur d'onde (nm)",
    #                     "Ratio")
