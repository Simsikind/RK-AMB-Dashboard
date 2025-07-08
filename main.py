# file: main.py

import tkinter.filedialog
from datetime import datetime
import tkinter
from tkinter import ttk
import csv
import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import sys
import functions
import shortcuts
from secure_io import write_encrypted, read_encrypted
import auth

fernet = auth.load_key_with_pin()

filter_status = "alle"
filter_place = ""
filter_transport = ""

print("Starte Ambulanz-Dashboard")

# Function to get the current time
def now():
    currentTime = datetime.now()
    return str(currentTime.strftime("%H:%M"))

# Global variables

Version = "1.4"

AmbNum = "Ambulanznummer (bitte setzten)"
AmbName = "Ambulanzname (bitte setzten)"
AmbDate = "Datum (bitte setzten)"
max_counts = {"Nicht zugeordnet":100}
filepath = ""
Betreuungen = 0
CurrentPatindex = 0
Patlist = []
lastUpdate = now()

def Pat0():
    global Patlist
    if Patlist:
        if Patlist[0].Num == 0:
            Patlist.pop(0)
    Patlist.insert(0, functions.Patient(0))  # Add Patient zero, so that the Index is the same as the "Ablagenummer"
    Patlist[0].setfinished(True)
    Patlist[0].setAlarmt("-")
    Patlist[0].setHSTPlace("-")
    Patlist[0].setEndt(" - ")
    Patlist[0].setComment("Geisterpatient")

main_window = tkinter.Tk(className='~Amulanz-Dashboard~')

main_window.grid_columnconfigure(4, weight=1)
main_window.grid_rowconfigure(0, weight=1)

Pat0()

# Function to toggle fullscreen mode
def toggle_fullscreen(event=None):
    is_fullscreen = main_window.attributes("-fullscreen")
    main_window.attributes("-fullscreen", not is_fullscreen)

# Function to prompt user for patient number and open Edit_pat
def prompt_edit_patient(event=None):
    def on_submit(event=None):
        global CurrentPatindex
        try:
            patient_num = int(entry.get())
            if 0 <= patient_num <= latestpatindex():
                CurrentPatindex = patient_num
                Update_lables()
                prompt_window.destroy()
            else:
                error_label.config(text="Ungültige Patientennummer.")
        except ValueError:
            error_label.config(text="Bitte eine gültige Nummer eingeben.")

    def on_cancel(event=None):
        prompt_window.destroy()

    prompt_window = tkinter.Toplevel(main_window)
    prompt_window.title("Lade Patient")
    prompt_window.focus_force()

    label = tkinter.Label(prompt_window, text="Bitte geben Sie eine Patientennummer ein:")
    label.pack(pady=5)

    entry = tkinter.Entry(prompt_window)
    entry.pack(pady=5)
    entry.focus()
    entry.bind(shortcuts.Confirm, on_submit)
    entry.bind(shortcuts.Cancel, on_cancel)

    button_frame = tkinter.Frame(prompt_window)
    button_frame.pack(pady=5)

    submit_button = tkinter.Button(button_frame, text="OK", command=on_submit)
    submit_button.pack(side="left", padx=5)

    cancel_button = tkinter.Button(button_frame, text="Abbrechen", command=on_cancel)
    cancel_button.pack(side="left", padx=5)

    error_label = tkinter.Label(prompt_window, text="", fg="red")
    error_label.pack(pady=5)

# Add Triage-Kategorie to the global variables
TriageCategories = ["-","Rot - I", "Gelb - II", "Grün - III", "Blau - IV", "Schwarz (tot) - V"]

# Create necessary directories if they don't exist
while os.path.exists("Userdata") == False:
    os.mkdir("Userdata")
    print("Ordner 'Userdata' erstellt")


while os.path.exists("Userdata/Export") == False:
    os.mkdir("Userdata/Export")
    print("Ordner 'Export' in 'Userdata' erstellt")

while os.path.exists("PatDat") == False:
    os.mkdir("PatDat")
    print("Ordner 'PatDat' erstellt")

ambdat_path = "PatDat/.ambdat"
if not os.path.exists(ambdat_path):
    with open(ambdat_path, "wb") as f:
        pass  # Leere Datei erstellen
    print(f"Leere .ambdat-Datei erstellt: {ambdat_path}")

# Functions to set global variables
def setNum(str):
    global AmbNum
    AmbNum = str

def setName(str):
    global AmbName
    AmbName = str

def setDate(str):
    global AmbDate
    AmbDate = str

# Function to navigate to the previous patient
def PrevPat_Button():
    global CurrentPatindex
    if CurrentPatindex > 0:
        CurrentPatindex = CurrentPatindex - 1
    print("Current Patient Index: ", CurrentPatindex)
    Update_lables()

# Function to navigate to the next patient
def NextPat_Button():
    global CurrentPatindex
    if CurrentPatindex < len(Patlist) - 1:
        CurrentPatindex = CurrentPatindex + 1
    else:
        NewPat_Button()
    print("Current Patient Index: ", CurrentPatindex)
    Update_lables()

# Function to get the index of the latest patient
def latestpatindex():
    return len(Patlist) - 1

# Function to update the patient list in the scrollable frame
def Update_patient_list():
    global CurrentPatindex
    global filter_active, filter_place, filter_transport
    global sort_column, sort_order

    if not Patlist:
        l_Pat.config(text="0 Patienten")
        l_Betreuungen.config(text=str(Betreuungen) + " Betreuungen")
        l_AmbNum.config(text=AmbNum)
        l_AmbName.config(text=AmbName)
        l_AmbDate.config(text=AmbDate)
        return

    def Patclick(idx):
        global CurrentPatindex
        if idx == CurrentPatindex:
            CurrentPatindex = idx 
            Update_lables()
            Edit_pat(idx)
        else: 
            CurrentPatindex = idx 
            Update_lables()
        return idx

    def sort_patients(column):
        global sort_column, sort_order
        if sort_column == column:
            sort_order = "desc" if sort_order == "asc" else "asc"
        else:
            sort_column = column
            sort_order = "asc"
        Update_patient_list()

    for widget in patient_list_frame.winfo_children():
        widget.destroy()

    # Add legend at the top
    legend_frame = tkinter.Frame(patient_list_frame)
    legend_frame.grid(row=0, column=0, sticky="ew")

    legend_items = [
        ("| Nr.", "Num"),
        ("| BeH-Zeit", "HSTt"),
        ("| BeH", "HSTPlace"),
        ("| Si-Ka", "Triage"),
        ("| Abtrans.", "TransportAgency"),
        ("| NACA", "Naca"),
        ("| Ber.G", "Alarmstr"),
        ("& Kommentar", "Comment")
    ]

    for text, column in legend_items:
        indicator = " ▲" if sort_column == column and sort_order == "asc" else " ▼" if sort_column == column and sort_order == "desc" else ""
        legend_label = tkinter.Label(legend_frame, text=text + indicator, foreground="black", anchor="w")
        legend_label.pack(side="left", fill="x")
        legend_label.bind("<Button-1>", lambda e, col=column: sort_patients(col))

    row_index = 1  # Start after the legend

    sorted_patlist = sorted(Patlist, key=lambda p: getattr(p, sort_column), reverse=(sort_order == "desc"))

    for patient in sorted_patlist:

        if patient.Num == 0:
            continue
        if filter_status == "aktiv" and patient.Endt != "-":
            continue
        elif filter_status == "entlassen" and patient.Endt == "-":
            continue
        if filter_place and patient.HSTPlace != filter_place:
            continue
        if filter_transport and patient.TransportAgency != filter_transport:
            continue
        
        color = "grey" if patient.Endt != "-" else {
            "Rot - I": "red",
            "Gelb - II": "yellow",
            "Grün - III": "green",
            "Blau - IV": "blue",
            "Schwarz (tot) - V": "black"
        }.get(patient.Triage, "white")

        text_color = "white" if color in ["black", "blue"] else "black"
        if patient.Endt != "-" and not patient.finished:
            text_color = "#990000"
        patient_num_formatted = f"{patient.Num:03}"  # Format number as 001, 002, etc.
        patient_info = f"{patient_num_formatted} | {patient.HSTt} | {patient.HSTPlace} | {patient.Triage} | {patient.TransportAgency} | {patient.Naca} | {patient.Alarmstr}: {patient.Comment}"
        label = tkinter.Label(patient_list_frame, text=patient_info, background=color, foreground=text_color, anchor="w")
        label.grid(row=row_index, column=0, sticky="w")
        label.bind("<Button-1>", lambda e, idx=patient.Num: (Patclick(idx)))
        
        # Add a separator line
        separator = tkinter.Frame(patient_list_frame, height=1, bd=1, relief="sunken", background="black")
        separator.grid(row=row_index + 1, column=0, sticky="ew", pady=2)
        
        row_index += 2

# Initialize sorting variables
sort_column = "Num"
sort_order = "asc"

# Function to open the filter menu
def open_filter_menu():
    global filter_status, filter_place, filter_transport

    filter_window = tkinter.Toplevel(main_window)
    filter_window.title("Filter Einstellungen")
    filter_window.focus_force()

    # Variablen vorbereiten
    status_var = tkinter.StringVar(value=filter_status)
    place_var = tkinter.StringVar(value=filter_place)
    abtransport_var = tkinter.StringVar(value=filter_transport)

    # Trace-Update-Funktionen
    def update_status_label(*args):
        l_status.config(text=f"Aktuell: {status_var.get()}")

    def update_place_label(*args):
        l_place.config(text=f"Aktuell: {place_var.get() or 'alle'}")

    def update_transport_label(*args):
        l_transport.config(text=f"Aktuell: {abtransport_var.get() or 'alle'}")

    # Traces setzen
    status_var.trace_add("write", update_status_label)
    place_var.trace_add("write", update_place_label)
    abtransport_var.trace_add("write", update_transport_label)

    # Status-Filter
    tkinter.Label(filter_window, text="Status:").grid(row=0, column=0, padx=10, pady=10)
    status_options = ["alle", "aktiv", "entlassen"]
    tkinter.OptionMenu(filter_window, status_var, *status_options).grid(row=0, column=1, padx=10, pady=10)
    l_status = tkinter.Label(filter_window, text=f"Aktuell: {status_var.get()}")
    l_status.grid(row=0, column=2, padx=10)

    # Behandlungsplatz
    places = sorted(set(p.HSTPlace for p in Patlist if p.HSTPlace.strip()))
    places.insert(0, "")
    tkinter.Label(filter_window, text="Behandlungsplatz:").grid(row=1, column=0, padx=10, pady=10)
    tkinter.OptionMenu(filter_window, place_var, *places).grid(row=1, column=1, padx=10, pady=10)
    l_place = tkinter.Label(filter_window, text=f"Aktuell: {place_var.get() or 'alle'}")
    l_place.grid(row=1, column=2, padx=10)

    # Abtransport
    transports = sorted(set(p.TransportAgency for p in Patlist if p.TransportAgency.strip()))
    transports.insert(0, "")
    tkinter.Label(filter_window, text="Abtransport:").grid(row=2, column=0, padx=10, pady=10)
    tkinter.OptionMenu(filter_window, abtransport_var, *transports).grid(row=2, column=1, padx=10, pady=10)
    l_transport = tkinter.Label(filter_window, text=f"Aktuell: {abtransport_var.get() or 'alle'}")
    l_transport.grid(row=2, column=2, padx=10)

    # Anwenden
    def apply():
        global filter_status, filter_place, filter_transport
        filter_status = status_var.get()
        filter_place = place_var.get()
        filter_transport = abtransport_var.get()
        print("[DEBUG] Filter:", filter_status, filter_place, filter_transport)
        Update_lables()
        filter_window.destroy()

    # Zurücksetzen
    def reset_filters():
        status_var.set("alle")
        place_var.set("")
        abtransport_var.set("")

    ttk.Button(filter_window, text="Anwenden", command=apply).grid(row=3, column=0, columnspan=2, pady=10)
    ttk.Button(filter_window, text="Zurücksetzen", command=reset_filters).grid(row=3, column=2, pady=10)


# Function to update labels in the main window
def Update_lables():
    global lastUpdate
    global Betreuungen
    global Patlist
    global CurrentPatindex

    # Clear existing labels to avoid artifacts
    for widget in main_window.grid_slaves():
        if int(widget.grid_info()["row"]) >= 19:
            widget.grid_forget()
    
    for widget in main_window.grid_slaves():
        if int(widget.grid_info()["row"]) == 3 and isinstance(widget, tkinter.LabelFrame) and widget.cget("text") == "Behandlungsplatz-Auslastung":
            widget.destroy()
# Update feste Labels
    l_Pat.config(text=str(latestpatindex()) + " Patienten")
    l_Betreuungen.config(text=str(Betreuungen) + " Betreuungen")
    l_AmbNum.config(text=AmbNum)
    l_AmbName.config(text=AmbName)
    l_AmbDate.config(text=AmbDate)

    # Update dynamische Patienteninformationen
    values = {
        "Aktuell Angezeigter Pat Nr:": Patlist[CurrentPatindex].Num,
        "Einsatzbeginn:": Patlist[CurrentPatindex].Alarmt,
        "Berufungsgrund:": Patlist[CurrentPatindex].Alarmstr,
        "Berufungsort:": Patlist[CurrentPatindex].BOplace,
        "Zeit am BO:": Patlist[CurrentPatindex].BOt,
        "Sichtungs-Kategorie:": Patlist[CurrentPatindex].Triage,
        "Zeit auf der Behandlung:": Patlist[CurrentPatindex].HSTt,
        "Behandlungsplatz:": Patlist[CurrentPatindex].HSTPlace,
        "Abtransport:": Patlist[CurrentPatindex].TransportAgency,
        "Einsatzende:": Patlist[CurrentPatindex].Endt,
        "Protokoll fertig:": Patlist[CurrentPatindex].finished,
        "NACA:": Patlist[CurrentPatindex].Naca,
        "Name/Kommentar:": Patlist[CurrentPatindex].Comment
    }

    for key, value in values.items():
        if key in label_refs:
            label_refs[key].config(text=str(value))

    # Update Behandlungsplätze usage
    usage_frame = tkinter.LabelFrame(main_window, text="Behandlungsplatz-Auslastung", padx=10, pady=5)
    usage_frame.grid(column=0, row=3, columnspan=3)

    b_Usage = tkinter.Button(usage_frame, text="Auslastung-Details", command=lambda:[DisplayPatientsInPlace()])
    b_Usage.grid(row=0, column=3)

    l_Ausl = tkinter.Label(usage_frame, text="Auslastung:")
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

        usage_label = tkinter.Label(usage_frame, text=f"{place}: {percentage:.2f}%", fg=text_color, bg=bg_color)
        usage_label.grid(column=0, row=row)

        progress = ttk.Progressbar(usage_frame, length=200, mode='determinate')
        progress['value'] = percentage
        progress.grid(column=1, row=row)

        row += 1

    main_window.title(AmbName + (" - Dashboard"))
    Update_patient_list()
    lastUpdate = now()
    auth.log("Patientenliste aktualisiert", AmbNum)

# Function to edit patient details
def Edit_pat(index):
    if index == 0:
        return  # Skip patient 0
    
    

    Edit = tkinter.Toplevel(main_window)
    Edit.title("Patient " + str(index) + " bearbeiten")
    Edit.focus_force()

    l_textr3 = tkinter.Label(Edit, text="Akuell Angezeigter Pat Nr: ")
    l_textr3.grid(column=0, row=0)
    l_CurrentPatNum = tkinter.Label(Edit, text=str(Patlist[index].Num))
    l_CurrentPatNum.grid(column=1, row=0)
    
    l_textr4 = tkinter.Label(Edit, text="Einsatzbeginn:")
    l_textr4.grid(column=0, row=1)
    e_CurrentPatAlarmt = tkinter.Entry(Edit)
    e_CurrentPatAlarmt.insert(0, str(Patlist[index].Alarmt))
    e_CurrentPatAlarmt.grid(column=1, row=1)
    Patlist[index].setAlarmt(e_CurrentPatAlarmt.get())

    b_now_alarmt = tkinter.Button(Edit, text="Jetzt", command=lambda: [e_CurrentPatAlarmt.delete(0, tkinter.END), e_CurrentPatAlarmt.insert(0, now())])
    b_now_alarmt.grid(column=2, row=1)

    l_textr5 = tkinter.Label(Edit, text="Berufungsgrund:")
    l_textr5.grid(column=0, row=2)
    e_CurrentPatAlarmstr = tkinter.Entry(Edit)
    e_CurrentPatAlarmstr.insert(0, str(Patlist[index].Alarmstr))
    e_CurrentPatAlarmstr.grid(column=1, row=2)

    l_textr6 = tkinter.Label(Edit, text="Berufungsort:")
    l_textr6.grid(column=0, row=3)
    e_CurrentPatBO = tkinter.Entry(Edit)
    e_CurrentPatBO.insert(0, str(Patlist[index].BOplace))
    e_CurrentPatBO.grid(column=1, row=3)

    l_textr7 = tkinter.Label(Edit, text="Zeit am BO: ")
    l_textr7.grid(column=0, row=4)
    e_CurrentPatBot = tkinter.Entry(Edit)
    e_CurrentPatBot.insert(0, str(Patlist[index].BOt))
    e_CurrentPatBot.grid(column=1, row=4)

    b_now_bot = tkinter.Button(Edit, text="Jetzt", command=lambda: [e_CurrentPatBot.delete(0, tkinter.END), e_CurrentPatBot.insert(0, now())])
    b_now_bot.grid(column=2, row=4)

    l_textr8 = tkinter.Label(Edit, text="Sichtungs-Kategorie:")
    l_textr8.grid(column=0, row=5)
    e_CurrentPatTriage = ttk.Combobox(Edit, values=TriageCategories, state="readonly")
    e_CurrentPatTriage.set(Patlist[index].Triage)
    e_CurrentPatTriage.grid(column=1, row=5)

    l_textr9 = tkinter.Label(Edit, text="Zeit auf der Behandlung:")
    l_textr9.grid(column=0, row=6)
    e_CurrentPatHSTt = tkinter.Entry(Edit)
    e_CurrentPatHSTt.insert(0, str(Patlist[index].HSTt))
    e_CurrentPatHSTt.grid(column=1, row=6)

    b_now_hstt = tkinter.Button(Edit, text="Jetzt", command=lambda: [e_CurrentPatHSTt.delete(0, tkinter.END), e_CurrentPatHSTt.insert(0, now())])
    b_now_hstt.grid(column=2, row=6)

    l_textr10 = tkinter.Label(Edit, text="Behandlungsplatz:")
    l_textr10.grid(column=0, row=7)
    l_SelectedPlace = tkinter.Label(Edit, text=str(Patlist[index].HSTPlace))
    l_SelectedPlace.grid(column=1, row=7)
    b_SelectPlace = tkinter.Button(Edit, text="Platz auswählen", command=lambda: SelectPlace_Window(index, l_SelectedPlace))
    b_SelectPlace.grid(column=2, row=7)

    # Disable the button if only one Behandlungsplatz is configured
    if len(max_counts) <= 1:
        b_SelectPlace.config(state=tkinter.DISABLED)

    l_textr11 = tkinter.Label(Edit, text="Abtransport-Organisation:")
    l_textr11.grid(column=0, row=8)
    e_CurrentPatTransportAgency = ttk.Combobox(Edit, values=["-", "KTW", "NKTW", "RTW", "RTW+NEF/NAW", "Anderes"], state="readonly")
    e_CurrentPatTransportAgency.set(Patlist[index].TransportAgency)
    e_CurrentPatTransportAgency.grid(column=1, row=8)

    l_textr12 = tkinter.Label(Edit, text="Einsatzende:")
    l_textr12.grid(column=0, row=9)
    e_CurrentPatEndt = tkinter.Entry(Edit)
    e_CurrentPatEndt.insert(0, str(Patlist[index].Endt))
    e_CurrentPatEndt.grid(column=1, row=9)

    b_now_endt = tkinter.Button(Edit, text="Jetzt", command=lambda: [e_CurrentPatEndt.delete(0, tkinter.END), e_CurrentPatEndt.insert(0, now())])
    b_now_endt.grid(column=2, row=9)

    l_textr13 = tkinter.Label(Edit, text="Protokoll fertig:")
    l_textr13.grid(column=0, row=10)

    finished_var = tkinter.StringVar()
    finished_var.set("Nein" if not Patlist[index].finished else "Ja")

    optionmenu_finished = tkinter.OptionMenu(Edit, finished_var, "Nein", "Ja")
    optionmenu_finished.grid(column=1, row=10)
    l_finished_status = tkinter.Label(Edit, text=f"Aktuell: {finished_var.get()}")
    l_finished_status.grid(column=2, row=10, padx=5)
    l_finished_status.config(text=f"Aktuell: {finished_var.get()}")
    finished_var.trace_add("write", lambda *args: l_finished_status.config(text=f"Aktuell: {finished_var.get()}"))


    l_textr14 = tkinter.Label(Edit, text="NACA:")
    l_textr14.grid(column=0, row=11)
    e_CurrentPatNACA = tkinter.Entry(Edit)
    e_CurrentPatNACA.insert(0, str(Patlist[index].Naca))
    e_CurrentPatNACA.grid(column=1, row=11)

    l_textr15 = tkinter.Label(Edit, text="Name/Kommentar:")
    l_textr15.grid(column=0, row=12)
    e_CurrentPatComment = tkinter.Entry(Edit)
    e_CurrentPatComment.insert(0, str(Patlist[index].Comment))
    e_CurrentPatComment.grid(column=1, row=12)


    def update_finished_state(*args):
        hstt_ok = e_CurrentPatHSTt.get() != "-"
        place_ok = l_SelectedPlace.cget("text") != "-"
        endt_ok = e_CurrentPatEndt.get() != "-"

        menu = optionmenu_finished["menu"]
        menu.delete(0, "end")
        menu.add_command(label="Nein", command=lambda: finished_var.set("Nein"))

        if hstt_ok and place_ok and endt_ok:
            optionmenu_finished.config(state=tkinter.NORMAL)
            menu.add_command(label="Ja", command=lambda: finished_var.set("Ja"))
        else:
            optionmenu_finished.config(state=tkinter.NORMAL)
            finished_var.set("Nein")


    def delete_patient_ask():
        if tkinter.messagebox.askyesno("Patient löschen", f"Möchten Sie den Patienten Nr. {index} wirklich löschen?"):
            delete_patient()

    def delete_patient():
        global CurrentPatindex
        if CurrentPatindex == latestpatindex():
            CurrentPatindex -= 1
        Patlist.pop(index)
        [patient.setNum(Patlist.index(patient)) for patient in Patlist]
        write_list(Patlist)
        # Sicherstellen, dass CurrentPatindex gültig ist
        if not Patlist or CurrentPatindex >= len(Patlist):
            CurrentPatindex = max(0, latestpatindex())
        Update_lables()
        auth.log(f"Patient Nr. {index} gelöscht", AmbNum)

    b_OK = tkinter.Button(Edit, text="OK", command=lambda: [
        Patlist[index].setAlarmt(e_CurrentPatAlarmt.get()),
        Patlist[index].setAlarmstr(e_CurrentPatAlarmstr.get()),
        Patlist[index].setBOplace(e_CurrentPatBO.get()),
        Patlist[index].setBOt(e_CurrentPatBot.get()),
        Patlist[index].setHSTt(e_CurrentPatHSTt.get()),
        Patlist[index].setTransportOrg(e_CurrentPatTransportAgency.get()),
        Patlist[index].setEndt(e_CurrentPatEndt.get()),
        Patlist[index].setNaca(e_CurrentPatNACA.get()),
        Patlist[index].setTriage(e_CurrentPatTriage.get()),
        Patlist[index].setfinished(finished_var.get() == "Ja"),
        Patlist[index].setComment(e_CurrentPatComment.get()),
        write_list(Patlist),
        Update_lables(), 
        Edit.destroy()
    ])


    b_Cancel = tkinter.Button(Edit, text="Abbruch", command=Edit.destroy)
    b_Delete = tkinter.Button(Edit, text="Patient löschen", command=lambda: [delete_patient_ask(), Edit.destroy()], bg="red")

    b_OK.grid(row=16, column=2)
    b_Cancel.grid(row=16, column=1)
    b_Delete.grid(row=16, column=0)

    update_finished_state()

    # Add keyboard shortcuts
    Edit.bind(shortcuts.Confirm, lambda event: [
        Patlist[index].setAlarmt(e_CurrentPatAlarmt.get()),
        Patlist[index].setAlarmstr(e_CurrentPatAlarmstr.get()),
        Patlist[index].setBOplace(e_CurrentPatBO.get()),
        Patlist[index].setBOt(e_CurrentPatBot.get()),
        Patlist[index].setHSTt(e_CurrentPatHSTt.get()),
        Patlist[index].setTransportOrg(e_CurrentPatTransportAgency.get()),
        Patlist[index].setEndt(e_CurrentPatEndt.get()),
        Patlist[index].setNaca(e_CurrentPatNACA.get()),
        Patlist[index].setTriage(e_CurrentPatTriage.get()),
        Patlist[index].setfinished(finished_var.get() == "Ja"),
        Patlist[index].setComment(e_CurrentPatComment.get()),
        write_list(Patlist),
        Update_lables(), 
        Edit.destroy()
    ])
    Edit.bind(shortcuts.Cancel, lambda event: Edit.destroy())
    Edit.bind(shortcuts.PatientDel, lambda event: [delete_patient_ask(), Edit.destroy()])
    Edit.bind(shortcuts.NowBeginTime, lambda event: [e_CurrentPatAlarmt.delete(0, tkinter.END), e_CurrentPatAlarmt.insert(0, now())])
    Edit.bind(shortcuts.NowBoTime, lambda event: [e_CurrentPatBot.delete(0, tkinter.END), e_CurrentPatBot.insert(0, now())])
    Edit.bind(shortcuts.NowHstTime, lambda event: [e_CurrentPatHSTt.delete(0, tkinter.END), e_CurrentPatHSTt.insert(0, now())])
    Edit.bind(shortcuts.NowEndTime, lambda event: [e_CurrentPatEndt.delete(0, tkinter.END), e_CurrentPatEndt.insert(0, now())])
    Edit.bind(shortcuts.SelectPlace, lambda event: SelectPlace_Window(index, l_SelectedPlace))
    Edit.bind(shortcuts.ProtocolFinished, lambda event: finished_var.set("Nein" if finished_var.get() == "Ja" else "Ja"))
    auth.log(f"Patient Nr. {index} bearbeitet", AmbNum)


# Function to select a place for the patient
def SelectPlace_Window(index, l_SelectedPlace):
    SelectPlace = tkinter.Toplevel(main_window)
    SelectPlace.title("Behandlungsplatz auswählen")
    SelectPlace.focus_force()

    l_Ausl = tkinter.Label(SelectPlace, text="Auslastung:", font=("Arial", 12, "bold"))
    l_Ausl.grid(column=0, row=0, columnspan=4, pady=(10, 5))

    row = 1
    triage_colors = {
        "Rot - I": "red",
        "Gelb - II": "yellow",
        "Grün - III": "green",
        "Blau - IV": "blue",
        "Schwarz (tot) - V": "black",
        "-": "white"
    }
    triage_weights = {
        "Rot - I": 3,
        "Gelb - II": 2,
        "Grün - III": 1,
        "Blau - IV": 1,
        "Schwarz (tot) - V": 1,
        "-": 1
    }

    # Gewichte für den aktuellen Patienten
    patient_triage = Patlist[index].Triage
    current_weight = triage_weights.get(patient_triage, 1)

    lowest_load = float("inf")
    suggestion = None

    for place, max_count in max_counts.items():
        # Zählen pro Kategorie
        triage_counts = {triage: 0 for triage in TriageCategories}
        for patient in Patlist:
            if patient.HSTPlace == place and patient.Endt == "-":
                if patient.Triage in triage_counts:
                    triage_counts[patient.Triage] += 1

        total_count = sum(triage_counts.values())
        percentage = (total_count / max_count) * 100 if max_count > 0 else 0

        # Farb-Label
        if percentage >= 100:
            bg_color = "red"
        elif percentage >= 80:
            bg_color = "orange"
        elif percentage >= 50:
            bg_color = "yellow"
        else:
            bg_color = "green"

        usage_label = tkinter.Label(
            SelectPlace,
            text=f"{place}: {total_count}/{max_count} ({percentage:.1f}%)",
            bg=bg_color,
            anchor="w",
            width=35
        )
        usage_label.grid(column=0, row=row, columnspan=2, sticky="w", padx=10)

        # Balken-Canvas
        c_width = 200
        c_height = 20
        canvas = tkinter.Canvas(
            SelectPlace,
            width=c_width,
            height=c_height,
            bg="#cccccc",
            highlightthickness=1,
            highlightbackground="black"
        )
        canvas.grid(column=2, row=row, padx=5, pady=2)

        # Rechtecke zeichnen
        x = 0
        for triage, count in triage_counts.items():
            width = (count / max_count) * c_width if max_count > 0 else 0
            color = triage_colors.get(triage, "grey")
            if count > 0:
                canvas.create_rectangle(x, 0, x + width, c_height, fill=color, outline="")
                if width >= 20:
                    canvas.create_text(x + width / 2, c_height / 2, text=str(count), fill="black")
            x += width

        # Vorschlagsberechnung: gewichtete Last (prozentual)
        total_weighted = sum(
            triage_weights.get(triage, 1) * count
            for triage, count in triage_counts.items()
        )
        if max_count > 0:
            relative_load_with_new = (total_weighted + current_weight) / max_count
        else:
            relative_load_with_new = float("inf")

        if relative_load_with_new < lowest_load:
            lowest_load = relative_load_with_new
            suggestion = place

        row += 1

    # Vorschlag anzeigen
    l_suggestion = tkinter.Label(SelectPlace, text=f"Vorschlag: {suggestion}", fg="blue", font=("Arial", 12, "bold"))
    l_suggestion.grid(row=row, column=0, columnspan=2, pady=(10, 5))

    def apply_suggestion():
        place_var.set(suggestion)

    b_apply = tkinter.Button(SelectPlace, text="Vorschlag übernehmen", command=apply_suggestion)
    b_apply.grid(row=row, column=2, pady=(10, 5))

    # Dropdown + aktueller Platz
    row += 1
    place_var = tkinter.StringVar(value=Patlist[index].HSTPlace)
    tkinter.Label(SelectPlace, text="Behandlungsplatz wählen:").grid(row=row, column=0, padx=10, pady=(15, 5), sticky="e")
    places = list(max_counts.keys())
    dropdown = tkinter.OptionMenu(SelectPlace, place_var, *places)
    dropdown.grid(row=row, column=1, pady=(15, 5), sticky="w")

    l_current = tkinter.Label(SelectPlace, text=f"Aktuell: {place_var.get() or '-'}")
    l_current.grid(row=row, column=2, padx=10)

    def update_label(*args):
        l_current.config(text=f"Aktuell: {place_var.get() or '-'}")

    place_var.trace_add("write", update_label)

    def select_place(event=None):
        selected_place = place_var.get()
        if selected_place:
            Patlist[index].setHSTPlace(selected_place)
            l_SelectedPlace.config(text=selected_place)
            SelectPlace.destroy()

    b_select = tkinter.Button(SelectPlace, text="Auswählen", command=select_place)
    b_select.grid(row=row+1, column=0, columnspan=3, pady=10)

    SelectPlace.bind(shortcuts.Confirm, select_place)
    SelectPlace.bind(shortcuts.Cancel, lambda event: SelectPlace.destroy())

    auth.log(f"Behandlungsplatz für Patient Nr. {index} ausgewählt", AmbNum)

# Function to create a new patient
def NewPat():
    """
    Erstellt einen neuen Patienten und fügt ihn zur Liste hinzu.
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        read_list()
        global CurrentPatindex
        global Patlist
        
        new_patient_num = latestpatindex() + 1
        print(f"Neuer Patient mit Ablagenummer {new_patient_num}")
        
        # Validierung: Überprüfen ob Patient bereits existiert
        if any(patient.Num == new_patient_num for patient in Patlist):
            error_msg = f"Patient mit Nummer {new_patient_num} existiert bereits"
            tkinter.messagebox.showerror("Fehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        # Neuen Patienten erstellen
        try:
            new_patient = functions.Patient(new_patient_num)
            Patlist.append(new_patient)
        except Exception as patient_error:
            error_msg = f"Fehler beim Erstellen des Patienten: {patient_error}"
            tkinter.messagebox.showerror("Patientenerstellungsfehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        # Patientenliste speichern
        if not write_list(Patlist):
            # Wenn das Speichern fehlschlägt, Patient wieder entfernen
            Patlist.pop()
            error_msg = "Fehler beim Speichern des neuen Patienten"
            tkinter.messagebox.showerror("Speicherfehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        CurrentPatindex = latestpatindex()
        
        # Sicherstellen, dass CurrentPatindex gültig ist
        if not Patlist or CurrentPatindex >= len(Patlist):
            CurrentPatindex = max(0, latestpatindex())
        
        auth.log(f"Neuer Patient Nr. {CurrentPatindex} angelegt", AmbNum)
        return True
        
    except Exception as e:
        error_msg = f"Unerwarteter Fehler beim Erstellen des Patienten: {str(e)}"
        tkinter.messagebox.showerror("Fehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False

# Function to create a new patient and add them to the end of the list
def NewPat_Button():
    """
    UI-Funktion zum Erstellen eines neuen Patienten mit Bestätigungsdialog.
    """
    try:
        top = tkinter.Toplevel(main_window)
        top.title("Neuer Patient")
        top.focus_force()
        
        # Fenster zentrieren
        top.geometry("300x150")
        top.transient(main_window)
        top.grab_set()
        
        l_newPatinfo = tkinter.Label(top, text="Wollen Sie einen neuen Patienten anlegen?")
        l_newPatinfo.pack(pady=20)

        def create_patient():
            try:
                if NewPat():
                    Update_lables()
                    top.destroy()
                    # Nur bei erfolgreichem Erstellen den Editor öffnen
                    Edit_pat(CurrentPatindex)
                else:
                    # Fehler wurde bereits in NewPat() behandelt
                    pass
            except Exception as e:
                error_msg = f"Fehler beim Erstellen des Patienten: {str(e)}"
                tkinter.messagebox.showerror("Fehler", error_msg)
                auth.log(f"Fehler: {error_msg}", AmbNum)

        def cancel_creation():
            try:
                top.destroy()
            except Exception as e:
                auth.log(f"Fehler beim Schließen des Dialogs: {str(e)}", AmbNum)

        button_frame = tkinter.Frame(top)
        button_frame.pack(pady=10)

        b_OK = tkinter.Button(button_frame, text="Ja", command=create_patient, width=10)
        b_OK.pack(side="left", padx=10)

        b_Cancel = tkinter.Button(button_frame, text="Nein", command=cancel_creation, width=10)
        b_Cancel.pack(side="left", padx=10)

        # Keyboard shortcuts
        top.bind(shortcuts.Confirm, lambda event: create_patient())
        top.bind(shortcuts.Cancel, lambda event: cancel_creation())
        
        # Focus auf den OK-Button
        b_OK.focus_set()
        
    except Exception as e:
        error_msg = f"Fehler beim Öffnen des Patientenerstellungs-Dialogs: {str(e)}"
        tkinter.messagebox.showerror("UI-Fehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)

# Function to delete the current patient
def DelPat():
    """
    Löscht den aktuellen Patienten aus der Liste.
    Diese Funktion war vorher leer - jetzt implementiert.
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    global CurrentPatindex
    global Patlist
    
    try:
        if not Patlist or CurrentPatindex < 0 or CurrentPatindex >= len(Patlist):
            error_msg = "Kein gültiger Patient zum Löschen ausgewählt"
            tkinter.messagebox.showerror("Fehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        if CurrentPatindex == 0:
            error_msg = "Der Geisterpatient (Patient 0) kann nicht gelöscht werden"
            tkinter.messagebox.showerror("Fehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        # Bestätigung vom Benutzer
        patient_num = Patlist[CurrentPatindex].Num
        if not tkinter.messagebox.askyesno("Patient löschen", 
                                          f"Möchten Sie den Patienten Nr. {patient_num} wirklich löschen?"):
            return False
        
        # Patient löschen
        deleted_patient = Patlist.pop(CurrentPatindex)
        
        # Patientennummern neu zuordnen
        try:
            for i, patient in enumerate(Patlist):
                patient.setNum(i)
        except Exception as renumber_error:
            # Patient wieder hinzufügen, falls Neunummerierung fehlschlägt
            Patlist.insert(CurrentPatindex, deleted_patient)
            error_msg = f"Fehler beim Neunummerieren der Patienten: {renumber_error}"
            tkinter.messagebox.showerror("Fehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        # Liste speichern
        if not write_list(Patlist):
            # Patient wieder hinzufügen, falls Speichern fehlschlägt
            Patlist.insert(CurrentPatindex, deleted_patient)
            error_msg = "Fehler beim Speichern nach dem Löschen"
            tkinter.messagebox.showerror("Speicherfehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        # CurrentPatindex anpassen
        if CurrentPatindex >= len(Patlist):
            CurrentPatindex = max(0, len(Patlist) - 1)
        
        auth.log(f"Patient Nr. {patient_num} gelöscht", AmbNum)
        return True
        
    except Exception as e:
        error_msg = f"Unerwarteter Fehler beim Löschen des Patienten: {str(e)}"
        tkinter.messagebox.showerror("Fehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False

def DelPat_Button():
    """
    UI-Funktion zum Löschen des aktuellen Patienten.
    """
    try:
        if DelPat():
            Update_lables()
    except Exception as e:
        error_msg = f"Fehler beim Löschen des Patienten: {str(e)}"
        tkinter.messagebox.showerror("Fehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)

# Function to create a new Betreuung
def NewBetreuung():
    global Betreuungen
    global filepath
    setDatfromFile(filepath)
    Betreuungen = Betreuungen + 1
    print("Neue Betreuung mit der Nummer", Betreuungen)
    saveDatinFile(filepath)
    auth.log(f"Neue Betreuung Nr. {Betreuungen} angelegt", AmbNum)

def NewBetreuung_Button():
    NewBetreuung()
    Update_lables()

# Function to delete a Betreuung
def DelBetreuung():
    global Betreuungen
    if Betreuungen > 0:
        Betreuungen = Betreuungen - 1
        print("Eine Betreuung gelöscht, die Neue Nummer ist nun ", Betreuungen, " Betreuungen")
        saveDatinFile(filepath)
        auth.log(f"Eine betreuung gelöscht", AmbNum)

def DelBetreuung_Button():
    DelBetreuung()
    Update_lables()

# Function to initialize statistics
def Init_Stats():
    Init = tkinter.Toplevel(main_window)
    Init.title("Ambulanzdaten eingeben")
    Init.focus_force()

    l_textr4 = tkinter.Label(Init, text="Ambulanznummer:")
    l_textr4.grid(column=0, row=0)
    e_AmbNr = tkinter.Entry(Init)
    e_AmbNr.insert(0, AmbNum)
    e_AmbNr.grid(column=1, row=0)

    l_textr5 = tkinter.Label(Init, text="Ambulanzname:")
    l_textr5.grid(column=0, row=1)
    e_AmbNam = tkinter.Entry(Init)
    e_AmbNam.insert(0, AmbName)
    e_AmbNam.grid(column=1, row=1)

    l_textr6 = tkinter.Label(Init, text="Datum der Ambulanz:")
    l_textr6.grid(column=0, row=2)
    e_AmbDate = tkinter.Entry(Init)
    e_AmbDate.insert(0, AmbDate)
    e_AmbDate.grid(column=1, row=2)

    l_places = tkinter.Label(Init, text="Behandlungsplätze:")
    l_places.grid(column=0, row=3, columnspan=3)

    place_entries = []
    max_count_entries = []
    remove_buttons = []

    auth.log("Ambulanzdaten initialisiert", AmbNum)

    # Function to add a new place row
    def add_place_row(place="", max_count=""):
        row = len(place_entries) + 4
        e_place = tkinter.Entry(Init)
        e_place.insert(0, place)
        e_place.grid(column=0, row=row)
        e_max_count = tkinter.Entry(Init)
        e_max_count.insert(0, max_count)
        e_max_count.grid(column=1, row=row)
        place_entries.append(e_place)
        max_count_entries.append(e_max_count)
        
        b_remove = tkinter.Button(Init, text="Entfernen", command=lambda: remove_place_row(row))
        b_remove.grid(column=2, row=row)
        remove_buttons.append(b_remove)

    # Function to remove a place row
    def remove_place_row(row):
        place = place_entries[row - 4].get()
        if any(patient.HSTPlace == place and patient.Endt == "-" for patient in Patlist):
            tkinter.messagebox.showerror("Fehler", f"Behandlungsplatz '{place}' kann nicht entfernt werden, da Patienten dort sind.")
            return
        place_entries[row - 4].grid_forget()
        max_count_entries[row - 4].grid_forget()
        remove_buttons[row - 4].grid_forget()
        place_entries.pop(row - 4)
        max_count_entries.pop(row - 4)
        remove_buttons.pop(row - 4)

    for place, max_count in max_counts.items():
        add_place_row(place, max_count)

    b_add_place = tkinter.Button(Init, text="Platz hinzufügen", command=add_place_row)
    b_add_place.grid(column=0, row=len(place_entries) + 10)

    # Function to save statistics
    def save_stats():
        setNum(e_AmbNr.get())
        setName(e_AmbNam.get())
        setDate(e_AmbDate.get())
        global max_counts
        max_counts = {}
        for e_place, e_max_count in zip(place_entries, max_count_entries):
            place = e_place.get()
            max_count = e_max_count.get()
            if place and max_count:
                max_counts[place] = int(max_count)
        Update_lables()
        Init.destroy()

        auth.log("Ambulanzdaten gespeichert", AmbNum)

    b_OK = tkinter.Button(Init, text="OK", command=save_stats)
    b_Cancel = tkinter.Button(Init, text="Abbruch", command=Init.destroy)

    b_OK.grid(row=len(place_entries) + 11, column=1)
    b_Cancel.grid(row=len(place_entries) + 11, column=0)

    # Add keyboard shortcuts
    Init.bind(shortcuts.Confirm, lambda event: save_stats())
    Init.bind(shortcuts.Cancel, lambda event: Init.destroy())

# Function to write the patient list to a file
def write_list(list):
    """
    Schreibt die Patientenliste verschlüsselt in eine Datei.
    
    Args:
        list: Liste der Patienten
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    global AmbName
    global AmbDate
    global AmbNum

    try:
        if not AmbNum or not re.search(r'\d', AmbNum):
            tkinter.messagebox.showerror("Fehler", "Ambulanznummer ist nicht gesetzt oder ungültig.")
            auth.log("Fehler: Ambulanznummer nicht gesetzt beim Speichern", AmbNum)
            return False

        filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"
        
        # Sicherstellen, dass das Verzeichnis existiert
        os.makedirs("PatDat", exist_ok=True)
        
        # Backup der vorherigen Datei erstellen, falls sie existiert
        if os.path.exists(filepath):
            backup_filepath = filepath + ".backup"
            try:
                import shutil
                shutil.copy2(filepath, backup_filepath)
                auth.log(f"Backup erstellt: {backup_filepath}", AmbNum)
            except Exception as backup_error:
                auth.log(f"Warnung: Backup konnte nicht erstellt werden: {backup_error}", AmbNum)

        write_encrypted(filepath, list, fernet)
        auth.log(f"Patientenliste in Datei '{filepath}' geschrieben", AmbNum)
        return True
        
    except PermissionError:
        error_msg = f"Keine Berechtigung zum Schreiben in Datei '{filepath}'"
        tkinter.messagebox.showerror("Berechtigungsfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False
    except FileNotFoundError:
        error_msg = f"Verzeichnis für Datei '{filepath}' konnte nicht erstellt werden"
        tkinter.messagebox.showerror("Dateifehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False
    except Exception as e:
        error_msg = f"Unerwarteter Fehler beim Speichern: {str(e)}"
        tkinter.messagebox.showerror("Speicherfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False

def read_list():
    """
    Liest die Patientenliste aus einer verschlüsselten Datei.
    
    Returns:
        list: Liste der Patienten oder leere Liste bei Fehler
    """
    global AmbNum
    global Patlist
    global CurrentPatindex

    try:
        if not AmbNum or not re.search(r'\d', AmbNum):
            error_msg = "Ambulanznummer ist nicht gesetzt oder ungültig."
            tkinter.messagebox.showerror("Fehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return []

        filename = re.sub('[^0-9]', '', AmbNum) + ".ambdat"
        filepath = os.path.join("PatDat", filename)

        # Sicherstellen, dass das Verzeichnis existiert
        os.makedirs("PatDat", exist_ok=True)

        # Wenn die Datei nicht existiert → leer initialisieren & verschlüsseln
        if not os.path.exists(filepath):
            try:
                write_encrypted(filepath, Patlist, fernet)
                print(f"Leere Datei verschlüsselt erstellt: {filepath}")
                auth.log(f"Neue verschlüsselte Datei erstellt: {filepath}", AmbNum)
                return Patlist
            except Exception as create_error:
                error_msg = f"Fehler beim Erstellen der neuen Datei: {create_error}"
                tkinter.messagebox.showerror("Dateierstellungsfehler", error_msg)
                auth.log(f"Fehler: {error_msg}", AmbNum)
                return []

        try:
            Patlist = read_encrypted(filepath, fernet)
            auth.log(f"Patientenliste aus Datei '{filepath}' gelesen", AmbNum)
        except Exception as decrypt_error:
            error_msg = f"Fehler beim Entschlüsseln der Datei: {decrypt_error}"
            tkinter.messagebox.showerror("Entschlüsselungsfehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            
            # Versuche Backup zu laden, falls vorhanden
            backup_filepath = filepath + ".backup"
            if os.path.exists(backup_filepath):
                try:
                    Patlist = read_encrypted(backup_filepath, fernet)
                    tkinter.messagebox.showinfo("Backup wiederhergestellt", 
                                               "Die Hauptdatei war beschädigt, aber das Backup konnte wiederhergestellt werden.")
                    auth.log(f"Patientenliste aus Backup '{backup_filepath}' wiederhergestellt", AmbNum)
                except Exception as backup_error:
                    error_msg = f"Auch das Backup konnte nicht geladen werden: {backup_error}"
                    tkinter.messagebox.showerror("Backup-Fehler", error_msg)
                    auth.log(f"Fehler: {error_msg}", AmbNum)
                    return []
            else:
                return []

        if not Patlist:
            Pat0()

        # Sicherstellen, dass CurrentPatindex gültig ist
        if not Patlist or CurrentPatindex >= len(Patlist):
            CurrentPatindex = max(0, latestpatindex())

        return Patlist

    except PermissionError:
        error_msg = f"Keine Berechtigung zum Lesen der Datei '{filepath}'"
        tkinter.messagebox.showerror("Berechtigungsfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return []
    except Exception as e:
        error_msg = f"Unerwarteter Fehler beim Laden: {str(e)}"
        tkinter.messagebox.showerror("Ladefehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return []



def Button_read_list():
    global Patlist
    global CurrentPatindex
    Patlist = read_list()
    #CurrentPatindex = 0
    Update_lables()

def ExportPatlist():
    """
    Exportiert die Patientenliste als CSV-Datei.
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        if not Patlist:
            tkinter.messagebox.showwarning("Warnung", "Keine Patienten zum Exportieren vorhanden.")
            return False
        
        if not AmbNum or not AmbName:
            error_msg = "Ambulanznummer oder -name ist nicht gesetzt"
            tkinter.messagebox.showerror("Fehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        # Sicherstellen, dass das Export-Verzeichnis existiert
        export_dir = 'Userdata/Export'
        os.makedirs(export_dir, exist_ok=True)
        
        # Dateipfad erstellen
        safe_ambnum = re.sub(r'\W+', '_', AmbNum)
        safe_ambname = re.sub(r'\W+', '_', AmbName)
        path = os.path.join(export_dir, f"{safe_ambnum}_{safe_ambname}.csv")
        
        # CSV-Export
        try:
            with open(path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                
                # Header schreiben
                writer.writerow([
                    "Pat-Nr", "Alarmzeit", "B.Grund", "BO", "BO-Zeit", 
                    "HST-Zeit", "Sichtungs-Kat", "Behandlungsstelle", 
                    "Abtransport", "NACA", "Fertig", "Kommentar", 
                    f"{Betreuungen} Betreuungen"
                ])
                
                # Patientendaten schreiben
                exported_count = 0
                for patient in Patlist:
                    if patient.Num > 0:  # Patient 0 nicht exportieren
                        try:
                            is_finished = "Ja" if patient.finished else "Nein"
                            
                            writer.writerow([
                                patient.Num,
                                patient.Alarmt,
                                patient.Alarmstr,
                                patient.BOplace,
                                patient.BOt,
                                patient.HSTt,
                                patient.Triage,
                                patient.HSTPlace,
                                patient.TransportAgency,
                                patient.Naca,
                                is_finished,
                                patient.Comment
                            ])
                            exported_count += 1
                        except Exception as row_error:
                            auth.log(f"Fehler beim Exportieren von Patient {patient.Num}: {row_error}", AmbNum)
                            continue
                
                if exported_count == 0:
                    error_msg = "Keine gültigen Patienten zum Exportieren gefunden"
                    tkinter.messagebox.showerror("Fehler", error_msg)
                    auth.log(f"Fehler: {error_msg}", AmbNum)
                    return False
        
        except PermissionError:
            error_msg = f"Keine Berechtigung zum Schreiben in Datei '{path}'"
            tkinter.messagebox.showerror("Berechtigungsfehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        except UnicodeEncodeError:
            # Fallback auf ANSI-Encoding versuchen
            try:
                with open(path, 'w', newline='', encoding='ansi') as csvfile:
                    writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    # Header und Daten erneut schreiben (vereinfacht)
                    writer.writerow(["Pat-Nr", "Alarmzeit", "Kommentar", f"{Betreuungen} Betreuungen"])
                    for patient in Patlist:
                        if patient.Num > 0:
                            writer.writerow([patient.Num, patient.Alarmt, patient.Comment])
            except Exception as fallback_error:
                error_msg = f"Encoding-Fehler beim Export: {fallback_error}"
                tkinter.messagebox.showerror("Encoding-Fehler", error_msg)
                auth.log(f"Fehler: {error_msg}", AmbNum)
                return False
        
        print(f"Daten in Datei geschrieben: {path}")
        tkinter.messagebox.showinfo("Export erfolgreich", f"Patientenliste wurde nach '{path}' exportiert.")
        auth.log(f"Patientenliste nach '{path}' exportiert", AmbNum)
        return True
        
    except Exception as e:
        error_msg = f"Unerwarteter Fehler beim Export: {str(e)}"
        tkinter.messagebox.showerror("Export-Fehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False

def setDatfromFile(path):
    """
    Lädt Ambulanzdaten aus einer Datei.
    
    Args:
        path: Dateipfad zum Laden
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    global AmbNum, AmbName, AmbDate, Betreuungen, max_counts, filepath, CurrentPatindex
    
    try:
        if not path or not os.path.exists(path):
            error_msg = f"Datei '{path}' existiert nicht"
            tkinter.messagebox.showerror("Dateifehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        filepath = path
        
        with open(path, "r", encoding='utf-8') as file:
            lines = file.readlines()
            
            if len(lines) < 4:
                error_msg = f"Datei '{path}' hat ein ungültiges Format (zu wenige Zeilen)"
                tkinter.messagebox.showerror("Formatfehler", error_msg)
                auth.log(f"Fehler: {error_msg}", AmbNum)
                return False
            
            try:
                AmbNum = lines[0].strip()
                AmbName = lines[1].strip()
                AmbDate = lines[2].strip()
                Betreuungen = int(lines[3].strip())
            except (ValueError, IndexError) as parse_error:
                error_msg = f"Fehler beim Parsen der Grunddaten: {parse_error}"
                tkinter.messagebox.showerror("Formatfehler", error_msg)
                auth.log(f"Fehler: {error_msg}", AmbNum)
                return False
            
            # Behandlungsplätze laden
            max_counts = {}
            for line_num, line in enumerate(lines[4:], start=5):
                line = line.strip()
                if ':' in line:
                    try:
                        place, max_count = line.split(":", 1)
                        max_counts[place] = int(max_count)
                    except (ValueError, IndexError) as place_error:
                        auth.log(f"Warnung: Ungültiger Behandlungsplatz in Zeile {line_num}: {place_error}", AmbNum)
                        continue
        
        # Patientenliste zurücksetzen
        Patlist.clear()
        Pat0()
        CurrentPatindex = 0
        
        # Sicherstellen, dass CurrentPatindex gültig ist
        if not Patlist or CurrentPatindex >= len(Patlist):
            CurrentPatindex = max(0, latestpatindex())
        
        print(f"Daten aus Datei gelesen: {path}")
        auth.log(f"Ambulanzdaten aus '{path}' geladen", AmbNum)
        return True
        
    except PermissionError:
        error_msg = f"Keine Berechtigung zum Lesen der Datei '{path}'"
        tkinter.messagebox.showerror("Berechtigungsfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False
    except UnicodeDecodeError:
        # Fallback auf andere Encodings versuchen
        try:
            with open(path, "r", encoding='ansi') as file:
                lines = file.readlines()
                # Vereinfachte Verarbeitung für Fallback
                if len(lines) >= 4:
                    AmbNum = lines[0].strip()
                    AmbName = lines[1].strip()
                    AmbDate = lines[2].strip()
                    Betreuungen = int(lines[3].strip())
                    return True
        except Exception as fallback_error:
            error_msg = f"Encoding-Fehler beim Laden: {fallback_error}"
            tkinter.messagebox.showerror("Encoding-Fehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
    except Exception as e:
        error_msg = f"Unerwarteter Fehler beim Laden: {str(e)}"
        tkinter.messagebox.showerror("Ladefehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False

def Button_setDat():
    """
    UI-Funktion zum Laden von Ambulanzdaten aus einer Datei.
    """
    try:
        file_dialog = tkinter.filedialog.askopenfile(filetypes=[("Data-Datei", "*.dat")])
        if file_dialog is None:
            # Benutzer hat abgebrochen
            return
        
        filepath = file_dialog.name
        file_dialog.close()
        
        if not os.path.exists(filepath):
            error_msg = f"Datei '{filepath}' existiert nicht"
            tkinter.messagebox.showerror("Dateifehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return
        
        setDatfromFile(filepath)
        Button_read_list()
        Update_lables()
        
    except PermissionError:
        error_msg = "Keine Berechtigung zum Lesen der ausgewählten Datei"
        tkinter.messagebox.showerror("Berechtigungsfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
    except Exception as e:
        error_msg = f"Fehler beim Laden der Datei: {str(e)}"
        tkinter.messagebox.showerror("Ladefehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)

def saveDatinFile(path):
    """
    Speichert Ambulanzdaten in eine Datei.
    
    Args:
        path: Dateipfad zum Speichern
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    global AmbNum, AmbName, AmbDate, Betreuungen, max_counts
    
    try:
        if not path:
            error_msg = "Kein Dateipfad angegeben"
            tkinter.messagebox.showerror("Fehler", error_msg)
            auth.log(f"Fehler: {error_msg}", AmbNum)
            return False
        
        # Verzeichnis erstellen, falls es nicht existiert
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(path, "w", encoding='utf-8') as file:
            file.write(f"{AmbNum}\n")
            file.write(f"{AmbName}\n")
            file.write(f"{AmbDate}\n")
            file.write(f"{Betreuungen}\n")
            
            for place, count in max_counts.items():
                if place and str(count).isdigit():
                    file.write(f"{place}:{count}\n")
        
        print(f"Daten in Datei geschrieben: {path}")
        auth.log(f"Ambulanzdaten in '{path}' gespeichert", AmbNum)
        return True
        
    except PermissionError:
        error_msg = f"Keine Berechtigung zum Schreiben in Datei '{path}'"
        tkinter.messagebox.showerror("Berechtigungsfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False
    except Exception as e:
        error_msg = f"Unerwarteter Fehler beim Speichern: {str(e)}"
        tkinter.messagebox.showerror("Speicherfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
        return False

def Button_saveasDat():
    """
    UI-Funktion zum Speichern von Ambulanzdaten unter einem neuen Namen.
    """
    try:
        file_dialog = tkinter.filedialog.asksaveasfile(
            filetypes=[("Data-Datei", "*.dat")],
            defaultextension=".dat"
        )
        if file_dialog is None:
            # Benutzer hat abgebrochen
            return
        
        global filepath
        filepath = file_dialog.name
        file_dialog.close()
        
        if not saveDatinFile(filepath):
            error_msg = "Fehler beim Speichern der Datei"
            tkinter.messagebox.showerror("Speicherfehler", error_msg)
            return
        
        Button_read_list()
        Update_lables()
        print(f"Datei gespeichert unter: {filepath}")
        
    except PermissionError:
        error_msg = "Keine Berechtigung zum Schreiben in den ausgewählten Ordner"
        tkinter.messagebox.showerror("Berechtigungsfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)
    except Exception as e:
        error_msg = f"Fehler beim Speichern: {str(e)}"
        tkinter.messagebox.showerror("Speicherfehler", error_msg)
        auth.log(f"Fehler: {error_msg}", AmbNum)

def Button_saveDat():
    global filepath
    saveDatinFile(filepath)
    Button_read_list()
    Update_lables()

def Patstats():
    stats = tkinter.Toplevel(main_window)
    stats.title("Statistik")
    stats.focus_force()

    naca_counts = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}}
    for patient in Patlist:
        if patient.Num != 0:
            naca = int(patient.Naca)
            place = patient.HSTPlace
            if place in naca_counts[naca]:
                naca_counts[naca][place] += 1
            else:
                naca_counts[naca][place] = 1

    row = 0
    for naca, places in naca_counts.items():
        naca_label = tkinter.Label(stats, text=f"NACA {naca}:")
        naca_label.grid(column=0, row=row)
        row += 1
        for place, count in places.items():
            place_label = tkinter.Label(stats, text=f"  {place}: {count} Patienten")
            place_label.grid(column=0, row=row)
            row += 1
    auth.log("Patientenstatistik angezeigt", AmbNum)

def DisplayPatientsInPlace():
    global max_counts
    place_counts = {place: 0 for place in max_counts}

    for patient in Patlist:
        if patient.Num != 0 and patient.Endt == "-":
            place = patient.HSTPlace
            if place in place_counts:
                place_counts[place] += 1
            else:
                place_counts[place] = 1

    place_window = tkinter.Toplevel(main_window)
    place_window.title("Patienten in Behandlungsplätzen")
    place_window.focus_force()

    row = 0
    for place, count in place_counts.items():
        max_count = max_counts.get(place, 1)  # Default to 1 to avoid division by zero
        percentage = (count / max_count) * 100
        
        progress = tkinter.ttk.Progressbar(place_window, length=200, mode='determinate')
        progress['value'] = percentage
        progress.grid(column=2, row=row)
        
        if percentage >= 80:
            progress_style = 'red.Horizontal.TProgressbar'
            bg_color = 'red'
        elif percentage >= 50:
            progress_style = 'yellow.Horizontal.TProgressbar'
            bg_color = 'yellow'
        else:
            progress_style = 'green.Horizontal.TProgressbar'
            bg_color = 'green'
        
        style = tkinter.ttk.Style()
        style.configure(progress_style, background=progress_style.split('.')[0])
        progress['style'] = progress_style
        
        place_label = tkinter.Label(place_window, text=f"{place}: {count} von {max_count} Plätzen belegt ({percentage:.2f}%)", bg=bg_color)
        place_label.grid(column=0, row=row)
        row += 1

    place_window.bind(shortcuts.Cancel, lambda event: place_window.destroy())

def DetailedStats(patlist, betreuungen):
    global max_counts
    global filepath
    global main_window

    # Toplevel-Fenster
    fenster = tkinter.Toplevel(main_window)
    fenster.title("Detaillierte Statistik")
    fenster.focus_force()

    # Statistische Zählung vorbereiten
    naca_counts = {n: {} for n in range(1, 8)}
    all_places = set()

    for patient in patlist:
        if patient.Num == 0 or patient.Endt == "-":
            continue
        try:
            naca = int(patient.Naca)
            if 1 <= naca <= 7:
                place = patient.HSTPlace
                all_places.add(place)
                naca_counts[naca][place] = naca_counts[naca].get(place, 0) + 1
        except (ValueError, TypeError):
            continue

    # Behandlungsstellen sortieren
    sorted_places = sorted(
        all_places,
        key=lambda place: list(max_counts.keys()).index(place) if place in max_counts else len(max_counts)
    )

    # Kopfzeile (NACA 1–7 + Summe)
    for col, naca in enumerate(range(1, 8), start=1):
        tkinter.Label(fenster, text=f"NACA {naca}  |", anchor="w").grid(column=col, row=0, sticky="w")
    tkinter.Label(fenster, text="Summe", anchor="w").grid(column=8, row=0, sticky="w")

    # Zeilen für jede Behandlungsstelle
    row = 1
    for place in sorted_places:
        tkinter.Label(fenster, text=place + ":", anchor="w").grid(column=0, row=row, sticky="w")
        place_sum = 0
        for col, naca in enumerate(range(1, 8), start=1):
            count = naca_counts[naca].get(place, 0)
            place_sum += count
            tkinter.Label(fenster, text=str(count), anchor="w").grid(column=col, row=row, sticky="w")
        tkinter.Label(fenster, text=str(place_sum), anchor="w").grid(column=8, row=row, sticky="w")

        # Trennlinie
        row += 1
        tkinter.Frame(fenster, height=1, bd=1, relief="sunken", background="black").grid(column=0, row=row, columnspan=9, sticky="ew", pady=2)
        row += 1

    # Summe aller NACA-Werte
    total_counts = {naca: sum(naca_counts[naca].values()) for naca in range(1, 8)}
    total_sum = sum(total_counts.values())

    # Trennlinie vor Gesamtsumme
    tkinter.Frame(fenster, height=2, bd=1, relief="sunken", background="black").grid(column=0, row=row, columnspan=9, sticky="ew", pady=5)
    row += 1

    tkinter.Label(fenster, text="Summe:", anchor="w").grid(column=0, row=row, sticky="w")
    for col, naca in enumerate(range(1, 8), start=1):
        tkinter.Label(fenster, text=str(total_counts[naca]), anchor="w").grid(column=col, row=row, sticky="w")
    tkinter.Label(fenster, text=str(total_sum), anchor="w").grid(column=8, row=row, sticky="w")

    # Betreuungen
    tkinter.Label(fenster, text=f"Betreuungen: {betreuungen}", anchor="w").grid(column=0, row=row+1, sticky="w")

    # Tortendiagramm
    def tortendiagramm_zeigen(data, title, zeile, spalte):
        fig, ax = plt.subplots(figsize=(4, 4))
        gefiltert = {k: v for k, v in data.items() if v > 0}
        labels = [f"NACA {k}" for k in gefiltert]
        sizes = list(gefiltert.values())
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis("equal")
        ax.set_title(title)
        canvas = FigureCanvasTkAgg(fig, master=fenster)
        canvas.draw()
        canvas.get_tk_widget().grid(column=spalte, row=zeile, padx=10, pady=10)

    tortendiagramm_zeigen(total_counts, "Summe", row+2, 10)

    # Schließen per Tastendruck
    fenster.bind(shortcuts.Cancel, lambda e: fenster.destroy())

    # Logging
    auth.log("Detaillierte Statistik angezeigt", AmbNum)

# Function to create x patients with random Triage Categories
def CreateRandomPatients(x):
    global CurrentPatindex
    for _ in range(x):
        new_patient = functions.Patient(latestpatindex() + 1)
        new_patient.setTriage(random.choice(TriageCategories[1:]))  # Exclude the "-" option
        new_patient.setNaca(random.randint(1, 7))  # Choose a random NACA from 1 to 7
        Patlist.append(new_patient)
        CurrentPatindex =+ 1
    Update_lables()
    auth.log(f"{x} zufällige Patienten erstellt", AmbNum)

patient_list_section_frame = tkinter.LabelFrame(main_window, text="Patientenliste & Filter", padx=10, pady=10)
patient_list_section_frame.grid(row=0, column=4, rowspan=21, columnspan=20, sticky="nsew", padx=5, pady=5)
patient_list_section_frame.grid_rowconfigure(1, weight=1)


main_window.grid_columnconfigure(4, weight=1)
patient_list_section_frame.grid_columnconfigure(0, weight=1)
main_window.grid_rowconfigure(0, weight=1)
patient_list_section_frame.grid_rowconfigure(0, minsize=30)

# Filter-Button ins neue Frame
b_open_filter_menu = tkinter.Button(patient_list_section_frame, text="Filter Menü öffnen", command=open_filter_menu)
b_open_filter_menu.grid(row=0, column=0, sticky="nw", padx=(5, 0))

# Canvas + Scrollbar ins neue Frame
patient_list_canvas = tkinter.Canvas(patient_list_section_frame)
patient_list_frame = tkinter.Frame(patient_list_canvas)
scrollbar = tkinter.Scrollbar(patient_list_section_frame, orient="vertical", command=patient_list_canvas.yview)
patient_list_canvas.configure(yscrollcommand=scrollbar.set)

# Grid-Anordnung
patient_list_canvas.grid(row=1, column=0, sticky="nsew")
scrollbar.grid(row=1, column=1, sticky="ns")
patient_list_canvas.create_window((0, 0), window=patient_list_frame, anchor="nw")

patient_list_canvas.configure(width=1, height=1)  # Hilft bei automatischer Breite/Höhe
def on_frame_configure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

patient_list_frame.bind("<Configure>", lambda event, canvas=patient_list_canvas: on_frame_configure(canvas))


def open_menu_window():
    menu_window = tkinter.Toplevel(main_window)
    menu_window.title("Menü")
    menu_window.focus_force()

    b_init = tkinter.Button(menu_window, text="Daten konfigurieren", command=lambda:[Init_Stats(), menu_window.destroy()])
    b_init.grid(row=0, column=0)

    b_loaddat = tkinter.Button(menu_window, text="Daten lesen", command=lambda:[Button_setDat(), menu_window.destroy()])
    b_loaddat.grid(row=3, column=0)

    b_savedat = tkinter.Button(menu_window, text="Daten speichern", command=lambda:[Button_saveDat(), menu_window.destroy()])
    b_savedat.grid(row=2, column=0)

    b_saveasdat = tkinter.Button(menu_window, text="Daten speichern als", command=lambda:[Button_saveasDat(), menu_window.destroy()])
    b_saveasdat.grid(row=1, column=0)

    b_save = tkinter.Button(menu_window, text="Patienten speichern", command=lambda:[write_list(Patlist), menu_window.destroy()])
    b_save.grid(row=2, column=1)

    b_load = tkinter.Button(menu_window, text="Patienten laden", command=lambda:[Button_read_list(), menu_window.destroy()])
    b_load.grid(row=3, column=1)

    b_export = tkinter.Button(menu_window, text="Patienten Exportieren (csv)", command=lambda:[ExportPatlist(), menu_window.destroy()])
    b_export.grid(row=1, column=1)

    b_stats = tkinter.Button(menu_window, text="Statistik anzeigen", command=lambda:[read_list(), Update_lables(), DetailedStats(Patlist, Betreuungen), menu_window.destroy()])
    b_stats.grid(row=0, column=1)

    l_Update = tkinter.Label(menu_window, text="Letztes Patienten Update: " + lastUpdate)
    l_Update.grid(column=0, row=5)
    l_version = tkinter.Label(menu_window, text="AMB-Dash-Version: "+Version)
    l_version.grid(column=0, row=6)

    b_create_random_patients = tkinter.Button(menu_window, text="Erstelle zufällige Patienten", command=lambda: [CreateRandomPatients(10), menu_window.destroy()])
    b_create_random_patients.grid(row=10, column=0)

# Create frames for the buttons and labels
# ------------------------- Frames -------------------------

ambulance_info_frame = tkinter.LabelFrame(main_window, text="Ambulanz-Informationen", padx=10, pady=5)
ambulance_info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

patient_info_frame = tkinter.LabelFrame(main_window, text="Patientenübersicht", padx=10, pady=5)
patient_info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

button_frame = tkinter.LabelFrame(main_window, text="Betreuung verwalten", padx=10, pady=5)
button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

# ------------------------- Ambulanzdaten -------------------------

l_AmbNum = tkinter.Label(ambulance_info_frame, text=AmbNum, font=("Helvetica", 12, "bold"))
l_AmbNum.grid(row=0, column=0, sticky="w")

l_AmbName = tkinter.Label(ambulance_info_frame, text=AmbName, font=("Helvetica", 12, "bold"))
l_AmbName.grid(row=1, column=0, sticky="w")

l_AmbDate = tkinter.Label(ambulance_info_frame, text=AmbDate, font=("Helvetica", 12, "bold"))
l_AmbDate.grid(row=2, column=0, sticky="w")

b_open_menu = tkinter.Button(ambulance_info_frame, text="Menü öffnen", command=open_menu_window)
b_open_menu.grid(row=0, column=1, rowspan=3, padx=10)

# ------------------------- Patientenübersicht -------------------------

labels = [
    ("Aktuell Angezeigter Pat Nr:", lambda: Patlist[CurrentPatindex].Num),
    ("Einsatzbeginn:", lambda: Patlist[CurrentPatindex].Alarmt),
    ("Berufungsgrund:", lambda: Patlist[CurrentPatindex].Alarmstr),
    ("Berufungsort:", lambda: Patlist[CurrentPatindex].BOplace),
    ("Zeit am BO:", lambda: Patlist[CurrentPatindex].BOt),
    ("Sichtungs-Kategorie:", lambda: Patlist[CurrentPatindex].Triage),
    ("Zeit auf der Behandlung:", lambda: Patlist[CurrentPatindex].HSTt),
    ("Behandlungsplatz:", lambda: Patlist[CurrentPatindex].HSTPlace),
    ("Abtransport:", lambda: Patlist[CurrentPatindex].TransportAgency),
    ("Einsatzende:", lambda: Patlist[CurrentPatindex].Endt),
    ("Protokoll fertig:", lambda: Patlist[CurrentPatindex].finished),
    ("NACA:", lambda: Patlist[CurrentPatindex].Naca),
    ("Name/Kommentar:", lambda: Patlist[CurrentPatindex].Comment),
]

label_refs = {}  # dict für spätere Updates

for i, (text, get_value) in enumerate(labels):
    tkinter.Label(patient_info_frame, text=text).grid(row=i+1, column=0, sticky="e", padx=5, pady=2)
    value_label = tkinter.Label(patient_info_frame, text=str(get_value()))
    value_label.grid(row=i+1, column=1, sticky="w", padx=5, pady=2)
    label_refs[text] = value_label  # Text ist der Key, z. B. "Einsatzbeginn:"

# Patientenanzahl + Neuer Patient
l_Pat = tkinter.Label(patient_info_frame, text=f"{latestpatindex()} Patienten")
l_Pat.grid(row=0, column=0, sticky="w")

b_newPat = tkinter.Button(patient_info_frame, text="Neuer Patient", command=lambda: (Button_read_list(), NewPat_Button()), bg="red")
b_newPat.grid(row=0, column=1, sticky="e")

# Navigation und Bearbeiten
b_prevPat = tkinter.Button(patient_info_frame, text="<", width=15, command=PrevPat_Button)
b_prevPat.grid(row=len(labels)+2, column=0, padx=5, pady=10)

b_EditPat = tkinter.Button(patient_info_frame, text="Pat Bearbeiten", width=15, command=lambda: Edit_pat(CurrentPatindex))
b_EditPat.grid(row=len(labels)+2, column=1, padx=5, pady=10)

b_nextPat = tkinter.Button(patient_info_frame, text=">", width=15, command=NextPat_Button)
b_nextPat.grid(row=len(labels)+2, column=2, padx=5, pady=10)

# ------------------------- Betreuung -------------------------

b_DelBet = tkinter.Button(button_frame, text="Betreuung Löschen", command=DelBetreuung_Button, bg="green")
b_DelBet.grid(column=0, row=0, padx=5, pady=5)

l_Betreuungen = tkinter.Label(button_frame, text=str(Betreuungen) + " Betreuungen")
l_Betreuungen.grid(column=1, row=0, padx=5)

b_newBet = tkinter.Button(button_frame, text="Neue Betreuung", command=NewBetreuung_Button, bg="green")
b_newBet.grid(column=2, row=0, padx=5, pady=5)

#icon = tkinter.PhotoImage(file="image_files/RK.png")
#main_window.wm_iconphoto(False, icon)

#shortcut definitions for the main Window
main_window.bind(shortcuts.DataSave, lambda event: [Button_saveDat()])
main_window.bind(shortcuts.DataSaveAs, lambda event: [Button_saveasDat()])
main_window.bind(shortcuts.DataLoad, lambda event: [Button_setDat()])

main_window.bind(shortcuts.PatientNew, lambda event: [Button_read_list(), NewPat_Button()])
main_window.bind(shortcuts.NextPatient, lambda event: [NextPat_Button()])
main_window.bind(shortcuts.PreviousPatient, lambda event: [PrevPat_Button()])
main_window.bind(shortcuts.PatientEdit, lambda event: [Edit_pat(CurrentPatindex)])
main_window.bind(shortcuts.SpecificPatient, prompt_edit_patient)

main_window.bind(shortcuts.BetreuungNew, lambda event: [NewBetreuung_Button()])
#main_window.bind(shortcuts.BetreuungDel, lambda event: [DelBetreuung_Button()])

main_window.bind(shortcuts.Fullscreen, toggle_fullscreen)

main_window.bind(shortcuts.FilterMenu, lambda event: [open_filter_menu()])
main_window.bind(shortcuts.AuslastungMenu, lambda event: [DisplayPatientsInPlace()])
main_window.bind(shortcuts.Statistik, lambda event: [DetailedStats()])
main_window.bind(shortcuts.EditConfig, lambda event: [Init_Stats()])

Update_lables()

def on_closing():
    main_window.destroy()
    print("Fenster geschlossen")
    print("Ambulanznummer:", AmbNum)
    print("Ambulanzname:", AmbName)
    print("Datum:", AmbDate)
    print("Anzahl der Patienten:", len(Patlist))
    print("Anzahl der Betreuungen:", Betreuungen)
    print("\n")
    print("Vielen Dank für die Nutzung von Ambulanz-Dashboard")
    print("Version: " + Version)
    print("Entwickler: Simon")
    print("Besuchen Sie meine Website für mehr Informationen.")
    print("Programm beendet")
    auth.log("Programm beendet", AmbNum)
    sys.exit()

main_window.protocol("WM_DELETE_WINDOW", on_closing)

# Function to check the file modification time
def check_file_modification():
    global Patlist
    global last_modification_time
    global CurrentPatindex
    ambdat_filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"
    try:
        current_modification_time = os.path.getmtime(ambdat_filepath)
        if current_modification_time != last_modification_time:
            last_modification_time = current_modification_time
            Patlist = read_list()
            if CurrentPatindex > latestpatindex():
                CurrentPatindex = latestpatindex()
            Update_lables()
            Update_patient_list()
    except FileNotFoundError:
        # Datei existiert (noch) nicht, einfach ignorieren oder initialisieren
        pass
    main_window.after(1000, check_file_modification)  # Check every 1 second

# Initialisierung:
ambdat_filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"
try:
    last_modification_time = os.path.getmtime(ambdat_filepath)
except FileNotFoundError:
    last_modification_time = 0

# Start checking the file modification time
check_file_modification()

main_window.mainloop()