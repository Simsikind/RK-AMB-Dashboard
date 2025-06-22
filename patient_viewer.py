import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pickle
import os
import re
import time
import auth
import secure_io

class PatientDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Patientenanzeige")

        # Daten
        self.amb_num = ""
        self.amb_name = ""
        self.amb_date = ""
        self.betreuuungen = 0
        self.max_counts = {"Nicht zugeordnet": 100}
        self.patlist = []
        self.last_modification_time = 0
        self.last_update_time = "-"
        self.filter_place = ""
        self.filter_abtransport = ""

        # Schlüssel laden
        self.fernet = auth.load_key_with_pin()

        # GUI-Elemente
        self.setup_gui()

    def setup_gui(self):
        # Input Frame
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=20)

        tk.Button(self.input_frame, text="Ambulanznummer setzen", command=self.set_ambulanznummer, font=("Arial", 16)).pack(side="left")
        self.l_last_update = tk.Label(self.input_frame, text="Letztes Update: -", font=("Arial", 16))
        self.l_last_update.pack(side="left", padx=20)
        self.l_amb_info = tk.Label(self.input_frame, text=" | ", font=("Arial", 16))
        self.l_amb_info.pack(side="left", padx=20)
        tk.Button(self.input_frame, text="Filter", command=self.open_filter_menu, font=("Arial", 16)).pack(side="left", padx=20)

        # Canvas + Scrollbar
        self.patient_list_canvas = tk.Canvas(self.root)
        self.patient_list_frame = tk.Frame(self.patient_list_canvas)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.patient_list_canvas.yview)
        self.patient_list_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="left", fill="y")
        self.patient_list_canvas.pack(side="left", fill="both", expand=True)
        self.patient_list_canvas.create_window((0, 0), window=self.patient_list_frame, anchor="nw")
        self.patient_list_frame.bind("<Configure>", lambda event: self.patient_list_canvas.configure(scrollregion=self.patient_list_canvas.bbox("all")))

        # Usage Frame
        self.usage_frame = tk.Frame(self.root)
        self.usage_frame.pack(pady=20)

    def read_data(self, filepath):
        with open(filepath, "r") as file:
            self.amb_num = file.readline().strip()
            self.amb_name = file.readline().strip()
            self.amb_date = file.readline().strip()
            self.betreuuungen = int(file.readline().strip())
            self.max_counts = {line.split(":")[0].strip(): int(line.split(":")[1]) for line in file}

    def read_list(self):
        filepath = f"PatDat/{re.sub('[^0-9]', '', self.amb_num)}.ambdat"
        self.patlist = secure_io.read_encrypted(filepath, self.fernet)

    def update_patient_list(self):
        for widget in self.patient_list_frame.winfo_children():
            widget.destroy()

        legend_frame = tk.Frame(self.patient_list_frame)
        legend_frame.grid(row=0, column=0, sticky="ew")
        legend_items = ["| Nr.", "| BeH-Zeit", "| BeH", "| Si-Ka", "| NACA", "| Ber.G", "& Kommentar"]
        for item in legend_items:
            tk.Label(legend_frame, text=item, font=("Arial", 16)).pack(side="left", fill="x")

        row_index = 1
        for patient in self.patlist:
            if patient.Num == 0 or patient.Endt != "-" or (self.filter_place and patient.HSTPlace != self.filter_place) or (self.filter_abtransport and patient.TransportAgency != self.filter_abtransport):
                continue

            color = {"Rot - I": "red", "Gelb - II": "yellow", "Gr\u00fcn - III": "green", "Blau - IV": "blue", "Schwarz (tot) - V": "black"}.get(patient.Triage, "white")
            text_color = "white" if color in ["black", "blue"] else "black"
            if patient.Endt != "-" and not patient.finished:
                text_color = "#990000"
            info = f"{patient.Num:03} | {patient.HSTt} | {patient.HSTPlace} | {patient.Triage} | {patient.Naca} | {patient.Alarmstr}: {patient.Comment}"
            tk.Label(self.patient_list_frame, text=info, bg=color, fg=text_color, font=("Arial", 16)).grid(row=row_index, column=0, sticky="w")
            tk.Frame(self.patient_list_frame, height=2, bd=1, relief="sunken", background="black").grid(row=row_index+1, column=0, sticky="ew", pady=4)
            row_index += 2

    def update_usage(self):
        for widget in self.usage_frame.winfo_children():
            widget.destroy()

        tk.Label(self.usage_frame, text="Auslastung:", font=("Arial", 16)).grid(column=0, row=0)
        row = 1
        for place, max_count in self.max_counts.items():
            current_count = sum(1 for p in self.patlist if p.HSTPlace == place and p.Endt == "-")
            percentage = (current_count / max_count) * 100
            bg_color = "green" if percentage < 50 else "yellow" if percentage < 80 else "red"
            fg_color = "#880000" if percentage > 100 else "black"
            tk.Label(self.usage_frame, text=f"{place}: {percentage:.2f}%", fg=fg_color, bg=bg_color, font=("Arial", 16)).grid(column=0, row=row, sticky="ew")
            ttk.Progressbar(self.usage_frame, length=400, mode='determinate', value=percentage).grid(column=1, row=row)
            row += 1

    def open_filter_menu(self):
        filter_window = tk.Toplevel(self.root)
        filter_window.title("Filter Einstellungen")

        places = list(set(p.HSTPlace for p in self.patlist)) + [""]
        place_var = tk.StringVar(filter_window, value=self.filter_place)
        tk.Label(filter_window, text="Behandlungsplatz:", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=10)
        tk.OptionMenu(filter_window, place_var, *places).grid(row=0, column=1, padx=10, pady=10)

        transports = list(set(p.TransportAgency for p in self.patlist)) + [""]
        abtransport_var = tk.StringVar(filter_window, value=self.filter_abtransport)
        tk.Label(filter_window, text="Abtransport:", font=("Arial", 16)).grid(row=1, column=0, padx=10, pady=10)
        tk.OptionMenu(filter_window, abtransport_var, *transports).grid(row=1, column=1, padx=10, pady=10)

        def apply():
            self.filter_place = place_var.get()
            self.filter_abtransport = abtransport_var.get()
            self.update_patient_list()
            filter_window.destroy()

        tk.Button(filter_window, text="Anwenden", command=apply, font=("Arial", 16)).grid(row=2, column=0, columnspan=2, pady=20)

    def set_ambulanznummer(self):
        file = filedialog.askopenfile(filetypes=[("Data-Datei", ".dat")])
        if not file:
            return
        try:
            self.read_data(file.name)
            self.read_list()
            filepath = f"PatDat/{re.sub('[^0-9]', '', self.amb_num)}.ambdat"
            self.last_modification_time = os.path.getmtime(filepath)
            self.update_patient_list()
            self.update_usage()
            self.l_amb_info.config(text=f"{self.amb_num} | {self.amb_name}")
            self.check_file_modification()
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def check_file_modification(self):
        filepath = f"PatDat/{re.sub('[^0-9]', '', self.amb_num)}.ambdat"
        current_time = os.path.getmtime(filepath)
        if current_time != self.last_modification_time:
            self.last_modification_time = current_time
            time.sleep(0.1)
            self.read_list()
            self.update_patient_list()
            self.update_usage()
            self.last_update_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.l_last_update.config(text=f"Letztes Update: {self.last_update_time}")
        self.root.after(100, self.check_file_modification)


if __name__ == "__main__":
    root = tk.Tk()
    app = PatientDisplayApp(root)
    root.mainloop()
