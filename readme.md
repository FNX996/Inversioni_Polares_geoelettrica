# PolaresInversion

**PolaresInversion** is a professional-grade geoelectrical tool designed for 2D processing, inversion, and advanced visualization of Electrical Resistivity Tomography (ERT) datasets. Tailored explicitly around the native output structures of the **POLARES 32** imaging tool, it bridges raw data acquisition with highly polished, deployment-ready tomographic cross-sections.

![Version](https://img.shields.io/badge/version-2.5.0-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Core Capabilities

* **General Array File Parsing:** Direct import of structural `.dat` configuration assets exported by POLARES hardware arrays.
* **Dynamic Visualization GUI:** Interactive, industry-standard multi-panel canvas featuring:
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

### Windows Standalone Executive (Recommended)
Navigate to the **[Releases](https://github.com/FNX996/InGeoLab/releases)** framework on the right sidebar, download the standalone compilation `PolaresInvert.exe`, and launch the asset directly. No local Python runtime or library installations are required.

### Developer Environment Setup
1. Verify a local running setup of Python 3.12+.
2. Clone this repository structure:
   ```bash
   git clone [https://github.com/FNX996/InGeoLab.git](https://github.com/FNX996/InGeoLab.git)
