import xlwings as xl
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path


matplotlib.use("TkAgg")
data_path_450 = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Spectres laser\Deuxième test\OSA\450")
data_path_976 = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Spectres laser\Deuxième test\OSA\976")
data_path_1976 = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Spectres laser\Deuxième test\OSA\1976")
app = xl.App(visible=False)

plt.rcParams.update({
    "axes.labelsize": 14,    # Axis labels
    "xtick.labelsize": 12,   # X-axis tick labels
    "ytick.labelsize": 12,   # Y-axis tick labels
    "legend.fontsize": 12    # Legend
})


# 450nm

for file in data_path_450.iterdir():

    print(file.name[:-4])

    source_data = xl.Book(file)
    source_data_sheet = source_data.sheets[0]
    source = source_data_sheet["A40:A5040"].options(np.array, expand="table").value

    split_arr = np.char.split(source, ',')
    source_wv = np.array([x[0] for x in split_arr], dtype=float)
    source_pw_dBm = np.array([x[1] for x in split_arr], dtype=float)
    source_pw_mW = np.power(10, (source_pw_dBm / 10))

    source_pw_mW_norm = source_pw_mW / np.max(source_pw_mW)

    plt.plot(source_wv[1300:2250], source_pw_mW_norm[1300:2250], label=f"spectre optique pour {file.name[:-4]}nm")

plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Puissance en mW normalisée")
plt.legend(loc="upper left")
plt.grid(True)
plt.show()


# 976nm

for file in data_path_976.iterdir():

    print(file.name[:-4])

    source_data = xl.Book(file)
    source_data_sheet = source_data.sheets[0]
    source = source_data_sheet["A40:A5040"].options(np.array, expand="table").value

    split_arr = np.char.split(source, ',')
    source_wv = np.array([x[0] for x in split_arr], dtype=float)
    source_pw_dBm = np.array([x[1] for x in split_arr], dtype=float)
    source_pw_mW = np.power(10, (source_pw_dBm / 10))

    source_pw_mW_norm = source_pw_mW / np.max(source_pw_mW)

    plt.plot(source_wv[1300:2100], source_pw_mW_norm[1300:2100], label=f"spectre optique pour {file.name[:-4]}nm")

plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Puissance en mW normalisée")
plt.legend(loc="upper left")
plt.grid(True)
plt.show()


# 1976nm

for file in data_path_1976.iterdir():

    print(file.name[:-4])

    source_data = xl.Book(file)
    source_data_sheet = source_data.sheets[0]
    source = source_data_sheet["A30:A530"].options(np.array, expand="table").value

    split_arr = np.char.split(source, ',')
    source_wv = np.array([x[0] for x in split_arr], dtype=float)
    source_pw_dBm = np.array([x[1] for x in split_arr], dtype=float)
    source_pw_mW = np.power(10, (source_pw_dBm / 10))

    source_pw_mW_norm = source_pw_mW / np.max(source_pw_mW)

    plt.plot(source_wv[200:345], source_pw_mW_norm[200:345], label=f"spectre optique pour {file.name[:-4]}nm")

plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Puissance en mW normalisée")
plt.legend(loc="upper left")
plt.grid(True)
plt.show()
