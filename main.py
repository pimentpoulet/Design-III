from calibration_class import PowerMeter_calibration
from powermeter import PowerMeter
import numpy as np
import os
from time import sleep
from affichage import show_image_opencv
import cv2
import sys


def main_cal():
    # print("toto")
    t_min = 20
    t_max = 150
    step = 5
    name = 'gauche'
    if not os.path.exists("calibration_data"):
        os.mkdir("calibration_data")
    os.chdir("calibration_data")
    try:
        # Initialisation de la caméra
        pm = PowerMeter_calibration(20, 30, 6)
        temp_moys = np.zeros(((t_max-t_min)//step+1, pm.rows, pm.cols))
        temps = np.zeros(((t_max-t_min)//step+1))
        for i, temp in enumerate(range(t_min, t_max+step, step)):
            print(f"Calibration pour {temp}°C")
            input("Appuyez sur une touche lorsque le corps noir est à température\n")
            
            pm.ref_temp = temp
            # Calibration
            for frame in range(pm.number_of_frames + pm.remove_frames):
                # print(f"Frame {frame}")
                if frame == pm.remove_frames:
                    print("Début de la calibration")
                if frame >= pm.remove_frames:
                    try:
                        captured_temp = pm.get_temp()
                        pm.update_temperature(captured_temp)
                        show_image_opencv(captured_temp)
                        # break
                    except ValueError as e:
                        print(f"Erreur de communication avec le capteur à la frame {frame}: {e}")
                        sleep(1)
                        continue
                    except Exception as e:
                        print(f"Unexpected error at frame {frame}: {e}")
                        sleep(1)
                        continue
                else:
                    try:
                        show_image_opencv(pm.get_temp())
                        # break
                    except ValueError as e:
                        print(f"Erreur de communication avec le capteur à la frame {frame}: {e}")
                        sleep(1)
                        continue
                    except Exception as e:
                        print(f"Unexpected error at frame {frame}: {e}")
                        sleep(1)
                        continue
            print(pm.get_moy_temp())
            # Sauvegarde des données
            if i != 0 and os.path.exists(f"{name}_temp_diffs.npy"):
                temp_moys = np.load(f"{name}_temp_diffs.npy")
            if i != 0 and os.path.exists(f"{name}_temps.npy"):
                temps = np.load(f"{name}_temps.npy")
            temp_moys[i,:,:] = pm.get_moy_temp()
            temps[i] = temp
            np.save(f"{name}_temp_diffs.npy", temp_moys)
            np.save(f"{name}_temps.npy", temps)
            print(temp_moys)
            print(temps)
            print("Données sauvegardées")
            
    except ValueError as e:
        print(f"Erreur lors de la calibration: {e}")
    except Exception as e:
        print(f"Unexpected error during calibration: {e}")

    os.chdir("..")
    print("Calibration terminée")


def main_fit_cal():
    # print("tata")
    # Chargement des données
    if not os.path.exists("calibration_data"):
        print("Pas de données de calibration")
        return
    os.chdir("calibration_data")
    temp_moys = np.load("temp_diffs.npy")
    temps = np.load("temps.npy")
    if not np.all(temp_moys) or not temps:
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
    return coeffs_array


def test_cal(calibration_data: np.ndarray):
    # print("titi")
    pm = PowerMeter()
    pm.coeffs_array = calibration_data
    while True:
        for i in range(32):
            pm.update_temperature(pm.get_temp())
            sleep(1/30)
        corrected_temp = pm.calibrate_temp(pm.get_moy_temp())
        show_image_opencv(corrected_temp)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Fermeture détectée. Arrêt du programme...")
            cv2.destroyAllWindows()
            sys.exit(0)


if __name__ == "__main__":
    main_cal()
    #ca = main_fit_cal()
    #while True:
        #try:
         #   pm = PowerMeter()
          #  for i in range(32):
           #     sleep(1/30)
            #    pm.update_temperature(pm.get_temp())
                
            #show_image_opencv(pm.get_moy_temp())
        #except:
         #   sleep(1)
       

    
    #ca = np.load("calibration_data/coeffs_range20-20_jump0.0.npy")
    #test_cal(ca)
    