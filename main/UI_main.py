import tkinter as tk
import tkinter.font as tkFont
import matplotlib.pyplot as plt
import xlwings as xl
import numpy as np
import csv
import sys
import os
import time
import serial
import serial.tools.list_ports
import webbrowser

from ToggleButton_main import ToggleButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from powermeter_main import PowerMeter
from matplotlib.patches import Circle


class TextRedirector:
    def __init__(self, text_widget):
        self.terminal = text_widget

    def write(self, message):
        self.terminal.configure(state='normal')
        self.terminal.insert(tk.END, message)
        self.terminal.see(tk.END)
        self.terminal.configure(state='disabled')

    def flush(self):
        pass


class PowerMeterApp:
    def __init__(self, root):

        self.root = root
        self.root.title("Powermeter UI")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.configure(background = "red")

        logo_path = r"Threading_dev\RVLABS_logo.png"
        image = Image.open(logo_path)
        image = image.resize((300, 150), Image.LANCZOS)
        self.logo_img = ImageTk.PhotoImage(image)

        self.app = xl.App(visible=False, add_book=False)

        # global variables
        self.wavelengths_1 = None
        self.power_values_1 = None
        self.wavelengths_2 = None
        self.power_values_2 = None
        self.position_tuple = (0, 0)
        self.last_selected_wavelength = ""
        self.current_values = [450, 976, 1976]

        # time parameters
        self.total_saving_duration = None    #  si c'est None, la durée d'enregistrement est illimitée
        self.current_save_duration = 0
        self.power_time_inc = 1000           # ms --> updates power and position graphs at 1Hz

        # save parameters
        self.recording_path = None

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
        self.acq_frame.grid(row=0, column=0, columnspan=1, padx=15, pady=5, sticky="nsw")

        # measures frame
        self.meas_frame = tk.Frame(self.up_glob_frame, highlightbackground="black", highlightthickness=2)
        self.meas_frame.grid(row=0, column=2, columnspan=2, padx=15, pady=5, sticky="nsew")

        # graphs frame
        self.graph_frame = tk.Frame(self.mid_glob_frame, highlightbackground="black", highlightthickness=2)
        self.graph_frame.grid(row=0, column=0, rowspan=2, columnspan=5, padx=15, pady=5, sticky="nsew")

        # terminal frame
        self.term_frame = tk.Frame(self.lw_glob_frame, highlightbackground="black", highlightthickness=2)
        self.term_frame.grid(row=0, column=0, rowspan=2, columnspan=2, padx=15, pady=5, sticky="nsew")

        # logo frame
        self.logo_frame = tk.Frame(self.lw_glob_frame, highlightbackground="black", highlightthickness=2)
        self.logo_frame.grid(row=0, column=2, columnspan=2, padx=15, pady=5)
        self.logo_frame.configure(width=300, height=150)

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
        self.start_button = tk.Button(self.acq_frame, text="    Démarrer    ", command=self.click_start, font=font)
        self.start_button.grid(row=0, column=0, rowspan=2, columnspan=2, padx=10, pady=10, sticky="nsew")

        # wavelength label
        self.wavelength_label = tk.Label(self.acq_frame, text="Mode du puissance-mètre [nm]:", font=font)
        self.wavelength_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # wavelength selection drop-down
        self.selected_wavelength = tk.StringVar()
        wavelength_options = ["déterminer la longueur d'onde"] + sorted(self.current_values)
        self.wavelength_menu = ttk.Combobox(self.acq_frame, textvariable=self.selected_wavelength, values=wavelength_options,
                                            width=30, font=font)
        self.wavelength_menu.grid(row=0, column=3, columnspan=2, padx=10, pady=10, sticky="w")

        # test duration label
        self.test_duration_label = tk.Label(self.acq_frame, text="Durée d'acquisition [sec]:", font=font)

        # test duration entry
        self.test_duration_entry = tk.Entry(self.acq_frame, font=font)
        self.test_duration_entry.bind("<Return>", self.display_saving_time)

        # Bouton toggle d'enregistrement
        self.toggle_button = ToggleButton(
            self.acq_frame,
            text_on="Enregistrement activé",
            text_off="Enregistrement désactivé",
            height=40,
            padding=20,
            off_color="#D3D3D3",
            on_color="#4CD964",
            text_color="black",
            font=("Trebuchet MS", 12, "bold"),
            command=self.toggle_recording
        )
        self.toggle_button.grid(row=1, column=2, columnspan=2, padx=20, pady=10, stick="nsw")

        # Bind events for selection or manual entry
        self.wavelength_menu.bind("<<ComboboxSelected>>", self.on_wavelength_selected)
        self.wavelength_menu.bind("<Return>", self.on_wavelength_entered)
        self.wavelength_menu.bind("<FocusOut>", self.on_wavelength_entered)

        """ meas_frame """

        # position measurement display
        self.pos_label = tk.Label(self.meas_frame, text="Position du faisceau:", font=font_pw)
        self.pos_label.grid(row=0, column=1, padx=15, pady=10, sticky="e")
        self.pos_measurement_label = tk.Label(self.meas_frame, text="----", font=font_pw)
        self.pos_measurement_label.grid(row=1, column=1, padx=0, pady=10)

        # power measurement display
        self.power_label = tk.Label(self.meas_frame, text="Puissance mesurée [W]:", font=font_pw)
        self.power_label.grid(row=0, column=3, padx=15, pady=10, sticky="e")
        self.pw_measurement_label = tk.Label(self.meas_frame, text="----", font=font_pw)
        self.pw_measurement_label.grid(row=0, column=4, padx=0, pady=10, sticky="e")

        # wavelength measurement display
        self.wv_label = tk.Label(self.meas_frame, text="Longueur d'onde mesurée [nm]:", font=font_pw)
        self.wv_label.grid(row=1, column=3, padx=15, pady=10, sticky="e")
        self.wv_measurement_label = tk.Label(self.meas_frame, text="----", font=font_pw)
        self.wv_measurement_label.grid(row=1, column=4, padx=0, pady=10, sticky="e")

        """ graph_frame """

        # power graph
        self.fig_1, self.ax_1 = plt.subplots(figsize=(10, 5))
        self.canvas_1 = FigureCanvasTkAgg(self.fig_1, master=self.graph_frame)
        self.ax_1.set_xlabel("Temps [s]")
        self.ax_1.set_ylabel("Puissance [mW]")
        self.ax_1.set_ylim(-1, 12)
        self.ax_1.grid(True)

        # position graph
        self.fig_2, self.ax_2 = plt.subplots(figsize=(5, 5))
        self.canvas_2 = FigureCanvasTkAgg(self.fig_2, master=self.graph_frame)

        self.ax_2.set_title("Position du faisceau")
        self.ax_2.set_xlabel("Position [mm]")
        self.ax_2.set_ylabel("Position [mm]")

        circle = Circle((0, 0), 25, color='black', fill=False)
        self.ax_2.add_patch(circle)
        self.ax_2.set_xlim(-28, 28)
        self.ax_2.set_ylim(-28, 28)
        self.ax_2.set_aspect("equal")
        self.ax_2.grid(True)
        
        # place graphs
        self.canvas_1.get_tk_widget().grid(row=0, column=0, columnspan=4, padx=15, pady=10, sticky="nsew")
        self.canvas_2.get_tk_widget().grid(row=0, column=4, columnspan=2, padx=15, pady=10, sticky="nsew")

        # clear button 1
        self.clear_button_1 = tk.Button(self.graph_frame, text="Effacer le graphique de puissance",
                                        command=self.click_clear_1,
                                        font=font)
        self.clear_button_1.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky="ew")

        # save button 1
        self.save_button_1 = tk.Button(self.graph_frame, text="Enregistrer les données de puissance",
                                       command=self.save_data, font=font)
        self.save_button_1.grid(row=1, column=1, columnspan=1, padx=10, pady=10, sticky="ew")

        # clear button 2
        self.clear_button_2 = tk.Button(self.graph_frame, text="Effacer le graphique de position",
                                        command=self.click_clear_2,
                                        font=font)
        self.clear_button_2.grid(row=1, column=4, padx=10, pady=10, sticky="w")

        """ term_frame """

        # terminal
        self.log_text = tk.Text(self.term_frame, height=8, width=120, wrap="word", font=font)
        self.log_text.grid(column=0, row=0, sticky="nsew")
        self.log_text.insert(tk.END, " Journaux d'application initialisés...\n")
        self.log_text.bind("<Key>", lambda e: "break")
        self.log_text.bind("<Button-1>", lambda e: "break")

        # terminal scrollbar
        scrollbar = ttk.Scrollbar(self.term_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(column=1, row=0, sticky="nsew")
        self.log_text["yscrollcommand"] = scrollbar.set

        # print logs to terminal
        sys.stdout = TextRedirector(self.log_text)

        """ logo_frame """

        # RVLABS logo
        self.logo = tk.Label(self.logo_frame, image=self.logo_img, cursor="hand2")
        self.logo.grid(row=0, column=0, sticky="ne")
        self.logo.bind("<Button-1>", self.secret_sauce)

        """ other initializations """

        # set flags
        self.cam_is_connected = False
        self.cam_is_refreshing = False
        self.recording_enabled = False
        self.total_saving_duration_entered = False

        # initialize the powermeter object
        self.pm = None

        # necessary initializations
        self.plot_y_1 = getattr(self, 'plot_y', [])
        self.plot_x_1 = getattr(self, 'plot_x', [])

        self.plot_y_2 = getattr(self, 'plot_y', [])
        self.plot_x_2 = getattr(self, 'plot_x', [])

    def update_pm_data(self):
        """
        update data from the powermeter
        """
        try:
            self.pm.update_temperature()
        except Exception as e:
            print(f" An error occurred: {e}")
        
        if self.cam_is_refreshing:
            self.root.after(500, self.update_pm_data())

    def toggle_recording(self, state):
        """
        Gère l'activation/désactivation de l'enregistrement
        """
        self.recording_enabled = state

        # recording enabled
        if state:
            try:
                # get saving path
                self.recording_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt")],
                    title="Choisir un fichier pour l'enregistrement automatique")

                if not self.recording_path:
                    self.toggle_button.set_state(False)
                    self.recording_enabled = False
                    print(" Enregistrement annulé - Aucun chemin spécifié.")
                    return
                else:
                    print(f" Enregistrement activé:\n --> Les données seront sauvegardées à {self.recording_path}")
                    
                    # create the test duration label and entry
                    self.test_duration_label.grid(row=1, column=4, padx=10, pady=5, sticky="e")
                    self.test_duration_entry.grid(row=1, column=5, padx=10, pady=5, sticky="we")

                    # configure start button accordingly
                    self.start_button.config(text="     Démarrer l'enregistrement      ")
            except Exception as e:
                print(f" Erreur lors de la sélection du chemin d'enregistrement: {e}")
        else:
            self.start_button.config(text="     Démarrer      ")
            print(" Enregistrement désactivé")
            self.total_saving_duration = None
            self.total_saving_duration_entered = False
            self.cam_is_refreshing = False
            self.test_duration_label.grid_forget()
            self.test_duration_entry.grid_forget()
            if hasattr(self, 'recording_path'):
                delattr(self, 'recording_path')

    def disable_buttons(self):
        """
        disable all buttons in the UI
        """
        self.clear_button_1.config(state="disabled")
        self.clear_button_2.config(state="disabled")
        self.save_button_1.config(state="disabled")
        self.wavelength_menu.config(state="disabled")
        self.toggle_button.disable()
        self.test_duration_entry.config(state="disabled")

    def enable_buttons(self):
        """
        enable all buttons in the UI
        """
        self.clear_button_1.config(state="normal")
        self.clear_button_2.config(state="normal")
        self.save_button_1.config(state="normal")
        self.wavelength_menu.config(state="normal")
        self.toggle_button.enable()
        self.test_duration_entry.config(state="normal")

    def display_saving_time(self, event=None):
        """
        dummy function to test the saving functionality
        """
        if not self.total_saving_duration_entered and self.recording_enabled:
            try:
                self.click_clear_1(logs=False)
                self.total_saving_duration = float(self.test_duration_entry.get())

                if self.total_saving_duration <= 0:
                    raise ValueError()

                # set the power graph x-axis to the saving duration
                self.ax_1.set_xlim(0, self.total_saving_duration)
                self.canvas_1.draw()

                # print logs
                print(f" Le puissance-mètre est en mode < Acquisition de données >\n >> La durée d'enregistrement est de {self.total_saving_duration} secondes.")
                self.total_saving_duration_entered = True
            except Exception:
                print(f" Erreur lors de la définition de la durée d'enregistrement: la durée doit être un entier positif >:\\")
                self.total_saving_duration = None
                self.total_saving_duration_entered = False

        # the total duration has already been entered but a new one is set
        elif self.total_saving_duration_entered and self.recording_enabled and not self.cam_is_refreshing:
            try:
                self.click_clear_1(logs=False)
                self.total_saving_duration = float(self.test_duration_entry.get())

                if self.total_saving_duration <= 0:
                    raise ValueError()

                # set the power graph x-axis to the saving duration
                self.ax_1.set_xlim(0, self.total_saving_duration)
                self.canvas_1.draw()

                # print logs
                print(f" >> La nouvelle durée d'enregistrement est de {self.total_saving_duration} secondes.")
                self.total_saving_duration_entered = True
            except Exception:
                print(f" Erreur lors de la définition de la durée d'enregistrement: la durée doit être un entier positif >:\\")
                self.total_saving_duration = None
                self.total_saving_duration_entered = True
        else:
            pass

    def save_data(self, save_path=None):
        """
        save the power graph data
        """
        if self.wavelengths_1 is None or self.power_values_1 is None:
            print(" Aucune donnée à enregistrer !")
            return

        # recording disabled
        if save_path is None:
            try:
                save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                         filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt")],
                                                         title="Choisir un fichier pour l'enregistrement automatique"
                                                         )
            except Exception as e:
                print(" Erreur durant la sauvegarde: {e}")
        try:
            with open(save_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Time [s]", "Power [mW]"])
                for time, pw in zip(self.wavelengths_1, self.power_values_1):
                    writer.writerow([time, pw])
            print(f" Données enregistrées à {save_path}")
        except Exception as e:
            print(f" Erreur durant la sauvegarde: {e}")

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

    def display_position(self, position_tuple):
        """
        draws the coordinate on the position graph
        """
        self.click_clear_2()
        if position_tuple is None:
            return
        if isinstance(position_tuple[0], np.floating):
            position_tuple = float(position_tuple[0]), float(position_tuple[1])

        x_pos, y_pos = position_tuple[0], position_tuple[1]

        # plot the position dot and circle
        self.ax_2.scatter(x_pos, y_pos, s=5, color="black")
        pos_circle = Circle((x_pos, y_pos), 0.75, color='black', fill=False)
        self.ax_2.add_patch(pos_circle)

        # place grid in the background
        self.ax_2.grid(True)
        self.ax_2.set_axisbelow(True)
        self.canvas_2.draw()

    def click_clear_1(self, logs=True):
        """
        clears the plot
        """
        self.power_values_1 = None
        self.wavelengths_1 = None
        self.plot_x_1 = []
        self.plot_y_1 = []
        self.ax_1.clear()

        if self.total_saving_duration is not None:
            self.ax_1.set_xlim(0, self.total_saving_duration)

        self.ax_1.set_xlabel('Time')
        self.ax_1.set_ylabel('Power (mW)')
        self.ax_1.grid(True)
        self.canvas_1.draw()

    def click_clear_2(self):
        """
        clears the plot
        """
        self.plot_x_2 = []
        self.plot_y_2 = []
        self.ax_2.clear()

        self.ax_2.set_title("Position du faisceau")
        self.ax_2.set_xlabel("Position [mm]")
        self.ax_2.set_ylabel("Position [mm]")

        # graph the sensor's area
        circle = Circle((0, 0), 25, color='black', fill=False)
        self.ax_2.add_patch(circle)
        self.ax_2.set_xlim(-28, 28)
        self.ax_2.set_ylim(-28, 28)
        self.ax_2.set_aspect("equal")

        # place grid in the background
        self.ax_2.grid(True)
        self.ax_2.set_axisbelow(True)

        self.canvas_2.draw()

    def on_closing(self):
        print(" Fermeture de l'application...")        
        try:
            self.is_refreshing = False
            self.cam_is_refreshing = False
            if self.pm is not None:
                self.pm.cleanup()
            self.app.quit()
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f" Erreur lors de la fermeture de l'application: {e}")
        finally:
            sys.exit(0)

    def secret_sauce(self, event):
        """
        secret sauce
        """
        webbrowser.open("https://www.youtube.com/watch?v=xvFZjo5PgG0")
        image_path = r"main\secret_sauce.jpg"
        try:
            os.startfile(image_path)
        except Exception as e:
            return


if __name__ == "__main__":
    root = tk.Tk()
    app = PowerMeterApp(root)
    root.mainloop()
