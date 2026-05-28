import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import numpy as np
import pygimli as pg
from pygimli.physics import ert
import threading
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.tri as tri
from matplotlib.widgets import TextBox, Button, CheckButtons
from matplotlib.ticker import FuncFormatter  # Aggiunto per formattare i numeri della colorbar
import webbrowser

class PolaresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inversione Geoelettrica POLARES 32 - Ultimate Edition")
        self.root.geometry("450x280")
        self.root.resizable(False, False)
        
        self.filepath = None
        self.topo_filepath = None
        self.raw_data = None 
        self.mgr = None
        
        # Variabili di inversione e IP
        self.inv_method = tk.StringVar(value="L2")
        self.lam_val = tk.DoubleVar(value=20.0)
        self.z_weight = tk.DoubleVar(value=1.0)
        self.max_depth = tk.DoubleVar(value=12.0)
        self.ip_enabled = tk.BooleanVar(value=False)
        self.ip_cutoff = tk.DoubleVar(value=0.5)

        # Nuove variabili Mesh stile ResIPy
        self.mesh_cl = tk.DoubleVar(value=0.3) # Characteristic Length (paraDX)
        self.mesh_refine = tk.BooleanVar(value=False) # Refine Mesh

        # --- BARRA DEI MENU ---
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # 1. File
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Apri file dati POLARES (.dat)...", command=self.load_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salva Immagine Grafici (.png)", command=self.export_image, state="disabled")
        self.file_menu.add_command(label="Esporta Modello per QGIS (.vtk)", command=self.export_vtk, state="disabled")
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # 2. Edit
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.edit_menu.add_command(label="Exterminate bad data points (Visivo)", command=self.filter_bad_data, state="disabled")
        self.edit_menu.add_command(label="Exclude data points in X range", command=self.exclude_range, state="disabled")
        self.edit_menu.add_command(label="Trim large data set (X min/max)", command=self.trim_data, state="disabled")
        self.edit_menu.add_command(label="Reverse pseudosection (Capovolgi X)", command=self.reverse_data, state="disabled")
        self.edit_menu.add_command(label="Change first electrode location (Shift X)", command=self.change_start_pos, state="disabled")
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)

        # 3. Topography
        self.topo_menu = tk.Menu(self.menubar, tearoff=0)
        self.topo_menu.add_command(label="Load topography data (X Z)...", command=self.load_topo)
        self.topo_menu.add_command(label="Clear topography", command=self.clear_topo)
        self.menubar.add_cascade(label="Topography", menu=self.topo_menu)

        # 4. Inversion & IP
        self.inv_menu = tk.Menu(self.menubar, tearoff=0)
        self.inv_menu.add_command(label="Inversion methods and settings...", command=self.open_settings)
        
        self.ip_menu = tk.Menu(self.inv_menu, tearoff=0)
        self.ip_menu.add_checkbutton(label="Enable I.P. Inversion (Chargeability)", variable=self.ip_enabled)
        self.ip_menu.add_command(label="Cutoff for valid I.P. values...", command=self.set_ip_cutoff)
        self.inv_menu.add_cascade(label="I.P. options", menu=self.ip_menu)
        
        self.inv_menu.add_separator()
        self.inv_menu.add_radiobutton(label="Smoothness-constrained (L2)", variable=self.inv_method, value="L2")
        self.inv_menu.add_radiobutton(label="Robust / Blocky (L1)", variable=self.inv_method, value="L1")
        self.menubar.add_cascade(label="Inversion", menu=self.inv_menu)

        # 5. Tools & Display
        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.tools_menu.add_command(label="Mostra grafici a 3 pannelli", command=self.show_custom_plots, state="disabled")
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="Estrai Profilo Stratigrafico (Sezione 1D)...", command=self.extract_1d_section, state="disabled")
        self.menubar.add_cascade(label="Display & Tools", menu=self.tools_menu)

        # 6. Info
        self.info_menu = tk.Menu(self.menubar, tearoff=0)
        self.info_menu.add_command(label="About PolaresInversion...", command=self.show_about)
        self.menubar.add_cascade(label="Info", menu=self.info_menu)

        # --- INTERFACCIA ---
        self.btn_load = tk.Button(self.root, text="1. Seleziona file .dat", command=self.load_file, width=25, font=("Arial", 10, "bold"))
        self.btn_load.pack(pady=15)
        self.lbl_file = tk.Label(self.root, text="Nessun file selezionato", fg="gray")
        self.lbl_file.pack()
        self.lbl_topo = tk.Label(self.root, text="Topografia: Nessuna", fg="gray")
        self.lbl_topo.pack()
        self.btn_run = tk.Button(self.root, text="2. Esegui Inversione", command=self.run_inversion_thread, state="disabled", width=25, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.btn_run.pack(pady=15)
        self.lbl_status = tk.Label(self.root, text="", fg="blue")
        self.lbl_status.pack()
        
        self.current_fig = None # Per mantenere vivi i widget matplotlib

    # --- ABOUT ---
    def show_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title("About")
        about_win.geometry("400x300")
        
        tk.Label(about_win, text="PolaresInversion", font=("Arial", 14, "bold")).pack(pady=(15, 0))
        tk.Label(about_win, text="by Fabrizio Nori - InGeoLab s.r.l.", font=("Arial", 11, "italic")).pack(pady=(0, 5))
        tk.Label(about_win, text="Versione 2.5.0", font=("Arial", 10)).pack(pady=(0, 10))
        
        tk.Label(about_win, text="Librerie Open Source Utilizzate:", font=("Arial", 9, "bold")).pack()
        libs_text = "• Python 3\n• pyGIMLi (Core FEM)\n• Matplotlib & NumPy (Grafica e Matrici)\n• Tkinter (Interfaccia GUI)"
        tk.Label(about_win, text=libs_text, font=("Arial", 9), justify="left").pack(pady=5)
        
        link_lbl = tk.Label(about_win, text="GitHub: https://github.com/FNX996", font=("Arial", 10, "underline"), fg="blue", cursor="hand2")
        link_lbl.pack(pady=10)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/FNX996"))
        
        tk.Button(about_win, text="Chiudi", command=about_win.destroy, width=15).pack(pady=5)

    # --- FUNZIONI IMPOSTAZIONI VIA MENU ---
    def open_settings(self):
        popup = tk.Toplevel(self.root)
        popup.title("Inversion & Mesh Settings")
        popup.geometry("380x280")
        
        tk.Label(popup, text="Lambda (Damping):").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        e_lam = tk.Entry(popup, width=12); e_lam.insert(0, str(self.lam_val.get())); e_lam.grid(row=0, column=1)
        
        tk.Label(popup, text="Z-Weight (Anisotropy):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        e_z = tk.Entry(popup, width=12); e_z.insert(0, str(self.z_weight.get())); e_z.grid(row=1, column=1)
        
        tk.Label(popup, text="Max Depth / Profondità (m):").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        e_dep = tk.Entry(popup, width=12); e_dep.insert(0, str(self.max_depth.get())); e_dep.grid(row=2, column=1)

        tk.Label(popup, text="Char Length (Fine<0.1 - 1.0>Coarse):").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        e_cl = tk.Entry(popup, width=12); e_cl.insert(0, str(self.mesh_cl.get())); e_cl.grid(row=3, column=1)

        chk_refine = tk.Checkbutton(popup, text="Refine Mesh", variable=self.mesh_refine)
        chk_refine.grid(row=4, column=0, columnspan=2, pady=5)
        
        def save():
            try: 
                self.lam_val.set(float(e_lam.get()))
                self.z_weight.set(float(e_z.get()))
                self.max_depth.set(float(e_dep.get()))
                self.mesh_cl.set(float(e_cl.get()))
                popup.destroy()
            except: pass
        tk.Button(popup, text="Salva", command=save, width=15, bg="#2196F3", fg="white").grid(row=5, column=0, columnspan=2, pady=15)

    def set_ip_cutoff(self):
        val = simpledialog.askfloat("I.P. Cutoff", "Minimo valore di I.P. (mV/V) accettabile:", initialvalue=self.ip_cutoff.get())
        if val is not None: self.ip_cutoff.set(val)

    # --- LETTURA DATI & TOPOGRAFIA ---
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("File POLARES", "*.dat"), ("Tutti i file", "*.*")])
        if file_path:
            self.filepath = file_path
            self.lbl_file.config(text=self.filepath.split('/')[-1], fg="black")
            try:
                self.raw_data = self.parse_dat_file()
                self.btn_run.config(state="normal")
                for i in range(5): self.edit_menu.entryconfig(i, state="normal") 
                self.lbl_status.config(text=f"Dati: {self.raw_data.size()} misure pronte.")
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
            self.lbl_topo.config(text=f"Topografia: {file_path.split('/')[-1]}", fg="green")
            
    def clear_topo(self):
        self.topo_filepath = None
        self.lbl_topo.config(text="Topografia: Nessuna", fg="gray")

    # --- FUNZIONI EDIT ---
    def reverse_data(self):
        if not self.raw_data: return
        max_x = max([self.raw_data.sensorPosition(i)[0] for i in range(self.raw_data.sensorCount())])
        for i in range(self.raw_data.sensorCount()):
            pos = self.raw_data.sensorPosition(i)
            self.raw_data.setSensorPosition(i, [max_x - pos[0], pos[1], pos[2]])
        self.raw_data.set('k', ert.geometricFactors(self.raw_data))
        self.lbl_status.config(text="Sezione specchiata (Reverse). Pronta da invertire.")
        messagebox.showinfo("Reverse", "La geometria della stesa è stata capovolta.")

    def change_start_pos(self):
        if not self.raw_data: return
        offset = simpledialog.askfloat("Shift X", "Metri da sommare alla coordinata X di partenza:")
        if offset is not None:
            for i in range(self.raw_data.sensorCount()):
                pos = self.raw_data.sensorPosition(i)
                self.raw_data.setSensorPosition(i, [pos[0] + offset, pos[1], pos[2]])
            self.lbl_status.config(text=f"X Shiftata di {offset}m")

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
            self.lbl_status.config(text=f"Filtraggio applicato. {self.raw_data.size()} dati rimasti.")
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
            self.lbl_status.config(text=f"Rimossi {len(to_remove)} punti visivamente.")

    # --- INVERSIONE ---
    def run_inversion_thread(self):
        if not self.raw_data: return
        self.btn_run.config(state="disabled")
        method = "Robust (L1)" if self.inv_method.get() == "L1" else "Smooth (L2)"
        self.lbl_status.config(text=f"Calcolo in corso ({method})...")
        threading.Thread(target=self.process_inversion, daemon=True).start()

    def process_inversion(self):
        try:
            is_robust = (self.inv_method.get() == "L1")
            max_d = self.max_depth.get() 
            para_dx = self.mesh_cl.get()
            quality = 34.5 if self.mesh_refine.get() else 33.5 # Regola la finezza
            
            if self.topo_filepath:
                topo_data = np.loadtxt(self.topo_filepath)
                topo_data = topo_data[topo_data[:, 0].argsort()]
                for i in range(self.raw_data.sensorCount()):
                    pos = self.raw_data.sensorPosition(i)
                    z_val = np.interp(pos[0], topo_data[:, 0], topo_data[:, 1]) 
                    self.raw_data.setSensorPosition(i, [pos[0], z_val, pos[2]])

            self.mgr = ert.ERTManager(self.raw_data)
                
            self.mgr.invert(lam=self.lam_val.get(), zWeight=self.z_weight.get(), robustData=is_robust, 
                            blockyModel=is_robust, paraDepth=max_d, paraDX=para_dx, quality=quality, 
                            maxIter=10, verbose=False)
            
            self.current_response = self.mgr.inv.response
            self.root.after(0, self.on_inversion_complete)
        except Exception as e:
            self.root.after(0, self.on_inversion_error, str(e))

    def on_inversion_complete(self):
        self.lbl_status.config(text="Inversione completata!", fg="green")
        self.btn_run.config(state="normal")
        self.file_menu.entryconfig("Salva Immagine Grafici (.png)", state="normal")
        self.file_menu.entryconfig("Esporta Modello per QGIS (.vtk)", state="normal")
        self.tools_menu.entryconfig("Mostra grafici a 3 pannelli", state="normal")
        self.tools_menu.entryconfig("Estrai Profilo Stratigrafico (Sezione 1D)...", state="normal")
        self.show_custom_plots()

    def on_inversion_error(self, error_msg):
        self.btn_run.config(state="normal")
        self.lbl_status.config(text="Errore.", fg="red")
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

    # --- MOTORE GRAFICO STILE RESIPY CON PANNELLO INTERATTIVO E NUMERI REALI ---
    def show_custom_plots(self):
        if not self.mgr: return
        plt.close('all')
        
        # Inizializza la figura con spazio a destra per la colorbar e in basso per i controlli
        fig = plt.figure(figsize=(14, 10))
        fig.canvas.manager.set_window_title('Risultati Inversione (Stile ResIPy)')
        self.current_fig = fig
        
        ax1 = fig.add_axes([0.08, 0.70, 0.75, 0.22])
        ax2 = fig.add_axes([0.08, 0.42, 0.75, 0.22], sharex=ax1)
        ax3 = fig.add_axes([0.08, 0.14, 0.75, 0.22], sharex=ax1)
        cbar_ax = fig.add_axes([0.86, 0.14, 0.02, 0.78]) # Barra Verticale a destra
        
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
        
        # Limiti Iniziali (Percentili Robusti)
        all_vals = np.concatenate((rhoa_m, rhoa_c, model_rho))
        init_min = np.percentile(all_vals, 2)
        init_max = np.percentile(all_vals, 98)
        if init_min <= 0: init_min = np.min(all_vals[all_vals > 0])

        # Prepara la mesh per il modello inverso
        mesh = self.mgr.paraDomain
        node_x = np.array([n.pos()[0] for n in mesh.nodes()])
        node_z = np.array([n.pos()[1] for n in mesh.nodes()])
        node_rho = np.array(pg.interpolate(mesh, model_rho, mesh.positions()))
        
        triang_pseudo = tri.Triangulation(x_centers, z_pseudo)
        triang_model = tri.Triangulation(node_x, node_z)
        
        # Coordinate per il taglio (Crop)
        x_min_data = np.min([data.sensorPosition(i)[0] for i in range(data.sensorCount())])
        x_max_data = np.max([data.sensorPosition(i)[0] for i in range(data.sensorCount())])

        # --- WIDGETS INTERATTIVI IN BASSO ---
        ax_vmin = fig.add_axes([0.15, 0.03, 0.1, 0.04])
        txt_vmin = TextBox(ax_vmin, 'Min Rho: ', initial=f"{init_min:.1f}")

        ax_vmax = fig.add_axes([0.35, 0.03, 0.1, 0.04])
        txt_vmax = TextBox(ax_vmax, 'Max Rho: ', initial=f"{init_max:.1f}")

        ax_btn = fig.add_axes([0.48, 0.03, 0.08, 0.04])
        btn_apply = Button(ax_btn, 'Apply')

        ax_chk = fig.add_axes([0.60, 0.01, 0.23, 0.08])
        chk = CheckButtons(ax_chk, ['Contour Lines', 'Crop Corners'], [True, False])

        # Salviamo i widget in memoria per evitare che vengano rimossi dal garbage collector
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
            
            # Gestione Crop
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

            # Formatting
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

            # Colorbar formattata con Numeri Reali (Senza notazione scientifica)
            def res_fmt(x, pos):
                return f"{int(x)}" if x >= 10 else f"{x:.2f}"
            
            fmt = FuncFormatter(res_fmt)
            cbar = fig.colorbar(tc, cax=cbar_ax, orientation='vertical', format=fmt)
            cbar.set_label("Resistivity (ohm.m)", fontsize=11)
            
            fig.canvas.draw_idle()

        # Collega i trigger
        btn_apply.on_clicked(draw_all)
        chk.on_clicked(draw_all)

        # Prima esecuzione
        draw_all()
        plt.show()

    def export_image(self):
        if not self.mgr: return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if file_path:
            # Rimuove temporaneamente i widgets prima di salvare per una foto pulita
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
