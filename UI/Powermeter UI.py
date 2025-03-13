import tkinter as tk
import random
import tkinter.font as tkFont
import matplotlib.pyplot as plt
import xlwings as xl
import numpy as np
import csv
import sys

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, filedialog


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


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class PowerMeterApp:
    def __init__(self, root):

        self.root = root
        self.root.title("Powermeter UI")

        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)
        self.root.columnconfigure(4, weight=1)
        self.root.columnconfigure(5, weight=1)

        self.app = xl.App(visible=False)

        # global variables
        self.wavelengths_1 = None
        self.power_values_1 = None
        self.wavelengths_2 = None
        self.power_values_2 = None
        self.last_selected_wavelength = ""

        size = 20
        self.big_font = tkFont.Font(family='Calibri', size=size)
        self.bigb_font = tkFont.Font(family='Calibri', size=size, weight='bold')

        # setup the power graph
        self.fig_1, self.ax_1 = plt.subplots(figsize=(6, 4))
        self.canvas_1 = FigureCanvasTkAgg(self.fig_1, master=self.root)
        self.canvas_1.get_tk_widget().grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # setup the position graph
        self.fig_2, self.ax_2 = plt.subplots(figsize=(6, 4))
        self.canvas_2 = FigureCanvasTkAgg(self.fig_2, master=self.root)
        self.canvas_2.get_tk_widget().grid(row=2, column=3, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.box = tk.Frame(self.root)
        self.box.grid(row=0, column=0, columnspan=4, padx=25, pady=10, sticky="nsew")

        # power measurement display
        self.power_label = tk.Label(self.box, text="Power reading:")
        self.power_label.grid(row=1, column=5, padx=0, pady=10, sticky="w")
        self.measurement_label = tk.Label(self.box, text="--- mW")
        self.measurement_label.grid(row=1, column=6, padx=0, pady=10, sticky="w")

        # start button (1,0)
        self.start_button = tk.Button(self.box, text="Start", command=self.click_start)
        self.start_button.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        # save button (2,0)
        self.save_button = tk.Button(self.box, text="Save data…", command=self.save_data)
        self.save_button.grid(row=0, column=2, padx=10, pady=10)

        # clear button (3,0)
        self.clear_button_1 = tk.Button(self.box, text="Clear graph 1", command=self.click_clear_1)
        self.clear_button_1.grid(row=0, column=4, padx=10, pady=10)

        # clear button (3,0)
        self.clear_button_2 = tk.Button(self.box, text="Clear graph 2", command=self.click_clear_2)
        self.clear_button_2.grid(row=1, column=4, padx=10, pady=10)

        # load button 1
        self.load_button_1 = tk.Button(self.box, text="Load data 1", command=lambda: self.display_data_1(load_data()))
        self.load_button_1.grid(row=0, column=3, sticky=tk.W, pady=5)

        # load button 2
        self.load_button_2 = tk.Button(self.box, text="Load data 2", command=lambda: self.display_data_2(load_data()))
        self.load_button_2.grid(row=1, column=3, sticky=tk.W)

        # wavelength label
        self.wavelength_label = tk.Label(self.box, text="Wavelength [nm]:")
        self.wavelength_label.grid(row=0, column=5, padx=10, pady=10, sticky="e")

        # wavelength selection drop-down
        self.selected_wavelength = tk.StringVar()
        wavelength_options = sorted(["determine wavelength", 450, 976, 1976], key=lambda x: (isinstance(x, str), x))
        self.wavelength_menu = ttk.Combobox(self.box, textvariable=self.selected_wavelength, values=wavelength_options, width=35)
        self.wavelength_menu.grid(row=0, column=6, padx=10, pady=10, sticky="w")
        # self.wavelength_menu.set("Enter wavelength or select one")

        # Bind events for selection or manual entry
        self.wavelength_menu.bind("<<ComboboxSelected>>", self.on_wavelength_selected)
        self.wavelength_menu.bind("<Return>", self.on_wavelength_entered)
        self.wavelength_menu.bind("<FocusOut>", self.on_wavelength_entered)

        # firmware version label
        self.firmware_label = tk.Label(self.root, text="", font=self.big_font)
        self.firmware_label.grid(row=3, column=0, columnspan=3, padx=25, pady=10, sticky="w")

        self.terminal = tk.Frame(self.root)
        self.terminal.grid(row=3, column=0, columnspan=2, padx=25, pady=25, sticky="nsew")

        self.log_text = tk.Text(self.terminal, height=10, width=120, wrap="word")
        self.log_text.grid(column=0, row=0)
        self.log_text.insert(tk.END, "Log initialized...\n")

        scrollbar = ttk.Scrollbar(self.terminal, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.log_text["yscrollcommand"] = scrollbar.set

        sys.stdout = TextRedirector(self.log_text)

        self.device = PowerMeterDevice()
        self.is_refreshing = False          # flag for running process

        self.plot_y_1 = getattr(self, 'plot_y', [])
        self.plot_x_1 = getattr(self, 'plot_x', [])

        self.plot_y_2 = getattr(self, 'plot_y', [])
        self.plot_x_2 = getattr(self, 'plot_x', [])

        self.update_loop()  # We update once at least

    def on_wavelength_selected(self, event=None):
        """
        Handles when a preset wavelength is selected
        """
        print(f"Selected wavelength: {self.selected_wavelength.get()}")

    def on_wavelength_entered(self, event=None):
        """
        Handles manual entry of wavelength
        """
        new_value = self.selected_wavelength.get()
        if new_value == "" or new_value == self.last_selected_wavelength:
            pass
        else:
            if new_value in self.wavelength_menu["values"]:
                pass
            else:
                self.last_selected_wavelength = new_value

                current_values = list(self.wavelength_menu["value"])
                current_values.append(new_value)
                current_values.sort(key=lambda x: (isinstance(x, str), x))

                self.wavelength_menu["values"] = tuple(current_values)
                print(f"User defined wavelength: {self.selected_wavelength.get()}")

    def display_data_1(self, data_tuple):
        if data_tuple is None:
            return
        self.wavelengths_1, self.power_values_1, file_path = data_tuple

        self.ax_1.clear()
        self.ax_1.plot(self.wavelengths_1, self.power_values_1, label="wpcurve", color="blue", linewidth=1)
        self.ax_1.set_xlabel("Wavelength [nm]")
        self.ax_1.set_ylabel("Power [dB]")
        self.ax_1.set_title("OSA data 1")
        self.ax_1.legend()
        self.ax_1.grid(True)

        self.canvas_1.draw()

        # log to terminal
        print(f"loaded {str(file_path)}")

    def display_data_2(self, data_tuple):
        if data_tuple is None:
            return
        self.wavelengths_2, self.power_values_2, file_path = data_tuple

        self.ax_2.clear()
        self.ax_2.plot(self.wavelengths_2, self.power_values_2, label="wpcurve", color="blue", linewidth=1)
        self.ax_2.set_xlabel("Wavelength [nm]")
        self.ax_2.set_ylabel("Power [dB]")
        self.ax_2.set_title("OSA data 2")
        self.ax_2.legend()
        self.ax_2.grid(True)

        self.canvas_2.draw()

        # log to terminal
        print(f"loaded {str(file_path)}")

    def click_start(self):
        """
        setups the start button, updates the is_refreshing flag and starts data acquisition
        """
        if not self.is_refreshing:                    # if process is not running
            self.is_refreshing = True                 # set flag as process is running
            self.update_loop()                        # starts the process
            self.start_button.config(text="Stop")
            print("Process started !")
        else:
            self.is_refreshing = False                # set flag as process not running
            self.start_button.config(text="Start")
            print("Process stopped !")

    def update_loop(self):
        """
        updates the plot every 300 ms
        """
        self.device.update_from_device()

        power = self.device.power
        self.measurement_label.config(text=f"{power:.2f} mW")

        # Update plot
        last = len(self.plot_x_1) if hasattr(self, 'plot_x_1') else 0
        self.plot_x_1.append(last)
        self.plot_y_1.append(power)

        self.ax_1.clear()
        self.ax_1.plot(self.plot_x_1, self.plot_y_1)
        self.ax_1.set_xlabel('Time')
        self.ax_1.set_ylabel('Power (mW)')
        self.canvas_1.draw()

        if self.is_refreshing:
            self.root.after(300, self.update_loop)    # recursively calls the update_loop function until is_refreshing=False

    def save_data(self):
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

    def click_clear_1(self):
        """
        clears the plot
        """
        self.plot_x_1 = []
        self.plot_y_1 = []
        self.ax_1.clear()
        self.ax_1.set_xlabel('Time')
        self.ax_1.set_ylabel('Power (mW)')
        self.canvas_1.draw()

        # log to terminal
        print("Graph 1 cleared.")

    def click_clear_2(self):
        """
        clears the plot
        """
        self.plot_x_2 = []
        self.plot_y_2 = []
        self.ax_2.clear()
        self.ax_2.set_xlabel('Time')
        self.ax_2.set_ylabel('Power (mW)')
        self.canvas_2.draw()

        # log to terminal
        print("Graph 2 cleared.")


class PowerMeterDevice:
    debug = True

    def __init__(self):
        self.power = 0
        self.wavelength = 1064
        self.firmware = None
        self.temperature = None

    def get_power_from_device(self):
        if self.debug:
            self.power = random.randrange(900, 1000, 1) / 100
        return self.power

    def get_firmware_from_device(self):
        if self.debug:
            self.firmware = "1.0.0alpha1"
        return self.firmware

    def get_temperature_from_device(self):
        if self.debug:
            self.temperature = random.randrange(70, 73, 1)
        return self.temperature

    def get_wavelength_from_device(self):
        if self.debug:
            pass
        return self.wavelength

    def update_from_device(self):
        self.get_power_from_device()
        self.get_firmware_from_device()
        self.get_temperature_from_device()
        self.get_wavelength_from_device()


if __name__ == "__main__":
    root = tk.Tk()
    app = PowerMeterApp(root)
    root.mainloop()
