import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import numpy as np
import pygimli as pg
from pygimli.physics import ert
import threading
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.tri as tri
from matplotlib.widgets import TextBox, Button, CheckButtons
from matplotlib.ticker import FuncFormatter
import webbrowser

class PolaresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PolaresInversion - Ultimate Edition")
        self.root.resizable(False, False)
        self.root.configure(bg="#F4F6F9")
        
        # --- SPLASH SCREEN (Schermata di Caricamento) ---
        self.root.withdraw() # Nasconde la finestra principale
        self.splash = tk.Toplevel(self.root)
        self.splash.overrideredirect(True)
        self.splash.configure(bg="#1E1E2E")
        
        # Centra lo splash screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 540, 320
        x, y = int(sw/2 - w/2), int(sh/2 - h/2)
        self.splash.geometry(f"{w}x{h}+{x}+{y}")
        
        tk.Label(self.splash, text="POLARES", font=("Segoe UI Black", 42), bg="#1E1E2E", fg="#89B4FA").pack(pady=(60, 0))
        tk.Label(self.splash, text="INVERSION", font=("Segoe UI", 20, "bold"), bg="#1E1E2E", fg="#F5E0DC").pack(pady=(0, 10))
        tk.Label(self.splash, text="Versione 3.0.0", font=("Segoe UI", 12), bg="#1E1E2E", fg="#A6ADC8").pack()
        
        tk.Label(self.splash, text="by Fabrizio Nori - InGeoLab s.r.l.", font=("Segoe UI", 10), bg="#1E1E2E", fg="#585B70").pack(side=tk.BOTTOM, pady=20)
        
        # --- VARIABILI LOGICHE ---
        self.filepath = None
        self.topo_filepath = None
        self.raw_data = None 
        self.mgr = None
        self.current_fig = None 
        
        self.inv_method = tk.StringVar(value="L2")
        self.lam_val = tk.DoubleVar(value=20.0)
        self.z_weight = tk.DoubleVar(value=1.0)
        self.max_depth = tk.DoubleVar(value=12.0)
        self.ip_enabled = tk.BooleanVar(value=False)
        self.ip_cutoff = tk.DoubleVar(value=0.5)

        self.mesh_cl = tk.DoubleVar(value=0.3)
        self.mesh_refine = tk.BooleanVar(value=False)
        self.mesh_quality = tk.DoubleVar(value=34.0)
        self.mesh_area = tk.DoubleVar(value=0.0) 
        self.plot_vmin = tk.DoubleVar(value=0.0) 
        self.plot_vmax = tk.DoubleVar(value=0.0) 

        # Esegue il passaggio alla GUI principale dopo 3 secondi
        self._build_main_gui()
        self.root.after(3000, self._close_splash_and_start)

    def _close_splash_and_start(self):
        self.splash.destroy()
        # Centra la finestra principale
        w, h = 480, 360
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x, y = int(sw/2 - w/2), int(sh/2 - h/2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.deiconify()

    def _build_main_gui(self):
        # --- BARRA DEI MENU ---
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Apri file dati POLARES (.dat)...", command=self.load_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salva Immagine Grafici (.png)", command=self.export_image, state="disabled")
        self.file_menu.add_command(label="Esporta Modello per QGIS (.vtk)", command=self.export_vtk, state="disabled")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Esci", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.edit_menu.add_command(label="Exterminate bad data points (Visivo)", command=self.filter_bad_data, state="disabled")
        self.edit_menu.add_command(label="Exclude data points in X range", command=self.exclude_range, state="disabled")
        self.edit_menu.add_command(label="Trim large data set (X min/max)", command=self.trim_data, state="disabled")
        self.edit_menu.add_command(label="Reverse pseudosection (Capovolgi X)", command=self.reverse_data, state="disabled")
        self.edit_menu.add_command(label="Change first electrode location (Shift X)", command=self.change_start_pos, state="disabled")
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)

        self.topo_menu = tk.Menu(self.menubar, tearoff=0)
        self.topo_menu.add_command(label="Load topography data (X Z)...", command=self.load_topo)
        self.topo_menu.add_command(label="Clear topography", command=self.clear_topo)
        self.menubar.add_cascade(label="Topography", menu=self.topo_menu)

        self.inv_menu = tk.Menu(self.menubar, tearoff=0)
        self.inv_menu.add_command(label="Inversion methods and settings...", command=self.open_settings)
        self.inv_menu.add_separator()
        self.inv_menu.add_radiobutton(label="Smoothness-constrained (L2)", variable=self.inv_method, value="L2")
        self.inv_menu.add_radiobutton(label="Robust / Blocky (L1)", variable=self.inv_method, value="L1")
        self.menubar.add_cascade(label="Inversion", menu=self.inv_menu)

        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.tools_menu.add_command(label="Mostra grafici a 3 pannelli", command=self.show_custom_plots, state="disabled")
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="Estrai Profilo Stratigrafico (Sezione 1D)...", command=self.extract_1d_section, state="disabled")
        self.menubar.add_cascade(label="Display & Tools", menu=self.tools_menu)

        self.info_menu = tk.Menu(self.menubar, tearoff=0)
        self.info_menu.add_command(label="About PolaresInversion...", command=self.show_about)
        self.menubar.add_cascade(label="Info", menu=self.info_menu)

        # --- AREA DI LAVORO PRINCIPALE ---
        main_frame = tk.Frame(self.root, bg="#F4F6F9")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=25)

        tk.Label(main_frame, text="Area di Lavoro", font=("Segoe UI", 16, "bold"), bg="#F4F6F9", fg="#2C3E50").pack(pady=(0, 20))

        self.btn_load = tk.Button(main_frame, text="📁 1. Seleziona file .dat", command=self.load_file, 
                                  bg="#3B82F6", fg="white", font=("Segoe UI", 11, "bold"), 
                                  relief="flat", cursor="hand2", pady=8, activebackground="#2563EB", activeforeground="white")
        self.btn_load.pack(fill=tk.X, pady=(0, 5))
        
        self.lbl_file = tk.Label(main_frame, text="Nessun file selezionato", font=("Segoe UI", 9, "italic"), bg="#F4F6F9", fg="#7F8C8D")
        self.lbl_file.pack(pady=(0, 5))
        
        self.lbl_topo = tk.Label(main_frame, text="Topografia: Nessuna", font=("Segoe UI", 9), bg="#F4F6F9", fg="#7F8C8D")
        self.lbl_topo.pack(pady=(0, 20))

        self.btn_run = tk.Button(main_frame, text="⚙️ 2. Esegui Inversione", command=self.run_inversion_thread, 
                                 state="disabled", bg="#9CA3AF", fg="white", font=("Segoe UI", 11, "bold"), 
                                 relief="flat", pady=8, activebackground="#059669", activeforeground="white")
        self.btn_run.pack(fill=tk.X, pady=(0, 10))

        self.lbl_status = tk.Label(main_frame, text="In attesa dei dati...", font=("Segoe UI", 10, "bold"), bg="#F4F6F9", fg="#9CA3AF")
        self.lbl_status.pack()

    # --- ABOUT ---
    def show_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title("About PolaresInversion")
        about_win.geometry("420x360")
        about_win.configure(bg="#F4F6F9")
        
        tk.Label(about_win, text="POLARES", font=("Segoe UI Black", 24), bg="#F4F6F9", fg="#3B82F6").pack(pady=(25, 0))
        tk.Label(about_win, text="INVERSION", font=("Segoe UI", 16, "bold"), bg="#F4F6F9", fg="#2C3E50").pack(pady=(0, 5))
        tk.Label(about_win, text="Versione 3.0.0", font=("Segoe UI", 11), bg="#F4F6F9", fg="#7F8C8D").pack(pady=(0, 15))
        
        tk.Label(about_win, text="Librerie Open Source:", font=("Segoe UI", 10, "bold"), bg="#F4F6F9").pack()
        libs_text = "Python 3 • pyGIMLi (Core FEM)\nMatplotlib & NumPy • Tkinter"
        tk.Label(about_win, text=libs_text, font=("Segoe UI", 10), bg="#F4F6F9", fg="#34495E").pack(pady=5)
        
        tk.Label(about_win, text="Sviluppato da:", font=("Segoe UI", 10, "bold"), bg="#F4F6F9").pack(pady=(15, 0))
        tk.Label(about_win, text="Fabrizio Nori - InGeoLab s.r.l.", font=("Segoe UI", 10, "italic"), bg="#F4F6F9", fg="#2C3E50").pack()
        
        link = "https://github.com/FNX996"
        link_lbl = tk.Label(about_win, text=f"GitHub: {link}", font=("Segoe UI", 10, "underline"), bg="#F4F6F9", fg="#3B82F6", cursor="hand2")
        link_lbl.pack(pady=10)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open_new(link))
        
        tk.Button(about_win, text="Chiudi", command=about_win.destroy, width=15, bg="#9CA3AF", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", pady=5).pack(pady=10)

    # --- IMPOSTAZIONI ---
    def open_settings(self):
        popup = tk.Toplevel(self.root)
        popup.title("Impostazioni Avanzate")
        popup.geometry("450x490")
        popup.configure(bg="#F4F6F9")
        
        tk.Label(popup, text="Impostazioni Inversione & Mesh", font=("Segoe UI", 14, "bold"), bg="#F4F6F9", fg="#2C3E50").grid(row=0, column=0, columnspan=2, pady=(15, 15))
        
        lbl_font = ("Segoe UI", 10)
        entry_kwargs = {"width": 14, "font": ("Segoe UI", 10)}
        
        tk.Label(popup, text="Lambda (Damping):", font=lbl_font, bg="#F4F6F9").grid(row=1, column=0, padx=30, pady=6, sticky="w")
        e_lam = ttk.Entry(popup, **entry_kwargs); e_lam.insert(0, str(self.lam_val.get())); e_lam.grid(row=1, column=1)
        
        tk.Label(popup, text="Z-Weight (Anisotropy):", font=lbl_font, bg="#F4F6F9").grid(row=2, column=0, padx=30, pady=6, sticky="w")
        e_z = ttk.Entry(popup, **entry_kwargs); e_z.insert(0, str(self.z_weight.get())); e_z.grid(row=2, column=1)
        
        tk.Label(popup, text="Max Depth / Profondità (m):", font=lbl_font, bg="#F4F6F9").grid(row=3, column=0, padx=30, pady=6, sticky="w")
        e_dep = ttk.Entry(popup, **entry_kwargs); e_dep.insert(0, str(self.max_depth.get())); e_dep.grid(row=3, column=1)

        tk.Label(popup, text="Char Length (Fine<0.1-1.0>Coarse):", font=lbl_font, bg="#F4F6F9").grid(row=4, column=0, padx=30, pady=6, sticky="w")
        e_cl = ttk.Entry(popup, **entry_kwargs); e_cl.insert(0, str(self.mesh_cl.get())); e_cl.grid(row=4, column=1)
        
        tk.Label(popup, text="Mesh Quality (es. 34.0):", font=lbl_font, bg="#F4F6F9").grid(row=5, column=0, padx=30, pady=6, sticky="w")
        e_mq = ttk.Entry(popup, **entry_kwargs); e_mq.insert(0, str(self.mesh_quality.get())); e_mq.grid(row=5, column=1)

        tk.Label(popup, text="Mesh Max Area (0=Auto):", font=lbl_font, bg="#F4F6F9").grid(row=6, column=0, padx=30, pady=6, sticky="w")
        e_ma = ttk.Entry(popup, **entry_kwargs); e_ma.insert(0, str(self.mesh_area.get())); e_ma.grid(row=6, column=1)

        tk.Label(popup, text="Plot Resistivity MIN (0=Auto):", font=lbl_font, bg="#F4F6F9").grid(row=7, column=0, padx=30, pady=6, sticky="w")
        e_vmin = ttk.Entry(popup, **entry_kwargs); e_vmin.insert(0, str(self.plot_vmin.get())); e_vmin.grid(row=7, column=1)

        tk.Label(popup, text="Plot Resistivity MAX (0=Auto):", font=lbl_font, bg="#F4F6F9").grid(row=8, column=0, padx=30, pady=6, sticky="w")
        e_vmax = ttk.Entry(popup, **entry_kwargs); e_vmax.insert(0, str(self.plot_vmax.get())); e_vmax.grid(row=8, column=1)

        chk_refine = tk.Checkbutton(popup, text="Refine Mesh (Affina i bordi)", variable=self.mesh_refine, font=lbl_font, bg="#F4F6F9", activebackground="#F4F6F9", cursor="hand2")
        chk_refine.grid(row=9, column=0, columnspan=2, pady=10)
        
        def save():
            try: 
                self.lam_val.set(float(e_lam.get()))
                self.z_weight.set(float(e_z.get()))
                self.max_depth.set(float(e_dep.get()))
                self.mesh_cl.set(float(e_cl.get()))
                self.mesh_quality.set(float(e_mq.get()))
                self.mesh_area.set(float(e_ma.get()))
                self.plot_vmin.set(float(e_vmin.get()))
                self.plot_vmax.set(float(e_vmax.get()))
                popup.destroy()
            except: pass
            
        tk.Button(popup, text="Salva Impostazioni", command=save, width=20, bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", pady=6).grid(row=10, column=0, columnspan=2, pady=15)

    def set_ip_cutoff(self):
        val = simpledialog.askfloat("I.P. Cutoff", "Minimo valore di I.P. (mV/V) accettabile:", initialvalue=self.ip_cutoff.get())
        if val is not None: self.ip_cutoff.set(val)

    # --- LETTURA DATI & TOPOGRAFIA ---
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("File POLARES", "*.dat"), ("Tutti i file", "*.*")])
        if file_path:
            self.filepath = file_path
            self.lbl_file.config(text=self.filepath.split('/')[-1], fg="#34495E")
            try:
                self.raw_data = self.parse_dat_file()
                self.btn_run.config(state="normal", bg="#10B981", cursor="hand2")
                for i in range(5): self.edit_menu.entryconfig(i, state="normal") 
                self.lbl_status.config(text=f"Dati: {self.raw_data.size()} misure pronte.", fg="#10B981")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def parse_dat_file(self):
        a_x, b_x, m_x, n_x, rhoa = [], [], [], [], []
        with open(self.filepath, 'r') as f:
            for line in f:
                line = line.strip().replace(',', '.')
                parts = line.split()
                if len(parts) == 10 and parts[0] == '4':
                    try:
                        val_rho = float(parts[9])
                        if val_rho <= 0: continue
                        a_x.append(float(parts[1])); b_x.append(float(parts[3]))
                        m_x.append(float(parts[5])); n_x.append(float(parts[7]))
                        rhoa.append(val_rho)
                    except: continue
        if not rhoa: raise ValueError("Nessun dato valido.")
        all_electrodes = np.unique(np.concatenate((a_x, b_x, m_x, n_x)))
        data = pg.DataContainerERT()
        for pos in all_electrodes: data.createSensor([pos, 0.0, 0.0])
        pos_to_idx = {pos: i for i, pos in enumerate(all_electrodes)}
        data.resize(len(rhoa))
        data.set('a', [pos_to_idx[x] for x in a_x])
        data.set('b', [pos_to_idx[x] for x in b_x])
        data.set('m', [pos_to_idx[x] for x in m_x])
        data.set('n', [pos_to_idx[x] for x in n_x])
        data.set('rhoa', rhoa)
        data.set('k', ert.geometricFactors(data))
        data.set('err', ert.estimateError(data, relativeError=0.03, absoluteUError=0.001))
        return data

    def load_topo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Testo (X Z)", "*.txt *.csv"), ("Tutti", "*.*")])
        if file_path:
            self.topo_filepath = file_path
            self.lbl_topo.config(text=f"Topografia: {file_path.split('/')[-1]}", fg="#10B981")
            
    def clear_topo(self):
        self.topo_filepath = None
        self.lbl_topo.config(text="Topografia: Nessuna", fg="#7F8C8D")

    # --- FUNZIONI EDIT ---
    def reverse_data(self):
        if not self.raw_data: return
        max_x = max([self.raw_data.sensorPosition(i)[0] for i in range(self.raw_data.sensorCount())])
        for i in range(self.raw_data.sensorCount()):
            pos = self.raw_data.sensorPosition(i)
            self.raw_data.setSensorPosition(i, [max_x - pos[0], pos[1], pos[2]])
        self.raw_data.set('k', ert.geometricFactors(self.raw_data))
        self.lbl_status.config(text="Sezione specchiata (Reverse). Pronta da invertire.", fg="#F59E0B")
        messagebox.showinfo("Reverse", "La geometria della stesa è stata capovolta.")

    def change_start_pos(self):
        if not self.raw_data: return
        offset = simpledialog.askfloat("Shift X", "Metri da sommare alla coordinata X di partenza:")
        if offset is not None:
            for i in range(self.raw_data.sensorCount()):
                pos = self.raw_data.sensorPosition(i)
                self.raw_data.setSensorPosition(i, [pos[0] + offset, pos[1], pos[2]])
            self.lbl_status.config(text=f"X Shiftata di {offset}m", fg="#F59E0B")

    def trim_data(self):
        if not self.raw_data: return
        xmin = simpledialog.askfloat("Trim", "Mantieni dati con X maggiore di:")
        xmax = simpledialog.askfloat("Trim", "Mantieni dati con X minore di:")
        if xmin is not None and xmax is not None:
            self._filter_by_x(xmin, xmax, keep_inside=True)

    def exclude_range(self):
        if not self.raw_data: return
        xmin = simpledialog.askfloat("Exclude", "Elimina dati tra X minimo:")
        xmax = simpledialog.askfloat("Exclude", "e X massimo:")
        if xmin is not None and xmax is not None:
            self._filter_by_x(xmin, xmax, keep_inside=False)

    def _filter_by_x(self, xmin, xmax, keep_inside):
        invalid = []
        for i in range(self.raw_data.size()):
            a, b, m, n = [self.raw_data.sensorPosition(self.raw_data(key)[i])[0] for key in ['a', 'b', 'm', 'n']]
            center = (a + b + m + n) / 4.0
            in_range = (xmin <= center <= xmax)
            if (keep_inside and not in_range) or (not keep_inside and in_range):
                invalid.append(i)
        if invalid:
            self.raw_data.markInvalid(invalid)
            self.raw_data.removeInvalid()
            self.lbl_status.config(text=f"Filtraggio applicato. {self.raw_data.size()} dati rimasti.", fg="#F59E0B")
            messagebox.showinfo("Completato", f"Rimossi {len(invalid)} punti dalla pseudosezione.")

    def filter_bad_data(self):
        if not self.raw_data: return
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.canvas.manager.set_window_title('Seleziona punti anomali')
        x_centers, z_pseudo = [], []
        for i in range(self.raw_data.size()):
            a,b,m,n = [self.raw_data.sensorPosition(self.raw_data(k)[i])[0] for k in ['a','b','m','n']]
            x_centers.append((a+b+m+n)/4.0)
            z_pseudo.append(max(abs(a-b), abs(a-m), abs(a-n), abs(b-m), abs(b-n), abs(m-n)) * 0.25)
            
        sc = ax.scatter(x_centers, z_pseudo, c=self.raw_data('rhoa'), cmap='seismic', norm=LogNorm(), s=50, picker=True)
        ax.invert_yaxis()
        ax.set_title("Clicca sui punti spuri per rimuoverli. Chiudi la finestra per salvare.")
        fig.colorbar(sc, ax=ax, label="Apparent Resistivity (Ohm.m)")
        
        to_remove = set()
        def on_pick(event):
            ind = event.ind[0]
            to_remove.add(ind)
            sc._offsets.data[ind] = [np.nan, np.nan]
            fig.canvas.draw_idle()
        fig.canvas.mpl_connect('pick_event', on_pick)
        plt.show()
        
        if to_remove:
            self.raw_data.markInvalid(list(to_remove))
            self.raw_data.removeInvalid()
            self.lbl_status.config(text=f"Rimossi {len(to_remove)} punti visivamente.", fg="#F59E0B")

    # --- INVERSIONE ---
    def run_inversion_thread(self):
        if not self.raw_data: return
        self.btn_run.config(state="disabled", bg="#9CA3AF", cursor="arrow")
        method = "Robust (L1)" if self.inv_method.get() == "L1" else "Smooth (L2)"
        self.lbl_status.config(text=f"Calcolo in corso ({method})...", fg="#F59E0B")
        threading.Thread(target=self.process_inversion, daemon=True).start()

    def process_inversion(self):
        try:
            is_robust = (self.inv_method.get() == "L1")
            max_d = self.max_depth.get() 
            para_dx = self.mesh_cl.get()
            
            base_quality = self.mesh_quality.get()
            quality = base_quality + 0.5 if self.mesh_refine.get() else base_quality
            
            if self.topo_filepath:
                topo_data = np.loadtxt(self.topo_filepath)
                topo_data = topo_data[topo_data[:, 0].argsort()]
                for i in range(self.raw_data.sensorCount()):
                    pos = self.raw_data.sensorPosition(i)
                    z_val = np.interp(pos[0], topo_data[:, 0], topo_data[:, 1]) 
                    self.raw_data.setSensorPosition(i, [pos[0], z_val, pos[2]])

            self.mgr = ert.ERTManager(self.raw_data)
            
            inv_kwargs = {
                'lam': self.lam_val.get(),
                'zWeight': self.z_weight.get(),
                'robustData': is_robust,
                'blockyModel': is_robust,
                'paraDepth': max_d,
                'paraDX': para_dx,
                'quality': quality,
                'maxIter': 10,
                'verbose': False
            }
            
            if self.mesh_area.get() > 0:
                inv_kwargs['paraMaxCellSize'] = self.mesh_area.get()
                
            self.mgr.invert(**inv_kwargs)
            
            self.current_response = self.mgr.inv.response
            self.root.after(0, self.on_inversion_complete)
        except Exception as e:
            self.root.after(0, self.on_inversion_error, str(e))

    def on_inversion_complete(self):
        self.lbl_status.config(text="Inversione completata!", fg="#10B981")
        self.btn_run.config(state="normal", bg="#10B981", cursor="hand2")
        self.file_menu.entryconfig("Salva Immagine Grafici (.png)", state="normal")
        self.file_menu.entryconfig("Esporta Modello per QGIS (.vtk)", state="normal")
        self.tools_menu.entryconfig("Mostra grafici a 3 pannelli", state="normal")
        self.tools_menu.entryconfig("Estrai Profilo Stratigrafico (Sezione 1D)...", state="normal")
        self.show_custom_plots()

    def on_inversion_error(self, error_msg):
        self.btn_run.config(state="normal", bg="#10B981", cursor="hand2")
        self.lbl_status.config(text="Errore durante l'inversione.", fg="#EF4444")
        messagebox.showerror("Errore", error_msg)

    def extract_1d_section(self):
        if not self.mgr: return
        x_val = simpledialog.askfloat("Sezione 1D", "Inserisci la coordinata X (metri) dove estrarre la colonna virtuale:")
        if x_val is not None:
            min_z = min([pos[1] for pos in self.mgr.paraDomain.positions()])
            z_vals = np.linspace(0, min_z, 50) 
            points = [[x_val, z] for z in z_vals]
            
            rho_1d = pg.interpolate(self.mgr.paraDomain, self.mgr.model, points)
            
            plt.figure(figsize=(4, 7))
            plt.plot(rho_1d, abs(z_vals), 'b-', linewidth=2.5, marker='o', markersize=4)
            plt.xlabel("Real Resistivity (Ohm.m)")
            plt.ylabel("Depth (m)")
            plt.title(f"Vertical Profile at X = {x_val}m")
            plt.gca().invert_yaxis()
            plt.grid(True, which="both", ls="--", alpha=0.5)
            plt.xscale('log')
            plt.show()

    # --- MOTORE GRAFICO STILE RESIPY ---
    def show_custom_plots(self):
        if not self.mgr: return
        plt.close('all')
        
        fig = plt.figure(figsize=(14, 10))
        fig.canvas.manager.set_window_title('Risultati Inversione (Stile ResIPy)')
        self.current_fig = fig
        
        ax1 = fig.add_axes([0.08, 0.70, 0.75, 0.22])
        ax2 = fig.add_axes([0.08, 0.42, 0.75, 0.22], sharex=ax1)
        ax3 = fig.add_axes([0.08, 0.14, 0.75, 0.22], sharex=ax1)
        cbar_ax = fig.add_axes([0.86, 0.14, 0.02, 0.78]) 
        
        data = self.mgr.data
        x_centers, z_pseudo = [], []
        for i in range(data.size()):
            a, b, m, n = [data.sensorPosition(data(k)[i])[0] for k in ['a','b','m','n']]
            x_centers.append((a+b+m+n)/4.0)
            z_pseudo.append(max(abs(a-b), abs(a-m), abs(a-n), abs(b-m), abs(b-n), abs(m-n)) * 0.25)

        rhoa_m = np.array(data('rhoa'))
        try: rhoa_c = np.array(self.mgr.inv.response)
        except: rhoa_c = rhoa_m
        model_rho = np.array(self.mgr.model)
        
        all_vals = np.concatenate((rhoa_m, rhoa_c, model_rho))
        init_min = np.percentile(all_vals, 2)
        init_max = np.percentile(all_vals, 98)
        if init_min <= 0: init_min = np.min(all_vals[all_vals > 0])

        mesh = self.mgr.paraDomain
        node_x = np.array([n.pos()[0] for n in mesh.nodes()])
        node_z = np.array([n.pos()[1] for n in mesh.nodes()])
        node_rho = np.array(pg.interpolate(mesh, model_rho, mesh.positions()))
        
        triang_pseudo = tri.Triangulation(x_centers, z_pseudo)
        triang_model = tri.Triangulation(node_x, node_z)
        
        x_min_data = np.min([data.sensorPosition(i)[0] for i in range(data.sensorCount())])
        x_max_data = np.max([data.sensorPosition(i)[0] for i in range(data.sensorCount())])

        ax_vmin = fig.add_axes([0.15, 0.03, 0.1, 0.04])
        txt_vmin = TextBox(ax_vmin, 'Min Rho: ', initial=f"{init_min:.1f}")

        ax_vmax = fig.add_axes([0.35, 0.03, 0.1, 0.04])
        txt_vmax = TextBox(ax_vmax, 'Max Rho: ', initial=f"{init_max:.1f}")

        ax_btn = fig.add_axes([0.48, 0.03, 0.08, 0.04])
        btn_apply = Button(ax_btn, 'Apply')

        ax_chk = fig.add_axes([0.60, 0.01, 0.23, 0.08])
        chk = CheckButtons(ax_chk, ['Contour Lines', 'Crop Corners'], [True, False])

        fig.widgets = [txt_vmin, txt_vmax, btn_apply, chk]

        def draw_all(event=None):
            try:
                v_min = float(txt_vmin.text)
                v_max = float(txt_vmax.text)
            except ValueError:
                v_min, v_max = init_min, init_max
                
            if v_min >= v_max: v_max = v_min + 1.0
            
            show_contour = chk.get_status()[0]
            crop_corners = chk.get_status()[1]

            ax1.clear(); ax2.clear(); ax3.clear(); cbar_ax.clear()

            res_cmap = plt.get_cmap('seismic')
            norm = LogNorm(vmin=v_min, vmax=v_max)
            
            if crop_corners:
                depth = -triang_model.y
                mask = (triang_model.x < x_min_data + depth) | (triang_model.x > x_max_data - depth)
                tmask = np.any(mask[triang_model.triangles], axis=1)
                triang_model.set_mask(tmask)
            else:
                triang_model.set_mask(None)

            if show_contour:
                levels = np.logspace(np.log10(v_min), np.log10(v_max), 20)
                tc = ax1.tricontourf(triang_pseudo, rhoa_m, levels=levels, cmap=res_cmap, norm=norm, extend='both')
                ax2.tricontourf(triang_pseudo, rhoa_c, levels=levels, cmap=res_cmap, norm=norm, extend='both')
                ax3.tricontourf(triang_model, node_rho, levels=levels, cmap=res_cmap, norm=norm, extend='both')
            else:
                tc = ax1.tripcolor(triang_pseudo, rhoa_m, cmap=res_cmap, norm=norm, shading='gouraud')
                ax2.tripcolor(triang_pseudo, rhoa_c, cmap=res_cmap, norm=norm, shading='gouraud')
                ax3.tripcolor(triang_model, node_rho, cmap=res_cmap, norm=norm, shading='gouraud')

            max_d = self.max_depth.get()
            ax1.invert_yaxis()
            ax1.set_ylim(bottom=max_d, top=0)
            ax1.set_title("1. Measured Apparent Resistivity", fontsize=11)
            ax1.set_ylabel("Ps. Depth (m)")
            
            ax2.invert_yaxis()
            ax2.set_ylim(bottom=max_d, top=0)
            ax2.set_title("2. Calculated Apparent Resistivity", fontsize=11)
            ax2.set_ylabel("Ps. Depth (m)")
            
            if not self.topo_filepath:
                ax3.set_ylim(bottom=-max_d, top=0)
            ax3.set_title("3. Inverse Model Resistivity Section", fontsize=11)
            ax3.set_ylabel("Depth (m)")
            ax3.set_xlabel("Distance X (m)")

            for ax in [ax1, ax2, ax3]: ax.set_aspect('auto')

            def res_fmt(x, pos):
                return f"{int(x)}" if x >= 10 else f"{x:.2f}"
            
            fmt = FuncFormatter(res_fmt)
            cbar = fig.colorbar(tc, cax=cbar_ax, orientation='vertical', format=fmt)
            cbar.set_label("Resistivity (ohm.m)", fontsize=11)
            
            fig.canvas.draw_idle()

        btn_apply.on_clicked(draw_all)
        chk.on_clicked(draw_all)

        draw_all()
        plt.show()

    def export_image(self):
        if not self.mgr: return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if file_path:
            if self.current_fig:
                for w in self.current_fig.widgets:
                    if hasattr(w, 'ax'): w.ax.set_visible(False)
                self.current_fig.savefig(file_path, dpi=300, bbox_inches='tight')
                for w in self.current_fig.widgets:
                    if hasattr(w, 'ax'): w.ax.set_visible(True)
                messagebox.showinfo("Salvato", "Immagine salvata con successo!")

    def export_vtk(self):
        if not self.mgr: return
        file_path = filedialog.asksaveasfilename(defaultextension=".vtk", filetypes=[("VTK", "*.vtk")])
        if file_path: self.mgr.exportVTK(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = PolaresApp(root)
    root.mainloop()
