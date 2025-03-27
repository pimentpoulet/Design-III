from mlx90640_evb9064x import *
from mlx90640 import *
from calibration import *
from affichage import *
import numpy as np
import time


# Paramètres de l'image
rows, cols = 24, 32    # Résolution du capteur MLX90640
MAX_RETRIES = 5        # Nombre max de tentatives en cas de timeout

def calculate_centroid(temperature_array):
    """
    Calcule le centroïde de la distribution thermique
    """
    total_temp = np.sum(temperature_array)
    if total_temp == 0:
        return (0, 0)
    
    x_coords, y_coords = np.meshgrid(np.arange(cols), np.arange(rows))
    x_centroid = np.sum(x_coords * temperature_array) / total_temp
    y_centroid = np.sum(y_coords * temperature_array) / total_temp
    
    return (x_centroid, y_centroid)


def main():
    print("Initialisation du capteur MLX90640...")
    dev = MLX90640()

    # Initialisation de l'I2C avec détection automatique du port
    r = dev.i2c_init(evb9064x_get_i2c_comport_url('auto'))
    print("Init I2C:", r)

    # Configuration du taux de rafraîchissement
    dev.set_refresh_rate(6)
    refresh_rate = dev.get_refresh_rate()
    print(f"Taux de rafraîchissement: {refresh_rate}Hz")

    dev.dump_eeprom()
    dev.extract_parameters()

    print("Démarrage de l'affichage thermique...")

    moy_diff = np.zeros((rows, cols, 1))  # Initialisation

    pixel_row, pixel_col = 12, 16    # Coordonnées du pixel à surveiller
    pixel_temps = []                 # Liste pour stocker la température du pixel

    frame_buffer = []
    buffer_size = 10    # Nombre de frames à moyenner

    while True:         # Boucle infinie, gérée par OpenCV
        try:
            dev.get_frame_data()
            ta = dev.get_ta() - 8.0    # Compensation de la température ambiante
            emissivity = 1.0
            to = dev.calculate_to(emissivity, ta)    # Conversion en températures
            to_array = np.array(to).reshape((rows, cols))
            to_array *= gain
            to_array += off_set

            moy_diff, mean_moy_diff = update_moy_diff(moy_diff, to_array, filename="mean_moy_diff.txt")

            frame_buffer.append(to_array + mean_moy_diff)
            if len(frame_buffer) > buffer_size:
                frame_buffer.pop(0)

            averaged_frame = np.mean(frame_buffer, axis=0)
            show_image_opencv(averaged_frame)    # Affichage OpenCV

            # Stocke la température du pixel surveillé
            pixel_temps.append(to_array[pixel_row, pixel_col])

            # Calcul et affichage du centroïde
            centroid = calculate_centroid(averaged_frame)
            print(f"Centroid de la distribution thermique: {centroid}")

        except Exception as e:
            print(f"Erreur : {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
