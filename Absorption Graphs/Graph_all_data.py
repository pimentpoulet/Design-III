import os
import xlwings as xl
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt
from pathlib import Path

matplotlib.use("TkAgg")
saving_path = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Absorption Curves_stax"
app = xl.App(visible=False)


def butter_lowpass_filter(data, cutoff=0.05, order=3):
    b, a = butter(order, cutoff, btype='lowpass')
    return filtfilt(b, a, data)


""" Source """

source_data_low = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data low\SREF-350-1200.CSV")
source_data_high = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data high\SrEF-1200-2400.CSV")

wb_source_low = xl.Book(source_data_low)
sheet_source_low = wb_source_low.sheets[0]

raw_source_data_low = sheet_source_low["A40:A510"].options(np.array).value

split_arr = np.char.split(raw_source_data_low, ',')
source_wavelength_low = np.array([x[0] for x in split_arr], dtype=float)
source_power_dBm_low = np.array([x[1] for x in split_arr], dtype=float)
source_power_mW_low = np.power(10, (source_power_dBm_low/10))

# filter low data
wsource_power_mW_low = butter_lowpass_filter(source_power_mW_low)

wb_source_low.close()

# high data
wb_source_high = xl.Book(source_data_high)
sheet_source_high = wb_source_high.sheets[0]
raw_source_data_high = sheet_source_high["A30:A3030"].options(np.array).value

split_arr = np.char.split(raw_source_data_high, ',')
source_wavelength_high = np.array([x[0] for x in split_arr], dtype=float)
source_power_dBm_high = np.array([x[1] for x in split_arr], dtype=float)
source_power_mW_high = np.power(10, (source_power_dBm_high/10))

# filter high data
source_power_mW_high = butter_lowpass_filter(source_power_mW_high)
wb_source_high.close()

# source scale factor
source_scale_factor = source_power_mW_low[-1] / source_power_mW_high[0]
source_power_mW_high *= source_scale_factor

# complete source data
source_wavelength_array = np.concatenate((source_wavelength_low, source_wavelength_high), axis=0)
source_power_array = np.concatenate((source_power_mW_low, source_power_mW_high), axis=0)


""" Materials """

data_low = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data low")
data_high = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data high")

data = []
for file in data_low.iterdir():
    data.append([file])

for i, file in enumerate(data_high.iterdir()):
    data[i].append(file)

data = data[1:]

# iterate to get every material's absorption curve
for material in data:

    # low data
    wb_material_low = xl.Book(material[0])
    sheet_material_low = wb_material_low.sheets[0]
    raw_material_data_low = sheet_material_low["A40:A510"].options(np.array).value

    split_arr = np.char.split(raw_material_data_low, ',')
    material_wavelength_low = np.array([x[0] for x in split_arr], dtype=float)
    material_power_dBm_low = np.array([x[1] for x in split_arr], dtype=float)
    material_power_mW_low = np.power(10, (material_power_dBm_low / 10))

    # filter low data
    material_power_mW_low = butter_lowpass_filter(material_power_mW_low)
    wb_material_low.close()

    # high data
    wb_material_high = xl.Book(material[1])
    sheet_material_high = wb_material_high.sheets[0]

    raw_material_data_high = sheet_material_high["A30:A3030"].options(np.array).value

    split_arr = np.char.split(raw_material_data_high, ',')
    material_wavelength_high = np.array([x[0] for x in split_arr], dtype=float)
    material_power_dBm_high = np.array([x[1] for x in split_arr], dtype=float)
    material_power_mW_high = np.power(10, (material_power_dBm_high / 10))

    # filter high data
    material_power_mW_high = butter_lowpass_filter(material_power_mW_high)
    wb_material_high.close()

    # material scale factor
    material_scale_factor = material_power_mW_low[-1] / material_power_mW_high[0]
    material_power_mW_high *= material_scale_factor

    # complete material data
    material_wavelength_array = np.concatenate((material_wavelength_low, material_wavelength_high), axis=0)
    material_power_array = np.concatenate((material_power_mW_low, material_power_mW_high), axis=0)

    # get absorption curve
    power_absorption_array = 100 * (1 - (material_power_array / source_power_array))

    plt.clf()
    plt.plot(source_wavelength_array, power_absorption_array)
    plt.title(f"Absorption de la texturation pour le matériau #{material[0].name[1:-4]} sur toute la plage de longueurs d'onde", wrap=True)
    plt.xlabel("Longueur d'onde [nm]")
    plt.ylabel("Pourcentage d'absorption")
    plt.grid(True)
    plt.ylim(0,100)

    os.makedirs(saving_path, exist_ok=True)
    save_path = os.path.join(saving_path, f"{material[0].name[1:-4]}")
    plt.savefig(save_path)
