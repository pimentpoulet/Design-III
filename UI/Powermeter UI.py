import tkinter as tk
# import random
import tkinter.font as tkFont
import matplotlib.pyplot as plt
import xlwings as xl
import numpy as np
import csv
import sys

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from time import sleep
from powermeter import PowerMeter


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

        logo_path = r"C:\Clément PC_t\UL\Session H2025_6\Design III\Powermeter App\RVLABS.png"
        image = Image.open(logo_path)
        image = image.resize((300, 150), Image.LANCZOS)
        self.logo_img = ImageTk.PhotoImage(image)

        self.app = xl.App(visible=False)

        # global variables
        self.wavelengths_1 = None
        self.power_values_1 = None
        self.wavelengths_2 = None
        self.power_values_2 = None
        self.last_selected_wavelength = ""
        self.current_values = [450, 976, 1976]

        # fonts
        font = tkFont.Font(family='Trebuchet MS', size=12)
        font_pw = tkFont.Font(family='Trebuchet MS', size=18)

        """ global frames """

        # upper global frame
        self.up_glob_frame = tk.Frame(self.root, background="gray", highlightbackground="black", highlightthickness=2)
        self.up_glob_frame.grid(row=0, column=0, rowspan=2, columnspan=5, padx=25, pady=10, sticky="nsew")

        # mid global frame
        self.mid_glob_frame = tk.Frame(self.root, background="gray", highlightbackground="black", highlightthickness=2)
        self.mid_glob_frame.grid(row=2, column=0, rowspan=2, columnspan=5, padx=25, pady=10, sticky="nsew")

        # lower global frame
        self.lw_glob_frame = tk.Frame(self.root, background="gray", highlightbackground="black", highlightthickness=2)
        self.lw_glob_frame.grid(row=4, column=0, rowspan=3, columnspan=5, padx=25, pady=10, sticky="nsew")

        """ subglobal frames """

        # acquisition frame
        self.acq_frame = tk.Frame(self.up_glob_frame, highlightbackground="black", highlightthickness=2)
        self.acq_frame.grid(row=0, column=0, columnspan=1, padx=25, pady=10, sticky="nsw")

        # measures frame
        self.meas_frame = tk.Frame(self.up_glob_frame, highlightbackground="black", highlightthickness=2)
        self.meas_frame.grid(row=0, column=2, columnspan=2, padx=25, pady=10, sticky="nsew")

        # graphs frame
        self.graph_frame = tk.Frame(self.mid_glob_frame, highlightbackground="black", highlightthickness=2)
        self.graph_frame.grid(row=0, column=0, rowspan=2, columnspan=5, padx=25, pady=10, sticky="nsew")

        # terminal frame
        self.term_frame = tk.Frame(self.lw_glob_frame, highlightbackground="black", highlightthickness=2)
        self.term_frame.grid(row=0, column=0, rowspan=2, columnspan=2, padx=25, pady=10, sticky="nsew")

        # logo frame
        self.logo_frame = tk.Frame(self.lw_glob_frame, highlightbackground="black", highlightthickness=2)
        self.logo_frame.grid(row=0, column=2, columnspan=2, padx=25, pady=10)
        self.logo_frame.configure(width=300, height=150)

        # version frame
        self.vrs_frame = tk.Frame(self.lw_glob_frame, highlightbackground="black", highlightthickness=2)
        self.vrs_frame.grid(row=2, column=0, padx=25, pady=10, sticky="nsew")

        """ configure frames """

        # root
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)
        self.root.columnconfigure(4, weight=1)

        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.rowconfigure(4, weight=1)

        # global frames
        self.up_glob_frame.columnconfigure(0, weight=1)
        self.up_glob_frame.columnconfigure(1, weight=1)
        self.up_glob_frame.columnconfigure(2, weight=1)
        self.up_glob_frame.columnconfigure(3, weight=1)

        self.up_glob_frame.rowconfigure(0, weight=1)
        self.up_glob_frame.rowconfigure(1, weight=1)
        self.up_glob_frame.rowconfigure(2, weight=1)

        self.mid_glob_frame.columnconfigure(0, weight=1)
        self.mid_glob_frame.columnconfigure(1, weight=1)
        self.mid_glob_frame.columnconfigure(2, weight=1)
        self.mid_glob_frame.columnconfigure(3, weight=1)

        self.mid_glob_frame.rowconfigure(0, weight=1)
        self.mid_glob_frame.rowconfigure(1, weight=1)
        self.mid_glob_frame.rowconfigure(2, weight=1)

        self.lw_glob_frame.columnconfigure(0, weight=1)
        self.lw_glob_frame.columnconfigure(1, weight=1)
        self.lw_glob_frame.columnconfigure(2, weight=1)
        self.lw_glob_frame.columnconfigure(3, weight=1)

        self.lw_glob_frame.rowconfigure(0, weight=1)
        self.lw_glob_frame.rowconfigure(1, weight=1)
        self.lw_glob_frame.rowconfigure(2, weight=1)

        # graph_frame
        self.graph_frame.columnconfigure(0, weight=1)
        self.graph_frame.columnconfigure(1, weight=1)
        self.graph_frame.columnconfigure(2, weight=1)
        self.graph_frame.columnconfigure(3, weight=1)
        self.graph_frame.columnconfigure(4, weight=1)

        self.graph_frame.rowconfigure(0, weight=1)
        self.graph_frame.rowconfigure(1, weight=1)

        """ acq_frame """

        # start button
        self.start_button = tk.Button(self.acq_frame, text="Démarrer", command=self.click_start, font=font)
        self.start_button.grid(row=1, column=0, padx=10, pady=10, sticky="we")

        # start camera button
        self.start_cam_button = tk.Button(self.acq_frame, text="Démarrer la caméra", command=self.click_start_cam, font=font)
        self.start_cam_button.grid(row=1, column=1, padx=10, pady=10, sticky="we")

        # wavelength selection drop-down
        self.selected_wavelength = tk.StringVar()
        wavelength_options = ["déterminer la longueur d'onde"] + sorted(self.current_values)
        self.wavelength_menu = ttk.Combobox(self.acq_frame, textvariable=self.selected_wavelength, values=wavelength_options,
                                            width=30, font=font)
        self.wavelength_menu.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        # Bind events for selection or manual entry
        self.wavelength_menu.bind("<<ComboboxSelected>>", self.on_wavelength_selected)
        self.wavelength_menu.bind("<Return>", self.on_wavelength_entered)
        self.wavelength_menu.bind("<FocusOut>", self.on_wavelength_entered)

        # wavelength label
        self.wavelength_label = tk.Label(self.acq_frame, text="Mode du puissance-mètre [nm]:", font=font)
        self.wavelength_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        """ meas_frame """

        # power measurement display
        self.power_label = tk.Label(self.meas_frame, text="Puissance mesurée [W]:", font=font_pw)
        self.power_label.grid(row=0, column=1, padx=15, pady=10, sticky="e")
        self.measurement_label = tk.Label(self.meas_frame, text="---", font=font_pw)
        self.measurement_label.grid(row=0, column=2, padx=0, pady=10, sticky="w")

        # wavelength measurement display
        self.wv_label = tk.Label(self.meas_frame, text="Longueur d'onde mesurée [nm]:", font=font_pw)
        self.wv_label.grid(row=1, column=1, padx=15, pady=10, sticky="e")
        self.wv_measurement_label = tk.Label(self.meas_frame, text="----", font=font_pw)
        self.wv_measurement_label.grid(row=1, column=2, padx=0, pady=10, sticky="w")

        """ graph_frame """

        # power graph
        self.fig_1, self.ax_1 = plt.subplots(figsize=(6, 5))
        self.canvas_1 = FigureCanvasTkAgg(self.fig_1, master=self.graph_frame)
        self.ax_1.set_xlabel("Temps [s]")
        self.ax_1.set_ylabel("Puissance [mW]")
        self.ax_1.set_ylim(-1, 12)
        self.ax_1.grid(True)

        # position graph
        self.fig_2, self.ax_2 = plt.subplots(figsize=(5, 5))
        self.canvas_2 = FigureCanvasTkAgg(self.fig_2, master=self.graph_frame)
        self.ax_2.set_title("Image thermique")
        self.ax_2.axis("off")

        # place graphs
        self.canvas_1.get_tk_widget().grid(row=0, column=0, columnspan=3, padx=15, pady=10, sticky="nsew")
        self.canvas_2.get_tk_widget().grid(row=0, column=3, columnspan=2, padx=15, pady=10, sticky="nsew")

        # clear button 1
        self.clear_button_1 = tk.Button(self.graph_frame, text="Effacer le graphique de puissance",
                                        command=self.click_clear_1,
                                        font=font)
        self.clear_button_1.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # save button 1
        self.save_button_1 = tk.Button(self.graph_frame, text="Enregistrer les données de puissance",
                                       command=self.save_data, font=font)
        self.save_button_1.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # load button 1
        self.load_button_1 = tk.Button(self.graph_frame, text="Charger des données de puissance",
                                       command=lambda: self.display_data_1(load_data()), font=font)
        self.load_button_1.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        # clear button 2
        self.clear_button_2 = tk.Button(self.graph_frame, text="Effacer le graphique de position",
                                        command=self.click_clear_2,
                                        font=font)
        self.clear_button_2.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

        """ term_frame """

        # terminal
        self.log_text = tk.Text(self.term_frame, height=8, width=120, wrap="word", font=font)
        self.log_text.grid(column=0, row=0, sticky="nsew")
        self.log_text.insert(tk.END, " Journaux d'application initialisés...\n")

        # terminal scrollbar
        scrollbar = ttk.Scrollbar(self.term_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(column=1, row=0, sticky="nsew")
        self.log_text["yscrollcommand"] = scrollbar.set

        # print logs to terminal
        sys.stdout = TextRedirector(self.log_text)

        """ logo_frame """

        # RVLABS logo
        self.logo = tk.Label(self.logo_frame, image=self.logo_img)
        self.logo.grid(row=0, column=0, sticky="ne")

        # firmware version label
        self.firmware_label = tk.Label(self.vrs_frame, text="1.0.0alpha1")
        self.firmware_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        """ instantiate the UI """

        # create a Powermeter class instance
        self.pm = PowerMeter()

        # set flags
        self.is_refreshing = False
        self.cam_is_refreshing = False

        # necessary initializations
        self.plot_y_1 = getattr(self, 'plot_y', [])
        self.plot_x_1 = getattr(self, 'plot_x', [])

        self.plot_y_2 = getattr(self, 'plot_y', [])
        self.plot_x_2 = getattr(self, 'plot_x', [])

        # self.update_loop()  # We update once at least

    def on_wavelength_selected(self, event=None):
        """
        Handles when a preset wavelength is selected
        """
        if self.selected_wavelength.get() == "déterminer la longueur d'onde":
            print(" Mode de détermination de la longueur d'onde activé.")
        else:
            print(f" Longueur d'onde choisie: {self.selected_wavelength.get()} nm")

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
                try:
                    self.current_values.append(int(new_value))
                    self.current_values.sort()

                    self.wavelength_menu["values"] = tuple(["déterminer la longueur d'onde"] + self.current_values)
                    print(f" L'utilisateur a défini la longueur d'onde: {self.selected_wavelength.get()} nm")

                except Exception as e:
                    print(f" La longueur d'onde entrée manuellement doit être un nombre !")

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
        print(f" Fichier chargé: {str(file_path)}")

    def display_data_2(self, camera_data: np.ndarray):
        print("tutu")
        if camera_data is None:
            return

        self.ax_2.clear()
        self.ax_2.imshow(camera_data, cmap="plasma")
        self.ax_2.set_title("Image thermique")
        self.ax_2.axis("off")

        self.canvas_2.draw()

        # log to terminal
        # print(f" Fichier chargé: {str(file_path)}")

    def click_start(self):
        """
        setups the start button, updates the is_refreshing flag and starts data acquisition
        """
        if not self.is_refreshing:
            self.is_refreshing = True
            self.update_loop()
            self.start_button.config(text="Arrêter")
            print(" Processus démarré !")
        else:
            self.is_refreshing = False
            self.start_button.config(text="Démarrer")
            print(" Processus arrêté !")

    def click_start_cam(self):
        """
        setups the start camera button, updates the cam_is_refreshing flag and starts camera data acquisition
        """
        if not self.cam_is_refreshing:
            self.cam_is_refreshing = True
            self.start_cam_button.config(text="Arrêter la caméra")
            self.update_cam()
            print(" Caméra démarrée !")
        else:
            self.cam_is_refreshing = False
            self.start_cam_button.config(text="Démarrer la caméra")
            print(" Caméra arrêtée !")

    def update_loop(self):
        """
        updates the plot every 300 ms
        """
        if False:
            self.device.update_from_device()

            power = self.device.power
            self.measurement_label.config(text=f"{power:.2f} mW")

            # Update plot
            last = len(self.plot_x_1) if hasattr(self, 'plot_x_1') else 0
            self.plot_x_1.append(last)
            self.plot_y_1.append(power)

            self.ax_1.clear()
            self.ax_1.plot(self.plot_x_1, self.plot_y_1)
            self.ax_1.set_xlabel('Temps [s]')
            self.ax_1.set_ylabel('Puissance (mW)')
            self.ax_1.set_ylim(-1, 12)
            self.ax_1.grid(True)

            self.canvas_1.draw()

            if self.is_refreshing:
                self.root.after(1000, self.update_loop)    # recursively calls the update_loop function until is_refreshing=False
        pass

    def update_cam(self):
        """
        updates the camera plot
        """
        if self.cam_is_refreshing:
            try:
                camera_data = self.pm.get_temp()
                print("Température captée :", camera_data.shape, camera_data.min(), camera_data.max())
                
                self.ax_2.clear()
                self.ax_2.imshow(camera_data, cmap="plasma")
                self.ax_2.set_title("Image thermique")
                self.ax_2.axis("off")
                self.canvas_2.draw()
                
            except Exception as e:
                print(f"Erreur lors de la mise à jour de la caméra : {e}")
            
            self.root.after(1000, self.update_cam)

    def save_data(self):
        if self.wavelengths_1 is None or self.power_values_1 is None:
            print(" No data to save!")
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
            print(f" Données enregistrées à {file_path}")
        except Exception as e:
            print(f" Erreur durant la sauvegarde: {e}")

    def click_clear_1(self):
        """
        clears the plot
        """
        self.wavelengths_1 = None
        self.power_values_1 = None

        self.plot_x_1 = []
        self.plot_y_1 = []
        self.ax_1.clear()
        self.ax_1.set_xlabel('Time')
        self.ax_1.set_ylabel('Power (mW)')
        self.ax_1.grid(True)
        self.canvas_1.draw()

        # log to terminal
        print(" Graphique de puissance effacé.")

    def click_clear_2(self):
        """
        clears the plot
        """
        self.plot_x_2 = []
        self.plot_y_2 = []
        self.ax_2.clear()

        self.ax_2.set_xlabel("Position [mm]")
        self.ax_2.set_ylabel("Position [mm]")
        self.ax_2.set_xlim(-6, 6)
        self.ax_2.set_ylim(-6, 6)
        self.ax_2.grid(True)

        self.canvas_2.draw()

        # log to terminal
        print(" Graphique de position effacé.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PowerMeterApp(root)
    root.mainloop()
