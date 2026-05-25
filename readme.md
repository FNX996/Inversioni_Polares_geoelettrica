Markdown

# PolaresInversion

**PolaresInversion** is a professional geophysical software tool designed for the 2D inversion, processing, and visualization of Electrical Resistivity Tomography (ERT) data. Specifically tailored to handle the native output data format of the **POLARES 32** instrument, the software provides a seamless desktop workflow from raw data optimization to final cross-section visualization.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Key Features

* **Native Data Import:** Direct parsing of POLARES `.dat` files (General Array format).
* **Data Filtering & Editing:**
    * Visual detection and removal of noisy/spurious points (*Exterminate bad data points*).
    * Profile spatial transformations: electrode shifting (*Shift X*) and layout mirroring (*Flip X*).
    * Dataset trimming (*Trim*) and localized window exclusions (*Exclude range*).
* **Advanced 2D Inversion:** Powered by robust optimization algorithms supporting both **Smoothness-constrained (L2)** and **Robust/Blocky (L1)** inversion methods.
* **Topographic Constraints:** Load custom elevation files (X, Z) to seamlessly adapt the finite element mesh to real-world topography.
* **Depth Control:** User-defined maximum analysis depth limits directly integrated into the mesh generation and visual axis controls.
* **Commercial-Grade Visualization:** High-fidelity 3-panel plotting matching industry standards (such as RES2DINV or ResIPy):
    * Measured and calculated apparent resistivity pseudosections.
    * Real inverted model resistivity depth sections.
    * Standardized **Seismic** (Red-White-Blue) logarithmic discrete colormap with automated robust clipping (2nd/98th percentiles) to prevent color scale saturation.
* **Professional Exporting:** Save figures as high-resolution `.png` images and export 2D/3D inversion meshes into `.vtk` format for advanced processing in QGIS or ParaView.

---

## 🛠️ Built With

The software is written in Python, leveraging a robust scientific open-source stack:
* **pyGIMLi**: Core computational physics library for modeling and inversion using Finite Element Methods (FEM).
* **Matplotlib**: Desktop and layout graphic engine for geophysical plotting.
* **NumPy**: Multidimensional array mapping and matrix calculations.
* **Tkinter**: Fast and lightweight desktop Graphical User Interface (GUI).

---

## 📦 Getting Started

### For End Users (Windows Standalone)
Go to the **[Releases](https://github.com/FNX996/InGeoLab/releases)** section on the right side of this repository, download `PolaresInvert.exe`, and run it directly. No Python installation or background configuration is required.

### For Developers (Running from Source)
1. Ensure you have Python 3.12+ installed on your machine.
2. Clone this repository:
   ```bash
   git clone [https://github.com/FNX996/InGeoLab.git](https://github.com/FNX996/InGeoLab.git)

    Install the required dependencies:
    Bash

    pip install pygimli matplotlib numpy

    Run the application:
    Bash

    python PolaresInvert.py

    (Optional) Recompile the executable using the provided automation script:
    Bash

    build_exe.bat

👨‍💻 Author

    Fabrizio Nori - InGeoLab s.r.l.

    GitHub Profile: @FNX996

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
