import xlwings as xl
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt
from pathlib import Path

matplotlib.use("TkAgg")
source_data_low = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data low\SREF-350-1200.CSV")
source_data_high = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data high\SrEF-1200-2400.CSV")

app = xl.App(visible=False)
# fig, axes = plt.subplots(1, 3)


def butter_lowpass_filter(data, cutoff=0.05, order=3):
    b, a = butter(order, cutoff, btype='lowpass')
    return filtfilt(b, a, data)


""" Source Low Wavelengths Data """

wb_source_low = xl.Book(source_data_low)
sheet_source_low = wb_source_low.sheets[0]

raw_source_data_low = sheet_source_low["A40:A510"].options(np.array).value

split_arr = np.char.split(raw_source_data_low, ',')
source_wavelength_low = np.array([x[0] for x in split_arr], dtype=float)
source_power_dBm_low = np.array([x[1] for x in split_arr], dtype=float)
source_power_mW_low = np.power(10, (source_power_dBm_low/10))

# filter
source_power_mW_low = butter_lowpass_filter(source_power_mW_low)

wb_source_low.close()


""" Source High Wavelengths Data """

wb_source_high = xl.Book(source_data_high)
sheet_source_high = wb_source_high.sheets[0]

raw_source_data_high = sheet_source_high["A30:A3030"].options(np.array).value

split_arr = np.char.split(raw_source_data_high, ',')
source_wavelength_high = np.array([x[0] for x in split_arr], dtype=float)
source_power_dBm_high = np.array([x[1] for x in split_arr], dtype=float)
source_power_mW_high = np.power(10, (source_power_dBm_high/10))

# filter
source_power_mW_high = butter_lowpass_filter(source_power_mW_high)

wb_source_high.close()


""" Calculate Scale Factor """

source_scale_factor = source_power_mW_low[-1] / source_power_mW_high[0]
source_power_mW_high *= source_scale_factor


""" Combine Data """

source_wavelength_array = np.concatenate((source_wavelength_low, source_wavelength_high), axis=0)
source_power_array = np.concatenate((source_power_mW_low, source_power_mW_high), axis=0)


""" Plot All Data """

# axes[0].grid(True)
# axes[0].plot(source_wavelength_low, source_power_mW_low)
# axes[0].set_title("Puissance de la source aux basses longueurs d'onde")
# axes[0].set_xlabel("Longueur d'onde [nm]")
# axes[0].set_ylabel("Puissance [mW]")

# axes[1].grid(True)
# axes[1].plot(source_wavelength_high, source_power_mW_high)
# axes[1].set_title("Puissance de la source aux hautes longueurs d'onde")
# axes[1].set_xlabel("Longueur d'onde [nm]")
# axes[1].set_ylabel("Puissance [mW]")

# axes[2].grid(True)
# axes[2].plot(source_wavelength_array, source_power_array)
# axes[2].set_title("Puissance de la source sur toute la plage de longueurs d'onde")
# axes[2].set_xlabel("Longueur d'onde [nm]")
# axes[2].set_ylabel("Puissance [mW]")

# plt.tight_layout()
# plt.show()


material_data_low = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data low\W0000.CSV")
material_data_high = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data high\W0000.CSV")


""" Repeat Process For Material Data """

# fig_2, axes = plt.subplots(1, 3)


""" Low Wavelengths Data """

wb_material_low = xl.Book(material_data_low)
sheet_material_low = wb_material_low.sheets[0]

raw_material_data_low = sheet_material_low["A40:A510"].options(np.array).value

split_arr = np.char.split(raw_material_data_low, ',')
material_wavelength_low = np.array([x[0] for x in split_arr], dtype=float)
material_power_dBm_low = np.array([x[1] for x in split_arr], dtype=float)
material_power_mW_low = np.power(10, (material_power_dBm_low/10))

# filter
material_power_mW_low = butter_lowpass_filter(material_power_mW_low)

wb_material_low.close()


""" High Wavelengths Data """

wb_material_high = xl.Book(material_data_high)
sheet_material_high = wb_material_high.sheets[0]

raw_material_data_high = sheet_material_high["A30:A3030"].options(np.array).value

split_arr = np.char.split(raw_material_data_high, ',')
material_wavelength_high = np.array([x[0] for x in split_arr], dtype=float)
material_power_dBm_high = np.array([x[1] for x in split_arr], dtype=float)
material_power_mW_high = np.power(10, (material_power_dBm_high/10))

# filter
material_power_mW_high = butter_lowpass_filter(material_power_mW_high)

wb_material_high.close()


""" Calculate Scale Factor """

material_scale_factor = material_power_mW_low[-1] / material_power_mW_high[0]
material_power_mW_high *= material_scale_factor


""" Combine Data """

material_wavelength_array = np.concatenate((material_wavelength_low, material_wavelength_high), axis=0)
material_power_array = np.concatenate((material_power_mW_low, material_power_mW_high), axis=0)


""" Plot Material Data """

# n = 0000
# axes[0].grid(True)
# axes[0].plot(material_wavelength_low, material_power_mW_low)
# axes[0].set_title(f"Puissance réfléchie de la source aux basses longueurs d'onde pour le matériau #{n}", wrap=True)
# axes[0].set_xlabel("Longueur d'onde [nm]")
# axes[0].set_ylabel("Puissance [mW]")

# axes[1].grid(True)
# axes[1].plot(material_wavelength_high, material_power_mW_high)
# axes[1].set_title(f"Puissance réfléchie de la source aux hautes longueurs d'onde pour le matériau #{n}", wrap=True)
# axes[1].set_xlabel("Longueur d'onde [nm]")
# axes[1].set_ylabel("Puissance [mW]")

# axes[2].grid(True)
# axes[2].plot(material_wavelength_array, material_power_array)
# axes[2].set_title(f"Puissance réfléchie de la source sur toute la plage de longueurs d'onde pour le matériau #{n}", wrap=True)
# axes[2].set_xlabel("Longueur d'onde [nm]")
# axes[2].set_ylabel("Puissance [mW]")

# plt.tight_layout()
# plt.show()


""" Get Absorption Curve """

power_absorption_array = 100 * (1 - (material_power_array / source_power_array))


""" Display Source And Material Absorption Curves """

fig_3, axes = plt.subplots(1, 3)

n = 0000
axes[0].grid(True)
axes[0].plot(source_wavelength_array, source_power_array)
axes[0].set_title("Puissance de la source sur toute la plage de longueurs d'onde")
axes[0].set_xlabel("Longueur d'onde [nm]")
axes[0].set_ylabel("Puissance [mW]")

axes[1].grid(True)
axes[1].plot(material_wavelength_array, material_power_array)
axes[1].set_title(f"Puissance réfléchie de la source sur toute la plage de longueurs d'onde pour le matériau #{n}", wrap=True)
axes[1].set_xlabel("Longueur d'onde [nm]")
axes[1].set_ylabel("Puissance [mW]")

axes[2].grid(True)
axes[2].plot(source_wavelength_array, power_absorption_array)
axes[2].set_title(f"Absorption de la surface sur toute la plage de longueurs d'onde pour le matériau #{n}", wrap=True)
axes[2].set_xlabel("Longueur d'onde [nm]")
axes[2].set_ylabel("Pourcentage d'absorption")

plt.tight_layout()
plt.show()
