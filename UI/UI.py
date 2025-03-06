import xlwings as xl
import numpy as np

from tkinter import *
from tkinter import ttk, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


app = xl.App(visible=False)


def load_data():
    """
    Loads a .csv file and displays it in the UI
    """
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return None

    try:
        wb = xl.Book(file_path)
        sheet = wb.sheets[0]
        raw_data = sheet["A40:A540"].options(np.array, expand="table").value
        wb.close()
        split_arr = np.char.split(raw_data, ',')
        return np.array([x[0] for x in split_arr], dtype=float), np.array([x[1] for x in split_arr], dtype=float)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def display_data_1(data_tuple):
    """
    Updates the Matplotlib graph with new data
    """
    wavelengths, power_values = data_tuple
    if data_tuple is None:
        return

    ax1.clear()
    ax1.plot(wavelengths, power_values, label="wpcurve", color="blue", linewidth=1)
    ax1.set_xlabel("Wavelength [nm]")
    ax1.set_ylabel("Power [dB]")
    ax1.set_title("OSA data 1")
    ax1.legend()
    ax1.grid(True)

    canvas.draw()


def display_data_2(data_tuple):
    """
    Updates the Matplotlib graph with new data
    """
    wavelengths, power_values = data_tuple
    if data_tuple is None:
        return

    ax2.clear()
    ax2.plot(wavelengths, power_values, label="wpcurve", color="blue", linewidth=1)
    ax2.set_xlabel("Wavelength [nm]")
    ax2.set_ylabel("Power [dB]")
    ax2.set_title("OSA data 2")
    ax2.legend()
    ax2.grid(True)

    canvas.draw()


root = Tk()
root.title("UI")
root.geometry("1800x800")
root.resizable(True,True)

mainframe = ttk.Frame(root, padding="20 20 20 20")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

power = StringVar()
power_entry = ttk.Entry(mainframe, width=7, textvariable=power)
power_entry.grid(column=1, row=1, sticky=(W, E))
ttk.Label(mainframe, text="Power [mW]").grid(column=2, row=1, sticky=W)

load_button_1 = ttk.Button(root, text="Load Data 1", command=lambda: display_data_1(load_data()))
load_button_1.grid(column=0, row=2, columnspan=2, pady=10)
load_button_2 = ttk.Button(root, text="Load Data 2", command=lambda: display_data_2(load_data()))
load_button_2.grid(column=1, row=2, columnspan=2, pady=10)

fig = Figure(figsize=(14,6), dpi=100)
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(column=0, row=3, columnspan=3, sticky=(N, W, E, S))

root.mainloop()
