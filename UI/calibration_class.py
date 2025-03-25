from mlx90640_evb9064x import *
from mlx90640 import *
import numpy as np
from powermeter import PowerMeter
import cv2
import sys


class PowerMeter_calibration(PowerMeter):
    def __init__(self, reference_temp: float, calibration_time: int,
                 refresh_rate: int =6):
        # Catch error
        if refresh_rate < 1 or refresh_rate > 7:
            raise ValueError("Refresh rate invalide")
        # Initialisation de la caméra
        fps = 2**(refresh_rate-1)
        super().__init__(fps*calibration_time)
        self.dev.set_refresh_rate(refresh_rate)
        self.dev.dump_eeprom()
        self.dev.extract_parameters()
        # Initialisation des paramètres de calibration
        self.ref_temp = reference_temp
        self.refresh_rate = refresh_rate
        self.remove_frames = fps
        self.number_of_frames = calibration_time*fps

    def afficher_temp(self, temp_array: np.ndarray):
        # Correction des valeurs invalides
        image_array = np.nan_to_num(temp_array, nan=0.0, posinf=255.0, neginf=0.0)

        norm_image = cv2.normalize(image_array, None, 0, 255, cv2.NORM_MINMAX)
        color_image = cv2.applyColorMap(np.uint8(norm_image), cv2.COLORMAP_INFERNO)

        # Affichage en plein écran
        cv2.namedWindow("Thermal Camera", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Thermal Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cv2.imshow("Thermal Camera", color_image)

        # Quitter proprement avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Fermeture détectée. Arrêt du programme...")
            cv2.destroyAllWindows()
            sys.exit(0)
