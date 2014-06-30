#!/usr/bin/env python 2.7.3
## -*- coding: latin-1 -*-
# -*- coding: utf-8 -*-
from Tkinter import *
import time
import datetime
import csv
import sqlite3 as lite
import subprocess
from ConfigParser import ConfigParser
import sys
import os
# For regular expressions
import re
sys.path.append("python-docx")
try:
    import docx
except ImportError:
    print "DoCID requires the python-docx library for Python. " \
            "See https://github.com/mikemaccana/python-docx/"
                #    raise ImportError, "DoCID requires the python-docx library
from os.path import join
import zipfile
from lxml import etree
#
# Class Tool
#
class Tool():
    '''
        Class toolbox
        '''
    def CommentStripper (self,iterator):
        '''
            Remove # comment
            '''
        for line in iterator:
            if line [:1] == '#':
                continue
            if not line.strip ():
                continue
            yield line
    def getOptions(self,key,tag):
        if self.config_parser.has_option(key,tag):
            value = self.config_parser.get(key,tag)
        else:
            value = ""
        return value

    def _loadConfigSynergy(self):
        self.gen_dir = "result"
        try:
            # get generation directory
            self.gen_dir = self.getOptions("Generation","dir")
            self.ccm_server = self.getOptions("Synergy","synergy_server")
            conf_synergy_dir = self.getOptions("Synergy","synergy_dir")
            self.ccm_exe = os.path.join(conf_synergy_dir, 'ccm')
            print "Synergy config reading succeeded"
        except IOError as exception:
            print "Synergy config reading failed:", exception

##    def _loadConfigMySQL(self):
##        self.gen_dir = "result"
##        try:
##            # get generation directory
##            self.gen_dir = self.getOptions("Generation","dir")
##            conf_synergy_dir = self.getOptions("Apache","mysql_dir")
##            self.mysql_exe = os.path.join(conf_synergy_dir, 'mysql')
##        except IOError as exception:
##            print "Config reading failed:", exception

    def __init__(self):
        '''
            get in file .ini information to access synergy server
            '''
        # Get config
        self.config_parser = ConfigParser()
        self.config_parser.read('docid.ini')
        self.gen_dir = self.getOptions("Generation","dir")
        self._loadConfigSynergy()
        # En doublon avec la classe BuildDoc
        self.dico_descr_docs = {}
        self.dico_descr_docs_default = {}
        # read dictionary of generic description for doc
        # 2 columns separated by comma
        if self.config_parser.has_option("Generation","glossary"):
            file_descr_docs = self.config_parser.get("Generation","glossary")
            with open(file_descr_docs, 'rb') as file_csv_handler:
                reader = csv.reader (self.CommentStripper (file_csv_handler))
                for tag,description in reader:
                    self.dico_descr_docs_default[tag] = description

    def ccb_minutes(self):
        pass
    def plan_review_minutes(self):
        pass
    def spec_review_minutes(self):
        pass
    def scrollEvent(self,event):
        print event.delta
        if event.delta >0:
            print 'move up'
            self.help_text.yview_scroll(-2,'units')
        else:
            print 'move down'
            self.help_text.yview_scroll(2,'units')
    def onLink(self,event):
        event.widget.configure(cursor="arrow")
    def outsideLink(self,event):
        event.widget.configure(cursor="xterm")
    def populate_listbox(self,query,listbox,first,two=False):
        # populate systems listbox
        listbox.delete(0, END)
        listbox.insert(END, first)
        if two:
            result_query = self.sqlite_query(query)
            if result_query in (None,[]):
                result = None
            else:
                 # Remove doublons; attention set supprime le tri
                result = result_query
                for item in sorted(set(result)):
                    txt = item[0] + " (" + item[1] + ")"
                    listbox.insert(END, txt)
        else:
            result = self.sqlite_query(query)
             # Remove doublons; attention set supprime le tri
            for item in sorted(set(result)):
                listbox.insert(END, item[0])
        # return list of entries found in SQLite database
        return result
    def populate_specific_listbox(self,listbox,item_id,system):
        query = 'SELECT items.name FROM items LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id \
                                                LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                WHERE systems.name LIKE \'' + system + '\' ORDER BY items.name ASC'
        self.populate_listbox(query,listbox,"All")
        if item_id != ():
            listbox.selection_set(first=item_id)
            listbox.see(item_id)
            item = listbox.get(item_id)
        else:
            listbox.selection_set(first=0)
            item = ""
        return item
    def populate_components_listbox(self,listbox,item_id,item,system=""):
        if item != "" and system != "":
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            LEFT OUTER JOIN items ON items.id = link_items_components.item_id \
                                                            WHERE systems.name LIKE \'' + system + '\' AND items.name LIKE \'' + item + '\'  ORDER BY components.name ASC'
        elif system != "":
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            WHERE systems.name LIKE \'' + system + '\' ORDER BY components.name ASC'
        else:
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            ORDER BY components.name ASC'
        result_query = self.populate_listbox(query,listbox,"All")
        if item_id != ():
            listbox.selection_set(first=item_id)
            listbox.see(item_id)
            item = listbox.get(item_id)
        else:
            listbox.selection_set(first=0)
            item = ""
        if result_query in (None,[]):
            result = None
        else:
            result = result_query
        return result
    def populate_components_listbox_wo_select(self,listbox,item="",system=""):
        if item != "" and system != "":
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            LEFT OUTER JOIN items ON items.id = link_items_components.item_id \
                                                            WHERE systems.name LIKE \'' + system + '\' AND items.name LIKE \'' + item + '\'  ORDER BY components.name ASC'
        elif system != "":
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            WHERE systems.name LIKE \'' + system + '\'  ORDER BY components.name ASC'
        else:
             query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                             ORDER BY components.name ASC'
        result_query = self.populate_listbox(query,listbox,"All")
        return result_query
    def _getCRChecklist(self,status="",sw=True):
        '''
        Get checklist according to CR status
        Return None if no CCB decision is needed
        '''
        dico_status_vs_transition = {"In_Review":"To Under Modification",
                                     "Complementary_Analysis":"To Under Modification",
                                     "Postponed":"From_Postponed",
                                     "Fixed":"From Fixed"
                                    }
        result = []
        if status in dico_status_vs_transition:
            transition = dico_status_vs_transition[status]
            if sw:
                query = "SELECT check_item FROM cr_checklist WHERE transition LIKE '{:s}'".format(transition)
            else:
                query = "SELECT check_item FROM cr_pld_checklist WHERE transition LIKE '{:s}'".format(transition)
            result = self.sqlite_query(query)
        if result != []:
            return result
        else:
            return None
    def _getComponentCRType(self,component=""):
        '''
        Get CR type according to component
        Return None if no CR type found
        '''
        query = "SELECT cr_type FROM components \
                WHERE components.name LIKE '" + component + "'"
        result = self.sqlite_query(query)
        if result == None or result == []:
            cr_type = None
        else:
            cr_type = result[0][0]
        return cr_type
    def _getItemCRType(self,item="",system=""):
        '''
        Get CR type according to component
        Return None if no CR type found
        '''
        query = 'SELECT items.cr_type FROM items \
                LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id \
                LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                WHERE systems.name LIKE \'' + system + '\' AND items.name LIKE \'' + item + '\'  ORDER BY items.name ASC'
        result = self.sqlite_query(query)
        if result in (None,[]):
            cr_type = None
        else:
            cr_type = result[0][0]
        return cr_type
    def _getCRType(self,item=""):
        '''
        Get CR type according to item
        Return None if no CR type found
        '''
        query = "SELECT cr_type FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + item + "' and systems.name LIKE '" + system + "'"
        result = self.sqlite_query(query)
        if result == None or result == []:
            cr_type = None
        else:
            cr_type = result[0][0]
        return cr_type
    #
    # SQLite
    #
    def get_image(self,item):
        '''
            Get image in SQLite database
            '''
        query = "SELECT img FROM systems WHERE aircraft LIKE '{:s}'".format(item) + " LIMIT 1"
        result = self.sqlite_query_one(query)
        if result == None:
            image_name = "earhart12_240x116.gif"
        else:
            image_name = result[0]
        return image_name
    def get_database(self,name):
        query = "SELECT items.database,aircraft FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + name + "'"
        result = self.sqlite_query(query)
        if result != []:
            return result[0][0],result[0][1]
        else:
            return None,None
    def get_sys_item_database(self,system,item):
        query = "SELECT items.database,aircraft FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + item + "' and systems.name LIKE '" + system + "'"
##        print "TEST get_sys_item_database",query
        result = self.sqlite_query(query)
        if result != []:
            return result[0][0],result[0][1]
        else:
            return None,None
    def get_sys_database(self):
        if self.system != "":
            query = "SELECT systems.database,aircraft FROM systems WHERE systems.name LIKE '" + self.system + "'"
##            print "TEST get_sys_database",query
            result = self.sqlite_query(query)
            if result != []:
                return result[0][0],result[0][1]
            else:
                return None,None
        else:
            return None,None
    def get_ci_identification(self,item):
        if item != "":
            query = "SELECT ci_identification FROM items WHERE items.name LIKE '" + item + "'"
            result = self.sqlite_query(query)
            if result == None or result == []:
                ci_id = "None"
            else:
                ci_id = result[0][0]
        else:
            ci_id = "None"
        return ci_id
    def get_ci_sys_item_identification(self,system,item):
        query = "SELECT ci_identification FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + item + "' and systems.name LIKE '" + system + "'"
        result = self.sqlite_query(query)
        if result == None or result == []:
            ci_id = "None"
        else:
            ci_id = result[0][0]
        return ci_id
    def get_sys_item_old_workflow(self,system,item):
        query = "SELECT old_workflow FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + item + "' and systems.name LIKE '" + system + "'"
        result = self.sqlite_query(query)
        if result in (None,[]):
            old_workflow = False
        else:
            if result[0][0] == 1:
                old_workflow = True
            else:
                old_workflow = False
        return old_workflow
    def get_ear(self,item):
        if item != "" and item != "None":
            query = "SELECT ear FROM items LEFT OUTER JOIN link_systems_items ON item_id = items.id LEFT OUTER JOIN systems ON systems.id = system_id WHERE items.name LIKE '" + item + "'"
            result = self.sqlite_query(query)
            if result == None:
                ear = ""
            else:
                ear = result[0][0]
        else:
            ear = ""
        return ear
    def get_lastquery(self):
        query = 'SELECT database,item,project,release FROM last_query WHERE id = 1'
        item = self.sqlite_query(query)
        item = cur.fetchall()
        return item
    def sqlite_save_projects(self,projects_set):
        try:
            con = lite.connect('docid.db3')
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS gen_save")
            cur.execute("CREATE TABLE gen_save(release TEXT, baseline TEXT, project TEXT)")
            cur.executemany("INSERT INTO gen_save VALUES(?, ?, ?)", projects_set)
            con.commit()
##            print time.strftime("%H:%M:%S", time.localtime()) + " Generation set saved."
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
    def sqlite_restore_projects(self):
        query = "SELECT release,baseline,project FROM gen_save"
        result = self.sqlite_query(query)
        return result
    def sqlite_create(self):
        try:
            con = lite.connect('docid.db3')
            cur = con.cursor()
            cur.executescript("""
                                BEGIN TRANSACTION;
                                CREATE TABLE components (id INTEGER PRIMARY KEY, description TEXT, ci_id TEXT, cr_type TEXT, name TEXT);
                                INSERT INTO components VALUES(1,'Electric Network Management','A338','SW_ENM','ENM');
                                INSERT INTO components VALUES(2,'Monitoring and communication','A326','SW_BITE','BITE');
                                INSERT INTO components VALUES(3,'Whindshield Deicing Control and Contactor','A331','SW_WHCC','WHCC');
                                INSERT INTO components VALUES(4,'PLD SDS IO','A325','PLD_SDSIO','SDSIO');
                                INSERT INTO components VALUES(5,'PLD TIE','A415','PLD_TIE','TIE');
                                INSERT INTO components VALUES(6,'Ethernet communication','A330','SW_COM','COM');
                                INSERT INTO components VALUES(7,'Plans',NULL,'SW_PLAN','PLAN');
                                CREATE TABLE cr_checklist (check_item TEXT, transition TEXT);
                                INSERT INTO cr_checklist VALUES('decide if postponed CR shall be corrected on planned release','From Postponed');
                                INSERT INTO cr_checklist VALUES('check that defect/evolution is understandable (description, problem condition, ...)
                                ','To Under Modification');
                                INSERT INTO cr_checklist VALUES('check CR field coherency with SCMP process','To Under Modification');
                                INSERT INTO cr_checklist VALUES('discuss and validate classification in case of Defect','To Under Modification');
                                INSERT INTO cr_checklist VALUES('approve corrective action and impact analysis','To Under Modification');
                                INSERT INTO cr_checklist VALUES('schedule correction release','To Under Modification');
                                INSERT INTO cr_checklist VALUES('check CR field coherency with SCMP process','From Fixed');
                                INSERT INTO cr_checklist VALUES('confirm that performed activities (development and verification) are complete and consistent','From Fixed');
                                CREATE TABLE cr_pld_checklist (field1, field2);
                                INSERT INTO cr_pld_checklist VALUES('check_item','transition');
                                INSERT INTO cr_pld_checklist VALUES('decide if postponed CR shall be corrected on planned release','From Postponed');
                                INSERT INTO cr_pld_checklist VALUES('check that defect/evolution is understandable (description, problem condition, ...)
                                ','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('check CR field coherency with configuration management process','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('discuss and validate classification','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('approve corrective action and impact analysis','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('schedule ?CR implemented for? correction','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('check CR field coherency with configuration management process
                                -?Under_modification? reviewed and approved
                                -?Under_verification? reviewed and approved','From Fixed');
                                INSERT INTO cr_pld_checklist VALUES('confirm that performed activities (development and verification) are complete and consistent','From Fixed');
                                CREATE TABLE document_types (description TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO document_types VALUES('Hardware Confguration Management Record',1,'HCMR');
                                INSERT INTO document_types VALUES('Software Configuration Index',2,'SCI');
                                INSERT INTO document_types VALUES('Configuration Index Document',3,'CID');
                                INSERT INTO document_types VALUES('Software Quality Assurance Plan',4,'SQAP');
                                INSERT INTO document_types VALUES('Plan for Software Aspects of Certification',5,'PSAC');
                                INSERT INTO document_types VALUES('Software Development Plan',6,'SDP');
                                INSERT INTO document_types VALUES('Software Verification Plan',7,'SVP');
                                INSERT INTO document_types VALUES('Software Configuration Management Plan',8,'SCMP');
                                CREATE TABLE documents (status_id NUMERIC, reference TEXT, last_revision TEXT, id INTEGER PRIMARY KEY, item_id NUMERIC, type NUMERIC);
                                INSERT INTO documents VALUES(41,'PQ 0.1.0.160',NULL,1,'',4);
                                INSERT INTO documents VALUES(41,'PQ 0.1.0.155',NULL,2,5,4);
                                INSERT INTO documents VALUES(45,'PQ 0.1.0.163',1.2,3,1,4);
                                INSERT INTO documents VALUES(41,'PQ 0.1.0.169',NULL,4,15,4);
                                INSERT INTO documents VALUES(45,'ET3335-E',NULL,5,1,6);
                                INSERT INTO documents VALUES(45,'ET3337-E',NULL,6,1,8);
                                INSERT INTO documents VALUES(45,'ET3334-E',NULL,7,1,5);
                                INSERT INTO documents VALUES(45,'ET3336-E',NULL,8,1,7);
                                CREATE TABLE gen_save(release TEXT, baseline TEXT, project TEXT);
                                INSERT INTO gen_save VALUES('SW_PLAN/01','SW_PLAN_01_07','SW_PLAN-1.7');
                                INSERT INTO gen_save VALUES('SW_PLAN_PDS_SDS/01','SW_PLAN_PDS_SDS_01_03','SW_PLAN_PDS_SDS-1.3');
                                INSERT INTO gen_save VALUES('SW_ENM/01','SW_ENM_01_06','SW_ENM-1.6');
                                INSERT INTO gen_save VALUES('SW_ENM/01','SW_ENM_01_06','CODE_SW_ENM-1.6');
                                INSERT INTO gen_save VALUES('SW_ENM_DELIV/01','SW_ENM_DELIV_01_02','SW_ENM_DELIV-1.2');
                                CREATE TABLE history (writer_id NUMERIC, date TEXT, issue TEXT, document_id NUMERIC, id INTEGER PRIMARY KEY, modifications TEXT);
                                CREATE TABLE items (cr_type TEXT, old_workflow NUMERIC, ci_identification TEXT, database TEXT, description TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO items VALUES(NULL,NULL,'A333','db_g7000_ppds','AC logic board',1,'ACLOG');
                                INSERT INTO items VALUES(NULL,NULL,'A334','db_g7000_ppds','DC logic board',2,'DCLOG');
                                INSERT INTO items VALUES(NULL,NULL,NULL,'db_g7000_ppds','Electrical Distribution Management Unit',3,'EDMU');
                                INSERT INTO items VALUES(NULL,NULL,'A335','db_g7000_ppds','EMERgency LOGic board',4,'EMERLOG');
                                INSERT INTO items VALUES('ESSNESS',NULL,'A338','db_sms_pds','ESSential Non ESSential board',5,'ESSNESS');
                                INSERT INTO items VALUES('TIE',NULL,NULL,'db_sms_pds','TIE board',6,'TIE');
                                INSERT INTO items VALUES('SDSIO',NULL,'A330','db_sms_pds','Secondary Distribution System Input Output',7,'SDSIO');
                                INSERT INTO items VALUES(NULL,1,'A267','db_787','Electrical Load Control Unit - Protection',8,'ELCU_P');
                                INSERT INTO items VALUES(NULL,NULL,NULL,NULL,'Electrical Load Control Unit - Command',9,'ELCU_C');
                                INSERT INTO items VALUES(NULL,1,'A295','db_a350_enmu','Electrical Network Management Unit',10,'ENMU');
                                INSERT INTO items VALUES(NULL,1,'A297','db_a350_rccb','Remote Control Circuit Breaker',11,'RCCB');
                                INSERT INTO items VALUES(NULL,1,'A304','db_egp','Windshield Wiper Electronic Unit',12,'WECU');
                                INSERT INTO items VALUES(NULL,NULL,NULL,'db_sms_ocp','Overhead Cockpit Panel',13,'ARINC');
                                INSERT INTO items VALUES('WHCC',NULL,'A331','db_sms_pds','Windshield Heater Control Command',15,'WHCC');
                                INSERT INTO items VALUES(NULL,1,'A320','db_cseries_cpdd','Circuit Protection Device Detector',16,'CPDD');
                                INSERT INTO items VALUES(NULL,NULL,'A417','db_mc21_ppds','Electrical Network Management Unit',17,'ENMU');
                                CREATE TABLE last_query (id INTEGER PRIMARY KEY, reference TEXT, revision TEXT ,database TEXT, project TEXT, item TEXT, release TEXT, baseline TEXT, input_date timestamp);
                                INSERT INTO last_query VALUES(51,'','','db_sms_pds','','ESSNESS','SW_ENM/02','','2014-05-21 10:30:13.425000');
                                INSERT INTO last_query VALUES(53,'ET3142-E','1D2','db_sms_pds','All','','SW_ENM/02','SW_ENM_02_04','2014-05-13 15:44:49.471000');
                                INSERT INTO last_query VALUES(55,'','','db_sms_pds','','SDSIO','SW_ENM/02','','2014-05-19 15:22:05.019000');
                                INSERT INTO last_query VALUES(56,'','','db_sms_pds','','WHCC','SW_ENM/02','','2014-05-19 15:36:35.260000');
                                CREATE TABLE link_items_components (component_id NUMERIC, id INTEGER PRIMARY KEY, item_id NUMERIC);
                                INSERT INTO link_items_components VALUES(1,1,5);
                                INSERT INTO link_items_components VALUES(2,2,5);
                                INSERT INTO link_items_components VALUES(3,3,15);
                                INSERT INTO link_items_components VALUES(4,4,7);
                                INSERT INTO link_items_components VALUES(5,5,6);
                                INSERT INTO link_items_components VALUES(6,6,7);
                                INSERT INTO link_items_components VALUES(2,7,7);
                                INSERT INTO link_items_components VALUES(7,8,5);
                                INSERT INTO link_items_components VALUES(7,9,6);
                                INSERT INTO link_items_components VALUES(7,10,7);
                                INSERT INTO link_items_components VALUES(7,11,15);
                                CREATE TABLE link_std_pn (id NUMERIC, pn_id NUMERIC, std_id NUMERIC);
                                CREATE TABLE link_systems_items (id INTEGER PRIMARY KEY, item_id NUMERIC, system_id NUMERIC);
                                INSERT INTO link_systems_items VALUES(1,1,3);
                                INSERT INTO link_systems_items VALUES(2,2,3);
                                INSERT INTO link_systems_items VALUES(3,3,3);
                                INSERT INTO link_systems_items VALUES(4,4,3);
                                INSERT INTO link_systems_items VALUES(5,5,2);
                                INSERT INTO link_systems_items VALUES(6,6,2);
                                INSERT INTO link_systems_items VALUES(7,7,11);
                                INSERT INTO link_systems_items VALUES(8,8,1);
                                INSERT INTO link_systems_items VALUES(9,9,1);
                                INSERT INTO link_systems_items VALUES(10,10,4);
                                INSERT INTO link_systems_items VALUES(11,11,4);
                                INSERT INTO link_systems_items VALUES(12,12,5);
                                INSERT INTO link_systems_items VALUES(13,13,6);
                                INSERT INTO link_systems_items VALUES(14,15,8);
                                INSERT INTO link_systems_items VALUES(15,16,9);
                                INSERT INTO link_systems_items VALUES(16,17,12);
                                CREATE TABLE part_number (id NUMERIC, name TEXT);
                                CREATE TABLE review_types (description TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO review_types VALUES('Software Plan Review',1,'PR');
                                INSERT INTO review_types VALUES('Software Requirement Review',2,'SRR');
                                INSERT INTO review_types VALUES('Software Design Review',3,'SDR');
                                INSERT INTO review_types VALUES('Software COde Review',4,'SCOR');
                                INSERT INTO review_types VALUES('High Level Test Readiness Review',5,'HL-TRR');
                                INSERT INTO review_types VALUES('Low Level Test Readiness Review',6,'LL-TRR');
                                INSERT INTO review_types VALUES('High Level Test Review',7,'HL-TR');
                                INSERT INTO review_types VALUES('Low Level Test Review',8,'LL-TR');
                                INSERT INTO review_types VALUES('Software Conformity Review',9,'SCR');
                                CREATE TABLE standards (id NUMERIC, name TEXT);
                                CREATE TABLE status (description TEXT, id INTEGER PRIMARY KEY, name TEXT, transition TEXT, type TEXT);
                                INSERT INTO status VALUES('peer data review has been performed and has been taken into account.',10,'Reviewed',0,'data');
                                INSERT INTO status VALUES('No peer data review has been performed yet.',11,'New',0,'data');
                                INSERT INTO status VALUES('review successfully passed',17,'Accepted',0,'review');
                                INSERT INTO status VALUES('Document has been signed AQ',45,'Approved',0,'data');
                                CREATE TABLE status_id (description TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO status_id VALUES('Not created.',1,'None');
                                CREATE TABLE systems (database TEXT, ear TEXT, img TEXT, aircraft TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO systems VALUES('db_787',NULL,'B787.gif','B787',1,'Boeing B787 PPDS');
                                INSERT INTO systems VALUES('db_sms_pds',NULL,'SMS.gif','F5X',2,'Dassault F5X PDS');
                                INSERT INTO systems VALUES('db_g7000_ppds','EAR
                                Information contained herein is subject to the export administration regulations (EAR) of the united states of America and export classified under those regulations as (ECCN: 9E991). No portion of this document can be re-exported from the recipient country or re-transferred or disclosed to any other entity or person not authorized to receive it without the prior authorization of ECE.
                                ','G7000.gif','G7000',3,'Bombardier G7000 PPDS');
                                INSERT INTO systems VALUES('db_a350_xwb',NULL,'A350.gif','A350',4,'Airbus A350 EPDS');
                                INSERT INTO systems VALUES('db_egp',NULL,'A350.gif','A350',5,'Airbus A350 WWS');
                                INSERT INTO systems VALUES(NULL,NULL,'SMS.gif','F5X',6,'Dassault F5X OCP');
                                INSERT INTO systems VALUES('db_sms_pds',NULL,'SMS.gif','F5X',8,'Dassault F5X WDS');
                                INSERT INTO systems VALUES('db_cseries_cpdd',NULL,'CSERIES.gif','Cseries',9,'Bombardier CSeries EPC');
                                INSERT INTO systems VALUES('db_tools',NULL,'TOOL.gif','All',10,'Tools');
                                INSERT INTO systems VALUES('db_sms_pds',NULL,'SMS.gif','F5X',11,'Dassault F5X SDS');
                                INSERT INTO systems VALUES('db_mc21_ppds',NULL,'MC21.gif','MC21',12,'Irkut MC21 PPDS');
                                CREATE TABLE writers (id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO writers VALUES(1,'O. APPERE');
                                INSERT INTO writers VALUES(2,'F. CLOCHET');
                                COMMIT;
                """)
            con.commit()
            print 'New SQLite database created.'
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
    def storeSelection(self,project,item,release,baseline):
        '''
        Store selection in SQLite database
         -project
         -release
         -baseline
        '''
        try:
            now = datetime.datetime.now()
            con = lite.connect('docid.db3', isolation_level=None)
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS last_query (id INTEGER PRIMARY KEY, reference TEXT, revision TEXT ,database TEXT, project TEXT, item TEXT, release TEXT, baseline TEXT, input_date timestamp)")
            cur.execute("SELECT id FROM last_query WHERE item LIKE '" + item + "' LIMIT 1")
##            print "SELECT id FROM last_query WHERE item LIKE '" + item + "' LIMIT 1"
            data = cur.fetchone()
            if data != None:
                id = data[0]
##                print "Update row in SQLite database"
                cur.execute("UPDATE last_query SET database=?,reference=?,revision=?,project=?,release=?,baseline=?,input_date=? WHERE id= ?",(self.database,self.reference,self.revision,project,release,baseline,now,id))
            else:
##                print "Insert new row in SQLite database"
                cur.execute("INSERT INTO last_query(database,reference,revision,project,item,release,baseline,input_date) VALUES(?,?,?,?,?,?,?,?)",(self.database,self.reference,self.revision,project,item,release,baseline,now))
            # Keep only the 4 last input
            cur.execute("DELETE FROM last_query WHERE id NOT IN ( SELECT id FROM ( SELECT id FROM last_query ORDER BY input_date DESC LIMIT 4) x )")
            lid = cur.lastrowid
        except lite.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if con:
                con.close()
    def sqlite_query(query,database='docid.db3'):
        try:
            con = lite.connect(database)
            cur = con.cursor()
            cur.execute(query)
##            print time.strftime("%H:%M:%S", time.localtime()) + " " + query
            result = cur.fetchall()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
        return result
    def sqlite_query_one(query,database='docid.db3'):
        try:
            con = lite.connect(database)
            cur = con.cursor()
            cur.execute(query)
##            print time.strftime("%H:%M:%S", time.localtime()) + " " + query
            result = cur.fetchone()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
        return result
    # Apache
    def apache_start(self,config="httpd_home.conf"):
        # read config file
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        httpd_dir = config_parser.get("Apache","httpd_dir")
        conf_dir = config_parser.get("Apache","conf_dir")
        mysql_dir = config_parser.get("Apache","mysql_dir")
        config = conf_dir + config
        # hide commmand DOS windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        # default config
        print time.strftime("%H:%M:%S", time.localtime()) + " httpd.exe -f " + config
        proc_httpd = subprocess.Popen(httpd_dir + "httpd.exe -f " + config, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
        print time.strftime("%H:%M:%S", time.localtime()) + " mysqld --defaults-file=mysql\\bin\\my.ini --standalone --console"
        proc_mysql = subprocess.Popen(mysql_dir + "mysqld --defaults-file=mysql\\bin\\my.ini --standalone --console", stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
        stdout_httpd, stderr_httpd = proc_httpd.communicate()
        stdout_mysql, stderr_mysql = proc_mysql.communicate()
        ##    print time.strftime("%H:%M:%S", time.localtime()) + " " + stdout
        if stderr_httpd:
            print "Error while executing httpd command: " + stderr_httpd
        elif stderr_mysql:
            print "Error while executing mysql command: " + stderr_mysql
        time.sleep(1)
        return_code_httpd = proc_httpd.wait()
        return_code_mysql = proc_mysql.wait()
        print stdout_httpd
        print stdout_mysql
    # Synergy
    def ccm_query(self,query,cmd_name):
        '''
        Invoke ccm command
        '''
        stdout = ""
        stderr = ""
        # hide commmand DOS windows
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        except AttributeError:
            print "ccm_query works on Windows only."
            return "",""
        try:
            proc = subprocess.Popen(self.ccm_exe + " " + query, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
            stdout, stderr = proc.communicate()
            if stderr:
                print "Error while executing " + cmd_name + " command: " + stderr
            time.sleep(1)
            return_code = proc.wait()
        except UnicodeEncodeError as exception:
            print "Character not supported:", exception
        return stdout,stderr

    # MySQL
##    def mysql_query(self,query,cmd_name):
##        '''
##        Invoke mysql command
##        '''
##        stdout = ""
##        stderr = ""
##        # hide commmand DOS windows
##        try:
##            startupinfo = subprocess.STARTUPINFO()
##            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
####            startupinfo.wShowWindow = subprocess.SW_HIDE
##        except AttributeError:
##            print "mysql_query works on Windows only so far."
##            return "",""
##        try:
##            print self.mysql_exe + " " + query
##            proc = subprocess.Popen(self.mysql_exe + " " + query, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
##            stdout, stderr = proc.communicate()
##            print "STDOUT",stdout
##            if stderr:
##                print "Error while executing " + cmd_name + " command: " + stderr
##            time.sleep(1)
##            return_code = proc.wait()
##        except UnicodeEncodeError as exception:
##            print "Character not supported:", exception
##        return stdout,stderr

    def retrieveLastSelection(self,item):
        data = []
        try:
            data = self.sqlite_query("SELECT * FROM last_query WHERE item LIKE '" + item + "' LIMIT 1")
            if data == []:
                data = self.sqlite_query("SELECT * FROM last_query ORDER BY input_date DESC LIMIT 1")
        except:
            pass
        return data

    def getSystemName(self,item):
        query = "SELECT systems.name FROM systems \
                    LEFT OUTER JOIN link_systems_items ON link_systems_items.system_id = systems.id \
                    LEFT OUTER JOIN items ON items.id = link_systems_items.item_id \
                    WHERE items.name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result == None:
            description = "None"
        else:
            description = result[0]
        return description

    def getItemDescription(self,item):
        query = "SELECT description FROM items WHERE name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result == None:
            description = item
        else:
            if result[0] == None:
                description = ""
            else:
                description = result[0]
        return description
    def getComponentDescription(self,item):
        query = "SELECT description FROM components WHERE name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result == None:
            description = item
        else:
            if result[0] == None:
                description = ""
            else:
                description = result[0]
        return description
    def getComponentID(self,item):
        if not self._is_array(item):
            query = "SELECT ci_id FROM components WHERE name LIKE '{:s}'".format(item)
            print "getComponentID",query
            result = self.sqlite_query_one(query)
        else:
            result = None
        if result == None:
            ci_id = "None"
        else:
            if result[0] == None:
                ci_id = "None"
            else:
                ci_id = result[0]
        return ci_id
    def getListModifs(self,item):
        query = "SELECT issue,date,modifications,writers.name FROM history LEFT OUTER JOIN documents ON documents.id = document_id LEFT OUTER JOIN items ON items.id = documents.item_id LEFT OUTER JOIN writers ON writers.id = history.writer_id WHERE items.name LIKE '{:s}'".format(item)
        result = self.sqlite_query(query)
        if result == None:
            history = "None"
        else:
            history = result
        return history
    def getLastModificationLog(self,item):
        if item != "" and item != "None":
            query = "SELECT modifications FROM history LEFT OUTER JOIN documents ON documents.id = history.document_id WHERE documents.reference LIKE '{:s}' ORDER BY date DESC LIMIT 1".format(item)
            result = self.sqlite_query(query)
            if result == None:
                modif = "None"
            else:
                modif = result[0]
        else:
            modif = "None"
        return modif
    def updateLastModificationLog(self):
        now = datetime.datetime.now()
        con = lite.connect('docid.db3', isolation_level=None)
        cur = con.cursor()
        cur.execute("SELECT history.id FROM history LEFT OUTER JOIN documents ON documents.id = history.document_id WHERE reference LIKE '" + self.reference + "' AND issue LIKE '" + self.revision + "' LIMIT 1")
        data = cur.fetchone()
        if data != None:
            id = data[0]
            cur.execute("UPDATE history SET date=?,writer_id=?,modifications=? WHERE id= ?",(now,1,interface.modif_log.get(1.0,END),id))
        else:
            cur.execute("INSERT INTO history(document_id,issue,writer_id,date,modifications) VALUES(?,?,?,?,?)",(3,self.revision,1,now,interface.modif_log.get(1.0,END)))
    def getTypeDocDescription(self,item):
        query = "SELECT description FROM document_types WHERE name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result == None:
            description = "None"
        else:
            description = result[0]
        return description
    def getDocRef(self,item,type):
        query = "SELECT reference,document_types.description FROM documents LEFT OUTER JOIN items ON items.id = documents.item_id LEFT OUTER JOIN document_types ON document_types.id = documents.type WHERE document_types.name LIKE '"+ type +"' AND items.name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result != None:
            description = result[0] + " " + result[1]
        else:
            description = ""
        return description
    def getDocInfo(self,item):
        '''
            Get information on the document
            - reference allocated to the document according to the project
            - revision: last revision known
            '''
        query = "SELECT reference,last_revision,status.name FROM documents LEFT OUTER JOIN items ON items.id = documents.item_id LEFT OUTER JOIN status ON status.id = documents.status_id WHERE items.name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result == None:
            reference = "None"
            revision = "1.0"
            status = "None"
        else:
            if result[0] != None:
                reference = result[0]
            else:
                reference = "None"
            if result[1] != None:
                try:
                    revision = int(result[1])
                except ValueError:
                    revision = float(result[1]) + 0.1
            else:
                revision = 1.0
            if result[2] != None:
                status = result[2]
            else:
                status = "None"
        return reference,revision,status

    def getUsersList(self):
        query = "SELECT name FROM writers"
        result = self.sqlite_query(query)
        if result == None:
            list = "None"
        else:
            list = result
        return list
    def updateRevision(self,reference,revision):
        '''
            '''
        pass
    def getProjectInfo(self,project):
        m = re.match(r'(.*)-(.*)',project)
        if m:
            name = m.group(1)
            version = m.group(2)
        else:
            name = project
            version = "*"
        return name,version
    def up_event(self, event,listbox):
        index = listbox.index("active")
        if listbox.selection_includes(index):
            index = index - 1
        else:
            index = listbox.size() - 1
        if index < 0:
            listbox.bell()
        else:
            self.select(index,listbox)
            self.on_select(index)
        return "break"
    def down_event(self, event,listbox):
        index = listbox.index("active")
        if listbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= listbox.size():
            listbox.bell()
        else:
            self.select(index,listbox)
            self.on_select(index)
        return "break"
    def on_select(self, event):
        pass
    def select(self,index,listbox):
        listbox.focus_set()
        listbox.activate(index)
        listbox.selection_clear(0, "end")
        listbox.selection_set(index)
        listbox.see(index)
    def createCrStatus(self,cr_status="",find_status=False):
        '''
            Create Change Request status query
        '''
        condition = ""
        if cr_status != "" and cr_status != None:
            if find_status == True:
                condition = ' or (crstatus=\''+ cr_status +'\') '
            else:
                find_status = True
                condition =  ' and ((crstatus=\''+ cr_status +'\') '
        return(condition,find_status)
    def createItemType(self,item_type="",find_status=False):
        '''
            Create Synergy type query
        '''
        condition = ""
        if item_type not in ("",None):
            if find_status == True:
                condition = ' or '
            else:
                condition = '"('
                find_status = True
            condition = condition + ' (cvtype=\''+ item_type +'\') '
        return(condition,find_status)
    def _splitComma(self,input):
        '''
        Creates a string like "((CR_implemented_for='SW_ENM/01') or(CR_implemented_for='SW_PLAN/02'))"
        if keyword = CR_implemented_for and release = SW_ENM/01,SW_PLAN/02
        '''
        for list_rel in csv.reader([input]):
            pass
        text = ""
        if self._is_array(list_rel):
            for rel in list_rel:
                text +=  rel +' and '
            # Remove last comma
            text = text[0:-5]
        else:
            text= input
        return text
    def createCrImplemented(self,cr_std="",find=False,filter_cr="CR_detected_on"):
        '''
            Create Change Request status query with attribute
        '''
        condition = ""
        if cr_std not in ("",None):
            if find == True:
                condition = ' or ('+filter_cr+'=\''+ cr_std +'\') '
            else:
                find = True
                condition =  ' and (('+filter_cr+'=\''+ cr_std +'\') '
        return(condition,find)
    def makeobjectsFilter(self,object_released,object_integrate):
        '''
            Create Synergy item status query
        '''
        query = ""
        if object_integrate == 1 and object_released == 1:
            query = ' and (status=\'released\' or status=\'integrate\')'
        elif object_integrate == 0 and object_released == 1:
            query = '  and status=\'released\' '
        elif object_integrate == 1 and object_released == 0:
            query = ' and status=\'integrate\' '
        else:
            pass
        return query
    def _is_array(self,var):
        '''
            Define if a variable is an array (a list or a tuple)
        '''
        return isinstance(var, (list, tuple))
    def _getOptionArray(self,label,option):
        ##        self.sources_filter = self.getOptions(label,option)
        table = ()
        if self.config_parser.has_option(label,option):
            sources_filter = self.config_parser.get(label,option)
            if sources_filter:
                m = re.search(r',',sources_filter)
                if m:
                    ##                    print type(sources_filter)
                    for table in csv.reader([sources_filter]):
                        pass
                else:
                    table = sources_filter
            else:
                table = ()
        return(table)
    #
    # Regular expressions
    #
    def _prepareRegexp(self,filters):
        #global project_name
        index = 0
        list_items_skipped = []
        regexp=[]
        for filter_array in filters:
            ##            print type(filter_array)
            if self._is_array(filter_array):
                sub_regexp=[]
                ##                regexp[index] = '^(.*)'+ project_name + '\\\\([A-Z]*\\\\)?' + re.escape(filter) + '\\\\(.*)-(.*)@(.*)-(.*)$'
                for filter in filter_array:
                    sub_regexp.append('^(.*)'+ re.escape(filter) + '(.*)\\\\(.*)-(.*)@(.*)-(.*)$')
                    list_items_skipped.append([])
                    index += 1
                regexp.append(sub_regexp)
            else:
                regexp.append('^(.*)'+ re.escape(filter_array) + '(.*)\\\\(.*)-(.*)@(.*)-(.*)$')
                list_items_skipped.append([])
                index += 1
        return regexp,list_items_skipped
    def _filterRegexp(self,regexp,line):
        list_items_skipped = ""
        if self._is_array(regexp):
            for sub_regexp in regexp:
                match_result = re.match(sub_regexp,line)
                if match_result:
                    ##                            print m_input_data.group(3)
                    list_items_skipped = match_result.group(3)
        else:
            match_result = re.match(regexp,line)
            if match_result:
                ##                            print m_input_data.group(3)
                list_items_skipped = match_result.group(3)
            else:
                pass
        return list_items_skipped
    def _par(self,txt):
        repl = ''
        # Will make a table
        unicode_paragraph = []
##            repl = ""
        for element in txt:
            try:
                # Unicodize
                unicode_paragraph.append(element)
##                    repl = unicode(replace[1], errors='ignore')
##                    unicode_paragraph = unicode(element, errors='ignore')
##                    unicode_paragraph.append( map(lambda i: unicode(i, errors='ignore'), element) )
            except TypeError as exception:
                print "Execution failed:", exception
                unicode_paragraph.append(element)
##                    print element
            except UnicodeDecodeError as exception:
                print "Execution failed:", exception
                unicode_paragraph.append(element)
            if not len(unicode_paragraph):
                # Empty paragraph
                repl = ''
            else:
##                    print "unicode_paragraph:",unicode_paragraph
                # create 'lxml.etree._Element' objects
##                print "TEST_PAR",unicode_paragraph
                try:
                    repl = docx.paragraph(unicode_paragraph)
                except ValueError as exception:
                    print "unicode_paragraph",unicode_paragraph
                    print "TXT",txt
        return repl
    def _table(self,array,fmt):
        # Will make a table
        unicode_table = []
        for element in array:
            try:
                # Unicodize
                unicode_table.append( map(lambda i: unicode(i, errors='ignore'), element) )
            except TypeError as exception:
                print "Execution failed:", exception
                unicode_table.append(element)
##                    print element
            except UnicodeDecodeError as exception:
                print "Execution failed:", exception
                unicode_table.append(element)
        if not len(unicode_table):
            # Empty table
            repl = ''
        else:
            repl = docx.table(
                unicode_table,
                heading = fmt['heading'] if 'heading' in fmt.keys() else False,
                colw = fmt['colw'] if 'colw' in fmt.keys() else None,
                cwunit = fmt['cwunit'] if 'cwunit' in fmt.keys() else 'dxa',
                tblw = fmt['tblw'] if 'tblw' in fmt.keys() else 0,
                twunit = fmt['twunit'] if 'twunit' in fmt.keys() else 'auto',
                borders = fmt['borders'] if 'borders' in fmt.keys() else {},
                celstyle = fmt['celstyle'] if 'celstyle' in fmt.keys() else None,
##                headstyle = fmt['headstyle'] if 'headstyle' in fmt.keys() else {},
            )
        return repl
    def replaceTag(self,doc, tag, replace, fmt = {}):
        """ Searches for {{tag}} and replaces it with replace.
    Replace is a list with two indexes: 0=type, 1=The replacement
    Supported values for type:
    'str': <string> Renders a simple text string
    'par': <paragraph> Renders a paragraph with carriage return
    'tab': <table> Renders a table, use fmt to tune look
    'mix': <mixed> Render a list of table and paragraph
    'img': <image> Renders an image
    PR_002 Add paragraph type with array as an input
    """
##        try:
##            import docx
##        except ImportError:
##            print "DoCID requires the python-docx library for Python. " \
##                    "See https://github.com/mikemaccana/python-docx/"
##                        #    raise ImportError, "DoCID requires the python-docx library for Python. " \
##                        #         "See https://github.com/mikemaccana/python-docx/"
        if replace[0] == 'str':
            try:
                repl = unicode(replace[1], errors='ignore')
            except TypeError as exception:
                print "Execution failed:", exception
                repl = replace[1]
##                print repl
            except UnicodeDecodeError as exception:
                print "Execution failed:", exception
##                print replace[1]
        elif replace[0] == 'par':
            # Will make a paragraph
            repl = self._par(replace[1])
        elif replace[0] == 'tab':
            # Will make a table
            repl = self._table(replace[1],fmt)
        elif replace[0] == 'img':
            relationships = docx.relationshiplist()
            relationshiplist, repl = self.picture_add(relationships, replace[1],'This is a test description')
            return docx.advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl),relationshiplist
        elif replace[0] == 'mix':
            num_begin = ord("a")
            num_end = ord("z")
            num = num_begin
            prefix = ""
            repl = []
            dico = replace[1]
            for key,value in dico.items():
                if key[0] == "checklist":
                    par = []
                    par.append((prefix + chr(num) + ") " + dico['domain'] + " " + key[1],'rb'))
                    elt = self._par(par)
                    num += 1
                    if num > num_end:
                        prefix += "a"
                        num = num_begin
                    repl.append(elt)
                    elt = self._table(value,fmt)
                    repl.append(elt)
                    par = []
                    par.append(("Conclusion of CR review:",''))
                    elt = self._par(par)
                    repl.append(elt)
                    par = []
                    par.append(("CR Transition to state:",''))
                    elt = self._par(par)
                    repl.append(elt)
        else:
            raise NotImplementedError, "Unsupported " + replace[0] + " tag type!"
        # Replace tag with 'lxml.etree._Element' objects
        result = docx.advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl,6)
##        result = docx.advReplace_new(doc, '\{\{'+re.escape(tag)+'\}\}', repl,6)
        return result
    def picture_add(self,relationshiplist, picname, picdescription, pixelwidth=None, pixelheight=None, nochangeaspect=True, nochangearrowheads=True):
        '''Take a relationshiplist, picture file name, and return a paragraph containing the image
        and an updated relationshiplist'''
        # http://openxmldeveloper.org/articles/462.aspx
        # Create an image. Size may be specified, otherwise it will based on the
        # pixel size of image. Return a paragraph containing the picture'''
        # Copy the file into the media dir
    ##    media_dir = join(template_dir, 'word', 'media')
    ##    if not os.path.isdir(media_dir):
    ##        os.mkdir(media_dir)
    ##    shutil.copyfile(picname, join(media_dir, picname))
        # Check if the user has specified a size
        if not pixelwidth or not pixelheight:
            # If not, get info from the picture itself
            pixelwidth, pixelheight = Image.open(picname).size[0:2]
        # OpenXML measures on-screen objects in English Metric Units
        # 1cm = 36000 EMUs
        emuperpixel = 12667
        width = str(pixelwidth * emuperpixel)
        height = str(pixelheight * emuperpixel)
        # Set relationship ID to the first available
        picid = '2'
        picrelid = 'rId'+str(len(relationshiplist)+1)
        relationshiplist.append([
            'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
            'media/'+picname])
        # There are 3 main elements inside a picture
        # 1. The Blipfill - specifies how the image fills the picture area (stretch, tile, etc.)
        blipfill = docx.makeelement('blipFill', nsprefix='pic')
        blipfill.append(docx.makeelement('blip', nsprefix='a', attrnsprefix='r',
                        attributes={'embed': picrelid}))
        stretch = docx.makeelement('stretch', nsprefix='a')
        stretch.append(docx.makeelement('fillRect', nsprefix='a'))
        blipfill.append(docx.makeelement('srcRect', nsprefix='a'))
        blipfill.append(stretch)
        # 2. The non visual picture properties
        nvpicpr = docx.makeelement('nvPicPr', nsprefix='pic')
        cnvpr = docx.makeelement('cNvPr', nsprefix='pic',
                            attributes={'id': '0', 'name': 'Picture 1', 'descr': picname})
        nvpicpr.append(cnvpr)
        cnvpicpr = docx.makeelement('cNvPicPr', nsprefix='pic')
        cnvpicpr.append(docx.makeelement('picLocks', nsprefix='a',
                        attributes={'noChangeAspect': str(int(nochangeaspect)),
                                    'noChangeArrowheads': str(int(nochangearrowheads))}))
        nvpicpr.append(cnvpicpr)
        # 3. The Shape properties
        sppr = docx.makeelement('spPr', nsprefix='pic', attributes={'bwMode': 'auto'})
        xfrm = docx.makeelement('xfrm', nsprefix='a')
        xfrm.append(docx.makeelement('off', nsprefix='a', attributes={'x': '0', 'y': '0'}))
        xfrm.append(docx.makeelement('ext', nsprefix='a', attributes={'cx': width, 'cy': height}))
        prstgeom = docx.makeelement('prstGeom', nsprefix='a', attributes={'prst': 'rect'})
        prstgeom.append(docx.makeelement('avLst', nsprefix='a'))
        sppr.append(xfrm)
        sppr.append(prstgeom)
        # Add our 3 parts to the picture element
        pic = docx.makeelement('pic', nsprefix='pic')
        pic.append(nvpicpr)
        pic.append(blipfill)
        pic.append(sppr)
        # Now make the supporting elements
        # The following sequence is just: make element, then add its children
        graphicdata = docx.makeelement('graphicData', nsprefix='a',
                                    attributes={'uri': 'http://schemas.openxmlforma'
                                                     'ts.org/drawingml/2006/picture'})
        graphicdata.append(pic)
        graphic = docx.makeelement('graphic', nsprefix='a')
        graphic.append(graphicdata)
        framelocks = docx.makeelement('graphicFrameLocks', nsprefix='a',
                                 attributes={'noChangeAspect': '1'})
        framepr = docx.makeelement('cNvGraphicFramePr', nsprefix='wp')
        framepr.append(framelocks)
        docpr = docx.makeelement('docPr', nsprefix='wp',
                            attributes={'id': picid, 'name': 'Picture 1',
                                        'descr': picdescription})
        effectextent = docx.makeelement('effectExtent', nsprefix='wp',
                                     attributes={'l': '25400', 't': '0', 'r': '0',
                                                 'b': '0'})
        extent = docx.makeelement('extent', nsprefix='wp',
                             attributes={'cx': width, 'cy': height})
        inline = docx.makeelement('inline', attributes={'distT': "0", 'distB': "0",
                                                     'distL': "0", 'distR': "0"},
                             nsprefix='wp')
        inline.append(extent)
        inline.append(effectextent)
        inline.append(docpr)
        inline.append(framepr)
        inline.append(graphic)
        drawing = docx.makeelement('drawing')
        drawing.append(inline)
        run = docx.makeelement('r')
        run.append(drawing)
        paragraph = docx.makeelement('p')
        paragraph.append(run)
        return relationshiplist, paragraph
    def _compareReleaseName(self,releases=[]):
        sub_regexp = '^(.*)/([0-9]*)$'
        name = []
        if len(releases) > 2:
            raise Exception("This function accept array of 2 elements only!")
            return False
        for release in releases:
            match_result = re.match(sub_regexp,release)
            if match_result:
                name.append(match_result.group(1))
        if name[0] == name[1]:
            return True
        else:
            return False
    def removeNonAscii(self,s): return "".join(filter(lambda x: ord(x)<128, s))

    def replaceBeacon(self,text):
        char = {r'\x02':r'<',r'\x03':r'>'}
        for before, after in char.iteritems():
            text = re.sub(before,after,text)
        return text

    def _parseCRParent(self,text_html):
        # instantiate the parser and fed it some HTML
        parser = MyHTMLParserPlain()
        parser.tbl = []
        parser.feed(text_html)
        return parser.tbl
    def _filterASCII(self,transi_log):
        print "transi_log",transi_log
        # Remove ASCII control characters
        # Replace FS and RS characters
##        char = {r'\x1e':'',r'\x1c':'',r'\x0d':'<br/>'}
        char = {r'\x1e(.*)\x0d':'<span style="color:\'red\'">\1</span><br/>',r'\x1c(.*)\x0d':'<span style="color:\'green\'">\1</span><br/>'}
        for before, after in char.iteritems():
            transi_log = re.sub(before,after,transi_log)
        if transi_log != None:
            transi_log_filtered = self.removeNonAscii(transi_log)
            #transi_log_filter.decode('latin1') #filter(string.printable[:-5].__contains__,transi_log_filter)
        else:
            transi_log_filtered = transi_log
        return transi_log_filtered
    def _parseCR(self,text_html,transition_log,parent_cr,output_filename):
        # instantiate the parser and fed it some HTML
        parser = MyHTMLParser()
        parser.text = ""
        parser.tbl = []
        parser.dico = {}
        parser.foundCell = False
 #       xml_buffer = ""
##        numero = 1
##        for line in text_html:
##            print numero
##            numero += 1
##        print "HTML",text_html
 #       xml_buffer += line
        parser.feed(text_html)
##        print "RESULT",parser.dico
##        transition_log = ""
        replacements = {r'\${CR_ID}':parser.dico['problem_number'],
                        r'\${CR_STATUS}':parser.dico['crstatus'],
                        r'\${CR_SYNOPSIS}':parser.dico['problem_synopsis'],
                        r'\${CR_APPLICABLE_SINCE}':parser.dico['CR_applicable_since'],
                        r'\${CR_IMPLEMENTED_FOR}':parser.dico['CR_implemented_for'],
                        r'\${SCR_IN_ANALYSIS_ID}':parser.dico['SCR_In_Analysis_id'],
                        r'\${CREATE_TIME}':parser.dico['create_time'],
                        r'\${CR_ECE_CLASSIFICATION}':parser.dico['CR_ECE_classification'],
                        r'\${CR_CUSTOMER_CLASSIFICATION}':parser.dico['CR_customer_classification'],
                        r'\${CR_REQUEST_TYPE}':parser.dico['CR_request_type'],
                        r'\${CR_DETECTED_ON}':parser.dico['CR_detected_on'],
                        r'\${CR_EXPECTED}':parser.dico['CR_expected'],
                        r'\${CR_OBSERVED}':parser.dico['CR_observed'],
                        r'\${CR_FUNCTIONAL_IMPACT}':parser.dico['CR_functional_impact'],
                        r'\${CR_ORIGIN}':parser.dico['CR_origin'],
                        r'\${CR_ORIGIN_DESC}':parser.dico['CR_origin_desc'],
                        r'\${CR_ANALYSIS}':parser.dico['CR_analysis'],
                        r'\${CR_CORRECTION_DESCRIPTION}':parser.dico['CR_correction_description'],
                        r'\${CR_PRODUCT_IMPACT}':parser.dico['CR_product_impact'],
                        r'\${CR_DOC_IMPACT}':parser.dico['CR_doc_impact'],
                        r'\${CR_VERIF_IMPACT}':parser.dico['CR_verif_impact'],
                        r'\${IMPACT_ANALYSIS}':parser.dico['impact_analysis'],
                        r'\${FUNCTIONAL_LIMITATION_DESC}':parser.dico['functional_limitation_desc'],
                        r'\${IMPLEMENTED_MODIFICATION}':parser.dico['implemented_modification'],
                        r'\${CR_IMPLEMENTATION_BASELINE}':parser.dico['CR_implementation_baseline'],
                        r'\${CR_VERIFICATION_ACTIVITIES}':parser.dico['CR_verification_activities'],
                        r'\${FUNCTIONAL_LIMITATION}':parser.dico['functional_limitation'],
                        r'\${CR_PARENT}':parent_cr,
                        r'\${SCR_CLOSED_ID}':parser.dico['SCR_Closed_id'],
                        r'\${SCR_CLOSED_TIME}':parser.dico['SCR_Closed_time'],
                        r'\${TRANSITION_LOG}':transition_log,
                        r'\${MODIFY_TIME}':parser.dico['modify_time'],
                        r'\${VISUAL_STATUS}':parser.dico['crstatus'],
                        r'\${CR_DOMAIN}':parser.dico['CR_domain'],
                        r'\${CR_TYPE}':parser.dico['CR_type']}
        fin = open('template/cr_template.html')
        input = fin.read()
        out = open(output_filename, 'w')
        for before, after in replacements.iteritems():
            filtered_after = self.removeNonAscii(after)
            try:
                filtered_after = filtered_after.encode("utf-8")
                input = re.sub(before,filtered_after,input)
            except UnicodeDecodeError,exception:
                # Vieux patch
                print exception," ",before," ",filtered_after
                # Remove span
                char = {r'<span style =  ?".*" >':'','<br>':''}
                for before_char, after_char in char.iteritems():
                    filtered_after = re.sub(before_char,after_char,filtered_after)
                print "PATCH",filtered_after
                filtered_after = filtered_after.encode("utf-8")
                input = re.sub(before,filtered_after,input)
##                print "TEST",filtered_after
##                parser = MyHTMLParserPlain()
##                parser.tbl = []
##                parser.feed(filtered_after)
##                input = re.sub(before,parser.tbl[0],input)
        out.write(input)
        out.close

    def _getTemplate(self,template_type):
        # Get config
        self.config_parser = ConfigParser()
        self.config_parser.read('docid.ini')
        try:
            # get template name
            template_dir = join(os.path.dirname("."), 'template')
            template_name = self.getOptions("Template",template_type)
            template = join(template_dir, template_name)
        except IOError as exception:
            print "Execution failed:", exception
        #except NoOptionError as exception:
        #    print "Execution failed:", exception
        return template

    def _createDico2Word(self,list_tags,template_name,filename,image_name=None):
        # Load the original template
        template_found = False
        try:
            template = zipfile.ZipFile(template_name,mode='r')
            template_found = True
        except IOError as exception:
            print "Execution failed:", exception
            docx_filename = False
            try:
                self.template_default_name = "review_template.docx"
                template = zipfile.ZipFile(self.template_default_name,mode='r')
                template_found = True
                print "TAKE DEFAULT TEMPLATE"
            except IOError as exception:
                print "Execution failed:", exception
                docx_filename = False
        if template.testzip() or not template_found:
            raise Exception('File is corrupted!')
            docx_filename = False
        else:
            # List of section to modify
            # (<section>, <namespace>)
            actlist = []
            actlist.append(('word/document.xml', '/w:document/w:body'))
            list = template.namelist()
            for entry in list:
                m = re.match(r'^word/header.*',entry)
                if m:
                    actlist.append((entry, '/w:hdr'))
                m = re.match(r'^word/footer.*',entry)
                if m:
                    actlist.append((entry, '/w:ftr'))
            # Will store modified sections here
            outdoc = {}
            try:
                for curact in actlist:
                    xmlcontent = template.read(curact[0])
                    outdoc[curact[0]] = etree.fromstring(xmlcontent)
                    # Will work on body
                    docbody = outdoc[curact[0]].xpath(curact[1], namespaces=docx.nsprefixes)[0]
                    # Loop to replace tags
                    for key, value in list_tags.items():
                        if curact[0] == "word/document.xml":
                            print "TEST:" + key,value
                        if value['text'] != None:
                            text = value['text']
                        else:
                            text = "None"
                        docbody = self.replaceTag(docbody, key, (value['type'], text), value['fmt'])
                    # Cleaning
                    docbody = docx.clean(docbody)
            except KeyError as exception:
                print >>sys.stderr, "Execution failed:", exception
            # ------------------------------
            # Save output
            # ------------------------------
            # Prepare output file
            docx_filename = filename
            try:
                outfile = zipfile.ZipFile(self.gen_dir + docx_filename,mode='w',compression=zipfile.ZIP_DEFLATED)
                # Replace image if image exists in SQLite database
                if image_name != None:
                    actlist.append(('word/media/image1.png', ''))
                    img = open('img/' + image_name,'rb')
                    data = img.read()
                    outfile.writestr('word/media/image1.png',data)
                    img.close()
                # Copy unmodified sections
                for file in template.namelist():
                    if not file in map(lambda i: i[0], actlist):
                        fo = template.open(file,'rU')
                        data = fo.read()
                        outfile.writestr(file,data)
                        fo.close()
                # The copy of modified sections
                for sec in outdoc.keys():
                    treestring = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "\n"
                    treestring += etree.tostring(outdoc[sec], pretty_print=True)
                    outfile.writestr(sec,treestring)
                # Done. close files.
                outfile.close()
                exception = ""
            except IOError as exception:
                print >>sys.stderr, "Execution failed:", exception
                docx_filename = False
        return docx_filename,exception
    #
    # Gestion des docs
    #

    def _clearDicofound(self):
        self.dico_found = {}

    def _getDicoFound(self,key,type_doc):
        if (key,type_doc) in self.dico_found:
            doc = self.dico_found[(key,type_doc)]
        else:
            doc = False
        return(doc)

    def _getReference(self,filename):
        '''
        Get reference like ET1234-S in the document name
        '''
        m = re.match(r"(.*)(ET[0-9]{4}_[ESV])",filename)
        if m:
            reference = re.sub(r"(.*)_(.*)",r"\1-\2",m.group(2))
        else:
            m = re.match(r"(.*)(ET[0-9]{4})",filename)
            if m:
                reference = m.group(2)
            else:
                m = re.match(r"(.*)(PQ ?[0-9\.])",filename)
                if m:
                    reference = m.group(2)
                else:
                    reference = ""
        return reference

    def _getDescriptionDoc(self,filename):
        '''
        return description of a document if name or keyword is found in database
        '''
        # remove suffix, extension
        description = ""
        reference = ""
        doc_name = re.sub(r"(.*)\.(.*)",r"\1",filename)
        # Look into the user list first
        if doc_name in self.dico_descr_docs:
            description = self.dico_descr_docs[doc_name]
            reference = self.dico_descr_docs_ref[doc_name]
        else:
            # Look into the default list then
            find = False
            # Peer review type ?
            if re.match("^PRR_(.*)",doc_name):
                description = self.dico_descr_docs_default["PRR"]
                find = True
            else:
                for key in self.dico_descr_docs_default:
                    if key in doc_name:
                        description = self.dico_descr_docs_default[key]
                        # find keyword in doc name
                        find = True
            if not find:
                pass
            reference = self._getReference(doc_name)
        return description,reference

    def _getDoc(self,m,dico,filter_type_doc=('doc','pdf','xls','ascii')):
        '''
            Add a document in dictionary if
            - the name of the document match the name in document dictionary
            - the type of the document is doc or pdf
        '''
        result = False
        description = ""
        release_item = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type_doc = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        if type_doc in filter_type_doc:
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description,reference = self._getDescriptionDoc(document)
                    description = dico[key]
                    self.dico_found[key,type_doc] = doc_name + " issue " + version
                    print "DICO_FOUND",self.dico_found
                    result = True
                    break
        return result

    sqlite_query = staticmethod(sqlite_query)
    sqlite_query_one = staticmethod(sqlite_query_one)

from HTMLParser import HTMLParser
# create a subclass and override the handler methods
class MyHTMLParserPlain(HTMLParser):
    def handle_starttag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        self.tbl.append(data)
class MyHTMLParser(HTMLParser):
    def _createBeacon(self,tag,attrs):
        text = "<" + tag
        for key,value in attrs:
            if key != None and value != None:
                attr_inline = ' ' + key + ' =  "'+value+'" '
                text += attr_inline
        text += ">"
        return (text)
    def handle_starttag(self, tag, attrs):
##            print "Encountered a start tag:", tag
        if tag == "cell":
            self.foundCell = True
            for attr in attrs:
                self.attr = attr[1]
        elif self.foundCell:
            try:
                self.text += self._createBeacon(tag,attrs)
            except UnicodeDecodeError,exception:
                pass
            #self.text += "<" + tag + ">"
    def handle_endtag(self, tag):
##            print "Encountered an end tag :", tag
        if tag == "cell":
            self.foundCell = False
            self.tbl.append(self.text)
            if self.attr != None:
                self.dico[self.attr] = self.text
            self.text= ""
    def handle_data(self, data):
##            print "Encountered some data  :", data
        if self.foundCell:
            self.text += data

if __name__ == "__main__":
    # Put test procedures to the Tool class here
    # Test 1: Regular expressions
    tool = Tool()
    for filters in [["BUILD"],["INPUT_DATA","REVIEW","VTPR"]]:
        regexp, list_items_skipped = tool._prepareRegexp(filters)
        print regexp
        print list_items_skipped
    # Test 2
    result = tool._compareReleaseName(["PLD_TIE/01","PLD_TIE/02"])
    print "_compareReleaseName PLD_TIE/01 vs PLD_TIE/02",result
    result = tool._compareReleaseName(["PLD_TIE/01","BOARD_ESSNESS/01"])
    print "_compareReleaseName PLD_TIE/01 vs BOARD_ESSNESS/01",result
    try:
        result = tool._compareReleaseName(["PLD_TIE/01","BOARD_ESSNESS/01","TEST"])
    except Exception as exception:
        print "Execution failed:", exception
    cmd_out = ['CR 418: Modification of "TRU overload in progress" curve definition']
    cr_id = []
    for line_cr in cmd_out:
        m = re.match(r'^CR ([0-9]*):(.*)$',line_cr)
        # Get CR ID
        if m:
            print m
            cr_id.append(m.group(1))
            print cr_id
            break
    # Test 3
    result = tool.get_sys_item_old_workflow("Bombardier CSeries EPC","CPDD")
    print "OLD WORKFLOW",result
    result = tool.get_sys_item_old_workflow("Dassault F5X PDS","ESSNESS")
    print "NEW WORKFLOW",result
    # Test 4
    output = tool._splitComma("SW_ENM/01,SW_PLAN/01")
    print "T41",output
    output = tool._splitComma("SW_ENM/02,SW_PLAN/02")
    print "T42",output
    # Test 5
    result = tool._getCRChecklist("In_Review")
    print "checklist",result
    result = tool._getCRChecklist("Postponed")
    print "checklist",result
    result = tool._getCRChecklist("Fixed")
    print "checklist",result
    result = tool._getCRChecklist("In_Analysis")
    print "checklist",result
    result = tool._getItemCRType("ESSNESS","Dassault F5X PDS")
    print "_getItemCRType",result
    char = {r'\x02':r'<',r'\x03':r'>'}
    for before, after in char.iteritems():
##    for before,after in char:
        print before," ",after
##    fichier = open("result/log_SCR_419_1400837741.html", "r")
##    text_html = fichier.readlines()
##    tool._parseCR(text_html,'result/test.html')
    test = (u'SDSIO', u'PLD')
    print test[0]
    test = '<span \xe9 style =  "font-size:10.0pt;mso-bidi-font-size:12.0pt;  font-family:"Arial","sans-serif";mso-fareast-font-family:"Times New Roman";  mso-bidi-font-family:"Times New Roman";mso-ansi-language:FR;mso-fareast-language:  FR;mso-bidi-language:AR-SA" >In requirement SDTS_PDS_7073 (new version)<br>CABC1_SHED and CABC2_SHED have to be validated during 100ms<br>'
    text = re.sub(r"{TEST}",test,"TITI{TEST}TOTO")
    print text
    line = "SSCS ESSNESS<br />ICD CAN data<br />ICD SPI data<br />ATP carte ESSNESS<br />software FUNC<br />software BITE<br />"
    line = re.sub(r"<br ?\/>",r"\n",line)
    print line
    psac_doc = ['None', 'PSAC_SW_PLAN_PDS_SDS_ET3131 issue 2.0', 'PSAC_SW_PLAN_PDS_SDS_ET3131 issue 2.0', 'PSAC_SW_PLAN_PDS_SDS_ET3131 issue 2.0', 'PSAC_SW_PLAN_PDS_SDS_ET3131 issue 2.0', 'PSAC_SW_PLAN_WDS_ET3162 issue 2.0']
    psac_doc_filtered = sorted(set(psac_doc))
    print psac_doc_filtered
    cr = "93) SQA: Clarification for SQA audits scheduling and modus operandi (SQA Action item ID 1435)"
    m = re.match(r'^([0-9]*\)) (.*)$',cr)
    if m:
        print "HELLO"
##    import wckCalendar
##
##    root = Tk()
##
##    def echo():
##        print calendar.getselection()
##
##    calendar = wckCalendar.Calendar(root, command=echo)
##    calendar.pack()
##
##    mainloop()
    TBL_IN = {'text': [
    ['Ref', 'Name', 'Reference', 'Version', 'Description'],
     ['[R2]', 'SSCS_ESSNESS_ET2788_S', 'ET2788-S', '6', 'Board Specification Document'],
     ['[R3]', 'SMS_EPDS_ESSNESS_SPI_Annex_ET3547_S', 'ET3547-S', '2', 'SPI Interface Document'],
     ['[R4]', 'SMS_EPDS_SPI_ICD_ET3532_S', 'ET3532-S', '3', 'Interface Control Document'],
     ['[R5]', 'CCB_Minutes_SW_ENM_001', '', '1.0', 'CCB minutes'],
     ['[R6]', 'CCB_Minutes_SW_ENM_002', '', '1.0', 'CCB minutes'],
     ['[R7]', 'CCB_Minutes_SW_ENM_003', '', '1.0', 'CCB minutes'],
     ['[R8]', 'CCB_Minutes_SW_ENM_004', '', '1.0', 'CCB minutes'],
     ['[R9]', 'CCB_Minutes_SW_ENM_005', '', '1.0', 'CCB minutes'],
     ['[R10]', 'CCB_Minutes_SW_ENM_006', '', '3.0', 'CCB minutes'],
     ['[R11]', 'CCB_Minutes_SW_ENM_007', '', '3.0', 'CCB minutes'],
     ['[R12]', 'CCB_Minutes_SW_ENM_008', '', '3.0', 'CCB minutes'],
     ['[R14]', 'CCB_Minutes_SW_ENM_009', '', '3.0', 'CCB minutes'],
     ['[R17]', 'SCMP_SW_PLAN_ET3134', 'ET3134', '1.8', 'Software Configuration Management Plan'],
     ['[R18]', 'CCB_Minutes_SW_PLAN_001', '', '1.0', 'CCB minutes'],
     ['[R19]', 'SRTS_SW_STANDARD_ET3157', 'ET3157', '1.5', 'Software Requirement Test Standard'],
     ['[R20]', 'SDP_SW_PLAN_ET3132', 'ET3132', '1.9', 'Software Development Plan'],
     ['[R21]', 'SVP_SW_PLAN_ET3133', 'ET3133', '1.10', 'Software Verification Plan'],
     ['[R22]', 'CCB_Minutes_SW_PLAN_002', '', '1.0', 'CCB minutes'],
     ['[R23]', 'CCB_Minutes_SW_PLAN_PDS_SDS_001', '', '1.0', 'CCB minutes'],
     ['[R24]', 'CCB_Minutes_SW_PLAN_PDS_SDS_002', '', '1.0', 'CCB minutes']], 'fmt': {'colw': [500, 1000, 500, 500, 2500], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'tab'}
    TBL_OUT  = {'text': [
    ['Ref', 'Name', 'Reference', 'Version', 'Description'],
    ['[R15]', 'SHLDR_ENM_ET3196_S', 'ET3196-S', '3.0', 'Software High-Level Derived Requirement document'],
    ['[R16]', 'SWRD_ENM_ET3135_S', 'ET3135-S', '3.2', 'Software Requirements Document']], 'fmt': {'colw': [500, 1000, 500, 500, 2500], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'tab'}