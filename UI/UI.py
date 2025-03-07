import xlwings as xl
import numpy as np
import csv
import sys
import tkinter as tk

from tkinter import ttk, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


def load_data():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return None

    try:
        wb = xl.Book(file_path)
        sheet = wb.sheets[0]
        raw_data = sheet["A40:A540"].options(np.array, expand="table").value
        wb.close()
        split_arr = np.char.split(raw_data, ',')
        return np.array([x[0] for x in split_arr], dtype=float), np.array([x[1] for x in split_arr], dtype=float), file_path
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def print_grid_info(root):
    for child in root.winfo_children():
        info = child.grid_info()
        if info:
            print(f"Widget: {child}, Row: {info['row']}, Column: {info['column']}")


class PowerMeterApp:
    def __init__(self, root):

        self.root = root
        self.root.title("Powermeter UI")
        # self.root.state("zoomed")
        self.root.resizable(True, True)

        self.power = None
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.canvas = None
        self.log_text = None

        # global variables
        self.wavelengths_1 = None
        self.power_values_1 = None
        self.wavelengths_2 = None
        self.power_values_2 = None

        self.app = xl.App(visible=False)

        self.setup_ui()

    def setup_ui(self):
        mainframe = ttk.Frame(self.root, padding="20 20 20 20")
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # 4 even columns
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)

        # 4 even rows
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)

        self.power = tk.StringVar()
        power_entry = ttk.Entry(mainframe, width=7, textvariable=self.power)
        power_entry.grid(column=0, row=0, sticky=(tk.W, tk.E))
        ttk.Label(mainframe, text="Power [mW]").grid(column=1, row=0, sticky=tk.N)
        ttk.Label(mainframe, text="Test Position").grid(column=0, row=3)

        # data loading buttons
        ttk.Button(self.root, text="Load Data 1", command=lambda: self.display_data_1(load_data())).grid(column=0,
                                                                                                         row=2,
                                                                                                         sticky=tk.W,
                                                                                                         pady=10)
        ttk.Button(self.root, text="Load Data 2", command=lambda: self.display_data_2(load_data())).grid(column=1,
                                                                                                         row=2,
                                                                                                         sticky=tk.W,
                                                                                                         pady=10)
        # saving button
        ttk.Button(self.root, text="Save Data 1", command=self.save_data_1).grid(column=0, row=2, pady=10)

        self.fig = Figure(figsize=(7, 2), dpi=100)
        self.ax1 = self.fig.add_subplot(121)
        # self.ax2 = self.fig.add_subplot(122)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(column=0, row=1, sticky=tk.W)

        # terminal setup
        log_frame = ttk.LabelFrame(self.root, text="Terminal")
        log_frame.grid(column=0, row=4, sticky=(tk.W, tk.E, tk.S), pady=20, padx=20)    # sticky OK

        self.log_text = tk.Text(log_frame, height=10, width=120, wrap="word")
        self.log_text.grid(column=0, row=0)
        self.log_text.insert(tk.END, "Log initialized...\n")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.log_text["yscrollcommand"] = scrollbar.set

        sys.stdout = TextRedirector(self.log_text)

        # debugging
        print_grid_info(self.root)

    def display_data_1(self, data_tuple):
        if data_tuple is None:
            return
        self.wavelengths_1, self.power_values_1, file_path = data_tuple

        self.ax1.clear()
        self.ax1.plot(self.wavelengths_1, self.power_values_1, label="wpcurve", color="blue", linewidth=1)
        self.ax1.set_xlabel("Wavelength [nm]")
        self.ax1.set_ylabel("Power [dB]")
        self.ax1.set_title("OSA data 1")
        self.ax1.legend()
        self.ax1.grid(True)

        self.canvas.draw()

        # log to terminal
        print(f"loaded {str(file_path)}")

    def display_data_2(self, data_tuple):
        if data_tuple is None:
            return
        self.wavelengths_2, self.power_values_2, file_path = data_tuple

        try:
            self.ax2.clear()
            self.ax2.plot(self.wavelengths_2, self.power_values_2, label="wpcurve", color="blue", linewidth=1)
            self.ax2.set_xlabel("Wavelength [nm]")
            self.ax2.set_ylabel("Power [dB]")
            self.ax2.set_title("OSA data 2")
            self.ax2.legend()
            self.ax2.grid(True)

            self.canvas.draw()

            # log to terminal
            print(f"loaded {str(file_path)}")

        except Exception as e:
            print(f"Error displaying data: {e}")

    def save_data_1(self):
        if self.wavelengths_1 is None or self.power_values_1 is None:
            print("No data to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Wavelength [nm]", "Power [dB]"])
                for w, p in zip(self.wavelengths_1, self.power_values_1):
                    writer.writerow([w, p])

            print(f"Data saved successfully to {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PowerMeterApp(root)
    root.mainloop()
