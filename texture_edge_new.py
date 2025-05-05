# -*- coding: utf-8 -*-
"""
Created on Thu Apr  3 16:51:12 2025

@author: kangputong
"""

import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

def generate_edge_gcode(loc):
    texture_w = 50
    length = 250
    offset = 5  # outward expansion from the square edge
    x_coord = length / 4 - texture_w / 2
    y_coord = length / 4 - texture_w / 2

    if loc == "1":
        ini_pt = [x_coord, y_coord]
        fin_pt = [x_coord + texture_w, y_coord + texture_w]
    elif loc == "2":
        ini_pt = [-x_coord - texture_w, y_coord]
        fin_pt = [-x_coord, y_coord + texture_w]
    elif loc == "3":
        ini_pt = [-(x_coord + texture_w), -(y_coord + texture_w)]
        fin_pt = [-x_coord, -y_coord]
    elif loc == "4":
        ini_pt = [x_coord, -(y_coord + texture_w)]
        fin_pt = [x_coord + texture_w, -y_coord]
    else:
        raise ValueError("Invalid location number (should be 1–4)")

    x_min, y_min = min(ini_pt[0], fin_pt[0]), min(ini_pt[1], fin_pt[1])
    x_max, y_max = max(ini_pt[0], fin_pt[0]), max(ini_pt[1], fin_pt[1])

    # Expand the square by the offset
    x_min -= offset
    y_min -= offset
    x_max += offset
    y_max += offset

    corners = [
        (x_min, y_min),
        (x_max, y_min),
        (x_max, y_max),
        (x_min, y_max),
        (x_min, y_min)
    ]

    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    z_height = -0.15

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
        "X 0.0000 Y 0.0000 Z 80.0000 U 0.0000 V 0.0000 W -80.0000 F 5.0000 \n",
        f"X {corners[0][0]:.4f} Y {corners[0][1]:.4f} Z 80.0000 U {center_x:.4f} V {center_y:.4f} W -80.0000 F 5.0000\n"
    ]

    date_code = datetime.now().strftime("%m%d")
    folder_name = f"edge_path_{date_code}"
    os.makedirs(folder_name, exist_ok=True)
    file_name = f"edge_path_loc{loc}_{date_code}.txt"
    file_path = os.path.join(folder_name, file_name)

    with open(file_path, 'w') as file:
        file.writelines(head_lines)
        for x, y in corners:
            variables = [x, y, z_height, center_x, center_y, 0.0]
            file.write("X %.4f Y %.4f Z %.4f U %.4f V %.4f W %.4f\n" % tuple(variables))
        file.write("CLOSE ALL\n")

    print(f"Edge G-code saved to: {file_path}")
    return ini_pt, fin_pt, offset

def plot_squares(ini_pt, fin_pt, offset):
    x0_min, y0_min = min(ini_pt[0], fin_pt[0]), min(ini_pt[1], fin_pt[1])
    x0_max, y0_max = max(ini_pt[0], fin_pt[0]), max(ini_pt[1], fin_pt[1])
    original = [
        (x0_min, y0_min),
        (x0_max, y0_min),
        (x0_max, y0_max),
        (x0_min, y0_max),
        (x0_min, y0_min)
    ]
    x1_min, y1_min = x0_min - offset, y0_min - offset
    x1_max, y1_max = x0_max + offset, y0_max + offset
    expanded = [
        (x1_min, y1_min),
        (x1_max, y1_min),
        (x1_max, y1_max),
        (x1_min, y1_max),
        (x1_min, y1_min)
    ]
    original = np.array(original)
    expanded = np.array(expanded)
    plt.figure(figsize=(6, 6))
    plt.plot(original[:, 0], original[:, 1], 'b-o', label='Original')
    plt.plot(expanded[:, 0], expanded[:, 1], 'r--o', label='Offset')
    plt.legend()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title("Square vs Offset Square")
    plt.grid(True)
    plt.show()

def main():
    date_code = datetime.now().strftime("%m%d")
    folder_name = f"edge_path_{date_code}"
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, f"edge_path_all_{date_code}.txt")

    with open(file_path, 'w') as file:
        for loc in ["1", "2", "3", "4"]:
            texture_w = 50
            length = 250
            offset = 5
            x_coord = length / 4 - texture_w / 2
            y_coord = length / 4 - texture_w / 2

            if loc == "1":
                ini_pt = [x_coord, y_coord]
                fin_pt = [x_coord + texture_w, y_coord + texture_w]
            elif loc == "2":
                ini_pt = [-x_coord - texture_w, y_coord]
                fin_pt = [-x_coord, y_coord + texture_w]
            elif loc == "3":
                ini_pt = [-(x_coord + texture_w), -(y_coord + texture_w)]
                fin_pt = [-x_coord, -y_coord]
            elif loc == "4":
                ini_pt = [x_coord, -(y_coord + texture_w)]
                fin_pt = [x_coord + texture_w, -y_coord]

            x_min, y_min = min(ini_pt[0], fin_pt[0]), min(ini_pt[1], fin_pt[1])
            x_max, y_max = max(ini_pt[0], fin_pt[0]), max(ini_pt[1], fin_pt[1])
            x_min -= offset
            y_min -= offset
            x_max += offset
            y_max += offset

            corners = [
                (x_min, y_min),
                (x_max, y_min),
                (x_max, y_max),
                (x_min, y_max),
                (x_min, y_min)
            ]

            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            z_height = -0.15

            if loc == "1":  # only include head_lines once at the beginning
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
                ]
                file.writelines(head_lines)

            file.write("X 0.0000 Y 0.0000 Z 80.0000 U 0.0000 V 0.0000 W -80.0000 F 5.0000\n")
            file.write(f"X {corners[0][0]:.4f} Y {corners[0][1]:.4f} Z 80.0000 U {center_x:.4f} V {center_y:.4f} W -80.0000 F 5.0000\n")

            for x, y in corners:
                variables = [x, y, z_height, center_x, center_y, 0.0]
                file.write("X %.4f Y %.4f Z %.4f U %.4f V %.4f W %.4f\n" % tuple(variables))
            file.write("X 0.0000 Y 0.0000 Z 80.0000 U 0.0000 V 0.0000 W -80.0000\n")

        file.write("CLOSE ALL\n")
    print(f"Combined edge G-code saved to: {file_path}")

if __name__ == "__main__":
    main()
