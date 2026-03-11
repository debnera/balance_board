import math
import random
import time
import tkinter as tk
import threading

class RealtimeDebugger:
    def __init__(self, max_angle):
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.max_angle = max_angle

    def create_canvas(self, root):
        self.root = root
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()


        # Draw circle for yaw visualization
        self.canvas.create_oval(50, 50, 350, 350, outline="lightgray")
        mid = 200
        size = 150
        sx = self.max_angle/90 * 300
        self.canvas.create_oval(mid-sx, mid-sx, mid+sx, mid+sx, outline="lightgray")

        self.yaw_vector = self.canvas.create_line(200, 200, 200, 50, tags="yaw_vector")

        # Draw circle for pitch/roll visualization
        self.pitch_roll_dot = self.canvas.create_oval(195, 195, 205, 205, fill="blue")

    def update_values(self, yaw, pitch, roll):
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll

    def update(self):
        self.draw_yaw()
        self.draw_pitch_roll()

    def draw_yaw(self):
        x = 200 - 150 * math.sin(math.radians(self.yaw))
        y = 200 - 150 * math.cos(math.radians(self.yaw))
        self.canvas.coords(self.yaw_vector, 200, 200, x, y)

    def draw_pitch_roll(self):
        x = 200 + 150 * math.sin(math.radians(self.roll))
        y = 200 - 150 * math.sin(math.radians(self.pitch))

        # roll = min(self.roll, max_angle)
        # roll = max(self.roll, -max_angle) * (90 / max_angle)
        # pitch = min(self.pitch, max_angle)
        # pitch = max(self.pitch, -max_angle) * (90 / max_angle)
        # x = 200 + 150 * math.sin(math.radians(roll))
        # y = 200 - 150 * math.sin(math.radians(pitch))
        self.canvas.coords(self.pitch_roll_dot, x-5, y-5, x+5, y+5)

def start_gui(max_angle):
    debugger = RealtimeDebugger(max_angle=max_angle)
    def thread_function(debugger):
        root = tk.Tk()
        debugger.create_canvas(root)
        def update_visualization():
            debugger.update()
            root.update()
            root.after(1, update_visualization)

        update_visualization()
        root.mainloop()
    gui_thread = threading.Thread(target=thread_function, args=(debugger,))
    gui_thread.start()
    return debugger

if __name__ == "__main__":
    debugger = start_gui(max_angle=30)
    while True:
        yaw = 45 * random.random()
        pitch = 30 * random.random()
        roll = 20 * random.random()
        debugger.update_values(yaw, pitch, roll)
        time.sleep(0.1)


#%%
