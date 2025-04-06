 def check_connection(self):
        """
        checks the camera's connection status
        """
        try:
            self.pm = PowerMeter_test()
            if self.pm.dev is not None:
                self.cam_is_connected = True
            else:
                self.cam_is_connected = False
        except Exception as e:
            print(f" Erreur lors de la connexion avec le capteur: {e}")
