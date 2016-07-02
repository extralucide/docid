#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
__author__ = 'Olivier.Appere'
import re
import sqlite3 as lite

class Swrd():
    def __init__(self,
                 list_tbl_tables_begin=[],
                 **kwargs):
        if "callback" in self.__dict__:
            print "CALLBACK",self.__dict__["callback"]
            self.callback = self.__dict__["callback"]
        else:
            self.callback = False
        self.dico_alias = {}
        self.dico_ext_signal = {}
        self.dico_int_signal = {}
        self.dico_missing_signals = {}
        self.list_tbl_tables_begin = list_tbl_tables_begin
        self.nb_errors = 0

    def log(self,
            text,
            error=False,
            gui_display=True):

        if self.callback and gui_display:
            if error:
                self.callback(text,color = "yellow",display_gui=gui_display)
            else:
                self.callback(text,display_gui=gui_display)
        else:
            print text

    def traceError(self,signal,req):
        #print "Signal/Alias {:s} used in requirement {:s} not found.".format(signal,req)
        if signal in self.dico_missing_signals:
            self.dico_missing_signals[signal].append(req)
        else:
            self.dico_missing_signals[signal] = [req]
        self.nb_errors += 1

    def populateDicoExtSignal(self,index=3):
        max = len(self.list_tbl_tables_begin)
        #print "MAX",max
        found = False
        #print "TBL",self.list_tbl_tables_begin
        for index in range(1,max+1):
            #print "TBL:",self.list_tbl_tables_begin[index]
            first_cell = self.list_tbl_tables_begin[index][0][0]
            if "External" in first_cell:
                found =True
                print "Found external signals table"
                break
        if found:
            for line in self.list_tbl_tables_begin[index]:
                if len(line) > 9:
                    signal_name = self.isSignal(line[2].replace("\r",""))
                    if signal_name:
                        self.dico_ext_signal[signal_name] = {"data_flow":line[1].replace("\r",""),
                                                            "range":line[5].replace("\r",""),
                                                            "left":line[8].replace("\r",""),
                                                            "right":line[9].replace("\r","")}
                elif len(line) > 8:
                    signal_name = self.isSignal(line[2].replace("\r",""))
                    if signal_name:
                        self.dico_ext_signal[signal_name] = {"data_flow":line[1].replace("\r",""),
                                                            "range":line[5].replace("\r",""),
                                                            "left":line[8].replace("\r",""),
                                                            "right":""}
        nb_signals = len(self.dico_ext_signal)
        return nb_signals

    def populateDicoIntSignal(self):
        max = len(self.list_tbl_tables_begin)
        found = False
        for index in range(1,max+1):
            first_cell = self.list_tbl_tables_begin[index][0][0]
            if "Internal" in first_cell:
                found =True
                print "Found internal signals table"
                break
        if found:
            for line in self.list_tbl_tables_begin[index]:
                if len(line) > 8:
                    signal_name = self.isSignal(line[2].replace("\r",""))
                    if signal_name:
                        self.dico_int_signal[signal_name] = {"data_flow":line[1].replace("\r",""),
                                                            "range":line[4].replace("\r",""),
                                                            "left":line[7].replace("\r",""),
                                                            "right":line[8].replace("\r","")}
        nb_signals = len(self.dico_int_signal)
        return nb_signals

    def populateDicoAlias(self,index=5):
        max = len(self.list_tbl_tables_begin)
        found = False
        for index in range(1,max+1):
            first_cell = self.list_tbl_tables_begin[index][0][0]
            #print "FIRST_CELL:",first_cell
            if "Alias" in first_cell:
                found =True
                print "Found aliases table"
                break
        if found:
            for line in self.list_tbl_tables_begin[index]:
                if len(line) > 4:
                    alias_name = self.isAlias(line[0].replace("\r",""))
                    if alias_name:
                        self.dico_alias[alias_name] = {"data_flow":"",
                                                        "range":line[2].replace("\r",""),
                                                        "left":line[3].replace("\r",""),
                                                        "right":line[4].replace("\r","")}
        nb_alias = len(self.dico_alias)
        return nb_alias

    def allocateSide(self,signal):
        lh_signal = re.sub(r'(xH)','LH',signal)
        rh_signal = re.sub(r'(xH)','RH',signal)
        if lh_signal == signal:
            lh_signal = False
        if rh_signal == signal:
            rh_signal = False
        return lh_signal,rh_signal

    def allocatePhase(self,signal):
        pha_signal = re.sub(r'(PHx)','PHA',signal)
        phb_signal = re.sub(r'(PHx)','PHB',signal)
        phc_signal = re.sub(r'(PHx)','PHC',signal)
        if pha_signal == signal:
            pha_signal = False
        if phb_signal == signal:
            phb_signal = False
        if phc_signal == signal:
            phc_signal = False
        return pha_signal,pha_signal,phc_signal

    def isSignal(self,data):
        m = re.match(r'\[(.*)\]',data)
        if m:
            signal = m.group(1)
            #print "SIGNAL:",signal
        else:
            signal = False
        return signal

    def ExtSignalExists(self,signal):
        if signal in self.dico_ext_signal:
            exist = True
        else:
            exist = False
        return exist

    def IntSignalExists(self,signal):
        if signal in self.dico_int_signal:
            exist = True
        else:
            exist = False
        return exist

    def aliasExists(self,alias):
        if alias in self.dico_alias:
            exist = True
        else:
            exist = False
        return exist

    def signalExists(self,signal):
        if self.ExtSignalExists(signal) or self.IntSignalExists(signal):
            exist = True
        else:
            exist = False
        return exist

    def isAlias(self,data):
        m = re.match(r'{(.*)}',data)
        if m:
            alias = m.group(1)
            #print "SIGNAL:",signal
        else:
            alias = False
        return alias

    def sqlite_connect(self):
        try:
            self.con = lite.connect('swrd_tables.db3', isolation_level=None)
            #cur = self.con.cursor()
            #cur.execute("DROP TABLE IF EXISTS hlr_vs_chapter")
            return True
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            return False

    def sqlite_delete(self):
        try:
            #self.con = lite.connect('swrd_enm.db3', isolation_level=None)
            cur = self.con.cursor()
            cur.execute("DROP TABLE IF EXISTS swrd_tables")
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)

    def sqlite_close(self):
        if self.con:
            self.con.close()

    def sqlite_create(self):
        try:
            #con = lite.connect('swrd_enm.db3')
            cur = self.con.cursor()
            cur.executescript("""
                                BEGIN TRANSACTION;
                                DROP TABLE IF EXISTS swrd_tables;
                                CREATE TABLE swrd_tables (id INTEGER PRIMARY KEY, name TEXT, type TEXT, data_flow TEXT, range TEXT, left TEXT, right TEXT);
                                COMMIT;
                """)
            self.con.commit()
            print 'New SQLite database created.'
            return True
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            return False
        #finally:
        #    if con:
        #        con.close()

    def sqlite_insert_many(self,dico_signals,type):
        with self.con:
            counter = 0
            cur = self.con.cursor()
            #self.con.set_progress_handler(self.progress_handler, 1)
            #print "tbl_req_vs_chapter",tbl_req_vs_chapter
            #cur.execute("INSERT INTO last_query(database,reference,revision,project,item,release,baseline,input_date) VALUES(?,?,?,?,?,?,?,?)",(self.database,self.reference,self.revision,project,item,release,baseline,now))
            for signal_name,data in dico_signals.iteritems():
                print "Insert signal:",signal_name,type,data["data_flow"],data["range"],data["left"],data["right"]
                self.log("Found {:s}: {:s} {:s} {:s} {:s}".format(signal_name,type,data["data_flow"],data["range"],data["left"],data["right"]))
                counter += 1
                cur.execute("INSERT INTO swrd_tables(name,type,data_flow,range,left,right) VALUES(?,?,?,?,?,?)",(signal_name,type,data["data_flow"],data["range"],data["left"],data["right"]))
            #cur.executemany("INSERT INTO hlr_vs_chapter(chapter,req_id) VALUES(?,?)", tbl_req_vs_chapter)
            #print cur.rowcount
            self.con.commit()
        return counter

    def sqlite_insert(self,name,type,data_flow,range,left,right):
        with self.con:
        #con = lite.connect('swrd_enm.db3', isolation_level=None)
            cur = self.con.cursor()
        #cur.execute("SELECT hlr_vs_chapter.id FROM hlr_vs_chapter WHERE req_id LIKE '" + req_id + "' LIMIT 1")
        #data = cur.fetchone()
        #if data != None:
        #    id = data[0]
        #    cur.execute("UPDATE hlr_vs_chapter SET req_id=?,chapter=? WHERE id= ?",(req_id,chapter,id))
        #else:
            cur.execute("INSERT INTO swrd_tables(name,type,data_flow,range,left,right) VALUES(?,?,?,?,?,?)",(name,data_flow,range,left,right))

    def sqlite_get_all(self):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id,name,type,data_flow,range,left,right FROM swrd_tables")
            data = cur.fetchall()
        return data

    def sqlite_get(self,signal_name):
        with self.con:
            cur = self.con.cursor()
            try:
                cur.execute("SELECT id,name,type,data_flow,range,left,right FROM hlr_vs_chapter WHERE name LIKE '" + signal_name + "' LIMIT 1")
                data = cur.fetchone()
                if data is not None:
                    #print "DATA:",data
                    id = data[0]
                    name = data[1]
                    type = data[2]
                    data_flow = data[3]
                    left = data[4]
                    right = data[5]
                else:
                    data_flow = ""
                    left = ""
                    right = ""
            except OperationalError,e:
                print e
                chapter = ""
        return name,type,data_flow,left,right

if __name__ == '__main__':
    swrd = Swrd()
    result = swrd.isSignal("[SPI/SDSIO_SPI_PLD_REV_ID_MSB]")
    print "isSignal",result
    swrd.dico_int_signal["SPI/SDSIO_SPI_PLD_REV_ID_MSB"] = {}
    result = swrd.signalExists("SPI/SDSIO_SPI_PLD_REV_ID_MSB")
    print "signalExists",result
    un,deux = swrd.allocateSide("TBD")
    print "RES",un,deux