import xlwings as xl
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit


matplotlib.use("TkAgg")
data_path = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Spectres laser\Deuxième test\TestLaser(14_03_2025).xlsx"
app = xl.App(visible=False)

plt.rcParams.update({
    "axes.labelsize": 14,    # Axis labels
    "xtick.labelsize": 12,   # X-axis tick labels
    "ytick.labelsize": 12,   # Y-axis tick labels
    "legend.fontsize": 12    # Legend
})


def gaussian(x, a, mu, sigma):
    return a * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))


def find_base_width(position, power, wv):
    if wv == 450:
        threshold_factor = 0.3
    else:
        threshold_factor = 0.22
    max_power = max(power)
    threshold = threshold_factor * max_power

    indices_above = np.where(power > threshold)[0]

    if len(indices_above) > 0:
        left_index = indices_above[0]
        right_index = indices_above[-1]

        left_pos = position[left_index]
        right_pos = position[right_index]

        base_width = right_pos - left_pos
        return left_pos, right_pos, base_width, max_power, threshold
    else:
        return None, None, None, None, None


data_book = xl.Book(data_path)
data = data_book.sheets[0]

# 450nm data
data_450_pos = data["B4:B76"].options(np.array).value
data_450_pw = data["C4:C76"].options(np.array).value

# 976nm data
data_976_pos = data["M4:M137"].options(np.array).value
data_976_pw = data["N4:N137"].options(np.array).value

# 1976nm data
data_1976_pos = data["X4:X83"].options(np.array).value
data_1976_pw = data["Y4:Y83"].options(np.array).value


# 450nm

left_450, right_450, width_450, max_450_pw, pw_450_th = find_base_width(data_450_pos, data_450_pw, wv=450)
print(f"\n450nm Base Width: {width_450:.2f} mm (from {left_450:.2f} to {right_450:.2f})\nMax power: {max_450_pw} | Threshold power: {pw_450_th}")

# base width annotation
mid_pos_450 = (left_450 + right_450) / 2
mid_pw_450 = (pw_450_th + pw_450_th) / 2 + 0.02 * max(data_450_pw)

plt.plot(data_450_pos, data_450_pw, label="experimental data")
plt.plot([left_450, right_450 + 13.5], [pw_450_th, pw_450_th], label="Base Width", linestyle="--", color="black")

plt.text(mid_pos_450, mid_pw_450, f"Base Width = {width_450:.2f} mm", ha="center", fontsize=12, color="black")

plt.xlabel("Position [mm]")
plt.ylabel("Puissance [mW]")
plt.legend()
plt.grid(True)
plt.show()


# 976nm

left_976, right_976, width_976, max_976_pw, pw_976_th = find_base_width(data_976_pos, data_976_pw, wv=976)
print(f"\n976nm Base Width: {width_976:.2f} mm (from {left_976:.2f} to {right_976:.2f})\nMax power: {max_976_pw} | Threshold power: {pw_976_th}")

# base width annotation
mid_pos_976 = (left_976 + right_976) / 2
mid_pw_976 = (pw_976_th + pw_976_th) / 2 + 0.02 * max(data_976_pw)

plt.plot(data_976_pos, data_976_pw, label="experimental data")
plt.plot([left_976, right_976 + 94], [pw_976_th, pw_976_th], label="Base Width", linestyle="--", color="black")

plt.text(mid_pos_976, mid_pw_976, f"Base Width = {width_976:.2f} mm", ha="center", fontsize=12, color="black")

plt.xlabel("Position [mm]")
plt.ylabel("Puissance [mW]")
plt.legend()
plt.grid(True)
plt.show()


# 1976nm

# curvefit gaussien sur le 1976nm
mean = sum(data_1976_pos * data_1976_pw) / sum(data_1976_pw)
sigma = np.sqrt(sum(data_1976_pw * (data_1976_pos - mean) ** 2) / sum(data_1976_pw))

# curve_fit a gaussian
params, covariance = curve_fit(gaussian, data_1976_pos, data_1976_pw, p0=[max(data_1976_pw), mean, sigma])
a_fit, mu_fit, sigma_fit = params

# fitted gaussian data
data_1976_pw_fit = gaussian(data_1976_pos, a_fit, mu_fit, sigma_fit)

half_max_amplitude = a_fit / 2              # max_amplitude = a_fit
peak_index = np.argmax(data_1976_pw_fit)
peak_pos = data_1976_pos[peak_index]

# get indices for FWHM
indices_below = np.where(data_1976_pw_fit[:peak_index] < half_max_amplitude)[0]
indices_above = np.where(data_1976_pw_fit[peak_index:] < half_max_amplitude)[0] + peak_index
left_index = indices_below[-1]
right_index = indices_above[0]

# get FWHM data
left_pos = data_1976_pos[left_index]
right_pos = data_1976_pos[right_index]
left_pw = data_1976_pw[left_index]
right_pw = data_1976_pw[right_index]

# FWHM annotation
fhwm_value = right_pos - left_pos
mid_pos_1976 = (left_pos + right_pos) / 2
mid_pw_1976 = (left_pw + right_pw) / 2 + 0.035 * max(data_1976_pw)

# graph data
plt.plot(data_1976_pos, data_1976_pw, label="experimental data", color="blue")
plt.plot(data_1976_pos, data_1976_pw_fit, label="fitted data", color="red")
plt.plot([left_pos, right_pos], [left_pw, right_pw], label="FWHM", linestyle="--", color="black")

plt.text(mid_pos_1976, mid_pw_1976, f"FWHM = {fhwm_value:.2f} mm", ha="center", fontsize=12, color="black")

plt.xlabel("Position [mm]")
plt.ylabel("Puissance [mW]")
plt.legend()
plt.grid(True)
plt.show()
