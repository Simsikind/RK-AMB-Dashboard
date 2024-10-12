import functions
from datetime import datetime
import tkinter

AmbNum = "xxxx/xxxxx-x"
AmbName = "Ambulanzname"
AmbDate = "DD:MM:YYYY"
Betreuungen = 0
CurrentPatindex = 0
Patlist = []
Patlist.append(functions.Patient(0))                        #Add Patient zero, so thet the Index ist the same as the "Ablagenummer"
Patlist[0].setAlarmt("xx:xx")
Patlist[0].setAlarmstr("Berufungsgrund")
Patlist[0].setBOt("xx:xx")
Patlist[0].setBOplace("Berufungsort")
Patlist[0].setHSTt("xx:xx")
Patlist[0].setTransportOrg("Rettungsorganisation")
Patlist[0].setTransOrdert("xx:xx")
Patlist[0].setEndt("xx:xx")
Patlist[0].setfinished(False)
Patlist[0].setNaca(0)



def PrevPat_Button():
    global CurrentPatindex
    if CurrentPatindex > 0:
        CurrentPatindex = CurrentPatindex -1
    print("Current Patient Index: ", CurrentPatindex)
    Update_lables()

def NextPat_Button():
    global CurrentPatindex
    if Patlist[CurrentPatindex+1]:
        CurrentPatindex = CurrentPatindex +1
    print("Current Patient Index: ", CurrentPatindex)
    Update_lables()

def latestpatindex():                                       #gets the index of the latest Patient
    z = 0
    for x in Patlist:
        z = z+1
    return z-1

def Update_lables():
    l_Pat.config(text=str(latestpatindex()) + " Patienten")
    l_Betreuungen.config(text=str(Betreuungen) + " Betreuungen")
    l_CurrentPatNum.config(text= str(Patlist[CurrentPatindex].Num))


def NewPat():
    global CurrentPatindex
    print("Create new patient with number: ", latestpatindex()+1)
    Patlist.append(functions.Patient(latestpatindex()+1))
    CurrentPatindex = latestpatindex()


def NewPat_Button():                                               #creates a new patient and adds them to the Ende of the list
    top = tkinter.Toplevel(main_window)
    top.title("Neuer Patient" )
    l_newPatinfo = tkinter.Label(top, text= "Neuer Patient mit der Ablagenummer "+ str(latestpatindex()+1))
    l_newPatinfo.pack()

    b_OK = tkinter.Button(top, text="OK",command=lambda: [NewPat(), Update_lables(), top.destroy()])
    b_Cancel = tkinter.Button(top, text="Abbruch",command=top.destroy)

    b_OK.pack()
    b_Cancel.pack()
   

def NewBetreuung():
    global Betreuungen
    Betreuungen = Betreuungen + 1
    print("Neue Betreung mit der Nummer", Betreuungen)

def NewBetreuung_Button():
    NewBetreuung()
    Update_lables()

main_window = tkinter.Tk(className=' Simons Amulanz-Dashboard')

b_newBet = tkinter.Button(main_window, text='Neue Betreuung', command=lambda: (NewBetreuung_Button()))
b_newBet.grid(column=0, row=0)
l_Betreuungen = tkinter.Label(main_window, text=str(Betreuungen) + " Betreuungen")
l_Betreuungen.grid(column=1, row=0)

b_newPat = tkinter.Button(main_window, text='Neuer Patient', command=lambda: (NewPat_Button()))
b_newPat.grid(column=0, row=1)
l_Pat = tkinter.Label(main_window, text=str(latestpatindex()) + " Patienten")
l_Pat.grid(column=1, row=1)




l_textr3 = tkinter.Label(main_window, text="Akuell Angezeigter Pat Nr: ")
l_textr3.grid(column=0, row=3)
l_CurrentPatNum = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Num))
l_CurrentPatNum.grid(column=1, row=3)


l_textr4 = tkinter.Label(main_window, text="Einsatzbeginn: ")
l_textr4.grid(column=0, row=4)
l_CurrentPatAlarmt = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Alarmt))
l_CurrentPatAlarmt.grid(column=1, row=4)


l_textr5 = tkinter.Label(main_window, text="Berufungsgrund: ")
l_textr5.grid(column=0, row=5)
l_CurrentPatAlarmstr = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Alarmstr))
l_CurrentPatAlarmstr.grid(column=1, row=5)


l_textr6 = tkinter.Label(main_window, text="Berufungsort: ")
l_textr6.grid(column=0, row=6)
l_CurrentPatBO = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].BOplace))
l_CurrentPatBO.grid(column=1, row=6)


l_textr7 = tkinter.Label(main_window, text="Zeit am BO: ")
l_textr7.grid(column=0, row=7)
l_CurrentPatBot = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].BOt))
l_CurrentPatBot.grid(column=1, row=7)


l_textr8 = tkinter.Label(main_window, text="Zeit auf der Behandlung: ")
l_textr8.grid(column=0, row=8)
l_CurrentPatHSTt = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].HSTt))
l_CurrentPatHSTt.grid(column=1, row=8)


l_textr9 = tkinter.Label(main_window, text="Abtransport (Wenn ja welche Orga): ")
l_textr9.grid(column=0, row=9)
l_CurrentPatHSTt = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].TransportAgency))
l_CurrentPatHSTt.grid(column=1, row=9)


l_textr10 = tkinter.Label(main_window, text="Einsatzende: ")
l_textr10.grid(column=0, row=10)
l_CurrentPatEndt = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Endt))
l_CurrentPatEndt.grid(column=1, row=10)


l_textr11 = tkinter.Label(main_window, text="Protokoll fertig: ")
l_textr11.grid(column=0, row=11)
l_CurrentPatfin = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].finished))
l_CurrentPatfin.grid(column=1, row=11)


l_textr12 = tkinter.Label(main_window, text="NACA: ")
l_textr12.grid(column=0, row=12)
l_CurrentPatNACA = tkinter.Label(main_window, text= str(Patlist[CurrentPatindex].Naca))
l_CurrentPatNACA.grid(column=1, row=12)



b_prevPat = tkinter.Button(main_window, text="<", lambda:(width=main_window.winfo_width / 3), command=lambda: (PrevPat_Button()))
b_prevPat.grid(column=0, row=100)

b_nextPat = tkinter.Button(main_window, text=">", width=main_window.winfo_width / 3, command=lambda: (NextPat_Button()))
b_nextPat.grid(column=2, row=100)

b_EditPat = tkinter.Button(main_window, width=main_window.winfo_width / 3, text="Pat Bearbeiten", command=lambda: (NextPat_Button()))
b_EditPat.grid(column=1, row=100)

main_window.mainloop()