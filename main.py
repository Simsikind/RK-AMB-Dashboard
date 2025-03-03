import tkinter.filedialog
import functions
from datetime import datetime
import time
import tkinter
from tkinter import ttk
import pickle
import csv
import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import sys

print("Starte Ambulanz-Dashboard")

# Function to get the current time
def now():
    currentTime = datetime.now()
    return str(currentTime.strftime("%H:%M"))

# Global variables
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

Pat0()

main_window = tkinter.Tk(className='~Amulanz-Dashboard~')


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
            continue  # Skip patient 0

        if filter_active and patient.Endt != "-":
            continue  # Skip inactive patients if filter is active

        if filter_place and patient.HSTPlace != filter_place:
            continue  # Skip patients not in the selected place

        if filter_transport and patient.TransportAgency != filter_transport:
            continue  # Skip patients not in the selected transport agency

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
        patient_info = f"{patient_num_formatted} | {patient.HSTt} | {patient.HSTPlace} | {patient.Triage} | {patient.Alarmstr}: {patient.Comment}"
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
    filter_window = tkinter.Toplevel(main_window)
    filter_window.title("Filter Menü")
    filter_window.focus_force()

    global filter_active, filter_place, filter_transport

    filter_active_var = tkinter.BooleanVar(value=filter_active)
    filter_place_var = tkinter.StringVar(value=filter_place)
    filter_transport_var = tkinter.StringVar(value=filter_transport)

    tkinter.Checkbutton(filter_window, text="Nur aktive Patienten anzeigen", variable=filter_active_var).grid(row=0, column=0, sticky="w")

    tkinter.Label(filter_window, text="Behandlungsplatz:").grid(row=1, column=0, sticky="w")
    place_options = [""] + list(max_counts.keys())
    tkinter.OptionMenu(filter_window, filter_place_var, *place_options).grid(row=1, column=1, sticky="w")

    tkinter.Label(filter_window, text="Abtransport:").grid(row=2, column=0, sticky="w")
    transport_options = [""] + list(set(patient.TransportAgency for patient in Patlist if patient.TransportAgency))
    tkinter.OptionMenu(filter_window, filter_transport_var, *transport_options).grid(row=2, column=1, sticky="w")

    def apply_filters():
        global filter_active, filter_place, filter_transport
        filter_active = filter_active_var.get()
        filter_place = filter_place_var.get()
        filter_transport = filter_transport_var.get()
        Update_patient_list()
        filter_window.destroy()

    def reset_filters():
        global filter_active, filter_place, filter_transport
        filter_active = False
        filter_place = ""
        filter_transport = ""
        Update_patient_list()
        filter_window.destroy()

    tkinter.Button(filter_window, text="Anwenden", command=apply_filters).grid(row=3, column=0, sticky="w")
    tkinter.Button(filter_window, text="Zurücksetzen", command=reset_filters).grid(row=3, column=1, sticky="w")

# Initialize filter variables
filter_active = False
filter_place = ""
filter_transport = ""

# Add a button to open the filter menu
b_open_filter_menu = tkinter.Button(main_window, text="Filter Menü öffnen", command=open_filter_menu)
b_open_filter_menu.grid(row=0, column=50)

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
    
    l_Pat.config(text=str(latestpatindex()) + " Patienten")
    l_Betreuungen.config(text=str(Betreuungen) + " Betreuungen")

    l_CurrentPatNum.config(text=str(Patlist[CurrentPatindex].Num))
    l_CurrentPatAlarmt.config(text=str(Patlist[CurrentPatindex].Alarmt))
    l_CurrentPatAlarmstr.config(text=str(Patlist[CurrentPatindex].Alarmstr))
    l_CurrentPatBO.config(text=str(Patlist[CurrentPatindex].BOplace))
    l_CurrentPatBot.config(text=str(Patlist[CurrentPatindex].BOt))
    l_CurrentPatHSTt.config(text=str(Patlist[CurrentPatindex].HSTt))
    l_CurrentPatHSTplace.config(text=str(Patlist[CurrentPatindex].HSTPlace))
    l_CurrentPatTransA.config(text=str(Patlist[CurrentPatindex].TransportAgency))
    l_CurrentPatEndt.config(text=str(Patlist[CurrentPatindex].Endt))
    l_CurrentPatfin.config(text=str(Patlist[CurrentPatindex].finished))
    l_CurrentPatNACA.config(text=str(Patlist[CurrentPatindex].Naca))
    l_CurrentPatTriage.config(text=str(Patlist[CurrentPatindex].Triage))
    l_CurrentPatComment.config(text=str(Patlist[CurrentPatindex].Comment))

    l_AmbNum.config(text=AmbNum)
    l_AmbName.config(text=AmbName)
    l_AmbDate.config(text=AmbDate)

    # Update Behandlungsplätze usage
    usage_frame = tkinter.Frame(main_window)
    usage_frame.grid(column=1, row=6, columnspan=1, sticky="ew")

    b_Usage = tkinter.Button(usage_frame, text="Auslastung-Details", command=lambda:[DisplayPatientsInPlace()])
    b_Usage.grid(row=0, column=0)

    l_Ausl = tkinter.Label(usage_frame, text="Auslastung:")
    l_Ausl.grid(column=0, row=1)
    row = 2
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

# Function to edit patient details
def Edit_pat(index):
    if index == 0:
        return  # Skip patient 0
    
    Done = tkinter.BooleanVar()
    Edit = tkinter.Toplevel(main_window)
    Edit.title("Patient " + str(index) + " bearbeiten")
    Edit.focus_force()

    l_textr3 = tkinter.Label(Edit, text="Akuell Angezeigter Pat Nr: ")
    l_textr3.grid(column=0, row=3)
    l_CurrentPatNum = tkinter.Label(Edit, text=str(Patlist[index].Num))
    l_CurrentPatNum.grid(column=1, row=3)
    
    l_textr4 = tkinter.Label(Edit, text="Einsatzbeginn:")
    l_textr4.grid(column=0, row=4)
    e_CurrentPatAlarmt = tkinter.Entry(Edit)
    e_CurrentPatAlarmt.insert(0, str(Patlist[index].Alarmt))
    e_CurrentPatAlarmt.grid(column=1, row=4)
    Patlist[index].setAlarmt(e_CurrentPatAlarmt.get())

    l_textr5 = tkinter.Label(Edit, text="Berufungsgrund:")
    l_textr5.grid(column=0, row=5)
    e_CurrentPatAlarmstr = tkinter.Entry(Edit)
    e_CurrentPatAlarmstr.insert(0, str(Patlist[index].Alarmstr))
    e_CurrentPatAlarmstr.grid(column=1, row=5)

    l_textr6 = tkinter.Label(Edit, text="Berufungsort:")
    l_textr6.grid(column=0, row=6)
    e_CurrentPatBO = tkinter.Entry(Edit)
    e_CurrentPatBO.insert(0, str(Patlist[index].BOplace))
    e_CurrentPatBO.grid(column=1, row=6)

    l_textr7 = tkinter.Label(Edit, text="Zeit am BO: ")
    l_textr7.grid(column=0, row=7)
    e_CurrentPatBot = tkinter.Entry(Edit)
    e_CurrentPatBot.insert(0, str(Patlist[index].BOt))
    e_CurrentPatBot.grid(column=1, row=7)

    l_textr9 = tkinter.Label(Edit, text="Zeit auf der Behandlung:")
    l_textr9.grid(column=0, row=9)
    e_CurrentPatHSTt = tkinter.Entry(Edit)
    e_CurrentPatHSTt.insert(0, str(Patlist[index].HSTt))
    e_CurrentPatHSTt.grid(column=1, row=9)

    l_textr10 = tkinter.Label(Edit, text="Behandlungsplatz:")
    l_textr10.grid(column=0, row=10)
    l_SelectedPlace = tkinter.Label(Edit, text=str(Patlist[index].HSTPlace))
    l_SelectedPlace.grid(column=1, row=10)
    b_SelectPlace = tkinter.Button(Edit, text="Platz auswählen", command=lambda: SelectPlace_Window(index, l_SelectedPlace))
    b_SelectPlace.grid(column=2, row=10)

    # Disable the button if only one Behandlungsplatz is configured
    if len(max_counts) <= 1:
        b_SelectPlace.config(state=tkinter.DISABLED)

    l_textr11 = tkinter.Label(Edit, text="Abtransport-Organisation:")
    l_textr11.grid(column=0, row=11)
    e_CurrentPatTransportAgency = ttk.Combobox(Edit, values=["-", "KTW", "NKTW", "RTW", "RTW+NEF/NAW", "Anderes"], state="readonly")
    e_CurrentPatTransportAgency.set(Patlist[index].TransportAgency)
    e_CurrentPatTransportAgency.grid(column=1, row=11)

    l_textr12 = tkinter.Label(Edit, text="Einsatzende:")
    l_textr12.grid(column=0, row=12)
    e_CurrentPatEndt = tkinter.Entry(Edit)
    e_CurrentPatEndt.insert(0, str(Patlist[index].Endt))
    e_CurrentPatEndt.grid(column=1, row=12)

    l_textr13 = tkinter.Label(Edit, text="Protokoll fertig:")
    l_textr13.grid(column=0, row=13)
    c_CurrentPatfin = tkinter.Checkbutton(Edit, variable=Done)
    c_CurrentPatfin.grid(column=1, row=13)
    if Patlist[index].finished == 1:
        c_CurrentPatfin.select()

    l_textr14 = tkinter.Label(Edit, text="NACA:")
    l_textr14.grid(column=0, row=14)
    e_CurrentPatNACA = tkinter.Entry(Edit)
    e_CurrentPatNACA.insert(0, str(Patlist[index].Naca))
    e_CurrentPatNACA.grid(column=1, row=14)

    l_textr8= tkinter.Label(Edit, text="Triage-Kategorie:")
    l_textr8.grid(column=0, row=8)
    e_CurrentPatTriage = ttk.Combobox(Edit, values=TriageCategories, state="readonly")
    e_CurrentPatTriage.set(Patlist[index].Triage)
    e_CurrentPatTriage.grid(column=1, row=8)

    l_textr15 = tkinter.Label(Edit, text="Kommentar:")
    l_textr15.grid(column=0, row=15)
    e_CurrentPatComment = tkinter.Entry(Edit)
    e_CurrentPatComment.insert(0, str(Patlist[index].Comment))
    e_CurrentPatComment.grid(column=1, row=15)

    b_now_alarmt = tkinter.Button(Edit, text="Jetzt", command=lambda: [e_CurrentPatAlarmt.delete(0, tkinter.END), e_CurrentPatAlarmt.insert(0, now())])
    b_now_alarmt.grid(column=2, row=4)

    b_now_bot = tkinter.Button(Edit, text="Jetzt", command=lambda: [e_CurrentPatBot.delete(0, tkinter.END), e_CurrentPatBot.insert(0, now())])
    b_now_bot.grid(column=2, row=7)

    b_now_hstt = tkinter.Button(Edit, text="Jetzt", command=lambda: [e_CurrentPatHSTt.delete(0, tkinter.END), e_CurrentPatHSTt.insert(0, now())])
    b_now_hstt.grid(column=2, row=9)

    b_now_endt = tkinter.Button(Edit, text="Jetzt", command=lambda: [e_CurrentPatEndt.delete(0, tkinter.END), e_CurrentPatEndt.insert(0, now())])
    b_now_endt.grid(column=2, row=12)

    def update_finished_state(*args):
        if e_CurrentPatHSTt.get() != "-" and l_SelectedPlace.cget("text") != "-" and e_CurrentPatEndt.get() != "-":
            c_CurrentPatfin.config(state=tkinter.NORMAL)
        else:
            c_CurrentPatfin.config(state=tkinter.DISABLED)

    e_CurrentPatHSTt.bind("<KeyRelease>", update_finished_state)
    e_CurrentPatEndt.bind("<KeyRelease>", update_finished_state)
    l_SelectedPlace.bind("<Configure>", update_finished_state)

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
        Patlist[index].setfinished(Done.get()),
        Patlist[index].setComment(e_CurrentPatComment.get()),
        write_list(Patlist),
        Update_lables(), 
        Edit.destroy()
    ])

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
        Update_lables()

    b_Cancel = tkinter.Button(Edit, text="Abbruch", command=Edit.destroy)
    b_Delete = tkinter.Button(Edit, text="Patient löschen", command=lambda: [delete_patient_ask(), Edit.destroy()], bg="red")

    b_OK.grid(row=16, column=2)
    b_Cancel.grid(row=16, column=1)
    b_Delete.grid(row=16, column=0)

    update_finished_state()

# Function to select a place for the patient
def SelectPlace_Window(index, l_SelectedPlace):
    SelectPlace = tkinter.Toplevel(main_window)
    SelectPlace.title("Behandlungsplatz auswählen")
    SelectPlace.focus_force()

    l_Ausl = tkinter.Label(SelectPlace, text="Auslastung:")
    l_Ausl.grid(column=0, row=0)
    row = 1
    for place, max_count in max_counts.items():
        current_count = sum(1 for patient in Patlist if patient.HSTPlace == place and patient.Endt == "-")
        percentage = (current_count / max_count) * 100
        usage_label = tkinter.Label(SelectPlace, text=f"{place}: {current_count}/{max_count} ({percentage:.2f}%)")
        usage_label.grid(column=0, row=row)
        
        # Determine button color based on usage percentage
        if percentage >= 80:
            color = "red"
        elif percentage >= 50:
            color = "yellow"
        else:
            color = "green"
        
        b_Select = tkinter.Button(SelectPlace, text="Auswählen", bg=color, command=lambda p=place: [
            Patlist[index].setHSTPlace(p),
            l_SelectedPlace.config(text=p),
            SelectPlace.destroy()
        ])
        b_Select.grid(column=1, row=row)
        row += 1

# Function to create a new patient
def NewPat():
    read_list()
    global CurrentPatindex
    global Patlist
    print("Neuer Patient mit Ablagenummer ", latestpatindex() + 1)
    Patlist.append(functions.Patient(latestpatindex() + 1))
    write_list(Patlist)
    CurrentPatindex = latestpatindex()
    Edit_pat(CurrentPatindex)

# Function to create a new patient and add them to the end of the list
def NewPat_Button():
    top = tkinter.Toplevel(main_window)
    top.title("Neuer Patient")
    top.focus_force()
    l_newPatinfo = tkinter.Label(top, text="Neuer Patient mit der Ablagenummer " + str(latestpatindex() + 1))
    l_newPatinfo.pack()

    b_OK = tkinter.Button(top, text="OK", command=lambda: [NewPat(), Update_lables(), top.destroy()])
    b_Cancel = tkinter.Button(top, text="Abbruch", command=lambda: [top.destroy()])

    b_OK.pack()
    b_Cancel.pack()

# Function to delete the current patient
def DelPat():
    pass
    #global CurrentPatindex
    #if latestpatindex() > 0:
        #Patlist.pop()
        #print("Patient mit Nummer ", CurrentPatindex, " gelöscht")
        #write_list(Patlist)

def DelPat_Button():
    DelPat()
    Update_lables()

# Function to create a new Betreuung
def NewBetreuung():
    global Betreuungen
    Betreuungen = Betreuungen + 1
    print("Neue Betreuung mit der Nummer", Betreuungen)
    saveDatinFile(filepath)

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

    b_OK = tkinter.Button(Init, text="OK", command=save_stats)
    b_Cancel = tkinter.Button(Init, text="Abbruch", command=Init.destroy)

    b_OK.grid(row=len(place_entries) + 11, column=1)
    b_Cancel.grid(row=len(place_entries) + 11, column=0)

# Function to write the patient list to a file
def write_list(list):
    global AmbName
    global AmbDate
    global AmbNum

    filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"

    if not os.path.exists(filepath):
        with open(filepath, 'w+') as file:
            pickle.dump(Patlist, file)
    else:
        print("Die Datei {file_path} existiert schon.")
        

    with open(filepath, "wb") as fp:
        pickle.dump(list, fp)
        print(f"Daten in Datei geschrieben: {filepath}")
        fp.close()

def read_list():
    global AmbName
    global AmbDate
    filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"

    if not os.path.exists(filepath):
        with open(filepath, 'w+') as file:
            pickle.dump("", file)
            file.close()
    else:
        print("Die Datei existiert schon.")

    if os.path.getsize(filepath) <= 0:
        Pat0()
        fil = open(filepath, 'wb+')
        pickle.dump(Patlist, fil)
        fil.close()

    with open(filepath, "rb") as fp:
        mydata = pickle.load(fp)
        print(f"Daten aus Datei gelesen: {filepath}")
        fp.close
        return mydata

def Button_read_list():
    global Patlist
    global CurrentPatindex
    Patlist = read_list()
    #CurrentPatindex = 0
    Update_lables()

def ExportPatlist():
    path = 'Userdata/Export/' + re.sub(r'\W+', '_', AmbNum) + "_" + AmbName + '.csv'
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["Pat-Nr", "Alarmzeit", "B.Grund", "BO", "BO-Zeit", "HST-Zeit", "Triage-Kat", "Behandlungsstelle", "Abtransport", "NACA", "Fertig", "Kommentar", str(Betreuungen) + " Betreuungen"])
        for x in range(len(Patlist)):
            if x > 0:
                is_finished = "Nein"
                if Patlist[x].finished == True:
                    is_finished = "Ja"

                spamwriter.writerow([
                    Patlist[x].Num,
                    Patlist[x].Alarmt, 
                    Patlist[x].Alarmstr, 
                    Patlist[x].BOplace, 
                    Patlist[x].BOt, 
                    Patlist[x].HSTt,
                    Patlist[x].Triage, 
                    Patlist[x].HSTPlace,
                    Patlist[x].TransportAgency, 
                    Patlist[x].Naca, 
                    is_finished,
                    Patlist[x].Comment
                    
                ])
    print(f"Daten in Datei geschrieben: {path}")

def setDatfromFile(path):
    global AmbNum
    global AmbName
    global AmbDate
    global Betreuungen
    global max_counts
    global filepath
    filepath = path
    with open(path, "r") as File:
        AmbNum = re.sub('\n', '', File.readline())
        AmbName = re.sub('\n', '', File.readline())
        AmbDate = re.sub('\n', '', File.readline())
        Betreuungen = int(re.sub('\n', '', File.readline()))
        max_counts = {}
        for line in File:
            place, max_count = line.strip().split(":")
            max_counts[place] = int(max_count)
    print(f"Daten aus Datei gelesen: {path}")

def Button_setDat():
    filepath = tkinter.filedialog.askopenfile(filetypes=[("Data-Datei",".dat")]).name
    setDatfromFile(filepath)
    Button_read_list()
    Update_lables()

def saveDatinFile(path):
    global AmbNum
    global AmbName
    global AmbDate
    global Betreuungen
    global max_counts
    with open(path, "w") as File:
        File.writelines(AmbNum + "\n")
        File.writelines(AmbName + "\n")
        File.writelines(AmbDate + "\n")
        File.writelines(str(Betreuungen) + "\n")
        for place in max_counts:
            File.writelines(f"{place}:{max_counts[place]}\n")
    print(f"Daten in Datei geschrieben: {path}")

def Button_saveasDat():
    global filepath
    filepath = tkinter.filedialog.asksaveasfile(filetypes=[("Data-Datei",".dat")]).name
    saveDatinFile(filepath)
    Button_read_list()
    Update_lables()
    print(filepath)

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
        

def DetailedStats():
    global Betreuungen

    stats = tkinter.Toplevel(main_window)
    stats.title("Detaillierte Statistik")
    stats.focus_force()

    naca_counts = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}}
    all_places = set()

    for patient in Patlist:
        if patient.Num != 0:
            place = patient.HSTPlace
            all_places.add(place)
            if patient.Endt != "-":
                naca = int(patient.Naca)
                if place in naca_counts[naca]:
                    naca_counts[naca][place] += 1
                else:
                    naca_counts[naca][place] = 1

    # Sort places in the same order as in the .dat file
    sorted_places = sorted(all_places, key=lambda place: list(max_counts.keys()).index(place) if place in max_counts else len(max_counts))

    # Create header row with NACA scores
    col = 1
    for naca in range(1, 8):
        naca_label = tkinter.Label(stats, text=f"NACA {naca}  |", anchor="w")
        naca_label.grid(column=col, row=0, sticky="w")
        col += 1

    # Add a header for the sum column
    sum_header_label = tkinter.Label(stats, text="Summe", anchor="w")
    sum_header_label.grid(column=col, row=0, sticky="w")

    # Create rows for each place
    row = 1
    for place in sorted_places:
        place_label = tkinter.Label(stats, text=str(place + ":"), anchor="w")
        place_label.grid(column=0, row=row, sticky="w")
        col = 1
        place_sum = 0
        for naca in range(1, 8):
            count = naca_counts[naca].get(place, 0)
            place_sum += count
            count_label = tkinter.Label(stats, text=str(count), anchor="w")
            count_label.grid(column=col, row=row, sticky="w")
            col += 1
        # Add the sum for the place
        place_sum_label = tkinter.Label(stats, text=str(place_sum), anchor="w")
        place_sum_label.grid(column=col, row=row, sticky="w")
        row += 1

        # Add a thin line separator between places
        separator = tkinter.Frame(stats, height=1, bd=1, relief="sunken", background="black")
        separator.grid(column=0, row=row, columnspan=col+1, sticky="ew", pady=2)
        row += 1

    # Add a thick line separator above the sum row
    thick_separator = tkinter.Frame(stats, height=2, bd=1, relief="sunken", background="black")
    thick_separator.grid(column=0, row=row, columnspan=col+1, sticky="ew", pady=5)
    row += 1

    # Add a last row for the sum
    sum_label = tkinter.Label(stats, text="Summe:", anchor="w")
    sum_label.grid(column=0, row=row, sticky="w")
    col = 1
    total_counts = {naca: sum(naca_counts[naca].values()) for naca in range(1, 8)}
    total_sum = sum(total_counts.values())
    for naca in range(1, 8):
        total_count = total_counts[naca]
        total_label = tkinter.Label(stats, text=str(total_count), anchor="w")
        total_label.grid(column=col, row=row, sticky="w")
        col += 1
    # Add the total sum
    total_sum_label = tkinter.Label(stats, text=str(total_sum), anchor="w")
    total_sum_label.grid(column=col, row=row, sticky="w")

    # Add a label for Betreuungen
    betreuungen_label = tkinter.Label(stats, text=f"Betreuungen: {Betreuungen}", anchor="w")
    betreuungen_label.grid(column=0, row=row+1, sticky="w")

    # Create pie charts
    def create_pie_chart(data, title, row, col):
        fig, ax = plt.subplots(figsize=(4, 4))  # Smaller figure size
        filtered_data = {k: v for k, v in data.items() if v > 0}
        labels = [f"NACA {naca}" for naca in filtered_data.keys()]
        sizes = filtered_data.values()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(title)
        canvas = FigureCanvasTkAgg(fig, master=stats)
        canvas.draw()
        canvas.get_tk_widget().grid(column=col, row=row, padx=10, pady=10)
        
    create_pie_chart(total_counts, "Summe", row+2, 10)

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


# Create a scrollable frame for the patient list
patient_list_canvas = tkinter.Canvas(main_window)
patient_list_frame = tkinter.Frame(patient_list_canvas)
scrollbar = tkinter.Scrollbar(main_window, orient="vertical", command=patient_list_canvas.yview)
patient_list_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.grid(row=0, column=3, rowspan=21, sticky="ns")
patient_list_canvas.grid(row=0, column=4, rowspan=21, columnspan=20, sticky="nsew")
patient_list_canvas.create_window((0, 0), window=patient_list_frame, anchor="nw")

def on_frame_configure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

patient_list_frame.bind("<Configure>", lambda event, canvas=patient_list_canvas: on_frame_configure(canvas))

# Create frames for the buttons and labels
ambulance_info_frame = tkinter.Frame(main_window)
ambulance_info_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

separator1 = tkinter.Label(main_window, text="----------------------------------------------------------------------------------------")
separator1.grid(row=1, column=0, columnspan=3, sticky="ew")

patient_info_frame = tkinter.Frame(main_window)
patient_info_frame.grid(row=2, column=0, columnspan=3, sticky="ew")

separator2 = tkinter.Label(main_window, text="----------------------------------------------------------------------------------------")
separator2.grid(row=3, column=0, columnspan=3, sticky="ew")

button_frame = tkinter.Frame(main_window)
button_frame.grid(row=4, column=0, columnspan=3, sticky="ew")

separator3 = tkinter.Label(main_window, text="----------------------------------------------------------------------------------------")
separator3.grid(row=5, column=0, columnspan=3, sticky="ew")

config_frame = tkinter.Frame(main_window)
config_frame.grid(row=0, column=2, columnspan=1, sticky="ew")

b_newBet = tkinter.Button(button_frame, text='Neue Betreuung', command=lambda: (NewBetreuung_Button()), bg="green")
b_newBet.grid(column=2, row=0)
l_Betreuungen = tkinter.Label(button_frame, text=str(Betreuungen) + " Betreuungen")
l_Betreuungen.grid(column=1, row=0)
b_DelBet = tkinter.Button(button_frame, text='Betreuung Löschen', command=lambda: (DelBetreuung_Button()), bg="green")
b_DelBet.grid(column=0, row=0)

#b_newPat = tkinter.Button(patient_info_frame, text='Neuesten Pat. löschen', command=lambda: (DelPat_Button()), bg="red")
#b_newPat.grid(column=0, row=0)
l_Pat = tkinter.Label(patient_info_frame, text=str(latestpatindex()) + " Patienten")
l_Pat.grid(column=1, row=0)
b_newPat = tkinter.Button(patient_info_frame, text='Neuer Patient', command=lambda: (Button_read_list(), NewPat_Button()), bg="red")
b_newPat.grid(column=2, row=0)

l_textr3 = tkinter.Label(patient_info_frame, text="Akuell Angezeigter Pat Nr:")
l_textr3.grid(column=0, row=1)
l_CurrentPatNum = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].Num))
l_CurrentPatNum.grid(column=1, row=1)

l_textr4 = tkinter.Label(patient_info_frame, text="Einsatzbeginn:")
l_textr4.grid(column=0, row=2)
l_CurrentPatAlarmt = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].Alarmt))
l_CurrentPatAlarmt.grid(column=1, row=2)

l_textr5 = tkinter.Label(patient_info_frame, text="Berufungsgrund:")
l_textr5.grid(column=0, row=3)
l_CurrentPatAlarmstr = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].Alarmstr))
l_CurrentPatAlarmstr.grid(column=1, row=3)

l_textr6 = tkinter.Label(patient_info_frame, text="Berufungsort:")
l_textr6.grid(column=0, row=4)
l_CurrentPatBO = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].BOplace))
l_CurrentPatBO.grid(column=1, row=4)

l_textr7 = tkinter.Label(patient_info_frame, text="Zeit am BO:")
l_textr7.grid(column=0, row=5)
l_CurrentPatBot = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].BOt))
l_CurrentPatBot.grid(column=1, row=5)

l_textr14 = tkinter.Label(patient_info_frame, text="Triage-Kategorie:")
l_textr14.grid(column=0, row=6)
l_CurrentPatTriage = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].Triage))
l_CurrentPatTriage.grid(column=1, row=6)

l_textr8 = tkinter.Label(patient_info_frame, text="Zeit auf der Behandlung:")
l_textr8.grid(column=0, row=7)
l_CurrentPatHSTt = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].HSTt))
l_CurrentPatHSTt.grid(column=1, row=7)

l_textr9 = tkinter.Label(patient_info_frame, text="Behandlungsplatz:")
l_textr9.grid(column=0, row=8)
l_CurrentPatHSTplace = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].HSTPlace))
l_CurrentPatHSTplace.grid(column=1, row=8)

l_textr10 = tkinter.Label(patient_info_frame, text="Abtransport")
l_textr10.grid(column=0, row=9)
l_CurrentPatTransA = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].TransportAgency))
l_CurrentPatTransA.grid(column=1, row=9)

l_textr11 = tkinter.Label(patient_info_frame, text="Einsatzende:")
l_textr11.grid(column=0, row=10)
l_CurrentPatEndt = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].Endt))
l_CurrentPatEndt.grid(column=1, row=10)

l_textr12 = tkinter.Label(patient_info_frame, text="Protokoll fertig:")
l_textr12.grid(column=0, row=11)
l_CurrentPatfin = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].finished))
l_CurrentPatfin.grid(column=1, row=11)

l_textr13 = tkinter.Label(patient_info_frame, text="NACA:")
l_textr13.grid(column=0, row=12)
l_CurrentPatNACA = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].Naca))
l_CurrentPatNACA.grid(column=1, row=12)

l_textr15 = tkinter.Label(patient_info_frame, text="Kommentar:")
l_textr15.grid(column=0, row=13)
l_CurrentPatComment = tkinter.Label(patient_info_frame, text=str(Patlist[CurrentPatindex].Comment))
l_CurrentPatComment.grid(column=1, row=13)

b_prevPat = tkinter.Button(patient_info_frame, text="<", width=20, command=lambda: (PrevPat_Button()))
b_prevPat.grid(row=14, column=0)

b_nextPat = tkinter.Button(patient_info_frame, text=">", width=20, command=lambda: (NextPat_Button()))
b_nextPat.grid(row=14, column=2)

b_EditPat = tkinter.Button(patient_info_frame, width=20, text="Pat Bearbeiten", command=lambda: (Edit_pat(CurrentPatindex)))
b_EditPat.grid(row=14, column=1)

l_AmbNum = tkinter.Label(ambulance_info_frame, text=AmbNum, font=("Helvetica", 12, "bold"))
l_AmbNum.grid(row=0, column=0)

l_AmbName = tkinter.Label(ambulance_info_frame, text=AmbName, font=("Helvetica", 12, "bold"))
l_AmbName.grid(row=1, column=0)

l_AmbDate = tkinter.Label(ambulance_info_frame, text=AmbDate, font=("Helvetica", 12, "bold"))
l_AmbDate.grid(row=2, column=0)

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

    b_stats = tkinter.Button(menu_window, text="Statistik anzeigen", command=lambda:[DetailedStats(), menu_window.destroy()])
    b_stats.grid(row=0, column=1)

    l_Update = tkinter.Label(menu_window, text="Letztes Update: " + lastUpdate)
    l_Update.grid(column=0, row=5)

    #b_create_random_patients = tkinter.Button(menu_window, text="Erstelle zufällige Patienten", command=lambda: [CreateRandomPatients(10), menu_window.destroy()])
    #b_create_random_patients.grid(row=4, column=0)

b_open_menu = tkinter.Button(config_frame, text="Menü öffnen", command=open_menu_window)
b_open_menu.grid(row=0, column=0)

icon = tkinter.PhotoImage(file="image_files/RK.png")
main_window.wm_iconphoto(False, icon)

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
    print("Version: 1.1.2")
    print("Entwickler: Simon")
    print("Besuchen Sie meine Website für mehr Informationen.")
    print("Programm beendet")
    sys.exit()

main_window.protocol("WM_DELETE_WINDOW", on_closing)

# Function to check the file modification time
def check_file_modification():
    global Patlist
    global last_modification_time
    global CurrentPatindex
    ambdat_filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"
    current_modification_time = os.path.getmtime(ambdat_filepath)
    if current_modification_time != last_modification_time:
        last_modification_time = current_modification_time

        time.sleep(0.1)  # Wait for the file to be written
        Patlist = read_list()
        #CurrentPatindex = 0
        Update_lables()
        Update_patient_list()
        
    main_window.after(10, check_file_modification)  # Check every 10 milliseconds (1 second)

# Initialize the last modification time
ambdat_filepath = "PatDat/" + re.sub('[^0-9]', '', AmbNum) + ".ambdat"
last_modification_time = os.path.getmtime(ambdat_filepath)

# Start checking the file modification time
check_file_modification()

main_window.mainloop()