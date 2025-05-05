# AMPL_texture_toolkit
Python scripts for generating and visualizing G-codes for surface texture patches.
It is designed for precision incremental forming processes and supports both direct and mirrored motion strategies.
<img width="1121" alt="screenshot" src="https://github.com/user-attachments/assets/df9f2f1d-0be8-4264-8fc8-1adf1c69b357" />

---

## 🚀 Features

- **Intuitive GUI** using `tkinter` with organized user inputs and actions
- **G-code generation** for:
  - Textures (one-direction, zig-zag, inward, outward)
  - Square-edge boundary patterns
- **Built-in visualization tools**:
  - Static 3D plots
  - Top/bottom path overlays
  - Dynamic comet animation (2D & 3D) with **looping** and **manual stop**
- **Automatic file organization** using timestamps and location tags
- **Export to Excel** for coordinate tracking

---

## 📁 Project Structure

```
├── gui_texture.py              # Main GUI application
├── texture_dual.py             # G-code generation with dual motion logic
├── texture_edge_new.py         # Generates boundary edge G-code
├── ampl_visualization_GUI.py   # Visualization library (static + dynamic)
├── output/                     # Auto-created folder for G-code results
└── README.md
```

---

## 🧰 Requirements

- Python 3.8+
- tkinter
- matplotlib
- numpy
- pandas (for Excel export)

To install dependencies:

```bash
pip install matplotlib numpy pandas
```

---

## 🖥️ How to Use

1. **Run the GUI:**
   ```bash
   python gui_texture.py
   ```

2. **Enter Parameters:**
   - Choose texture patch location (1–4)
   - Define spacing, thinning, and angle
   - Select motion type (`one_direction`, `zig_zag`)
   - Choose merge logic (`inward`, `outward`)

3. **Operations:**
   - Generate G-code
   - Visualize paths (static/dynamic)
   - Save data to Excel

---

## ✍️ Author

Developed by Putong Kang, Department of Mechanical Engineering, Northwestern University.

---

## 📄 License

MIT License – see [`LICENSE`](LICENSE) file for details.
