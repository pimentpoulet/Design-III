import xlwings as xl
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from pathlib import Path


matplotlib.use("TkAgg")
germanium_thorlabs = Path(r"Absorption Graphs\Uncoated_Ge_Window_RawData.xlsx")

plt.rcParams.update({
    "axes.labelsize": 24,    # Axis labels
    "xtick.labelsize": 24,   # X-axis tick labels
    "ytick.labelsize": 24,   # Y-axis tick labels
    "legend.fontsize": 24    # Legend
})

app = xl.App(visible=False)

wb_data = xl.Book(germanium_thorlabs)
data_sheet = wb_data.sheets[0]
wv_data = data_sheet["C2:C2300"].options(np.array).value
tr_data = data_sheet["D2:D2300"].options(np.array).value

plt.plot(wv_data, tr_data, color="black", label="Transmission de la fenêtre de germanium")
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Transmission de la fenêtre de Germanium [%]")
plt.grid(True)
plt.legend()
plt.show()
