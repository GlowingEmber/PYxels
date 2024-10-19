import tkinter as tk
import math

total_px = 640

class App(tk.Frame):
    def __init__(self, master=None, pixel_size=20, grid_size=32):
        super().__init__(master)
        self.pixel_size = pixel_size
        self.grid_size = grid_size
        self.active_coordinates = []
        self.canvas = tk.Canvas(self, width=self.grid_size * self.pixel_size, height=self.grid_size * self.pixel_size)
        self.canvas.bind('<Button-1>', self.left_click)
        self.canvas.bind('<B1-Motion>', self.left_click)
        self.canvas.bind('<Button-2>', self.right_click)
        self.canvas.bind('<B2-Motion>', self.right_click)
        self.canvas.pack()
    
    def group(self, coordinate):
        return math.floor(coordinate / self.pixel_size)

    def left_click(self, event):
        x_group = self.group(event.x)
        y_group = self.group(event.y)
        if not (x_group, y_group) in self.active_coordinates:
            self.canvas.create_rectangle(x_group * self.pixel_size, y_group * self.pixel_size, x_group*self.pixel_size + self.pixel_size, y_group*self.pixel_size + self.pixel_size, fill='white')
            self.active_coordinates.append((x_group, y_group))
        print(self.active_coordinates)


    def right_click(self, event):
        x_group = self.group(event.x)
        y_group = self.group(event.y)
        if (x_group, y_group) in self.active_coordinates:
            self.canvas.delete(self.canvas.create_rectangle(x_group * self.pixel_size, y_group * self.pixel_size, x_group*self.pixel_size + self.pixel_size, y_group*self.pixel_size + self.pixel_size, fill='white'))
            self.active_coordinates.remove((x_group, y_group))
        print(self.active_coordinates)

root = tk.Tk()

# Create a GUI with a grid size of 32x32, where each "pixel" is 20x20 pixels on the screen
gui = App(root, pixel_size=20, grid_size=32)
gui.pack()

root.mainloop()
