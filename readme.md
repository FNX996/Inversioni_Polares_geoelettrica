Markdown

# PolaresInversion

**PolaresInversion** is a professional-grade geoelectrical tool designed for 2D processing, inversion, and advanced visualization of Electrical Resistivity Tomography (ERT) datasets. Tailored explicitly around the native output structures of the **POLARES 32** imaging tool, it bridges raw data acquisition with highly polished, deployment-ready tomographic cross-sections.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Core Capabilities

* **General Array File Parsing:** Direct import of structural `.dat` configuration assets exported by POLARES hardware arrays.
* **Modern GUI & Splash Screen:** Fully redesigned flat interface adopting modern visual standards, including an elegant Dark Mode splash loading screen and interactive status coloration indicating processing states.
* **Dynamic Visualization Canvas:** Interactive, industry-standard multi-panel canvas featuring:
    * Measured apparent resistivity pseudosection grid mapping.
    * Forward-calculated structural response cross-sections.
    * Finished subsurface FEM model tomographies.
* **Advanced UI Controls:** Live in-plot widgets to change boundary thresholds (`Min/Max Rho`) instantly, alongside toggle switches for `Contour Lines` and trapezoidal geometric filtering (`Crop Corners`).
* **ResIPy-Style Mesh Control:** Accessible parameter configuration menus detailing damping factors (`Lambda`), vertical weight constraints (`Z-Weight`), maximum depth profiles, and customizable finite-element triangular setups via `Characteristic Length` and boundary refinement (`Refine Mesh`).
* **Clean Numerical Legends:** Absolute colorbars mapped onto a vertical right-hand sidebar layout utilizing standard linear integer notation rather than scientific exponential symbols.
* **Professional Grade Exporting:** Direct extraction of high-resolution `.png` images and structural `.vtk` geometry layers built for rapid import into QGIS or ParaView pipelines.

---

## 🛠️ Software Architecture

The workflow is written natively in Python, deploying a robust scientific framework:
* **pyGIMLi**: Advanced multi-method modeling engine using Finite Element Methods (FEM).
* **Matplotlib**: Flexible plotting engine handling custom subplots and embedded graphical input widgets.
* **NumPy**: Low-level high-performance array management.
* **Tkinter**: Lightweight standalone desktop GUI.

---

## 📦 Distribution & Setup

### Windows Standalone Executable (Recommended)
Navigate to the **Releases** framework on the right sidebar, download the standalone compilation `PolaresInvert.exe`, and launch the asset directly. No local Python runtime or library installations are required.

### Developer Environment Setup
1. Verify a local running setup of Python 3.12+.
2. Clone this repository structure:
   ```bash
   git clone [https://github.com/FNX996/InGeoLab.git](https://github.com/FNX996/InGeoLab.git)

    Install missing library components:
    Bash

    pip install pygimli matplotlib numpy

    Run the code:
    Bash

    python PolaresInvert.py

👨‍💻 Author Info

    Fabrizio Nori - InGeoLab s.r.l.

    GitHub Profile: @FNX996

    Web: https://github.com/FNX996

📄 License

This project is licensed under the MIT License:

Copyright (c) 2026 Fabrizio Nori - InGeoLab s.r.l.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
