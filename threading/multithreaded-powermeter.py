import tkinter as tk
import threading
import queue
import time
import numpy as np
from powermeter_test import PowerMeter_test
from Powermeter_UI import PowerMeterApp

class PowerMeterThread(threading.Thread):
    """
    Worker thread that handles PowerMeter operations
    """
    def __init__(self, command_queue, result_queue):
        threading.Thread.__init__(self, daemon=True)
        self.command_queue = command_queue  # Queue for receiving commands from UI
        self.result_queue = result_queue    # Queue for sending results back to UI
        self.running = False
        self.pm = None

    def run(self):
        """Main thread execution loop"""
        self.running = True

        # Initialize PowerMeter instance
        try:
            self.pm = PowerMeter_test()
            print(self.pm)
            self.result_queue.put(("init_status", True))
        except Exception as e:
            self.result_queue.put(("init_status", False, str(e)))

        # Main thread loop
        while self.running:
            try:
                # Check for commands with a timeout to allow thread to terminate
                try:
                    command, args = self.command_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # Process commands
                if command == "stop":
                    self.running = False
                    break

                elif command == "update_temperature":
                    try:
                        self.pm.update_temperature()
                        self.result_queue.put(("temperature_updated", True))
                    except Exception as e:
                        self.result_queue.put(("temperature_updated", False, str(e)))

                elif command == "get_temp":
                    try:
                        temp = self.pm.get_temp()
                        self.result_queue.put(("temp_data", temp))
                    except Exception as e:
                        self.result_queue.put(("temp_data", None, str(e)))

                elif command == "get_moy_temp":
                    try:
                        half = args.get("half", None) if args else None
                        temp = self.pm.get_moy_temp(half)
                        self.result_queue.put(("moy_temp_data", temp))
                    except Exception as e:
                        self.result_queue.put(("moy_temp_data", None, str(e)))

                elif command == "get_test_moy_temp":
                    try:
                        temp = self.pm.get_test_moy_temp()
                        self.result_queue.put(("test_moy_temp_data", temp))
                    except Exception as e:
                        self.result_queue.put(("test_moy_temp_data", None, str(e)))

                elif command == "get_position":
                    try:
                        print(" ligne 77")
                        result = self.pm.get_power_center()
                        print(f" result of self.pm.get_power_center(): {result}")
                        
                        # Check that we got a tuple with at least 2 elements
                        if isinstance(result, tuple) and len(result) >= 2:
                            P, pos = result

                            print(f"P: {P} | pos: {pos}")
                            
                            # Check that pos is not None and has the expected format
                            if pos is not None and len(pos) == 2:
                                
                                print(" in if for position")

                                x, y = pos[0], pos[1]

                                print(f" x: {x} | y: {y}")

                                self.result_queue.put(("position_data", (x, y)))
                            else:
                                self.result_queue.put(("position_data", None, "Invalid position format"))
                        else:
                            self.result_queue.put(("position_data", None, "Invalid return format from get_power_center()"))
                    except Exception as e:
                        self.result_queue.put(("position_data", None, str(e)))

                """
                elif command == "get_position":
                    try:
                        P, pos = self.pm.get_power_center()
                        x, y = pos[0], pos[1]
                        self.result_queue.put(("position_data", (float(x), float(y))))
                    except Exception as e:
                        self.result_queue.put(("position_data", None, str(e)))
                """

                # Mark command as processed
                self.command_queue.task_done()

            except Exception as e:
                self.result_queue.put(("error", str(e)))

    def cleanup(self):
        """Clean up resources used by the thread"""
        self.running = False
        if self.pm and hasattr(self.pm, 'cleanup'):
            self.pm.cleanup()


class ThreadedPowerMeterApp(PowerMeterApp):
    """Modified PowerMeterApp that uses a worker thread for PowerMeter operations"""

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

    def check_connection(self):
        """Start the worker thread instead of directly creating a PowerMeter instance"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            # Start the worker thread
            self.worker_thread = PowerMeterThread(self.command_queue, self.result_queue)
            self.worker_thread.start()

            # We'll set the connection status based on thread init response
            self.cam_is_connected = False  # Initially assume not connected
            print(f"\n Starting PowerMeter thread and checking connection...")
        else:
            print(f"\n PowerMeter thread is already running.")

    def update_pm_data(self):
        """Queue the update_temperature command instead of calling it directly"""
        if self.worker_thread and self.worker_thread.is_alive():
            self.command_queue.put(("update_temperature", None))

        if self.cam_is_refreshing:
            self.root.after(500, self.update_pm_data)

    def update_loop(self, test=False):
        """Modified update_loop that uses the worker thread"""
        if self.cam_is_refreshing:
            # Request data from worker thread
            if test:
                self.command_queue.put(("get_test_moy_temp", None))
            else:
                self.command_queue.put(("get_temp", None))
            
            # The actual update will happen when process_results handles the response
            
            # Schedule the next update
            if self.total_saving_duration is None or self.current_save_duration < self.total_saving_duration:
                if self.total_saving_duration is not None:
                    self.current_save_duration += self.power_time_inc / 1000
                self.root.after(self.power_time_inc, lambda: self.update_loop(test))
            else:
                # End of recording
                self.wavelengths_1 = self.plot_x_1
                self.power_values_1 = self.plot_y_1
                self.save_data(self.recording_path)
                
                print(" Fin de l'acquisition de données.")
                self.start_button.config(text="    Démarrer    ")
                
                # Enable buttons
                self.enable_buttons()
                
                self.cam_is_refreshing = False
                self.recording_enabled = False
                self.toggle_recording = False
                if hasattr(self, 'toggle_button') and self.toggle_button:
                    self.toggle_button.toggle()
                self.current_save_duration = 0
    
    def update_cam(self):
        """Modified update_cam that uses the worker thread"""
        if self.cam_is_refreshing:
            # Request position data from worker thread
            self.command_queue.put(("get_position", None))
            
            # Schedule the next update
            self.root.after(self.power_time_inc, self.update_cam)
    
    def process_results(self):
        """Process results from the worker thread"""
        try:
            # Process all available results
            while not self.result_queue.empty():
                result = self.result_queue.get_nowait()
                result_type = result[0]
                
                if result_type == "init_status":
                    success = result[1]
                    if success:
                        self.cam_is_connected = True
                        print(" PowerMeter initialized successfully.")
                    else:
                        self.cam_is_connected = False
                        print(f" Failed to initialize PowerMeter: {result[2]}")
                        
                elif result_type == "temperature_updated":
                    # Temperature was updated, nothing to do here
                    pass
                    
                elif result_type == "temp_data":
                    if len(result) > 2:  # Error occurred
                        print(f" Error getting temperature: {result[2]}")
                    else:
                        temp_data = result[1]
                        # Process temperature data for plotting
                        mean_temp = np.nanmax(temp_data)
                        self.update_power_graph(mean_temp)
                        
                elif result_type == "test_moy_temp_data":
                    if len(result) > 2:  # Error occurred
                        print(f" Error getting test temperature: {result[2]}")
                    else:
                        mean_temp = result[1]
                        self.update_power_graph(mean_temp)

                elif result_type == "position_data":

                    print(f" in process_results()")

                    print(f" result: {result}")
                    if len(result) > 2:    # Error occurred
                        print(" toto")
                        print(f" result: {result}")
                        print(f" Error getting position: {result[2]}")
                    else:
                        print(" tata")
                        position = result[1]
                        print(f" position: {position}")

                        self.position_tuple = position
                        self.display_position(position)
                        self.pos_measurement_label.config(text=f"[{position[0]:.2f}:{position[1]:.2f}]")
                
                elif result_type == "error":
                    print(f" Error in worker thread: {result[1]}")
                
                # Mark result as processed
                self.result_queue.task_done()
                
        except Exception as e:
            print(f" Error processing results: {e}")
        
        # Schedule next check
        self.root.after(50, self.process_results)
    
    def update_power_graph(self, mean_temp):
        """Update power graph with new temperature data"""
        last = len(self.plot_x_1) if hasattr(self, 'plot_x_1') else 0
        
        # Add new data point
        self.plot_x_1.append(last)
        self.plot_y_1.append(mean_temp)
        
        # Update plot
        self.ax_1.clear()
        if self.total_saving_duration is not None:
            self.ax_1.set_xlim(0, self.total_saving_duration)
        self.ax_1.plot(self.plot_x_1, self.plot_y_1)
        self.ax_1.set_xlabel('Temps [s]')
        self.ax_1.set_ylabel('Puissance (mW)')
        self.ax_1.grid(True)
        self.canvas_1.draw()
        
        # Update power measurement label
        self.pw_measurement_label.config(text=f"{mean_temp:.2f} mW")
    
    def on_closing(self):
        """Clean up threads before closing"""
        print(" Closing the application...")
        try:
            self.cam_is_refreshing = False
            
            # Stop the worker thread
            if self.worker_thread and self.worker_thread.is_alive():
                self.command_queue.put(("stop", None))
                self.worker_thread.join(timeout=1.0)  # Wait for the thread to finish
            
            if hasattr(self, 'app') and self.app:
                self.app.quit()
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f" Error closing the application: {e}")
        finally:
            import sys
            sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = ThreadedPowerMeterApp(root)
    root.mainloop()
