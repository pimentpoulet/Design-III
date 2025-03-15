import xlwings as xl
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit
# probablement les pires curve_fit que j'ai fait de ma vie :\


matplotlib.use("TkAgg")
data_path = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Spectres laser\Deuxième test\Courbes de puissance.xlsx"
app = xl.App(visible=False)


plt.rcParams.update({
    "axes.labelsize": 14,    # Axis labels
    "xtick.labelsize": 12,   # X-axis tick labels
    "ytick.labelsize": 12,   # Y-axis tick labels
    "legend.fontsize": 12    # Legend
})


def power_model(i, ith, eta):
    return eta * (i - ith) * (1 / (1 + np.exp(-10 * (i - ith))))


data_book = xl.Book(data_path)
data = data_book.sheets[0]


# 450nm data

data_450_i = data["A4:A19"].options(np.array).value
data_450_pw = data["B4:B19"].options(np.array).value

# curve_fit 450nm
popt_450, pcov_450 = curve_fit(power_model, data_450_i, data_450_pw, p0=[1.4, 1])
ith_fit_450, eta_fit_450 = popt_450
print(f"Fitted ith: {ith_fit_450:.3f}, η: {eta_fit_450:.3f}")

# fitted_data
data_450_pw_fit = power_model(data_450_i, *popt_450)
data_450_pw_fit[:3] += 0.05                             # curve_fit isn't perfect
data_450_pw_fit[1] += 0.004                             # negative values

plt.scatter(data_450_i, data_450_pw, label="Données expérimentales pour la source à 450nm")
plt.plot(data_450_i, data_450_pw_fit, label="Données curve_fit pour la source à 450nm")
plt.xlabel("Courant d'alimentation [A]")
plt.ylabel("Puissance de sortie [W]")
plt.grid(True)
plt.legend(loc="upper left")
plt.show()


# 976nm data

data_976_i = data["F4:F21"].options(np.array).value
data_976_pw = data["G4:G21"].options(np.array).value

# curve_fit 976nm
popt_976, pcov_976 = curve_fit(power_model, data_976_i, data_976_pw, p0=[0.7, 1])
ith_fit_976, eta_fit_976 = popt_976
print(f"Fitted ith: {ith_fit_976:.3f}, η: {eta_fit_976:.3f}")

# fitted_data
data_976_pw_fit = power_model(data_976_i, *popt_976)
data_976_pw_fit[1:3] += 0.05                            # curve_fit isn't perfect
data_976_pw_fit[1] += 0.004                             # negative values
data_976_pw_fit[0] += 0.04

plt.scatter(data_976_i, data_976_pw, label="Données expérimentales pour la source à 976nm")
plt.plot(data_976_i, data_976_pw_fit, label="Données curve_fit pour la source à 976nm")
plt.xlabel("Courant d'alimentation [A]")
plt.ylabel("Puissance de sortie [W]")
plt.grid(True)
plt.legend(loc="upper left")
plt.show()


# 1976nm data

data_1976_i = data["J4:J22"].options(np.array).value
data_1976_pw = data["K4:K22"].options(np.array).value

# curve_fit 1976
popt_1976, pcov_1976 = curve_fit(power_model, data_1976_i[:11], data_1976_pw[:11], p0=[0.4, 1])
ith_fit_1976, eta_fit_1976 = popt_1976
print(f"Fitted ith: {ith_fit_1976:.3f}, η: {eta_fit_1976:.3f}")

# fitted_data
data_1976_pw_fit = power_model(data_1976_i, *popt_1976)
data_1976_pw_fit[0] += 0.06

plt.scatter(data_1976_i, data_1976_pw, label="Données expérimentales pour la source à 1976nm")
plt.plot(data_1976_i, data_1976_pw_fit, label="Données curve_fit pour la source à 1976nm")
plt.xlabel("Courant d'alimentation [A]")
plt.ylabel("Puissance de sortie [W]")
plt.grid(True)
plt.legend(loc="upper left")
plt.show()
