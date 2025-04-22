import tkinter as tk

from ToggleButton import ToggleButton
from tkinter import ttk


def toggle_recording(state):
    """
    Gère l'activation/désactivation de l'enregistrement
    """
    if state:
        print(state)
        bouton_conditionnel.grid(row=1, column=0, pady=10, padx=10)
    else:
        print(state)
        bouton_conditionnel.grid_forget()

fenetre = tk.Tk()
fenetre.title("Bouton conditionnel")
fenetre.geometry("300x200")

toggle_button = ToggleButton(
            fenetre,
            text_on="Enregistrement activé",
            text_off="Enregistrement désactivé",
            height=40,
            padding=20,
            off_color="#D3D3D3",
            on_color="#4CD964",
            text_color="black",
            font=("Trebuchet MS", 12, "bold"),
            command=toggle_recording,
        )
toggle_button.grid(row=1, column=2, columnspan=2, padx=20, pady=10, stick="nsw")

bouton_conditionnel = ttk.Button(fenetre, text="Bouton spécial", command=lambda: print("Bouton spécial cliqué !"))

fenetre.mainloop()
