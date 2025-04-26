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
data_path_echs_noir = Path(r"Absorption Graphs\Equipe4_ech.csv")
data_path = Path(r"Absorption Graphs\Plaques_Alexandre.csv")

plt.rcParams.update({
    "axes.labelsize": 24,    # Axis labels
    "xtick.labelsize": 24,   # X-axis tick labels
    "ytick.labelsize": 24,   # Y-axis tick labels
    "legend.fontsize": 24    # Legend
})

app = xl.App(visible=False)

wb_data = xl.Book(data_path)
data_sheet = wb_data.sheets[0]
raw_data = data_sheet["A3:A2253"].options(np.array).value
split_arr = np.char.split(raw_data, ',')

wb_data_echs_noir = xl.Book(data_path_echs_noir)
data_sheet_echs_noir = wb_data_echs_noir.sheets[0]
raw_data_echs_noir = data_sheet_echs_noir["A3:A2253"].options(np.array).value
split_arr_echs_noir = np.char.split(raw_data_echs_noir, ',')

wv_baseline_100 = np.array([x[0] for x in split_arr_echs_noir], dtype=float)    # ref abs
wv_baseline_0 = np.array([x[2] for x in split_arr_echs_noir], dtype=float)      # ref refl
wv_1 = np.array([x[10] for x in split_arr_echs_noir], dtype=float)              # 1
wv_2 = np.array([x[4] for x in split_arr_echs_noir], dtype=float)               # 2 --> front plate
wv_3 = np.array([x[6] for x in split_arr], dtype=float)                         # 3
wv_4 = np.array([x[4] for x in split_arr], dtype=float)                         # 4 --> back plate
wv_5 = np.array([x[2] for x in split_arr], dtype=float)                         # 5
wv_6 = np.array([x[0] for x in split_arr], dtype=float)                         # 6
wv_n = np.array([x[8] for x in split_arr], dtype=float)                         # BBQ

wv_rust_1 = np.array([x[4] for x in split_arr_echs_noir], dtype=float)    # rust 1
wv_rust_2 = np.array([x[6] for x in split_arr_echs_noir], dtype=float)    # rust 2
wv_rust_3 = np.array([x[8] for x in split_arr_echs_noir], dtype=float)    # rust 2

a_baseline_100 = 100.0 - np.array([x[1] for x in split_arr_echs_noir], dtype=float)    # ref abs
a_baseline_0 = 100.0 - np.array([x[3] for x in split_arr_echs_noir], dtype=float)      # ref refl
a_1 = 100.0 - np.array([x[11] for x in split_arr_echs_noir], dtype=float)              # 1
a_2 = 100.0 - np.array([x[5] for x in split_arr_echs_noir], dtype=float)               # 2 --> front plate
a_3 = 100.0 - np.array([x[7] for x in split_arr], dtype=float)                         # 3
a_4 = 100.0 - np.array([x[5] for x in split_arr], dtype=float)                         # 4 --> back plate
a_5 = 100.0 - np.array([x[3] for x in split_arr], dtype=float)                         # 5
a_6 = 100.0 - np.array([x[1] for x in split_arr], dtype=float)                         # 6
a_n = 100.0 - np.array([x[9] for x in split_arr], dtype=float)                         # BBQ

a_rust_1 = 100.0 - np.array([x[5] for x in split_arr_echs_noir], dtype=float)    # rust 1
a_rust_2 = 100.0 - np.array([x[7] for x in split_arr_echs_noir], dtype=float)    # rust 2
a_rust_3 = 100.0 - np.array([x[9] for x in split_arr_echs_noir], dtype=float)    # rust 3

# rust plots
plt.plot(wv_rust_1, a_rust_1, label="Échantillon non rouillé")
plt.plot(wv_rust_2, a_rust_2, label="Échantillon rouillé 1")
plt.plot(wv_rust_3, a_rust_3, label="Échantillon rouillé 2")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Absorptivité [%]")
plt.grid(True)
plt.legend()
plt.show()

# ratios

# 6/5 -> 6/3
r_6_5 = butter_lowpass_filter((a_6 / a_5))
r_6_4 = butter_lowpass_filter((a_6 / a_4))
r_6_3 = butter_lowpass_filter((a_6 / a_3))

# 5/4 -> 5/3
r_5_4 = butter_lowpass_filter((a_5 / a_4))
r_5_3 = butter_lowpass_filter((a_5 / a_3))

# 4/3
r_4_3 = butter_lowpass_filter((a_4 / a_3))

# 1/6 -> 1/3
r_1_6 = butter_lowpass_filter((a_1 / a_6))
r_1_5 = butter_lowpass_filter((a_1 / a_5))
r_1_4 = butter_lowpass_filter((a_1 / a_4))
r_1_3 = butter_lowpass_filter((a_1 / a_3))

# 2/6 -> 2/2
r_2_6 = butter_lowpass_filter((a_2 / a_6))
r_2_5 = butter_lowpass_filter((a_2 / a_5))
r_2_4 = butter_lowpass_filter((a_2 / a_4))
r_2_3 = butter_lowpass_filter((a_2 / a_3))

# differences

# 6-5 -> 6-1
r_65 = butter_lowpass_filter((a_6 - a_5))
r_64 = butter_lowpass_filter((a_6 - a_4))
r_63 = butter_lowpass_filter((a_6 - a_3))

# 5-4 -> 5-1
r_54 = butter_lowpass_filter((a_5 - a_4))
r_53 = butter_lowpass_filter((a_5 - a_3))

# 4-3
r_43 = butter_lowpass_filter((a_4 - a_3))

# 1-6 -> 1-3
r_16 = butter_lowpass_filter((a_1 - a_6))
r_15 = butter_lowpass_filter((a_1 - a_5))
r_14 = butter_lowpass_filter((a_1 - a_4))
r_13 = butter_lowpass_filter((a_1 - a_3))

# 2-6 -> 2-3
r_26 = butter_lowpass_filter((a_2 - a_6))
r_25 = butter_lowpass_filter((a_2 - a_5))
r_24 = butter_lowpass_filter((a_2 - a_4))
r_23 = butter_lowpass_filter((a_2 - a_3))


# abs plots

plt.plot(wv_1, a_1, label="plaque #1")
plt.plot(wv_2, a_2, label="Plaque #2")
plt.plot(wv_3, a_3, label="Plaque #3")
plt.plot(wv_4, a_4, label="Plaque #4")
plt.plot(wv_5, a_5, label="Plaque #5")
plt.plot(wv_6, a_6, label="Plaque #6")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Absorptivité [%]")
plt.grid(True)
plt.legend(loc="lower left")
plt.show()

# refl plots

plt.plot(wv_6, a_n, label="plaque peinturée")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Émissivité")
plt.grid(True)
plt.legend(loc="upper right")
plt.show()

# ratio plots

plt.plot(wv_6, r_6_5, label="6/5")
plt.plot(wv_6, r_6_4, label="6/4")
plt.plot(wv_6, r_6_3, label="6/3")
plt.plot(wv_6, r_5_4, label="5/4")
plt.plot(wv_6, r_5_3, label="5/3")
plt.plot(wv_6, r_4_3, label="4/3")

plt.plot(wv_6, r_1_6, marker="o", label="1/6")
plt.plot(wv_6, r_1_5, label="1/5")
plt.plot(wv_6, r_1_4, label="1/4")
plt.plot(wv_6, r_1_3, label="1/3")

plt.plot(wv_6, r_2_6, label="2/6")
plt.plot(wv_6, r_2_5, label="2/5")
plt.plot(wv_6, r_2_4, label="2/4")    # check
plt.plot(wv_6, r_2_3, label="2/3")

plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Ratio des absorptivités")
plt.grid(True)
plt.legend(loc="center right")
plt.show()

plt.plot(wv_6, r_65, label="6-5")
plt.plot(wv_6, r_64, label="6-4")
plt.plot(wv_6, r_63, label="6-3")
plt.plot(wv_6, r_54, label="5-4")
plt.plot(wv_6, r_53, label="5-3")
plt.plot(wv_6, r_43, label="4-3")

plt.plot(wv_6, r_16, marker="o", label="1-6")
plt.plot(wv_6, r_15, label="1-5")
plt.plot(wv_6, r_14, label="1-4")
plt.plot(wv_6, r_13, label="1-3")

plt.plot(wv_6, r_16, label="2-6")
plt.plot(wv_6, r_15, label="2-5")
plt.plot(wv_6, r_14, label="2-4")    # check
plt.plot(wv_6, r_13, label="2-3")

plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Différence des absorptivités [%]")
plt.grid(True)
plt.legend(loc="center right")
plt.show()

# useful curves

plt.plot(wv_6, r_1_6, label="1/6")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Ratio des absorptivités")
plt.grid(True)
plt.legend(loc="center right")
plt.show()

# np.save(r"C:\Clément MSI\UL\Session H2025_6\Design III\Design-III\Absorption Graphs\wv_6", wv_6)
# np.save(r"C:\Clément MSI\UL\Session H2025_6\Design III\Design-III\Absorption Graphs\Ratios_2_6", r_2_1_6)
