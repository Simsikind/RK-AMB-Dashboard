import tkinter as tk
from tkinter import ttk, filedialog
import pickle
import os
import re
import time
import functions

# Function to get the data from the .dat file
def read_data(filepath):
    with open(filepath, "r") as file:
        amb_num = re.sub('\n', '', file.readline())
        amb_name = re.sub('\n', '', file.readline())
        amb_date = re.sub('\n', '', file.readline())
        betreuungen = int(re.sub('\n', '', file.readline()))
        max_counts = {}
        for line in file:
            place, max_count = line.strip().split(":")
            max_counts[place] = int(max_count)
    return amb_num, amb_name, amb_date, betreuungen, max_counts

# Function to get the patient list from the .ambdat file
def read_list(amb_num):
    filepath = "PatDat/" + re.sub('[^0-9]', '', amb_num) + ".ambdat"
    with open(filepath, "rb") as fp:
        return pickle.load(fp)

# Function to update the patient list in the scrollable frame
def update_patient_list():
    for widget in patient_list_frame.winfo_children():
        widget.destroy()

    # Add legend at the top
    legend_frame = tk.Frame(patient_list_frame)
    legend_frame.grid(row=0, column=0, sticky="ew")

    legend_items = [
        ("| Nr.", "Num"),
        ("| BeH-Zeit", "HSTt"),
        ("| BeH", "HSTPlace"),
        ("| Si-Ka", "Triage"),
        ("| NACA", "Naca"),
        ("| Ber.G", "Alarmstr"),
        ("& Kommentar", "Comment")
    ]

    for text, color in legend_items:
        legend_label = tk.Label(legend_frame, text=text, foreground="black", anchor="w", font=("Arial", 16))
        legend_label.pack(side="left", fill="x")

    row_index = 1  # Start after the legend
    for patient in Patlist:
        if patient.Num == 0 or patient.Endt != "-":
            continue  # Skip patient 0 and inactive patients

        color = {
            "Rot - I": "red",
            "Gelb - II": "yellow",
            "Grün - III": "green",
            "Blau - IV": "blue",
            "Schwarz (tot) - V": "black"
        }.get(patient.Triage, "white")

        text_color = "white" if color in ["black", "blue"] else "black"
        is_finished = "Ja" if patient.finished else "Nein"
        if patient.Endt != "-" and not patient.finished:
            text_color = "#990000"
        patient_num_formatted = f"{patient.Num:03}"  # Format number as 001, 002, etc.
        patient_info = f"{patient_num_formatted} | {patient.HSTt} | {patient.HSTPlace} | {patient.Triage} | {patient.Naca} | {patient.Alarmstr}: {patient.Comment}"
        label = tk.Label(patient_list_frame, text=patient_info, background=color, foreground=text_color, anchor="w", font=("Arial", 16))
        label.grid(row=row_index, column=0, sticky="w")
        
        # Add a separator line
        separator = tk.Frame(patient_list_frame, height=2, bd=1, relief="sunken", background="black")
        separator.grid(row=row_index + 1, column=0, sticky="ew", pady=4)
        
        row_index += 2

# Function to update the usage (Auslastung) in the main window
def update_usage():
    for widget in usage_frame.winfo_children():
        widget.destroy()

    l_Ausl = tk.Label(usage_frame, text="Auslastung:", font=("Arial", 16))
    l_Ausl.grid(column=0, row=0)
    row = 1
    for place, max_count in max_counts.items():
        current_count = sum(1 for patient in Patlist if patient.HSTPlace == place and patient.Endt == "-")
        percentage = (current_count / max_count) * 100
        text_color = "#880000" if percentage > 100 else "black"
        
        if percentage >= 80:
            bg_color = "red"
        elif percentage >= 50:
            bg_color = "yellow"
        else:
            bg_color = "green"

        usage_label = tk.Label(usage_frame, text=f"{place}: {percentage:.2f}%", fg=text_color, bg=bg_color, font=("Arial", 16))
        usage_label.grid(column=0, row=row, sticky="ew")

        progress = ttk.Progressbar(usage_frame, length=400, mode='determinate')
        progress['value'] = percentage
        progress.grid(column=1, row=row)

        row += 1

# Function to check the file modification time and update the data
def check_file_modification():
    global Patlist
    global last_modification_time
    global last_update_time
    ambdat_filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"
    current_modification_time = os.path.getmtime(ambdat_filepath)
    if current_modification_time != last_modification_time:
        last_modification_time = current_modification_time

        # Wait for the file to be written
        time.sleep(0.1)
        Patlist = read_list(AmbNum)
        update_patient_list()
        update_usage()
        last_update_time = time.strftime("%Y-%m-%d %H:%M:%S")
        l_last_update.config(text=f"Letztes Update: {last_update_time}")
        
    root.after(100, check_file_modification)  # Check every 0.1 second

# Function to set the Ambulanznummer and initialize the data
def set_ambulanznummer():
    global AmbNum
    global AmbName
    global AmbDate
    global Betreuungen
    global max_counts
    global Patlist
    global last_modification_time
    filepath = filedialog.askopenfile(filetypes=[("Data-Datei", ".dat")]).name
    AmbNum, AmbName, AmbDate, Betreuungen, max_counts = read_data(filepath)
    Patlist = read_list(AmbNum)
    ambdat_filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"
    last_modification_time = os.path.getmtime(ambdat_filepath)
    update_patient_list()
    update_usage()
    l_amb_info.config(text=f"{AmbNum} | {AmbName}")
    check_file_modification()

# Initialize the main window
root = tk.Tk()
root.title("Ambulanz-Dashboard Echtzeit")

# Create frames for the input and display
input_frame = tk.Frame(root)
input_frame.pack(pady=20)

patient_list_canvas = tk.Canvas(root)
patient_list_frame = tk.Frame(patient_list_canvas)
scrollbar = tk.Scrollbar(root, orient="vertical", command=patient_list_canvas.yview)
patient_list_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="left", fill="y")
patient_list_canvas.pack(side="left", fill="both", expand=True)
patient_list_canvas.create_window((0, 0), window=patient_list_frame, anchor="nw")

usage_frame = tk.Frame(root)
usage_frame.pack(pady=20)

def on_frame_configure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

patient_list_frame.bind("<Configure>", lambda event, canvas=patient_list_canvas: on_frame_configure(canvas))

# Input for Ambulanznummer
button_set_amb_num = tk.Button(input_frame, text="Ambulanznummer setzen", command=set_ambulanznummer, font=("Arial", 16))
button_set_amb_num.pack(side="left")

# Label for last update time
l_last_update = tk.Label(input_frame, text="Letztes Update: -", font=("Arial", 16))
l_last_update.pack(side="left", padx=20)

# Label for Ambulanznummer and name
l_amb_info = tk.Label(input_frame, text=" | ", font=("Arial", 16))
l_amb_info.pack(side="left", padx=20)

# Global variables
AmbNum = ""
AmbName = ""
AmbDate = ""
Betreuungen = 0
Patlist = []
max_counts = {"Nicht zugeordnet": 100}
last_modification_time = 0
last_update_time = "-"

root.mainloop()
