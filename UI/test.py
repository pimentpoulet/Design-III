import tkinter as tk

class ToggleButton(tk.Canvas):
    def __init__(self, parent,
                 text_on="Enregistrement activé", text_off="Enregistrement désactivée",
                 height=40, padding=20,
                 on_color="#34C759", off_color="#E5E5EA",
                 slider_color="#f1f1f1", font=("Helvetica", 14, "bold"), **kwargs):

        # Temporary widget to measure text
        test = tk.Label(parent, text=text_on, font=font)
        test.update_idletasks()
        text_on_width = test.winfo_reqwidth()

        test.config(text=text_off)
        test.update_idletasks()
        text_off_width = test.winfo_reqwidth()
        test.destroy()

        max_text_width = max(text_on_width, text_off_width)

        self.width = max_text_width * 1.25 + padding * 2
        self.height = height
        self.radius = height // 2
        self.slider_diameter = height - 4

        super().__init__(parent, width=self.width, height=self.height, bg="#dfe3e8", highlightthickness=0, bd=0, **kwargs)

        self.text_on = text_on
        self.text_off = text_off
        self.font = font
        self.padding = padding
        self.is_on = False

        self.on_color = on_color
        self.off_color = off_color
        self.slider_color = slider_color

        # Track parts
        self.bg_left = self.create_oval(0, 0, height, height, fill=self.off_color, outline="black", width=3)
        self.bg_right = self.create_oval(self.width - height, 0, self.width, height, fill=self.off_color, outline="black", width=3)
        self.bg_center = self.create_rectangle(self.radius, 0, self.width - self.radius, height, fill=self.off_color, outline="black", width=4)
        self.bg_center_ = self.create_rectangle(self.radius, 4, self.width - self.radius, height-4, fill=self.off_color, outline=off_color, width=4)
        
        # Create the main text (normal font and color)
        self.text_label = self.create_text(self.width // 2, self.height // 2, text=self.text_off,
                                        fill="black", font=("Helvetica", 14, "bold"))

        # Slider knob
        self.slider = self.create_oval(2, 2, 2 + self.slider_diameter, 2 + self.slider_diameter,
                                       fill=self.slider_color, outline="#ccc", width=2)

        self.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        if self.is_on:
            self.animate(self.width - self.slider_diameter - 2, 2)
            self.set_colors(self.off_color)
            self.itemconfig(self.text_label, text=self.text_off)
        else:
            self.animate(2, self.width - self.slider_diameter - 2)
            self.set_colors(self.on_color)
            self.itemconfig(self.text_label, text=self.text_on)

        self.is_on = not self.is_on

    def animate(self, start, end):
        steps = 10
        dx = (end - start) / steps
        for _ in range(steps):
            self.move(self.slider, dx, 0)
            self.update()
            self.after(10)

    def set_colors(self, color):
        self.itemconfig(self.bg_left, fill=color, outline="black", width=3)
        self.itemconfig(self.bg_right, fill=color, outline="black", width=3)
        self.itemconfig(self.bg_center, fill=color, outline="black", width=4)
        self.itemconfig(self.bg_center_, fill=color, outline=color, width=4)

    def get_state(self):
        return self.is_on

# Example usage
root = tk.Tk()
root.title("Auto-Resizing iOS Toggle")
root.configure(bg="#dfe3e8")

toggle = ToggleButton(root,
                      text_on="Enregistrement activé",
                      text_off="Enregistrement désactivée",
                      font=("Helvetica", 14, "bold"))
toggle.pack(pady=30)

def show_state():
    print("save_is_on" if toggle.get_state() else "save_is_off")

tk.Button(root, text="Check State", command=show_state).pack()

root.mainloop()
