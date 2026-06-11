# LAS Photo Camera Simulator GUI

A modern, streamlined graphical user interface (GUI) wrapper for the `lasPhotoCamSIM` C++ executable. This tool is designed (in an afternoon) for forestry professionals and researchers to easily batch-process Terrestrial Laser Scanning (TLS) point clouds, deriving synthetic hemispherical canopy photos and gap fraction metrics without needing to use the command line.

**Author:** Andrew Saah, John Battles, Tracy Benning
**Date:** June 2026  

---

## Key Features

* **TLS Coordinate Handling:**  Set your scanner origin (e.g., `0, 0, 0`). The application dynamically handles camera CSV generation in the background.
* **Batch Processing:** Seamlessly point the app at an entire folder of `.las` or `.laz` files. The wrapper (hopefully) loops through the data without crashing or freezing.
* **Automated Image Rendering:** Automatically parses the raw `.asc` grid outputs into clean, high-contrast binary (black & white) `.jpg` hemispherical images.
* **Data Compilation:** Extracts the calculated Gap Fraction (%) from every scan and compiles it into a single, easy-to-read `master_summary.csv` for the entire batch.
* **Clean Workspaces:** Automatically creates timestamped output folders for every run and acts as a digital janitor, deleting intermediate/temporary `.csv` and `.out` files to keep your directories clutter-free.

---

## Installation & Setup

This application is built to be a simple front end for a program called LASPhotoCamSim developed by [Francesco Pirotti](https://github.com/fpirotti). Its highly encouraged to get familiar with LASPhotoCamSIM to get to know how the underlying mechanics of this app will work. This application is built with Python. To run it, you will need Python installed on your system along with a few standard libraries. Currently this has only been tested on a Windows 11 system, but should be able to work on all other systems with python instance. 

### 1. The Executable
Before running the app, ensure that the core C++ executable (`lasPhotoCamSIM.exe`) is located in the **exact same folder** as `app.py`. 

### 2. Install Dependencies
Open your terminal or command prompt, navigate to this folder, and run the following command to install the required Python packages:

    pip install customtkinter numpy matplotlib

---

## Usage Guide

To launch the application, run the following command in your terminal:

    python app.py

### Mode 1: Single Scan Mode
Use this mode if you only need to process one specific TLS point cloud.
1. Select your input `.las` or `.laz` file.
2. Enter your Scanner Origin (X, Y, Z). For most standalone TLS scans, this is `0.0, 0.0, 0.0`.
3. Select a **Master Output Directory** (a new timestamped folder will be created inside it).
4. Configure your simulation parameters (Grid Size, Camera Height, etc.).
5. Click **Generate Hemispherical Photos**.

### Mode 2: Batch Mode
Use this mode to process an entire folder of TLS scans using identical parameters.
1. Select the folder containing your `.las` or `.laz` files.
2. Select your Master Output Directory.
3. Configure your simulation parameters and Scanner Origin (these will be applied globally to every scan in the folder).
4. Click **Generate Hemispherical Photos**. 

---

## Understanding the Outputs

Once a run is complete, navigate to your Master Output Directory. You will find a new folder named `Single_Scan_[TIMESTAMP]` or `Batch_Scan_[TIMESTAMP]`.

Inside this folder, you will find:
1. **[ScanName].jpg:** The high-contrast, binary hemispherical photo representing your canopy mask.
2. **[ScanName].asc:** The raw ESRI grid file containing the exact point counts per pixel.
3. **master_summary.csv:** A compiled spreadsheet listing the name of every processed scan alongside its calculated Gap Fraction percentage.

---

## Troubleshooting

* **App crashes immediately or does nothing:** Ensure `lasPhotoCamSIM.exe` is in the same directory as `app.py`.
* **GUI looks strange or doesn't scale:** Ensure you are using the latest version of `customtkinter`. 
* **Command failed with exit code 1:** Check the Process Console log at the bottom of the app. This usually means your Zenith Cutoff or Camera Height parameters are conflicting with the actual dimensions of your point cloud.