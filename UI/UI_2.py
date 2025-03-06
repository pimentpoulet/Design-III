import xlwings as xl
import numpy as np
import csv
import sys
import tkinter as tk

from tkinter import *
from tkinter import ttk, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


app = xl.App(visible=False)
wavelengths_1 = None
power_values_1 = None
wavelengths_2 = None
power_values_2 = None


class TextRedirector:
    """
    Redirects stdout to a Tkinter Text terminal
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.End, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


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

    global wavelengths_1, power_values_1
    if data_tuple is None:
        return
    wavelengths_1, power_values_1 = data_tuple

    ax1.clear()
    ax1.plot(wavelengths_1, power_values_1, label="wpcurve", color="blue", linewidth=1)
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
    global wavelengths_2, power_values_2
    if data_tuple is None:
        return
    wavelengths_2, power_values_2 = data_tuple

    ax2.clear()
    ax2.plot(wavelengths_2, power_values_2, label="wpcurve", color="blue", linewidth=1)
    ax2.set_xlabel("Wavelength [nm]")
    ax2.set_ylabel("Power [dB]")
    ax2.set_title("OSA data 2")
    ax2.legend()
    ax2.grid(True)

    canvas.draw()


def save_data_1():
    """
    Saves the data from the power graph to a user-specified location
    """
    global wavelengths_1, power_values_1
    if wavelengths_1 is None or power_values_1 is None:
        print("No data to save!")
        return

    # get the saving path
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt")])
    if not file_path:
        return

    # Save data to CSV file
    try:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Wavelength [nm]", "Power [dB]"])  # Header
            for w, p in zip(wavelengths_1, power_values_1):
                writer.writerow([w, p])

        print(f"Data saved successfully to {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")


# UI window setup
root = Tk()
root.title("UI")
root.geometry("1800x800")
root.resizable(True,True)

mainframe = ttk.Frame(root, padding="20 20 20 20")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Power entry
power = StringVar()
power_entry = ttk.Entry(mainframe, width=7, textvariable=power)
power_entry.grid(column=1, row=1, sticky=(W, E))
ttk.Label(mainframe, text="Power [mW]").grid(column=2, row=1, sticky=W)

# Load buttons
load_button_1 = ttk.Button(root, text="Load Data 1", command=lambda: display_data_1(load_data()))
load_button_1.grid(column=0, row=1, columnspan=2, pady=10)
load_button_2 = ttk.Button(root, text="Load Data 2", command=lambda: display_data_2(load_data()))
load_button_2.grid(column=1, row=1, columnspan=2, pady=10)

# Save button
save_button_1 = ttk.Button(root, text="Save Data 1", command=save_data_1)
save_button_1.grid(column=0, row=2, columnspan=2, pady=10)

# Figure for graphs
fig = Figure(figsize=(14,6), dpi=100)
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(column=0, row=3, columnspan=3, sticky=(N, W, E, S))

# Terminal
log_frame = ttk.LabelFrame(root, text="Log Output")
log_frame.grid(column=0, row=4, columnspan=3, sticky=(W, E, S), pady=10, padx=10)

log_text = tk.Text(log_frame, height=10, width=120, wrap="word")
log_text.grid(column=0, row=0, sticky=(W, E, S, N))
log_text.insert(tk.END, "Log initialized...\n")

# scrollbar for terminal
scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
scrollbar.grid(column=1, row=0, sticky=(N, S))
log_text["yscrollcommand"] = scrollbar.set

# prints --> terminal
sys.stdout = TextRedirector(log_text)

root.mainloop()
