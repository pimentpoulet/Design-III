import tkinter as tk

from multithreading_main import ThreadedPowerMeterApp


if __name__ == "__main__":
    root = tk.Tk()
    app = ThreadedPowerMeterApp(root)
    root.mainloop()
