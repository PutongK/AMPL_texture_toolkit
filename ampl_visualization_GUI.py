# -*- coding: utf-8 -*-
"""
The current structure preprocesses the G-code, extracts XYZUVW coordinates, and plots them.
--------------------------------------------------------------------------------
*  New functions:                                                              *
*                                                                              *
*  parse_file(file_path)                  Reads G-code into x, y, z, u, v, w   *
*  comet_from_file(file_path)             Animates 2D motion + Top/Bottom plot *
*  comet3_from_file(file_path)            Animates 3D motion + Top/Bottom plot *
*  plot3d_static_from_file(file_path)     Static 3D plot + Top/Bottom plot     *
*  save_to_excel(file_path)	          Saves data to Excel without prompt   *
--------------------------------------------------------------------------------
@author: kangputong
"""

# Cleaned and GUI-ready visualization module
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AmplVisualization:
    # Parse G-code text file into arrays of X, Y, Z, U, V, W
    def parse_file(self, file_path):
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith("X"):
                    parts = line.strip().split()
                    variables = {}
                    for i in range(0, len(parts), 2):
                        variables[parts[i]] = float(parts[i + 1])
                    # Only append if both X and Y exist
                    if "X" in variables and "Y" in variables:
                        data.append([
                            variables.get("X", 0.0),
                            variables.get("Y", 0.0),
                            variables.get("Z", 0.0),
                            variables.get("U", 0.0),
                            variables.get("V", 0.0),
                            variables.get("W", 0.0)
                        ])
        array = np.array(data)
        return array[:, 0], array[:, 1], array[:, 2], array[:, 3], array[:, 4], array[:, 5]

    # Animate 2D comet plot from file
    def comet_from_file(self, file_path):
        x, y, z, u, v, w = self.parse_file(file_path)
        self.comet(x, y)
        self.plot_top_bottom(x, y, u, v)

    # Animate 3D comet plot from file
    def comet3_from_file(self, file_path):
        x, y, z, u, v, w = self.parse_file(file_path)
        self.comet3(x, y, z)
        self.plot_top_bottom(x, y, u, v)

    # Static 3D line plot from file
    def plot3d_static_from_file(self, file_path):
        x, y, z, u, v, w = self.parse_file(file_path)
        self.plot3d_static(x, y, z)
        self.plot_top_bottom(x, y, u, v)

    # Save parsed data into an Excel file
    def save_to_excel(self, file_path):
        x, y, z, u, v, w = self.parse_file(file_path)
        df = pd.DataFrame({
            "X": x,
            "Y": y,
            "Z": z,
            "U": u,
            "V": v,
            "W": w
        })
        excel_path = file_path.replace(".txt", ".xlsx")
        df.to_excel(excel_path, index=False)

    # Basic comet animation 2D (red lines)
    def comet(self, x, y):
        window = tk.Toplevel()
        window.title("Comet 2D View")

        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        ax.set_xlim(min(x)-5, max(x)+5)
        ax.set_ylim(min(y)-5, max(y)+5)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Comet 2D View")
        ax.grid(True)
        
        plt.close(fig)

        line, = ax.plot([], [], 'b-')
        
        self.stop_animation = False  # Control flag
        
        def stop():
            self.stop_animation = True
        
        def update(frame):
            line.set_data(x[:frame+1], y[:frame+1])
            canvas.draw_idle()
            canvas.flush_events()

        def animate():
            def single_pass(frame=0):
                if self.stop_animation:
                    return  # Stop gracefully if requested
                if frame < len(x):
                    update(frame)
                    window.update()
                    window.after(50, lambda: single_pass(frame + 1))
                else:
                    single_pass(0)  # Loop forever

            single_pass()

        # Add Stop button
        stop_button = ttk.Button(window, text="Stop Animation", command=stop)
        stop_button.pack(pady=10)

        window.after(0, animate)

    # Basic comet animation 3D (blue lines)
    def comet3(self, x, y, z):
        window = tk.Toplevel()
        window.title("Comet 3D View")

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        ax.set_xlim(min(x)-5, max(x)+5)
        ax.set_ylim(min(y)-5, max(y)+5)
        ax.set_zlim(min(z)-5, max(z)+5)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Comet 3D View")
        ax.grid(True)
        
        plt.close(fig)

        line, = ax.plot([], [], [], 'b-')
        
        self.stop_animation = False
        
        def stop():
            self.stop_animation = True

        def update(frame):
            line.set_data(x[:frame+1], y[:frame+1])
            line.set_3d_properties(z[:frame+1])
            canvas.draw_idle()
            canvas.flush_events()

        def animate():
            def single_pass(frame=0):
                if self.stop_animation:
                    return
                if frame < len(x):
                    update(frame)
                    window.update()
                    window.after(80, lambda: single_pass(frame + 1))
                else:
                    single_pass(0)  # Loop forever

            single_pass()

        stop_button = ttk.Button(window, text="Stop Animation", command=stop)
        stop_button.pack(pady=10)

        window.after(0, animate)

    # Static 3D plot (green lines)
    def plot3d_static(self, x, y, z):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(x, y, z, 'g-')
        ax.set_title("Static 3D Plot")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.grid(True)
        plt.show()

    # Always show Top Tool and Bottom Tool overlay
    def plot_top_bottom(self, x, y, u, v):
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))

        axs[0].plot(x, y, 'm-')
        axs[0].set_title("Top Tool Path")
        axs[0].set_xlabel("X")
        axs[0].set_ylabel("Y")
        axs[0].grid(True)

        axs[1].plot(u, v, 'c-')
        axs[1].set_title("Bottom Tool Path")
        axs[1].set_xlabel("U")
        axs[1].set_ylabel("V")
        axs[1].grid(True)

        plt.tight_layout()
        plt.show()

#%% Example use for testing
if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw()  # Hide main root window

    visualizer = AmplVisualization()

    sample_path = "texture_patch_test.txt"

    # Uncomment one of these to test:
    # visualizer.comet_from_file(sample_path)
    visualizer.comet3_from_file(sample_path)
    # visualizer.plot3d_static_from_file(sample_path)

    root.mainloop()
