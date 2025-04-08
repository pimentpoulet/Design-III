import xlwings as xl
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt
from pathlib import Path


def butter_lowpass_filter(data, cutoff=0.05, order=3):
    b, a = butter(order, cutoff, btype='lowpass')
    return filtfilt(b, a, data)


matplotlib.use("TkAgg")
data_path_echs_noir = Path(r"C:\Clément MSI\UL\Session H2025_6\Design III\Design-III\Absorption Graphs\Equipe4_ech.csv")
data_path = Path(r"C:\Clément MSI\UL\Session H2025_6\Design III\Design-III\Absorption Graphs\Plaques_Alexandre.csv")

plt.rcParams.update({
    "axes.labelsize": 18,    # Axis labels
    "xtick.labelsize": 16,   # X-axis tick labels
    "ytick.labelsize": 16,   # Y-axis tick labels
    "legend.fontsize": 13    # Legend
})

app = xl.App(visible=False)

wb_data = xl.Book(data_path)
data_sheet = wb_data.sheets[0]
raw_data = data_sheet["A3:A2253"].options(np.array).value
split_arr = np.char.split(raw_data, ',')

wv_6 = np.array([x[0] for x in split_arr], dtype=float)
wv_5 = np.array([x[2] for x in split_arr], dtype=float)
wv_4 = np.array([x[4] for x in split_arr], dtype=float)
wv_3 = np.array([x[6] for x in split_arr], dtype=float)
wv_n = np.array([x[8] for x in split_arr], dtype=float)

a_6 = 100.0 - np.array([x[1] for x in split_arr], dtype=float)
a_5 = 100.0 - np.array([x[3] for x in split_arr], dtype=float)
a_4 = 100.0 - np.array([x[5] for x in split_arr], dtype=float)
a_3 = 100.0 - np.array([x[7] for x in split_arr], dtype=float)
a_n = 100.0 - np.array([x[9] for x in split_arr], dtype=float)

wb_data_echs_noir = xl.Book(data_path_echs_noir)
data_sheet_echs_noir = wb_data_echs_noir.sheets[0]
raw_data_echs_noir = data_sheet_echs_noir["A3:A2253"].options(np.array).value
split_arr_echs_noir = np.char.split(raw_data_echs_noir, ',')

wv_baseline_100 = np.array([x[0] for x in split_arr_echs_noir], dtype=float)
wv_baseline_0 = np.array([x[2] for x in split_arr_echs_noir], dtype=float)
wv_ech_noir_1_1 = np.array([x[4] for x in split_arr_echs_noir], dtype=float)
wv_ech_noir_1_2 = np.array([x[6] for x in split_arr_echs_noir], dtype=float)
wv_ech_noir_1_3 = np.array([x[8] for x in split_arr_echs_noir], dtype=float)
wv_ech_noir_2_1 = np.array([x[10] for x in split_arr_echs_noir], dtype=float)

a_baseline_100 = 100.0 - np.array([x[1] for x in split_arr_echs_noir], dtype=float)
a_baseline_0 = 100.0 - np.array([x[3] for x in split_arr_echs_noir], dtype=float)
a_ech_noir_1_1 = 100.0 - np.array([x[5] for x in split_arr_echs_noir], dtype=float)
a_ech_noir_1_2 = 100.0 - np.array([x[7] for x in split_arr_echs_noir], dtype=float)
a_ech_noir_1_3 = 100.0 - np.array([x[9] for x in split_arr_echs_noir], dtype=float)
a_ech_noir_2_1 = 100.0 - np.array([x[11] for x in split_arr_echs_noir], dtype=float)

plt.plot(wv_3, a_3, label="Plaque #3")
plt.plot(wv_4, a_4, label="Plaque #4")
plt.plot(wv_5, a_5, label="Plaque #5")
plt.plot(wv_6, a_6, label="Plaque #6")
plt.plot(wv_ech_noir_1_1, a_ech_noir_1_1, label="ech_noir_1_1")
# plt.plot(wv_ech_noir_1_2, a_ech_noir_1_2, label="ech_noir_1_2")
# plt.plot(wv_ech_noir_1_3, a_ech_noir_1_3, label="ech_noir_1_3")
plt.plot(wv_ech_noir_2_1, a_ech_noir_2_1, label="ech_noir_2_1")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Absorptivité [%]")
plt.grid(True)
plt.legend(loc="lower left")
# plt.show()

"""
plt.plot(wv_6, a_n, label="plaque peinturée")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Émissivité")
plt.grid(True)
plt.legend(loc="upper right")
plt.show()
"""

# 6/5 -> 6/n
r_6_5 = butter_lowpass_filter((a_6 / a_5))
r_6_4 = butter_lowpass_filter((a_6 / a_4))
r_6_3 = butter_lowpass_filter((a_6 / a_3))
r_6_n = butter_lowpass_filter((a_6 / a_n))

# 5/4 -> 5/n
r_5_4 = butter_lowpass_filter((a_5 / a_4))
r_5_3 = butter_lowpass_filter((a_5 / a_3))
r_5_n = butter_lowpass_filter((a_5 / a_n))

# 4/3 -> 4/n
r_4_3 = butter_lowpass_filter((a_4 / a_3))
r_4_n = butter_lowpass_filter((a_4 / a_n))

# 3/n
r_3_n = butter_lowpass_filter((a_3 / a_n))

r_1_1_6 = butter_lowpass_filter((a_ech_noir_1_1 / a_6))
r_1_1_4 = butter_lowpass_filter((a_ech_noir_1_1 / a_4))
r_2_1_6 = butter_lowpass_filter((a_ech_noir_2_1 / a_6))
r_2_1_4 = butter_lowpass_filter((a_ech_noir_2_1 / a_4))

np.save(r"C:\Clément MSI\UL\Session H2025_6\Design III\Design-III\Absorption Graphs\wv_6", wv_6)
np.save(r"C:\Clément MSI\UL\Session H2025_6\Design III\Design-III\Absorption Graphs\Ratios_2_6", r_2_1_6)

"""
plt.plot(wv_6, r_6_5, label="r_6_5")
plt.plot(wv_6, r_6_4, label="r_6_4")

plt.plot(wv_6, r_6_3, label="r_6_3")
plt.plot(wv_6, r_5_4, label="r_5_4")
plt.plot(wv_6, r_5_3, label="r_5_3")
plt.plot(wv_6, r_4_3, label="r_4_3")
"""

plt.plot(wv_6, r_1_1_6, label="r_1_6")
plt.plot(wv_6, r_1_1_4, label="r_1_4")
plt.plot(wv_6, r_2_1_6, label="r_2_6")
plt.plot(wv_6, r_2_1_4, label="r_2_4")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Ratio des absorptivités")
plt.grid(True)
plt.legend(loc="center right")
# plt.show()

# 6-5 -> 6-3
r_65 = butter_lowpass_filter((a_6 - a_5))
r_64 = butter_lowpass_filter((a_6 - a_4))
r_63 = butter_lowpass_filter((a_6 - a_3))

# 5-4 -> 5-3
r_54 = butter_lowpass_filter((a_5 - a_4))
r_53 = butter_lowpass_filter((a_5 - a_3))

# 4-3
r_43 = butter_lowpass_filter((a_4 - a_3))

plt.plot(wv_6, r_65, label="6-5")
plt.plot(wv_6, r_64, label="6-4")
plt.plot(wv_6, r_63, label="6-3")
plt.plot(wv_6, r_54, label="5-4")
plt.plot(wv_6, r_53, label="5-3")
plt.plot(wv_6, r_43, label="4-3")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Différence des absorptivités [%]")
plt.grid(True)
plt.legend(loc="center right")
# plt.show()
