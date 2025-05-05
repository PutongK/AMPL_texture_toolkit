# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 18:34:31 2025

GUI for texture patch
In this version, the visualization part is taken via CLI

Next verison using buttons is under development

@0424 New integration here, combining with texture_morph_dual, with functions of:
    1. Basic parameters: including spacing, indentation depth, angle
    2. Basic directions: inward or outward (cause the bending)
    3. Two modes: one-direction or zig-zag (hopefully causing the twist)
    
@0425 Imporvement on the GUI look   
    Also, improvment on the visualization function, and run visualization with buttons

@author: kangputong
"""

# GUI integration for texture_morph_dual with edge G-code + visualization
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory
from texture_morph_dual import Initializer, generate_control_pairs, reorder_control_points_dual, write_Gcodes
from texture_edge_new import generate_edge_gcode
from ampl_visualization_GUI import AmplVisualization
import os

class TextureGUI:
    def __init__(self, root):
        self.root = root
        root.title("Texture Morph Toolpath Generator")

        self.t = Initializer()

        style = ttk.Style()
        common_font = ("Arial", 12)
        title_font = ("Arial", 12)
        style.configure("TLabel", font=common_font)
        style.configure("TLabelframe", font=title_font)
        style.configure("TLabelframe.Label", font=title_font)
        style.configure("TButton", font=common_font, padding=8)
        style.configure("TEntry", font=common_font)
        style.configure("TCombobox", font=common_font)

        # User Inputs frame
        input_frame = ttk.LabelFrame(root, text="User Inputs", padding=10, relief="groove")
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=2)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Operations frame
        action_frame = ttk.LabelFrame(root, text="Operations", padding=10, relief="groove")
        action_frame.columnconfigure(0, weight=1)
        action_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.entries = {}

        # Location dropdown
        ttk.Label(input_frame, text="Location:").grid(row=0, column=0, sticky="e")
        self.loc_var = tk.StringVar(value="1")
        loc_menu = ttk.Combobox(input_frame, textvariable=self.loc_var, values=["1", "2", "3", "4"])
        loc_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=6)

        fields = [
            ("Spacing (mm):", "sp"),
            ("Angle (deg):", "angle"),
            ("Thinning Top:", "thinning_t"),
            ("Z Hold:", "z_hold"),
        ]

        for i, (label, var) in enumerate(fields, start=1):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky="e")
            entry = ttk.Entry(input_frame)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=6)
            self.entries[var] = entry

        ttk.Label(input_frame, text="Motion Mode:").grid(row=5, column=0, sticky="e")
        self.mode_var = tk.StringVar(value="one_direction")
        mode_menu = ttk.Combobox(input_frame, textvariable=self.mode_var, values=["one_direction", "zig_zag"])
        mode_menu.grid(row=5, column=1, sticky="ew", padx=5, pady=6)

        ttk.Label(input_frame, text="Motion Direction:").grid(row=6, column=0, sticky="e")
        self.dir_var = tk.StringVar(value="inward")
        dir_menu = ttk.Combobox(input_frame, textvariable=self.dir_var, values=["inward", "outward"])
        dir_menu.grid(row=6, column=1, sticky="ew", padx=5, pady=6)

        # Operation buttons
        ttk.Button(action_frame, text="Generate G-code", command=self.generate_gcode).grid(row=0, column=0, pady=10, sticky="ew")
        ttk.Button(action_frame, text="Visualize Path", command=self.visualize_popup).grid(row=1, column=0, pady=10, sticky="ew")
        ttk.Button(action_frame, text="Save to Excel", command=self.save_excel).grid(row=2, column=0, pady=10, sticky="ew")
        ttk.Button(action_frame, text="Generate Edge G-code", command=self.generate_edge).grid(row=3, column=0, pady=10, sticky="ew")

        # Status bar
        self.status = tk.Label(root, text="Ready", anchor="w", relief="sunken", font=("Arial", 10))
        self.status.grid(row=2, column=0, columnspan=2, sticky="ew")

    def update_initializer(self):
        try:
            self.t.loc = self.loc_var.get()
            self.t.sp = float(self.entries['sp'].get())
            self.t.angle = float(self.entries['angle'].get())
            self.t.thinning_t = float(self.entries['thinning_t'].get())
            self.t.z_hold = float(self.entries['z_hold'].get())
            self.t.mode = self.mode_var.get()
            self.t.direction = self.dir_var.get()
            self.t.set_texture_bounds()
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

    def generate_gcode(self):
        self.update_initializer()
        pairs = generate_control_pairs(self.t.ini_pt, self.t.fin_pt, self.t.angle, self.t.sp)
        ordered_pts = reorder_control_points_dual(pairs, mode=self.t.mode, direction=self.t.direction)
        base_dir = askdirectory(title="Select output folder")
        if not base_dir:
            return
        folder = os.path.join(base_dir, f"texture_patch_{self.t.formatted_date}")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"texture_patch_loc{self.t.loc}_{self.t.mode}_{self.t.direction}.txt")
        write_Gcodes(ordered_pts, path, self.t.ini_pt, self.t.fin_pt, self.t.thinning_t, self.t.z_hold)
        self.status.config(text=f"G-code saved to: {path}")
        messagebox.showinfo("Done", f"G-code saved to: {path}")
        self.last_path = path

    def visualize_popup(self):
        if not hasattr(self, 'last_path'):
            messagebox.showerror("No G-code", "Please generate a G-code first.")
            return
        popup = tk.Toplevel()
        popup.title("Select Visualization Method")
        tk.Label(popup, text="Choose visualization type:", font=("Arial", 12)).pack(pady=5)
        for method in ["comet", "comet3", "plot3d_static"]:
            tk.Button(popup, text=method, font=("Arial", 12), command=lambda m=method: self.run_visualize(m, popup)).pack(pady=3)
            
    def run_visualize(self, method, popup):
        popup.destroy()
        visualizer = AmplVisualization()
        method_mapping = {
            "comet": visualizer.comet_from_file,
            "comet3": visualizer.comet3_from_file,
            "plot3d_static": visualizer.plot3d_static_from_file
        }
        try:
            method_mapping[method](self.last_path)
        except Exception as e:
            messagebox.showerror("Visualization Error", f"Error running {method}: {e}")

    def save_excel(self):
        if not hasattr(self, 'last_path'):
            messagebox.showerror("No G-code", "Please generate a G-code first.")
            return
        visualizer = AmplVisualization()
        base_dir = askdirectory(title="Select output folder")
        if not base_dir:
            return
        folder = os.path.join(base_dir, f"texture_patch_{self.t.formatted_date}")
        os.makedirs(folder, exist_ok=True)
        visualizer.save_to_excel(self.last_path)
        self.status.config(text="Excel file saved.")
        messagebox.showinfo("Done", "Excel file saved.")

    def generate_edge(self):
        self.update_initializer()
        generate_edge_gcode(self.t.loc)
        self.status.config(text="Edge path generated.")
        messagebox.showinfo("Done", "Edge path generated.")

if __name__ == "__main__":
    root = tk.Tk()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.geometry("800x400")
    root.resizable(False, False)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    app = TextureGUI(root)
    root.mainloop()

