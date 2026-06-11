import customtkinter
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import queue
import os
import shutil
import datetime
import numpy as np
import matplotlib.pyplot as plt

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("LAS Photo Camera Simulator")
        self.geometry("600x900")

        # --- Custom Icon Placeholder ---
        try:
            # 1. Tell Windows this is a unique app so it updates the taskbar icon
            import ctypes
            myappid = 'andrewsaah.lasphotocam.gui.1' # Arbitrary unique ID string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
            # 2. Safely locate the icon file using an absolute path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, "icon.ico")
            
            # 3. Apply the icon
            self.iconbitmap(icon_path)
        except Exception as e:
            # If it fails, it will quietly print the reason to your terminal but won't crash the app
            print(f"Could not load icon: {e}")
            pass

        # Configure main window layout: Top row expands, bottom row stays fixed
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Scrollable area gets all extra vertical space
        self.grid_rowconfigure(1, weight=0) # Log frame stays docked at the bottom

        # 1. TOP CONTAINER (Scrollable settings block)
        self.main_container = customtkinter.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))
        self.main_container.grid_columnconfigure(0, weight=1)

        # 2. BOTTOM CONTAINER (Fixed Log Console)
        self.log_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.log_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.log_frame.grid_columnconfigure(0, weight=1)


        # ==========================================
        # BUILD THE MAIN CONTAINER BLOCKS
        # ==========================================

        # --- BLOCK 1: MODE & INPUT SELECTION ---
        self.input_block = customtkinter.CTkFrame(self.main_container)
        self.input_block.grid(row=0, column=0, pady=(10, 5), sticky="ew")
        self.input_block.grid_columnconfigure(0, weight=1)

        self.tabview = customtkinter.CTkTabview(self.input_block, height=180)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tabview.add("Single Scan Mode")
        self.tabview.add("Batch Mode")
        self.tabview.tab("Single Scan Mode").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Batch Mode").grid_columnconfigure(0, weight=1)

        # Single Scan Mode Widgets
        self.single_scan_label = customtkinter.CTkLabel(self.tabview.tab("Single Scan Mode"), text="Select Single LAS/LAZ File:")
        self.single_scan_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
        
        self.single_file_frame = customtkinter.CTkFrame(self.tabview.tab("Single Scan Mode"), fg_color="transparent")
        self.single_file_frame.grid(row=1, column=0, sticky="ew")
        self.single_file_frame.grid_columnconfigure(0, weight=1)
        
        self.single_scan_file_entry = customtkinter.CTkEntry(self.single_file_frame, placeholder_text="No file selected")
        self.single_scan_file_entry.grid(row=0, column=0, padx=(5,5), pady=5, sticky="ew")
        self.single_scan_file_button = customtkinter.CTkButton(self.single_file_frame, text="Browse", width=70, command=lambda: self.browse_file(self.single_scan_file_entry, [("LAS/LAZ files", "*.las *.laz")]))
        self.single_scan_file_button.grid(row=0, column=1, padx=(0,5), pady=5)

        self.origin_label = customtkinter.CTkLabel(self.tabview.tab("Single Scan Mode"), text="Scanner Origin (X, Y, Z):")
        self.origin_label.grid(row=2, column=0, padx=5, pady=(10,0), sticky="w")
        
        self.coords_frame = customtkinter.CTkFrame(self.tabview.tab("Single Scan Mode"), fg_color="transparent")
        self.coords_frame.grid(row=3, column=0, sticky="ew")
        self.coords_frame.grid_columnconfigure((0,1,2), weight=1)
        self.origin_x_entry = customtkinter.CTkEntry(self.coords_frame, placeholder_text="0.0")
        self.origin_x_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.origin_y_entry = customtkinter.CTkEntry(self.coords_frame, placeholder_text="0.0")
        self.origin_y_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.origin_z_entry = customtkinter.CTkEntry(self.coords_frame, placeholder_text="0.0")
        self.origin_z_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Batch Mode Widgets
        self.batch_folder_label = customtkinter.CTkLabel(self.tabview.tab("Batch Mode"), text="Select Folder of LAS/LAZ Files:")
        self.batch_folder_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
        
        self.b_folder_frame = customtkinter.CTkFrame(self.tabview.tab("Batch Mode"), fg_color="transparent")
        self.b_folder_frame.grid(row=1, column=0, sticky="ew")
        self.b_folder_frame.grid_columnconfigure(0, weight=1)
        self.batch_folder_entry = customtkinter.CTkEntry(self.b_folder_frame, placeholder_text="No folder selected")
        self.batch_folder_entry.grid(row=0, column=0, padx=(5,5), pady=5, sticky="ew")
        self.batch_folder_button = customtkinter.CTkButton(self.b_folder_frame, text="Browse", width=70, command=lambda: self.browse_folder(self.batch_folder_entry))
        self.batch_folder_button.grid(row=0, column=1, padx=(0,5), pady=5)

        self.loc_csv_label = customtkinter.CTkLabel(self.tabview.tab("Batch Mode"), text="Select Camera -loc CSV File:")
        self.loc_csv_label.grid(row=2, column=0, padx=5, pady=(10,0), sticky="w")
        
        self.b_csv_frame = customtkinter.CTkFrame(self.tabview.tab("Batch Mode"), fg_color="transparent")
        self.b_csv_frame.grid(row=3, column=0, sticky="ew")
        self.b_csv_frame.grid_columnconfigure(0, weight=1)
        self.loc_csv_entry = customtkinter.CTkEntry(self.b_csv_frame, placeholder_text="No CSV selected")
        self.loc_csv_entry.grid(row=0, column=0, padx=(5,5), pady=5, sticky="ew")
        self.loc_csv_button = customtkinter.CTkButton(self.b_csv_frame, text="Browse", width=70, command=lambda: self.browse_file(self.loc_csv_entry, [("CSV files", "*.csv")]))
        self.loc_csv_button.grid(row=0, column=1, padx=(0,5), pady=5)

        # Output Directory (Applies to both modes)
        self.output_dir_label = customtkinter.CTkLabel(self.input_block, text="Master Output Directory:")
        self.output_dir_label.grid(row=1, column=0, padx=15, pady=(5,0), sticky="w")
        
        self.out_dir_frame = customtkinter.CTkFrame(self.input_block, fg_color="transparent")
        self.out_dir_frame.grid(row=2, column=0, padx=10, pady=(0,15), sticky="ew")
        self.out_dir_frame.grid_columnconfigure(0, weight=1)
        self.output_dir_entry = customtkinter.CTkEntry(self.out_dir_frame, placeholder_text="A new run folder will be created here")
        self.output_dir_entry.grid(row=0, column=0, padx=(5,5), pady=5, sticky="ew")
        self.output_dir_button = customtkinter.CTkButton(self.out_dir_frame, text="Browse", width=70, command=lambda: self.browse_folder(self.output_dir_entry))
        self.output_dir_button.grid(row=0, column=1, padx=(0,5), pady=5)


        # --- BLOCK 2: PARAMETERS ---
        self.parameter_frame = customtkinter.CTkFrame(self.main_container)
        self.parameter_frame.grid(row=1, column=0, pady=(5, 5), sticky="ew")
        self.parameter_frame.grid_columnconfigure((0,1), weight=1)

        param_title = customtkinter.CTkLabel(self.parameter_frame, text="Simulation Parameters", font=customtkinter.CTkFont(weight="bold"))
        param_title.grid(row=0, column=0, columnspan=2, pady=(10, 5))

        # Orientation
        self.orientation_label = customtkinter.CTkLabel(self.parameter_frame, text="Global Orientation (Pitch, Yaw, Roll):")
        self.orientation_label.grid(row=1, column=0, columnspan=2, padx=10, sticky="w")
        
        self.ori_frame = customtkinter.CTkFrame(self.parameter_frame, fg_color="transparent")
        self.ori_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.ori_frame.grid_columnconfigure((0,1,2), weight=1)
        self.ori_pitch_entry = customtkinter.CTkEntry(self.ori_frame, placeholder_text="0.0")
        self.ori_pitch_entry.grid(row=0, column=0, padx=(0,5), sticky="ew")
        self.ori_yaw_entry = customtkinter.CTkEntry(self.ori_frame, placeholder_text="0.0")
        self.ori_yaw_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.ori_roll_entry = customtkinter.CTkEntry(self.ori_frame, placeholder_text="0.0")
        self.ori_roll_entry.grid(row=0, column=2, padx=(5,0), sticky="ew")

        # Two-column grid for remaining parameters
        self.proj_label = customtkinter.CTkLabel(self.parameter_frame, text="Lens Projection:")
        self.proj_label.grid(row=3, column=0, padx=10, sticky="w")
        self.proj_optionmenu = customtkinter.CTkOptionMenu(self.parameter_frame, values=["eqa", "eqr", "ort", "rct", "str"])
        self.proj_optionmenu.set("eqa")
        self.proj_optionmenu.grid(row=4, column=0, padx=10, pady=(0,10), sticky="ew")

        self.grid_size_label = customtkinter.CTkLabel(self.parameter_frame, text="Grid Size (-orast):")
        self.grid_size_label.grid(row=3, column=1, padx=10, sticky="w")
        self.grid_size_entry = customtkinter.CTkEntry(self.parameter_frame, placeholder_text="180")
        self.grid_size_entry.grid(row=4, column=1, padx=10, pady=(0,10), sticky="ew")

        self.cam_height_label = customtkinter.CTkLabel(self.parameter_frame, text="Camera Height (-zCam):")
        self.cam_height_label.grid(row=5, column=0, padx=10, sticky="w")
        self.cam_height_entry = customtkinter.CTkEntry(self.parameter_frame, placeholder_text="0.0")
        self.cam_height_entry.grid(row=6, column=0, padx=10, pady=(0,10), sticky="ew")

        self.zenith_cutoff_label = customtkinter.CTkLabel(self.parameter_frame, text="Zenith Cutoff (-zenCut):")
        self.zenith_cutoff_label.grid(row=5, column=1, padx=10, sticky="w")
        self.zenith_cutoff_entry = customtkinter.CTkEntry(self.parameter_frame, placeholder_text="89")
        self.zenith_cutoff_entry.grid(row=6, column=1, padx=10, pady=(0,10), sticky="ew")

        self.max_dist_label = customtkinter.CTkLabel(self.parameter_frame, text="Max Distance (-maxdist):")
        self.max_dist_label.grid(row=7, column=0, padx=10, sticky="w")
        self.max_dist_entry = customtkinter.CTkEntry(self.parameter_frame, placeholder_text="1000")
        self.max_dist_entry.grid(row=8, column=0, padx=10, pady=(0,10), sticky="ew")

        self.inv_dist_weight_label = customtkinter.CTkLabel(self.parameter_frame, text="Inverse Dist Weight (-weight):")
        self.inv_dist_weight_label.grid(row=7, column=1, padx=10, sticky="w")
        self.inv_dist_weight_entry = customtkinter.CTkEntry(self.parameter_frame, placeholder_text="0.0")
        self.inv_dist_weight_entry.grid(row=8, column=1, padx=10, pady=(0,10), sticky="ew")

        self.log_checkbox = customtkinter.CTkCheckBox(self.parameter_frame, text="Log Scaling (-log)")
        self.log_checkbox.grid(row=9, column=0, padx=10, pady=(5,15), sticky="w")

        self.db_checkbox = customtkinter.CTkCheckBox(self.parameter_frame, text="Decibel Scaling (-db)")
        self.db_checkbox.grid(row=9, column=1, padx=10, pady=(5,15), sticky="w")


        # --- BLOCK 3: EXECUTION ---
        self.run_button = customtkinter.CTkButton(self.main_container, text="Generate Hemispherical Photos", height=40, font=customtkinter.CTkFont(weight="bold"), command=self.run_simulation)
        self.run_button.grid(row=2, column=0, pady=20, sticky="ew")


        # ==========================================
        # BUILD THE LOG CONSOLE (Bottom Pane)
        # ==========================================
        self.log_label = customtkinter.CTkLabel(self.log_frame, text="Process Console", font=customtkinter.CTkFont(weight="bold"))
        self.log_label.grid(row=0, column=0, padx=10, pady=(5,0), sticky="w")

        # Fixed height for the textbox so it acts like a terminal drawer
        self.log_textbox = customtkinter.CTkTextbox(self.log_frame, wrap="word", height=200, font=("Consolas", 12))
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(5,10), sticky="nsew")

        self.log_queue = queue.Queue()
        self.process_thread = None 
        
        self.update_log()


    # ==========================================
    # LOGIC & EXECUTION METHODS
    # ==========================================
    def _log_message(self, message):
        self.log_queue.put(message)

    def browse_file(self, entry_widget, filetypes):
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)

    def browse_folder(self, entry_widget):
        folderpath = filedialog.askdirectory()
        if folderpath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folderpath)

    def run_simulation(self):
        self._log_message("Initializing run...\n")
        current_mode = self.tabview.get()
        master_output_dir = self.output_dir_entry.get()

        if not master_output_dir or not os.path.isdir(master_output_dir):
            self._log_message("Error: Please select a valid Master Output Directory.\n")
            messagebox.showerror("Error", "Please select a valid Master Output Directory.")
            return

        target_files = []
        original_csv_path = None
        is_single_mode = False

        if current_mode == "Single Scan Mode":
            is_single_mode = True
            las_laz_file = self.single_scan_file_entry.get()
            if not las_laz_file or not (las_laz_file.lower().endswith(".las") or las_laz_file.lower().endswith(".laz")):
                self._log_message("Error: Please select a valid .las or .laz file.\n")
                return
            target_files.append(os.path.abspath(las_laz_file))

        elif current_mode == "Batch Mode":
            batch_folder = self.batch_folder_entry.get()
            original_csv_path = self.loc_csv_entry.get()

            if not batch_folder or not os.path.isdir(batch_folder):
                self._log_message("Error: Please select a valid Batch Folder.\n")
                return
            if not original_csv_path or not os.path.isfile(original_csv_path):
                self._log_message("Error: Please select a valid -loc CSV file.\n")
                return

            import glob
            las_files = glob.glob(os.path.join(batch_folder, "*.las"))
            laz_files = glob.glob(os.path.join(batch_folder, "*.laz"))
            target_files = las_files + laz_files
            
            if not target_files:
                self._log_message(f"Error: No .las or .laz files found in {batch_folder}\n")
                return

        base_command = ["lasPhotoCamSIM.exe"]
        
        pitch = self.ori_pitch_entry.get() or "0.0"
        yaw = self.ori_yaw_entry.get() or "0.0"
        roll = self.ori_roll_entry.get() or "0.0"
        base_command.extend(["-ori", pitch, yaw, roll])
        base_command.extend(["-proj", self.proj_optionmenu.get()])

        if self.grid_size_entry.get(): base_command.extend(["-orast", self.grid_size_entry.get()])
        if self.cam_height_entry.get(): base_command.extend(["-zCam", self.cam_height_entry.get()])
        if self.zenith_cutoff_entry.get(): base_command.extend(["-zenCut", self.zenith_cutoff_entry.get()])
        if self.max_dist_entry.get(): base_command.extend(["-maxdist", self.max_dist_entry.get()])
        if self.inv_dist_weight_entry.get(): base_command.extend(["-weight", self.inv_dist_weight_entry.get()])
        
        if self.log_checkbox.get(): base_command.append("-log")
        if self.db_checkbox.get(): base_command.append("-db")

        self.run_button.configure(state="disabled")

        self.process_thread = threading.Thread(
            target=self._execute_batch_loop, 
            args=(target_files, base_command, master_output_dir, is_single_mode, original_csv_path)
        )
        self.process_thread.start()


    def _execute_batch_loop(self, target_files, base_command, master_output_dir, is_single_mode, original_csv_path):
        total_files = len(target_files)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "Single_Scan" if is_single_mode else "Batch_Scan"
        run_dir = os.path.join(master_output_dir, f"{prefix}_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)
        self._log_message(f"Created dedicated run directory: {run_dir}\n")
        
        # Initialize the Master Summary CSV for this run
        master_csv_path = os.path.join(run_dir, "master_summary.csv")
        with open(master_csv_path, "w") as f:
            f.write("Scan Name,Gap Fraction (%)\n")
        
        for index, file_path in enumerate(target_files, 1):
            file_basename = os.path.basename(file_path)
            file_name_no_ext = os.path.splitext(file_basename)[0]
            
            self._log_message(f"\n--- Processing File {index} of {total_files}: {file_basename} ---\n")
            
            loop_csv_path = os.path.join(run_dir, f"{file_name_no_ext}.csv")
            
            if is_single_mode:
                try:
                    x = float(self.origin_x_entry.get() or 0.0)
                    y = float(self.origin_y_entry.get() or 0.0)
                    z = float(self.origin_z_entry.get() or 0.0)
                    with open(loop_csv_path, "w") as f:
                        f.write("X,Y,Z\n")
                        f.write(f"{x},{y},{z}\n")
                except ValueError:
                    self._log_message("Error: Coordinates must be numbers. Aborting loop.\n")
                    break
            else:
                shutil.copy(original_csv_path, loop_csv_path)
            
            cmd = base_command.copy()
            cmd.extend(["-i", f"\"{file_path}\"", "-loc", f"\"{loop_csv_path}\""])
            command_str = " ".join(cmd)
            
            gap_fraction = "N/A"
            
            try:
                process = subprocess.Popen(
                    command_str, 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    bufsize=1, 
                    universal_newlines=True
                )
                
                for line in process.stdout:
                    clean_line = line.replace('\b', '')
                    self._log_message(clean_line)
                    
                    # Snag the Gap Fraction directly from the console output
                    stripped_line = clean_line.strip()
                    if stripped_line:
                        try:
                            # The C++ tool prints the final gap fraction as a lone number on the last line
                            # If it successfully casts to a float, we save it as our fraction
                            float(stripped_line)
                            gap_fraction = stripped_line
                        except ValueError:
                            pass
                            
                process.wait()

                if process.returncode != 0:
                    self._log_message(f"\nCommand failed on {file_basename} with exit code {process.returncode}\n")
                else:
                    self._log_message(f"\nFinished C++ execution for {file_basename}.\n")
                    # Pass the successfully snagged gap fraction to the post-processor
                    self._post_process_and_cleanup(run_dir, loop_csv_path, file_name_no_ext, master_csv_path, gap_fraction)
                    
            except Exception as e:
                self._log_message(f"Error executing {file_basename}: {e}\n")
                
        self._log_message("\n=== ALL PROCESSING COMPLETE ===\n")
        self.after(0, lambda: self.run_button.configure(state="normal"))


    def _post_process_and_cleanup(self, run_dir, loop_csv_path, file_name_no_ext, master_csv_path, gap_fraction):
        self._log_message(f"Generating JPG for {file_name_no_ext}...\n")
        csv_basename = os.path.basename(loop_csv_path)
        
        asc_files = [f for f in os.listdir(run_dir) if f.endswith(".asc") and f.startswith(csv_basename)]
        
        for asc_file in asc_files:
            full_path = os.path.join(run_dir, asc_file)
            try:
                data = np.loadtxt(full_path, skiprows=6)
                binary_data = data > 0

                plt.imshow(binary_data, cmap="binary")
                plt.axis("off") 

                if len(asc_files) > 1:
                    clean_jpg_name = f"{file_name_no_ext}_plot{asc_files.index(asc_file)+1}.jpg"
                else:
                    clean_jpg_name = f"{file_name_no_ext}.jpg"
                    
                jpg_path = os.path.join(run_dir, clean_jpg_name)
                
                plt.savefig(jpg_path, bbox_inches="tight", pad_inches=0, dpi=300)
                plt.close() 
                self._log_message(f"Saved: {clean_jpg_name}\n")
                
                # I removed the os.remove(full_path) command here, so your .asc files are now safe!
                
            except Exception as e:
                self._log_message(f"Error processing {asc_file}: {e}\n")

        # Write the gap fraction to the master summary CSV
        with open(master_csv_path, "a") as f:
            f.write(f"{file_name_no_ext},{gap_fraction}\n")

        # Clean up the C++ tool's generated .out file so it doesn't clutter your directory
        out_csv_path = loop_csv_path + ".out"
        if os.path.exists(out_csv_path):
            os.remove(out_csv_path)

        # Delete the temporary 1-row CSV
        if os.path.exists(loop_csv_path):
            os.remove(loop_csv_path)

    def update_log(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_textbox.insert(tk.END, message)
            self.log_textbox.see(tk.END)
        self.after(100, self.update_log)

if __name__ == "__main__":
    app = App()
    app.mainloop()