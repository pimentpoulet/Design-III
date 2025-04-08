import tkinter as tk
import math

class ToggleButton(tk.Canvas):
    def __init__(self, parent, text_on="Enregistrement activé", text_off="Enregistrement désactivé",
                 height=50, padding=20, bg_color="#D3D3D3", toggle_color="#FFFFFF", 
                 text_color="#FFFFFF", on_color="#34C759", off_color="#D3D3D3", 
                 command=None, initial_state=False, font=("Arial", 12, "bold"), **kwargs):
        
        # Calculate required width based on text length
        temp_label = tk.Label(parent, text=text_on, font=font)
        temp_label.update_idletasks()
        text_on_width = temp_label.winfo_reqwidth()
        
        temp_label.config(text=text_off)
        temp_label.update_idletasks()
        text_off_width = temp_label.winfo_reqwidth()
        temp_label.destroy()
        # self.rec_frame = tk.Frame(self.up_glob_frame, highlightbackground="black", highlightthickness=2)
        # self.rec_frame.grid(row=1, column=0, columnspan=4, padx=25, pady=10, sticky="nsew")
        
        # Set width to accommodate the longer text plus padding
        max_text_width = max(text_on_width, text_off_width)
        width = max_text_width + height + padding * 2  # Add enough space for text + knob + padding
        
        super().__init__(parent, width=width, height=height, bg=parent["bg"], 
                         highlightthickness=0, bd=0, **kwargs)
        
        self.width = width
        self.height = height
        self.padding = padding
        self.bg_color = bg_color
        self.toggle_color = toggle_color
        self.text_color = text_color
        self.on_color = on_color
        self.off_color = off_color
        self.command = command
        self.is_on = initial_state
        self.text_on = text_on
        self.text_off = text_off
        self.font = font
        
        # Draw initial button state
        self.draw()
        
        # Bind click event
        self.bind("<Button-1>", self.toggle)
        
    def draw(self):
        self.delete("all")
        
        # Track/background
        radius = self.height // 2
        track_color = self.on_color if self.is_on else self.off_color
        
        # Create background rounded rectangle
        self.create_rounded_rect(0, 0, self.width, self.height, radius, fill=track_color, outline="#8E8E93", width=2)
        
        # Knob position
        if self.is_on:
            knob_x = self.width - radius - 4
        else:
            knob_x = radius + 4
            
        # Draw knob
        self.create_oval(knob_x - radius + 4, 4, 
                         knob_x + radius - 4, self.height - 4, 
                         fill=self.toggle_color, outline="#8E8E93", width=1)
        
        # Calculate text position
        if self.is_on:
            # When ON, position text to the left of the knob
            text_x = (self.width - radius - 4) / 2
            text = self.text_on
        else:
            # When OFF, position text to the right of the knob
            text_x = radius + 4 + (self.width - radius - 4) / 2
            text = self.text_off
            
        # Create text with current state
        self.create_text(text_x, self.height // 2, text=text, 
                         fill=self.text_color, font=self.font,
                         anchor="center")
    
    def toggle(self, event=None):
        self.is_on = not self.is_on
        self.animate_toggle()
        if self.command is not None:
            self.command(self.is_on)
    
    def animate_toggle(self):
        steps = 10
        radius = self.height // 2
        
        if self.is_on:
            start_x = radius + 4
            end_x = self.width - radius - 4
            start_color = self.off_color
            end_color = self.on_color
            start_text = self.text_off
            end_text = self.text_on
        else:
            start_x = self.width - radius - 4
            end_x = radius + 4
            start_color = self.on_color
            end_color = self.off_color
            start_text = self.text_on
            end_text = self.text_off
        
        dx = (end_x - start_x) / steps
        
        for step in range(steps + 1):
            t = step / steps
            
            # Linear interpolation for position
            knob_x = start_x + dx * step
            
            # Color interpolation
            r1, g1, b1 = self.hex_to_rgb(start_color)
            r2, g2, b2 = self.hex_to_rgb(end_color)
            
            r = r1 + (r2 - r1) * t
            g = g1 + (g2 - g1) * t
            b = b1 + (b2 - b1) * t
            
            current_color = self.rgb_to_hex(r, g, b)
            
            # Clear and redraw
            self.delete("all")
            
            # Background
            self.create_rounded_rect(0, 0, self.width, self.height, radius, fill=current_color, outline="#8E8E93", width=2)
            
            # Knob
            self.create_oval(knob_x - radius + 4, 4, 
                            knob_x + radius - 4, self.height - 4, 
                            fill=self.toggle_color, outline="#8E8E93", width=1)
            
            # Text - fade between texts
            if self.is_on:
                # When switching to ON, text moves from right to left
                text_x = (self.width - radius - 4) / 2
                text = start_text if step < steps/2 else end_text
            else:
                # When switching to OFF, text moves from left to right
                text_x = radius + 4 + (self.width - radius - 4) / 2
                text = start_text if step < steps/2 else end_text
                
            self.create_text(text_x, self.height // 2, text=text, 
                            fill=self.text_color, font=self.font,
                            anchor="center")
            
            self.update()
            self.after(10)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        # Create a rounded rectangle
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def hex_to_rgb(self, hex_color):
        # Convert hex color to RGB
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, r, g, b):
        # Convert RGB to hex
        return f'#{int(r):02x}{int(g):02x}{int(b):02x}'
    
    def get_state(self):
        return self.is_on
    
    def set_state(self, state):
        if state != self.is_on:
            self.is_on = state
            self.draw()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Auto-Scaling Toggle Button")
    root.configure(bg="#F0F0F0")
    root.geometry("600x200")
    
    def on_toggle(state):
        print(f"Toggle state: {'Enregistrement activé' if state else 'Enregistrement désactivé'}")
    
    # Create the toggle button
    toggle = ToggleButton(
        root, 
        text_on="Enregistrement activé",
        text_off="Enregistrement désactivé",
        height=50,
        padding=20,
        off_color="#D3D3D3",  # Light gray for OFF state
        on_color="#4CD964",   # iOS green for ON state
        text_color="black",   # Black text for better visibility
        font=("Arial", 12, "bold"),
        command=on_toggle
    )
    toggle.pack(pady=50)
    
    root.mainloop()
