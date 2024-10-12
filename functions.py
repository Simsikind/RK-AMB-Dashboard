import datetime

class Patient:
    def __init__(self, Num):
        self.Num = Num
        currentTime = datetime.datetime.now()
        self.Alarmt = str(currentTime.strftime("%H:%M"))
        pass

    def setNum(self, Num):
        self.Num = Num
        pass

    def setAlarmt(self, Alarmtime):
        self.Alarmt = Alarmtime
        pass

    def setAlarmstr(self, Alarmreason):
        self.Alarmstr = Alarmreason
        pass

    def setBOt(self, BOtime):
        self.BOt = BOtime
        pass

    def setBOplace(self, BOpl):
        self.BOplace = BOpl
        pass

    def setHSTt(self, HSTtime):
        self.HSTt = HSTtime
        pass

    def setTransportOrg(self, TrOrg):
        self.TransportAgency = TrOrg
        pass

    def setEndt(self, Endt):
        self.Endt = Endt
        pass

    def setfinished(self, fin):
        self.finished = fin
        pass

    def setNaca(self, Naca):
        self.Naca = Naca
        pass

    def getInfos(self):
        print("Abrufen der Infos von Patient", self.Num)
        return str(self.Num)+str(self.Alarmt)+str(self.Alarmstr)+str(self.BOt)+str(self.BOplace)+str(self.HSTt)+str(self.TransportAgency)+str(self.Endt)+str(self.finished)+tr(self.Naca)

    Alarmt = "-"
    Alarmstr = "-"
    BOt = "-"
    BOplace = "-"
    HSTt = "-"
    TransportAgency = "-"
    Endt = "-"
    finished = False
    Naca = int(0)