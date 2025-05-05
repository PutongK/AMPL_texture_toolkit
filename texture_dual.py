# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 14:07:12 2025

@0401 An ultimate version for texture patch.

@0404 Find a merge method instead
@0410 The updated version uses a mirror-merge from ends inward to avoid cracks at the corners.\

----------------------------------------------------------------------------------------------
@0428 Updates:
    Remove visualization related part. All visualization will be carried by the GUI

@author: kangputong
"""

import os
import numpy as np
import math
from datetime import datetime

class Initializer:
    def __init__(self):
        # Basic user inputs and settings
        self.sp = None
        self.ini_pt = None
        self.fin_pt = None
        self.thinning_t = None
        self.thinning_b = None
        self.loc = None
        self.name = None
        self.current_date = datetime.now()
        self.formatted_date = self.current_date.strftime("%m%d")
        self.angle = None
        self.z_hold = None
        self.mode = None
        self.flag = None

    def initialize(self):
        # Collect input from user through console
        self.loc = input("Enter location number of texture patch (1–4): ")
        self.sp = float(input("Enter spacing [mm]: "))
        self.angle = float(input("Enter angle [deg]: "))
        self.thinning_t = float(input("Enter thinning from the top: "))
        self.thinning_b = 0.0  # Not used for now
        self.z_hold = float(input("Enter z_hold [mm]: "))
        self.mode = input("Enter texture mode (one_direction or zig-zag): ") or "one_direction"
        self.flag = input("Enter texture method (inward or outward): ") or "outward"

    def set_texture_bounds(self):
        # Calculate initial and final point coordinates based on location number
        texture_w = 50
        length = 250
        x_coord = length / 4 - texture_w / 2
        y_coord = length / 4 - texture_w / 2

        if self.loc == "1":
            self.ini_pt = [x_coord, y_coord]
            self.fin_pt = [x_coord + texture_w, y_coord + texture_w]
        elif self.loc == "2":
            self.ini_pt = [-x_coord - texture_w, y_coord]
            self.fin_pt = [-x_coord, y_coord + texture_w]
        elif self.loc == "3":
            self.ini_pt = [-(x_coord + texture_w), -(y_coord + texture_w)]
            self.fin_pt = [-x_coord, -y_coord]
        elif self.loc == "4":
            self.ini_pt = [x_coord, -(y_coord + texture_w)]
            self.fin_pt = [x_coord + texture_w, -y_coord]
        else:
            raise ValueError("Invalid location number (should be 1–4)") 

# Compute the intersection between a given line and the square edges
def line_square_intersections(p0, dir_vec, x_min, x_max, y_min, y_max):
    hits = []
    square_edges = [
        (np.array([x_min, y_min]), np.array([x_max, y_min])),
        (np.array([x_max, y_min]), np.array([x_max, y_max])),
        (np.array([x_max, y_max]), np.array([x_min, y_max])),
        (np.array([x_min, y_max]), np.array([x_min, y_min])),
    ]
    for p1, p2 in square_edges:
        seg_dir = p2 - p1
        A = np.column_stack((dir_vec, -seg_dir))
        b = p1 - p0
        try:
            t_vals = np.linalg.solve(A, b)
            t1, t2 = t_vals
            if 0 <= t2 <= 1:
                hits.append(p0 + t1 * dir_vec)
        except np.linalg.LinAlgError:
            continue
    return hits if len(hits) == 2 else []

# Generate pairs of control points based on lines intersecting the square
def generate_control_pairs(ini_pt, fin_pt, angle_deg, sp):
    theta = math.radians(angle_deg)
    dir_vec = np.array([np.cos(theta), np.sin(theta)])
    normal_vec = np.array([-dir_vec[1], dir_vec[0]])

    x_min, y_min = min(ini_pt[0], fin_pt[0]), min(ini_pt[1], fin_pt[1])
    x_max, y_max = max(ini_pt[0], fin_pt[0]), max(ini_pt[1], fin_pt[1])

    corners = np.array([
        [x_min, y_min],
        [x_min, y_max],
        [x_max, y_min],
        [x_max, y_max]
    ])
    projections = corners @ normal_vec
    min_proj, max_proj = projections.min(), projections.max()
    num_lines = int((max_proj - min_proj) / sp) + 1

    x_min, y_min = min(ini_pt[0], fin_pt[0]), min(ini_pt[1], fin_pt[1])
    x_max, y_max = max(ini_pt[0], fin_pt[0]), max(ini_pt[1], fin_pt[1])

    intersections = []
    for i in range(num_lines):
        offset = min_proj + i * sp
        p0 = offset * normal_vec
        points = line_square_intersections(p0, dir_vec, x_min, x_max, y_min, y_max)
        if len(points) == 2:
            intersections.append(points)

    return intersections

def reorder_control_points_dual(pairs, mode="one_direction", direction="inward"):
    num_pairs = len(pairs)

    # Determine pair sequence
    if direction == "inward":
        # From ends to center (original logic)
        ordered_indices = []
        for i in range((num_pairs + 1) // 2):
            ordered_indices.append(i)
            if i != num_pairs - 1 - i:
                ordered_indices.append(num_pairs - 1 - i)
    elif direction == "outward":
        # From center to ends
        mid = num_pairs // 2
        ordered_indices = [mid]
        for i in range(1, mid + 1):
            if mid - i >= 0:
                ordered_indices.append(mid - i)
            if mid + i < num_pairs:
                ordered_indices.append(mid + i)
    else:
        raise ValueError("Direction must be 'inward' or 'outward'")

    # Reorder control points
    ordered_points = []
    for idx, i in enumerate(ordered_indices):
        pt1, pt2 = pairs[i]
        if pt1[0] > pt2[0]:
            pt1, pt2 = pt2, pt1
        if mode == "zig_zag" and idx % 2 == 1:
            ordered_points.extend([pt2, pt1])
        else:
            ordered_points.extend([pt1, pt2])

    return ordered_points

# Write final G-code including plunge, jog, and retract motions
def write_Gcodes(control_pts, file_path, ini_pt, fin_pt, thinning_t, z_hold):
    center_x = (ini_pt[0] + fin_pt[0]) / 2
    center_y = (ini_pt[1] + fin_pt[1]) / 2

    head_lines = [
        "DELGAT \n",
        "UNDEFINE ALL \n",
        "&1 \n",
        "CLOSE \n",
        "#1->-16000X \n",
        "#2->-16000X \n",
        "#3->16000Y \n",
        "#4->16000Y \n",
        "#5->16000Z \n",
        "#6->-16000U \n",
        "#7->-16000U \n",
        "#8->16000V \n",
        "#9->16000V \n",
        "#10->-16000W \n",
        "OPEN PROG 2 \n",
        "CLEAR \n",
        "FRAX(X,Y,Z) \n",
        "ABS \n",
        "TA 100.0 \n",
        "TS 50 \n",
        "X 0.0000 Y 0.0000 Z 80.0000 U 0.0000 V 0.0000 W -80.0000 F 5.0000 \n"
    ]

    with open(file_path, 'w') as file:
        file.writelines(head_lines)
        file.write(f"X {control_pts[0][0]:.4f} Y {control_pts[0][1]:.4f} Z 80.0000 U {center_x:.4f} V {center_y:.4f} W -80.0000 \n")

        for i in range(0, len(control_pts), 2):
            pt1, pt2 = control_pts[i], control_pts[i+1]
            # plunge to cutting depth
            file.write(f"X {pt1[0]:.4f} Y {pt1[1]:.4f} Z {-thinning_t:.4f} U {center_x:.4f} V {center_y:.4f} W 0.0000\n")
            file.write(f"X {pt2[0]:.4f} Y {pt2[1]:.4f} Z {-thinning_t:.4f} U {center_x:.4f} V {center_y:.4f} W 0.0000\n")
            # retract and jog to next pair
            if i + 2 < len(control_pts):
                next_pt = control_pts[i + 2]
                file.write(f"X {pt2[0]:.4f} Y {pt2[1]:.4f} Z {z_hold:.4f} U {center_x:.4f} V {center_y:.4f} W 0.0000\n")
                file.write(f"X {next_pt[0]:.4f} Y {next_pt[1]:.4f} Z {z_hold:.4f} U {center_x:.4f} V {center_y:.4f} W 0.0000\n")

        file.write("X 0.0000 Y 0.0000 Z 80.0000 U 0.0000 V 0.0000 W -80.0000 \n")
        file.write("CLOSE ALL\n")

if __name__ == "__main__":
    t = Initializer()
    t.initialize()
    t.set_texture_bounds()

    # Set up file path and folder
    date_code = datetime.now().strftime("%m%d")
    folder_name = f"new texture patch_{date_code}"
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, f"texture_patch_loc{t.loc}_{t.mode}_{date_code}.txt")

    # Generate, reorder, and write toolpath
    control_pairs = generate_control_pairs(t.ini_pt, t.fin_pt, t.angle, t.sp)
    ordered_points = reorder_control_points_dual(control_pairs, mode=t.mode, direction=t.flag)
    write_Gcodes(ordered_points, file_path, t.ini_pt, t.fin_pt, t.thinning_t, t.z_hold)

    print(f"Dual path G-code saved to: {file_path}")
    