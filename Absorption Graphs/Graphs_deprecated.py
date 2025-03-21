import xlwings as xl
import numpy as np
import matplotlib.pyplot as plt
import os

from pathlib import Path


# DATA LOW WAVELENGTH

data = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data low")
save_folder_1 = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Stacked Figs Low"
save_folder_2 = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Single Figs Low"
save_folder_3 = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Difference Figs Low"

app = xl.App(visible=False)

# loop for stacked graphs figure
for file in data.iterdir():
    if file.is_file():
        wb = xl.Book(file)
        sheet = wb.sheets[0]

        raw_data = sheet["A40:A540"].options(np.array, expand="table").value

        split_arr = np.char.split(raw_data, ',')
        wavelength = np.array([x[0] for x in split_arr], dtype=float)
        power = np.array([x[1] for x in split_arr], dtype=float)

        plt.plot(wavelength, power)

        os.makedirs(save_folder_1, exist_ok=True)
        save_path = os.path.join(save_folder_1, f"{file.name[:-4]}")

        plt.savefig(save_path)


ref = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data low\SREF-350-1200.CSV"
ref_sheet = xl.Book(ref).sheets[0]
ref_data = ref_sheet["A40:A540"].options(np.array, expand="table").value

split_arr = np.char.split(ref_data, ',')
ref_wavelength = np.array([x[0] for x in split_arr], dtype=float)
ref_power = np.array([x[1] for x in split_arr], dtype=float)

# loop for single graph figures
for file in data.iterdir():
    if file.is_file():
        wb = xl.Book(file)
        sheet = wb.sheets[0]

        raw_data = sheet["A40:A540"].options(np.array, expand="table").value

        split_arr = np.char.split(raw_data, ',')
        wavelength = np.array([x[0] for x in split_arr], dtype=float)
        power = np.array([x[1] for x in split_arr], dtype=float)

        plt.clf()
        plt.plot(wavelength, power)

        os.makedirs(save_folder_2, exist_ok=True)
        save_path = os.path.join(save_folder_2, f"{file.name[:-4]}")
        plt.savefig(save_path)

        if str(file) != ref:
            wb = xl.Book(file)
            sheet = wb.sheets[0]

            raw_data = sheet["A40:A540"].options(np.array, expand="table").value

            split_arr = np.char.split(raw_data, ',')
            wavelength = np.array([x[0] for x in split_arr], dtype=float)
            power = np.array([x[1] for x in split_arr], dtype=float)

            plt.clf()
            plt.plot(wavelength, ref_power - power)

            os.makedirs(save_folder_3, exist_ok=True)
            save_path = os.path.join(save_folder_3, f"{file.name[:-4]}")
            plt.savefig(save_path)


# DATA HIGH WAVELENGTH

data = Path(r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data high")
save_folder_1 = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Stacked Figs High"
save_folder_2 = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Single Figs High"
save_folder_3 = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Difference Figs High"

app = xl.App(visible=False)
plt.clf()

# loop for stacked graphs figure
for file in data.iterdir():
    if file.is_file():
        wb = xl.Book(file)
        sheet = wb.sheets[0]

        raw_data = sheet["A40:A540"].options(np.array, expand="table").value

        split_arr = np.char.split(raw_data, ',')
        wavelength = np.array([x[0] for x in split_arr], dtype=float)
        power = np.array([x[1] for x in split_arr], dtype=float)

        plt.plot(wavelength, power)

        os.makedirs(save_folder_1, exist_ok=True)
        save_path = os.path.join(save_folder_1, f"{file.name[:-4]}")

        plt.savefig(save_path)


ref = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Analyses OSA\Data high\SREF-1200-2400.CSV"
ref_sheet = xl.Book(ref).sheets[0]
ref_data = ref_sheet["A40:A540"].options(np.array, expand="table").value

split_arr = np.char.split(ref_data, ',')
ref_wavelength = np.array([x[0] for x in split_arr], dtype=float)
ref_power = np.array([x[1] for x in split_arr], dtype=float)

# loop for single graph figures
for file in data.iterdir():
    if file.is_file():
        wb = xl.Book(file)
        sheet = wb.sheets[0]

        raw_data = sheet["A40:A540"].options(np.array, expand="table").value

        split_arr = np.char.split(raw_data, ',')
        wavelength = np.array([x[0] for x in split_arr], dtype=float)
        power = np.array([x[1] for x in split_arr], dtype=float)

        plt.clf()
        plt.plot(wavelength, power)

        os.makedirs(save_folder_2, exist_ok=True)
        save_path = os.path.join(save_folder_2, f"{file.name[:-4]}")
        plt.savefig(save_path)

        if str(file) != ref:
            wb = xl.Book(file)
            sheet = wb.sheets[0]

            raw_data = sheet["A40:A540"].options(np.array, expand="table").value

            split_arr = np.char.split(raw_data, ',')
            wavelength = np.array([x[0] for x in split_arr], dtype=float)
            power = np.array([x[1] for x in split_arr], dtype=float)

            plt.clf()
            plt.plot(wavelength, ref_power - power)

            os.makedirs(save_folder_3, exist_ok=True)
            save_path = os.path.join(save_folder_3, f"{file.name[:-4]}")
            plt.savefig(save_path)
