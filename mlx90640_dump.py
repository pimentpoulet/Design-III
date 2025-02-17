from mlx90640_evb9064x import *
from mlx90640 import *
from calibration import *
import numpy as np
import matplotlib.pyplot as plt
import time
import sys

# Paramètres de l'image
rows, cols = 24, 32  # Résolution du capteur MLX90640

def on_close(event):
    """Arrête le programme lorsqu'on ferme la fenêtre."""
    print("Fermeture détectée. Arrêt du programme...")
    plt.close()  # Ferme la figure
    #sys.exit(0)  # Quitte immédiatement le script

# Initialisation de la figure
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)  # Détecte la fermeture
image = ax.imshow(np.zeros((rows, cols)), cmap='inferno', vmin=20, vmax=30)
plt.colorbar(image, ax=ax)

def update_image(data_array):
    """Met à jour l'image thermique"""
    image.set_array(data_array)
    plt.draw()
    plt.pause(0.001)  # Pause courte pour rafraîchir l'affichage

def calculate_centroid(temperature_array):
    """Calculate the centroid of the temperature array."""
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

    moy_diff = np.zeros((rows, cols, 1))  # Initialize with a 3rd dimension

    pixel_row, pixel_col = 12, 16  # Coordinates of the pixel to monitor
    pixel_temps = []  # List to store temperature values of the pixel

    frame_buffer = []
    buffer_size = 10  # Number of frames to average

    # Boucle principale pour la capture et l'affichage en direct
    while plt.fignum_exists(fig.number):  # Continue tant que la fenêtre est ouverte
        dev.get_frame_data()
        ta = dev.get_ta() - 8.0  # Compensation de la température ambiante
        emissivity = 1.0
        to = dev.calculate_to(emissivity, ta)  # Conversion en températures
        to_array = np.array(to).reshape((rows, cols))
        to_array *= gain
        to_array += off_set

        moy_diff, mean_moy_diff = update_moy_diff(moy_diff, to_array, filename="mean_moy_diff.txt")

        frame_buffer.append(to_array + mean_moy_diff)
        if len(frame_buffer) > buffer_size:
            frame_buffer.pop(0)

        averaged_frame = np.mean(frame_buffer, axis=0)
        update_image(averaged_frame)  # Mise à jour de l'affichage

        # Store the temperature value of the specified pixel
        pixel_temps.append(to_array[pixel_row, pixel_col])

        # Calculate and print the centroid
        centroid = calculate_centroid(averaged_frame)
        print(f"Centroid of the temperature distribution: {centroid}")

    # Plot the temperature values of the specified pixel
    plt.figure()
    plt.plot(pixel_temps[20:])
    plt.xlabel('Frame')
    plt.ylabel('Temperature (°C)')
    plt.title(f'Temperature of Pixel ({pixel_row}, {pixel_col}) Over Time')
    plt.show()

    print("Programme terminé.")

if __name__ == "__main__":
    main()
