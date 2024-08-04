import tkinter as tk
import time
import random
from pygame import mixer
from threading import Thread
import os

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.hover_start_time = None

        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        self.hover_start_time = time.time()
        self.widget.after(100, self.check_hover)

    def on_leave(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        self.hover_start_time = None

    def check_hover(self):
        if self.hover_start_time and time.time() - self.hover_start_time > 5:
            self.show_tooltip()
        else:
            self.widget.after(100, self.check_hover)

    def show_tooltip(self):
        if self.tooltip:
            return
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overridden(True)
        self.tooltip.wm_geometry(f"+{self.widget.winfo_rootx() + 20}+{self.widget.winfo_rooty() + 20}")
        label = tk.Label(self.tooltip, text=self.text, background="light yellow", relief="solid", borderwidth=1, padx=5, pady=5)
        label.pack()
        self.tooltip.after(3000, self.tooltip.destroy)

class Pet(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pet Animation with Tooltips")
        self.geometry('128x128')
        self.configure(bg='black')
        self.wm_attributes('-transparentcolor', 'black')
        self.attributes('-topmost', True)
        self.overrideredirect(True)

        # Load GIF frames
        self.frame_index = 0
        self.moveleft = [tk.PhotoImage(file='media/---duck.gif', format='gif -index %i' % (i)) for i in range(10)]
        self.moveright = [tk.PhotoImage(file='media/duck---.gif', format='gif -index %i' % (i)) for i in range(10)]
        self.img = self.moveleft[self.frame_index]

        # Create label to display GIF
        self.label = tk.Label(self, bd=0, bg='black', image=self.img)
        self.label.pack()

        # Initial positions and settings
        self.x = random.randint(0, self.winfo_screenwidth() - 128)
        self.y = random.randint(0, self.winfo_screenheight() - 128)
        self.dir = random.choice([-1, 1])
        self.jump_height = 0
        self.gravity = 0.5
        self.timestamp = time.time()
        self.last_update_time = self.timestamp
        self.speed = random.uniform(5, 15)
        self.mouse_hover = False
        self.is_dragging = False

        # Bind events
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.drag)
        self.label.bind('<ButtonRelease-1>', self.stop_drag)
        self.label.bind('<Enter>', self.on_hover)
        self.label.bind('<Leave>', self.off_hover)

        # FPS display
        self.fps_display = tk.Label(self, bg='black', fg='white', font=("Arial", 10))
        self.fps_display.pack()

        # Play background music
        if os.path.exists('background-music.mp3'):
            self.music_thread = Thread(target=self.play_music, daemon=True)
            self.music_thread.start()
        else:
            print("Background music file not found.")

        # Create additional widgets
        self.create_widgets()

        # Initialize update loop
        self.after(0, self.update)
        self.mainloop()

    def create_widgets(self):
        # Color-changing label
        self.color_label = tk.Label(self, text="Click me to change color!", bg='white', fg='black', width=30, height=2)
        self.color_label.pack(padx=10, pady=10)
        self.color_label.bind('<Button-1>', self.change_color)

        # Slider for animation speed
        self.slider_label = tk.Label(self, text="Animation Speed")
        self.slider_label.pack(padx=10, pady=5)
        self.animation_speed = tk.Scale(self, from_=1, to=100, orient='horizontal')
        self.animation_speed.set(10)
        self.animation_speed.pack(padx=10, pady=5)

        # Progress bar
        self.progress_bar = tk.Scale(self, from_=0, to=100, orient='horizontal', length=300)
        self.progress_bar.pack(padx=10, pady=10)
        self.update_progress_bar()

        # Popup window button
        self.popup_button = tk.Button(self, text="Show Popup", command=self.show_popup)
        self.popup_button.pack(padx=10, pady=10)

        # Tooltips for additional widgets
        Tooltip(self.color_label, "Click to change the color.")
        Tooltip(self.slider_label, "Adjust animation speed.")
        Tooltip(self.progress_bar, "Displays progress.")
        Tooltip(self.popup_button, "Click to show a popup window.")

    def change_color(self, event):
        color = f"#{random.randint(0, 0xFFFFFF):06x}"
        self.color_label.configure(bg=color)

    def update_progress_bar(self):
        value = (self.progress_bar.get() + 1) % 101
        self.progress_bar.set(value)
        self.after(100, self.update_progress_bar)

    def show_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Popup Window")
        tk.Label(popup, text="This is a popup window!").pack(padx=10, pady=10)
        tk.Button(popup, text="Close", command=popup.destroy).pack(padx=10, pady=10)

    def play_music(self):
        mixer.init()
        mixer.music.load('background-music.mp3')
        mixer.music.play(-1)

    def update_fps_display(self):
        now = time.time()
        elapsed = now - self.last_update_time
        if elapsed > 0:
            fps = round(1 / elapsed, 2)
            self.fps_display.config(text=f"FPS: {fps}", fg='green')
        self.last_update_time = now

    def update(self):
        # Update speed and position based on hover status
        if self.mouse_hover:
            self.speed = 30
        else:
            self.speed = max(self.speed / 1.05, 5)  # Normalize speed when not hovered

        # Randomize the direction and jump if needed
        if random.random() < 0.01:
            self.dir = -self.dir
        if random.random() < 0.01:
            self.jump_height = -10  # Start a jump

        # Update position and jump physics
        self.x += self.dir * self.speed
        self.jump_height += self.gravity
        self.y += self.jump_height

        # Bounce off the edges and screen boundaries
        if self.x < 0 or self.x > self.winfo_screenwidth() - 128:
            self.dir = -self.dir
        if self.y > self.winfo_screenheight() - 128:
            self.y = self.winfo_screenheight() - 128
            self.jump_height = 0

        # Update frame and position
        self.change_frame(self.moveleft if self.dir < 0 else self.moveright)
        self.geometry(f'128x128+{int(self.x)}+{int(self.y)}')

        # Update FPS display
        self.update_fps_display()

        # Continue the update loop
        self.after(max(1, int(1000 // self.speed)), self.update)

    def change_frame(self, direction):
        if time.time() > self.timestamp + (0.05 / self.speed):
            self.timestamp = time.time()
            self.frame_index = (self.frame_index + 1) % len(direction)
            self.img = direction[self.frame_index]
            self.label.config(image=self.img)

    def start_drag(self, event):
        self.is_dragging = True
        self.offset_x = event.x
        self.offset_y = event.y

    def drag(self, event):
        if self.is_dragging:
            new_x = self.winfo_pointerx() - self.offset_x
            new_y = self.winfo_pointery() - self.offset_y
            self.x = new_x
            self.y = new_y
            self.geometry(f'128x128+{int(self.x)}+{int(self.y)}')

    def stop_drag(self, event):
        self.is_dragging = False

    def on_hover(self, event):
        self.mouse_hover = True
        self.speed = 30  # Max speed when hovered

    def off_hover(self, event):
        self.mouse_hover = False
        self.speed = max(self.speed / 1.05, 5)  # Reset speed to normal when not hovered

if __name__ == "__main__":
    Pet()
