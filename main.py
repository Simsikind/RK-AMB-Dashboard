import tkinter.filedialog
import functions
#from datetime import datetime
import tkinter
import pickle
import csv
import os
import re

AmbNum = ""
AmbName = ""
AmbDate = ""
Betreuungen = 0
CurrentPatindex = 0
Patlist = []
Patlist.append(functions.Patient(0))                        #Add Patient zero, so thet the Index ist the same as the "Ablagenummer"
Patlist[0].setfinished(True)
Patlist[0].setAlarmt("-")

while os.path.exists("Export")==False:
    os.mkdir("Export")
    print("Ordner 'Export' estellt")

while os.path.exists("PatDat")==False:
    os.mkdir("PatDat")
    print("Ordner 'PatDat' estellt")

def setNum(str):
    global AmbNum
    AmbNum = str

def setName(str):
    global AmbName
    AmbName = str

def setDate(str):
    global AmbDate
    AmbDate = str

def PrevPat_Button():
    global CurrentPatindex
    if CurrentPatindex > 0:
        CurrentPatindex = CurrentPatindex -1
    print("Current Patient Index: ", CurrentPatindex)
    Update_lables()

def NextPat_Button():
    global CurrentPatindex
    if CurrentPatindex < len(Patlist) -1:
        CurrentPatindex = CurrentPatindex +1
    else:
        NewPat_Button()
    print("Current Patient Index: ", CurrentPatindex)
    Update_lables()

def latestpatindex():                                       #gets the index of the latest Patient
    z = 0
    for x in Patlist:
        z = z+1
    return z-1

def Update_lables():
    #main_window.title=AmbName +'Amulanz-Dashboard'
    
    l_Pat.config(text=str(latestpatindex()) + " Patienten")
    l_Betreuungen.config(text=str(Betreuungen) + " Betreuungen")

    l_CurrentPatNum.config(text= str(Patlist[CurrentPatindex].Num))
    l_CurrentPatNum.config(text=str(Patlist[CurrentPatindex].Num))
    l_CurrentPatAlarmt.config(text=str(Patlist[CurrentPatindex].Alarmt))
    l_CurrentPatAlarmstr.config(text=str(Patlist[CurrentPatindex].Alarmstr))
    l_CurrentPatBO.config(text=str(Patlist[CurrentPatindex].BOplace))
    l_CurrentPatBot.config(text=str(Patlist[CurrentPatindex].BOt))
    l_CurrentPatHSTt.config(text=str(Patlist[CurrentPatindex].HSTt))
    l_CurrentPatTransA.config(text=str(Patlist[CurrentPatindex].TransportAgency))
    l_CurrentPatEndt.config(text=str(Patlist[CurrentPatindex].Endt))
    l_CurrentPatfin.config(text=str(Patlist[CurrentPatindex].finished))
    l_CurrentPatNACA.config(text=str(Patlist[CurrentPatindex].Naca))

    l_AmbNum.config(text=AmbNum)
    l_AmbName.config(text=AmbName)
    l_AmbDate.config(text=AmbDate)

def Edit_pat(index):
    Done = tkinter.BooleanVar()
    Edit = tkinter.Toplevel(main_window)
    Edit.title("Patient " + str(index) + " bearbeiten")

    l_textr3 = tkinter.Label(Edit, text="Akuell Angezeigter Pat Nr: ")
    l_textr3.grid(column=0, row=3)
    l_CurrentPatNum = tkinter.Label(Edit, text= str(Patlist[index].Num))
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

    l_textr8 = tkinter.Label(Edit, text="Zeit auf der Behandlung:")
    l_textr8.grid(column=0, row=8)
    e_CurrentPatHSTt = tkinter.Entry(Edit)
    e_CurrentPatHSTt.insert(0, str(Patlist[index].HSTt))
    e_CurrentPatHSTt.grid(column=1, row=8)

    l_textr9 = tkinter.Label(Edit, text="Abtransport-Organisation:")
    l_textr9.grid(column=0, row=9)
    e_CurrentPatTransportAgency = tkinter.Entry(Edit)
    e_CurrentPatTransportAgency.insert(0, str(Patlist[index].TransportAgency))
    e_CurrentPatTransportAgency.grid(column=1, row=9)

    l_textr10 = tkinter.Label(Edit, text="Einsatzende:")
    l_textr10.grid(column=0, row=10)
    e_CurrentPatEndt = tkinter.Entry(Edit)
    e_CurrentPatEndt.insert(0, str(Patlist[index].Endt))
    e_CurrentPatEndt.grid(column=1, row=10)

    l_textr11 = tkinter.Label(Edit, text="Protokoll fertig:")
    l_textr11.grid(column=0, row=11)
    c_CurrentPatfin = tkinter.Checkbutton(Edit,variable=Done)
    c_CurrentPatfin.grid(column=1, row=11)
    if Patlist[index].finished == 1:
        c_CurrentPatfin.select()

    l_textr12 = tkinter.Label(Edit, text="NACA:")
    l_textr12.grid(column=0, row=12)
    e_CurrentPatNACA = tkinter.Entry(Edit)
    e_CurrentPatNACA.insert(0, str(Patlist[index].Naca))
    e_CurrentPatNACA.grid(column=1, row=12)

    l_sep_left = tkinter.Label(Edit, text="---------------------------------")
    l_sep_right = tkinter.Label(Edit, text="--------------------------------")
    l_sep_left.grid(column=0, row=13)
    l_sep_right.grid(column=1, row=13)

    b_OK = tkinter.Button(Edit, text="OK",command=lambda: [
        Patlist[index].setAlarmt(e_CurrentPatAlarmt.get()),
        Patlist[index].setAlarmstr(e_CurrentPatAlarmstr.get()),
        Patlist[index].setBOplace(e_CurrentPatBO.get()),
        Patlist[index].setBOt(e_CurrentPatBot.get()),
        Patlist[index].setHSTt(e_CurrentPatHSTt.get()),
        Patlist[index].setTransportOrg(e_CurrentPatTransportAgency.get()),
        Patlist[index].setEndt(e_CurrentPatEndt.get()),
        Patlist[index].setNaca(e_CurrentPatNACA.get()),
        Patlist[index].setfinished(Done.get()),
        write_list(Patlist),
        Update_lables(), 
        Edit.destroy()
        ])
    b_Cancel = tkinter.Button(Edit, text="Abbruch",command=Edit.destroy)

    b_OK.grid(row=14, column=1)
    b_Cancel.grid(row=14, column=0)

def NewPat():
    global CurrentPatindex
    print("Neuer Patient mit Ablagenummer ", latestpatindex()+1)
    Patlist.append(functions.Patient(latestpatindex()+1))
    CurrentPatindex = latestpatindex()
    Edit_pat(CurrentPatindex)

def NewPat_Button():                                         #creates a new patient and adds them to the Ende of the list
    top = tkinter.Toplevel(main_window)
    top.title("Neuer Patient" )
    l_newPatinfo = tkinter.Label(top, text= "Neuer Patient mit der Ablagenummer "+ str(latestpatindex()+1))
    l_newPatinfo.pack()

    b_OK = tkinter.Button(top, text="OK",command=lambda: [NewPat(), Update_lables(), top.destroy()])
    b_Cancel = tkinter.Button(top, text="Abbruch",command=top.destroy)

    b_OK.pack()
    b_Cancel.pack()

def DelPat():
    global CurrentPatindex
    if CurrentPatindex > 0:
        Patlist.pop()
        print("Patient mit Nummer ", CurrentPatindex, " gelöscht")
        CurrentPatindex = CurrentPatindex -1
        write_list(Patlist)

def DelPat_Button():
    DelPat()
    Update_lables()

def NewBetreuung():
    global Betreuungen
    Betreuungen = Betreuungen + 1
    print("Neue Betreung mit der Nummer", Betreuungen)

def NewBetreuung_Button():
    NewBetreuung()
    Update_lables()

def DelBetreuung():
    global Betreuungen
    if Betreuungen > 0:
        Betreuungen = Betreuungen -1
        print("Eine Betreuung gelöscht, die Neue Nummer ist nun ", Betreuungen, " Betreuungen")

def DelBetreuung_Button():
    DelBetreuung()
    Update_lables()

def Init_Stats():
    Init = tkinter.Toplevel(main_window)
    Init.title("Ambulanzdaten eingeben")

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

    b_OK = tkinter.Button(Init, text="OK",command=lambda: [
        setNum(e_AmbNr.get()),
        setName(e_AmbNam.get()),
        setDate(e_AmbDate.get()),
        Update_lables(), 
        Init.destroy()
        ])
    b_Cancel = tkinter.Button(Init, text="Abbruch",command=Init.destroy)

    b_OK.grid(row=3, column=1)
    b_Cancel.grid(row=3, column=0)

def write_list(list):
    global AmbName
    global AmbDate
    global AmbNum
    with open("PatDat/" + re.sub('[^0-9]', '', AmbNum) +".ambdat", "wb") as fp:
        pickle.dump(list, fp)
        print("Daten in Datei geschrieben")

def read_list():
    global AmbName
    global AmbDate
    with open("PatDat/" + re.sub('[^0-9]', '', AmbNum) +".ambdat", "rb") as fp:
        n_list = pickle.load(fp)
        print("Daten aus Datei geladen")
        return n_list

def Button_read_list():
    global Patlist
    global CurrentPatindex
    Patlist = read_list()
    CurrentPatindex = 0
    Update_lables()

def ExportPatlist():
    path = 'Export/' + re.sub(r'\W+', '_', AmbNum) + "_" + AmbName + '.csv'
    with open(path, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["Pat-Nr","Alarmzeit", "B.Grund", "BO", "BO-Zeit", "HST-Zeit", "Abtransport", "NACA", "Fertig", str(Betreuungen) + " Betreuungen"])
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
                    Patlist[x].TransportAgency, 
                    Patlist[x].Naca, 
                    is_finished
                ])
    print("Patientenliste exportiert")

def setDatfromFile(path):
    global AmbNum
    global AmbName
    global AmbDate
    global Betreuungen
    File=open(path, "r")
    AmbNum = re.sub('\n', '', File.readline())
    AmbName = re.sub('\n', '', File.readline())
    AmbDate = re.sub('\n', '', File.readline())
    Betreuungen = int(re.sub('\n', '', File.readline()))
    File.close()

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
    tmp=open(path, "w+")
    tmp.close()
    File=open(path, "w+")
    File.writelines(AmbNum + "\n")
    File.writelines(AmbName + "\n")
    File.writelines(AmbDate + "\n")
    File.writelines(str(Betreuungen))
    File.close()

def Button_saveDat():
    filepath = tkinter.filedialog.asksaveasfile(filetypes=[("Data-Datei",".dat")]).name
    saveDatinFile(filepath)
    Button_read_list()
    Update_lables()


main_window = tkinter.Tk(className='~Amulanz-Dashboard~')

b_newBet = tkinter.Button(main_window, text='Neue Betreuung', command=lambda: (NewBetreuung_Button()), bg="green")
b_newBet.grid(column=2, row=0)
l_Betreuungen = tkinter.Label(main_window, text=str(Betreuungen) + " Betreuungen")
l_Betreuungen.grid(column=1, row=0)
b_DelBet = tkinter.Button(main_window, text='Betreuung Löschen', command=lambda: (DelBetreuung_Button()), bg="green")
b_DelBet.grid(column=0, row=0)

b_newPat = tkinter.Button(main_window, text='Neuesten Pat. löschen', command=lambda: (DelPat_Button()), bg="red")
b_newPat.grid(column=0, row=1)
l_Pat = tkinter.Label(main_window, text=str(latestpatindex()) + " Patienten")
l_Pat.grid(column=1, row=1)
b_newPat = tkinter.Button(main_window, text='Neuer Patient', command=lambda: (NewPat_Button()), bg="red")
b_newPat.grid(column=2, row=1)

l_sep_left = tkinter.Label(main_window, text="-----------------------")
l_sep_center = tkinter.Label(main_window, text="----------------------")
l_sep_right = tkinter.Label(main_window, text="-----------------------")
l_sep_left.grid(column=0, row=2)
l_sep_center.grid(column=1, row=2)
l_sep_right.grid(column=2, row=2)

l_textr3 = tkinter.Label(main_window, text="Akuell Angezeigter Pat Nr:")
l_textr3.grid(column=0, row=3)
l_CurrentPatNum = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Num))
l_CurrentPatNum.grid(column=1, row=3)


l_textr4 = tkinter.Label(main_window, text="Einsatzbeginn:")
l_textr4.grid(column=0, row=4)
l_CurrentPatAlarmt = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Alarmt))
l_CurrentPatAlarmt.grid(column=1, row=4)


l_textr5 = tkinter.Label(main_window, text="Berufungsgrund:")
l_textr5.grid(column=0, row=5)
l_CurrentPatAlarmstr = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Alarmstr))
l_CurrentPatAlarmstr.grid(column=1, row=5)


l_textr6 = tkinter.Label(main_window, text="Berufungsort:")
l_textr6.grid(column=0, row=6)
l_CurrentPatBO = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].BOplace))
l_CurrentPatBO.grid(column=1, row=6)


l_textr7 = tkinter.Label(main_window, text="Zeit am BO:")
l_textr7.grid(column=0, row=7)
l_CurrentPatBot = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].BOt))
l_CurrentPatBot.grid(column=1, row=7)


l_textr8 = tkinter.Label(main_window, text="Zeit auf der Behandlung:")
l_textr8.grid(column=0, row=8)
l_CurrentPatHSTt = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].HSTt))
l_CurrentPatHSTt.grid(column=1, row=8)


l_textr9 = tkinter.Label(main_window, text="Abtransport-Organisation:")
l_textr9.grid(column=0, row=9)
l_CurrentPatTransA = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].TransportAgency))
l_CurrentPatTransA.grid(column=1, row=9)


l_textr10 = tkinter.Label(main_window, text="Einsatzende:")
l_textr10.grid(column=0, row=10)
l_CurrentPatEndt = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Endt))
l_CurrentPatEndt.grid(column=1, row=10)


l_textr11 = tkinter.Label(main_window, text="Protokoll fertig:")
l_textr11.grid(column=0, row=11)
l_CurrentPatfin = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].finished))
l_CurrentPatfin.grid(column=1, row=11)


l_textr12 = tkinter.Label(main_window, text="NACA:")
l_textr12.grid(column=0, row=12)
l_CurrentPatNACA = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Naca))
l_CurrentPatNACA.grid(column=1, row=12)



b_prevPat = tkinter.Button(main_window, text="<", width=20, command=lambda: (PrevPat_Button()))
b_prevPat.grid(row=13, column=0)

b_nextPat = tkinter.Button(main_window, text=">", width=20, command=lambda: (NextPat_Button()))
b_nextPat.grid(row=13, column=2)

b_EditPat = tkinter.Button(main_window, width=20, text="Pat Bearbeiten", command=lambda: (Edit_pat(CurrentPatindex)))
b_EditPat.grid(row=13, column=1)

l_AmbNum = tkinter.Label(main_window, text=AmbNum, font=1)
l_AmbNum.grid(row=15, column=0)

l_AmbName = tkinter.Label(main_window, text=AmbName, font=1)
l_AmbName.grid(row=14, column=0)

l_AmbDate = tkinter.Label(main_window, text=AmbDate, font=1)
l_AmbDate.grid(row=16, column=0)

b_init = tkinter.Button(main_window, text="Daten manuell Setzen", command=lambda:[Init_Stats()])
b_init.grid(row=14, column=1)

b_loaddat = tkinter.Button(main_window, text="Daten aus Datei lesen", command=lambda:[Button_setDat()])
b_loaddat.grid(row=15, column=1)

b_savedat = tkinter.Button(main_window, text="Daten in Datei speichern", command=lambda:[Button_saveDat()])
b_savedat.grid(row=16, column=1)



b_save = tkinter.Button(main_window, text="Patienten speichern", command=lambda:[write_list(Patlist)])
b_save.grid(row=14, column=2)

b_load = tkinter.Button(main_window, text="Patienten laden", command=lambda:[Button_read_list()])
b_load.grid(row=15, column=2)

b_export = tkinter.Button(main_window, text="Patienten Exportieren (csv)", command=lambda:[ExportPatlist()])
b_export.grid(row=16, column=2)


icon = tkinter.PhotoImage(file="image_files/RK.png")
main_window.wm_iconphoto(False, icon)


main_window.mainloop()