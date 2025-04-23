import tkinter as tk
import threading
import queue
import numpy as np
import serial

from powermeter_main import PowerMeter
from UI_main import PowerMeterApp


class PowerMeterThread(threading.Thread):
    """
    Worker thread that handles PowerMeter operations
    """
    def __init__(self, command_queue, result_queue, pm):
        threading.Thread.__init__(self, daemon=True)
        self.command_queue = command_queue    # queue for receiving commands from UI
        self.result_queue = result_queue      # queue for sending results back to UI
        self.running = False
        self.pm = pm

    def run(self):
        """
        Main thread execution loop
        """
        self.running = True

        # initialize PowerMeter instance
        try:
            # self.pm = PowerMeter()
            self.result_queue.put(("init_status", True))
        except Exception as e:
            self.result_queue.put(("init_status", False, str(e)))

        # main thread loop
        while self.running:
            try:
                # check for commands with a timeout to allow thread to terminate
                try:
                    command, args = self.command_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # process commands
                if command == "stop":
                    self.running = False
                    break

                elif command == "update_temperature":
                    try:
                        self.pm.update_temperature()
                        self.result_queue.put(("temperature_updated", True))
                    except Exception as e:
                        self.result_queue.put(("temperature_updated", False, str(e)))

                elif command == "get_position":
                    try:
                        result = self.pm.get_power_center()
                        print(f" result: {result}")

                        # check that we got a tuple with at least 2 elements
                        if isinstance(result, tuple) and len(result) >= 2:
                            P, pos = result
                            # print(f" pos: {pos}")

                            # check that pos is not None and has the expected format
                            if pos is not None and len(pos) == 2:
                                x, y = pos[0], pos[1]
                                self.result_queue.put(("position_data", P, (x, y)))
                            else:
                                self.result_queue.put(("position_data", None, "Invalid position format"))
                        else:
                            self.result_queue.put(("position_data", None, "Invalid return format from get_power_center()"))
                    except Exception as e:
                        self.result_queue.put(("position_data", None, str(e)))

                # mark command as processed
                self.command_queue.task_done()

            except Exception as e:
                self.result_queue.put(("error", str(e)))

    def cleanup(self):
        """
        Clean up resources used by the thread
        """
        self.running = False
        if self.pm and hasattr(self.pm, 'cleanup'):
            self.pm.cleanup()


class ThreadedPowerMeterApp(PowerMeterApp):
    """
    Modified PowerMeterApp that uses a worker thread for PowerMeter operations
    """
    def __init__(self, root):
        
        # Initialize command and result queues
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # Call parent constructor
        super().__init__(root)

        # Initialize threading flag
        self.worker_thread = None

        # Start processing results from worker thread
        self.process_results()

    def check_connection(self, check=False):
        """
        Checks the camera's connection status and returns the result
        """
        # check connection status at 1Hz
        if check:
            try:
                if "COM3" in [port.device for port in serial.tools.list_ports.comports()]:
                    self.cam_is_connected = True
                else:
                    self.cam_is_connected = False
            except serial.SerialException as e:
                print(f" Erreur de connexion au capteur: {e}")
                self.cam_is_connected = False

        # check connection status at launch
        else:
            try:
                ports = [port.device for port in serial.tools.list_ports.comports()]

                # check if the camera is connected to COM3
                if "COM3" in ports:
                    try:
                        if self.pm is None:
                            # test an initialization of the powermeter class
                            self.pm = PowerMeter()

                        # check if the powermeter class's init worked
                        if self.pm.dev is not None:
                            self.cam_is_connected = True
                        else:
                            self.cam_is_connected = False
                    except serial.SerialException as e:
                        print(f" Erreur de connexion au capteur: {e}")
                        self.cam_is_connected = True
                else:
                    print(" Veuillez connecter / reconnecter le capteur !")
                    self.wavelengths_1 = self.plot_x_1
                    self.power_values_1 = self.plot_y_1
                    self.cam_is_refreshing = False

                    # enable buttons
                    self.enable_buttons()

                    # disable the recording flag if recording
                    if self.recording_enabled:
                        self.recording_enabled = False
                        self.total_saving_duration = None
                        self.total_saving_duration_entered = False
                        self.toggle_button.toggle()

                        # reset the current saving counter
                        self.current_save_duration = 0
                    self.start_button.config(text="    Démarrer    ")

                    # set connection flag
                    self.cam_is_connected = False
                    
                # update UI to reflect connection status
                if hasattr(self, 'status_label'):
                    status_text = "Connecté" if self.cam_is_connected else "Déconnecté"
                    status_color = "green" if self.cam_is_connected else "red"
                    self.status_label.config(text=f"État: {status_text}", fg=status_color)
                    
            except Exception as e:
                print(f" Erreur lors de la vérification de la connexion: {e}")
                self.cam_is_connected = False
                return False
        
    def click_start(self):
        """
        setups the start button, updates the flags and starts data acquisition
        """
        if self.start_button.cget("text") == "    Démarrer    " or self.start_button.cget("text") == "     Démarrer l'enregistrement      ":
            self.check_connection()

        # camera is connected
        if self.cam_is_connected:

            # process is started
            if not self.cam_is_refreshing:

                # set the stop button according to sensor use mode
                if self.recording_enabled:
                    if self.total_saving_duration is not None:
                        self.start_button.config(text="     Arrêter l'enregistrement      ")
                    else:
                        print(" Veuillez spécifier une durée d'enregistrement.")
                        return
                else:
                    self.start_button.config(text="     Arrêter      ")

                # disable buttons
                self.disable_buttons()

                # start an acquisition thread
                self.start_acquisition_thread()
                
                print(" Processus démarré !")
                self.cam_is_refreshing = True

                # update pm data
                self.update_pm_data()

                # call update functions in real use mode
                self.update_loop()
                self.update_cam()

            # process is stopped
            else:
                print(" Processus arrêté !")
                self.wavelengths_1 = self.plot_x_1
                self.power_values_1 = self.plot_y_1
                self.cam_is_refreshing = False

                # enable buttons
                self.enable_buttons()

                # kill the acquisition thread
                self.kill_acquisition_thread()

                # disable the recording flag if recording
                if self.recording_enabled:
                    self.recording_enabled = False
                    self.total_saving_duration = None
                    self.total_saving_duration_entered = False
                    self.toggle_button.toggle()

                    # reset the current saving counter
                    self.current_save_duration = 0
                self.start_button.config(text="    Démarrer    ")

                # set connection flag
                self.cam_is_connected = False

        # camera is disconnected
        else:
            pass

    def start_acquisition_thread(self):
        """
        Start an acquisition thread if one is not already running
        """
        if self.worker_thread is None or not self.worker_thread.is_alive():
            # Initialize command and result queues if they don't exist
            if not hasattr(self, 'command_queue'):
                self.command_queue = queue.Queue()
            if not hasattr(self, 'result_queue'):
                self.result_queue = queue.Queue()

            # Start the worker thread
            self.worker_thread = PowerMeterThread(self.command_queue, self.result_queue, self.pm)
            self.worker_thread.start()
            return True
        else:
            # print(f" Thread d'acquisition déjà en cours d'exécution.")
            return False

    def kill_acquisition_thread(self):
        """
        Safely terminates the acquisition thread if it's running
        """
        if self.worker_thread and self.worker_thread.is_alive():
            try:
                # send stop command to thread
                self.command_queue.put(("stop", None))

                # Wait for the thread to finish with timeout
                self.worker_thread.join(timeout=1.0)

                # if thread is still alive after timeout, try more aggressive cleanup
                if self.worker_thread.is_alive():
                    if hasattr(self.worker_thread, 'cleanup'):
                        self.worker_thread.cleanup()
                    print(f" Le thread ne répond pas, arrêt forcé.")
                else:
                    # print(f" Thread d'acquisition arrêté avec succès.")
                    pass

                self.worker_thread = None
                return True

            except Exception as e:
                print(f" Erreur lors de l'arrêt du thread: {e}")
                return False
        else:
            # print(f" Aucun thread d'acquisition en cours d'exécution.")
            self.worker_thread = None

    def update_pm_data(self):
        """
        Queue the update_temperature command instead of calling it directly
        """
        if self.worker_thread and self.worker_thread.is_alive():
            self.command_queue.put(("update_temperature", None))

        if self.cam_is_refreshing:
            self.root.after(31, self.update_pm_data)

    def update_loop(self):
        """
        Modified update_loop that uses the worker thread
        """
        # check connection status
        self.check_connection(check=True)

        if not self.cam_is_connected:
            
            # handle disconnection during acquisition
            print(" Capteur déconnecté durant l'acquisition. Veuillez reconnecter le capteur.")
            self.check_connection()

            if not self.cam_is_connected:

                # reconnection failed --> stop acquisition
                print(" Reconnexion échouée. Arrêt de l'acquisition.")
                self.click_start()
                return
            else:
                print(" Reconnexion réussie. Reprise de l'acquisition.")

        if self.cam_is_connected and self.cam_is_refreshing:
            # the actual update will happen when process_results handles the response

            # schedule the next update
            if self.total_saving_duration is None or self.current_save_duration < self.total_saving_duration:
                if self.total_saving_duration is not None:
                    self.current_save_duration += self.power_time_inc / 1000
                self.root.after(self.power_time_inc, lambda: self.update_loop())
            else:
                # end of recording
                self.wavelengths_1 = self.plot_x_1
                self.power_values_1 = self.plot_y_1
                self.save_data(self.recording_path)

                print(" Fin de l'acquisition de données.")
                self.start_button.config(text="    Démarrer    ")

                # enable buttons
                self.enable_buttons()

                self.cam_is_refreshing = False
                self.recording_enabled = False
                self.toggle_recording = False
                if hasattr(self, 'toggle_button') and self.toggle_button:
                    self.toggle_button.toggle()
                self.current_save_duration = 0

    def update_cam(self):
        """
        Modified update_cam that uses the worker thread
        """
        if self.cam_is_refreshing:
            if self.cam_is_connected:
    
                # request position data from worker thread
                self.command_queue.put(("get_position", None))
                
                # schedule the next update
                self.root.after(self.power_time_inc, self.update_cam)
    
    def process_results(self):
        """
        Process results from the worker thread
        """
        if self.cam_is_connected and self.cam_is_refreshing:
            try:
                # process all available results
                while not self.result_queue.empty():
                    result = self.result_queue.get_nowait()
                    result_type = result[0]
                    
                    if result_type == "init_status":
                        success = result[1]
                        if success:
                            self.cam_is_connected = True
                            # print(" Initialisation du capteur réussie.")
                        else:
                            self.cam_is_connected = False
                            # print(f" Initialisation du capteur impossible: {result[2]}")
                            
                    elif result_type == "temperature_updated":
                        # temperature was updated, nothing to do here
                        pass

                    elif result_type == "position_data":

                        if len(result) > 3:    # error occurred
                            print(f" Erreur lors du calcul de position: {result[2]}")
                        else:
                            _, P, position = result

                            self.position_tuple = position
                            self.display_position(position)
                            self.pos_measurement_label.config(text=f"[{position[0]:.2f}:{position[1]:.2f}]")

                            self.update_power_graph(P)
                    # mark result as processed
                    self.result_queue.task_done()
                    
            except Exception as e:
                pass

        # schedule next check
        self.root.after(50, self.process_results)
    
    def update_power_graph(self, power):
        """
        Update power graph with new temperature data
        """
        last = len(self.plot_x_1) if hasattr(self, 'plot_x_1') else 0
        
        # add new data point
        self.plot_x_1.append(last)
        self.plot_y_1.append(power)
        
        # update plot
        self.ax_1.clear()
        if self.total_saving_duration is not None:
            self.ax_1.set_xlim(0, self.total_saving_duration)
        self.ax_1.plot(self.plot_x_1, self.plot_y_1)
        self.ax_1.set_xlabel('Temps [s]')
        self.ax_1.set_ylabel('Puissance (mW)')
        self.ax_1.grid(True)
        self.canvas_1.draw()
        
        # update power measurement label
        self.pw_measurement_label.config(text=f"{power:.2f} mW")
    
    def on_closing(self):
        """
        Clean up threads before closing
        """
        print(" Fermeture de l'application...")
        try:
            self.cam_is_refreshing = False
            
            # stop the worker thread
            if self.worker_thread and self.worker_thread.is_alive():
                self.command_queue.put(("stop", None))
                self.worker_thread.join(timeout=1.0)    # wait for the thread to finish
            
            if hasattr(self, 'app') and self.app:
                self.app.quit()
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f" Erreur lors de la fermeture de l'application: {e}")
        finally:
            import sys
            sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = ThreadedPowerMeterApp(root)
    root.mainloop()
