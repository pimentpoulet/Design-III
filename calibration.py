import numpy as np
from mlx90640_dump import rows, cols


temp = 25.0  # Température de référence pour la calibration
number_of_frames = 40  # Nombre de trames pour la moyenne
remove_frames = 20  # Nombre de trames à ignorer pour la moyenne
gain = np.ones((rows, cols))
off_set = np.zeros((rows, cols))

def get_diff(data, wanted_temp):
    diff = data - np.ones_like(data) * wanted_temp
    return diff

def update_moy_diff(moy_diff, data, filename=f'{temp}'+"mean_moy_diff.txt"):
    # Add new data array to the 3rd dimension
    moy_diff = np.concatenate((moy_diff, data[:, :, np.newaxis]), axis=2)
    print(moy_diff.shape)
    # Calculate the mean value element-wise along the 3rd dimension, ignoring the initialisation array

    if moy_diff.shape[2] > number_of_frames+remove_frames:
        mean_moy_diff = np.mean(moy_diff[:, :, remove_frames: remove_frames+number_of_frames], axis=2)*-1+temp
        
        # Save the mean_moy_diff to a file
        np.savetxt(filename, mean_moy_diff, fmt='%.6f')
        #exit()
        return moy_diff, mean_moy_diff
    return moy_diff, np.zeros((rows, cols))