#!/usr/bin/env python 2.7.3

#
# Generate Configuration Index Document from Synergy data repository
# Use TK library ofr the GUI
#

import sys
##import protocol
import os
sys.path.append("python-docx")

import subprocess
import sqlite3 as lite
#import csv
from Tkinter import *
##from Tix import *
import tkMessageBox
import docx
import threading
import time
from ConfigParser import ConfigParser
import re
import zipfile
from lxml import etree
import Queue
import datetime


def startSession(item,database,login,password):
    global session_started

    tool = Tool()
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Open Synergy session.\n")
##    stdout = tool.ccm_query(' status ',"Synergy session started")
##    print stdout
##    m = re.search(r'Database:(.*)',stdout)
##    if m:
##        print m.group
    query = 'start /nogui /q /d /usr/local/ccmdb/' + database + ' /u /usr/local/ccmdb/' + database + ' /s ' + tool.ccm_server + ' /n ' + login + ' /pw ' + password
    stdout,stderr = tool.ccm_query(query,"Synergy session started")
    print time.strftime("%H:%M:%S", time.gmtime()) + " " + stdout
    session_started = True

    data = tool.retrieveLastSelection(item)
    if data != []:
        if data[0][1] != None:
            interface.reference_entry.insert(0, data[0][1])
        if data[0][2] != None:
            interface.revision_entry.insert(0, data[0][2])
        interface.projectlistbox.insert(END, data[0][4])
        interface.releaselistbox.insert(END, data[0][6])
        interface.baselinelistbox.insert(END, data[0][7])

    interface.button_select.configure(state=NORMAL)
    interface.button_find_baselines.configure(state=NORMAL)
    interface.button_find_releases.configure(state=NORMAL)
    interface.button_find_projects.configure(state=NORMAL)
    m = re.match(r'^(.*):(.*):([0-9.])',stdout)
    if m:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Computer   => " + m.group(1) + "\n")
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Session ID => " + m.group(2) + "\n")
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " IP address => " + m.group(3) + "\n")
    else:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " " + stdout + stderr)
##    self.stop()
    return stdout

def getReleasesList():
    global session_started

    tool = Tool()
    interface.releaselistbox.delete(0, END)
    interface.releaselistbox.insert(END, "All")
    if session_started:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Get releases available ...\n")
#        stdout = tool.ccm_query("release -active -l","Get releases")
        stdout,stderr = tool.ccm_query("release -l","Get releases")
    else:
        stdout = ""
        print "No session started yet."
    if stdout != "":
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Releases found.\n")
        output = stdout.splitlines()
        for line in output:
            line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
            interface.releaselistbox.insert(END, line)
    else:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " No releases found.\n")

def getBaselinesList(release):
    global session_started

    tool = Tool()
    interface.baselinelistbox.delete(0, END)
    interface.baselinelistbox.insert(END, "All")
    if session_started:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Get baselines available ...\n")
        if release != "" and release != "All":
            query = 'baseline -l -release ' + release + ' -f "%name"'
        else:
            query = 'baseline -l -f "%name"'
        stdout,stderr = tool.ccm_query(query,"Get baselines")
    else:
        stdout = ""
        print "No session started yet."
    if stdout != "":
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Baseline found.\n")
        output = stdout.splitlines()
        for line in output:
            line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
            interface.baselinelistbox.insert(END, line)
    else:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " No baselines found.\n")

def getProjectsList(release,baseline_selected):
    global session_started
    global list_projects
    tool = Tool()
    interface.projectlistbox.delete(0, END)
    interface.projectlistbox.insert(END, "All")
    if session_started:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Get projects available ...\n")
        if release != "" and release != "All":
            query = 'query -release '+ release +' "(cvtype=\'project\')" -f "%name-%version;%in_baseline"'
        else:
            query = 'query "(cvtype=\'project\')" -f "%name-%version"'
        stdout,stderr = tool.ccm_query(query,"Get projects")
    else:
        stdout = ""
        print "No session started yet."
    if stdout != "":
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Projects found.\n")
        output = stdout.splitlines()
        list_projects = []
        #print baseline_selected
        if baseline_selected != "*" and baseline_selected != "All" and baseline_selected != "":
            for line in output:
                line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                m = re.match(r'(.*)-(.*);(.*)$',line)
                if m:
                    project = m.group(1) + "-" + m.group(2)
                    baseline_string = m.group(3)
                    baseline_splitted = baseline_string.split(',')
                    for baseline in baseline_splitted:
                        baseline = re.sub(r".*#",r"",baseline)
                        if baseline == baseline_selected:
                            list_projects.append(project)
                            interface.projectlistbox.insert(END, project)
                            break
##                   baseline_splitted = re.sub(r".*#",r"",baseline_splitted)

        else:
            for line in output:
                line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                m = re.match(r'(.*)-(.*);(.*)$',line)
                if m:
                    project = m.group(1) + "-" + m.group(2)
                    print "name " + m.group(1) + " version " + m.group(2)
                else:
                    project = line
                list_projects.append(project)
                interface.projectlistbox.insert(END, project)
    else:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " No projects found.\n")

def generateDoc(author,reference,release,aircraft,item,project,baseline,object_released,object_integrate):
    getProjectsList(release,baseline)
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Begin document generation ...\n")
    cid = BuildDoc(author,reference,release,aircraft,item,project,baseline)
    # Documentations
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Items query in progress...\n")
    tableau_items =cid.getArticles(object_released,object_integrate,("doc","xls"))
    # Source
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Source code query in progress...\n")
    tableau_sources = cid.getArticles(object_released,object_integrate,("csrc","asmsrc"))
    # Problem Reports
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " PR query in progress...\n")
    cid.getPR()
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Creation doc in progress...\n")
    # Create docx
    docx_filename,exception = cid.createDoc(tableau_items,tableau_sources)
    if docx_filename == False:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " " + exception.strerror + ", document not saved.\n")
    else:
        interface.output_txt.tag_configure("hlink", foreground='blue', underline=1)
        interface.output_txt.tag_bind("hlink", "<Button-1>", cid.openHLink)
        interface.output_txt.tag_bind("hlink", "<Enter>", cid.onLink)
        interface.output_txt.tag_bind("hlink", "<Leave>", cid.outsideLink)
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) +  " Word document created.\n")
        interface.output_txt.insert(END, "Available here:\n")
        interface.output_txt.insert(END, docx_filename, "hlink")
        interface.output_txt.insert(END, "\n")
##def populate_listbox(query,listbox,first):
##    # populate systems listbox
##    listbox.delete(0, END)
##    listbox.insert(END, first)
##    result = sqlite_query(query)
##    for item in result:
##        listbox.insert(item[0], item[1])
class Tool():
    def __init__(self):
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        self.ccm_server = config_parser.get("Synergy","synergy_server")
        conf_synergy_dir = config_parser.get("Synergy","synergy_dir")
        self.ccm_exe = os.path.join(conf_synergy_dir, 'ccm')

    def onLink(self,event):
        print "La souris est sur le le lien"
        fenetre.config(cursor='arrow')
        fenetre.update()

    def outsideLink(self,event):
        print "La souris n'est plus sur le le lien"
        fenetre.config(cursor='')
        fenetre.update()

    def populate_listbox(self,query,listbox,first):
        # populate systems listbox
        listbox.delete(0, END)
        listbox.insert(END, first)
        result = self.sqlite_query(query)
        for item in result:
            listbox.insert(END, item[0])

    def get_database(self,index):
        query = "SELECT items.database,aircraft FROM items LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + index + "'"
        result = self.sqlite_query(query)
        return result

    def get_ci_identification(self,index):
        query = "SELECT ci_identification FROM items WHERE items.name LIKE '" + index + "'"
        result = self.sqlite_query(query)
        return result[0][0]

    def get_lastquery(self):
        query = 'SELECT database,item,project,release FROM last_query WHERE id = 1'
        item = self.sqlite_query(query)
        item = cur.fetchall()
        return item

    # SQLite
    def sqlite_query(self,query):
        try:
            con = lite.connect('synergy.db')
            cur = con.cursor()
            cur.execute(query)
            print time.strftime("%H:%M:%S", time.gmtime()) + " " + query
            result = cur.fetchall()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
        return result

    def sqlite_query_one(self,query):
        try:
            con = lite.connect('synergy.db')
            cur = con.cursor()
            cur.execute(query)
            print time.strftime("%H:%M:%S", time.gmtime()) + " " + query
            result = cur.fetchone()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
        return result

    # Synergy
    def ccm_query(self,query,cmd_name):
        print time.strftime("%H:%M:%S", time.gmtime()) + " ccm " + query
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        verrou.acquire()
        proc = subprocess.Popen(self.ccm_exe + " " + query, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
        verrou.release()
        stdout, stderr = proc.communicate()
    ##    print time.strftime("%H:%M:%S", time.gmtime()) + " " + stdout
        if stderr:
            print "Error while executing " + cmd_name + " command: " + stderr
        time.sleep(1)
        return_code = proc.wait()
    #    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " " + cmd_name + ".\n")
        return stdout,stderr

    def retrieveLastSelection(self,item):
        data = []
        try:
##            query = "SELECT * FROM last_query WHERE item LIKE '" + item + "' LIMIT 1"
##            print query
            data = self.sqlite_query("SELECT * FROM last_query WHERE item LIKE '" + item + "' LIMIT 1")
        except:
            pass
        return data

    def getItemDescription(self,item):
        query = "SELECT description FROM items WHERE name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result == None:
            description = None
        else:
            description = result[0]
        return description

# -----------------------------------------------------------------------------
class BuildDoc(Tool):
    def __init__(self,author,reference,release,aircraft,item,project,baseline):
        Tool.__init__(self)
        self.author = author
        self.reference = reference
        self.release = release
        self.aircraft = aircraft
        self.item = item
        self.project = project
        self.baseline = baseline
##        self.tableau_items = []
##        self.tableau_source = []
        self.tableau_pr = []

        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        try:
            self.template_name = config_parser.get("Template","name")
            self.template_type = config_parser.get("Template","type")
            self.type_doc = config_parser.get("Objects","type_doc").split(",")
            self.type_src = config_parser.get("Objects","type_src").split(",")
        except NoSectionError as exception:
            print "Execution failed:", exception

    def replaceTag(self,doc, tag, replace, fmt = {}):
        """ Searches for {{tag}} and replaces it with replace.

    Replace is a list with two indexes: 0=type, 1=The replacement
    Supported values for type:
    'str': <string> Renders a simple text string
    'tab': <list> Renders a table, use fmt to tune look
    """

        if replace[0] == 'str':
            try:
                repl = unicode(replace[1], errors='ignore')
            except TypeError as exception:
                print "Execution failed:", exception
                repl = replace[1]
                print repl
            except UnicodeDecodeError as exception:
                print "Execution failed:", exception
                print replace[1]
        elif replace[0] == 'tab':
            # Will make a table

            unicode_table = []
            for element in replace[1]:
                try:
                    # Unicodize
                    unicode_table.append( map(lambda i: unicode(i, errors='ignore'), element) )
                except TypeError as exception:
                    print "Execution failed:", exception
                    repl = replace[1]
                    print element
                except UnicodeDecodeError as exception:
                    print "Execution failed:", exception
                    print element
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
        else:
            raise NotImplementedError, "Unsupported " + replace[0] + " tag type!"

        return docx.advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl)

    def openHLink(self,event):
        start, end = interface.output_txt.tag_prevrange("hlink",
        interface.output_txt.index("@%s,%s" % (event.x, event.y)))
        print "Going to %s..." % interface.output_txt.get(start, end)
        os.startfile(self.docx_filename, 'open')
        #webbrowser.open

    def makeobjectsFilter(self,object_released,object_integrate,type_object = ["doc","xls"]):
        if object_integrate == 1 and object_released == 1:
            query = '((cvtype=\''+type_object[0]+'\') or (cvtype=\''+type_object[1]+'\')) and (status=\'released\' or status=\'integrate\')'
        elif object_integrate == 0 and object_released == 1:
            query = '((cvtype=\''+type_object[0]+'\') or (cvtype=\''+type_object[1]+'\')) and status=\'released\' '
        elif object_integrate == 1 and object_released == 0:
            query = '((cvtype=\''+type_object[0]+'\') or (cvtype=\''+type_object[1]+'\')) and status=\'integrate\' '
        else:
            query = '((cvtype=\''+type_object[0]+'\') or (cvtype=\''+type_object[1]+'\'))'
        return query

    def getProjectInfo(self,project):
        m = re.match(r'(.*)-(.*)',project)
        if m:
            name = m.group(1)
            version = m.group(2)
        else:
            name = self.project
            version = "*"
        return name,version

    def getArticles(self,object_released,object_integrate,type_object):
        global session_started

        tableau = []
        # Header
        tableau.append(["Project","Data","Revision","Modified time","Status"])
        if session_started:
            query = 'query -sby project -n *.* -u '
            if self.release != "":
                query = query + '-release ' + self.release + " "
            query = query + '"' + self.makeobjectsFilter(object_released,object_integrate,type_object)
            if (self.project != "*") and (self.project != "All"):
                name, version = self.getProjectInfo(self.project)
                #% option possible: ccm query "recursive_is_member_of('projname-version','none')"
##                query = 'query -sby name -n *.* -u -release ' + self.release + ' "((cvtype=\'xls\') or (cvtype=\'doc\')) and is_member_of(cvtype=\'project\' and name=\'' + name + '\' and version=\'' + version + '\')" -f "%name; %version; %modify_time; %status"'
                final_query =  query +' and recursive_is_member_of(cvtype=\'project\' and name=\'' + name + '\' and version=\'' + version + '\' , \'none\')" -f "%name; %version; %modify_time; %status"'
                stdout,stderr = self.ccm_query(final_query,"Get articles")
                if stdout != "":
                    output = stdout.splitlines()
                    for line in output:
                        line = re.sub(r"<void>",r"",line)
                        m = re.match(r'(.*);(.*);(.*);(.*);(.*)',line)
                        if m:
                            self.tableau_items.append([m.group(1),m.group(2),m.group(3),m.group(4),m.group((5))])

            else:
                for prj in list_projects:
                    name, version = self.getProjectInfo(prj)
                    final_query = query + ' and is_member_of(cvtype=\'project\' and name=\'' + name + '\' and version=\'' + version + '\')" -f "%project; %project_version; %name; %version; %modify_time; %status"'
                    stdout,stderr = self.ccm_query(final_query,"Get articles")
                    if stdout != "":
                        output = stdout.splitlines()
                        for line in output:
                            line = re.sub(r"<void>",r"",line)
                            m = re.match(r'(.*);(.*);(.*);(.*);(.*)',line)
                            if m:
                                tableau.append([name + "-" + version,m.group(2),m.group(3),m.group(4),m.group((5))])
            if len(tableau) == 1:
                 tableau.append(["--","--","--","--","--"])
        return tableau

    def getPR(self):
##        proc = Popen(self.ccm_exe + ' query -sby crstatus -f "%problem_number;%problem_synopsis;%crstatus" "(cvtype=\'problem\') and ((crstatus=\'concluded\') or (crstatus=\'entered\') or (crstatus=\'in_review\') or (crstatus=\'assigned\') or (crstatus=\'resolved\') or (crstatus=\'deferred\'))"', stdout=PIPE, stderr=PIPE)
        query = 'query -sby crstatus '
        if self.release != "":
            condition = '"(cvtype=\'problem\') and (implemented_in=\''+ self.release +'\')" '
        else:
            condition = '"(cvtype=\'problem\')" '
##        query = 'query -sby crstatus "(cvtype=\'problem\') and (implemented_in=\''+ self.release +'\')" -f "%problem_number;%problem_synopsis;%crstatus;%detected_on;%implemented_in"'
        query = query + condition + '-f "%problem_number;%problem_synopsis;%crstatus;%detected_on;%implemented_in"'
        stdout,stderr = self.ccm_query(query,"Get PRs")
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Query completed.\n")
        self.tableau_pr = []
        # Header
        self.tableau_pr.append(["ID","Synopsis","Status","Detected on","Implemented in"])
        if stdout != "":
            output = stdout.splitlines()
            for line in output:
                line = re.sub(r"<void>",r"",line)
                line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                m = re.match(r'(.*);(.*);(.*);(.*);(.*)',line)
                if m:
                    self.tableau_pr.append([m.group(1),m.group(2),m.group(3),m.group(4),m.group(5)])
        if len(self.tableau_pr) == 1:
             self.tableau_pr.append(["--","--","--","--","--"])

    def createDoc(self,tableau_items,tableau_source):
        item_description = self.getItemDescription(self.item)
        ci_identification = self.get_ci_identification(self.item)
        # Load the original template

        template = zipfile.ZipFile(self.template_name,mode='r')
        if template.testzip():
            raise Exception('File is corrupted!')

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
                print curact
                xmlcontent = template.read(curact[0])
                outdoc[curact[0]] = etree.fromstring(xmlcontent)

                # Will work on body
                docbody = outdoc[curact[0]].xpath(curact[1], namespaces=docx.nsprefixes)[0]

                # Replace some tags
                if self.template_type == "HCMR":
                    docbody = self.replaceTag(docbody, 'SUBJECT', ('str', self.item + " Hardware Confguration Management Record") )
                    docbody = self.replaceTag(docbody, 'TITLE', ('str', self.item + ' HCMR') )
                elif self.template_type == "SCI":
                    docbody = self.replaceTag(docbody, 'SUBJECT', ('str', self.item + " Software Configuration Index") )
                    docbody = self.replaceTag(docbody, 'TITLE', ('str', self.item + ' SCI') )
                else:
                    docbody = self.replaceTag(docbody, 'SUBJECT', ('str', self.item + " Configuration Index Document") )
                    docbody = self.replaceTag(docbody, 'TITLE', ('str', self.item + ' CID') )
                docbody = self.replaceTag(docbody, 'CI_ID', ('str', ci_identification) )
                docbody = self.replaceTag(docbody, 'REFERENCE', ('str', self.reference) )
                docbody = self.replaceTag(docbody, 'ISSUE', ('str', "1D1") )
                docbody = self.replaceTag(docbody, 'ITEM', ('str', self.item) )
                docbody = self.replaceTag(docbody, 'ITEM_DESCRIPTION', ('str', item_description) )
                if self.project != "":
                    if len(list_projects) == 0:
                        text = "No project selected"
                    elif len(list_projects) == 1:
                        text = "The project is " + self.project
                    else:
                        text = "The projects are: "
                        for project in list_projects:
                            text =  text + project + ", "
                    docbody = self.replaceTag(docbody, 'PROJECT', ('str', text) )
                else:
                    docbody = self.replaceTag(docbody, 'PROJECT', ('str', 'The project is not defined.') )
                if self.release != "":
                    docbody = self.replaceTag(docbody, 'RELEASE', ('str', self.release) )
                else:
                    docbody = self.replaceTag(docbody, 'RELEASE', ('str', 'not defined.') )
                if self.baseline != "":
                    docbody = self.replaceTag(docbody, 'BASELINE', ('str', self.baseline) )
                else:
                    docbody = self.replaceTag(docbody, 'BASELINE', ('str', 'not defined.') )
                if self.author != "":
                    docbody = self.replaceTag(docbody, 'WRITER', ('str', self.author) )
                else:
                    docbody = self.replaceTag(docbody, 'WRITER', ('str', 'Nobody') )
                docbody = self.replaceTag(docbody, 'DATE', ('str', time.strftime("%d %b %Y", time.gmtime())))
                colw = [1000,2300,200,1000,500,500,500] # 5000 = 100%
                docbody = self.replaceTag(docbody, 'TABLEITEMS', ('tab', tableau_items),
                {
                    'heading': True,
                    'colw': colw,
                    'cwunit': 'pct',
                    'tblw': 5000,
                    'twunit': 'pct',
                    'borders': {
                        'all': {
                            'color': 'auto',
                            'space': 0,
                            'sz': 6,
                            'val': 'single',
                        },
                    },
        ##            'celstyle': [
        ##                {'align': 'center'},
        ##                {'align': 'left'},
        ##                {'align': 'right'},
        ##            ],
        ##            'headstyle': { 'fill':'C6D9F1', 'themeFill':None, 'themeFillTint':None },
                })
                docbody = self.replaceTag(docbody, 'TABLESOURCE', ('tab', tableau_source),
                {
                    'heading': True,
                    'colw': colw,
                    'cwunit': 'pct',
                    'tblw': 5000,
                    'twunit': 'pct',
                    'borders': {
                        'all': {
                            'color': 'auto',
                            'space': 0,
                            'sz': 6,
                            'val': 'single',
                        },
                    },
        ##            'celstyle': [
        ##                {'align': 'center'},
        ##                {'align': 'left'},
        ##                {'align': 'right'},
        ##            ],
        ##            'headstyle': { 'fill':'C6D9F1', 'themeFill':None, 'themeFillTint':None },
                })
                docbody = self.replaceTag(docbody, 'TABLEPRS', ('tab', self.tableau_pr),
                {
                    'heading': True,
                    'colw': [500,3000,500,500,500], # 5000 = 100%
                    'cwunit': 'pct',
                    'tblw': 5000,
                    'twunit': 'pct',
                    'borders': {
                        'all': {
                            'color': 'auto',
                            'space': 0,
                            'sz': 6,
                            'val': 'single',
                        },
                    },
        ##            'celstyle': [
        ##                {'align': 'center'},
        ##                {'align': 'left'},
        ##                {'align': 'right'},
        ##            ],
        ##            'headstyle': { 'fill':'C6D9F1', 'themeFill':None, 'themeFillTint':None },
                })
                # Cleaning
                docbody = docx.clean(docbody)
        except KeyError as exception:
            print >>sys.stderr, "Execution failed:", exception

        # ------------------------------
        # Save output
        # ------------------------------

        # Prepare output file
        self.docx_filename = self.aircraft + "_" + self.item + "_" + self.template_type + "_" + self.reference + ".docx"
        try:
            outfile = zipfile.ZipFile(self.docx_filename,mode='w',compression=zipfile.ZIP_DEFLATED)

            # Copy unmodified sections
            for f in template.namelist():
                if not f in map(lambda i: i[0], actlist):
                    fo = template.open(f,'rU')
                    data = fo.read()
                    outfile.writestr(f,data)
                    fo.close()

            # The copy modified sections
            for sec in outdoc.keys():
                treestring = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "\n"
                treestring += etree.tostring(outdoc[sec], pretty_print=True)
                outfile.writestr(sec,treestring)
            # Done. close files.
            outfile.close()
            exception = ""
        except IOError as exception:
            print >>sys.stderr, "Execution failed:", exception
            self.docx_filename = False

        template.close()
        return self.docx_filename,exception
# -----------------------------------------------------------------------------
class ThreadQuery(threading.Thread,Tool):

    def __init__(self,queue="",master=""):
        threading.Thread.__init__(self)
        Tool.__init__(self)
        self.queue = queue
        self.master = master
        self.running = 1

        self.database = ""
        self.author = ""
        self.login = ""
        self.password = ""
        self.reference = ""
        self.release = ""
        self.aircraft = ""
        self.item = ""
        self.project = ""
        self.baseline = ""

        self.verrou =threading.Lock()

##    def getSessionStatus(self):
##        global session_started
##        if session_started:
##            interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Check session...\n")
##            proc = Popen(self.ccm_exe + ' status ', stdout=PIPE, stderr=PIPE)
##            stdout, stderr = proc.communicate()
##            print stdout
##            if stderr:
##                print 'Error while starting a synergy Session: ' + stderr
##            time.sleep(1)
##            return_code = proc.wait() #\/usr\/local\/ccmdb\/
##            m = re.search(r'Database:(.*)',stdout)
##            if m:
##                print m.group
##            interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Session checking finished.\n")
##            return_code = m
##        else:
##            return_code = False
##        return return_code

    def stopSession(self):
        stdout,stderr = self.ccm_query('stop','Stop Synergy session')

    def storeSelection(self,project,item,release,baseline):
        try:
            now = datetime.datetime.now()
            if baseline == "All":
                baseline = ""
            if release == "All":
                release = ""
            if project == "All":
                project = ""
            con = lite.connect('synergy.db', isolation_level=None)
            cur = con.cursor()
##            cur.execute("DROP TABLE IF EXISTS last_query")
            cur.execute("CREATE TABLE IF NOT EXISTS last_query (id INTEGER PRIMARY KEY, reference TEXT, revision TEXT ,database TEXT, project TEXT, item TEXT, release TEXT, baseline TEXT, input_date timestamp)")
            cur.execute("SELECT id FROM last_query WHERE item LIKE '" + item + "' LIMIT 1")
            data = cur.fetchone()
            if data != None:
                id = data[0]
                cur.execute("UPDATE last_query SET database=?,project=?,release=?,baseline=?,input_date=? WHERE id= ?",(self.database,project,release,baseline,now,id))
            else:
                cur.execute("INSERT INTO last_query(database,project,item,release,baseline,input_date) VALUES(?,?,?,?,?,?)",(self.database,project,item,release,baseline,now))
            cur.execute("DELETE FROM last_query WHERE id NOT IN ( SELECT id FROM ( SELECT id FROM last_query ORDER BY input_date DESC LIMIT 4) x )")
            lid = cur.lastrowid
##            print "The last Id of the inserted row is %d" % lid

        except lite.Error, e:
            print "Error %s:" % e.args[0]
##            sys.exit(1)
        finally:
            if con:
                con.close()
    # -----------------------------------------------------------------------------
    # Utility replacement function
    # -----------------------------------------------------------------------------


    def processIncoming(self):
        global session_started
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                # Check contents of message
                action = self.queue.get(0)
                print action
                if action == "BUILD_DOCX":
                    data = self.queue.get(1)
                    author = data[0]
                    reference = data[1]
                    release = data[2]
                    project = data[3]
                    baseline = data[4]
                    object_released = data[5]
                    object_integrate = data[6]

                    interface.output_txt.delete(1.0, END)
                    #store information in sqlite db
                    self.storeSelection(project,self.item,release,baseline)
                    self.build_doc_thread = threading.Thread(None,generateDoc,None,(author,reference,release,self.aircraft,self.item,project,baseline,object_released,object_integrate))
                    self.build_doc_thread.start()
                    # Make a query to synergy

                elif action == "START_SESSION":
                    # start synergy session
                    data = self.queue.get(1)
                    self.database = data[0]
                    login = data[1]
                    password = data[2]
                    self.item = data[3]
                    self.aircraft = data[4]
                    self.start_session_thread = threading.Thread(None,startSession,None,(self.item,self.database,login,password))
                    if session_started:
                        interface.button_select.configure(state=DISABLED)
                        interface.button_find_baselines.configure(state=DISABLED)
                        interface.button_find_releases.configure(state=DISABLED)
                        interface.button_find_projects.configure(state=DISABLED)
##                        self.stopSession()
                    self.start_session_thread.start()

                elif action == "GET_BASELINES":
                    release = self.queue.get(1)
                    self.get_baselines_thread = threading.Thread(None,getBaselinesList,None,(release,))
                    self.get_baselines_thread.start()

                elif action == "GET_RELEASES":
                    self.get_releases_thread = threading.Thread(None,getReleasesList,None)
                    self.get_releases_thread.start()

                elif action == "GET_PROJECTS":
                    data = self.queue.get(1)
                    release = data[0]
                    baseline = data[1]
                    self.get_projects_thread = threading.Thread(None,getProjectsList,None,(release,baseline))
                    self.get_projects_thread.start()

                else:
                    pass
            except Queue.Empty:
                pass

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
##        print time.strftime("%H:%M:%S", time.gmtime())
        self.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    def run(self):
        self.periodicCall()

    def stop(self):
        self.terminated = True

class Login (Frame,Tool):
    def __init__(self, fenetre, **kwargs):
        global queue
        self.queue = queue
        # read config file
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        self.login = config_parser.get("User","login")
        self.password = config_parser.get("User","password")
        # Create widgets
        entry_size = 30
        # Create top frame, with scrollbar and listbox
        background = 'grey50'
        Frame.__init__(self, fenetre, width=768, height=576,relief =GROOVE, bg = background,**kwargs)
        self.pack(fill=BOTH)
        self.can = Canvas(self, width =64, height =64, bg =background,highlightthickness=0)
        bitmap = PhotoImage(file="doc.gif")
##        bitmap = BitmapImage(file="zodiac.xbm")
        self.can.create_image(32,32,image =bitmap)
        self.can.bitmap = bitmap
        self.login_txt = Label(self, text='Login:', fg='white',bg = background)
        self.login_entry = Entry(self, state=NORMAL,width=entry_size)
        self.login_entry.insert(END, self.login)
        self.password_txt = Label(self, text='Password:', fg='white',bg = background)
        self.password_entry = Entry(self, state=NORMAL,width=entry_size)
        self.password_entry.configure(show='*')
        self.password_entry.insert(END, self.password)

##        self.varcombo = StringVar()
##        self.database_txt = Label(self, text='Systems:', fg='white',bg = background)
##        self.combo = ComboBox(fenetre, editable=1, dropdown=1, variable=self.varcombo, command = self.Affiche)
##        self.combo.entry.config(width=8,state='readonly')  ## met la zone de texte en lecture seule
        # populate systems listbox with table of systems
##        result = sqlite_query('SELECT id,name FROM systems')
##        print result
##        for item in result:
##            self.combo.insert(item[0], item[1])
##        combo.insert(0, 'NT')
##        combo.insert(1, 'Linux')
##        self.combo.pack()


        self.database_txt = Label(self, text='Systems:', fg='white',bg = background)
        self.listbox = Listbox(self,height=12,width=entry_size,exportselection=0)
        self.populate_listbox('SELECT name FROM systems ORDER BY systems.name ASC',self.listbox,"None")
        # Tie listbox and scrollbar together
        self.vbar_1 = vbar_1 = Scrollbar(self, name="vbar_1")
        vbar_1["command"] = self.listbox.yview
        self.listbox["yscrollcommand"] = vbar_1.set
        # Bind events to the list box
        self.listbox.bind("<ButtonRelease-1>", self.select_system)
        self.listbox.bind("<Key-Up>", self.up_event_1)
        self.listbox.bind("<Key-Down>", self.down_event_1)

        self.items_txt = Label(self, text='Items:', fg='white',bg = background)
        self.itemslistbox = Listbox(self,height=6,width=entry_size,exportselection=0)
        self.itemslistbox.insert(END, "All")
        self.vbar_2 = vbar_2 = Scrollbar(self, name="vbar_2")
        vbar_2["command"] = self.itemslistbox.yview
        self.itemslistbox["yscrollcommand"] = vbar_2.set
        self.itemslistbox.bind("<ButtonRelease-1>", self.select_item)
##        self.itemslistbox.bind("<Double-ButtonRelease-1>", self.double_click_item)
        self.itemslistbox.bind("<Key-Up>", self.up_event_2)
        self.itemslistbox.bind("<Key-Down>", self.down_event_2)

        self.button_select = Button(self, text='OK', state=DISABLED, command = self.click_select)
        self.button_quit = Button(self, text='Quit', command = self.click_quit)

        row_index = 1
        self.login_txt.grid(row =row_index,sticky='ES')
        self.login_entry.grid(row =row_index, column =1,sticky='E')
        self.can.grid(row =0, column =3,rowspan =6, padx =10, pady =5,sticky='W')

        row_index = row_index + 1
        self.password_txt.grid(row =row_index,sticky='E')
        self.password_entry.grid(row =row_index, column =1,sticky='E')

        # Database
        row_index = row_index + 1
        self.database_txt.grid(row =row_index,sticky='E')
        self.listbox.grid(row =row_index, column =1,sticky='E')
        self.vbar_1.grid(row =row_index, column =2,sticky='W')

        # Item
        row_index = row_index + 1
        self.items_txt.grid(row =row_index,sticky='E')
        self.itemslistbox.grid(row =row_index, column =1,sticky='E')
        self.vbar_2.grid(row =row_index, column =2,sticky='W')

        # Build & Quit
        row_index = row_index + 1
        self.button_select.grid(row =row_index, column =1,sticky='E')
        self.button_quit.grid(row =row_index, column =2,sticky='W')

    def select_item(self, event):
        item_id = self.itemslistbox.curselection()
        self.item_id = item_id
        self.button_select.configure(state=NORMAL)

    def select_system(self, event):
        # populate items listbox
        system_id = self.listbox.curselection()
        if system_id != () and '0' not in system_id:
            system = self.listbox.get(system_id)
            # Populate items list box
            query = 'SELECT items.name FROM items LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE systems.name = \'' + system + '\' ORDER BY items.name ASC'
            self.populate_listbox(query,self.itemslistbox,"All")
            self.listbox.activate(system_id)

    def click_select(self):
        global login_success
        if self.item_id != () and '0' not in self.item_id:
            item = self.itemslistbox.get(self.item_id)
            value = self.get_database(item)
            self.database = value[0][0]
            self.aircraft = value[0][1]
            # Get login and password information
            login = self.login_entry.get()
            password = self.password_entry.get()
            self.queue.put("START_SESSION") # action to start session
            self.queue.put([self.database,login,password,item,self.aircraft])
            login_success = True
            self.destroy()
            login_window.destroy()

    def click_quit(self):
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit now?"):
            self.destroy()
            login_window.destroy()

    def up_event_1(self, event):
        index = self.listbox.index("active")
        if self.listbox.selection_includes(index):
            index = index - 1
        else:
            index = self.listbox.size() - 1
        if index < 0:
            self.listbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def down_event_1(self, event):
        index = self.listbox.index("active")
        if self.listbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.listbox.size():
            self.listbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def up_event_2(self, event):
        index = self.itemlistbox.index("active")
        if self.itemlistbox.selection_includes(index):
            index = index - 1
        else:
            index = self.itemlistbox.size() - 1
        if index < 0:
            self.itemlistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def down_event_2(self, event):
        index = self.itemlistbox.index("active")
        if self.itemlistbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.itemlistbox.size():
            self.itemlistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

class Interface (Frame,Tool):
    def __init__(self, fenetre, **kwargs):
        global queue
        self.queue = queue
        # read config file
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        self.login = config_parser.get("User","login")
        self.password = config_parser.get("User","password")
        self.author = config_parser.get("User","author")

        self.reference = "ET1234-V"
        self.revision = "1D1"
        self.database = ""
        self.project = "All"
        self.aircraft = ""
        self.item = ""
        self.release = ""
        self.baseline = ""
        self.item_id = ""
        self.session_started = False
        # Create widgets
        entry_size = 30
        # Create top frame, with scrollbar and listbox
        background = 'grey50'
        Frame.__init__(self, fenetre, width=768, height=576,relief =GROOVE, bg = background,**kwargs)
        self.pack(fill=BOTH)
        self.can = Canvas(self, width =64, height =64, bg =background,highlightthickness=0)
        bitmap = PhotoImage(file="doc.gif")
##        bitmap = BitmapImage(file="zodiac.xbm")
        self.can.create_image(32,32,image =bitmap)
        self.can.bitmap = bitmap
##        self.login_txt = Label(self, text='Login:', fg='white',bg = background)
##        self.login_entry = Entry(self, state=NORMAL,width=entry_size)
##        self.login_entry.insert(END, self.login)
##        self.password_txt = Label(self, text='Password:', fg='white',bg = background)
##        self.password_entry = Entry(self, state=NORMAL,width=entry_size)
##        self.password_entry.configure(show='*')
##        self.password_entry.insert(END, self.password)
        self.author_txt = Label(self, text='Author:', fg='white',bg = background)
        self.author_entry = Entry(self, state=NORMAL,width=entry_size)
        self.author_entry.insert(END, self.author)
        self.reference_txt = Label(self, text='Reference:', fg='white',bg = background)
        self.reference_entry = Entry(self, state=NORMAL,width=entry_size)
        self.reference_entry.insert(END, self.reference)
        self.revision_txt = Label(self, text='Issue:', fg='white',bg = background)
        self.revision_entry = Entry(self, state=NORMAL,width=entry_size)
        self.revision_entry.insert(END, self.revision)
        self.vbar_1 = vbar_1 = Scrollbar(self, name="vbar_1")
        self.vbar_2 = vbar_2 = Scrollbar(self, name="vbar_2")
        self.vbar_3 = vbar_3 = Scrollbar(self, name="vbar_3")
        self.vbar_4 = vbar_4 = Scrollbar(self, name="vbar_4")
        self.vbar_5 = vbar_5 = Scrollbar(self, name="vbar_5")

##        self.database_txt = Label(self, text='Systems:', fg='white',bg = background)
##        self.listbox = Listbox(self,height=3,width=entry_size,exportselection=0)
##        # Tie listbox and scrollbar together
##        vbar_1["command"] = self.listbox.yview
##        self.listbox["yscrollcommand"] = vbar_1.set
##        # Bind events to the list box
##        self.listbox.bind("<ButtonRelease-1>", self.select_system)
##        self.listbox.bind("<Double-ButtonRelease-1>", self.double_click_system)
##        self.listbox.bind("<Key-Up>", self.up_event_1)
##        self.listbox.bind("<Key-Down>", self.down_event_1)
##
##        self.items_txt = Label(self, text='Items:', fg='white',bg = background)
##        self.itemslistbox = Listbox(self,height=3,width=entry_size,exportselection=0)
##        self.itemslistbox.insert(END, "All")
##        if self.item != "":
##            self.itemslistbox.insert(END, self.item)
##        vbar_2["command"] = self.itemslistbox.yview
##        self.itemslistbox["yscrollcommand"] = vbar_2.set
##        self.itemslistbox.bind("<ButtonRelease-1>", self.select_item)
####        self.itemslistbox.bind("<Double-ButtonRelease-1>", self.double_click_item)
##        self.itemslistbox.bind("<Key-Up>", self.up_event_2)
##        self.itemslistbox.bind("<Key-Down>", self.down_event_2)

        self.release_txt = Label(self, text='Release:', fg='white',bg = background)
        self.releaselistbox = Listbox(self,height=3,width=entry_size,exportselection=0)
        self.releaselistbox.insert(END, "All")
##        if self.release != "*":
##            self.releaselistbox.insert(END, self.release)
        vbar_3["command"] = self.releaselistbox.yview
        self.releaselistbox["yscrollcommand"] = vbar_3.set
        self.releaselistbox.bind("<ButtonRelease-1>", self.select_release)
        self.releaselistbox.bind("<Key-Up>", self.up_event_3)
        self.releaselistbox.bind("<Key-Down>", self.down_event_3)
        self.button_find_releases = Button(self, text='Refresh', state=DISABLED, command = self.find_releases)

        self.project_txt = Label(self, text='Project:', fg='white',bg = background)
        self.projectlistbox = Listbox(self,height=3,width=entry_size,exportselection=0)
        self.projectlistbox.insert(END, "All")
##        if self.project != "*":
##            self.projectlistbox.insert(END, self.project)
        vbar_4["command"] = self.projectlistbox.yview
        self.projectlistbox["yscrollcommand"] = vbar_4.set
        self.projectlistbox.bind("<ButtonRelease-1>", self.select_project)
        self.projectlistbox.bind("<Key-Up>", self.up_event_4)
        self.projectlistbox.bind("<Key-Down>", self.down_event_4)
        self.button_find_projects = Button(self, text='Refresh', state=DISABLED, command = self.find_projects)

        self.directory_txt = Label(self, text='Directory:', fg='white',bg = background)
        self.directory_entry = Entry(self, state=NORMAL,width=entry_size)
        self.directory_entry.insert(END, "*")
        self.button_select = Button(self, text='Build', state=DISABLED, command = self.click_select)
        self.button_quit = Button(self, text='Quit', command = self.click_quit)
        self.status_released = IntVar()
        self.check_button_status_released = Checkbutton(self, text="Released", variable=self.status_released,fg='grey',bg = background,command=self.cb_released)
        self.status_integrate = IntVar()
        self.check_button_status_integrate = Checkbutton(self, text="Integrate", variable=self.status_integrate,fg='grey',bg = background,command=self.cb_integrate)
        self.output_label = Label(self, text='Output:',fg='white',bg = background)
        self.output_txt = Text(self, width = 44, height = 12)

        row_index = 1
##        self.login_txt.grid(row =row_index,sticky='ES')
##        self.login_entry.grid(row =row_index, column =1,sticky='E')
##        self.can.grid(row =0, column =3,rowspan =6, padx =10, pady =5,sticky='W')
##
##        row_index = row_index + 1
##        self.password_txt.grid(row =row_index,sticky='E')
##        self.password_entry.grid(row =row_index, column =1,sticky='E')
        self.author_txt.grid(row =row_index,sticky='E')
        self.author_entry.grid(row = row_index, column =1,sticky='E')

        row_index = row_index + 1
        self.reference_txt.grid(row =row_index,sticky='E')
        self.reference_entry.grid(row = row_index, column =1,sticky='E')

        row_index = row_index + 1
        self.revision_txt.grid(row =row_index,sticky='E')
        self.revision_entry.grid(row =row_index, column =1,sticky='E')

##        # Database
##        row_index = row_index + 1
##        self.database_txt.grid(row =row_index,sticky='E')
##        self.listbox.grid(row =row_index, column =1,sticky='E')
##        self.vbar_1.grid(row =row_index, column =2,sticky='W')
##
##        # Item
##        row_index = row_index + 1
##        self.items_txt.grid(row =row_index,sticky='E')
##        self.itemslistbox.grid(row =row_index, column =1,sticky='E')
##        self.vbar_2.grid(row =row_index, column =2,sticky='W')

        # Release
        row_index = row_index + 1
        self.release_txt.grid(row =row_index,sticky='E')
        self.releaselistbox.grid(row =row_index, column =1,sticky='E')
        self.vbar_3.grid(row =row_index, column =2,sticky='W')
        self.button_find_releases.grid(row =row_index, column =2,sticky='W',padx=20)

        # Baseline
        self.baseline_txt = Label(self, text='Baseline:', fg='white',bg = background)
        self.baselinelistbox = Listbox(self,height=3,width=entry_size,exportselection=0)
        self.baselinelistbox.insert(END, "All")
##        if self.baseline != "*":
##            self.baselinelistbox.insert(END, self.release)
        vbar_5["command"] = self.baselinelistbox.yview
        self.baselinelistbox["yscrollcommand"] = vbar_5.set
        self.baselinelistbox.bind("<ButtonRelease-1>", self.select_baseline)
        self.baselinelistbox.bind("<Key-Up>", self.up_event_5)
        self.baselinelistbox.bind("<Key-Down>", self.down_event_5)
        self.button_find_baselines = Button(self, text='Refresh', state=DISABLED, command = self.find_baselines)

        row_index = row_index + 1
        self.baseline_txt.grid(row =row_index,sticky='E')
        self.baselinelistbox.grid(row =row_index, column =1,sticky='E')
        self.vbar_5.grid(row =row_index, column =2,sticky='W')
        self.button_find_baselines.grid(row =row_index, column =2,sticky='W',padx=20)

        # Project
        row_index = row_index + 1
        self.project_txt.grid(row =row_index,sticky='E')
        self.projectlistbox.grid(row =row_index, column =1,sticky='E')
        self.vbar_4.grid(row =row_index, column =2,sticky='W')
        self.button_find_projects.grid(row =row_index, column =2,sticky='W',padx=20)

        #self.directory_txt.grid(row =8,sticky='E')
        #self.directory_entry.grid(row =8, column =1,sticky='E')
        # Build & Quit
        row_index = row_index + 1
        self.button_select.grid(row =row_index, column =1,pady=5,sticky='E')
        self.button_quit.grid(row =row_index, column =2,pady=5,sticky='W')
        # Check buttons
        row_index = row_index + 1
        self.objects_txt = Label(self, text='Objects:', fg='white',bg = background)
        self.objects_txt.grid(row =row_index,sticky='E')
        self.check_button_status_released.grid(row =row_index, column =1, padx=10,sticky='W')
        self.check_button_status_integrate.grid(row =row_index, column =1,sticky='E')
        # Output
        row_index = row_index + 1
        self.output_label.grid(row =row_index,sticky='E')
        row_index = row_index + 1
        self.output_txt.grid(row =row_index ,columnspan =4, pady =20,padx = 10)
        # populate systems listbox with table of systems
##        self.populate_listbox('SELECT id,name FROM systems',self.listbox,"None")

    def cb_released(self):
        print "variable is", self.status_released.get()

    def cb_integrate(self):
        print "variable is", self.status_integrate.get()

    def __del__(self):
        # kill threads
        pass

    def help(self):
        help_window = Tk()
        help_window.iconbitmap("qams.ico")
        help_window.title("Help")
        help_window.resizable(False,False)
        readme_file = open('README.txt', 'r')
        readme_text = readme_file.read()
        readme_file.close()
        tex1 = Label(help_window, text=readme_text, fg='grey50')
        tex1.pack()
        bou1 = Button(help_window, text='Quitter', command = fen1.destroy)
        bou1.pack()
        help_window.mainloop()

    def about(self):
        tkMessageBox.showinfo("Make configuration Index Document", "docid is written by Olivier Appere\n\n (c) Copyright 2013")

    def click_event(self, event):
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
        self.select(index)
        self.on_select(index)
        return "break"

    def double_click_event(self, event):
        index = self.listbox.index("active")
        self.select(index)
        self.on_double(index)
        return "break"
    menu = None

    def on_select(self, event):
       pass

    def select(self, event):
       pass

##    def select_system(self, event):
##        # populate items listbox
##        system_id = self.listbox.curselection()
##        if system_id != () and '0' not in system_id:
##            # Populate items list box
##            query = 'SELECT items.id, items.name FROM items LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id WHERE link_systems_items.system_id = {:s}'.format(system_id[0] + " ORDER BY items.name ASC")
##            self.populate_listbox(query,self.itemslistbox,"All")
##            self.listbox.activate(system_id)

    def select_item(self, event):
        item_id = self.itemslistbox.curselection()
        self.item_id = item_id
        if item_id != () and '0' not in item_id:
            item = self.itemslistbox.get(item_id)
            value = self.get_database(item)
            self.database = value[0][0]
            self.aircraft = value[0][1]
            # Get login and password information
            login = self.login_entry.get()
            password = self.password_entry.get()
            self.queue.put("START_SESSION") # action to start session
            self.queue.put([self.database,login,password])

    def double_click_system(self, event):
        pass

    def find_baselines(self):
        self.baselinelistbox.delete(0, END)
##        self.baselinelistbox.insert(END, "All")
        self.queue.put("GET_BASELINES") # action to get baselines
        self.queue.put(self.release)

    def find_releases(self):
        self.releaselistbox.delete(0, END)
##        self.releaselistbox.insert(END, "All")
        self.queue.put("GET_RELEASES") # action to get releases

    def find_projects(self):
        self.projectlistbox.delete(0, END)
##        self.projectlistbox.insert(END, "All")
        self.queue.put("GET_PROJECTS") # action to get projects
        self.queue.put((self.release,self.baseline))

    def select_baseline(self, event):
        index = self.baselinelistbox.curselection()
        if index == 0:
            baseline = ""
        else:
            baseline = self.baselinelistbox.get(index)
        self.baseline = baseline

    def select_release(self, event):
        index = self.releaselistbox.curselection()
        if index == 0:
            release = ""
        else:
            release = self.releaselistbox.get(index)
        self.release = release

    def select_project(self, event):
        index = self.projectlistbox.curselection()
        if index == 0:
            project = ""
        else:
            project = self.projectlistbox.get(index)
        self.project = project

    def make_menu(self):
        menu = Menu(self.listbox, tearoff=0)
        self.menu = menu
        self.fill_menu()

    def up_event_1(self, event):
        index = self.listbox.index("active")
        if self.listbox.selection_includes(index):
            index = index - 1
        else:
            index = self.listbox.size() - 1
        if index < 0:
            self.listbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def down_event_1(self, event):
        index = self.listbox.index("active")
        if self.listbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.listbox.size():
            self.listbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def up_event_2(self, event):
        index = self.itemlistbox.index("active")
        if self.itemlistbox.selection_includes(index):
            index = index - 1
        else:
            index = self.itemlistbox.size() - 1
        if index < 0:
            self.itemlistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def down_event_2(self, event):
        index = self.itemlistbox.index("active")
        if self.itemlistbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.itemlistbox.size():
            self.itemlistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def up_event_3(self, event):
        index = self.releaselistbox.index("active")
        if self.releaselistbox.selection_includes(index):
            index = index - 1
        else:
            index = self.releaselistbox.size() - 1
        if index < 0:
            self.releaselistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def down_event_3(self, event):
        index = self.releaselistbox.index("active")
        if self.releaselistbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.releaselistbox.size():
            self.releaselistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def up_event_4(self, event):
        index = self.projectlistbox.index("active")
        if self.projectlistbox.selection_includes(index):
            index = index - 1
        else:
            index = self.projectlistbox.size() - 1
        if index < 0:
            self.projectlistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def down_event_4(self, event):
        index = self.projectlistbox.index("active")
        if self.projectlistbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.projectlistbox.size():
            self.projectlistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def up_event_5(self, event):
        index = self.baselinelistbox.index("active")
        if self.baselinelistbox.selection_includes(index):
            index = index - 1
        else:
            index = self.baselinelistbox.size() - 1
        if index < 0:
            self.baselinelistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def down_event_5(self, event):
        index = self.baselinelistbox.index("active")
        if self.baselinelistbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= self.baselinelistbox.size():
            self.baselinelistbox.bell()
        else:
            self.select(index)
            self.on_select(index)
        return "break"

    def click_quit(self):
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit now?"):
            self.destroy()
            fenetre.destroy()

    def click_select(self):
            # Get author
            author = self.author
            # Get reference
            reference = self.reference_entry.get()
            # Get baseline
            baseline = self.baseline
            # Get release
            release = self.release
            # Get project
            project = self.project
            # Get aircraft
##            aircraft = self.aircraft
            # Get item
            #index = self.itemslistbox.curselection()
##            index = self.item_id
##            if index == "":
##                tkMessageBox.showerror("Item selection", "No item selected.")
##            else:
##                item = self.itemslistbox.get(index)
##                # Get directory
##                directory = self.directory_entry.get()
            # Get project and database listbox information
            self.queue.put("BUILD_DOCX") # order to build docx
            self.queue.put([self.author,self.reference,self.release,self.project,self.baseline,self.status_released.get(),self.status_integrate.get()])
def destroy_app():
    global thread_build_docx
    thread_build_docx.stop()
    print "CROSS MARK PUSHED"

if __name__ == '__main__':
    try:
        session_started = False
        list_projects = []
        login_success = False
        verrou = threading.Lock()

        # Create the queue
        queue = Queue.Queue()

        login_window = Tk()
        login_window.iconbitmap("qams.ico")
        login_window.title("Login")
        login_window.resizable(False,False)
        interface_login = Login(login_window)
        interface_login.mainloop()

        if login_success:
    ##        sys.exit()
            fenetre = Tk()
            fenetre.iconbitmap("qams.ico")
            fenetre.title("Create Configuration Index Document")
            fenetre.resizable(False,False)
            interface = Interface(fenetre)

            # create a toplevel menu
            mainmenu = Menu(fenetre)
            menubar = Menu(mainmenu)
            menubar.add_command(label="Help", command=interface.help)
            menubar.add_separator()
            menubar.add_command(label="Quit", command=interface.click_quit)
            mainmenu.add_cascade(label = "Home", menu = menubar)
            mainmenu.add_command(label="About", command=interface.about)
            # display the menu
            fenetre.configure(menu = mainmenu)

            # instance threads
            thread_build_docx = ThreadQuery(queue,fenetre)
            thread_build_docx.start()
            # --------------------------
            # to bind the window manager's CLOSE event to a fn
            # --------------------------
            fenetre.protocol( "WM_DELETE_WINDOW", destroy_app )

            interface.mainloop()
##            fenetre.destroy()
            synergy = ThreadQuery()
            error_code = synergy.stopSession()
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e
