from calibration_class import PowerMeter_calibration
from powermeter import PowerMeter
import numpy as np
import os
from time import sleep
from affichage import show_image_opencv
import cv2
import sys


def main_cal():
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
    temp_moys = np.load("temps_moy.npy")
    temps = np.load("gauche_temps.npy")
    # if not np.all(~np.isnan(temp_moys)) or not np.any(temps):
    #     print("Pas de données de calibration")
    #     return
    height, width = temp_moys.shape[1], temp_moys.shape[2]

    # Store polynomial coefficients for each pixel
    coeffs_array = np.zeros((5, height, width))  # 5 coefficients (4th-degree + constant)
    # Fit a 4th-degree polynomial for each pixel
    for i in range(height):
        for j in range(width):
            idx = np.isfinite(temp_moys[:, i, j]) & np.isfinite(temps)
            coeffs_array[:, i, j] = np.polyfit(temp_moys[idx, i, j], temps[idx], deg=4)
    os.chdir("..")
    np.save(f"coeffs_range{temps[0]}-{temps[-1]}_jump{(temps[-1]-temps[0])/(temps.size-1)}.npy", coeffs_array)
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

def reorder_calibration_data() -> np.ndarray:
    # Reorder the calibration data to match the expected shape
    d_temp_diffs_20_55 = np.load("calibration_data/droite_temp_diffs20-55.npy")
    d_temp_diffs_60_150 = np.load("calibration_data/droite_temp_diffs.npy")
    g_temp_diffs = np.load("calibration_data/gauche_temp_diffs.npy")
    # Combine the data
    print(d_temp_diffs_20_55.shape)
    print(d_temp_diffs_60_150.shape)
    print(g_temp_diffs.shape)
    d_temp_diffs = np.zeros_like(g_temp_diffs)
    d_temp_diffs[:8, :, :] = d_temp_diffs_20_55[:8, :, :]
    d_temp_diffs[8:, :, :] = d_temp_diffs_60_150[:19, :, :]
    temps_moys = np.zeros_like(g_temp_diffs)
    temps_moys[:, :, :16] = g_temp_diffs[:, :, :16]
    temps_moys[:, :, 16:] = d_temp_diffs[:, :, 16:]
    np.save("temps_moy.npy", temps_moys)


def main_test():
    p_min = 2.5
    p_max = 10
    step = 2.5
    nb_step = int((p_max-p_min)/step)+1
    time_per_step = 60
    name = f'test_{p_min}W-{p_max}W_step{step}W'
    if not os.path.exists("test_data"):
        os.mkdir("test_data")
    os.chdir("test_data")
    try:
        # Initialisation de la caméra
        pm = PowerMeter(5, 10)
        for i in range(64):
            try:
                captured_temp = pm.get_temp()
                show_image_opencv(captured_temp)
            except Exception as e:
                print(f"Unexpected error at frame {frame}: {e}")
                sleep(1)
                continue
        frames_per_step = pm.buffer_size*time_per_step
        temps_pow = np.zeros((frames_per_step*(nb_step), pm.rows, pm.cols))
        pows = np.zeros((nb_step))
        print("Prêt à enregistrer")
        for i in range(nb_step):
            pow = (i+1)*step
            print(f"Calibration pour {pow} W")
            # input("Appuyez sur une touche lorsque vous êtes prêt à allumer le laser.\n")

            # Calibration
            for frame in range(frames_per_step):
                # print(f"Frame {frame}")
                # if frame == 0:
                #     print("Début de l'enregistrement.")
                try:
                    captured_temp = pm.get_temp()
                    show_image_opencv(captured_temp)
                    temps_pow[i*frames_per_step+frame,:,:] = captured_temp
                    
                except Exception as e:
                    print(f"Unexpected error at frame {frame}: {e}")
                    sleep(1)
                    continue

            # Sauvegarde des données
            np.save(f"{name}_temps_pow.npy", temps_pow)
            pows[i] = pow
            np.save(f"{name}_pows.npy", pows)

    except Exception as e:
        print(f"Unexpected error during test: {e}")

    os.chdir("..")
    print("Test terminée")

if __name__ == "__main__":
    main_test()
    #pows = np.load('test_data/test_2.5W-10W_step2.5W_temps_pow.npy')
    #print(pows)
    
    # reorder_calibration_data()

    #main_cal()
    # ca = main_fit_cal()

    #pm = PowerMeter()
    #while True:
        #try:
          #  for i in range(32):
           #     sleep(1/30)
            #    pm.update_temperature(pm.get_temp())
                
            #show_image_opencv(pm.get_moy_temp())
        #except:
         #   sleep(1)
       

    
    #ca = np.load("calibration_data/coeffs_range20-20_jump0.0.npy")
    #test_cal(ca)