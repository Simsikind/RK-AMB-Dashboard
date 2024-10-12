class Patient:
    def __init__(self, Num):
        self.Num = Num
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

    def setTransOrdert(self, TrOt):
        self.TransOrdt = TrOt
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

    Alarmt = "xx:xx"
    Alarmstr = "Berufungsgrund"
    BOt = "xx:xx"
    BOplace = "Berufungsort"
    HSTt = "xx:xx"
    TransportAgency = "Rettungsorganisation"
    TransOrdert = "xx:xx"
    Endt = "xx:xx"
    finished = False
    Naca = int(0)