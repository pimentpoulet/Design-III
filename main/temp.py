
def check_connection(self):
        """
        checks the camera's connection status
        """
        ports = [port.device for port in serial.tools.list_ports.comports()]
        
        # check if the camera is connected to COM3
        if "COM3" in ports:
            try:
                with serial.Serial("COM3", baudrate=9600, timeout=1) as _:
                    pass
                
                if self.pm is None:
                    # test an initialization of the powermeter class
                    self.pm = PowerMeter()

                # check if the powermeter class's init worked
                if self.pm.dev is not None:
                    self.cam_is_connected = True
                else:
                    self.cam_is_connected = False
            except serial.SerialException as e:
                self.cam_is_connected = True
            
            print(self.cam_is_connected)

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
            print(" check is False")
            try:
                ports = [port.device for port in serial.tools.list_ports.comports()]

                # check if the camera is connected to COM3
                if "COM3" in ports:
                    try:
                        with serial.Serial("COM3", baudrate=9600, timeout=1) as _:
                            pass

                        print(self.pm)
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
                        self.cam_is_connected = False
                else:
                    self.cam_is_connected = True
                    
                # update UI to reflect connection status
                if hasattr(self, 'status_label'):
                    status_text = "Connecté" if self.cam_is_connected else "Déconnecté"
                    status_color = "green" if self.cam_is_connected else "red"
                    self.status_label.config(text=f"État: {status_text}", fg=status_color)
                    
                # return self.cam_is_connected
                    
            except Exception as e:
                print(f" Erreur lors de la vérification de la connexion: {e}")
                self.cam_is_connected = False
                return False
