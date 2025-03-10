from calibration_class import PowerMeter_calibration
import numpy as np
import os
from time import sleep
from scipy.optimize import curve_fit


def main_cal():
    temp_moys = []
    temps = []
    try:
        for temp in range(20, 180, 5):
            print(f"Calibration pour {temp}°C")
            print("Appuyez sur une touche lorsque le corps noir est à température")
            input()
            # Initialisation de la caméra
            pm = PowerMeter_calibration(temp, 60, 6)
            # Calibration
            for frame in range(pm.number_of_frames+pm.remove_frames):
                if frame == pm.remove_frames:
                    print("Début de la calibration")
                if frame >= pm.remove_frames:
                    for i in range(3):
                        try: 
                            pm.update_temperature(pm.get_temp())
                            break
                        except ValueError as e:
                            print(f"Erreur de communication avec le capteur: {e}")
                            sleep(1)
                else:
                    for i in range(3):
                        try: 
                            pm.get_temp()
                            break
                        except ValueError as e:
                            print(f"Erreur de communication avec le capteur: {e}")
                            sleep(1)
            temp_moys.append(pm.get_moy_temp())
            temps.append(temp) 
            print("Calibration terminée")
    except ValueError as e:
        print(f"Erreur lors de la calibration: {e}")

    # Sauvegarde des données
    if not os.path.exists("calibration_data"):
        os.mkdir("calibration_data")
    os.chdir("calibration_data")
    np.save("temp_diffs.npy", np.array(temp_moys))
    np.save("temps.npy", np.array(temps))
    os.chdir("..")
    print("Données sauvegardées")
    

def main_fit_cal():
    # Chargement des données
    if not os.path.exists("calibration_data"):
        print("Pas de données de calibration")
        return
    os.chdir("calibration_data")
    temp_moys = np.load("temp_diffs.npy")
    temps = np.load("temps.npy")
    if not temp_moys or not temps:
        print("Pas de données de calibration")
        return
    height, width = temp_moys.shape[1], temp_moys.shape[2]

    # Store polynomial coefficients for each pixel
    coeffs_array = np.zeros((5, height, width))  # 5 coefficients (4th-degree + constant)

    # Fit a 4th-degree polynomial for each pixel
    for i in range(height):
        for j in range(width):
            coeffs_array[:, i, j] = np.polyfit(temp_moys[:, i, j], temps, deg=4)
    np.save(f"coeffs_range{temps[0]}-{temps[-1]}_jump{(temps[-1]-temps[0])/temps.size}.npy", coeffs_array)
    os.chdir("..")

if __name__ == "__main__":
    main_cal()
