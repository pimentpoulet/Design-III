import xlwings as xl
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt
from pathlib import Path


matplotlib.use("TkAgg")
data_path = Path(r"C:\Clément MSI\UL\Session H2025_6\Design III\Design-III\UI\test_1.csv")

plt.rcParams.update({
    "axes.labelsize": 18,    # Axis labels
    "xtick.labelsize": 16,   # X-axis tick labels
    "ytick.labelsize": 16,   # Y-axis tick labels
    "legend.fontsize": 16    # Legend
})

app = xl.App(visible=False)

wb_data = xl.Book(data_path)
data_sheet = wb_data.sheets[0]
raw_data = data_sheet.range("A2").expand('down').options(np.array).value
split_arr = np.char.split(raw_data, ',')

wv = np.array([x[0] for x in split_arr], dtype=float)
pw = np.array([x[1] for x in split_arr], dtype=float)

plt.plot(wv, pw, label="test_1.csv")
plt.xlabel("Temps [s]")
plt.ylabel("Puissance [dBm]")
plt.grid(True)
plt.legend(loc="lower right")
plt.show()
