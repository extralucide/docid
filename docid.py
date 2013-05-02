#!/usr/bin/env python 2.7.3
# -*- coding: latin-1 -*-
"""
This file generates a SCI, HCMR and CID with a format .docx (Word 2007) based on a specific template.

"""
__author__ = "O. Appéré <olivier.appere@gmail.com>"
__date__ = "02 Mai 2013"
__version__ = "$Revision: 0.1 $"

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
try:
    import docx
except ImportError:
    raise ImportError, "DoCID requires the python-docx library for Python. " \
                       "See https://github.com/mikemaccana/python-docx/"
import threading
import time
from ConfigParser import ConfigParser
import re
import zipfile
from lxml import etree
import Queue
import datetime
from os.path import join
try:
    from PIL import Image
except ImportError:
    import Image
try:
    import Pmw
except ImportError:
    raise ImportError, "DoCID requires the Python MegaWidgets for Python. " \
                       "See http://sourceforge.net/projects/pmw/"
background = '#E7DAB2' #'grey50'
foreground = 'black'
def picture_add(relationshiplist, picname, picdescription, pixelwidth=None, pixelheight=None, nochangeaspect=True, nochangearrowheads=True):
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

def startSession(item,database,login,password):
    ''' Function to start Synergy session
         - invoke command ccm start ...
         - display synergy feedback
         - retrieve last session information
         - enable SELECT and REFRESH buttons
         - get list of releases
        called by the thread '''
    global session_started
    global description_item

    tool = Tool()
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Open Synergy session.\n")

    query = 'start /nogui /q /d /usr/local/ccmdb/' + database + ' /u /usr/local/ccmdb/' + database + ' /s ' + tool.ccm_server + ' /n ' + login + ' /pw ' + password
    stdout,stderr = tool.ccm_query(query,"Synergy session started")
    print time.strftime("%H:%M:%S", time.gmtime()) + " " + stdout
    if stderr:
        session_started = False
    else:
        session_started = True
    description_item = tool.getItemDescription(item)
    interface.project_description.configure(text = "Project: " + description_item)
    interface.project_description_entry_pg2.configure(text = description_item)
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
    getReleasesList()

    return stdout

def getReleasesList():
    ''' get releases list '''
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
    ''' get baseline list
            by invoking the command '''
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

def getProjectsList(release,baseline_selected,refresh=True):
    global session_started
    global list_projects
    tool = Tool()

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
                            break
##                   baseline_splitted = re.sub(r".*#",r"",baseline_splitted)

        else:
            for line in output:
                line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                m = re.match(r'(.*)-(.*);(.*)$',line)
                if m:
                    project = m.group(1) + "-" + m.group(2)
                    #print "name " + m.group(1) + " version " + m.group(2)
                else:
                    project = line
                list_projects.append(project)
        if refresh == True:
            interface.projectlistbox.delete(0, END)
            interface.projectlistbox.insert(END, "All")
            for project in list_projects:
                interface.projectlistbox.insert(END, project)
    else:
        interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " No projects found.\n")

def generateCID(author,
                reference,
                revision,
                release,
                aircraft,
                item,
                project,
                baseline,
                object_released,
                object_integrate,
                cid_type):
    '''
    get items by invoking synergy command
    get sources by invoking synergy command
    get CR by invoking synergy command
    '''
    import csv
    # read config file
    config_parser = ConfigParser()
    config_parser.read('docid.ini')
    type_doc = config_parser.get("Objects","type_doc")
    for list_type_doc in csv.reader([type_doc]):
        pass
    type_src = config_parser.get("Objects","type_src")
    for list_type_src in csv.reader([type_src]):
        pass

    if project == "All":
        getProjectsList(release,baseline,False)
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Begin document generation ...\n")
    cid = BuildDoc(author,reference,revision,aircraft,item,release,project,baseline)
    # Documentations
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Items query in progress...\n")
    tableau_items =cid.getArticles(object_released,object_integrate,list_type_doc)
    # Source
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Source code query in progress...\n")
    tableau_sources = cid.getArticles(object_released,object_integrate,list_type_src)
    # Problem Reports
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " PR query in progress...\n")
    cid.getPR()
    interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Creation doc in progress...\n")
    # Create docx
    docx_filename,exception = cid.createCID(tableau_items,tableau_sources,cid_type)
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

def generateSQAP(author,
                reference,
                revision,
                aircraft,
                item):
    '''

    '''
    sqap = BuildDoc(author,reference,revision,aircraft,item)

    interface.output_txt_pg2.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Creation doc in progress...\n")
    # Create docx
    docx_filename,exception = sqap.createSQAP()
    if docx_filename == False:
        interface.output_txt_pg2.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " " + exception.strerror + ", document not saved.\n")
    else:
        interface.output_txt_pg2.tag_configure("hlink", foreground='blue', underline=1)
        interface.output_txt_pg2.tag_bind("hlink", "<Button-1>", sqap.openHLink_qap)
        interface.output_txt_pg2.tag_bind("hlink", "<Enter>", sqap.onLink)
        interface.output_txt_pg2.tag_bind("hlink", "<Leave>", sqap.outsideLink)
        interface.output_txt_pg2.insert(END, time.strftime("%H:%M:%S", time.gmtime()) +  " Word document created.\n")
        interface.output_txt_pg2.insert(END, "Available here:\n")
        interface.output_txt_pg2.insert(END, docx_filename, "hlink")
        interface.output_txt_pg2.insert(END, "\n")

def getSessionStatus():
    global session_started
    tool = Tool()
    if 1==1:
##            interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Check session...\n")
        stdout,stderr = tool.ccm_query('status','Check session')
        print "OUT:" + stdout
        print "ERR:" + stderr
        m = re.search(r'Database:(.*)',stdout)
        if m:
            print m.group(1)
##            interface.output_txt.insert(END, time.strftime("%H:%M:%S", time.gmtime()) + " Session checking finished.\n")
        return_code = m
    else:
        return_code = False
    return return_code

##def populate_listbox(query,listbox,first):
##    # populate systems listbox
##    listbox.delete(0, END)
##    listbox.insert(END, first)
##    result = sqlite_query(query)
##    for item in result:
##        listbox.insert(item[0], item[1])

class Demo:
    def __init__(self, parent):
    # Create and pack the NoteBook.
        notebook = Pmw.NoteBook(parent)
        notebook.pack(fill = 'both', expand = 1, padx = 10, pady = 10)

        # Add the "Appearance" page to the notebook.
        page = notebook.add('Appearance')
        notebook.tab('Appearance').focus_set()

        # Create the "Toolbar" contents of the page.
        group = Pmw.Group(page, tag_text = 'Toolbar')
        group.pack(fill = 'both', expand = 1, padx = 10, pady = 10)
        b1 = Checkbutton(group.interior(), text = 'Show toolbar')
        b1.grid(row = 0, column = 0)
        b2 = Checkbutton(group.interior(), text = 'Toolbar tips')
        b2.grid(row = 0, column = 1)

        # Create the "Startup" contents of the page.
        group = Pmw.Group(page, tag_text = 'Startup')
        group.pack(fill = 'both', expand = 1, padx = 10, pady = 10)
        home = Pmw.EntryField(group.interior(), labelpos = 'w',
            label_text = 'Home page location:')
        home.pack(fill = 'x', padx = 20, pady = 10)

        # Add two more empty pages.
        page = notebook.add('Helpers')
        page = notebook.add('Images')

        notebook.setnaturalsize()

class Tool():
    '''
    Class toolbox
    '''
    def __init__(self):
        '''
        get in file .ini information to access synergy server
        '''
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        self.ccm_server = config_parser.get("Synergy","synergy_server")
        conf_synergy_dir = config_parser.get("Synergy","synergy_dir")
        self.ccm_exe = os.path.join(conf_synergy_dir, 'ccm')
    def ccb_minutes(self):
        pass
    def plan_review_minutes(self):
        pass
    def spec_review_minutes(self):
        pass

    def scrollEvent(self,event):
        print event.delta
        if event.delta >0:
            print 'déplacement vers le haut'
            self.help_text.yview_scroll(-2,'units')

        else:
            print 'déplacement vers le bas'
            self.help_text.yview_scroll(2,'units')

    def help(self):
        self.help_window = Tk()
        self.help_window.iconbitmap("qams.ico")
        self.help_window.title("Help")
        self.help_window.resizable(False,False)
        readme_file = open('README.txt', 'r')
        readme_text = readme_file.read()
        readme_file.close()
        help_frame = Frame(self.help_window, bg = '#80c0c0')
        help_frame.pack()
        scrollbar = Scrollbar(help_frame)
        self.help_window.bind('<MouseWheel>', self.scrollEvent)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.help_text = Text(help_frame,wrap=WORD, yscrollcommand=scrollbar.set, width = 100, height = 30)
        self.help_text.pack()
        scrollbar.config(command=self.help_text.yview)
        self.help_text.insert(END, readme_text)
        bou1 = Button(self.help_window, text='Quit', command = self.help_window.destroy)
        bou1.pack(side=RIGHT)
        self.help_window.mainloop()

    def about(self):
        tkMessageBox.showinfo("Make Configuration Index Document", "DoCID is written by Olivier Appere\n\n (c) Copyright 2013")

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

    def get_image(self,item):
        '''
        Get image in SQLite database
        '''
        query = "SELECT img FROM systems WHERE aircraft LIKE '{:s}'".format(item) + " LIMIT 1"
        result = self.sqlite_query_one(query)
        if result == None:
            image_name = None
        else:
            image_name = result[0]
        return image_name

    def get_database(self,index):
        query = "SELECT items.database,aircraft FROM items LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + index + "'"
        result = self.sqlite_query(query)
        print result
        return result[0][0],result[0][1]

    def get_ci_identification(self,index):
        if index != "":
            query = "SELECT ci_identification FROM items WHERE items.name LIKE '" + index + "'"
            result = self.sqlite_query(query)
            print result
            if result == None:
                ci_id = "TBD"
            else:
                ci_id = result[0][0]
        else:
            ci_id = None
        return ci_id

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

    def sqlite_create(self):
        try:
            con = lite.connect('docid.db3')
            cur = con.cursor()
            cur.executescript("""
            BEGIN TRANSACTION;
            CREATE TABLE document_types (id INTEGER PRIMARY KEY, description TEXT, name TEXT);
            CREATE TABLE documents (id INTEGER PRIMARY KEY, status_id NUMERIC, reference TEXT, last_revision TEXT,  item_id NUMERIC, type NUMERIC);
            CREATE TABLE history (id INTEGER PRIMARY KEY, writer_id NUMERIC, date TEXT, issue TEXT, document_id NUMERIC, modifications TEXT);
            CREATE TABLE items (id INTEGER PRIMARY KEY, ci_identification TEXT, database TEXT, description TEXT, name TEXT);
            CREATE TABLE link_systems_items (id INTEGER PRIMARY KEY, item_id NUMERIC, system_id NUMERIC);
            CREATE TABLE status (id INTEGER PRIMARY KEY, description TEXT,  name TEXT, transition TEXT, type TEXT);
            CREATE TABLE systems (id INTEGER PRIMARY KEY, img TEXT, aircraft TEXT,  name TEXT, ear TEXT);
            CREATE TABLE writers (id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE review_types (id INTEGER PRIMARY KEY, description TEXT, name TEXT);
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
    # SQLite
    def sqlite_query(self,query):
        try:
            con = lite.connect('docid.db3')
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
            con = lite.connect('docid.db3')
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
        proc_httpd = subprocess.Popen(httpd_dir + "httpd.exe -f " + config, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
        proc_mysql = subprocess.Popen(mysql_dir + "mysqld --defaults-file=mysql\bin\my.ini --standalone --console", stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
        stdout_httpd, stderr_httpd = proc_httpd.communicate()
        stdout_mysql, stderr_mysql = proc_mysql.communicate()
    ##    print time.strftime("%H:%M:%S", time.gmtime()) + " " + stdout
        if stderr_httpd:
            print "Error while executing httpd command: " + stderr_httpd
        elif stderr_mysql:
            print "Error while executing mysql command: " + stderr_mysql

##        time.sleep(1)
##        return_code_httpd = proc_httpd.wait()
##        return_code_mysql = proc_mysql.wait()
##        print stdout_httpd
##        print stdout_mysql

    # Synergy
    def ccm_query(self,query,cmd_name):
        print time.strftime("%H:%M:%S", time.gmtime()) + " ccm " + query
        # hide commmand DOS windows
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

    def getSystemName(self,item):
        query = "SELECT systems.name FROM systems LEFT OUTER JOIN link_systems_items ON link_systems_items.system_id = systems.id LEFT OUTER JOIN items ON items.id = link_systems_items.item_id WHERE items.name LIKE '{:s}'".format(item)
        print query
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
            description = "None"
        else:
            description = result[0]
        return description

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
    def getReviewList(self):
        query = "SELECT id,description FROM review_types"
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

# -----------------------------------------------------------------------------
class BuildDoc(Tool):
    def __init__(self,author,reference,revision,aircraft="",item="",release="",project="",baseline=""):
        Tool.__init__(self)
        self.author = author
        self.reference = reference
        self.revision = revision
        self.release = release
        self.aircraft = aircraft
        self.item = item
        self.project = project
        self.baseline = baseline
        self.tableau_pr = []

##        config_parser = ConfigParser()
##        config_parser.read('docid.ini')
##        try:
##            template_dir = join(os.path.dirname("."), 'template')
##            template_name = config_parser.get("Template","name")
##            self.template_name = join(template_dir, template_name)
##            self.template_type = config_parser.get("Template","type")
##            self.type_doc = config_parser.get("Objects","type_doc").split(",")
##            self.type_src = config_parser.get("Objects","type_src").split(",")
##        except IOError as exception:
####        except NoSectionError as exception:
##            print "Execution failed:", exception

    def replaceTag(self,doc, tag, replace, fmt = {}):
        """ Searches for {{tag}} and replaces it with replace.

    Replace is a list with two indexes: 0=type, 1=The replacement
    Supported values for type:
    'str': <string> Renders a simple text string
    'tab': <list> Renders a table, use fmt to tune look
    'img': <list> Renders an image
    """
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
        elif replace[0] == 'tab':
            # Will make a table
            unicode_table = []
            for element in replace[1]:
                try:
                    # Unicodize
                    unicode_table.append( map(lambda i: unicode(i, errors='ignore'), element) )
                except TypeError as exception:
                    print "Execution failed:", exception
                    unicode_table.append(element)
##                    print element
                except UnicodeDecodeError as exception:
                    print "Execution failed:", exception
                    unicode_table.appen(element)
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
        elif replace[0] == 'img':
            relationships = docx.relationshiplist()
            relationshiplist, repl = picture_add(relationships, replace[1],'This is a test description')
            return docx.advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl),relationshiplist
        else:
            raise NotImplementedError, "Unsupported " + replace[0] + " tag type!"

        return docx.advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl)

    def openHLink(self,event):
        start, end = interface.output_txt.tag_prevrange("hlink",
        interface.output_txt.index("@%s,%s" % (event.x, event.y)))
        print "Going to %s..." % interface.output_txt.get(start, end)
        os.startfile(self.docx_filename, 'open')
        #webbrowser.open

    def openHLink_qap(self,event):
        start, end = interface.output_txt_pg2.tag_prevrange("hlink",
        interface.output_txt_pg2.index("@%s,%s" % (event.x, event.y)))
        print "Going to %s..." % interface.output_txt_pg2.get(start, end)
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
                final_query =  query +' and recursive_is_member_of(cvtype=\'project\' and name=\'' + name + '\' and version=\'' + version + '\' , \'none\')" -f "%project; %name; %version; %modify_time; %status"'
                stdout,stderr = self.ccm_query(final_query,"Get articles")
                if stdout != "":
                    output = stdout.splitlines()
                    for line in output:
                        line = re.sub(r"<void>",r"",line)
                        m = re.match(r'(.*);(.*);(.*);(.*);(.*)',line)
                        if m:
                            tableau.append([m.group(1),m.group(2),m.group(3),m.group(4),m.group(5)])

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
        global session_started

        self.tableau_pr = []
        # Header
        self.tableau_pr.append(["ID","Synopsis","Status","Detected on","Implemented in"])
        if session_started:
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

    def createSQAP(self):
        '''
        This function creates the document based on the template
        - open template docx
        - get sections of the template
        - replace tag in document
        - create zip
         . copy unmodified section
         . copy modified section

        '''
        global list_projects

        template_type="SQAP"
        # Get config
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        try:
            template_dir = join(os.path.dirname("."), 'template')
            template_name = config_parser.get("Template",template_type)
            self.template_name = join(template_dir, template_name)
        except IOError as exception:
            print "Execution failed:", exception

        item_description = self.getItemDescription(self.item)
        ci_identification = self.get_ci_identification(self.item)
        # Load the original template
        try:
            template = zipfile.ZipFile(self.template_name,mode='r')
        except IOError as exception:
            print "Execution failed:", exception

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
                xmlcontent = template.read(curact[0])
                outdoc[curact[0]] = etree.fromstring(xmlcontent)

                # Will work on body
                docbody = outdoc[curact[0]].xpath(curact[1], namespaces=docx.nsprefixes)[0]

                # Replace some tags
                title = self.item + " " + template_type
                subject = self.item + " " + self.getTypeDocDescription(template_type)


                if self.author == "":
                    self.author = "Nobody"
                ear_txt = self.get_ear(self.item)
                # Update history in database
                self.updateLastModificationLog()
                # get list of modifications
                table_listmodifs = self.getListModifs(self.item)
                #convert tuple in array
                table_modifs = []
                # Header
                table_modifs.append(["Issue","Date","Purpose of Modification","Writer"])

                for issue,date,modification,author in table_listmodifs:
                    table_modifs.append([issue,date,modification,author])

##                table_modifs.append([self.revision,time.strftime("%d %b %Y", time.gmtime()),"Next",self.author])

##                print table_modifs
##                tableau = []
##                tableau.append(["Project","Data","Revision","Modified time","Status"])
##                table_listmodifs = [["TEST","DATE","TEXT","WRITER"]]
                colw = [500,1000,3000,500] # 5000 = 100%
                system_name = self.getSystemName(self.item)
                list_tags = {
                            'SUBJECT':{
                                'type':'str',
                                'text':subject,
                                'fmt':{}
                                },
                            'TITLE':{
                                'type':'str',
                                'text':title,
                                'fmt':{}
                                },
                            'TYPE':{
                                'type':'str',
                                'text':template_type,
                                'fmt':{}
                                },
                            'EAR':{
                                'type':'str',
                                'text': ear_txt,
                                'fmt':{}
                                },
                            'CI_ID':{
                                'type':'str',
                                'text':ci_identification,
                                'fmt':{}
                                },
                            'REFERENCE':{
                                'type':'str',
                                'text':self.reference,
                                'fmt':{}
                                },
                            'ISSUE':{
                                'type':'str',
                                'text':self.revision,
                                'fmt':{}
                                },
                            'ITEM':{
                                'type':'str',
                                'text':system_name,
                                'fmt':{}
                                },
                            'ITEM_DESCRIPTION':{
                                'type':'str',
                                'text':item_description,
                                'fmt':{}
                                },
                            'DATE':{
                                'type':'str',
                                'text':time.strftime("%d %b %Y", time.gmtime()),
                                'fmt':{}
                                },
                            'WRITER':{
                                'type':'str',
                                'text':self.author,
                                'fmt':{}
                                },
                            'PSAC':{
                                'type':'str',
                                'text':self.getDocRef(self.item,"PSAC"),
                                'fmt':{}
                                },
                            'SDP':{
                                'type':'str',
                                'text':self.getDocRef(self.item,"SDP"),
                                'fmt':{}
                                },
                            'SCMP':{
                                'type':'str',
                                'text':self.getDocRef(self.item,"SCMP"),
                                'fmt':{}
                                },
                            'SVP':{
                                'type':'str',
                                'text':self.getDocRef(self.item,"SVP"),
                                'fmt':{}
                                },
                            'TABLELISTMODIFS':{
                                'type':'tab',
                                'text':table_modifs,
                                'fmt':{
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
                                            }
                                        }
                                    }
                                }
                            }
                # Loop to replace tags
                for key, value in list_tags.items():
                    docbody = self.replaceTag(docbody, key, (value['type'], value['text']),value['fmt'] )

##                docbody,relationships = self.replaceTag(docbody, 'IMAGE', ('img', 'HW.png') )
##                wordrelationships = docx.wordrelationships(relationships)
                # Cleaning
                docbody = docx.clean(docbody)
        except KeyError as exception:
            print >>sys.stderr, "Execution failed:", exception

        # ------------------------------
        # Save output
        # ------------------------------

        # Prepare output file
        self.docx_filename = self.aircraft + "_" + self.item + "_" + template_type + "_" + self.reference + ".docx"
        try:
            outfile = zipfile.ZipFile(self.docx_filename,mode='w',compression=zipfile.ZIP_DEFLATED)

##            # Copy relationships
##            actlist.append(('word/_rels/document.xml.rels', '/w:document/w:wordrelationships'))
##            # Serialize our trees into out zip file
##            treesandfiles = {wordrelationships: 'word/_rels/document.xml.rels'}
##            for tree in treesandfiles:
##                treestring = etree.tostring(tree, pretty_print=True)
##                outfile.writestr(treesandfiles[tree], treestring)

            # Copy image
            image_name = self.get_image(self.aircraft)
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
            self.docx_filename = False

        template.close()
        return self.docx_filename,exception

    def createCID(self,tableau_items,tableau_source,cid_type):
        '''
        This function creates the document based on the template
        - open template docx
        - get sections of the template
        - replace tag in document
        - create zip
         . copy unmodified section
         . copy modified section

        '''
        global list_projects
        # Get config
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        try:
            # get template name

            template_dir = join(os.path.dirname("."), 'template')
            template_name = config_parser.get("Template",cid_type)
            self.template_name = join(template_dir, template_name)
            self.template_type = cid_type
            self.type_doc = config_parser.get("Objects","type_doc").split(",")
            self.type_src = config_parser.get("Objects","type_src").split(",")
        except IOError as exception:
            print "Execution failed:", exception

        item_description = self.getItemDescription(self.item)
        ci_identification = self.get_ci_identification(self.item)
        # Load the original template
        try:
            template = zipfile.ZipFile(self.template_name,mode='r')
        except IOError as exception:
            print "Execution failed:", exception

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
                xmlcontent = template.read(curact[0])
                outdoc[curact[0]] = etree.fromstring(xmlcontent)

                # Will work on body
                docbody = outdoc[curact[0]].xpath(curact[1], namespaces=docx.nsprefixes)[0]

                # Replace some tags
                title = self.item + " " + self.template_type
                subject = self.item + " " + self.getTypeDocDescription(self.item)
                project_text = "The project is not defined"
                if self.project != "":
                    if len(list_projects) in (0,1) :
                        project_text = "The project is " + self.project
                    else:
                        text = "The projects are: "
                        for project in list_projects:
                            text =  text + project + ", "
                        # remove last comma
                        project_text = text[0:-2]

                if self.release == "":
                    self.release = "not defined"

                if self.baseline == "":
                    self.baseline = "not defined"

                if self.author == "":
                    self.author = "Nobody"

                colw = [1000,2300,200,1000,500,500,500] # 5000 = 100%

                list_tags = {
                            'SUBJECT':{
                                'type':'str',
                                'text':subject,
                                'fmt':{}
                                },
                            'TITLE':{
                                'type':'str',
                                'text':title,
                                'fmt':{}
                                },
                            'CI_ID':{
                                'type':'str',
                                'text':ci_identification,
                                'fmt':{}
                                },
                            'REFERENCE':{
                                'type':'str',
                                'text':self.reference,
                                'fmt':{}
                                },
                            'ISSUE':{
                                'type':'str',
                                'text':self.revision,
                                'fmt':{}
                                },
                            'ITEM':{
                                'type':'str',
                                'text':self.item,
                                'fmt':{}
                                },
                            'ITEM_DESCRIPTION':{
                                'type':'str',
                                'text':item_description,
                                'fmt':{}
                                },
                            'DATE':{
                                'type':'str',
                                'text':time.strftime("%d %b %Y", time.gmtime()),
                                'fmt':{}
                                },
                            'PROJECT':{
                                'type':'str',
                                'text':project_text,
                                'fmt':{}
                                },
                            'RELEASE':{
                                'type':'str',
                                'text':self.release,
                                'fmt':{}
                                },
                            'BASELINE':{
                                'type':'str',
                                'text':self.baseline,
                                'fmt':{}
                                },
                            'WRITER':{
                                'type':'str',
                                'text':self.author,
                                'fmt':{}
                                },
                            'TABLEITEMS':{
                                'type':'tab',
                                'text':tableau_items,
                                'fmt':{
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
                                            }
                                        }
                                    }
                                },
                            'TABLESOURCE':{
                                'type':'tab',
                                'text':tableau_source,
                                'fmt':{
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
                                            }
                                        }
                                    }
                                },
                            'TABLEPRS':{
                                'type':'tab',
                                'text':self.tableau_pr,
                                'fmt':{
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
                                            }
                                        }
                                    }
                                }
                            }
##                docbody = self.replaceTag(docbody, 'TABLESOURCE', ('tab', tableau_source),
##                            {
##                                    'heading': True,
##                                    'colw': colw,
##                                    'cwunit': 'pct',
##                                    'tblw': 5000,
##                                    'twunit': 'pct',
##                                    'borders': {
##                                        'all': {
##                                            'color': 'auto',
##                                            'space': 0,
##                                            'sz': 6,
##                                            'val': 'single',
##                                            }
##                                        }
##                                    })
                # Loop to replace tags
                for key, value in list_tags.items():
                    print value
                    docbody = self.replaceTag(docbody, key, (value['type'], value['text']), value['fmt'] )

##                docbody,relationships = self.replaceTag(docbody, 'IMAGE', ('img', 'HW.png') )
##                wordrelationships = docx.wordrelationships(relationships)
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

##            # Copy relationships
##            actlist.append(('word/_rels/document.xml.rels', '/w:document/w:wordrelationships'))
##            # Serialize our trees into out zip file
##            treesandfiles = {wordrelationships: 'word/_rels/document.xml.rels'}
##            for tree in treesandfiles:
##                treestring = etree.tostring(tree, pretty_print=True)
##                outfile.writestr(treesandfiles[tree], treestring)

            # Copy image
            image_name = self.get_image(self.aircraft)
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

    def stopSession(self):
        global session_started
        if session_started:
            stdout,stderr = self.ccm_query('stop','Stop Synergy session')

    def storeSelection(self,project,item,release,baseline):
        '''
        Store selection in SQLite database
         -project
         -release
         -baseline
        '''
        try:
            now = datetime.datetime.now()
            if baseline == "All":
                baseline = ""
            if release == "All":
                release = ""
            if project == "All":
                project = ""
            con = lite.connect('docid.db3', isolation_level=None)
            cur = con.cursor()
##            cur.execute("DROP TABLE IF EXISTS last_query")
            cur.execute("CREATE TABLE IF NOT EXISTS last_query (id INTEGER PRIMARY KEY, reference TEXT, revision TEXT ,database TEXT, project TEXT, item TEXT, release TEXT, baseline TEXT, input_date timestamp)")
            cur.execute("SELECT id FROM last_query WHERE item LIKE '" + item + "' LIMIT 1")
            data = cur.fetchone()
            if data != None:
                id = data[0]
                cur.execute("UPDATE last_query SET database=?,reference=?,revision=?,project=?,release=?,baseline=?,input_date=? WHERE id= ?",(self.database,self.reference,self.revision,project,release,baseline,now,id))
            else:
                cur.execute("INSERT INTO last_query(database,reference,revision,project,item,release,baseline,input_date) VALUES(?,?,?,?,?,?,?,?)",(self.database,self.reference,self.revision,project,item,release,baseline,now))
            # Keep only the 4 last input
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
        global interface
        """
        Handle all the messages currently in the queue (if any).
         - BUILD_DOCX
          . Store selection
         - START_SESSION
         - GET_BASELINES
         - GET_RELEASES
         - GET_PROJECTS

        """
        while self.queue.qsize():
            try:
                # Check contents of message
                action = self.queue.get(0)
                print action
                if action == "BUILD_CID":
                    data = self.queue.get(1)
                    author = data[0]
                    self.reference = data[1]
                    self.revision = data[2]
                    release = data[3]
                    project = data[4]
                    baseline = data[5]
                    object_released = data[6]
                    object_integrate = data[7]
                    cid_type = data[8]

                    interface.output_txt.delete(1.0, END)
                    #store information in sqlite db
                    self.storeSelection(project,self.item,release,baseline)
                    self.build_doc_thread = threading.Thread(None,generateCID,None,(author,self.reference,self.revision,release,self.aircraft,self.item,project,baseline,object_released,object_integrate,cid_type))
                    self.build_doc_thread.start()
                    # Make a query to synergy

                if action == "BUILD_SQAP":
                    data = self.queue.get(1)
                    author = data[0]
                    self.reference = data[1]
                    self.revision = data[2]

                    self.build_doc_thread = threading.Thread(None,generateSQAP,None,(author,self.reference,self.revision,self.aircraft,self.item))
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
##                    if session_started:
##                        interface.button_select.configure(state=DISABLED)
##                        interface.button_find_baselines.configure(state=DISABLED)
##                        interface.button_find_releases.configure(state=DISABLED)
##                        interface.button_find_projects.configure(state=DISABLED)

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

                elif action == "READ_STATUS":
                    print "set_status thread"
                    self.set_status_thread = threading.Thread(None,getSessionStatus,None)
                    self.set_status_thread.start()

                else:
                    pass
            except Queue.Empty:
                pass

    def periodicCall(self):
        """
        Check every 1000 ms if there is something new in the queue.
        """
##        print time.strftime("%H:%M:%S", time.gmtime())
        self.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(1000, self.periodicCall)

    def run(self):
        # sleep to enables the GUI to finish its setting
        import time
        time.sleep(2)
        self.periodicCall()

    def stop(self):
        self.terminated = True

class Login (Frame,Tool):
    def __init__(self, fenetre, **kwargs):
        '''
        init login class
             - create GUI
             - invoke sqlite query SELECT name FROM systems ORDER BY systems.name ASC
               to populate system listbox
        '''
        global background
        global foreground
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
        Frame.__init__(self, fenetre, width=768, height=576,relief =GROOVE, bg = background,**kwargs)
        self.pack(fill=BOTH)
        self.listbox_txt = Label(self, text='Systems:', fg=foreground,bg = background)
        self.listbox_frame = Frame(self, bg = '#80c0c0')
        self.vbar_1 = vbar_1 = Scrollbar(self.listbox_frame, name="vbar_1")
        self.vbar_1.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(self.listbox_frame,height=6,width=entry_size,exportselection=0,yscrollcommand=vbar_1.set)
        self.listbox.pack()
        self.populate_listbox('SELECT name FROM systems ORDER BY systems.name ASC',self.listbox,"None")
        # Tie listbox and scrollbar together
        vbar_1["command"] = self.listbox.yview
        # Bind events to the list box
        self.listbox.bind("<ButtonRelease-1>", self.select_system)
        self.listbox.bind("<Key-Up>", self.up_event_1)
        self.listbox.bind("<Key-Down>", self.down_event_1)

         # Create and pack the dropdown ComboBox.
##        colours = ('cornsilk1', 'snow1', 'seashell1', 'antiquewhite1',
##                'bisque1', 'peachpuff1', 'navajowhite1', 'lemonchiffon1',
##                'ivory1', 'honeydew1', 'lavenderblush1', 'mistyrose1')
##        dropdown = Pmw.ComboBox(fenetre,
##                label_text = 'Dropdown ComboBox:',
##                labelpos = 'nw',
##                selectioncommand = self.changeColour,
##                scrolledlist_items = colours,
##        )
##        dropdown.pack(side = 'left', anchor = 'n',
##                fill = 'x', expand = 1, padx = 8, pady = 8)

        self.items_txt = Label(self, text='Items:', fg=foreground,bg = background)
        self.itemslistbox_frame = Frame(self, bg = '#80c0c0')
        self.vbar_2 = vbar_2 = Scrollbar(self.itemslistbox_frame , name="vbar_2")
        self.vbar_2.pack(side=RIGHT, fill=Y)
        self.itemslistbox = Listbox(self.itemslistbox_frame ,height=3,width=entry_size,exportselection=0,yscrollcommand=vbar_2.set)
        self.itemslistbox.pack()
        self.itemslistbox.insert(END, "All")
        vbar_2["command"] = self.itemslistbox.yview
        self.itemslistbox.bind("<ButtonRelease-1>", self.select_item)
##        self.itemslistbox.bind("<Double-ButtonRelease-1>", self.double_click_item)
        self.itemslistbox.bind("<Key-Up>", self.up_event_2)
        self.itemslistbox.bind("<Key-Down>", self.down_event_2)

        # Login
        row_index = 1
        self.login_txt = Label(self, text='Login:', fg=foreground,bg = background)
        self.login_entry = Entry(self, state=NORMAL,width=entry_size)
        self.login_entry.insert(END, self.login)
        self.login_txt.grid(row =row_index,sticky='ES')
        self.login_entry.grid(row =row_index, column =1,sticky='E')

        #Drawing
        self.can = Canvas(self, width =64, height =256, bg =background,highlightthickness=0)
        bitmap = PhotoImage(file="img/doc.gif")
        self.can.create_image(32,32,image =bitmap)
        self.can.bitmap = bitmap
        self.can.grid(row =0, column =3,rowspan =6, padx =5, pady =5,sticky='W')

        # Password
        row_index = row_index + 1
        self.password_txt = Label(self, text='Password:', fg=foreground,bg = background)
        self.password_entry = Entry(self, state=NORMAL,width=entry_size)
        self.password_entry.configure(show='*')
        self.password_entry.insert(END, self.password)
        self.password_txt.grid(row =row_index,sticky='E')
        self.password_entry.grid(row =row_index, column =1,sticky='E')

        # Systems
        row_index = row_index + 1
        self.listbox_txt.grid(row =row_index,sticky='E')
        self.listbox_frame.grid(row =row_index, column =1,sticky='E')
##        self.vbar_1.grid(row =row_index, column =2,sticky='W')

        # Items
        row_index = row_index + 1
        self.items_txt.grid(row =row_index,sticky='E')
        self.itemslistbox_frame.grid(row =row_index, column =1,sticky='E')
##        self.vbar_2.grid(row =row_index, column =2,sticky='W')

        # Build & Quit
        row_index = row_index + 1
        self.button_select = Button(self, text='OK', state=DISABLED, command = self.click_select)
        self.button_quit = Button(self, text='Quit', command = self.click_quit)
        self.button_select.grid(row =row_index, column =1,sticky='E')
        self.button_quit.grid(row =row_index, column =2,sticky='W')

    def changeColour(self, colour):
        print 'Colour: ' + colour
        self.listbox_txt.configure(background = colour)

    def select_item(self, event):
        ''' select item and enable OK button to goto the next popup window'''
        item_id = self.itemslistbox.curselection()
        self.item_id = item_id
        self.button_select.configure(state=NORMAL)

    def select_system(self, event):
        # populate items listbox
        system_id = self.listbox.curselection()
        if system_id != () and '0' not in system_id:
            system = self.listbox.get(system_id)
            # Populate items list box
            query = 'SELECT items.name FROM items LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE systems.name LIKE \'' + system + '\' ORDER BY items.name ASC'
            self.populate_listbox(query,self.itemslistbox,"All")
            self.listbox.activate(system_id)
        else:
            self.itemslistbox.delete(0, END)
    def press_ctrl_h(self,event):
        config= "httpd_ece.conf"
        self.apache_start(config)
        pass
    def press_ctrl_b(self,event):
        '''
        Bypass login. No message START_SESSION sent.
        '''
        global login_success

        login_success = True
        self.destroy()
        login_window.destroy()

    def click_select(self):
        global login_success
        global project_item
        if self.item_id != () and '0' not in self.item_id:
            item = self.itemslistbox.get(self.item_id)
            project_item = item
            self.database,self.aircraft = self.get_database(item)
##            self.database = database[0]
##            self.aircraft = aircraft[1]
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
    def __init__(self, notebook, **kwargs):
        global background
        global foreground
        global queue
        global entry_size

        self.queue = queue
        # read config file
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        self.login = config_parser.get("User","login")
        self.password = config_parser.get("User","password")
        self.author = config_parser.get("User","author")

        self.reference = "" #"ET1234-V"
        self.revision = "" #"1D1"
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
        # Add pages to the notebook.
        page_create_cid = notebook.add('Create CID')
        page_create_sqap = notebook.add('Create SQAP')
        page_create_checklist = notebook.add('Create checklist')
        page_create_ccb = notebook.add('Create CCB minutes')
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, page_create_cid, width=768, height=576,relief =GROOVE, bg = background,**kwargs)
        self.pack(fill=BOTH)

        # Type of CID
        row_index = 1
        self.cid_type_txt = Label(self, text='CID type:', fg=foreground,bg = background)

        self.cid_var_type = StringVar()
        self.radiobutton_sci = Radiobutton(self, indicatoron=0,width = 6,text="SCI", variable=self.cid_var_type,value="SCI",fg=foreground,bg = background,command=self.cid_type)
        self.radiobutton_hci = Radiobutton(self, indicatoron=0,width = 6,text="HCI", variable=self.cid_var_type,value="HCI",fg=foreground,bg = background,command=self.cid_type)
        self.radiobutton_cid = Radiobutton(self, indicatoron=0,width = 6,text="CID", variable=self.cid_var_type,value="CID",fg=foreground,bg = background,command=self.cid_type)
        self.cid_var_type.set("SCI") # initialize

        self.cid_type_txt.grid(row =row_index,sticky='E')
        self.radiobutton_sci.grid(row =row_index, column =1, padx=10,sticky='W')
        self.radiobutton_hci.grid(row =row_index, column =1, padx=58,sticky='W')
        self.radiobutton_cid.grid(row =row_index, column =1, padx=31,sticky='E')

        # Author
        row_index = row_index + 1
        self.author_txt = Label(self, text='Author:', fg=foreground,bg = background)
        self.author_txt.grid(row =row_index,sticky='E')
        self.author_entry = Entry(self, state=NORMAL,width=entry_size)
        self.author_entry.insert(END, self.author)
        self.author_entry.grid(row = row_index, column =1,sticky='E')

        # Description of the selected project
        self.project_description = Label(self, fg=foreground,bg = background)
        self.project_description.grid(row =row_index,column =4,sticky='E')

        # Image
        self.can = Canvas(self, width =240, height =116, bg =background,highlightthickness=0)
        bitmap = PhotoImage(file="img/earhart12_240x116.gif")
##        bitmap = BitmapImage(file="zodiac.xbm")
        self.can.create_image(120,58,image =bitmap)
        self.can.bitmap = bitmap
        self.can.grid(row =row_index+1, column =4,rowspan =5, padx =20, pady =5,sticky='W')

        # Reference
        row_index = row_index + 1
        self.reference_txt = Label(self, text='Reference:', fg=foreground,bg = background)
        self.reference_entry = Entry(self, state=NORMAL,width=entry_size)
        self.reference_entry.insert(END, self.reference)
        self.reference_txt.grid(row =row_index,sticky='E')
        self.reference_entry.grid(row = row_index, column =1,sticky='E')

        # Revision
        row_index = row_index + 1
        self.revision_txt = Label(self, text='Issue:', fg=foreground,bg = background)
        self.revision_entry = Entry(self, state=NORMAL,width=entry_size)
        self.revision_entry.insert(END, self.revision)
        self.revision_txt.grid(row =row_index,sticky='E')
        self.revision_entry.grid(row =row_index, column =1,sticky='E')

        # Release
        row_index = row_index + 1
        self.release_txt = Label(self, text='Release:', fg=foreground,bg = background)
        self.releaselistbox = Listbox(self,height=3,width=entry_size,exportselection=0)
        self.releaselistbox.insert(END, "All")
        self.vbar_3 = vbar_3 = Scrollbar(self, name="vbar_3")
        vbar_3["command"] = self.releaselistbox.yview
        self.releaselistbox["yscrollcommand"] = vbar_3.set
        self.releaselistbox.bind("<ButtonRelease-1>", self.select_release)
        self.releaselistbox.bind("<Key-Up>", self.up_event_3)
        self.releaselistbox.bind("<Key-Down>", self.down_event_3)
        self.button_find_releases = Button(self, text='Refresh', state=DISABLED, command = self.find_releases)
        self.release_txt.grid(row =row_index,sticky='E')
        self.releaselistbox.grid(row =row_index, column =1,sticky='E')
        self.vbar_3.grid(row =row_index, column =2,sticky='W')
        self.button_find_releases.grid(row =row_index, column =2,sticky='W',padx=20)

        # Baseline
        self.baseline_txt = Label(self, text='Baseline:', fg=foreground,bg = background)
        self.baselinelistbox = Listbox(self,height=3,width=entry_size,exportselection=0)
        self.vbar_5 = vbar_5 = Scrollbar(self, name="vbar_5")
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
        self.project_txt = Label(self, text='Project:', fg=foreground,bg = background)
        self.projectlistbox = Listbox(self,height=3,width=entry_size,exportselection=0)
        self.vbar_4 = vbar_4 = Scrollbar(self, name="vbar_4")
        vbar_4["command"] = self.projectlistbox.yview
        self.projectlistbox["yscrollcommand"] = vbar_4.set
        self.projectlistbox.bind("<ButtonRelease-1>", self.select_project)
        self.projectlistbox.bind("<Key-Up>", self.up_event_4)
        self.projectlistbox.bind("<Key-Down>", self.down_event_4)
        self.button_find_projects = Button(self, text='Refresh', state=DISABLED, command = self.find_projects)
        self.project_txt.grid(row =row_index,sticky='E')
        self.projectlistbox.grid(row =row_index, column =1,sticky='E')
        self.vbar_4.grid(row =row_index, column =2,sticky='W')
        self.button_find_projects.grid(row =row_index, column =2,sticky='W',padx=20)

        # Build
        row_index = row_index + 1
        self.button_select = Button(self, text='Build', state=DISABLED, command = self.click_build_cid)
        self.button_select.grid(row =row_index, column =1,pady=5,sticky='E')

        # Check buttons
        row_index = row_index + 1
        self.objects_txt = Label(self, text='Objects:', fg=foreground,bg = background)
##        group = Pmw.Group(fenetre, tag_text = 'Objects status')
##        group.grid(row =row_index,sticky='E')
        self.status_released = IntVar()
        self.check_button_status_released = Checkbutton(self, text="Released", variable=self.status_released,fg=foreground,bg = background,command=self.cb_released)
        self.status_integrate = IntVar()
        self.check_button_status_integrate = Checkbutton(self, text="Integrate", variable=self.status_integrate,fg=foreground,bg = background,command=self.cb_integrate)

        self.objects_txt.grid(row =row_index,sticky='E')
        self.check_button_status_released.grid(row =row_index, column =1, padx=10,sticky='W')
        self.check_button_status_integrate.grid(row =row_index, column =1,sticky='E')

        # Output
        output_frame = Frame(page_create_cid, bg = '#80c0c0')
        output_frame.pack()
        self.output_label = Label(output_frame, text='Output:',fg=foreground,bg = background)
        self.output_label.pack(fill=X);
        self.output_txt = Text(output_frame,wrap=WORD, width = 100, height = 10)
        self.output_txt.pack()

##        self.output_label = Label(self, text='Output:',fg=foreground,bg = background)
##        self.output_txt = Text(self, width = 72, height = 12)
##        row_index = row_index + 1
##        self.output_label.grid(row =row_index,sticky='E')
##        row_index = row_index + 1
##        self.output_txt.grid(row =row_index ,columnspan =5, pady =20,padx = 10)

        # Build SQAP folder in the notebook
        self.build_sqap_folder(page_create_sqap,**kwargs)

        # Build checklist folder in the notebook
        self.build_checklist_folder(page_create_checklist,**kwargs)

    def build_checklist_folder(self,page,**kwargs):
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, page, width=768, height=576,relief =GROOVE, bg = background,**kwargs)
        self.pack(fill=BOTH)
        # Type of CID
        row_index = 1
        self.review_type_txt = Label(self, text='Review type:', fg=foreground,bg = background)
        review_list = self.getReviewList()
##        print review_list
        self.var_review_type = IntVar()
        for id,text in review_list:
            b = Radiobutton(self, indicatoron=0,width = 20, text=text,variable=self.var_review_type, value=id)
            b.pack(anchor=W)
##        self.radiobutton_sci = Radiobutton(self, indicatoron=0,width = 6,text="SCI", variable=self.cid_var_type,value="SCI",fg=foreground,bg = background,command=self.cid_type)
##        self.radiobutton_hci = Radiobutton(self, indicatoron=0,width = 6,text="HCI", variable=self.cid_var_type,value="HCI",fg=foreground,bg = background,command=self.cid_type)
##        self.radiobutton_cid = Radiobutton(self, indicatoron=0,width = 6,text="CID", variable=self.cid_var_type,value="CID",fg=foreground,bg = background,command=self.cid_type)
        self.var_review_type.set(1) # initialize

##        self.review_type_txt.grid(row =row_index,sticky='E')
##        self.radiobutton_sci.grid(row =row_index, column =1, padx=10,sticky='W')
##        self.radiobutton_hci.grid(row =row_index, column =1, padx=58,sticky='W')
##        self.radiobutton_cid.grid(row =row_index, column =1, padx=31,sticky='E')

    def build_sqap_folder(self,page,**kwargs):
        global entry_size
        global project_item

        self.item = project_item
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, page, width=768, height=576,relief =GROOVE, bg = background,**kwargs)
        self.pack(fill=BOTH)

        row_index = 1
        # Description of the selected project
        self.project_description_pg2 = Label(self, text="Project:",fg=foreground,bg = background)
        self.project_description_pg2.grid(row =row_index,sticky='E')
        self.project_description_entry_pg2 = Entry(self,width=entry_size)
        self.project_description_entry_pg2.insert(END, self.getItemDescription(project_item))
        self.project_description_entry_pg2.grid(row =row_index,column =1,sticky='E')

        # Author
        row_index = row_index + 1
        self.author_txt_pg2 = Label(self, text='Author:', fg=foreground,bg = background)
        self.author_txt_pg2.grid(row =row_index,sticky='E')
        self.author_entry_pg2 = Entry(self, state=NORMAL,width=entry_size)
        self.author_entry_pg2.insert(END, self.author)
        self.author_entry_pg2.grid(row = row_index, column =1,sticky='E')

        reference,revision,status = self.getDocInfo(project_item)
        # Reference
        row_index = row_index + 1
        self.reference_txt_pg2 = Label(self, text='Reference:', fg=foreground,bg = background)
        self.reference_entry_pg2 = Entry(self, state=NORMAL,width=entry_size)
        self.reference_entry_pg2.insert(END, reference)
        self.reference_txt_pg2.grid(row =row_index,sticky='E')
        self.reference_entry_pg2.grid(row = row_index, column =1,sticky='E')

        # Revision
        row_index = row_index + 1
        self.revision_txt_pg2 = Label(self, text='Issue:', fg=foreground,bg = background)
        self.revision_entry_pg2 = Entry(self, state=NORMAL,width=entry_size)
        self.revision_entry_pg2.insert(END, revision)
        self.revision_txt_pg2.grid(row =row_index,sticky='E')
        self.revision_entry_pg2.grid(row =row_index, column =1,sticky='E')

        # Status
        row_index = row_index + 1
        self.status_txt = Label(self, text='Status:', fg=foreground,bg = background)
        self.status_entry = Entry(self, state=NORMAL,width=entry_size)
        self.status_entry.insert(END, status)
        self.status_txt.grid(row =row_index,sticky='E')
        self.status_entry.grid(row =row_index, column =1,sticky='E')

        # Build
        row_index = row_index + 1
        self.button_select_pg2 = Button(self, text='Build', state=NORMAL, command = self.click_build_sqap)
        self.button_select_pg2.grid(row =row_index, column =1,pady=5,sticky='E')

        # Modifications log

        modification_log_text = self.getLastModificationLog(reference)
        modif_log_frame = Frame(page, bg = '#80c0c0')
        modif_log_frame.pack()
        scrollbar = Scrollbar(modif_log_frame)
        page.bind('<MouseWheel>', self.scrollEvent)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.modif_log_label = Label(modif_log_frame, text='Modifications log:',fg=foreground,bg = background)
        self.modif_log_label.pack(fill=X);
        self.modif_log = Text(modif_log_frame,wrap=WORD, yscrollcommand=scrollbar.set, width = 100, height = 10)
        self.modif_log.pack()
        scrollbar.config(command=self.modif_log.yview)
        self.modif_log.insert(END, modification_log_text)
        output_frame = Frame(page, bg = '#80c0c0')
        output_frame.pack()
        self.output_label_pg2 = Label(output_frame, text='Output:',fg=foreground,bg = background)
        self.output_label_pg2.pack(fill=X);
        self.output_txt_pg2 = Text(output_frame,wrap=WORD, yscrollcommand=scrollbar.set, width = 100, height = 10)
        self.output_txt_pg2.pack()

        # Output
##        row_index = row_index + 1
##        self.output_label_pg2 = Label(self, text='Output:',fg=foreground,bg = background)
##        self.output_label_pg2.grid(row =row_index,sticky='E')
##
##        row_index = row_index + 1
##        self.output_txt_pg2 = Text(self, width = 72, height = 12)
##        self.output_txt_pg2.grid(row =row_index ,columnspan =5, pady =20,padx = 10)

    def press_ctrl_t(self,event):
        print "TEST CTRL + T"
        self.queue.put("READ_STATUS") # order to read session status

    def cid_type(self):
        print "CID type is '{:s}'".format(self.cid_var_type.get())

    def cb_released(self):
        print "variable is", self.status_released.get()

    def cb_integrate(self):
        print "variable is", self.status_integrate.get()

    def __del__(self):
        # kill threads
        pass

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

    def click_build_cid(self):
        '''
        Function which put
        - author
        - reference
        - revision
        - release
        - project
        - baseline
        - status_released
        - status_integrate

        into the queue
        called when the user press the Build button
        '''
        # Get author
        author = self.author
        # Get reference
        reference = self.reference_entry.get()
        if reference == "":
            reference = "TBD"
        # Get revision
        revision = self.revision_entry.get()
        if revision == "":
            revision = "TBD"
        # Get baseline
        baseline = self.baseline
        # Get release
        release = self.release
        # Get project
        project = self.project
        # Get aircraft
##            aircraft = self.aircraft
        # Get item

        # Get project and database listbox information
        self.queue.put("BUILD_CID") # order to build docx
        self.queue.put([author,reference,revision,self.release,self.project,self.baseline,self.status_released.get(),self.status_integrate.get(),self.cid_var_type.get()])

    def click_build_sqap(self):
        '''
        Function which put
        - author
        - reference
        - revision

        into the queue
        called when the user press the Build button
        '''
        # Get author
        author = self.author
        # Get reference
        reference = self.reference_entry_pg2.get()
        if reference == "":
            reference = "TBD"
        # Get revision
        revision = self.revision_entry_pg2.get()
        if revision == "":
            revision = "TBD"

        self.queue.put("BUILD_SQAP") # order to build docx
        self.queue.put([author,reference,revision])

def destroy_app():
    global thread_build_docx
    thread_build_docx.stop()
    print "CROSS MARK PUSHED"

if __name__ == '__main__':
    try:
        # Begin DoCID
        session_started = False
        project_item = ""
        list_projects = []
        login_success = False
        # Verify if the database SQLite exists
        try:
            with open('docid.db3'):
                pass
        except IOError:
            print 'SQLite database does not exists.'
            tool = Tool()
            tool.sqlite_create()
        verrou = threading.Lock()

        # Create the queue
        queue = Queue.Queue()

        login_window = Tk()
        Pmw.initialise(login_window)
        login_window.iconbitmap("qams.ico")
        login_window.title("Login")
        login_window.resizable(False,False)

        interface_login = Login(login_window)
        # create a toplevel menu
        mainmenu = Menu(login_window)
        menubar = Menu(mainmenu)
        menubar.add_command(label="Help", command=interface_login.help)
        menubar.add_separator()
        menubar.add_command(label="Quit", command=interface_login.click_quit)
        mainmenu.add_cascade(label = "Home", menu = menubar)
        mainmenu.add_command(label="About", command=interface_login.about)
        # Bind control keys
        mainmenu.bind_all("<Control-b>", interface_login.press_ctrl_b)
        mainmenu.bind_all("<Control-h>", interface_login.press_ctrl_h)

        # display the menu
        login_window.configure(menu = mainmenu)
        interface_login.mainloop()

        if login_success:
    ##        sys.exit()
            fenetre = Tk()
            Pmw.initialise(fenetre)
            fenetre.iconbitmap("qams.ico")
            fenetre.title("Create Configuration Index Document")
            fenetre.resizable(False,False)
            #notebook
            notebook = Pmw.NoteBook(fenetre)
            notebook.pack(fill = 'both', expand = 1, padx = 10, pady = 10)
####            notebook.configure('canvasSize'={768,640})
##            # Add pages to the notebook.
##            page_create_cid = notebook.add('Create CID')
##            page_create_sqap = notebook.add('Create SQAP')
##            page_create_checklist = notebook.add('Create checklist')
##            page_create_ccb = notebook.add('Create CCB minutes')

            interface = Interface(notebook)
            interface.button_quit = Button(fenetre, text='Quit', command = interface.click_quit)
            interface.button_quit.pack(side=RIGHT)
##            self.button_quit.grid(row =row_index, column =2,pady=5,sticky='W')
            notebook.tab('Create CID').focus_set()
            # Important pour que le notebook ai la taille du frame
            notebook.setnaturalsize()
            # create a toplevel menu
            mainmenu = Menu(fenetre)
            menubar = Menu(mainmenu)
            menubar.add_command(label="Create CCB minutes", command=interface.ccb_minutes)
            menubar.add_separator()
            menubar.add_command(label="Create Plan Review minutes", command=interface.plan_review_minutes)
            menubar.add_command(label="Create Specification Review minutes", command=interface.spec_review_minutes)
            menubar.add_separator()
            menubar.add_command(label="Quit", command=interface.click_quit)
            mainmenu.add_cascade(label = "Home", menu = menubar)
            mainmenu.add_command(label="About", command=interface.about)
            mainmenu.add_command(label="Help", command=interface.help)
            # Bind control keys
            mainmenu.bind_all("<Control-t>", interface.press_ctrl_t)
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
