#!/usr/bin/env python 2.7.3
## -*- coding: latin-1 -*-
# -*- coding: utf-8 -*-
"""
This file generates a SCI, HCMR and CID with a format .docx (Word 2007) based on a specific template.
1.0.0: [8th of August 2013 - O. Appéré]  First major revision.
1.1.0: [16th of August 2013 - O. Appéré] Add system's name before item's name in title of CID
                                         Add OLD parameter in config file for old CR workflow
                                         Add time in CCB minutes filename
                                         Add system's name in filename and Subject/Object of CCB minute
                                         For CCB minutes generation, correction in calling of createCrStatus
                                         Add CCB type "All"
                                         Remove log column from the implemented CR table
                                         Add log table information
                                         Remove prefix before Change status before listing CRs into Word document
                                         Add sw_src and hw_src option in config file (option type_src is obsolete but still managed)
1.2.0: [26th of September 2013 - O. Appéré]
                                         Manage no such file or directory error
                                         Correct List CR for spectific item.
                                         Replace HCMR by HCMR
                                         Add th possibilty to select one or several baselines ofr HCMR generation
                                         Main window is no more resizable
                                         Remove <void> in items list
1.2.1: [27th of September 2013 - O. Appéré]
                                         Minor modifications:
                                            - Enhancement of hyperlink toward word document created
                                            - Scrollbar is set to bottom automatically
1.3.0: [30th of September 2013 - O. Appéré]
                                         Add EXCR listing with specific workflow
                                         Add file log for CR listing
                                         CR state selection is disabled if all CR type are selected.
1.3.1: [1st of October 2013 - O. Appéré]
                                         Add a "Clear" button for baseline selection.
                                         Add a "Clear" button for release selection.
1.4.0: [8th of October 2013 - O. Appéré]
                                         Remove bug when listbox is empty and user click on it.
                                         Add a checkbutton to select wether or not the log for CR is displayed.
                                         Splt CR status to display a nicer output csv file when "List CR" button is clicked
                                         Add selection attribute in CR query
                                         Add A/C standards customization in config file to append release list. Comments in csv file skipped.
                                         Add " Reload PN csv file" in menu "Home"
1.5.0: [30th of October 2013 - O. Appéré]
                                         Add software part number and make a link between part number, release and baseline.
                                         Add a listbox for standard and part number.
                                         Modify folder "Create CCB Minutes" by "Change Requests"
                                         Modify folder "Create CID" by "Create configuration index document"
                                         Add " Reload config file" in menu "Home"
                                         Add "Save","Restore" function for CID generation
                                         Add automatic start and default template selection
                                         Split CR status like PLDCR_In_Analysis => PLDCR, In_Analysis
                                         Add "Clear selection" button for project.
                                         Add Baselne and Project display.
                                         Add "Show baseline command"
                                         Add frame baseline in Synergy command folder
                                         Make a correction when only a baseline is selected for "Generate" and "List items" commands
                                         Add "tasks" and  "CR" in source list
1.5.1: [10th of December 2013 - O. Appéré]
                                        Add list of items for project also
                                        Add task status
1.5.2: [10th of December 2013 - O. Appéré]
    Correction errors:
    1)
        File "docid.py", line 3731, in __getCR
        AttributeError: 'ThreadQuery' object has no attribute 'getTypeWorkflow'
        Move getTypeWorkflow from BuildDOc class in Interface class
    2)
        File "docid.py", line 2199, in getStatusAnalysis
        AttributeError: BuildDoc instance has no attribute 'old_cr_workflow'
    3)
        File "docid.py", line 828, in openHLink_ccb
        [Error 2] Le fichier spécifié est introuvable: u'result\\result\\Dassault SMS PDS__CCB_TBD_1386668705.522000.docx'
    Add 'Applicable Since' in combo box
    Add log on/off ofr CCB report generation
    Correct _getReleaseList, _getBaselineList and _GetProjectList
1.5.3: [10th of December 2013 - O. Appéré]
    Modify CCB report table width
    Add "CR_functional_impact" attribute (attention c'est lent parce qu'on fait 1 requête par CR)
1.6.0: [17th of December 2013 - O. Appéré]
    Correct real time issues (thread lock)
    Separate GUI from thread synergy treatments.
1.6.1: [15th of January 2014 - O. Appéré]
    Correct CR button disabled
1.6.2: [27th of January 2014 - O. Appéré]
    Correct minor bug
    Display project list in Project set box aftre project update and enable Generate button for HCMR.
1.6.3: [30th of January 2014 - O. Appéré]
    Correct minor bug
    Add an alert if template is not found
1.6.4: [31st of January 2014 - O. Appéré]
    Add HCMR selection for board
    Add logrun function to display text without carriage return
    Add DAL parameter on GUI
1.6.5: [5th of February 2014 - O. Appéré]
    Correct List items: First baseline then release
    Add 'None' in CR attribute set listbox
1.7.0: [19th of February 2014 - O. Appéré]
    Refactor CID generation code
2.0.0: [1st of April 2014 - O. Appéré]
    History can be mase on documents
    History take into account multiple CR linked to an item
    Login interface calling corrected
2.1.0: [7th of April 2014 - O. Appéré]
    Add a progress bar for CID generation
    Correct Synergy status command
    add "CLOSE_SESSION" command launched by pressiog CTRL + X
    Correct getArticles with cvtype extra "and"
    move "replaceTag" function in Tool class
    create the function _compareReleaseName
    Correct _getCR function
    Add CR ID association wit htasks
    PR 001 (Implemented): Correct if "Clear selection" is pressed reset CR implemented in release: impact unsetRelease function
                            If release is "None" then "CR_implemented_for" attribute has to be discarded in CR query.
    PR 002 (Implemented): Correct functional/operational impact paragraph generation
    PR 003 (Entered): Correct tag parsing with docx python library patch
    PR 004 (Implemented): Correct _startSession in case CI ID is unknown
2.1.1: [10th of April 2014 - O. Appéré]
    Correct color of GUI
    Correct BuilDoc _loadConfig function
    Move picture_add to Tool class
2.1.2: [05th of May 2014 - O. Appéré]
    Add "-ts all_tasks" after "task" synergy command
    Correct database identification with item selection
    Add in Tool class get_sys_item_database and get_ci_sys_item_identification
    Add button to clear "detected on" and "implemented for" field
2.2.0: [12th of May 2014 - O. Appéré]
    Convert "ID" in lower case to avoid Excel to detect SYLK format instead of "csv" format
    Add column "old_worlflow" in table "item" in SQLite database and manage automatically SPR
    Correct SPR query
    Add "Invalid role" log error.
    Add "finduse" command skip and correct CID generation if finduse command is not used
    Manage several "implemented for" or "detected on" releaseManage several "implemented for" or "detected on" release
2.2.1: [12th of May 2014 - O. Appéré]
    Correct starting session if no password is entered
2.2.2: [12th of May 2014 - O. Appéré]
   Add impl_release in docid.ini and correct release initialisation
2.3.0: [15th of May 2014 - O. Appéré]
    PR 005 (Implemented) Disable old worlkflow display and correct other stuffs like get_sys_item_old_workflow function
    PR 006 (Implemented) Correct set project list is a new baseline is selected
    Correct previous baseline and add previous baseline/release in IHM
    Remove CCB reference
    Add function _getReference to find default reference in filename
    Add protocol and data interface compatibility index
    Add log into a file
    Add flag for CCB minutes generation
    Display list of CR in listbox when clicking on "List CR" button
    getPR_CCB in BuildDoc class is reworked completely
    Add cr_checklist table in SQLite database for CCB minutes generation
    Add mix type in method replaceTag of class Tool
2.3.1: [15th of May 2014 - O. Appéré]
    Correct CR domain assignement in CCB report
    Index of Extract SCR when exceeding 'z' become 'aa' etc. otherwise CR cannot exceed 26
    Adapt severity list for PLD
2.4.0: [19th of May 2014 - O. Appéré]
    Make correlation with selected item and component and CR_type
    Add components, link_items_components tables in SQLite database
    Add components listbox in GUI according to selected item
    Adapt CCB template for PLDCR and HCR
    Select automatically the righ button according to the selected component
2.4.1: [26th of May 2014 - O. Appéré]
    Disable CR list entry which is read only
    open web browser when double clicking on CR number in CR listbox
    Update SQLite default database creation
    Remove global variable interface and make software more maintanable
    Make CLI version to invoke _getCR method and LIST_ITEMS(TBD)
    Use <FocusOut> to update detect in and implemented for
2.4.2: [28th of May 2014 - O. Appéré]
    Correct bug <type 'exceptions.NameError'>: global name 'interface' is not defined
    Correct bug ValueError: All strings must be XML compatible: Unicode or ASCII, no NULL bytes or control characters
    Correct bug display page
2.5.0: [05th of June 2014 - O. Appéré]
    Add Plan Review and Software Conformity Review report generation
    Increase "Change request found" listbox and add synopsis wih color enhancement and mousewheel effect
    PR 003 (Implemented): Correct tag parsing with docx python library patch
    docx export with replace tag for checklist for CCB does not wok anymmore
2.5.1: [06th of June 2014 - O. Appéré]
    Create action items database for CCB  minutes
    *** Make query on MySQL database and actions table via mysqld ?
    *** Ajouter Information CR
    docx export with replace tag for checklist for CCB does not wok anymmore
2.5.2: [09th of June 2014 - O. Appéré]
    Correct bug in python-docx module and now checklist export works
    Manage action items database for CCB minutes
2.6.0: [26th of June 2014 - O. Appéré]
    Refactor actions management by creating action_gui.py
    Use tkintertable to display actions
2.6.1: [27th of June 2014 - O. Appéré]
    Add checklists from SQLite database for reviews

TODO:
    Make sub function in class
    Hyperlink target is lost by the new hyperlink created. Need an history of hyperlink
    Create class Change
    Create folder for reviews ?
    Add default doc in SQLite database
    Mieux gérer les erreurs remontées par Synergy dans _ccmCmd. Voir _getSessionStatus
    besoin de filtrer les objets par projet (avec la version aussi)
    Add a folder "Parameters" with "Old workflow" selection for instance
    Comma in synopsis of CR disturb csv output file formatting
    Correct thread error (TClError exception etc.)
"""
__author__ = "O. Appéré <olivier.appere@gmail.com>"
__date__ = "27th of June 2014"
__version__ = "rev 2.6.1"
import sys
import logging
import os
sys.path.append("python-docx")
from tool import Tool
from synergy import Synergy
from actions_gui import ActionGui
#import csv
try:
    from Tkinter import *
##    import Tkinter              # Python 2
    import ttk
except ImportError:
    from tkinter import *
##    import tkinter as Tkinter   # Python 3
    import tkinter.ttk as ttk
import tkMessageBox
try:
    import docx
except ImportError:
    print "DoCID requires the python-docx library for Python. " \
            "See https://github.com/mikemaccana/python-docx/"
                #    raise ImportError, "DoCID requires the python-docx library for Python. " \
                #         "See https://github.com/mikemaccana/python-docx/"
import threading
import time
from ConfigParser import ConfigParser
import re
import zipfile
import csv
from lxml import etree
import Queue
import datetime
import string
from os.path import join
from math import floor
try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        print "DoCID requires the Image library for Python. "
        print "No module Image loaded."
try:
    import Pmw
except ImportError:
    print "DoCID requires the Python MegaWidgets for Python. " \
        "See http://sourceforge.net/projects/pmw/"
            #raise ImportError, "DoCID requires the Python MegaWidgets for Python. " \
            #             "See http://sourceforge.net/projects/pmw/"
from reviews import Review

gui_background_color = 'white' #'#E6D8AE' #'white' #gui_background_color
background = gui_background_color #gui_background_color #'grey50'
foreground = 'black'
count_project = 0
count_baseline = 0
count_release = 0
class Logger(object):
    def __init__(self,filename="log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "w")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def __del__(self):
        close(self.log)
# -----------------------------------------------------------------------------
class BuildDoc(Tool,Synergy):
    # cache du dictionnaire de taches
    cache_array = {}
    def setRelease(self,release):
        self.release = release
        self.impl_release = release
    def setPreviousRelease(self,release):
        self.previous_release = release
    def setBaseline(self,baseline):
        self.baseline = baseline
    def setProject(self,project):
        self.project = project
    def setSessionStarted(self,session_started):
        self.session_started = session_started
    def __init__(self,ihm):
        global session_started

        Synergy.__init__(self,session_started)
        self.ihm = ihm
        self.session_started = session_started
        self.ccb_type = "SCR"
        self.list_cr_for_ccb_available = False
        try:
            self.author = self.ihm.author_entry.get()
            self.reference = self.ihm.reference_entry.get()
            self.revision = self.ihm.revision_entry.get()
            self.release = self.ihm.release
            self.aircraft = self.ihm.aircraft
            self.system = self.ihm.system
            self.item = self.ihm.item
            self.project = self.ihm.project
            self.baseline = self.ihm.baseline
            self.tableau_pr = []
            self.docx_filename = ""
            self.cid_type = self.ihm.getCIDType()
            self.part_number = self.ihm.part_number_entry.get()
            self.board_part_number = self.ihm.board_part_number_entry.get()
            self.checksum = self.ihm.checksum_entry.get()
            self.dal = self.ihm.dal_entry.get()
            self.previous_release = self.ihm.previous_release_entry.get()
            self.impl_release = self.ihm.impl_release_entry.get()
            self.detect_release = self.previous_release

        except AttributeError:
            self.author = ""
            self.reference = ""
            self.revision = ""
            self.release = ""
            self.aircraft = ""
            self.system = ""
            self.item = ""
            self.project = ""
            self.baseline = ""
            self.tableau_pr = []
            self.docx_filename = ""
            self.cid_type = ""
            self.part_number = ""
            self.board_part_number = ""
            self.checksum = ""
            self.dal = ""
            self.previous_release = ""
            self.impl_release = ""
            self.detect_release = ""
        self.programing_file = ""
        self.input_data_filter =""
        self.peer_reviews_filter = ""
        self.verif_filter = ""
        self.sources_filter = ""
        # Default values
        self.gen_dir = "result"
        self.list_type_src_sci = ("csrc","asmsrc","incl","macro_c","library")
        self.list_type_doc = ("doc","xls","pdf")
        # Get config
        result = self._loadConfig()
        self.old_cr_workflow = self.ihm.getTypeWorkflow()
        self.protocol_interface_index = "0"
        self.data_interface_index = "0"
    def getCIDType(self):
        return self.cid_type
    def openHLink(self,event):
        start, end = self.ihm.general_output_txt.tag_prevrange("hlink",
        self.ihm.general_output_txt.index("@%s,%s" % (event.x, event.y)))
        print "Going to %s..." % self.ihm.general_output_txt.get(start, end)
        os.startfile(self.gen_dir + self.docx_filename, 'open')
        #webbrowser.open
    def openHLink_qap(self,event):
        start, end = self.ihm.general_output_txt.tag_prevrange("hlink",
        self.ihm.general_output_txt.index("@%s,%s" % (event.x, event.y)))
        print "Going to %s..." % self.ihm.general_output_txt.get(start, end)
        os.startfile(self.gen_dir + self.docx_filename, 'open')
        #webbrowser.open
    def openHLink_ccb(self,event):
        start, end = self.ihm.general_output_txt.tag_prevrange("hlink",
        self.ihm.general_output_txt.index("@%s,%s" % (event.x, event.y)))
        print "Going to %s..." % self.ihm.general_output_txt.get(start, end)
        print "gen_dir",self.gen_dir
        print "docx_filename",self.docx_filename
        os.startfile(self.gen_dir + self.docx_filename, 'open')
        #webbrowser.open
    def _runFinduseQuery(self,release,project,type_items,enabled=False):
        '''
            Synergy finduse
            No baseline used, only project and release
        '''
        global session_started
        if self.finduse == "skip":
            enabled = False
            self.ihm.log("Finduse disabled.",False)
        if enabled:
            if project not in ("*","All",""):
                # Get project information
                project_name, project_version = self.getProjectInfo(project)
                if release not in ("","All"):
                    query = "finduse -query \"release='" + release + "' and " + type_items + " and recursive_is_member_of(cvtype='project' and name='"+ project_name +"' and version='"+ project_version +"' , 'none')\""
                    text = 'Finduse query release: ' + release + ', project: ' + project + '.'
                else:
                    query = "finduse -query \"" + type_items + " and recursive_is_member_of(cvtype='project' and name='"+ project_name +"' and version='"+ project_version +"' , 'none')\""
                    text = 'Finduse query release: ' + release + '.'
            elif release not in ("","All"):
                query = "finduse -query \"release='" + release + "' and " + type_items + " \""
                text = 'Finduse query release: ' + release + '.'
            self.ihm.log(text,False)
            self.ihm.log('ccm ' + query)
            self.ihm.defill()
            ccm_query = 'ccm ' + query + '\n\n'
            if session_started:
                stdout,stderr = self.ccm_query(query,text)
            else:
                stdout = ""
        else:
            stdout = ""
        return stdout
    def getSpecificBuild(self,release="",baseline="",project="",filters=["BUILD"]):
        '''
            Get file in  BUILD folder under a Synergy project
        '''
        type_items = "(cvtype='shsrc' or cvtype='executable' or cvtype='ascii' or cvtype='makefile')"
        stdout = self._runFinduseQuery(release,project,type_items,True)
        if stdout != "":
            # Build regular expression to filter only configuration items under BUILD folder
            regexp, list_items_skipped = self._prepareRegexp(filters)
            output = stdout.splitlines()
            for line in output:
                item = self._filterRegexp(regexp[0],line)
                if item != "":
                    # The item is in the folder
                    list_items_skipped[0].append(item)
                # ex: SW_PLAN\SDP\IS_SDP_SW_PLAN_SQA.xlsm-1.7.0@SW_PLAN-1.3
            # suppress redundant items
            table = list(set(list_items_skipped[0]))
            for data in table:
                self.ihm.log('Found in BUILD folder: ' + data,False)
        else:
            table = []
            self.ihm.log('No build files found with finduse command.')
        return table
    def getSpecificData(self,release="",baseline="",project="",filters=["INPUT_DATA","REVIEW","VTPR"],source=False):
        '''
            Use finduse command of Synergy to find path
        '''
##        regexp=["","",""]
        regexp=[]
        list_items_skipped = []
        if source:
            table = []
            type_items = "(cvtype='ascii' or cvtype='csrc' or cvtype='incl')"
        else:
            table = [[],[],[]]
            type_items = "(cvtype='xls' or cvtype='doc' or cvtype='pdf' or cvtype='ascii' or cvtype='csrc' or cvtype='incl')"
        enabled = True
        for filter in filters:
            if self._is_array(filter):
                for filt in filter:
                    self.ihm.log('Search folder containing keyword: ' + filt)
            else:
                self.ihm.log('Search folder containing keyword: ' + filter)
        stdout = self._runFinduseQuery(release,project,type_items,enabled)
        if enabled:
            if stdout != "":
                self.ihm.log(stdout,False)
                regexp, list_items_skipped = self._prepareRegexp(filters)
                output = stdout.splitlines()
                if not source:
##                    print "REGEXP"
##                    print regexp
                    for line in output:
                        item = self._filterRegexp(regexp[0],line)
                        if item != "":
                            list_items_skipped[0].append(item)
                        item = self._filterRegexp(regexp[1],line)
                        if item != "":
                            list_items_skipped[1].append(item)
                        item = self._filterRegexp(regexp[2],line)
                        if item != "":
                            list_items_skipped[2].append(item)
                        # ex: SW_PLAN\SDP\IS_SDP_SW_PLAN_SQA.xlsm-1.7.0@SW_PLAN-1.3
                    table[0] = list(set(list_items_skipped[0]))
                    table[1] = list(set(list_items_skipped[1]))
                    table[2] = list(set(list_items_skipped[2]))
                    for data in table[0]:
                        if self._is_array(filters[0]):
                            text = ""
                            for filter in filters[0]:
                                text += " " + filter
                        else:
                            text = filters[0]
                        self.ihm.log('Found in '+ text +' folder: ' + data,False)
                    for data in table[1]:
                        if self._is_array(filters[1]):
                            text = ""
                            for filter in filters[1]:
                                text += " " + filter
                        else:
                            text = filters[1]
                        self.ihm.log('Found in '+ text +' folder: ' + data,False)
                    for data in table[2]:
                        if self._is_array(filters[2]):
                            text = ""
                            for filter in filters[2]:
                                text += " " + filter
                        else:
                            text = filters[2]
                        self.ihm.log('Found in '+ text +' folder: ' + data,False)
                else:
##                    print "REGEXP"
##                    print regexp
                    for line in output:
                        item = self._filterRegexp(regexp[0],line)
                        if item != "":
                            list_items_skipped[0].append(item)
                        # ex: SW_PLAN\SDP\IS_SDP_SW_PLAN_SQA.xlsm-1.7.0@SW_PLAN-1.3
                    table = list(set(list_items_skipped[0]))
                    for data in table:
                        if self._is_array(filters[0]):
                            text = ""
                            for filter in filters[0]:
                                text += " " + filter
                        else:
                            text = filters[0]
                        self.ihm.log('Found in '+ text +' folder: ' + data,False)
            else:
                self.ihm.log('No items found with finduse command.')
        return table
    def _isSourceFile(self,filename):
        m = re.match("(.*)\.(c|h|asm|vhd)",filename)
        if m:
            result = True
        else:
            result = False
        return result
    def _getConstraintFile(self,filename):
        m = re.match(r"(.*)\.(pdc|sdc|tcl)",filename)
        if m:
            output_file = filename
        else:
            output_file = ""
        return output_file
    def _getSynthesisFile(self,filename):
        m = re.match(r"(.*)\.(edn|srr|sdf)",filename)
        if m:
            output_file = filename
        else:
            output_file = ""
        return output_file
    def _getSwOutputs(self,filename):
        m = re.match(r"(.*)\.(cof|hex|map|txt)",filename)
        if m:
            output_file = filename
        else:
            output_file = ""
        return output_file
    def _getSwProg(self,filename):
        m = re.match(r"(.*)\.(bat|sh|log|gld|txt|exe)",filename)
        if m:
            output_file = filename
        else:
            m = re.match(r"(m|Makefile)",filename)
            if m:
                output_file = filename
            else:
                output_file = ""
        return output_file
    def _getSwEOC(self,filename):
        m = re.match(r"(.*)\.(hex)",filename)
        if m:
            output_file = filename
        else:
            output_file = ""
        return output_file
    def _getProgramingFile(self,filename):
        m = re.match(r"(.*)\.stp",filename)
        if m:
            output_file = filename
        else:
            output_file = ""
        return output_file
    def _createTblPrograming(self,match):
        # For PLD/FGPA programming
##        if seek_file in ("",None):
        seek_file = self._getProgramingFile(match.group(2))
        if seek_file not in ("",None):
            # Found a programming file
            # Add the item to table
            self.tbl_program_file.append([match.group(2),match.group(3),match.group(1)])
    def _createTblSynthesis(self,match):
        # For PLD/FGPA synthesis
        seek_file = self._getSynthesisFile(match.group(2))
        if seek_file not in ("",None):
            self.tbl_synthesis_file.append([match.group(2),match.group(3),match.group(1)])
    def _createTblSources(self,m):
        result = False
        release_item = m.group(1)
        document = m.group(2)
        issue = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        if type in self.list_type_src and self._isSourceFile(document):
            if self.getCIDType() not in ("SCI"):
                self.tableau_src.append([release_item + ":" + project,document,issue,task,cr])
            else:
                self.tableau_src.append([document,issue,type,instance,release_item,cr])
            result = True
        return result
    def _createTblSourcesHistory(self,m,source_only=True):
        result = False
        document = m.group(1)
        version = m.group(2)
        task = m.group(3)
        task_synopsis = m.group(4)
        cr = m.group(5)
        cr_synopsis = m.group(6)
        type = m.group(7)
        line = False
        if source_only:
            condition = (type in self.list_type_src and self._isSourceFile(document))
        else:
            condition = True
        if condition:
##            if "SSCS" in document:
##                print "TASK",task
##                print "CR",cr
            # Tasks ID are separated by comma
            list_tasks = task.split(",")
            # Tasks synopsis are separated by semicolon
            list_task_synopsis = task_synopsis.split(";")
            # CR ID are separated by comma
            list_cr = cr.split(",")
            # Tasks CR are separated by semicolon
            list_cr_synopsis = cr_synopsis.split(";")
            line = []
            cr_linked_to_task = False
            for index in range(len(list_tasks)):
                # multiple tasks and at least one CR
                if len(list_tasks) > 1 and cr != "":
                    task_id_str = list_tasks[index]
                    task_id_int = int(task_id_str)
                    # Find CR linked if more than one task is linked to the item
                    text_summoning = "find CRs"
                    # if the command has already be executed  go get the cache instead
                    if task_id_str not in self.cache_array:
                        query = "task -show change_request " + task_id_str
                        self.ihm.log("ccm " + query)
                        stdout,stderr = self.ccm_query(query,text_summoning)
                        # Set scrollbar at the bottom
                        self.ihm.defill()
                        if stdout != "":
                            task_vs_cr_array = stdout.splitlines()
                            if len(task_vs_cr_array) > 1:
                                cr_linked_to_task = True
                                self.cache_array[task_id_str] = True
                                for cr_id in list_cr:
                                    self.ihm.log("   CR linked: " + cr_id)
                            else:
                                cr_linked_to_task = False
                                self.cache_array[task_id_str] = False
                                self.ihm.log("   No CRs found")
                        else:
                            self.ihm.log("   No CRs found")
                    else:
                        cr_linked_to_task = self.cache_array[task_id_str]
                if cr_linked_to_task:
                    for index_cr in range(len(list_cr)):
                        line.append(document + ";" + version + ";" + list_tasks[index] + ";" + list_task_synopsis[index] + ";" + list_cr[index_cr] + ";" + list_cr_synopsis[index_cr])
                else:
                    line.append(document + ";" + version + ";" + list_tasks[index] + ";" + list_task_synopsis[index] + ";;")
##            self.tableau_items.append([document,version,task,task_synopsis,cr,cr_synopsis])
##            print "CACHE:",self.cache_array
            result = True
        return line
    def _createTblSoftwareProgramming(self,m):
        result = False
        release_item = m.group(1)
        document = m.group(2)
        issue = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        seek_file = self._getSwProg(document)
        if type in self.list_type_prog and seek_file:
##            description = self._getDescriptionDoc(m.group(2))
            self.tableau_prog.append([document,issue,type,instance,release_item,cr])
            result = True
        return result
    def _createTblSoftwareOutputs(self,m):
        '''
            self.tbl_sw_outputs is filled if document fullfilled criteria of _getSwOutputs
        '''
        # For software outputs
        release_item = m.group(1)
        document = m.group(2)
        issue = m.group(3)
        task = m.group(4)
        status = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        seek_file = self._getSwOutputs(document)
        if seek_file not in ("",None):
            self.tbl_sw_outputs.append([document,issue,type,instance,release_item])
    def _createTblSoftwareEOC(self,m):
        # For software EOC
        release_item = m.group(1)
        document = m.group(2)
        issue = m.group(3)
        task = m.group(4)
        status = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        seek_file = self._getSwEOC(document)
        if seek_file not in ("",None):
            self.tbl_sw_eoc.append([document,issue,type,instance,release_item])
    def _createTblConstraint(self,match):
        # For PLD/FGPA synthesis
        seek_file = self._getConstraintFile(match.group(2))
        if seek_file not in ("",None):
            self.tbl_constraint_file.append([match.group(2),match.group(3),match.group(1)])

    def _createTblDocuments(self,m):
        result = False
        release = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        # discard SCI
        doc_name = re.sub(r"(.*)\.(.*)",r"\1",document)
        if "SCI_" not in doc_name:
            if type in self.list_type_doc:
                description,reference = self._getDescriptionDoc(document)
                if self.getCIDType() not in ("SCI"):
                    self.tableau_items.append([m.group(1) + ":" + m.group(7),m.group(2),m.group(3),description,m.group(4)])
                else:
                    self.tableau_items.append([description,reference,document,version,type,instance,release,cr])
                result = True
        return result
    def _createTblInputData(self,m,release):
        '''
        Filter input data.
        Data selected are those
            - which release is different from the release selected
            - which type is in self.list_type_doc
        '''
        result = False
        release_item = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        status = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        # Check if the release basename is the same by removin /01 etc
        same_releases = self._compareReleaseName([release_item,release])
        if not same_releases and type in self.list_type_doc:
            # May be input data
            description,reference = self._getDescriptionDoc(document)
            if self.getCIDType() not in ("SCI"):
                self.tbl_input_data.append([release_item + ":" + project,document,version,description,task])
            else:
                self.tbl_input_data.append([description,reference,document,version,type,instance,release_item])
            result = True
        return result
    def _createTblPlans(self,m):
        '''
           Add a plan document in table of plans if
            - the name of the document match the name in development plans dictionary
            - the type of the document is doc or pdf
        '''
        result = False
        description = ""
        release_item = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        if type in ('doc','pdf'):
            # List of expected keywords in document name
            dico = {"SCMP_SW_PLAN":"Software Configuration Management Plan",
                    "SDP_SW_PLAN":"Software Development Plan",
                    "smp":"Software Development Plan",
                    "SQAP_SW_PLAN":"Software Quality Assurance Plan",
                    "sqap":"Software Quality Assurance Plan",
                    "SVP_SW_PLAN":"Software Verification Plan",
                    "PSAC_SW_PLAN":"Plan for Software Aspect of Certification",
                    "psac":"Plan for Software Aspect of Certification",
                    "PHAC":"Plan for Hardware Aspect of Certification",
                    "PLD_HMP":"PLD Hardware Management Plan"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",document)
##            print doc_name
            for key in dico:
                if key in doc_name:
                    description,reference = self._getDescriptionDoc(document)
                    description = dico[key]
                    if self.getCIDType() not in ("SCI"):
                        self.tbl_plans.append([m.group(1) + ":" + m.group(7),document,m.group(3),description,m.group(4)])
                    else:
                        reference = self._getReference(document)
                        self.tbl_plans.append([description,reference,document,version,type,instance,release_item,cr])
                    result = True
                    break;
        return result
    def _createTblStds(self,m):
        '''
            Add a standard document in table of standards if
            - the name of the document match the name in software standards dictionary
            - the type of the document is doc or pdf
        '''
        result = False
        description = ""
        release_item = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        if type in ('doc','pdf','xls'):
            dico = {"SCS_SW_STANDARD":"Software Coding Standard",
                    "coding_standard":"Software Coding Standard",
                    "SDTS_SW_STANDARD":"Software Design and Testing Standard",
                    "design_standard":"Software Design Standard",
                    "SRTS_SW_STANDARD":"Software Requirement and Testing Standard",
                    "IEEE_830_1988":"Software Requirement Standard",
                    "PLD_Coding_Standard":"PLD Coding Standard",
                    "PLD_Design_Standard":"PLD Design Standard",
                    "SAQ":"Template"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description,reference = self._getDescriptionDoc(document)
                    description = dico[key]
                    if self.getCIDType() not in ("SCI"):
                        self.tbl_stds.append([m.group(1) + ":" + m.group(7),m.group(2),m.group(3),description,m.group(4)])
                    else:
                        reference = self._getReference(document)
                        self.tbl_stds.append([description,reference,document,version,type,instance,release_item,cr])
                    result = True
                    break;
        return result
    def _createTblCcb(self,m):
        '''
            Add a CCB minutes report document in table of CCB minutes if
            - the name of the document match the name in software CCB minutes report dictionary
            - the type of the document is doc or pdf
        '''
        result = False
        description = ""
        release_item = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        if type in ('doc','pdf'):
            dico = {"CCB_Minutes":"CCB meeting report",
                    "CCB":"CCB meeting report"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description = dico[key]
                    if self.getCIDType() not in ("SCI"):
                        self.tbl_ccb.append([m.group(1) + ":" + m.group(7),m.group(2),m.group(3),description,m.group(4)])
                    else:
                        self.tbl_ccb.append([description,document,version,type,instance,release_item])
                    result = True
                    break
        return result
    def _createTblSas(self,m):
        '''
            Add a SAS document in table of SAS if
            - the name of the document match the name in SAS dictionary
            - the type of the document is doc or pdf
        '''
        result = False
        description = ""
        release_item = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        if type in ('doc','pdf'):
            dico = {"SAS":"Software Accomplishment Summary"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description,reference = self._getDescriptionDoc(document)
                    description = dico[key]
                    if self.getCIDType() not in ("SCI"):
                        self.tbl_sas.append([m.group(1) + ":" + m.group(7),m.group(2),m.group(3),description,m.group(4)])
                    else:
                        self.tbl_sas.append([description,reference,document,version,type,instance,release_item,cr])
                    result = True
                    break
        return result
    def _createTblSeci(self,m):
        '''
            Add a SECI document in table of SECI if
            - the name of the document match the name in SECI dictionary
            - the type of the document is doc or pdf
        '''
        result = False
        description = ""
        release_item = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        if type in ('doc','pdf'):
            dico = {"SECI":"Software Environment Configuration Index"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description,reference = self._getDescriptionDoc(document)
                    description = dico[key]
                    if self.getCIDType() not in ("SCI"):
                        self.tbl_seci.append([m.group(1) + ":" + m.group(7),m.group(2),m.group(3),description,m.group(4)])
                    else:
                        self.tbl_seci.append([description,reference,document,version,type,instance,release_item,cr])
                    result = True
                    break
        return result
    def _createTblInspectionSheets(self,m):
        '''
            Add a review document in table of review if
            - the name of the document match the name in review dictionary
            - the type of the document is xls
        '''
        result = False
        description = ""
        release = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        if type in ('xls'):
            dico = {"IS_":"Inspection Sheet",
                    "PRR":"Peer Review Register"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description = dico[key]
                    if self.getCIDType() not in ("SCI"):
                        self.tbl_inspection_sheets.append([m.group(1) + ":" + m.group(7),m.group(2),m.group(3),description,m.group(4)])
                    else:
                        self.tbl_inspection_sheets.append([document,version,release])
                    result = True
        return result
    def getArticles(self,type_object,release,baseline,project="",source=False):
        '''
         Function to get list of items in Synergy with a specific release or baseline
        '''
        if self.session_started:
            # Create filter for item type
            query_cvtype = ""
            status = False
            if type_object != ():
                for type in type_object:
                    result,status = self.createItemType(type,status)
                    query_cvtype += result
                query_cvtype += ')'
                query_cvtype += self.makeobjectsFilter(self.object_released,self.object_integrate)
            if source:
                # get task and CR for source code
                if self.getCIDType() not in ("SCI"):
                    display_attr = ' -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"' # %task_synopsis
                else:
                    display_attr = self.display_attr
            else:
                display_attr = ' -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"'
            if baseline not in ("","All"):
                # Baseline
                #
                #  -sh: show
                #   -u: unnumbered
                # -sby: sort by
                #
                if source:
                    query = 'baseline -u -sby name -sh objects  ' + baseline
                    text_summoning = "Get source files from baseline: "
                else:
                    query = 'baseline -u -sby project -sh objects  ' + baseline
                    text_summoning = "Get documents from baseline: "
                query += display_attr
                self.ihm.log(text_summoning + baseline)
                self.ihm.log("ccm " + query)
                self.ihm.defill()
                stdout,stderr = self.ccm_query(query,text_summoning + baseline)
                # Set scrollbar at the bottom
                self.ihm.defill()
##                print stdout
                if stdout != "":
##                    print "TEST_BASELINE"
##                    print stdout
                    output = stdout.splitlines()
                    return output
                else:
                    self.ihm.log("No items found")
                    return ""
            elif release not in ("","All"):
                if source:
                    query = 'query -sby name -n *.* -u '
                else:
                    query = 'query -sby project -n *.* -u '
                query += '-release ' + release + " "
                if query_cvtype != "":
                    query += query_cvtype
                    need_and = True
                else:
                    need_and = False
                if project != "":
                    prj_name, prj_version = self.getProjectInfo(project)
                    #% option possible: ccm query "recursive_is_member_of('projname-version','none')"
                    if need_and:
                         query += ' and '
                    query += ' recursive_is_member_of(cvtype=\'project\' and name=\'' + prj_name + '\' and version=\'' + prj_version + '\' , \'none\')" '
                    text = "project"
                    param = project
                else:
                    query += '"'
                    text = "release"
                    param = release
                query += display_attr
                self.ihm.log("ccm " + query)
                self.ihm.log("Get items from " + text + ": " + param)
                stdout,stderr = self.ccm_query(query,"Get items from " + text + ": " + param)
                # Set scrollbar at the bottom
                self.ihm.defill()
                if stdout != "":
                    output = stdout.splitlines()
                    return output
                else:
                    self.ihm.log("No items found.")
                    return ""
            elif project not in ("","All"):
                if source:
                    query = 'query -sby name -n *.* -u '
                else:
                    query = 'query -sby project -n *.* -u '
                if query_cvtype != "":
                    query += query_cvtype
                    need_and = True
                else:
                    need_and = False
                prj_name, prj_version = self.getProjectInfo(project)
                #% option possible: ccm query "recursive_is_member_of('projname-version','none')"
                if need_and:
                     query += ' and '
                query += ' recursive_is_member_of(cvtype=\'project\' and name=\'' + prj_name + '\' and version=\'' + prj_version + '\' , \'none\')" '
                text = "project"
                param = project
                query += display_attr
                self.ihm.log("ccm " + query)
                self.ihm.log("Get items from " + text + ": " + param)
                stdout,stderr = self.ccm_query(query,"Get items from " + text + ": " + param)
                # Set scrollbar at the bottom
                self.ihm.defill()
                if stdout != "":
                    output = stdout.splitlines()
                    return output
                else:
                    self.ihm.log("No items found.")
                    return ""
            else:
                print "Bug: problème avec la recherche d'objets."
        else:
            self.ihm.log("Session not started.",False)
        # Set scrollbar at the bottom
        self.ihm.defill()
        return ""
    def getStatusCheck(self):
        '''
            This function
            - select all checkbuttons for Change Request status
            - build the Change query condition filtering according checkbuttons state
            Attention cette fonction est dŽjˆ implŽmentŽe dans la fonction suivante getPR
        '''
        self.ihm.check_button_status_in_analysis.select()
        self.ihm.check_button_status_compl_analysis.select()
        self.ihm.check_button_status_in_review.select()
        self.ihm.check_button_status_postponed.select()
        self.ihm.check_button_status_under_modif.select()
        self.ihm.check_button_status_under_verif.select()
        self.ihm.check_button_status_fixed.select()
        self.ihm.check_button_status_closed.select()
        self.ihm.check_button_status_canceled.select()
        self.ihm.check_button_status_rejected.select()
        self.ihm.check_button_status_all.select()
        self.ihm.cr_activate_all_button()
        self.ihm.checkbutton_all = True
        self.ihm.cr_activate_all_button()
        condition,detect_attribut = self._createConditionStatus()
##        condition += '-f "%problem_number;%problem_synopsis;%crstatus;' + detect_attribut + '"'
        return condition
    def _createImpl(self,keyword,release):
        '''
        Creates a string like "((CR_implemented_for='SW_ENM/01') or(CR_implemented_for='SW_PLAN/02'))"
        if keyword = CR_implemented_for and release = SW_ENM/01,SW_PLAN/02
        '''
        for list_rel in csv.reader([release]):
            pass
        text = "("
        if self._is_array(list_rel):
            for rel in list_rel:
                text += '('+ keyword + '=\''+ rel +'\') or'
            # Remove last comma
            text = text[0:-3] + ')'
        return text
    def _createConditionStatus(self,release="",old_cr_workflow=False,attribute="CR_implemented_for"):
        '''
            Create CR status filter for Change query
        '''
        # [X]CR Workflow
        def getStatusClosed():
            '''
            concluded
            [X]CR_Closed
            '''
            try:
                cr_status = self.ihm.status_closed.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0:
                status = None
            else:
                if self.old_cr_workflow:
                    status = "concluded"
                else:
                    status = self.ccb_type + "_Closed"
            return status
        def getStatusCancel():
            try:
                cr_status = self.ihm.status_canceled.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0 or self.old_cr_workflow:
                status = None
            else:
                status = self.ccb_type + "_Cancelled"
            return status
        def getStatusReject():
            try:
                cr_status = self.ihm.status_rejected.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0 or self.old_cr_workflow:
                status = None
            else:
                status = self.ccb_type + "_Rejected"
            return status
        def getStatusAnalysis():
            '''
            entered
            [EX]CR_Entered
            [X]CR_In_Analysis
            '''
            try:
                cr_status = self.ihm.status_in_analysis.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0:
                status = None
            else:
                if self.old_cr_workflow:
                    status = "entered"
                else:
                    if self.ccb_type == "EXCR":
                        status = self.ccb_type + "_Entered"
                    else:
                        status = self.ccb_type + "_In_Analysis"
            return status
        def getStatusComplAnalysis():
            try:
                cr_status = self.ihm.status_compl_analysis.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0 or self.old_cr_workflow:
                status = None
            else:
                status = self.ccb_type + "_Complementary_Analysis"
            return status
        def getStatusReview():
            '''
            in_review
            [X]_In_Review
            '''
            try:
                cr_status = self.ihm.status_in_review.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0:
                status = None
            else:
                if self.old_cr_workflow:
                    status = "in_review"
                else:
                    status = self.ccb_type + "_In_Review"
            return status
        def getStatusModif():
            '''
            assigned
            [EX]CR_In_Progress
            [X]CR_Under_Modification
            '''
            try:
                cr_status = self.ihm.status_under_modif.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0:
                status = None
            else:
                if self.old_cr_workflow:
                    status = "assigned"
                else:
                    if self.ccb_type == "EXCR":
                        status = self.ccb_type + "_In_Progress"
                    else:
                        status = self.ccb_type + "_Under_Modification"
            return status
        def getStatusVerif():
            try:
                cr_status = self.ihm.status_under_verif.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0 or self.old_cr_workflow:
                status = None
            else:
                status = self.ccb_type + "_Under_Verification"
            return status
        def getStatusFixed():
            '''
            assigned
            [EX]CR_Implemented
            [X]CR_Fixed
            '''
            try:
                cr_status = self.ihm.status_fixed.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0:
                status = None
            else:
                if self.old_cr_workflow:
                    status = "resolved"
                else:
                    if self.ccb_type == "EXCR":
                        status = self.ccb_type + "_Implemented"
                    else:
                        status = self.ccb_type + "_Fixed"
            return status
        def getStatusPostpon():
            '''
            Get postponed checkbox status of the GUI according to CR workfow (Old,EXCR or [X]CR)
            [EX]CR_Workaround
            [X]CR_Postponed
            Note this function should be in Interface class with workflow type for parameter
            '''
            try:
                cr_status = self.ihm.status_postponed.get()
            except AttributeError:
                cr_status = 1
            if cr_status == 0:
                status = None
            else:
                if self.old_cr_workflow:
                    status = "postponed"
                else:
                    if self.ccb_type == "EXCR":
                        status = self.ccb_type + "_Workaround"
                    else:
                        status = self.ccb_type + "_Postponed"
            return status

        old_cr_workflow = self.ihm.getTypeWorkflow()
##        condition = '"(cvtype=\'problem\') '
        # Get filter attributes
        #
        # Default = CR_implemented_for
        # Detected on
        # Implemented for
        # Applicable Since
        #
        if attribute == "None":
            filter_cr = ""
        else:
            filter_cr = attribute
        # Determine wether an old or new Change Request workflow is used
        # Query format is modified accordingly
##        print "TEST",self.release,self.previous_release
        if release not in ("","All","None"):
            if old_cr_workflow:
                detection_word = "detected_on"
                filter_cr = "implemented_in"
            else:
                detection_word = "CR_detected_on"
                filter_cr = "CR_implemented_for"
            detect_attribut = "%"+ detection_word + ";%" + filter_cr
            condition = '"(cvtype=\'problem\') and '
            # implemented
            condition += self._createImpl(filter_cr,release)
            # detected
            if self.previous_release != "":
                condition += ' and '
                condition += self._createImpl(detection_word,self.previous_release)
##                    condition += 'and (CR_detected_on=\''+ self.previous_release +'\')'
        else:
            if old_cr_workflow:
                detect_attribut = "%detected_on;%implemented_in"
            else:
                detection_word = "CR_detected_on"
                filter_cr = "CR_implemented_for"
                detect_attribut = "%"+ detection_word + ";%" + filter_cr
            condition = '"(cvtype=\'problem\') '
            # detected
            if self.previous_release != "":
                condition += ' and '
                condition += self._createImpl(detection_word,self.previous_release)
        # cr type
        if self.ihm.cr_type != "":
            condition += ' and '
            condition += self._createImpl("CR_type",self.ihm.cr_type)
        #
        # Status
        #
        find_status = False
        cr_status = getStatusAnalysis()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
        cr_status = getStatusClosed()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
        cr_status = getStatusReview()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
        cr_status = getStatusCancel()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
        cr_status = getStatusReject()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
        cr_status = getStatusComplAnalysis()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
        cr_status = getStatusModif()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
        cr_status = getStatusVerif()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition = condition + delta_condition
        cr_status = getStatusFixed()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
        cr_status = getStatusPostpon()
        delta_condition,find_status = self.createCrStatus(cr_status,find_status)
        condition += delta_condition
##            self.ihm.cr_deactivate_all_button()
        if find_status == True:
            condition = condition + ')" '
        else:
            condition = condition + '" '
        return condition,detect_attribut
    def getPR(self):
        '''
            Run a Change Request query
            Remove prefix to make generic status name
            The result is put in the table self.tableau_pr with the following columns:
            --------------------------------------------------------------------
            | ID | Synopsis | Type | Status | Detected on | Implemented in/for |
            --------------------------------------------------------------------
            Used by CreateCID function
        '''
        global session_started
        self.tableau_pr = []
        self.tableau_closed_pr = []
        self.tableau_opened_pr = []
        # Header
        self.tableau_pr.append(["ID","Synopsis","Type","Status","Detected on","Implemented in/for"])
        self.tableau_closed_pr.append(["ID","Synopsis","Type","Status","Detected on","Implemented in/for"])
        self.tableau_opened_pr.append(["ID","Synopsis","Type","Status","Detected on","Implemented in/for"])
        query = 'query -sby crstatus '
        condition,detect_attribut = self._createConditionStatus(self.ihm.impl_release,self.old_cr_workflow)
        condition += '-f "%problem_number;%problem_synopsis;%crstatus;' + detect_attribut + '"'
        query += condition #+ '-f "%problem_number;%problem_synopsis;%crstatus;' + detect_attribut + '"'
##        print query
        if session_started:
            self.ihm.cr_activate_all_button()
            self.ihm.checkbutton_all = True
            stdout,stderr = self.ccm_query(query,"Get PRs")
            self.ihm.log(query + " completed.")
            # Set scrollbar at the bottom
            self.ihm.defill()
            if stdout != "":
                output = stdout.splitlines()
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                    if self.old_cr_workflow:
                        m = re.match(r'(.*);(.*);(.*);(.*);(.*)',line)
                        if m:
                            problem_number = m.group(1)
                            problem_synopsis = m.group(2)
                            status = m.group(3)
                            detected_on = m.group(4)
                            implemented_in = m.group(5)
                            self.tableau_pr.append([problem_number,problem_synopsis,"SPR",status,detected_on,implemented_in])
                            if status in ("concluded"):
                                self.tableau_closed_pr.append([problem_number,problem_synopsis,"SPR",status,detected_on,implemented_in])
                            else:
                                self.tableau_opened_pr.append([m.group(1),m.group(2),"SPR",status,detected_on,implemented_in])
                    else:
                        # Split CR status on case all CR are displayed
                        result = re.sub(r'(.*);(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*);(.*)', r'\1;\2;\3;\4', line)
                        m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*)',result)
                        if m:
                            type = m.group(3)
                            status = m.group(4)
                            self.tableau_pr.append([m.group(1),m.group(2),type,status,m.group(5),m.group(6)])
                            if status in ("Closed"):
                                self.tableau_closed_pr.append([m.group(1),m.group(2),type,status,m.group(5),m.group(6)])
                            else:
                                self.tableau_opened_pr.append([m.group(1),m.group(2),type,status,m.group(5),m.group(6)])
        if len(self.tableau_pr) == 1:
             self.tableau_pr.append(["--","--","--","--","--","--"])
        if len(self.tableau_closed_pr) == 1:
             self.tableau_closed_pr.append(["--","--","--","--","--","--"])
        if len(self.tableau_opened_pr) == 1:
             self.tableau_opened_pr.append(["--","--","--","--","--","--"])
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
##                table_modifs.append([self.revision,time.strftime("%d %b %Y", time.localtime()),"Next",self.author])
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
                                'text':time.strftime("%d %b %Y", time.localtime()),
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
        self.docx_filename = self.gen_dir + self.aircraft + "_" + self.item + "_" + template_type + "_" + self.reference + ".docx"
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
    def _loadConfig(self):
        # Get config
        read_config = True
        self.config_parser = ConfigParser()
        try:
            self.config_parser.read('docid.ini')
            # get template name
            template_dir = join(os.path.dirname("."), 'template')
            template_name = self.getOptions("Template",self.cid_type)
            self.ihm.log("Template selected: " + template_name)
            template_default_name = "HCMR_template.docx"
            self.template_name = join(template_dir, template_name)
            self.template_default_name = join(template_dir, template_default_name)
            if self.cid_type in ("HCMR_PLD","HCMR_BOARD"):
                self.template_type = "HCMR"
            else:
                self.template_type = self.cid_type
            self.previous_baseline = self.getOptions("Default","previous_baseline")
            self.finduse = self.getOptions("Generation","finduse")
             # get generation directory
            self.gen_dir = self.getOptions("Generation","dir")
            self.input_data_filter = self._getOptionArray("Generation","input_data")
            self.peer_reviews_filter = self._getOptionArray("Generation","peer_reviews")
            self.verif_filter = self._getOptionArray("Generation","verification")
            self.sources_filter= self._getOptionArray("Generation","sources")
            self.dico_descr_docs = {}
            self.dico_descr_docs_ref = {}
            self.dico_descr_docs_default = {}
##            self.dico_descr_docs_default = {"SWRD":"Software Requirements Document",
##                                            "SWDD":"Software Design Document",
##                                            "SCOD":"Source Code Output Document",
##                                            "SSCS":"Board Specification Document",
##                                            "PHAC":"Plan for Hardware Aspects of Certification",
##                                            "HMP":"Hardware Management Plan",
##                                            "PLDRD":"PLD Requirements Document",
##                                            "PLDVPR":"PLD Verification Procedures and Results",
##                                            "PLDVTR":"PLD Verification Tests and Results",
##                                            "PLDDD":"PLD Design Document",
##                                            "HwRD":"Hardware Requirements Document",
##                                            "HwDD":"Hardware Design Document",
##                                            "HSID":"Hardware Software Interface Document",
##                                            "HPID":"Hardware PLD Interface Document",
##                                            "PRR":"Peer Review Register",
##                                            "IS_":"Inspection Sheet",
##                                            "ICD":"Interface Control Design",
##                                            "CRI_":"EASA Certification Review Item",
##                                            "IP_SW":"FAA Issue Paper"}
            # read dictionary of doc for project
            # 3 columns separated by comma
            if self.config_parser.has_option("Generation","description_docs"):
                file_descr_docs = self.config_parser.get("Generation","description_docs")
                with open(file_descr_docs, 'rb') as file_csv_handler:
                    reader = csv.reader (self.CommentStripper (file_csv_handler))
                    for tag,description,reference in reader:
                        self.dico_descr_docs[tag] = description
                        self.dico_descr_docs_ref[tag] = reference
            # read dictionary of generic description for doc
            # 2 columns separated by comma
            if self.config_parser.has_option("Generation","glossary"):
                file_descr_docs = self.config_parser.get("Generation","glossary")
                with open(file_descr_docs, 'rb') as file_csv_handler:
                    reader = csv.reader (self.CommentStripper (file_csv_handler))
                    for tag,description in reader:
                        self.dico_descr_docs_default[tag] = description
            # read object type
            type_doc = self.config_parser.get("Objects","type_doc")
            for self.list_type_doc in csv.reader([type_doc]):
                pass
            if self.config_parser.has_option("Objects","type_src"):
                type_src = self.config_parser.get("Objects","type_src")
                if type_src:
                    for self.list_type_src_sci in csv.reader([type_src]):
                        pass
                else:
                    self.list_type_src_sci = ("csrc","asmsrc","incl","macro_c","library")
            elif self.config_parser.has_option("Objects","sw_src"):
                type_src = self.config_parser.get("Objects","sw_src")
                if type_src:
                    for self.list_type_src_sci in csv.reader([type_src]):
                        pass
                else:
                    self.list_type_src_sci = ()
            else:
                self.list_type_src_sci = ()
            if self.config_parser.has_option("Objects","sw_prog"):
                type_prog = self.config_parser.get("Objects","sw_prog")
                if type_prog:
                    for self.list_type_prog in csv.reader([type_prog]):
                        pass
                else:
                    self.list_type_prog = ()
            else:
                self.list_type_prog = ()
            if self.config_parser.has_option("Objects","sw_ouputs"):
                type_outputs = self.config_parser.get("Objects","sw_outputs")
                if type_outputs:
                    for self.list_type_outputs in csv.reader([type_outputs]):
                        pass
                else:
                    self.list_type_outputs = ("ascii")
            else:
                self.list_type_outputs = ("ascii")
            if self.config_parser.has_option("Objects","type_src"):
                type_src = self.config_parser.get("Objects","type_src")
                if type_src:
                    for self.list_type_src_hcmr in csv.reader([type_src]):
                        pass
                else:
                    self.list_type_src_hcmr = ("ascii")
            elif self.config_parser.has_option("Objects","hw_src"):
                type_src = self.config_parser.get("Objects","hw_src")
                if type_src:
                    for self.list_type_src_hcmr in csv.reader([type_src]):
                        pass
                else:
                    self.list_type_src_hcmr = ("ascii")
            else:
                self.list_type_src_hcmr = ("ascii")
            func_chg_filename = self.getOptions("Generation","func_chg_filename")
            if func_chg_filename != "":
                fichier = open(func_chg_filename, "r")
                func_chg_tbl = fichier.readlines()
                self.func_chg = []
                for line in func_chg_tbl:
                    self.func_chg.append((line,'r'))
            else:
                self.func_chg = ""
            oper_chg_filename = self.getOptions("Generation","oper_chg_filename")
            if oper_chg_filename != "":
                fichier = open(oper_chg_filename, "r")
                oper_chg_tbl = fichier.readlines()
##                self.oper_chg = oper_chg_tbl
                self.oper_chg = []
                for line in oper_chg_tbl:
                    self.oper_chg.append((line,'r'))
            else:
                self.oper_chg = ""
            self.protocol_interface = self.getOptions("Generation","protocol_interface")
            self.data_interface = self.getOptions("Generation","data_interface")
            try:
                # get CR workflow type
                if self.config_parser.has_section("Workflow"):
                    self.ihm.check_cr_workflow_status.config(state=DISABLED)
                    self.ihm.type_cr_workflow = self.config_parser.get("Workflow","CR")
                else:
                    self.ihm.type_cr_workflow = "None"
            except KeyError as exception:
                self.ihm.log("CR workflow determination failed.")
                self.ihm.log(exception)
            except IOError as exception:
                self.ihm.log(exception)
            self.ihm.log("Generation config reading succeeded.")
        except IOError as exception:
            self.ihm.log("Generation config reading failed.")
            self.ihm.log(exception)
            read_config = False
        self.ihm.defill()
        return read_config
##        print "BuildDoc._loadConfig executed."
    def _setOuptutFilename(self):
        self.docx_filename = self.system + "_"
        if self.item != "":
            self.docx_filename += self.item + "_" + self.template_type + "_" + self.reference + "_%d" % floor(time.time()) + ".docx"
        else:
            self.docx_filename += self.template_type + "_" + self.reference + "_%d" % floor(time.time()) + ".docx"
        self.ihm.log("Preparing " + self.docx_filename + " document.")
    def _getAllProg(self,release,baseline,project):
        '''
            Looking for progamming files according to self.list_type_prog
        '''
        output = self.getArticles(self.list_type_prog,release,baseline,project,True)
        index_prog = 0
        index_sw_outputs = 0
        index_sw_eoc = 0
        for line in output:
            line = re.sub(r"<void>",r"",line)
            self.ihm.log("Found prog: "+line,False)
            m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
            if m:
                result = self._createTblSoftwareProgramming(m)
                if result:
                    index_prog +=1
                result = self._createTblSoftwareOutputs(m)
                if result:
                    index_sw_outputs +=1
                result = self._createTblSoftwareEOC(m)
                if result:
                    index_sw_eoc +=1
        if index_prog > 0:
            self.ihm.log("Amount of programming files found: " + str(index_prog),False)
        else:
            self.ihm.log("No programming files found.",False)
        if index_sw_outputs > 0:
            self.ihm.log("Amount of output files found: " + str(index_sw_outputs),False)
        else:
            self.ihm.log("No output files found.",False)
        if index_sw_eoc > 0:
            self.ihm.log("Amount of EOC found: " + str(index_sw_eoc),False)
        else:
            self.ihm.log("No EOC found.",False)
    def _getAllSourcesHistory(self,release,baseline,project):
        '''
            Looking for source files according to self.list_type_src
        '''
        output = self.getArticles(self.list_type_src,release,baseline,project,True)
        index_src = 0
        for line in output:
            line = re.sub(r"<void>",r"",line)
            m = re.match(r'(.*)|(.*)|(.*)|(.*)|(.*)|(.*)|(.*)',line)
            if m:
                result = self._createTblSourcesHistory(m)
                if result:
                    index_src +=1
        self.ihm.log("Amount of source files found: " + str(index_src),False)
        return output
    def _getAllSources(self,release,baseline,project):
        '''
            Looking for source files according to self.list_type_src
        '''
        output = self.getArticles(self.list_type_src,release,baseline,project,True)
        index_src = 0
        index_prog = 0
        for line in output:
            line = re.sub(r"<void>",r"",line)
            self.ihm.log("Found src: " + line,False)
            m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
            if m:
                # For PLD/FGPA programming and synthesis
                result = self._createTblPrograming(m)
                if result:
                    index_prog +=1
                self._createTblSynthesis(m)
                self._createTblConstraint(m)
                # For PLD/FPGA and software
                result = self._createTblSources(m)
                if result:
                    index_src +=1
        self.ihm.log("Amount of source files found: " + str(index_src),False)
        self.ihm.log("Amount of programming files found: " + str(index_prog),False)
    def _getAllDocuments(self,release,baseline,project):
        # Patch
        if project == "All":
            project = ""
        output = self.getArticles(self.list_type_doc,release,baseline,project,False)
        index_doc = 0
        index_input = 0
        index_plan = 0
        index_std = 0
        index_sas = 0
        index_seci = 0
        index_ccb = 0
        index_is = 0
        index_icd_protocol = 0
        index_icd_data = 0
        for line in output:
            line = re.sub(r"<void>",r"",line)
            self.ihm.log("Found doc: " + line,False)
            m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
            if m:
                # Look for IS first
                result = self._createTblInspectionSheets(m)
                if result:
                    index_is +=1
                else:
                    # Look for plans
                    result = self._createTblPlans(m)
                    if result:
                        index_plan +=1
                    else:
                        # Look for CCB minutes report
                        result = self._createTblCcb(m)
                        if result:
                            index_ccb +=1
                        else:
                            # Look for standards
                            result = self._createTblStds(m)
                            if result:
                                index_std +=1
                            else:
                                # Look for Software Accomplishment Summary
                                result = self._createTblSas(m)
                                if result:
                                    index_sas +=1
                                else:
                                    # Look for Software Environement Configuration Index
                                    result = self._createTblSeci(m)
                                    if result:
                                        index_seci +=1
                                    else:
                                        # Look for interface
                                        # m.group(2) is the filename
                                        # m.group(3) is the Synergy version
##                                        print "TEST",m.group(2),m.group(3),self.protocol_interface,self.data_interface_index
                                        if  self.protocol_interface in m.group(2):
                                            self.protocol_interface_index = m.group(3)
                                            index_icd_protocol +=1
                                        elif self.data_interface in m.group(2) :
                                            self.data_interface_index = m.group(3)
                                            index_icd_data +=1
                                        # Then input data (meaning not included in release)
                                        if release not in ("",None,"All","None"):
                                            result = self._createTblInputData(m,release)
                                        else:
                                            result = False
                                        if result:
                                            index_input +=1
                                        else:
                                            # Then all => self.tableau_items
                                            result = self._createTblDocuments(m)
                                            if result:
                                                index_doc +=1
        self.ihm.log("Amount of documents found: " + str(index_doc),False)
        self.ihm.log("Amount of input data found: " + str(index_input),False)
        self.ihm.log("Amount of inspection sheets found: " + str(index_is),False)
        self.ihm.log("Amount of plans found: " + str(index_plan),False)
        self.ihm.log("Amount of standards found: " + str(index_std),False)
        self.ihm.log("Amount of CCB minutes found: " + str(index_ccb),False)
        self.ihm.log("Amount of SAS found: " + str(index_sas),False)
        self.ihm.log("Amount of SECI found: " + str(index_seci),False)
        self.ihm.log("Amount of protocol interface document found: " + str(index_icd_protocol),False)
        self.ihm.log("Amount of ddata interface document found: " + str(index_icd_data),False)
    def isCodeOnly(self,baseline):
        '''
        Check baseline name for CODE keyword
        '''
        baseline_code_only = re.match(r'^CODE_(.*)',baseline)
        return baseline_code_only
    def _initTables(self):
        '''
        '''
        # Header for documents
        if self.getCIDType() not in ("SCI"):
            # FPGA
            # Header for sources
            header_soft_sources = ["Release:Project","Data","Issue","Tasks","Change Request"]
            header = ["Release:Project","Data","Issue","Tasks","Change Request"]
            self.tbl_build = []
            self.tbl_build.append(header)
            header = ["Release:Project","Document","Issue","Description","Tasks"]
            header_input = ["Release:Project","Document","Issue","Description","Tasks"]
            header_ccb_input = ["Release:Project","Document","Issue","Description","Tasks"]
            header_prr = header
        else:
            # software
            # Header for sources
            header_soft_sources = ["File Name","Version","Type","Instance","Release","CR"]
            self.tbl_build = []
            self.tbl_build.append(header_soft_sources)
            header_input = ["Title","Reference","Synergy Name","Version","Type","Instance","Release"]
            header_ccb_input = ["Title","Synergy Name","Version","Type","Instance","Release"]
            header = ["Title","Reference","Synergy Name","Version","Type","Instance","Release","CR"]
            header_prr = ["Name","Version","Release"]
        # Header for delivery
        header_delivery = ["File Name","Version","Type","Instance","Release"]
        tiny_header = ["Name","Version","Release"]
        self.tableau_items = []
        self.tbl_items_filtered = []
        self.tbl_items_filtered.append(header)
        self.tbl_input_data = []
        self.tbl_input_data.append(header_input)
        self.tbl_plans = []
        self.tbl_plans.append(header)
        self.tbl_stds = []
        self.tbl_stds.append(header)
        self.tbl_ccb = []
        self.tbl_ccb.append(header_ccb_input)
        self.tableau_prog = []
        self.tbl_program_file = []
        self.tbl_synthesis_file = []
        self.tbl_constraint_file = []
        self.tbl_synthesis_file.append(tiny_header)
        self.tbl_constraint_file.append(tiny_header)
        self.tbl_program_file.append(tiny_header)
        # Specific Software
        self.tbl_inspection_sheets = []
        self.tbl_sas = []
        self.tbl_seci = []
        self.tbl_sas.append(header)
        self.tbl_seci.append(header)
        # Split table of items with input data and peer reviews
        self.tbl_verif = []
        self.tbl_verif.append(header)
        self.tbl_peer_reviews = []
        self.tbl_peer_reviews.append(header_prr)
    def _removeDoublons(self,tbl_in):
        '''
        '''
        tbl_out = []
        for elt in tbl_in:
            if elt not in tbl_out:
                tbl_out.append(elt)
        return tbl_out
    def _initTablesSrc(self):
        '''
        '''
        # Header for documents
        header = ["Release:Project","Document","Issue","Description","Tasks"]
        # Header for delivery
        header_delivery = ["File Name","Version","Type","Instance","Release"]
        # Header for sources
        if self.cid_type == "SCI":
            # software
            header_soft_sources = ["File Name","Version","Type","Instance","Release","CR"]
        else:
            # FPGA
            header_soft_sources = ["Release:Project","Data","Issue","Tasks","Change Request"]
        self.tbl_build = []
        self.tbl_build.append(header_soft_sources)
##            tbl_sources.append(header)
        self.tbl_sources = []
        self.tbl_sources.append(header_soft_sources)
        self.tableau_items = []
##        self.tableau_items.append(header_soft_sources)
        self.tableau_prog = []
        self.tableau_src = []
        self.tbl_program_file = []
        self.tbl_synthesis_file = []
        self.tbl_constraint_file = []
        tiny_header = ["Name","Version","Release"]
        self.tbl_synthesis_file.append(tiny_header)
        self.tbl_constraint_file.append(tiny_header)
        self.tbl_program_file.append(tiny_header)
        # Specific Software
        self.tbl_sw_outputs = []
        self.tbl_sw_outputs.append(header_delivery)
        self.tbl_sw_eoc = []
        self.tbl_sw_eoc.append(header_delivery)
##        return tbl_sources
    def getSrcType(self):
        # Get expected type of sources according to CID type
        if self.cid_type == "SCI":
            list_type_src = self.list_type_src_sci
            self.ccb_type = "SCR"
        elif self.cid_type == "HCMR_PLD":
            list_type_src = self.list_type_src_hcmr
            self.ccb_type = "PLDCR"
        elif self.cid_type == "HCMR_BOARD":
            list_type_src = ()
            self.ccb_type = "HCR"
        else:
            self.ccb_type = "ALL"
            list_type_src = ()
##        print self.cid_type,list_type_src
        return list_type_src
    def _getInfo(self):
        global item   # Default
        if self.author == "":
            author = "Nobody"
        else:
            author = self.author
        if self.item != "":
            item = self.item
        if item == "":
            database,aircraft = self.get_sys_database()
            item = "Unidentified"
            item_description = "Unknown"
            ci_identification = "A000"
        else:
            database,aircraft = self.get_sys_item_database(self.system,item)
            if database == None:
                database,aircraft = self.get_sys_database()
            item_description = self.getItemDescription(item)
            ci_identification = self.get_ci_sys_item_identification(self.system,item)
        if aircraft != None and self.system != None:
            program = aircraft + " " + self.system
        else:
            program = None
        return author,item,database,aircraft,item_description,ci_identification,program
    def createCID(self,object_released=False,object_integrate=False):
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
        global item
        # start horizontal progress bar with refreshng rate of 1s
##        interface.success.pack_forget()
##        interface.pb_vd.pack(expand=True, fill=BOTH, padx=300,pady=10, side=LEFT)
##        interface.pb_vd.start(1000)
        self.ihm.success.config(fg='red',bg = 'yellow',text="GENERATION IN PROGRESS")
        self.object_released = object_released
        self.object_integrate = object_integrate
        self.list_type_src = self.getSrcType()
        # Prepare output file
        self._setOuptutFilename()
        #
        # Documentations
        #
        self.ihm.log("Items query in progress...")
        self.ihm.defill()
        self._initTables()
        # Header for documents
        if self.getCIDType() not in ("SCI"):
            header = ["Release:Project","Document","Issue","Description","Tasks"]
            line_empty_input = ["--","--","--","--","--"]
            line_empty = ["--","--","--","--","--"]
        else:
            line_empty_input = ["--","--","--","--","--","--","--"]
            line_empty = ["--","--","--","--","--","--","--","--"]
            header = ["Title","Reference","Synergy Name","Version","Type","Instance","Release","CR"]
        line_empty_three_columns = ["--","--","--"]
        table_input_data = []
        table_peer_reviews = []
        table_verif = []
        items_filter = [self.input_data_filter,self.peer_reviews_filter,self.verif_filter]
        #
        # Document part
        #
        # check if baseline name begin with CODE
        baseline_code_only = self.isCodeOnly(self.baseline)
        # self.tableau_items array is filled by invoking
        #
        # - _getAllDocuments
        # -     _getArticles
        #
        if baseline_code_only:
            print "Only code in baseline"
        else:
            #
            # Projects are available in GUI
            #
            if self.ihm.project_list != []:
                self.ihm.log("Use project set list to create CID for documents",False)
                # Project set in GUI
                for release,baseline,project in self.ihm.project_list:
                    self.ihm.log("Use release " + release,False)
                    self.ihm.log("Use baseline " + baseline,False)
                    self.ihm.log("Use project " + project,False)
                    self._getAllDocuments(release,baseline,project)
                    # finduse
                    l_table_input_data,l_table_peer_reviews,l_table_verif = self.getSpecificData(release,baseline,project,items_filter,False)
                    table_input_data.extend(l_table_input_data)
                    table_peer_reviews.extend(l_table_peer_reviews)
                    table_verif.extend(l_table_verif)
            else:
                self.ihm.log("Use invariant release and baseline to create CID for documents",False)
                self.ihm.log("Use release " + self.release,False)
                self.ihm.log("Use baseline " + self.baseline,False)
                #
                # Projects are available in Synergy
                # list_projects is filled when Update project button is pressed
                #
                if list_projects == []:
                    list_projects.append(self.project)
                # Get all documents
                # Find plans
                # Find Peer reviews or Inspection Sheets
                # Find documents in specific folder
                for project in list_projects:
                    self.ihm.log("Use project " + project,False)
                    self._getAllDocuments(self.release,self.baseline,project)
                    # finduse
                    l_table_input_data,l_table_peer_reviews,l_table_verif = self.getSpecificData(self.release,self.baseline,project,items_filter,False)
                    table_input_data.extend(l_table_input_data)
                    table_peer_reviews.extend(l_table_peer_reviews)
                    table_verif.extend(l_table_verif)
        if len(self.tableau_items) == 1:
                 self.tableau_items.append(line_empty)
        # Split table of items with input data and peer reviews
        # self.tbl_input_data array is filled by invoking
        #
        # - _getAllDocuments
        # -     _createTblInputData
        #
        # Get input data, peer reviews and verification documents found with Synergy finduse
        if self.getCIDType() not in ("SCI"):
            index = 1
        else:
            index = 2
        for doc in self.tableau_items:
            # index 2 correspond to Synergy name of the document
            if doc[index] in table_input_data:
                # remove last column regarding CR
                self.tbl_input_data.append(doc[0:7])
            elif doc[index] in table_peer_reviews:
                # remove last column regarding CR
                self.tbl_peer_reviews.append(doc[0:7])
            elif doc[index] in table_verif:
                self.tbl_verif.append(doc)
            else:
                self.tbl_items_filtered.append(doc)
        tbl_input_data = []
        # Add all input data found to input data
        tbl_input_data.extend(self.tbl_input_data)
        if len(tbl_input_data) == 1:
                 tbl_input_data.append(line_empty_input)
        self.tbl_input_data = self._removeDoublons(self.tbl_input_data)
        if len(self.tbl_verif) == 1:
                 self.tbl_verif.append(line_empty)
        if len(self.tbl_items_filtered) == 1:
                 self.tbl_items_filtered.append(line_empty)
        # Add all inspection sheets found to peer reviews
        self.tbl_peer_reviews.extend(self.tbl_inspection_sheets)
        # At least one line
        if len(self.tbl_peer_reviews) == 1:
            if self.getCIDType() not in ("SCI"):
                 self.tbl_peer_reviews.append(line_empty)
            else:
                 self.tbl_peer_reviews.append(line_empty_three_columns)
        # Enlever doublons dans les tableaux
        #
        # Sources part
        #
        # Header for sources
        line_empty = ["--","--","--","--","--"]
        self.display_attr = ' -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"' # %task_synopsis
        #
        # Source
        #
        self.ihm.log("Source code query in progress...")
        self.ihm.defill()
        tableau_sources_finduse = []
        tbl_build_finduse = []
        # Header
        self._initTablesSrc()
        # Split table of items with sources
        tbl_src_filtered = []
        items_filter = [self.sources_filter]
        programing_file = ""
        synthesis_file = ""
        constraint_file = ""
        l_tbl_program_file = []
        # Get projects from GUI
        if self.ihm.project_list != []:
            self.ihm.log("Use project set list to create CID for source code",False)
            for release,baseline,project in self.ihm.project_list:
                self.ihm.log("Use release " + release,False)
                self.ihm.log("Use baseline " + baseline,False)
                self.ihm.log("Use project " + project,False)
 #               self.tableau_items =self.getArticles(self.tableau_items,self.list_type_src,release,baseline,project,True)
                self._getAllSources(release,baseline,project)
                self._getAllProg(release,baseline,project)
                # Second chance to find sources in specific folder like SRC
                l_table_sources = self.getSpecificData(release,baseline,project,items_filter,True)
                tableau_sources_finduse.extend(l_table_sources)
                # For software get build script in specific folder BUILD
                l_tbl_program_file = self.getSpecificBuild(release,baseline,project)
                tbl_build_finduse.extend(l_tbl_program_file)
        else:
            self.ihm.log("Use invariant release and baseline to create CID for source code",False)
            release = self.release
            baseline = self.baseline
            project = self.project
            self.ihm.log("Use release " + release,False)
            self.ihm.log("Use baseline " + baseline,False)
            if list_projects == []:
                list_project.append(self.project)
            # Projects are available in Synergy
            # list_projects is filled when Update project button is pressed
            for project in list_projects:
                self.ihm.log("Use project " + project,False)
                # Project found from Synergy query
                self._getAllSources(release,baseline,project)
                self._getAllProg(release,baseline,project)
                # Finduse
                # Second chance to find sources in specific folder like SRC
                l_table_sources = self.getSpecificData(release,baseline,project,items_filter,True)
##                print "l_table_sources",l_table_sources
                tableau_sources_finduse.extend(l_table_sources)
##                print "tableau_sources_finduse",tableau_sources_finduse
                # For software get build script in specific folder BUILD
                l_tbl_program_file = self.getSpecificBuild(release,baseline,project)
                tbl_build_finduse.extend(l_tbl_program_file)
        # Source trouvé dans les repertoires attendus genre SRC ou VHDL
        if self.getCIDType() not in ("SCI"):
            index = 1
        else:
            index = 0
        if tableau_sources_finduse != []:
            for src in self.tableau_src:
                # index 0 correspond to Synergy name of the source file
                if src[index] in tableau_sources_finduse:
                    self.tbl_sources.append(src)
                else:
                    pass
        else:
            # par défault on prend tout
            self.tbl_sources.extend(self.tableau_src)
        # Scripts trouvés dans les repertoire attendus BUILD
        if tbl_build_finduse != []:
            for src in self.tableau_prog:
                if src[index] in tbl_build_finduse:
                    self.tbl_build.append(src)
                else:
                    pass
        else:
            self.tbl_build.extend(self.tableau_prog)
        #
        # Manage Problem Reports
        #
        self.ihm.log("Change Request query in progress...")
        self.ihm.defill()
        self.getPR()
        #
        # Manage array form for Word document
        #
        if self.getCIDType() not in ("SCI"):
            colw = [1000,2300,200,1000,500,500,500] # 5000 = 100%
            colw_ccb = [1000,2300,200,1000,1500] # 5000 = 100%
            line_src_empty = ["--","--","--","--","--"]
            line_ccb_empty = ["--","--","--","--","--"]
            line_other_empty = ["--","--","--","--","--"]
            fmt_prr =  {'heading': True,'colw': colw, # 5000 = 100%
                        'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                        }
            fmt_ccb =  {
                        'heading': True,'colw': colw_ccb, # 5000 = 100%
                        'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                        }
            fmt =  {'heading': True,'colw': colw, # 5000 = 100%
                        'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                        }
            fmt_small = {'heading': True,'colw': [500,3000,500,500,500,500], # 5000 = 100%
                            'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                        }
            fmt_tiny = {'heading': True,'colw': [4000,500,500], # 5000 = 100%
                            'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                            }
            fmt_tiny_sw = {'heading': True,'colw': [3000,500,500,500,500], # 5000 = 100%
                            'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                            }
        else:
            colw = [1000,2300,200,500,500,500,500,500] # 5000 = 100%
            line_src_empty = ["--","--","--","--","--","--"]
            line_ccb_empty = ["--","--","--","--","--","--","--"]
            line_other_empty = ["--","--","--","--","--","--","--","--"]
            fmt =  {'heading': True,'colw': colw, # 5000 = 100%
                        'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                        }
            fmt_ccb = fmt
            fmt_prr = {'heading': True,'colw': [4000,500,500], # 5000 = 100%
                        'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                        }
            fmt_small = {'heading': True,'colw': [500,3000,500,500,500,500], # 5000 = 100%
                            'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                        }
            fmt_tiny = {'heading': True,'colw': [4000,500,500], # 5000 = 100%
                            'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                            }
            fmt_tiny_sw = {
                            'heading': True,'colw': [3000,500,500,500,500], # 5000 = 100%
                            'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                            }
        self.tbl_peer_reviews = self._removeDoublons(self.tbl_peer_reviews)
        self.tbl_inspection_sheets = self._removeDoublons(self.tbl_inspection_sheets)
        self.tbl_sas = self._removeDoublons(self.tbl_sas)
        self.tbl_seci = self._removeDoublons(self.tbl_seci)
        self.tbl_sw_eoc_new = self._removeDoublons(self.tbl_sw_eoc)
        self.tbl_sw_outputs = self._removeDoublons(self.tbl_sw_outputs)
        self.tableau_prog = self._removeDoublons(self.tableau_prog)
        self.tableau_src = self._removeDoublons(self.tableau_src)
        self.tbl_build = self._removeDoublons(self.tbl_build)
        self.tbl_sources = self._removeDoublons(self.tbl_sources)
        self.tbl_plans = self._removeDoublons(self.tbl_plans)
        self.tbl_stds = self._removeDoublons(self.tbl_stds)
        self.tbl_ccb = self._removeDoublons(self.tbl_ccb)
        self.tbl_program_file = self._removeDoublons(self.tbl_program_file)
        self.tbl_synthesis_file = self._removeDoublons(self.tbl_synthesis_file)
        if len(self.tbl_program_file) == 1:
                 self.tbl_program_file.append(line_empty_three_columns)
        if len(self.tbl_synthesis_file) == 1:
                 self.tbl_synthesis_file.append(line_empty_three_columns)
        if len(self.tbl_inspection_sheets) == 1:
            self.tbl_inspection_sheets.append(line_empty)
        if len(self.tbl_sas) == 1:
            self.tbl_sas.append(line_other_empty)
        if len(self.tbl_seci) == 1:
            self.tbl_seci.append(line_other_empty)
        if len(self.tableau_prog) == 1:
            self.tableau_prog.append(line_empty)
        if len(self.tableau_src) == 1:
            self.tableau_src.append(line_empty)
        if len(self.tbl_sw_outputs) == 1:
            self.tbl_sw_outputs.append(line_empty)
        if len(self.tbl_sw_eoc) == 1:
            self.tbl_sw_eoc.append(line_empty)
        if len(self.tbl_build) == 1:
            self.tbl_build.append(line_src_empty)
        if len(self.tbl_sources) == 1:
            self.tbl_sources.append(line_src_empty)
        if len(self.tbl_plans) == 1:
            self.tbl_plans.append(line_other_empty)
        if len(self.tbl_stds) == 1:
            self.tbl_stds.append(line_other_empty)
        if len(self.tbl_ccb) == 1:
            self.tbl_ccb.append(line_ccb_empty)
        if len(self.tbl_constraint_file) == 1:
            self.tbl_constraint_file.append(line_empty_three_columns)
        # Prepare information to put instead of tags
        title = self.system + " "
        subject = self.system + " "
        if self.item != "":
            title += " " + self.item + " "
            subject += " " + self.item + " "
        doc_type = self.getTypeDocDescription(self.template_type)
        title += self.template_type
        subject += self.template_type
        # Releases
        release_text = "not defined"
        release_list = []
        # Baselines
        baseline_text = "not defined"
        baseline_list = []
        # Projects
        project_text = "The project is not defined"
        if self.ihm.project_list != []:
            text = ""
            for release,baseline,project in self.ihm.project_list:
                release_list.append(release)
                baseline_list.append(baseline)
                text +=  project + "\n, "
            # remove last comma
            project_text = text[0:-2]
        else:
            if len(list_projects) in (0,1) and self.project not in ("All",""):
                project_text = self.project
            else:
                text = ""
                for project in list_projects:
                    text += project + "\n, "
                # remove last comma
                project_text = text[0:-2]
        if release_list != []:
            text = ""
            # remove doublons
            list_unique = set(release_list)
            for release in list_unique:
                text += release + ", "
            # remove last comma
            release_text = text[0:-2]
        else:
            if self.release == "":
                release_text = "None"
            else:
                release_text = self.release
        if baseline_list != []:
            text = ""
            # remove doublons
            list_unique = set(baseline_list)
            for baseline in list_unique:
                if baseline == "All":
                    text += "None, "
                else:
                    text += baseline + ", "
            # remove last comma
            baseline_text = text[0:-2]
        else:
            if self.baseline == "All":
                baseline_text = "None"
            else:
                baseline_text = self.baseline
        author,item,database,aircraft,item_description,ci_identification,program = self._getInfo()
        # Replace some tags
        self.protocol_compat = "TDB"
        self.data_compat = "TDB"
        list_tags = {
                    'SUBJECT':{'type':'str','text':subject,'fmt':{}},
                    'TYPE':{'type':'str','text':doc_type,'fmt':{}},
                    'TITLE':{'type':'str','text':title,'fmt':{}},
                    'CI_ID':{'type':'str','text':ci_identification,'fmt':{}},
                    'REFERENCE':{'type':'str','text':self.reference,'fmt':{}},
                    'ISSUE':{'type':'str','text':self.revision,'fmt':{}},
                    'ITEM':{'type':'str','text':item,'fmt':{}},
                    'ITEM_DESCRIPTION':{'type':'str','text':item_description,'fmt':{}},
                    'DATE':{'type':'str','text':time.strftime("%d %b %Y", time.localtime()),'fmt':{}},
                    'PROJECT':{'type':'str','text':project_text,'fmt':{}},
                    'RELEASE':{'type':'str','text':release_text,'fmt':{}},
                    'PREVIOUS_BASELINE':{'type':'str','text':self.previous_baseline,'fmt':{}},
                    'BASELINE':{'type':'str','text':baseline_text,'fmt':{}},
                    'WRITER':{'type':'str','text':author,'fmt':{}},
                    'PART_NUMBER':{'type':'str','text':self.part_number,'fmt':{}},
                    'BOARD_PART_NUMBER':{'type':'str','text':self.board_part_number,'fmt':{}},
                    'CHECKSUM':{'type':'str','text':self.checksum,'fmt':{}},
                    'DATABASE':{'type':'str','text':database,'fmt':{}},
                    'PROGRAM':{'type':'str','text':program,'fmt':{}},
                    'FUNCCHG':{'type':'par','text':self.func_chg,'fmt':{}},
                    'OPCHG':{'type':'par','text':self.oper_chg,'fmt':{}},
                    'PROTOCOL_COMPAT':{'type':'str','text':self.protocol_interface_index,'fmt':{}},
                    'DATA_COMPAT':{'type':'str','text':self.data_interface_index,'fmt':{}},
                    'OPCHG':{'type':'par','text':self.oper_chg,'fmt':{}},
                    'TABLEITEMS':{'type':'tab','text':self.tbl_items_filtered,'fmt':fmt},
                    'TABLEINPUTDATA':{'type':'tab','text':tbl_input_data,'fmt':fmt},
                    'TABLEPEERREVIEWS':{'type':'tab','text':self.tbl_peer_reviews,'fmt':fmt_prr},
                    'TABLESOURCE':{'type':'tab','text':self.tbl_sources,'fmt':fmt},
                    'TABLEBUILD':{'type':'tab','text':self.tbl_build,'fmt':fmt},
                    'TABLEEOC':{'type':'tab','text':self.tbl_sw_eoc_new,'fmt':fmt_tiny_sw},
                    'TABLEEOCID':{'type':'tab','text':self.tbl_sw_eoc_new,'fmt':fmt_tiny_sw},
                    'TABLEOUPUTS':{'type':'tab','text':self.tbl_sw_outputs,'fmt':fmt_tiny_sw},
                    'TABLEVERIF':{'type':'tab','text':self.tbl_verif,'fmt':fmt},
                    'TABLEPLAN':{'type':'tab','text':self.tbl_plans,'fmt':fmt},
                    'TABLESTD':{'type':'tab','text':self.tbl_stds,'fmt':fmt},
                    'TABLECCB':{'type':'tab','text':self.tbl_ccb,'fmt':fmt_ccb},
                    'TABLESAS':{'type':'tab','text':self.tbl_sas,'fmt':fmt},
                    'TABLESECI':{'type':'tab','text':self.tbl_seci,'fmt':fmt_ccb},
                    'TABLEPRS':{'type':'tab','text':self.tableau_pr,'fmt':fmt_small},
                    'TABLECLOSEPRS':{'type':'tab','text':self.tableau_closed_pr,'fmt':fmt_small},
                    'TABLEOPR':{'type':'tab','text':self.tableau_opened_pr,'fmt':fmt_small},
                    'PROGRAMING_FILE':{'type':'tab','text':self.tbl_program_file,'fmt':fmt_tiny},
                    'SYNTHESIS_FILES':{'type':'tab','text':self.tbl_synthesis_file,'fmt':fmt_tiny},
                    'CONSTRAINT_FILES':{'type':'tab','text':self.tbl_constraint_file,'fmt':fmt_tiny}
                    }
        image_name = self.get_image(self.aircraft)
        self.docx_filename,exception = self._createDico2Word(list_tags,self.template_name,self.docx_filename,image_name)
        self.ihm.success.config(fg='magenta',bg = 'green',text="GENERATION SUCCEEDED")
        return self.docx_filename,exception
    def _getSpecificCR(self):
        '''
        To get info form a CR, TBD
        '''
        global session_started
        tableau_pr = []
        # Header
        tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis"])
        if session_started and cr_status != None:
    ##        proc = Popen(self.ccm_exe + ' query -sby crstatus -f "%problem_number;%problem_synopsis;%crstatus" "(cvtype=\'problem\') and ((crstatus=\'concluded\') or (crstatus=\'entered\') or (crstatus=\'in_review\') or (crstatus=\'assigned\') or (crstatus=\'resolved\') or (crstatus=\'deferred\'))"', stdout=PIPE, stderr=PIPE)
            query_root = 'query -sby crstatus  '
            condition = '"(cvtype=\'problem\')'
            old_cr_workflow = self.ihm.getTypeWorkflow()
            if old_cr_workflow:
                detection_word = "detected_on"
                impl_word = "implemented_in"
            else:
                detection_word = "CR_detected_on"
                impl_word = "CR_implemented_for"
            # detected
            if self.detect_release != "":
                condition += ' and '
                condition += self._createImpl(detection_word,self.detect_release)
            # implemnted
            if self.impl_release != "":
                condition += ' and '
                condition += self._createImpl(impl_word,self.impl_release)
            if cr_status != "":
                condition +=  ' and (crstatus=\''+ cr_status +'\') '
                condition_func_root = condition
                condition += '" '
            else:
                sub_cond = self.getStatusCheck()
                #gros patch
                condition += sub_cond[19:]
            condition_func_root = condition[0:-2]
##            condition = condition + '" '
    ##        query = 'query -sby crstatus "(cvtype=\'problem\') and (implemented_in=\''+ self.release +'\')" -f "%problem_number;%problem_synopsis;%crstatus;%detected_on;%implemented_in"'
            query = query_root + condition + '-f "%problem_number;%CR_type;%problem_synopsis;%crstatus;%CR_detected_on;%submitter;%resolver;%CR_implemented_for;%modify_time"' # ;%CR_functional_impact
            stdout,stderr = self.ccm_query(query,"Get PRs")
            self.ihm.log(query + " completed.")
            if stdout != "":
                output = stdout.splitlines()
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                    m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
                    if m:
                        cr_type = m.group(2)
                        synopsis = m.group(3)
                        cr_status = m.group(4)
                        print "TEST",cr_status
                        status_m = re.match(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)',cr_status)
                        if status_m:
                            domain = status_m.group(1)
                            status = status_m.group(2)
                        else:
                            domain = ""
                            status = cr_status
                        cr_id = m.group(1)
                        # Find functional limitation
                        func_impact = ""
                        condition_func = condition_func_root + ' and (problem_number = \'' + cr_id + '\')" '
                        query = query_root + ' -u ' + condition_func + '-f "%CR_functional_impact"'
                        func_impact,stderr = self.ccm_query(query,"Get PRs")
                        self.ihm.log(query + " completed.")
##                        print func_impact
                        # remove ASCI control character
                        filtered_func_impact = filter(string.printable[:-5].__contains__,func_impact)
                        #remove <void>
                        filtered_func_impact = re.sub(r"<void>",r"",filtered_func_impact)
                        #remove br/
                        filtered_func_impact = re.sub(r"br/",r"",filtered_func_impact)
                        print "Functional impact:",filtered_func_impact
##                        m = re.match(r'(.*)',line)
                        # Explode status by removing prefix
                        # Print pretty status self.ccb_type
                        status = re.sub(self.ccb_type+"_","",m.group(4))
                        tableau_pr.append([domain,cr_type,cr_id,status,synopsis])
                    else:
                        # Remove ASCII control characters
                        filtered_line = filter(string.printable[:-5].__contains__,line)
                        print "Functional impact:",filtered_line
                        tableau_pr.append(["","","","",""])
            if len(tableau_pr) == 1:
                 tableau_pr.append(["--","--","--","--","--"])
        else:
            tableau_pr.append(["--","--","--","--","--"])
        # Set scrollbar at the bottom
        self.ihm.defill()
        return(tableau_pr)
    def getPR_CCB(self,cr_status="",for_review=False,cr_with_parent=False):
        '''
        Create CR table for CCB minutes from Synergy query
        Useful Change keywords:
            %CR_detected_on
            %CR_implemented_for
            %problem_number
            %problem_synopsis
            %crstatus
            %CR_ECE_classification => Showstopper, etc.
            %CR_request_type => Defect or Evolution
            %CR_type => SW_ENM, SW_BITE, SW_WHCC, SW_PLAN etc...
            %CR_domain => EXCR, SCR, PLCDCR etc.
            %modify_time
        '''
        global session_started
        tableau_pr = []
        # Header
        if session_started and cr_status != None:
    ##        proc = Popen(self.ccm_exe + ' query -sby crstatus -f "%problem_number;%problem_synopsis;%crstatus" "(cvtype=\'problem\') and ((crstatus=\'concluded\') or (crstatus=\'entered\') or (crstatus=\'in_review\') or (crstatus=\'assigned\') or (crstatus=\'resolved\') or (crstatus=\'deferred\'))"', stdout=PIPE, stderr=PIPE)
            query_root = 'query -sby crstatus  '
            condition = '"(cvtype=\'problem\')'
            old_cr_workflow = self.ihm.getTypeWorkflow()
            if old_cr_workflow:
                detection_word = "detected_on"
                impl_word = "implemented_in"
            else:
                detection_word = "CR_detected_on"
                impl_word = "CR_implemented_for"
            # detected
            if self.detect_release != "":
                condition += ' and '
                condition += self._createImpl(detection_word,self.detect_release)
            # implemented
            if self.impl_release != "":
                condition += ' and '
                condition += self._createImpl(impl_word,self.impl_release)
            # cr type already done in _createConditionStatus
##            if self.cr_type != "":
##                condition += ' and '
##                print "cr_type",self.cr_type
##                condition += self._createImpl("CR_type",self.cr_type)
            if cr_status != "":
                condition +=  ' and (crstatus=\''+ cr_status +'\') '
                condition_func_root = condition
                condition += '" '
            else:
                sub_cond = self.getStatusCheck()
                #gros patch
                condition += sub_cond[19:]
            condition_func_root = condition[0:-2]
##            condition = condition + '" '
    ##        query = 'query -sby crstatus "(cvtype=\'problem\') and (implemented_in=\''+ self.release +'\')" -f "%problem_number;%problem_synopsis;%crstatus;%detected_on;%implemented_in"'
            # Ajouter la gestion de l'ancien workflow
            query = query_root + condition + '-f "%problem_number;%CR_type;%problem_synopsis;%crstatus;%CR_ECE_classification;%CR_request_type;%CR_domain;%CR_detected_on;%CR_implemented_for"' # ;%CR_functional_impact
            stdout,stderr = self.ccm_query(query,"Get PRs")
            self.ihm.log(query + " completed.")
            if stdout != "":
                output = stdout.splitlines()
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                    m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
                    if m:
                        cr_type = m.group(2)
                        # remove ASCI control character
                        cr_synopsis = filter(string.printable[:-5].__contains__,m.group(3))
##                        cr_synopsis = m.group(3)
                        cr_status = m.group(4)
                        cr_request_type = m.group(6)
                        cr_domain = m.group(7)
                        cr_detected_on = m.group(8)
                        cr_implemented_for = m.group(9)
                        if cr_request_type == "Evolution":
                            cr_severity = "N/A"
                        else:
                            cr_severity = m.group(5)
                        status_m = re.match(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)',cr_status)
                        if status_m:
                            cr_domain = status_m.group(1)
                            status = status_m.group(2)
                        else:
                            domain = cr_domain
                            status = cr_status
                        cr_id = m.group(1)
##                        print "Avail", self.list_cr_for_ccb_available
##                        print "list",self.list_cr_for_ccb
                        info_parent_cr = ""
                        if cr_with_parent:
                            parent_cr_id = self._getParentCR(cr_id)
                            if parent_cr_id:
                                #
                                # Get parent ID informations
                                #
                                parent_cr = self._getParentInfo(parent_cr_id)
                                if parent_cr:
                                    parent_decod = self._parseCRParent(parent_cr)
                                    print "parent_decod",parent_decod
                                    text = self.removeNonAscii(parent_decod[4])
                                    parent_status = self.discardCRPrefix(parent_decod[3])
                                    info_parent_cr = "{:s} {:s} {:s}: {:s} [{:s}]".format(parent_decod[0],parent_decod[1],parent_decod[2],text,parent_status)
                                else:
                                    info_parent_cr = ""
                        if self.list_cr_for_ccb_available:
                            if cr_id in self.list_cr_for_ccb:
                                if self.ccb_type == "SCR":
                                    if for_review:
                                        tableau_pr.append([cr_id,cr_synopsis,cr_severity,status,info_parent_cr])
                                    else:
                                        tableau_pr.append([cr_domain,cr_type,cr_id,status,cr_synopsis,cr_severity])
                                else:
                                    tableau_pr.append([cr_domain,cr_type,cr_id,status,cr_synopsis,cr_severity,cr_detected_on,cr_implemented_for])
                            else:
                                print "CR discarded",cr_id
                        else:
                            self.list_cr_for_ccb.append(cr_id)
                            if self.ccb_type == "SCR":
                                if for_review:
                                    tableau_pr.append([cr_id,cr_synopsis,cr_severity,status,info_parent_cr])
                                else:
                                    tableau_pr.append([cr_domain,cr_type,cr_id,status,cr_synopsis,cr_severity])
                            else:
                                tableau_pr.append([cr_domain,cr_type,cr_id,status,cr_synopsis,cr_severity,cr_detected_on,cr_implemented_for])
                    else:
                        # Remove ASCII control characters
                        filtered_line = filter(string.printable[:-5].__contains__,line)
                        print "Functional impact:",filtered_line
                        if self.ccb_type == "SCR":
                            if for_review:
                                tableau_pr.append(["","","","",""])
                            else:
                                tableau_pr.append(["","","","","",""])
                        else:
                            tableau_pr.append(["","","","","","","",""])
        if len(tableau_pr) == 0:
            if self.ccb_type == "SCR":
                if for_review:
                    tableau_pr.append(["--","--","--","--","--"])
                else:
                    tableau_pr.append(["--","--","--","--","--","--"])
            else:
                tableau_pr.append(["--","--","--","--","--","--","--","--"])
##        else:
##            if self.ccb_type == "SCR":
##                tableau_pr.append(["--","--","--","--","--","--"])
##            else:
##                tableau_pr.append(["--","--","--","--","--","--","--","--"])
        # Set scrollbar at the bottom
        self.ihm.defill()
        return(tableau_pr)
    def getPR_Log(self,cr_status=""):
        global session_started
        tableau_pr = []
        # Header
        tableau_pr.append(["id","Log"])
        if session_started and cr_status != None:
    ##        proc = Popen(self.ccm_exe + ' query -sby crstatus -f "%problem_number;%problem_synopsis;%crstatus" "(cvtype=\'problem\') and ((crstatus=\'concluded\') or (crstatus=\'entered\') or (crstatus=\'in_review\') or (crstatus=\'assigned\') or (crstatus=\'resolved\') or (crstatus=\'deferred\'))"', stdout=PIPE, stderr=PIPE)
            query = 'query -sby crstatus '
            condition = '"(cvtype=\'problem\') '
            if self.release not in ("","All"):
                condition = condition + ' and (CR_implemented_for=\''+ self.release +'\') '
            if cr_status != "":
                condition = condition + ' and (crstatus=\''+ cr_status +'\') '
            condition = condition + '" '
    ##        query = 'query -sby crstatus "(cvtype=\'problem\') and (implemented_in=\''+ self.release +'\')" -f "%problem_number;%problem_synopsis;%crstatus;%detected_on;%implemented_in"'
            query = query + condition + '-f "%problem_number;%transition_log"'
            stdout,stderr = self.ccm_query(query,"Get PRs")
            self.ihm.log(query + " completed.")
            if stdout != "":
                output = stdout.splitlines()
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                    m = re.match(r'(.*);(.*)',line)
                    if m:
                        tableau_pr.append([m.group(1),m.group(2)])
                    else:
                        # Remove ASCII control characters
                        filtered_line = filter(string.printable[:-5].__contains__,line)
                        tableau_pr.append(["",filtered_line])
            if len(tableau_pr) == 1:
                 tableau_pr.append(["--","--"])
        else:
            tableau_pr.append(["--","--"])
        return tableau_pr

    def _getListCRForCCB(self):
        '''
        Get list of CR to take into account in the CCB minutes
        from the CR list box
        '''
        index_list_crs = self.ihm.crlistbox.curselection()
        list_cr_for_ccb = []
        for cr_index in index_list_crs:
            if cr_index != ():
                cr = self.ihm.crlistbox.get(cr_index)
                print "CR",cr
                m = re.match(r'^([0-9]*)\) (.*)$',cr)
                if m:
                    cr_id = m.group(1)
                else:
                    pass
                list_cr_for_ccb.append(cr_id)
                self.ihm.log("CR in CCB scope: " + cr_id)
        if list_cr_for_ccb == []:
            self.list_cr_for_ccb_available = False
        else:
            self.list_cr_for_ccb_available = True
        return list_cr_for_ccb
    def _getCRStatus(self,cr_id):
        cr_status = ""
        for pr in self.tableau_pr:
            if pr[2] == cr_id:
                cr_status = pr[3]
                break
        return cr_status
    def _getSeverity(self,cr):
        scores_default = {'Blocking': 1, 'Major': 2, 'Minor': 3, 'Enhancement': 4 , 'N/A' : 5}
        scores_sw = {'Showstopper': 1, 'Severe': 2, 'Medium': 3, 'Minor': 4 , 'N/A' : 5}
        if self.ccb_type == "SCR":
            scores = scores_sw
        else:
            scores = scores_default
        if cr[5] in scores:
            return scores[cr[5]]
        else:
            return 5
    def createChecklist(self,domain):
        #
        # Checklist
        #
        dico_cr_checklist ={'domain':domain}
        for cr_id in self.list_cr_for_ccb:
            cr_status = self._getCRStatus(cr_id)
            if domain == "SCR":
                tbl_chk = self._getCRChecklist(cr_status)
            else:
                tbl_chk = self._getCRChecklist(cr_status,sw=False)
            if tbl_chk != None:
                table_cr_checklist = []
                table_cr_checklist.append(["Check","Status","Remark"])
                for chk_item in tbl_chk:
                    table_cr_checklist.append([chk_item[0],"",""])
                # Add generic tokens
                if len(table_cr_checklist) == 1:
                    table_cr_checklist.append(["--","--","--"])
                dico_cr_checklist['checklist',cr_id] = table_cr_checklist
        return dico_cr_checklist

    def createCCB(self):
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
        self.ihm.success.config(fg='red',bg = 'yellow',text="GENERATION IN PROGRESS")
        self.list_cr_for_ccb = self._getListCRForCCB()
        self.ccb_type = self.ihm.ccb_var_type.get()
        self.detect_release = self.ihm.previous_release
        self.impl_release = self.ihm.impl_release
        self.cr_type = self.ihm.cr_type
        # CR list created based on array self.tableau_pr
        tableau_pr_unsorted = self.getPR_CCB()
        tableau_pr_sorted = sorted(tableau_pr_unsorted,key=self._getSeverity)
        if self.ccb_type == "SCR":
            self.tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity"])
        else:
            self.tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity","Dectected on","Implemented for"])
        self.tableau_pr.extend(tableau_pr_sorted)
        log_on = self.ihm.log_on_var.get()
        if log_on:
            tableau_log = self.getPR_Log()
        else:
            tableau_log = []
            tableau_log.append(["id","Log"])
            tableau_log.append(["--","--"])
        table_cr_undefined = []
        table_cr_undefined.append(["id","Type","Synopsis","Status","Detected on","Implemented in","Modified time","Functional impact"])
        #
        # Checklist
        #
        dico_cr_checklist = self.createChecklist(self.ccb_type)
##        dico_cr_checklist ={'domain':self.ccb_type}
##        for cr_id in self.list_cr_for_ccb:
##            cr_status = self._getCRStatus(cr_id)
##            if self.ccb_type == "SCR":
##                tbl_chk = self._getCRChecklist(cr_status)
##            else:
##                tbl_chk = self._getCRChecklist(cr_status,sw=False)
##            if tbl_chk != None:
##                table_cr_checklist = []
##                table_cr_checklist.append(["Check","Status","Remark"])
##                for chk_item in tbl_chk:
##                    table_cr_checklist.append([chk_item[0],"",""])
##                # Add generic tokens
##                if len(table_cr_checklist) == 1:
##                    table_cr_checklist.append(["--","--","--"])
##                dico_cr_checklist['checklist',cr_id] = table_cr_checklist
        #
        # Annex
        #
        list_cr_annex = []
        num_begin = ord("a")
        num_end = ord("z")
        num = num_begin
        prefix = ""
        for cr_id in self.list_cr_for_ccb:
            line = prefix + chr(num) + ") Extract " + self.ccb_type + "-" + cr_id
            num += 1
            if num > num_end:
                prefix += "a"
                num = num_begin
            list_cr_annex.append((line,'rb'))
            list_cr_annex.append(('','r'))
        #
        # Action_items
        #
        tbl_actions = []
        tbl_actions.append(["Action ID","Context","Description","Assignee","Date open"])
        list_action_items = self.ihm.getActionItem("",1) # Only action items open
        if list_action_items:
            for action_item in list_action_items:
                print "Action",action_item
                tbl_actions.append(["{:d}".format(action_item[0]),action_item[2],action_item[1],action_item[3],action_item[4]])
        template_type = "CCB"
        item_description = self.getItemDescription(self.item)
        ci_identification = self.get_ci_sys_item_identification(self.system,self.item)
        title = self.system
        subject = self.system
        if self.item != "":
            title += " " + self.item + " " + template_type
            subject += " " + self.item + " " + self.getTypeDocDescription(template_type)
        else:
            title += " " + self.template_type
            subject += " " + self.getTypeDocDescription(self.template_type)
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
        colw_actions = [500,1000,3000,1000,500]
        if self.ccb_type == "SCR":
            colw_pr = [500,     # Domain
                        500,    # CR Type
                        500,    # ID
                        500,    # Synopsis
                        2500,
                        500] # 5000 = 100%
        else:
            colw_pr = [500,     # Domain
                        500,    # CR Type
                        500,    # ID
                        500,    # Synopsis
                        1500,
                        500,500,500] # 5000 = 100%
        fmt_pr =  {
                    'heading': True,
                    'colw': colw_pr, # 5000 = 100%
                    'cwunit': 'pct',
                    'tblw': 5000,
                    'twunit': 'pct',
                    'borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }
        fmt_actions =  {
                    'heading': True,
                    'colw': colw_actions, # 5000 = 100%
                    'cwunit': 'pct',
                    'tblw': 5000,
                    'twunit': 'pct',
                    'borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }
        colw_chk = [3000,    # Check
                    500,    # Status
                    1000]    # Remark
        fmt_chk =  {
                    'heading': True,
                    'colw': colw_chk, # 5000 = 100%
                    'cwunit': 'pct',
                    'tblw': 5000,
                    'twunit': 'pct',
                    'borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }
        colw_log = [500,4500] # 5000 = 100%
        fmt_log =  {
                    'heading': True,
                    'colw': colw_log, # 5000 = 100%
                    'cwunit': 'pct',
                    'tblw': 5000,
                    'twunit': 'pct',
                    'borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }
        list_tags = {
                    'SUBJECT':{'type':'str','text':subject,'fmt':{}},
                    'TITLE':{'type':'str','text':title,'fmt':{}},
                    'CI_ID':{'type':'str','text':ci_identification,'fmt':{}},
                    'REFERENCE':{'type':'str','text':self.reference,'fmt':{}},
                    'ISSUE':{'type':'str','text':self.revision,'fmt':{}},
                    'ITEM':{'type':'str','text':self.item,'fmt':{}},
                    'ITEM_DESCRIPTION':{'type':'str','text':item_description,'fmt':{}},
                    'DATE':{'type':'str','text':time.strftime("%d %b %Y", time.localtime()),'fmt':{}},
                    'PROJECT':{'type':'str','text':project_text,'fmt':{}},
                    'RELEASE':{'type':'str','text':self.release,'fmt':{}},
                    'BASELINE':{'type':'str','text':self.baseline,'fmt':{}},
                    'WRITER':{'type':'str','text':self.author,'fmt':{}},
                    'COPIES':{'type':'str','text':"Nobody",'fmt':{}},
                    'MISSING':{'type':'str','text':"Nobody",'fmt':{}},
                    'TABLECHECKLIST':{'type':'mix','text':dico_cr_checklist,'fmt':fmt_chk},
                    'TABLEPRS':{'type':'tab','text':self.tableau_pr,'fmt':fmt_pr},
                    'PREVIOUS_ACTIONS':{'type':'tab','text':tbl_actions,'fmt':fmt_actions},
                    'TABLELOGS':{'type':'tab','text':tableau_log,'fmt':fmt_log},
                    'TABLEANNEX':{'type':'par','text':list_cr_annex,'fmt':{}}
                        }
        docx_filename = self.system + "_" + self.item + "_" + template_type + "_Minutes_" + self.reference + "_%f" % time.time() + ".docx"
        template_name = self._getTemplate(template_type)
        self.docx_filename,exception = self._createDico2Word(list_tags,template_name,docx_filename)
        self.ihm.success.config(fg='magenta',bg = 'green',text="GENERATION SUCCEEDED")
        return self.docx_filename,exception

    def _clearDicofound(self):
        self.dico_found = {}
    def _getDicoFound(self,key,type_doc):
        if (key,type_doc) in self.dico_found:
            doc = self.dico_found[(key,type_doc)]
        else:
            doc = False
        return(doc)

    def createReviewReport(self,type_review="SCR"):
        '''
        Create review report using docx module
        '''
        target_release = self.ihm.previous_release
        release = self.ihm.release
        baseline =  self.ihm.baseline
##        baseline_deliv = self.ihm.baseline_deliv_entry.get()

        sci_doc = "None"
        seci_doc = "None"
        sas_doc = "None"
        sci_is = "None"
        seci_is = "None"
        sas_is = "None"
        # List of attendees
        tbl_attendees = []
        tbl_attendees.append(["Olivier Appere","SQA manager"])
        # List of missing
        tbl_missing = []
        tbl_missing.append(["David Bailleul","Board manager"])
        # List of copies
        tbl_copies = []
        tbl_copies.append(["Marc Maufret","QA team leader"])
        # List CR for review
        # A modifier pour avoir le tableau correct
        self.ccb_type = "SCR"#self.ihm.ccb_var_type.get()
        self.detect_release = self.ihm.previous_release
        self.impl_release = self.ihm.impl_release
        self.cr_type = self.ihm.cr_type
        self.list_cr_for_ccb = self._getListCRForCCB()
        tbl_cr = self.getPR_CCB("",True)
        tableau_pr = []
##        if self.ccb_type == "SCR":
        tableau_pr.append(["CR ID","Synopsis","Severity","Status","Comment/Impact/Risk"])
##            tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity"])
##        else:
##            tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity","Dectected on","Implemented for"])
##        tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity"])
        tableau_pr.extend(tbl_cr)
        # Liste d'actions vierge
        # Accès base MySQL QAMS ?
        tbl_actions = []
        tbl_actions.append(["Action item ID","Origin","Action","Impact","Severity","Assignee","Closure due date","Status","Closing proof"])
        tbl_actions.append(["--","--","--","--","--","--","--","--","--"])
        if self.ihm.component != "":
            ci_identification = self.getComponentID(self.ihm.component)
        else:
            ci_identification = self.get_ci_sys_item_identification(self.system,self.item)
        date_meeting = time.strftime("%d %b %Y", time.localtime())
        review_number = self.ihm.var_review_type.get()
        print "var_review_type",review_number
        colw_pr = [500,     # Domain
                    2000,    # CR Type
                    500,    # ID
                    500,    # Synopsis
                    500,
                    1000] # 5000 = 100%
        colw_action = [500,     # Domain
                    500,    # CR Type
                    500,    # ID
                    500,    # Synopsis
                    2500,
                    500,500,500,500] # 5000 = 100%
        fmt_pr =  {
                    'heading': True,
                    'colw': colw_pr, # 5000 = 100%
                    'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }
        fmt_action =  {
                    'heading': True,
                    'colw': colw_action, # 5000 = 100%
                    'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }
        fmt_two =  {
                    'heading': False,
                    'colw': [2000,3000], # 5000 = 100%
                    'cwunit': 'pct','tblw': 5000,'twunit': 'pct'
                    }
        fmt_one =  {
                    'heading': False,
                    'colw': [500,4500], # 5000 = 100%
                    'cwunit': 'pct','tblw': 5000,'twunit': 'pct'
                    }
        self._clearDicofound()
        self.object_released = False
        self.object_integrate = False
        self.tbl_inspection_sheets = []
        part_number = self.ihm.part_number_entry.get()
        checksum = self.ihm.checksum_entry.get()
        subject = self.getReviewList(review_number)
        dico_plan_doc = {"PSAC":"Plan for Software Aspect of Certification",
                    "SDP":"Software Development Plan",
                    "SVP":"Software Verificaiton Plan",
                    "SCMP":"Software Configuration Management Plan",
                    "SQAP":"Software Quality Assurance Plan",
                    "SRTS":"Software Requirement Test Standard",
                    "SDTS":"Software Design Test Standard",
                    "SCS":"Software Coding Standard"}
        dico_sas = {"SAS":"Software Accomplishment Summary"}
        dico_sci = {"SCI":"Software Configuration Index"}
        dico_seci = {"SECI":"Software Environment Configuration Index"}

        dico_is = {"IS_PSAC":"PSAC Inspection Sheet",
                        "IS_SDP":"SDP Inspection Sheet",
                        "IS_SVP":"SVP Inspection Sheet",
                        "IS_SCMP":"SVP Inspection Sheet",
                        "IS_SQAP":"SQAP Inspection Sheet",
                        "IS_SCI":"SCI Inspection Sheet",
                        "IS_SAS":"SAS Inspection Sheet",
                        "IS_SECI":"SECI Inspection Sheet"}
        psac_doc = []
        sdp_doc = "No " + dico_plan_doc["SDP"]
        svp_doc = "No " + dico_plan_doc["SVP"]
        scmp_doc = "No " + dico_plan_doc["SCMP"]
        sqap_doc = "No " + dico_plan_doc["SQAP"]
        srts_doc = ""
        sdts_doc = ""
        scs_doc = ""
        project_list = []
        if self.ihm.project_list == []:
            project_list.append([release,baseline,""])
        else:
            project_list = self.ihm.project_list
        if review_number == 9: # SCR
            review_string = "SCR"
            # Documents and inspections
            # For SAS and SCI
            index_sci = 0
            index_sas = 0
            index_is = 0

            sci_doc = "No " + dico_sci["SCI"]
            sas_doc = "No " + dico_sas["SAS"]
            self.tbl_inspection_sheets = []
            index_seci = 0
            index_is = 0
            index_log = 0
            index_plans = 0
            dico_log = {"checksum":"checksum"}
            make_log = "No " + dico_log["checksum"]
            seci_doc = "No " + dico_seci["SECI"]

            # Project set in GUI
            baseline_doc = ""
            release_doc = ""
            for release,baseline,project in project_list:
                output = self.getArticles(("pdf","doc","xls","ascii"),release,baseline,project,False)
                baseline_doc += baseline + "\n"
                release_doc += release + "\n"
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    self.ihm.log("Found doc: " + line,False)
                    m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
                    if m:
                        # Look for IS first
                        result = self._getDoc(m,dico_is)
                        if result:
                            index_is +=1
                            doc  = self._getDicoFound("IS_SAS","xls")
                            if doc:
                                sas_is  = doc
                            doc  = self._getDicoFound("IS_SCI","xls")
                            if doc:
                                sci_is  = doc
                            doc  = self._getDicoFound("IS_SECI","xls")
                            if doc:
                                seci_is  = doc
                        # Look for Software Accomplishment Summary
                        result = self._getDoc(m,dico_sas)
                        if result:
                            index_sas +=1
                            sas_doc  = self._getDicoFound("SAS","doc")
                        # Look for Software Environement Configuration Index
                        result = self._getDoc(m,dico_sci)
                        if result:
                            index_sci +=1
                            sci_doc  = self._getDicoFound("SCI","doc")
                        # Look for Software Environement Configuration Index
                        result = self._getDoc(m,dico_seci)
                        if result:
                            index_seci +=1
                            doc  = self._getDicoFound("SECI","doc")
                            if doc:
                                seci_doc  = doc
                        # Look for compilation log
                        result = self._getDoc(m,dico_log)
                        if result:
                            index_log +=1
                            doc  = self._getDicoFound("checksum","ascii")
                            if doc:
                                make_log = doc
                        result = self._getDoc(m,dico_plan_doc)
                        if result:
                            index_plans += 1
                            doc  = self._getDicoFound("PSAC","doc")
                            if doc:
                                psac_doc.append(doc)
                            doc  = self._getDicoFound("SDP","doc")
                            if doc:
                                sdp_doc  = doc
                            doc  = self._getDicoFound("SVP","doc")
                            if doc:
                                svp_doc  = doc
                            doc  = self._getDicoFound("SCMP","doc")
                            if doc:
                                scmp_doc  = doc
                            doc  = self._getDicoFound("SQAP","doc")
                            if doc:
                                sqap_doc  = doc
                            doc  = self._getDicoFound("SRTS","pdf")
                            if doc:
                                srts_doc  = doc
                            doc  = self._getDicoFound("SDTS","pdf")
                            if doc:
                                sdts_doc  = doc
                            doc  = self._getDicoFound("SCS","pdf")
                            if doc:
                                scs_doc  = doc
            self.ihm.log("Amount of inspection sheets found: " + str(index_is),False)
            self.ihm.log("Amount of SCI found: " + str(index_sci),False)
            self.ihm.log("Amount of SAS found: " + str(index_sas),False)
            self.ihm.log("Amount of SECI found: " + str(index_seci),False)
            self.ihm.log("Amount of plans found: " + str(index_plans),False)
            self.ihm.log("Amount of checksum log found: " + str(index_log),False)
            psac_doc_tbl = self._getIinspectionSheetList(psac_doc)
            list_tags = {
                        'Name':{'type':'str','text':"O. Appere",'fmt':{}},
                        'DateMe':{'type':'str','text':date_meeting,'fmt':{}},
                        'Date':{'type':'str','text':date_meeting,'fmt':{}},
                        'Subject':{'type':'str','text':subject,'fmt':{}},
                        'Service':{'type':'str','text':'Quality Department','fmt':{}},
                        'Place':{'type':'str','text':'Montreuil','fmt':{}},
                        'Ref':{'type':'str','text':'CR149000','fmt':{}},
                        'Tel':{'type':'str','text':'','fmt':{}},
                        'Fax':{'type':'str','text':'','fmt':{}},
                        'Email':{'type':'str','text':'olivier.appere@zodiacaerospace.com','fmt':{}},
                        'TGT_REL':{'type':'str','text':target_release,'fmt':{}},
                        'REL':{'type':'str','text':release_doc,'fmt':{}},
                        'BAS':{'type':'str','text':baseline_doc,'fmt':{}},
                        'CSCI':{'type':'str','text':ci_identification,'fmt':{}},
                        'CONFLEVEL':{'type':'str','text':'1','fmt':{}},
                        'SW_LEVEL':{'type':'str','text':'B','fmt':{}},
                        'PART_NUMBER':{'type':'str','text':part_number,'fmt':{}},
                        'CHECKSUM':{'type':'str','text':checksum,'fmt':{}},
                        'TBL_CR':{'type':'tab','text':tableau_pr,'fmt':fmt_pr},
                        'ATTENDEES':{'type':'tab','text':tbl_attendees,'fmt':fmt_two},
                        'MISSING':{'type':'tab','text':tbl_missing,'fmt':fmt_two},
                        'COPIES':{'type':'tab','text':tbl_copies,'fmt':fmt_two},
                        'PREVIOUS_ACTIONS':{'type':'tab','text':tbl_actions,'fmt':fmt_action},
                        'CURRENT_ACTIONS':{'type':'tab','text':tbl_actions,'fmt':fmt_action},
                        'MAKE_LOG':{'type':'str','text':make_log,'fmt':{}},
                        'SCI_DOC':{'type':'str','text':sci_doc,'fmt':{}},
                        'SECI_DOC':{'type':'str','text':seci_doc,'fmt':{}},
                        'SAS_DOC':{'type':'str','text':sas_doc,'fmt':{}},
                        'SCI_IS':{'type':'str','text':sci_is,'fmt':{}},
                        'SECI_IS':{'type':'str','text':seci_is,'fmt':{}},
                        'SAS_IS':{'type':'str','text':sas_is,'fmt':{}},
                        'PSAC_DOC':{'type':'tab','text':psac_doc_tbl,'fmt':fmt_one},
                        'SDP_DOC':{'type':'str','text':sdp_doc,'fmt':{}},
                        'SVP_DOC':{'type':'str','text':svp_doc,'fmt':{}},
                        'SCMP_DOC':{'type':'str','text':scmp_doc,'fmt':{}},
                        'SQAP_DOC':{'type':'str','text':sqap_doc,'fmt':{}},
                        'SRTS_DOC':{'type':'str','text':srts_doc,'fmt':{}},
                        'SDTS_DOC':{'type':'str','text':sdts_doc,'fmt':{}},
                        'SCS_DOC':{'type':'str','text':scs_doc,'fmt':{}},
                        'SQAP_DOC':{'type':'str','text':sqap_doc,'fmt':{}}
                        }
        elif review_number == 1: # PR:
            review_string = "PR"
            # Documents and inspections
            # For PSAC, SDP, SCMP, SVP and SQAP
            index_doc = 0
            index_is = 0

            psac_is = []
            sdp_is = []
            svp_is = []
            scmp_is = []
            sqap_is = []

            # Project set in GUI
            baseline_doc = ""
            release_doc = ""
            for release,baseline,project in project_list:
                output = self.getArticles(self.list_type_doc,release,baseline,project,False)
                baseline_doc += baseline + "\n"
                release_doc += release + "\n"
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    self.ihm.log("Found doc: " + line,False)
                    m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
                    if m:
                        # Look for plans documents
                        result = self._getDoc(m,dico_plan_doc)
                        if result:
                            index_doc +=1
                            doc  = self._getDicoFound("PSAC","doc")
                            if doc:
                                psac_doc.append(doc)
                            doc  = self._getDicoFound("SDP","doc")
                            if doc:
                                sdp_doc  = doc
                            doc  = self._getDicoFound("SVP","doc")
                            if doc:
                                svp_doc  = doc
                            doc  = self._getDicoFound("SCMP","doc")
                            if doc:
                                scmp_doc  = doc
                            doc  = self._getDicoFound("SQAP","doc")
                            if doc:
                                sqap_doc  = doc
                            doc  = self._getDicoFound("SRTS","pdf")
                            if doc:
                                srts_doc  = doc
                            doc  = self._getDicoFound("SDTS","pdf")
                            if doc:
                                sdts_doc  = doc
                            doc  = self._getDicoFound("SCS","pdf")
                            if doc:
                                scs_doc  = doc
                        # Look for inspection sheet
                        result = self._getDoc(m,dico_is)
                        if result:
                            index_is +=1
                            doc  = self._getDicoFound("IS_PSAC","xls")
                            if doc:
                                psac_is.append(doc)
                            doc  = self._getDicoFound("IS_SDP","xls")
                            if doc:
                                sdp_is.append(doc)
                            doc  = self._getDicoFound("IS_SVP","xls")
                            if doc:
                                svp_is.append(doc)
                            doc  = self._getDicoFound("IS_SCMP","xls")
                            if doc:
                                scmp_is.append(doc)
                            doc  = self._getDicoFound("IS_SQAP","xls")
                            if doc:
                                sqap_is.append(doc)

            psac_doc_tbl = self._getIinspectionSheetList(psac_doc)
            psac_is_tbl = self._getIinspectionSheetList(psac_is)
            sdp_is_tbl = self._getIinspectionSheetList(sdp_is)
            svp_is_tbl = self._getIinspectionSheetList(svp_is)
            scmp_is_tbl = self._getIinspectionSheetList(scmp_is)
            sqap_is_tbl = self._getIinspectionSheetList(sqap_is)
            self.ihm.log("Amount of inspection sheets found: " + str(index_is),False)
            self.ihm.log("Amount of plans found: " + str(index_doc),False)
            list_tags = {
                        'Name':{'type':'str','text':"O. Appere",'fmt':{}},
                        'DateMe':{'type':'str','text':date_meeting,'fmt':{}},
                        'Date':{'type':'str','text':date_meeting,'fmt':{}},
                        'Subject':{'type':'str','text':'Review','fmt':{}},
                        'Service':{'type':'str','text':'Quality Department','fmt':{}},
                        'Place':{'type':'str','text':'Montreuil','fmt':{}},
                        'Ref':{'type':'str','text':'CR149000','fmt':{}},
                        'Tel':{'type':'str','text':'','fmt':{}},
                        'Fax':{'type':'str','text':'','fmt':{}},
                        'Email':{'type':'str','text':'olivier.appere@zodiacaerospace.com','fmt':{}},
                        'TGT_REL':{'type':'str','text':target_release,'fmt':{}},
                        'REL':{'type':'str','text':release_doc,'fmt':{}},
                        'BAS':{'type':'str','text':baseline_doc,'fmt':{}},
                        'CSCI':{'type':'str','text':ci_identification,'fmt':{}},
                        'CONFLEVEL':{'type':'str','text':'1','fmt':{}},
                        'SW_LEVEL':{'type':'str','text':'B','fmt':{}},
                        'PART_NUMBER':{'type':'str','text':part_number,'fmt':{}},
                        'CHECKSUM':{'type':'str','text':checksum,'fmt':{}},
                        'TBL_CR':{'type':'tab','text':tableau_pr,'fmt':fmt_pr},
                        'ATTENDEES':{'type':'tab','text':tbl_attendees,'fmt':fmt_two},
                        'MISSING':{'type':'tab','text':tbl_missing,'fmt':fmt_two},
                        'COPIES':{'type':'tab','text':tbl_copies,'fmt':fmt_two},
                        'PREVIOUS_ACTIONS':{'type':'tab','text':tbl_actions,'fmt':fmt_action},
                        'CURRENT_ACTIONS':{'type':'tab','text':tbl_actions,'fmt':fmt_action},
                        'PSAC_DOC':{'type':'tab','text':psac_doc_tbl,'fmt':fmt_one},
                        'SDP_DOC':{'type':'str','text':sdp_doc,'fmt':{}},
                        'SVP_DOC':{'type':'str','text':svp_doc,'fmt':{}},
                        'SCMP_DOC':{'type':'str','text':scmp_doc,'fmt':{}},
                        'SQAP_DOC':{'type':'str','text':sqap_doc,'fmt':{}},
                        'SRTS_DOC':{'type':'str','text':srts_doc,'fmt':{}},
                        'SDTS_DOC':{'type':'str','text':sdts_doc,'fmt':{}},
                        'SCS_DOC':{'type':'str','text':scs_doc,'fmt':{}},
                        'SQAP_DOC':{'type':'str','text':sqap_doc,'fmt':{}},
                        'PSAC_IS':{'type':'tab','text':psac_is_tbl,'fmt':fmt_one},
                        'SDP_IS':{'type':'tab','text':sdp_is_tbl,'fmt':fmt_one},
                        'SVP_IS':{'type':'tab','text':svp_is_tbl,'fmt':fmt_one},
                        'SCMP_IS':{'type':'tab','text':scmp_is_tbl,'fmt':fmt_one},
                        'SQAP_IS':{'type':'tab','text':sqap_is_tbl,'fmt':fmt_one},
                        }
        elif review_number == 2: # SRR:
            list_tags = {
                        'Name':{'type':'str','text':"O. Appere",'fmt':{}},
                        'DateMe':{'type':'str','text':date_meeting,'fmt':{}},
                        'Date':{'type':'str','text':date_meeting,'fmt':{}},
                        'Subject':{'type':'str','text':'Review','fmt':{}},
                        'Service':{'type':'str','text':'Quality Department','fmt':{}},
                        'Place':{'type':'str','text':'Montreuil','fmt':{}},
                        'Ref':{'type':'str','text':'CR149000','fmt':{}},
                        'Tel':{'type':'str','text':'','fmt':{}},
                        'Fax':{'type':'str','text':'','fmt':{}},
                        'Email':{'type':'str','text':'olivier.appere@zodiacaerospace.com','fmt':{}},
                        'TGT_REL':{'type':'str','text':target_release,'fmt':{}}}
        else:
            self.ihm.log("Review report export not implemented yet")
##            tkMessageBox.showinfo("Review report export not implemented yet")
        template_type = review_string
        template_name = self._getTemplate(template_type)
        docx_filename = self.system + "_" + self.item + "_" + template_type + "_Report_" + self.reference + "_%f" % time.time() + ".docx"
        if review_number in (1,9): # Patch temporaire
            self.docx_filename,exception = self._createDico2Word(list_tags,template_name,docx_filename)
        else:
            self.docx_filename = False
            exception = None
        return self.docx_filename,exception
    def _getIinspectionSheetList(self,is_doc):
        if is_doc == []:
            is_doc.append(["","None"])
            return is_doc
        else:
            is_doc_filtered = sorted(set(is_doc))
        is_doc_tbl = []
        for item in is_doc_filtered:
            is_doc_tbl.append(["",item])
        return is_doc_tbl

# -----------------------------------------------------------------------------
class Gui(Tool):
    '''
    Display the bottom of the GUI which is generic for all notebooks
    Use interface as global (not good)
    '''
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
    def scrollEvent(self,event):
        if event.delta >0:
            # déplacement vers le haut
            self.help_text.yview_scroll(-2,'units')
        else:
            # déplacement vers le bas
            self.help_text.yview_scroll(2,'units')
    def about(self):
        tkMessageBox.showinfo("Make Configuration Index Document", "DoCID " + __version__ + "\n\n Written by Olivier Appere\nTél:0155825104\nCourriel:olivier.appere@zodiacaerospace.com\n\n (c) Copyright 2013-2014")
    def __init__(self,master,queue,system,item):
        global gui_background_color
        Tool.__init__(self)
        width_output_log = 120
        #
        # Start GUI notebook definition
        #
        #notebook
        notebook = Pmw.NoteBook(master)
        notebook.pack(fill = 'both', expand = 1, padx = 10, pady = 10)
        #
        # Specific high panels
        #
        self.ihm = Interface(notebook,queue,system,item)
        #
        # Bottom common panel
        #
        bottom_frame = Frame(master)
        bottom_frame.pack()
        baseline_frame = Frame(bottom_frame)
        baseline_frame.pack()
        # Release
        baseline_label = Label(baseline_frame, text='Standard/Part Number/Release applied:', fg=foreground,width=30,anchor=W,padx=20)
        baseline_label.pack(side=LEFT)
        release = self.ihm.getBaseline()
        if release != "":
            self.ihm.baseline_txt = Label(baseline_frame,text=release,width=25,anchor=W,padx=20)
            self.ihm.button_select.configure(state=NORMAL)
            self.ihm.button_list_history.configure(state=NORMAL)
            self.ihm.button_list_items.configure(state=NORMAL)
            self.ihm.button_list_tasks.configure(state=NORMAL)
        else:
            self.ihm.baseline_txt = Label(baseline_frame,text="None",width=25,anchor=W,padx=20)
        self.ihm.baseline_txt.pack(side=LEFT)
        # Synergy Baseline
        baseline_synergy_label = Label(baseline_frame, text='Baseline applied:', fg=foreground,width=20,anchor=W,padx=20)
        baseline_synergy_label.pack(side=LEFT)
        baseline = self.ihm.baseline
        if  baseline != "":
            self.ihm.baseline_synergy_txt = Label(baseline_frame,text=baseline,width=25,anchor=W,padx=20)
            self.ihm.button_list_tasks.configure(state=NORMAL)
            self.ihm.button_list_items.configure(state=NORMAL)
        else:
            self.ihm.baseline_synergy_txt = Label(baseline_frame,text="None",width=25,anchor=W,padx=20)
        self.ihm.baseline_synergy_txt.pack(side=LEFT)
        #
        # Project
        #
        project_label = Label(baseline_frame, text='Project applied:', fg=foreground,width=20,anchor=W,padx=20)
        project_label.pack(side=LEFT)
        project = self.ihm.project
        if  project != "":
            self.ihm.project_txt = Label(baseline_frame,text=project,width=25,anchor=W,padx=20)
        else:
            self.ihm.project_txt = Label(baseline_frame,text="None",width=25,anchor=W,padx=20)
        self.ihm.project_txt.pack()
        #
        # CR
        #
        cr_frame = Label(bottom_frame,padx=2,pady=1,width=240,anchor=W)
        cr_frame.pack()
##        row_index += 1
        detect_cr_txt = "CR detected in release " + self._splitComma(self.ihm.previous_release)
        self.ihm.detect_cr = Label(cr_frame, text=detect_cr_txt, fg=foreground,width=80,anchor=W,padx=0)
        self.ihm.detect_cr.pack(side=LEFT)
##        self.detect_cr.grid(row = row_index, sticky='W')
##        row_index += 1
        text = self._splitComma(self.ihm.impl_release)
        impl_cr_txt = "CR implemented for release " + text
        self.ihm.impl_cr = Label(cr_frame, text=impl_cr_txt, fg=foreground,width=100,anchor=W,padx=0)
        self.ihm.impl_cr.pack()
##        self.impl_cr.grid(row = row_index, sticky='W')
        if self.ihm.getStandard():
            size_list_box=28
            change_frame = LabelFrame(bottom_frame, text="From Docid database (.csv file)")
            change_frame.pack(side=LEFT)
            spare_frame = Frame(bottom_frame,width=30)
            spare_frame.pack(side=LEFT)
        else:
            size_list_box=48
        rel_bas_proj_frame = LabelFrame(bottom_frame, text="From Synergy configuration management system tool database",padx=5,pady=5)
        rel_bas_proj_frame.pack()
        #
        # Project listbox
        #
        project_frame = LabelFrame(rel_bas_proj_frame,text="Project",bd=0)
        project_frame.pack(side=RIGHT,ipadx=5,ipady=5)
        sub_project_frame = Frame(project_frame)
        sub_project_frame.pack()
        self.ihm.projectlistbox = Listbox(sub_project_frame,height=6,width=size_list_box,exportselection=0,state=DISABLED,bg="gray")
        self.ihm.projectlistbox.insert(END, "All")
        self.ihm.vbar_4 = vbar_4 = Scrollbar(sub_project_frame, name="vbar_4")
        self.ihm.vbar_4.pack(side=RIGHT, fill=Y)
        vbar_4["command"] = self.ihm.projectlistbox.yview
        self.ihm.projectlistbox["yscrollcommand"] = vbar_4.set
        self.ihm.projectlistbox.bind("<ButtonRelease-1>", self.ihm.select_project)
        self.ihm.projectlistbox.bind("<Key-Up>", lambda event, arg=self.ihm.projectlistbox: self.ihm.up_event(event, arg))
        self.ihm.projectlistbox.bind("<Key-Down>", lambda event, arg=self.ihm.projectlistbox: self.ihm.down_event(event, arg))
        self.ihm.button_find_projects = Button(project_frame, text='Update', state=DISABLED, command = self.ihm._find_projects)
        self.ihm.button_set_baselines = Button(project_frame, text='Set', state=DISABLED, command = self.ihm.set_baselines)
        self.ihm.button_clear_project = Button(project_frame, text='Clear selection', state=NORMAL, command = self.ihm.clear_project)
        self.ihm.projectlistbox.pack()
        self.ihm.button_find_projects.pack(side=RIGHT,fill=X,padx=5)
        self.ihm.button_set_baselines.pack(side=LEFT,fill=X,padx=5)
        self.ihm.button_clear_project.pack(side=LEFT,fill=X,padx=5)
        #
        # Baseline listbox
        #
        baseline_frame = LabelFrame(rel_bas_proj_frame, text="Baseline",bd=0)
        baseline_frame.pack(side=RIGHT,ipadx=5,ipady=5)
        sub_baseline_frame = Frame(baseline_frame)
        sub_baseline_frame.pack()
        self.ihm.baselinelistbox = Listbox(sub_baseline_frame,height=6,width=size_list_box,exportselection=0,state=DISABLED,bg="gray")
        self.ihm.baselinelistbox.insert(END, "All")
        self.ihm.vbar_5 = vbar_5 = Scrollbar(sub_baseline_frame, name="vbar_5")
        self.ihm.vbar_5.pack(side=RIGHT, fill=Y)
        vbar_5["command"] = self.ihm.baselinelistbox.yview
        self.ihm.baselinelistbox["yscrollcommand"] = vbar_5.set
        self.ihm.baselinelistbox.bind("<ButtonRelease-1>", self.ihm.select_baseline)
        self.ihm.baselinelistbox.bind("<Key-Up>", lambda event, arg=self.ihm.baselinelistbox: self.ihm.up_event(event, arg))
        self.ihm.baselinelistbox.bind("<Key-Down>", lambda event, arg=self.ihm.baselinelistbox: self.ihm.down_event(event, arg))
        self.ihm.button_find_baselines = Button(baseline_frame, text='Update', state=DISABLED, command = self.ihm.find_baselines)
        self.ihm.button_clear_baseline = Button(baseline_frame, text='Clear selection', state=NORMAL, command = self.ihm.clear_baselines)
        self.ihm.baselinelistbox.pack()
        self.ihm.button_find_baselines.pack(side=RIGHT,fill=X,padx=5)
        self.ihm.button_clear_baseline.pack(side=LEFT,fill=X,padx=5)
        #
        # Release listbox
        #
        release_frame = LabelFrame(rel_bas_proj_frame,text="Release",bd=0)
        release_frame.pack(side=RIGHT,ipadx=5,ipady=5)
        sub_release_frame = Frame(release_frame)
        sub_release_frame.pack()
        self.ihm.releaselistbox = Listbox(sub_release_frame,height=6,width=size_list_box,exportselection=0,bg="gray")
        self.ihm.vbar_3 = vbar_3 = Scrollbar(sub_release_frame, name="vbar_3")
        self.ihm.vbar_3.pack(side=RIGHT, fill=Y)
        vbar_3["command"] = self.ihm.releaselistbox.yview
        self.ihm.releaselistbox["yscrollcommand"] = vbar_3.set
        self.ihm.releaselistbox.bind("<ButtonRelease-1>", self.ihm.select_release)
        self.ihm.releaselistbox.bind("<Key-Up>", lambda event, arg=self.ihm.releaselistbox: self.ihm.up_event(event, arg))
        self.ihm.releaselistbox.bind("<Key-Down>", lambda event, arg=self.ihm.releaselistbox: self.ihm.down_event(event, arg))
        self.ihm.button_find_releases = Button(release_frame, text='Update', state=DISABLED, command = self.ihm.find_releases)
        self.ihm.active_release_var = IntVar()
        self.ihm.check_release_active = Checkbutton(release_frame, text="Active", variable=self.ihm.active_release_var,fg=foreground,command=self.ihm.cb_active_release)
        self.ihm.check_release_active.pack(side=LEFT)
        self.ihm.button_clear_release = Button(release_frame, text='Clear selection', state=NORMAL, command = self.ihm.clear_releases)
        self.ihm.releaselistbox.pack()
        self.ihm.button_find_releases.pack(side=RIGHT,fill=X,padx=5)
        self.ihm.button_clear_release.pack(side=LEFT,fill=X,padx=5)
        self.ihm.display_release()
        if self.ihm.getStandard():
            #
            # Part number
            #
            pn_frame = LabelFrame(change_frame, text="Part Number",bd=0)
            pn_frame.pack(side=RIGHT,ipadx=5,ipady=5)
            sub_pn_frame = Frame(pn_frame)
            sub_pn_frame.pack()
            self.ihm.pnlistbox = Listbox(sub_pn_frame,height=6,width=size_list_box,exportselection=0,bg="gray")
            self.ihm.vbar_pn = vbar_pn = Scrollbar(sub_pn_frame, name="vbar_pn")
            self.ihm.vbar_pn.pack(side=RIGHT, fill=Y)
            vbar_pn["command"] = self.ihm.pnlistbox.yview
            self.ihm.pnlistbox["yscrollcommand"] = vbar_pn.set
            self.ihm.pnlistbox.bind("<ButtonRelease-1>", self.ihm.select_partnumber)
            self.ihm.pnlistbox.bind("<Key-Up>", lambda event, arg=self.ihm.pnlistbox: self.ihm.up_event(event, arg))
            self.ihm.pnlistbox.bind("<Key-Down>", lambda event, arg=self.ihm.pnlistbox: self.ihm.down_event(event, arg))
            self.ihm.pnlistbox.pack()
            self.ihm.display_partnumber()
            #
            # Standard
            #
            standard_frame = LabelFrame(change_frame, text="Standard",bd=0)
            standard_frame.pack(side=RIGHT,ipadx=5,ipady=5)
            sub_standard_frame = Frame(standard_frame)
            sub_standard_frame.pack()
            self.ihm.stdlistbox = Listbox(sub_standard_frame,height=6,width=size_list_box,exportselection=0,bg="gray")
            self.ihm.vbar_std = vbar_std = Scrollbar(sub_standard_frame, name="vbar_std")
            self.ihm.vbar_std.pack(side=RIGHT, fill=Y)
            vbar_std["command"] = self.ihm.stdlistbox.yview
            self.ihm.stdlistbox["yscrollcommand"] = vbar_std.set
            self.ihm.stdlistbox.bind("<ButtonRelease-1>", self.ihm.select_standard)
            self.ihm.stdlistbox.bind("<Key-Up>", lambda event, arg=self.ihm.stdlistbox: self.ihm.up_event(event, arg))
            self.ihm.stdlistbox.bind("<Key-Down>", lambda event, arg=self.ihm.stdlistbox: self.ihm.down_event(event, arg))
            self.ihm.stdlistbox.pack()
            self.ihm.display_standard()
        #
        # Output log
        #
        general_output_frame = Frame(master)
        general_output_frame.pack(ipadx=5,ipady=5)
        sub_general_output_frame = Frame(general_output_frame)
        sub_general_output_frame.pack()
        self.ihm.log_scrollbar = log_scrollbar = Scrollbar(sub_general_output_frame)
        self.ihm.log_scrollbar.pack(side=RIGHT, fill=Y)
        self.ihm.general_output_txt = Text(sub_general_output_frame,wrap=WORD, width = width_output_log, height = 8,fg='green',bg='black')
        self.ihm.log_scrollbar["command"] = self.ihm.general_output_txt.yview
        self.ihm.general_output_txt["yscrollcommand"] = log_scrollbar.set
        self.ihm.general_output_txt.bind("<MouseWheel>", self.ihm.log_scrollEvent)
        self.ihm.general_output_txt.bind("<Key-Up>", self.ihm.log_upEvent)
        self.ihm.general_output_txt.bind("<Key-Down>", self.ihm.log_downEvent)
        self.ihm.general_output_txt.pack()
        progress_bar_frame = Frame(general_output_frame, width=400, height=10)
        progress_bar_frame.pack(ipadx=5,ipady=5)
        # Clear
        self.ihm.button_clear = Button(progress_bar_frame, text='Clear', command = self.ihm.click_clear)
        self.ihm.button_clear.pack(side=LEFT,padx=0,pady=10)
        # progress bar
        self.ihm.pb_vd = ttk.Progressbar(progress_bar_frame, orient='horizontal', mode='indeterminate',length = 200)
        self.ihm.pb_vd.pack(expand=True, fill=BOTH, padx=300,pady=10, side=LEFT)
        self.ihm.pb_vd.pack_forget()
        self.ihm.success = Label(progress_bar_frame, text='', fg='red',width=150)
        self.ihm.success.pack(expand=True, fill=BOTH, padx=5,pady=10, side=LEFT)
        # Quit
        self.ihm.button_quit = Button(progress_bar_frame, text='Quit', command = self.ihm.click_quit)
        self.ihm.button_quit.pack(side=RIGHT,padx=0,pady=10)
        notebook.tab('Create configuration index document').focus_set()
        # Important pour que le notebook ai la taille du frame
        notebook.setnaturalsize()
        self.ihm.setBaseline(release)
        self.ihm.setBaselineSynergy(baseline)
        self.ihm.setProject(project)
        #
        # End GUI notebook definition
        #
class ThreadQuery(threading.Thread,Synergy):
    def lock(self):
        global count_baseline
        count_baseline +=1
##        print "Wait lock release: " + str(count_baseline) + "\n"
##        print "amount of threads alive:" + str(threading.active_count()) + "\n"
        self.verrou.acquire()
    def unlock(self):
        self.verrou.release()
##        print "Release lock.\n"
    def __init__(self,name_id="",master="",queue=""):
        # Global
        global system
        global item
        global no_start_session
        global login
        global password

        threading.Thread.__init__(self)
        Tool.__init__(self)
        # Create the queue
        self.queue = queue
        self.master_ihm = master
        self.running = 1
        self.system = self.master_ihm.system
        self.item = self.master_ihm.item
        # Get database name and aircraft name
        if self.item != "":
            self.database,self.aircraft = self.get_sys_item_database(system,self.item)
            if self.database == None:
                self.database,self.aircraft = self.get_sys_database()
        else:
            self.database,self.aircraft = self.get_sys_database()
##        print "no_start_session",no_start_session
##        print "database",self.database
        self.author = ""
        self.reference = ""
        self.release = ""
        self.project = ""
        self.baseline = ""
        self.revision = ""
        # Recursive lock
        self.verrou = threading.RLock()
        self.name_id = name_id
        self.input_data_filter = ""
        self.peer_reviews_filter = ""
        # Get config
##        self.__loadConfig()
        #
        # Create common GUI with 5 listbox and output log frame
        #
##        gui = Gui(master,self.queue,self.system,self.item)

        if not no_start_session and self.database != None:
##            print "start_session_thread"
            self.start_session_failed = False
            self.start_session_thread = threading.Thread(None,self._startSession,None,(self.system,self.item,self.database,login,password,self.aircraft))
            self.start_session_thread.start()
            self.launch_session = True
            Synergy.__init__(self,True)
        else:
            self.master_ihm.log("No database opened.")
            self.start_session_failed = True
            self.launch_session = False
            #
            #
            # Attention classe Synergy non init
            # AttributeError: 'ThreadQuery' object has no attribute 'loginfo'
            #
        # BuildDoc instance
        self.log = BuildDoc(self.master_ihm)

    def stopSession(self):
        global session_started
        if session_started:
            stdout,stderr = self.ccm_query('stop','Stop Synergy session')
            if stdout != "":
                # remove \r
                text = re.sub(r"\r\n",r"\n",stdout)
                self.master_ihm.log(text,False)
            if stderr:
                 # remove \r
                text = re.sub(r"\r\n",r"\n",stderr)
                self.master_ihm.log(text,False)
    # -----------------------------------------------------------------------------
    # Utility replacement function
    # -----------------------------------------------------------------------------
    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
         - BUILD_DOCX
            . Store selection
         - START_SESSION
         - GET_BASELINES
         - GET_RELEASES
         - GET_PROJECTS
         - etc.
        """
        global list_projects
        global session_started
        while self.queue.qsize():
            try:
                self.lock()
##                print threading.enumerate();
                # Check contents of message
                action = self.queue.get(0)
                print time.strftime("%H:%M:%S", time.localtime()) + " Commmand: " + action
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
                    self.item = data[9]
                    part_number = data[10]
                    checksum = data[11]
                    dal = data[12]
                    board_part_number = data[13]
                    previous_release = data[14]
                    #store information in sqlite db
                    self.storeSelection(project,self.system,release,baseline)
                    self.build_doc_thread = threading.Thread(None,self._generateCID,None)
                    self.build_doc_thread.start()
                if action == "BUILD_SQAP":
                    data = self.queue.get(1)
                    author = data[0]
                    self.reference = data[1]
                    self.revision = data[2]
                    self.build_doc_thread = threading.Thread(None,self._generateSQAP,None,(author,self.reference,self.revision,self.aircraft,self.system,self.item))
                    self.build_doc_thread.start()
                if action == "BUILD_CCB":
                    data = self.queue.get(1)
                    author = data[0]
                    self.reference = data[1]
                    self.revision = data[2]
                    release = data[3]
                    baseline = data[4]
                    project = data[5]
                    ccb_type = data[6]
                    detect_on = data[7]
                    impl_in = data[8]
                    self.build_doc_thread = threading.Thread(None,self._generateCCB,None)
                    self.build_doc_thread.start()
                if action == "BUILD_REVIEW_REPORT":
                    data = self.queue.get(1)
                    type_review = data[0]
                    self.build_doc_thread = threading.Thread(None,self._generateReviewReport,None,(type_review,))
                    self.build_doc_thread.start()
                elif action == "START_SESSION":
                    # start synergy session
                    data = self.queue.get(1)
                    self.database = data[0]
                    login = data[1]
                    password = data[2]
                    self.aircraft = data[3]
                    self.system = data[4]
                    self.item = data[5]
                    self.start_session_thread = threading.Thread(None,self._startSession,None,(self.system,self.item,self.database,login,password,self.aircraft))
                    self.start_session_thread.start()
                elif action == "GET_BASELINES":
                    if session_started:
                        query = self.queue.get(1)
                        self.get_baselines_thread = threading.Thread(None,self._getBaselinesList,None,(query,))
                        self.get_baselines_thread.start()
                elif action == "GET_RELEASES":
                    if session_started:
                        query = self.queue.get(1)
                        regexp = self.queue.get(2)
                        self.get_releases_thread = threading.Thread(None,self._getReleasesList,None,(query,regexp))
                        self.get_releases_thread.start()
                elif action == "GET_PROJECTS":
                    if session_started:
                        query = self.queue.get(1)
                        baseline_selected = self.queue.get(2)
                        release = self.queue.get(3)
                        self.get_projects_thread = threading.Thread(None,self._getProjectsList,None,(query,release,baseline_selected))
                        self.get_projects_thread.start()
                elif action == "READ_STATUS":
                    self.set_status_thread = threading.Thread(None,self._getSessionStatus,None)
                    self.set_status_thread.start()
                elif action == "CLOSE_SESSION":
                    self.set_status_thread = threading.Thread(None,self._closeSession,None)
                    self.set_status_thread.start()
                elif action == "MAKE_DIFF":
                    data = self.queue.get(1)
                    baseline_prev = data[0]
                    baseline_cur = data[1]
                    self.send_cmd_thread = threading.Thread(None,self._sendCmd,None,("BASELINES_DIFF","","","",baseline_prev,baseline_cur))
                    self.send_cmd_thread.start()
                elif action == "SHOW_BASELINE":
                    data = self.queue.get(1)
                    baseline_cur = data[0]
                    self.send_cmd_thread = threading.Thread(None,self._sendCmd,None,("BASELINES_SHOW","","","","",baseline_cur))
                    self.send_cmd_thread.start()
                elif action == "SEND_CMD":
                    self.send_cmd_thread = threading.Thread(None,self._sendCmd,None)
                    self.send_cmd_thread.start()
                elif action == "EXPORT_CR":
                    cr_id = self.queue.get(1)
                    self.send_cmd_thread = threading.Thread(None,self._exportCR,None,(cr_id,))
                    self.send_cmd_thread.start()
                elif action == "LIST_ITEMS":
                    release = self.queue.get(1)
                    project = self.queue.get(2)
                    baseline = self.queue.get(3)
                    self.send_cmd_thread = threading.Thread(None,self._sendCmd,None,("ITEMS",release,baseline,project))
                    self.send_cmd_thread.start()
                elif action == "SCOPE":
                    release = self.queue.get(1)
                    project = self.queue.get(2)
                    baseline = self.queue.get(3)
                    self.send_cmd_thread = threading.Thread(None,self._sendCmd,None,("SCOPE",release,baseline,project))
                    self.send_cmd_thread.start()
                elif action == "LIST_TASKS":
                    release = self.queue.get(1)
                    baseline = self.queue.get(2)
                    self.send_cmd_thread = threading.Thread(None,self._sendCmd,None,("TASKS",release,baseline))
                    self.send_cmd_thread.start()
                elif action == "LIST_HISTORY":
                    release = self.queue.get(1)
                    baseline = self.queue.get(2)
                    project = self.queue.get(3)
                    self.send_cmd_thread = threading.Thread(None,self._sendCmd,None,("HISTORY",release,baseline,project))
                    self.send_cmd_thread.start()
                elif action == "GET_RELEASE_VS_BASELINE":
                    if session_started:
                        baseline = self.queue.get(1)
                        self.send_cmd_thread = threading.Thread(None,self._sendCmd,None,("GET_RELEASE_VS_BASELINE","",baseline))
                        self.send_cmd_thread.start()
                elif action == "GET_CR":
                    data = self.queue.get(1)
                    baseline = data[0]
                    ccb_type = data[1]
                    self.build_doc_thread = threading.Thread(None,self._getCR,None,(baseline,ccb_type))
                    self.build_doc_thread.start()
                elif action == "START_APACHE":
                    config= "httpd_ece.conf"
                    self.send_cmd_thread = threading.Thread(None,self.__apache_start,None,(config,))
                    self.send_cmd_thread.start()
                elif action == "RELOAD_CONFIG":
                    # Get config
##                    self.__loadConfig()
##                    interface.log("Config file docid.ini reloaded.")
                    pass
                elif action == "RELOAD_BASELINEBOX":
                    if session_started:
                        stdout = self.queue.get(1)
                        if stdout != "":
                            self.master_ihm.log("Available baseline found:")
                            output = stdout.splitlines()
                            self.master_ihm.baselinelistbox.delete(0, END)
                            if len(output) > 1:
                                self.master_ihm.baselinelistbox.insert(END, "All")
                                self.master_ihm.baselinelistbox.selection_set(first=0)
                            for line in output:
                                line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                                self.master_ihm.baselinelistbox.insert(END, line)
                                self.master_ihm.baselinelistbox_1.insert(END, line)
                                self.master_ihm.baselinelistbox_2.insert(END, line)
                                self.master_ihm.log(line)
                            self.master_ihm.releaselistbox.selection_set(first=0)
                            self.master_ihm.baselinelistbox.configure(bg="white")
                        else:
                            self.master_ihm.resetBaselineListbox()
                            self.master_ihm.log(" No available baselines found.")
                        #self.resetProjectListbox()
                        self.master_ihm.baselinelistbox.configure(state=NORMAL)
                        # Set scrollbar at the bottom
                        self.master_ihm.general_output_txt.see(END)
                elif action == "RELOAD_RELEASEBOX":
                    if session_started:
                        stdout = self.queue.get(1)
                        if stdout != "":
                            self.master_ihm.log("Available releases found:")
                            self.master_ihm.releaselistbox.delete(0, END)
                            output = stdout.splitlines()
                            if len(output) > 1:
                                self.master_ihm.releaselistbox.insert(END, "All")
##                                interface.releaselistbox.selection_set(first=0)
                            for line in output:
                                line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                                if line !="":
                                    self.master_ihm.releaselistbox.insert(END, line)
                                    self.master_ihm.log("   " + line)
                            self.master_ihm.releaselistbox.selection_set(first=0)
                            self.master_ihm.releaselistbox.configure(bg="white")
                            # Authorize button clicking
                            self.master_ihm.button_list_items.configure(state=NORMAL)
                            self.master_ihm.button_list_tasks.configure(state=NORMAL)
                            self.master_ihm.button_list_history.configure(state=NORMAL)
                            self.master_ihm.baselinelistbox.configure(state=NORMAL)
                            self.master_ihm.button_find_projects.configure(state=NORMAL)
                            self.master_ihm.button_set_baselines.configure(state=NORMAL)
                            self.master_ihm.button_find_baselines.configure(state=NORMAL)
    ##                        interface.button_select.configure(state=NORMAL)
                        else:
                            self.master_ihm.log("No available releases found.")
                            self.master_ihm.resetReleaseListbox()
                        # Set scrollbar at the bottom
                        self.master_ihm.defill()
                elif action == "RELOAD_PROJECTBOX":
                    if session_started:
                        stdout = self.queue.get(1)
                        release = self.queue.get(2)
                        baseline_selected = self.queue.get(3)
                        if stdout != "":
                            self.master_ihm.projectlistbox.delete(0, END)
                            output = stdout.splitlines()
                            # Here the list of projects is set
                            list_projects = []
                            if baseline_selected not in ("*","All","",None):
                                if release not in ("","All",None):
                                    for line in output:
                                        line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                                        m = re.match(r'(.*)-(.*);(.*|<void>)$',line)
                                        if m:
                                            project = m.group(1) + "-" + m.group(2)
                                            baseline_string = m.group(3)
                                            baseline_splitted = baseline_string.split(',')
                                            for baseline in baseline_splitted:
                                                baseline = re.sub(r".*#",r"",baseline)
                                                if baseline == baseline_selected:
                                                    list_projects.append(project)
                                                    break
                                        else:
                                            m = re.match(r'^Baseline(.*):$',line)
                                            if not m:
                                                project = line
                                                list_projects.append(project)
                                else:
                                    num = 0
                                    for project in output:
                                        if num > 0:
                                            list_projects.append(project)
                                        num += 1
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
                            # Update list of project of GUI
                            self.master_ihm.projectlistbox.delete(0, END)
    ##                            interface.baseline_set_box.delete(0, END)
                            if len(list_projects) > 1:
                                self.master_ihm.projectlistbox.insert(END, "All")
                            for project in list_projects:
                                self.master_ihm.projectlistbox.insert(END, project)
    ##                                interface.baseline_set_box.insert(END, project)
                            if len(list_projects) > 1:
                                self.master_ihm.projectlistbox.selection_set(first=0)
                            self.master_ihm.projectlistbox.configure(bg="white")
                        else:
                            pass
                        if list_projects != []:
                            self.master_ihm.log("Available projects found:")
                            for project in list_projects:
                                self.master_ihm.log( "     " + project)
                        else:
                            self.master_ihm.log("No available projects found.")
                            self.master_ihm.resetProjectListbox()
                        self.master_ihm.releaselistbox.configure(state=NORMAL)
                        self.master_ihm.baselinelistbox.configure(state=NORMAL)
                        # Set scrollbar at the bottom
                        self.master_ihm.general_output_txt.see(END)
                        self.master_ihm.button_select.configure(state=NORMAL)
                        self.master_ihm.setProject("All")
                elif action == "RELOAD_CRLISTBOX":
                    if session_started:
                        try:
                            list_cr = self.queue.get(1)
                            # Update list of project of GUI
                            self.master_ihm.crlistbox.configure(state=NORMAL)
                            self.master_ihm.crlistbox.delete(0, END)
                            inter = 0
                            for cr_description in list_cr:
                                self.master_ihm.crlistbox.insert(END, cr_description)
                                if inter % 2 == 0:
                                    self.master_ihm.crlistbox.itemconfig(inter,{'bg':'darkgrey','fg':'white'})
                                else:
                                    self.master_ihm.crlistbox.itemconfig(inter,{'bg':'lightgrey','fg':'black'})
                                inter += 1
                            self.master_ihm.crlistbox.configure(bg="white")
                        except AttributeError:
                            pass
                else:
                    pass
                self.unlock()
            except Queue.Empty:
                pass
    def periodicCall(self):
        """
        Check every 1000 ms if there is something new in the queue.
        """
##        print time.strftime("%H:%M:%S", time.localtime())
##        print time.strftime("PERIODIC CALL " + self.name_id)
        self.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        try:
            self.master_ihm.after(1000, self.periodicCall)
        except AttributeError:
            time.sleep(1)
            self.periodicCall
##        print "periodicCall"
##    def _openHLink(self,event,type):
##        if type == "RELEASE":
##            interface.release = self.previous_release
##            interface.setBaseline(self.release)
##        elif type == "BASELINE":
##            interface.baseline = self.previous_baseline
##            interface.setBaselineSynergy(self.baseline)
##            interface.setBaselineSynergy(self.baseline)
##            interface.log("Selected baseline: " + self.baseline)
##            interface.projectlistbox.configure(state=NORMAL)
##            interface.button_find_projects.configure(state=NORMAL)
##            interface.button_select.configure(state=NORMAL)
##            interface.button_list_items.configure(state=NORMAL)
##            interface.button_list_tasks.configure(state=NORMAL)
##            interface._find_release_vs_baseline()
##            interface._find_projects()
##        else:
##            interface.project = self.previous_project
##            interface.setProject(self.project)
    def _setRelease(self):
        self.master_ihm.release = self.previous_release
##        interface.button_select.configure(state=NORMAL)
        self.master_ihm.button_list_items.configure(state=NORMAL)
        self.master_ihm.button_list_tasks.configure(state=NORMAL)
        self.master_ihm.button_set_baselines.configure(state=NORMAL)
        self.master_ihm.setBaseline(self.master_ihm.release)
    def _setBaseline(self):
        self.master_ihm.baseline = self.previous_baseline
        self.master_ihm.setBaselineSynergy(self.master_ihm.baseline)
        self.master_ihm.log("Selected baseline: " + self.master_ihm.baseline)
        self.master_ihm.projectlistbox.configure(state=NORMAL)
        self.master_ihm.button_find_projects.configure(state=NORMAL)
        self.master_ihm.button_list_items.configure(state=NORMAL)
        self.master_ihm.button_list_tasks.configure(state=NORMAL)
##        interface._find_release_vs_baseline()
##        interface._find_projects()
        executed = self._sendCmd("GET_RELEASE_VS_BASELINE","",self.master_ihm.baseline)
        if executed:
            pass
##            interface.button_select.configure(state=NORMAL)
        query = self._defineProjectQuery(self.master_ihm.release,self.master_ihm.baseline)
        self._getProjectsList(query,self.master_ihm.release,self.master_ihm.baseline)
    def _setProject(self):
        self.master_ihm.project = self.previous_project
        self.master_ihm.button_select.configure(state=NORMAL)
        self.master_ihm.button_list_items.configure(state=NORMAL)
        self.master_ihm.button_list_tasks.configure(state=NORMAL)
        self.master_ihm.setProject(self.master_ihm.project)
    def _add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hlink-%d" % len(self.links)
        self.links[tag] = action
        return "hlink", tag
    def _click(self, event):
        for tag in self.master_ihm.general_output_txt.tag_names(CURRENT):
            if tag[:6] == "hlink-":
                            self.links[tag]()
    def _startSession(self,system,item,database,login,password,aircraft):
        ''' Function to start Synergy session
             - invoke command ccm start ...
             - display synergy feedback
             - retrieve last session information
             - enable SELECT and REFRESH buttons
             - get list of releases
            called by the thread '''
        global session_started
        global description_item
        # GUI/CLI
        try:
            self.master_ihm.success.config(fg='red',bg = 'yellow',text="SESSION LOGGING IN PROGRESS")
        except AttributeError:
            pass
        self.lock()
        # Display system name
        self.master_ihm.log("System: " + system,False)
        # Display item name
        self.master_ihm.log("Item: " + item,False)
        # Display configuration item ID
        ci_id = self.get_ci_sys_item_identification(system,item)
        if ci_id != None:
            self.master_ihm.log("CI ID: " + ci_id,False)
        else:
            self.master_ihm.log("CI ID: Unknown",False)
        self.previous_release = ""
        self.previous_baseline = ""
        self.previous_project = ""
        # GUI/CLI
        try:
            self.master_ihm.project_description.configure(text = "System selected: " + system)
            self.master_ihm.project_description_entry_pg_ccb.insert(END, system)
            data = self.retrieveLastSelection(system)
            if data != []:
                if data[0][1] not in (None,""):
                    # delete text
                    self.master_ihm.reference_entry.delete(0, END)
                    self.master_ihm.reference_entry.insert(0, data[0][1])
                if data[0][2] not in (None,""):
                    self.master_ihm.revision_entry.delete(0, END)
                    self.master_ihm.revision_entry.insert(0, data[0][2])
                # Create hyoerlink
                self.previous_release = data[0][6]
                self.previous_baseline = data[0][7]
                self.previous_project = data[0][4]
                self.links = {}
                self.master_ihm.general_output_txt.tag_configure("hlink", foreground='yellow', underline=1)
                self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", self.onLink)
                self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", self.outsideLink)
                self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", self._click)
        except AttributeError:
            pass
        if database != None and login != "":
            self.master_ihm.log("Open Synergy session with database {base}. Please wait ...".format(base=database))
            query = 'start /nogui /q /d /usr/local/ccmdb/' + database + ' /u /usr/local/ccmdb/' + database + ' /s ' + self.ccm_server + ' /n ' + login + ' /pw ' + password
            stdout,stderr = self.ccm_query(query,"Synergy session start")
##            print time.strftime("%H:%M:%S", time.localtime()) + " " + stdout
            if stderr:
                m = re.match(r'Another Synergy CLI session is running',stderr)
                if m:
                    self.master_ihm.log("Session already started.")
                    # which database is used ?
                    self._getSessionStatus()
                    session_started = True
                else:
                    m = re.match(r'Cannot connect to router',stderr)
                    if m:
                        self.master_ihm.log("Synergy server not responding.")
                        session_started = False
                    else:
                        m = re.match(r'Invalid username or password',stderr)
                        if m:
                            self.master_ihm.log("Invalid username or password.")
                            session_started = False
                        else:
                            m = re.match(r'Invalid Role',stderr)
                            if m:
                                self.master_ihm.log("Invalid Role.")
                                session_started = False
                            else:
                                m = re.match(r'The /pw option requires a value',stderr)
                                if m:
                                    self.master_ihm.log("Password is missing.")
                                    session_started = False
                                else:
                                    session_started = True
            elif stdout:
                self.master_ihm.log("Session started successfully.")
                if self.previous_release not in ("","All"):
                    self.master_ihm.logrun("Previous selected release was: ")
                    self.master_ihm.general_output_txt.insert(END, self.previous_release, self._add(self._setRelease))
                    self.master_ihm.general_output_txt.insert(END, "\n")
                if self.previous_baseline not in ("","All"):
                    self.master_ihm.logrun("Previous selected baseline was: ")
                    self.master_ihm.general_output_txt.insert(END, self.previous_baseline, self._add(self._setBaseline))
                    self.master_ihm.general_output_txt.insert(END, "\n")
                if self.previous_project not in ("","All"):
                    self.master_ihm.logrun("Previous selected project was: ")
                    self.master_ihm.general_output_txt.insert(END, self.previous_project, self._add(self._setProject))
                    self.master_ihm.general_output_txt.insert(END, "\n")
                session_started = True
            else:
                session_started = False
##            interface.general_output_txt.insert(END, "\n")
            if session_started:
                try:
                    self.master_ihm.button_find_releases.configure(state=NORMAL)
                    self.master_ihm.button_find_baselines.configure(state=NORMAL)
                    self.master_ihm.button_find_projects.configure(state=NORMAL)
                    self.master_ihm.button_set_baselines.configure(state=NORMAL)
                except AttributeError:
                    pass
                # send info to BuildDoc instance class
                self.log.setSessionStarted(session_started)
            match_out = re.match(r'^(.*):(.*):([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',stdout)
            if match_out:
                if stderr != "":
                    self.master_ihm.log(" " + stderr,False)
                self.master_ihm.log("Computer   => " + match_out.group(1))
                self.master_ihm.log("Session ID => " + match_out.group(2))
                self.master_ihm.log("IP address => " + match_out.group(3))
            else:
                self.master_ihm.log(stdout + stderr,False)
        else:
            self.master_ihm.log("No database available or bypass mode activated.")
            self.master_ihm.log("Database:" + database)
            self.master_ihm.log("Login:"+ login)
            self.start_session_failed = True
            stdout = ""
##        self.__getReleasesList(True)
##        print"TEST START SESSION",stderr
        # Set scrollbar at the bottom
        self.master_ihm.defill()
        self.unlock()
        try:
            if not session_started:
                self.master_ihm.success.config(fg='yellow',bg = 'red',text="SESSION LOGGING FAILED")
##                self.master_ihm.log("SESSION LOGGING FAILED")
            else:
                self.master_ihm.success.config(fg='magenta',bg = 'green',text="SESSION LOGGING SUCCEEDED")
##                self.master_ihm.log("SESSION LOGGING SUCCEEDED")
        except AttributeError:
            if not session_started:
                self.master_ihm.log("SESSION LOGGING FAILED")
            else:
                self.master_ihm.log("SESSION LOGGING SUCCEEDED")
        return stdout
    def _getReleasesList(self,query="cmd release -u -l",regexp=""):
        ''' get releases list '''
        self.lock()
        stdout,stderr = self.ccm_query(query,"Get releases")
        if regexp != "":
            output = stdout.splitlines()
            list_release = ""
            if stdout != "":
                for line in output:
                    m = re.match(regexp,line)
                    if m:
                        list_release += line + "\n"
            if list_release == "":
                self.master_ihm.log("Check release_regexp parameter in docid.ini which value is: " + regexp)
        else:
            list_release = stdout
        self.queue.put("RELOAD_RELEASEBOX") # action to get baselines
        self.queue.put(list_release)
        self.unlock()
    def _getBaselinesList(self,query):
        ''' get baseline list
                by invoking the command '''
        self.lock()
        stdout,stderr = self.ccm_query(query,"Get baselines")
##            interface.button_find_projects.configure(state=NORMAL)
        self.queue.put("RELOAD_BASELINEBOX") # action to get baselines
        self.queue.put(stdout)
        self.unlock()
    def _getProjectsList(self,query,release,baseline_selected):
        self.lock()
##        if refresh == True:
##            interface.projectlistbox.delete(0, END)
##            interface.projectlistbox.insert(END, "Looking for projects ...")
##        interface.log("Get available projects...")
##        if release not in ("","All",None,"None"):
##            query = 'query -release '+ release +' "(cvtype=\'project\')" -f "%name-%version;%in_baseline"'
##        elif baseline_selected not in ("","All",None,"None"):
##            query = 'baseline -u -sby project -sh projects  ' + baseline_selected + ' -f "%name-%version"'
##        else:
##            query = 'query "(cvtype=\'project\')" -f "%name-%version"'
        self.master_ihm.log("ccm " + query)
        stdout,stderr = self.ccm_query(query,"Get projects")
        self.queue.put("RELOAD_PROJECTBOX") # action to get projects
        self.queue.put(stdout)
        self.queue.put(release)
        self.queue.put(baseline_selected)
        self.unlock()

    def _exportCR(self,cr_id):
        self.master_ihm.success.config(fg='red',bg = 'yellow',text="EXPORT IN PROGRESS")
        query = "query -t problem \"(problem_number='" + cr_id + "')\" -u -f \
                 \"<table border='1'>\
                 <cell name='CR_domain'>%CR_domain</cell>\
                 <cell name='CR_type'>%CR_type</cell>\
                 <cell name='crstatus'>%crstatus</cell>\
                 <cell name='problem_synopsis'>%problem_synopsis</cell>\
                 <cell name='SCR_In_Analysis_id'>%SCR_In_Analysis_id</cell>\
                 <cell name='create_time'>%create_time</cell>\
                 <cell name='CR_ECE_classification'>%CR_ECE_classification</cell>\
                 <cell name='CR_customer_classification'>%CR_customer_classification</cell>\
                 <cell name='CR_request_type'>%CR_request_type</cell>\
                 <cell name='CR_detected_on'>%CR_detected_on</cell>\
                 <cell name='CR_applicable_since'>%CR_applicable_since</cell>\
                 <cell name='CR_implemented_for'>%CR_implemented_for</cell>\
                 <cell name='CR_origin'>%CR_origin</cell>\
                 <cell name='CR_origin_desc'>%CR_origin_desc</cell>\
                 <cell name='CR_expected'>%CR_expected</cell>\
                 <cell name='CR_observed'>%CR_observed</cell>\
                 <cell name='CR_functional_impact'>%CR_functional_impact</cell>\
                 <cell name='CR_analysis'>%CR_analysis</cell>\
                 <cell name='CR_correction_description'>%CR_correction_description</cell>\
                 <cell name='CR_product_impact'>%CR_product_impact</cell>\
                 <cell name='CR_doc_impact'>%CR_doc_impact</cell>\
                 <cell name='CR_verif_impact'>%CR_verif_impact</cell>\
                 <cell name='impact_analysis'>%impact_analysis</cell>\
                 <cell name='functional_limitation_desc'>%functional_limitation_desc</cell>\
                 <cell name='implemented_modification'>%implemented_modification</cell>\
                 <cell name='CR_implementation_baseline'>%CR_implementation_baseline</cell>\
                 <cell name='SCR_Verif_Test_Bench'>%SCR_Verif_Test_Bench</cell>\
                 <cell name='SCR_Verif_Test_Procedure'>%SCR_Verif_Test_Procedure</cell>\
                 <cell name='CR_verification_activities'>%CR_verification_activities</cell>\
                 <cell name='functional_limitation'>%functional_limitation</cell>\
                 <cell name='SCR_Closed_id'>%SCR_Closed_id</cell>\
                 <cell name='SCR_Closed_time'>%SCR_Closed_time</cell>\
                 <cell name='problem_number'>%problem_number</cell>\
                 <cell name='modify_time'>%modify_time</cell>\
                 <cell name='SCR_Fixed_time'l>%SCR_Fixed_time</cell>\
                 </table>\""
##                 <cell name='transition_log'>%transition_log</cell>\
        executed = True
        filename = "log_SCR_" + cr_id + "_%d.html" % floor(time.time())
        #with open(self.gen_dir + filename, 'w') as of:
        if query != "":
##            self.master_ihm.log('ccm ' + query)
            ccm_query = 'ccm ' + query + '\n'
            cmd_out = self._ccmCmd(query,False)
##            if cmd_out == None:
##                executed = False
            # Replace STX and ETS and e cute characters
            char = {r'\x02':r'<',r'\x03':r'>',r'\xe9':r'e'}
            for before, after in char.iteritems():
                cmd_out = re.sub(before,after,cmd_out)
            #of.write(cmd_out)
            if cmd_out == "":
                self.master_ihm.log("No result.")
                executed = False
            #
            # Get transition log
            #
            query = "query -t problem \"(problem_number='" + cr_id + "')\" -u -f \"%transition_log\""
            ccm_query = 'ccm ' + query + '\n'
            transi_log = self._ccmCmd(query,False)
            transi_log_filtered = self._filterASCII(transi_log)
            #
            # Get parent CR
            #
            parent_cr_id = self._getParentCR(cr_id)
            if parent_cr_id:
                #
                # Get parent ID informations
                #
                parent_cr = self._getParentInfo(parent_cr_id)
                if parent_cr:
                    self.master_ihm.log("Parent CR:" + parent_cr)
                else:
                    self.master_ihm.log("No result for _getParentInfo (twice).")
            else:
                parent_cr = "<td><IMG SRC=\"../img/changeRequestIcon.gif\">---</td><td>---</td><td>---</td><td>---</td><td>---</td>"
            self._parseCR(cmd_out,transi_log_filtered,parent_cr,self.gen_dir + filename)
        if executed:
            self.master_ihm.log("Command executed.")
            self.log.docx_filename = filename
            self.master_ihm.general_output_txt.tag_configure("hlink", foreground='yellow', underline=1)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", self.log.openHLink_ccb)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", self.log.onLink)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", self.log.outsideLink)
            self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) +  " Log created.\n")
            self.master_ihm.general_output_txt.insert(END, "Available here:\n")
            self.master_ihm.general_output_txt.insert(END, filename, "hlink")
            self.master_ihm.general_output_txt.insert(END, "\n")
            self.master_ihm.success.config(fg='magenta',bg = 'green',text="EXPORT SUCCEEDED")
        else:
            self.master_ihm.success.config(fg='yellow',bg = 'red',text="EXPORT FAILED")
        # Set scrollbar at the bottom
        self.master_ihm.defill()
        return executed
    def _getItems(self,release="",baseline="",project=""):
        global session_started
        output = ""
        output_format = "csv"
        release_name = re.sub(r"\/",r"",release)
        filename = "log_" + release_name + "_" + baseline + "_" + project + "_%d" % floor(time.time())
        if output_format == "txt":
            filename += ".txt"
        else:
            filename += ".csv"
        executed = False
        filename = "log_items_" + release_name + "_" + baseline + "_" + project + "_%d" % floor(time.time())
        if output_format == "csv":
            display_attr = ' -f "%release;%name;%version;%modify_time;%status;%task;%task_status;%change_request;%type" '
            show_header = "-nch"
            filename += ".csv"
        else:
            display_attr = ' -f "%release %name %version %modify_time %status %task %task_status %change_request %type" '
            show_header = "-ch"
            filename += ".txt"
        if baseline not in ("","All"):
            # Baseline
            # sh: show
            #  u: no number
            query = 'baseline -sh objects  ' + baseline + " -u "
            query += display_attr
            executed = True
        elif release not in ("","All"):
            # Query with a specifcic release
            #  ch: Specifies to use column headers for the output
            # nch: Specifies not to use column headers for the output
            #   u: no number
            query = 'query -sby name ' + show_header + ' -n *.* -u -release ' + release + ' '
            if project not in ("*","All",""):
                # a project is selected
                # get sub-projects
                name, version = self.getProjectInfo(project)
                query += '"recursive_is_member_of(cvtype=\'project\' and name=\'' + name + '\' and version=\'' + version + '\' , \'none\')" '
            query += display_attr
            executed = True
        elif project not in ("","All"):
            # No baseline, nor release selected but a project is
            query = 'query -sby name ' + show_header + ' -n *.* -u "(is_member_of(\'' + project +'\'))" '
            query += display_attr
            executed = True
        else:
            self.master_ihm.log("Please select a release or a baseline or a project.")
        if executed:
            self.master_ihm.log(" ccm " + query)
            self.master_ihm.defill()
            ccm_query = 'ccm ' + query + '\n\n'
            self.master_ihm.log("List objects (directories and executable objects are discarded).")
            cmd_out = self._ccmCmd(query)
            with open(self.gen_dir + filename, 'w') as of:
                if output_format == "csv":
                    header = "Release;Name;Version;Modify time;Status;Task;Task status;CR;Type\n"
                    of.write(header)
                else:
                    of.write(ccm_query)
                output = cmd_out.splitlines()
                for line in output:
                    # Skip directory or relocatable objects
                    # Skip automatic tasks and components tasks
                    # Remove Baseline info at the beginning
                    if output_format == "csv":
                        if not re.search("(dir|relocatable_obj)$",line) and not re.search("(task_automatic|component_task)",line) and not re.search("(^Baseline)",line):
                            # For CLI
                            print line
                            of.write(line)
                            of.write("\n")
                    else:
                        if not re.search("(dir|relocatable_obj)$",line) and not re.search("(task_automatic|component_task)",line):
                            of.write(line)
                            of.write("\n")
        if executed:
            self.master_ihm.log("Command executed.")
            try:
                self.log.docx_filename = filename
                self.master_ihm.general_output_txt.tag_configure("hlink", foreground='yellow', underline=1)
                self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", self.log.openHLink_ccb)
                self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", self.log.onLink)
                self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", self.log.outsideLink)
                self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) +  " Log created.\n")
                self.master_ihm.general_output_txt.insert(END, "Available here:\n")
                self.master_ihm.general_output_txt.insert(END, filename, "hlink")
                self.master_ihm.general_output_txt.insert(END, "\n")
            except AttributeError:
                pass
        # Set scrollbar at the bottom
        self.master_ihm.defill()
        return output
    def _sendCmd(self,cmd="",release="",baseline="",project="",baseline_prev="",baseline_cur=""):
        global session_started
        output_format = "csv"
        release_name = re.sub(r"\/",r"",release)
        filename = "log_" + release_name + "_" + baseline + "_" + project + "_%d" % floor(time.time())
        if output_format == "txt":
            filename += ".txt"
        else:
            filename += ".csv"
        executed = False
        if cmd == "SCOPE":
            if release not in ("","All") and project not in ("*","All",""):
                test_string = "SQAP"
                text_found = ""
                project_name, project_version = self.getProjectInfo(project)
                query = "finduse -query \"release='" + release + "' and (cvtype='xls' or cvtype='doc' or cvtype='pdf' or cvtype='ascii' or cvtype='csrc') and recursive_is_member_of(cvtype='project' and name='"+ project_name +"' and version='"+ project_version +"' , 'none')\""
                self.master_ihm.log('ccm ' + query)
                self.master_ihm.general_output_txt.see(END)
                ccm_query = 'ccm ' + query + '\n\n'
                cmd_out = self._ccmCmd(query)
                output = cmd_out.splitlines()
##                test_string_1 = "Input_Data"
##                test_string_2 = "SQAP"
                list_items_skipped_1 = []
                list_items_skipped_2 = []
                regexp_1 = '^(.*)'+ project_name + '\\\\' + re.escape(self.input_data_filter) + '\\\\(.*)-(.*)@(.*)-(.*)$'
                regexp_2 = '^(.*)'+ project_name + '\\\\' + re.escape(self.peer_reviews_filter) + '\\\\(.*)-(.*)@(.*)-(.*)$'
                for line in output:
##                    print "Tested: " + line
                    # ex: SW_PLAN\SDP\IS_SDP_SW_PLAN_SQA.xlsm-1.7.0@SW_PLAN-1.3
                    m = re.match(regexp_1,line)
                    if m:
##                        text_found = m.group(2)
                        list_items_skipped_1.append(m.group(2))
                    else:
                        pass
                    m = re.match(regexp_2,line)
                    if m:
##                        text_found = m.group(2)
                        list_items_skipped_2.append(m.group(2))
                    else:
                        pass
##                print regexp_1
##                print regexp_2
                list_wo_doublons_1 = list(set(list_items_skipped_1))
                list_wo_doublons_2 = list(set(list_items_skipped_2))
##                print list_wo_doublons_1
##                print list_wo_doublons_2
                executed = True
            else:
                self.master_ihm.log("Please select a release and a project.")
        elif cmd == "ITEMS":
            filename = "log_items_" + release_name + "_" + baseline + "_" + project + "_%d" % floor(time.time())
            if output_format == "csv":
                display_attr = ' -f "%release;%name;%version;%modify_time;%status;%task;%task_status;%change_request;%type" '
                show_header = "-nch"
                filename += ".csv"
            else:
                display_attr = ' -f "%release %name %version %modify_time %status %task %task_status %change_request %type" '
                show_header = "-ch"
                filename += ".txt"
            if baseline not in ("","All"):
                # Baseline
                # sh: show
                #  u: no number
                query = 'baseline -sh objects  ' + baseline + " -u "
                query += display_attr
                executed = True
            elif release not in ("","All"):
                # Query with a specifcic release
                #  ch: Specifies to use column headers for the output
                # nch: Specifies not to use column headers for the output
                #   u: no number
                query = 'query -sby name ' + show_header + ' -n *.* -u -release ' + release + ' '
                if project not in ("*","All",""):
                    # a project is selected
                    # get sub-projects
                    name, version = self.getProjectInfo(project)
                    query += '"recursive_is_member_of(cvtype=\'project\' and name=\'' + name + '\' and version=\'' + version + '\' , \'none\')" '
                query += display_attr
                executed = True
            elif project not in ("","All"):
                # No baseline, nor release selected but a project is
                query = 'query -sby name ' + show_header + ' -n *.* -u "(is_member_of(\'' + project +'\'))" '
                query += display_attr
                executed = True
            else:
                self.master_ihm.log("Please select a release or a baseline or a project.")
            if executed:
                self.master_ihm.log(" ccm " + query)
                self.master_ihm.general_output_txt.see(END)
                ccm_query = 'ccm ' + query + '\n\n'
                self.master_ihm.log("List objects (directories and executable objects are discarded).")
                cmd_out = self._ccmCmd(query)
                with open(self.gen_dir + filename, 'w') as of:
                    if output_format == "csv":
                        header = "Release;Name;Version;Modify time;Status;Task;Task status;CR;Type\n"
                        of.write(header)
                    else:
                        of.write(ccm_query)
                    output = cmd_out.splitlines()
                    for line in output:
                        # Skip directory or relocatable objects
                        # Skip automatic tasks and components tasks
                        # Remove Baseline info at the beginning
                        if output_format == "csv":
                            if not re.search("(dir|relocatable_obj)$",line) and not re.search("(task_automatic|component_task)",line) and not re.search("(^Baseline)",line):
                                of.write(line)
                                of.write("\n")
                        else:
                            if not re.search("(dir|relocatable_obj)$",line) and not re.search("(task_automatic|component_task)",line):
                                of.write(line)
                                of.write("\n")
        elif cmd == "HISTORY":
            filename = "log_history_" + release_name + "_" + baseline + "_" + project + "_%d" % floor(time.time())
            filename += ".csv"
            self.log.setRelease(release)
            self.log.setBaseline(baseline)
            self.log.setProject(project)
##            cid = BuildDoc("","","","","","",release,baseline,project,"SCI","","","","")
            self.log.display_attr = ' -f "%name|%version|%task|%task_synopsis|%change_request|%change_request_synopsis|%type" '
            header = ["Document","Issue","Tasks","Synopsis","CR","Synopsis"]
            self.log.tableau_items = []
            self.log.tableau_items.append(header)
            source_only = self.master_ihm.history_scope.get()
            if source_only:
                list_type_src = self.log.list_type_src_sci
                list_type_src.extend(self.log.list_type_src_hcmr)
            else:
                list_type_src = ()
            self.log.object_released = False
            self.log.object_integrate = False
            output = self.log.getArticles(list_type_src,release,baseline,project,True)
            index_src = 0
##            output = cid._getAllSourcesHistory(release,baseline,project)
            with open(self.log.gen_dir + filename, 'w') as of:
        ##            output = cid.tableau_items
                header = "File;Version;Task;Synopsis;CR;Synopsis\n"
                of.write(header)
                for line in output:
##                    print line
                    line = re.sub(r"<void>",r"",line)
##                    print line
                    m = re.match(r'(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)\|(.*)',line)
                    if m:
##                        print cid.list_type_src
##                        print "TEST check:",interface.history_scope
                        result = self.log._createTblSourcesHistory(m,source_only)
                        if result:
                            index_src +=1
                            # Remove Baseline info at the beginning
                            if not re.search("(^Baseline)",line):
##                                of.write(m.group(1)+";"+m.group(2)+";"+m.group(3)+";"+m.group(4)+";"+m.group(5)+";"+m.group(6))
                                for line_csv in result:
                                    of.write(line_csv)
                                    of.write("\n")
            print "Amount of source files found: " + str(index_src)# + "\n"
            executed = True
        elif cmd == "TASKS":
            filename = "log_tasks_" + release_name + "_" + baseline + "_" + project + "_%d" % floor(time.time())
            if output_format == "csv":
                display_attr = '"%displayname;%status;%task_synopsis"'
                show_header = "-nch"
                filename += ".csv"
            else:
                display_attr = '"%displayname %status %task_synopsis"'
                show_header = "-ch"
                filename += ".txt"
            with_cr = self.master_ihm.with_cr.get()
            if baseline not in ("","All"):
                query = 'baseline -sh task ' + baseline + ' -u -f ' + display_attr + '\n'
                executed = True
            elif release not in ("","All"):
                #   -u: is not numbered
                #  -qu: query
                # -rel: release
                query = 'task -u -qu -ts all_tasks ' + show_header + ' -rel ' + release + ' -f ' + display_attr + '\n'
                executed = True
            else:
                query = 'task -u -qu -ts all_tasks ' + show_header + ' -f ' + display_attr + '\n'
                executed = True
##                interface.log("Please select a release or a baseline.")
            if executed:
                ccm_query = 'ccm ' + query + '\n'
                self.master_ihm.log(ccm_query)
                cmd_out = self._ccmCmd(query)
                self.master_ihm.defill()
                with open(self.gen_dir + filename, 'w') as of:
                    if output_format == "csv":
                        if not with_cr:
                            header = "Task ID;Status;Synopsis\n"
                        else:
                            header = "Task ID;Task status;Task synopsis;CR ID;CR status;CR synopsis\n"
                        of.write(header)
                    else:
                        of.write(ccm_query)
                    output = cmd_out.splitlines()
                    for line in output:
                        if with_cr:
                            # Add cr information
                            mtask = re.match(r'(.*);(.*);(.*)',line)
                            # Get task ID
                            if mtask:
                                task_id = mtask.group(1)
                                task_status = mtask.group(2)
                                task_synopsis = mtask.group(3)
                                query = 'task -u -show change_request ' + task_id + ' -f "CR %problem_number;;%problem_synopsis;;%crstatus" \n'
                                ccm_query = 'ccm ' + query + '\n'
                                self.master_ihm.log(ccm_query)
                                cmd_out = self._ccmCmd(query)
                                output_cr = cmd_out.splitlines()
                                cr_id_tbl = []
                                for line_cr in output_cr:
##                                    m = re.match(r'^CR ([0-9]*):(.*)$',line_cr)
##                                    print "LINE",line_cr
                                    mcr = re.match(r'^CR ([0-9]*);;(.*);;(.*)$',line_cr)
                                    # Get CR ID
##                                    print "MCR",mcr
                                    if mcr:
                                        cr_id = mcr.group(1)
                                        cr_synopsis = mcr.group(2)
                                        cr_status = mcr.group(3)
                                        print cr_id,cr_synopsis,cr_status
                                        #  Discard CR status prefix
                                        cr_status_lite = re.sub(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)', r'\2', cr_status)
                                        cr_id_tbl.append([task_id,task_status,task_synopsis,cr_id,cr_status_lite,cr_synopsis])
                                    else:
                                        cr_id_tbl.append([task_id,task_status,task_synopsis,"","",""])
                                self.master_ihm.defill()
                            for task_id,task_status,task_synopsis,cr_id,cr_synopsis,cr_status in cr_id_tbl:
                                text = ""
                                text += task_id + "; " + task_status + "; " + task_synopsis + "; "
                                text += cr_id + "; " + cr_synopsis + "; " + cr_status
                                line = text
##                                print line
                                # Remove Baseline info at the beginning
                                if output_format == "csv":
                                    # Skip automatic tasks and components tasks
                                    if not re.search("(task_automatic|component_task)",line) and not re.search("(^Baseline)",line):
                                        of.write(line)
                                        of.write("\n")
                                else:
                                    # Skip automatic tasks and components tasks
                                    if not re.search("(task_automatic|component_task)",line):
                                        of.write(line)
                                        of.write("\n")
                        else:
                            # Remove Baseline info at the beginning
                            if output_format == "csv":
                                # Skip automatic tasks and components tasks
                                if not re.search("(task_automatic|component_task)",line) and not re.search("(^Baseline)",line):
                                    of.write(line)
                                    of.write("\n")
                            else:
                                # Skip automatic tasks and components tasks
                                if not re.search("(task_automatic|component_task)",line):
                                    of.write(line)
                                    of.write("\n")
##                    of.write(cmd_out)
        elif cmd == "BASELINES_DIFF":
            #
            # - objects
            # all objects that are included in the baseline are displayed. The default format is:
            #   display name, status, owner, release, create time
            #
            # - tasks
            # all objects that are included in the baseline are displayed. The default format is:
            #   id, release, assignee, create time, description
            #
            # - changes requests
            #    include details about change requests (CRs) that are partially included and fully included in the two baselines.
            #    display name, problem synopsis
            #
            query = 'baseline -compare ' + baseline_prev + ' ' + baseline_cur + ' -tasks -objects -change_requests'
            ccm_query = 'ccm ' + query + '\n'
            self.master_ihm.log(ccm_query)
            cmd_out = self._ccmCmd(query)
            filename = "log_baseline_diff_" + release_name + "_" + baseline_prev + "_vs_" + baseline_cur + "_%d.txt" % floor(time.time())
            with open(self.gen_dir + filename, 'w') as of:
                of.write(ccm_query)
                of.write(cmd_out)
            executed = True
        elif cmd == "BASELINES_SHOW":
            #
            # - objects
            # all objects that are included in the baseline are displayed. The default format is:
            #   display name, status, owner, release, create time
            #
            # - tasks
            # all objects that are included in the baseline are displayed. The default format is:
            #   id, release, assignee, create time, description
            #
            # - changes requests
            #    include details about change requests (CRs) that are partially included and fully included in the two baselines.
            #    display name, problem synopsis
            #
            query = 'baseline -sh objects  ' + baseline_cur
            ccm_query = 'ccm ' + query + '\n'
            self.master_ihm.log(ccm_query)
            cmd_out = self._ccmCmd(query)
            filename = "log_baseline_show_" + baseline_cur + "_%d.txt" % floor(time.time())
            with open(self.gen_dir + filename, 'w') as of:
                of.write(ccm_query)
                of.write(cmd_out)
            executed = True
        elif cmd == "GET_RELEASE_VS_BASELINE":
            query = 'baseline -sh i  ' + baseline
            ccm_query = 'ccm ' + query + '\n'
            self.master_ihm.log(ccm_query)
            cmd_out = self._ccmCmd(query)
            if cmd_out == None:
                executed = False
            else:
                filename = "log_baseline_show_" + baseline + "_%d.txt" % floor(time.time())
                with open(self.gen_dir + filename, 'w') as of:
                    of.write(ccm_query)
                    of.write(cmd_out)
                output = cmd_out.splitlines()
                for line in output:
                    # Attention aux espaces à supprimer
                    m = re.match(r'^  Release:( *)([^ .]*)',line)
                    if m:
    ##            m = re.search(r'^  Release:(.*)',cmd_out)
    ##            if m:
                        release = m.group(2)
                        # TBC interface.release = release
                        self.master_ihm.log("Associated release is: " + release)
    ##                    interface.setBaseline(release)
    ##                    print m.group(1)
                executed = True
        else:
            cmd_txt = self.master_ihm.command_txt.get(1.0,END)
            output = cmd_txt.splitlines()
            executed = True
            filename = "log_%d.txt" % floor(time.time())
            with open(self.gen_dir + filename, 'w') as of:
                for query in output:
                    if query != "":
                        self.master_ihm.log('ccm ' + query)
                        ccm_query = 'ccm ' + query + '\n'
                        cmd_out = self._ccmCmd(query)
                        if cmd_out == None:
                            executed = False
                            break
                        try:
                            of.write(ccm_query)
                        except UnicodeEncodeError as exception:
                            print "Character not supported:", exception
                        of.write(cmd_out)
                        if cmd_out == "":
                            self.master_ihm.log("No result.")
                            executed = False
        if executed:
            self.master_ihm.log("Command executed.")
            self.log.docx_filename = filename
            self.master_ihm.general_output_txt.tag_configure("hlink", foreground='yellow', underline=1)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", self.log.openHLink_ccb)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", self.log.onLink)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", self.log.outsideLink)
            self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) +  " Log created.\n")
            self.master_ihm.general_output_txt.insert(END, "Available here:\n")
            self.master_ihm.general_output_txt.insert(END, filename, "hlink")
            self.master_ihm.general_output_txt.insert(END, "\n")
        # Set scrollbar at the bottom
        self.master_ihm.general_output_txt.see(END)
        return executed
    def _defineProjectQuery(self,release,baseline):
        self.master_ihm.projectlistbox.configure(state=NORMAL)
        self.master_ihm.projectlistbox.delete(0, END)
        self.master_ihm.log("Get available projects...")
        # First check for projects in baseline then in release
        if baseline not in ("","All",None,"None"):
            query = 'baseline -u -sby project -sh projects  ' + baseline + ' -f "%name-%version"'
        elif release not in ("","All",None,"None"):
            query = 'query -release '+ release +' "(cvtype=\'project\')" -f "%name-%version;%in_baseline"'
        else:
            query = 'query "(cvtype=\'project\')" -f "%name-%version"'
        return query
    def _generateCID(self):
        '''
        get items by invoking synergy command
        get sources by invoking synergy command
        get CR by invoking synergy command
        '''
        global list_projects
        project = self.master_ihm.project
        release = self.master_ihm.release
        baseline = self.master_ihm.baseline
        object_released = self.master_ihm.status_released
        object_integrate = self.master_ihm.status_integrate
        if project == "All":
            query = self._defineProjectQuery(release,baseline)
            self._getProjectsList(query,release,baseline)
        self.master_ihm.log("Begin document generation ...")
        self.master_ihm.defill()
        # Attentinon classe déjà instanciée auparavant à l'init
        cid = BuildDoc(self.master_ihm)
        self.master_ihm.log("Creation doc in progress...")
        self.master_ihm.defill()
        # Create docx
        self.docx_filename,exception = cid.createCID(object_released,object_integrate)
        if not self.docx_filename:
            self.master_ihm.log(exception.strerror + ", document not saved.\n")
            self.master_ihm.defill()
        else:
            # Create hyoerlink
            self.master_ihm.general_output_txt.tag_configure("hlink", foreground='yellow', underline=1)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", cid.openHLink)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", cid.onLink)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", cid.outsideLink)
            self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) +  " Word document created.\n")
            self.master_ihm.general_output_txt.insert(END, "         Available here: ")
            self.master_ihm.general_output_txt.insert(END, self.docx_filename, "hlink")
            self.master_ihm.general_output_txt.insert(END, "\n")
        # Set scrollbar at the bottom
        self.master_ihm.general_output_txt.see(END)
        self.master_ihm.cr_activate_all_button()
    def _generateSQAP(self,
                    author,
                    reference,
                    revision,
                    aircraft,
                    system,
                    item):
        '''
        '''
        sqap = BuildDoc(author,reference,revision,aircraft,system,item)
        self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) + " Creation doc in progress...\n")
        # Create docx
        docx_filename,exception = sqap.createSQAP()
        if docx_filename == False:
            self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) + " " + exception.strerror + ", document not saved.\n")
        else:
            self.master_ihm.general_output_txt.tag_configure("hlink", foreground='blue', underline=1)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", sqap.openHLink_qap)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", sqap.onLink)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", sqap.outsideLink)
            self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) +  " Word document created.\n")
            self.master_ihm.general_output_txt.insert(END, "Available here:\n")
            self.master_ihm.general_output_txt.insert(END, docx_filename, "hlink")
            self.master_ihm.general_output_txt.insert(END, "\n")
    def _generateCCB(self):
        '''
        '''
        ccb = BuildDoc(self.master_ihm)
        self.master_ihm.log("Creation doc in progress...")
        # Create docx
        docx_filename,exception = ccb.createCCB()
        if not docx_filename:
            self.master_ihm.log(exception.strerror + ", document not saved.")
        else:
            self.master_ihm.general_output_txt.tag_configure("hlink", foreground='yellow', underline=1)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", ccb.openHLink_ccb)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", ccb.onLink)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", ccb.outsideLink)
            self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) +  " Word document created.\n")
            self.master_ihm.general_output_txt.insert(END, "Available here: ")
            self.master_ihm.general_output_txt.insert(END, docx_filename, "hlink")
            self.master_ihm.general_output_txt.insert(END, "\n")
        # Set scrollbar at the bottom
        self.master_ihm.defill()
    def _generateReviewReport(self,review_type):
        '''
        '''
        global session_started
        self.master_ihm.log("Creation doc in progress...")
        # Create docx
        try:
            self.master_ihm.success.config(fg='red',bg = 'yellow',text="GENERATION IN PROGRESS")
        except AttributeError:
            pass
        old_review = BuildDoc(self.master_ihm)
        # new:
    ##    target_release = self.ihm.previous_release
    ##    release = self.ihm.release
    ##    baseline =  self.ihm.baseline
    ##    self.ccb_type = "SCR"#self.ihm.ccb_var_type.get()
        detect_release = self.master_ihm.previous_release
        impl_release = self.master_ihm.impl_release
    ##    self.cr_type = self.ihm.cr_type
        old_review.list_cr_for_ccb = old_review._getListCRForCCB()
        tbl_cr_for_ccb = old_review.getPR_CCB(cr_status="",
                                                for_review=True,
                                                cr_with_parent=True)

        review_number = self.master_ihm.var_review_type.get()
        subject = Review.getReviewList(review_number)
        checksum = self.master_ihm.checksum_entry.get()
        part_number = self.master_ihm.part_number_entry.get()
        release = self.master_ihm.release
        baseline = self.master_ihm.baseline
        project = self.master_ihm.project
        review_qams_id = self.master_ihm.review_qams_id
        reference = self.master_ihm.reference_entry.get()
        issue = self.master_ihm.revision_entry.get()
        project_list = []
        if self.master_ihm.project_list == []:
            project_list.append([release,baseline,project])
        else:
            project_list = self.master_ihm.project_list
        review = Review(review_number,
                        detect_release=detect_release,
                        impl_release=impl_release,
                        tbl_cr_for_ccb=tbl_cr_for_ccb,
                        session_started=session_started,
                        project_list=project_list,
                        system=self.system,
                        item=self.item,
                        component=self.master_ihm.component,
                        part_number=part_number,checksum=checksum,subject=subject,
                        reference=reference,
                        issue=issue,
                        review_qams_id=review_qams_id)

        docx_filename,exception = review.createReviewReport()
        old_review.docx_filename = docx_filename
        if not docx_filename:
            self.master_ihm.log(exception + ": document not saved.")
        else:
            try:
                self.master_ihm.success.config(fg='magenta',bg = 'green',text="GENERATION SUCCEEDED")
            except AttributeError:
                pass
            self.master_ihm.general_output_txt.tag_configure("hlink", foreground='yellow', underline=1)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", old_review.openHLink_ccb)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", old_review.onLink)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", old_review.outsideLink)
            self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) +  " Word document created.\n")
            self.master_ihm.general_output_txt.insert(END, "Available here: ")
            self.master_ihm.general_output_txt.insert(END, docx_filename, "hlink")
            self.master_ihm.general_output_txt.insert(END, "\n")
        # Set scrollbar at the bottom
        self.master_ihm.defill()
    def _closeSession(self):
        '''
        Close session
        '''
        global session_started
        query = "stop"
        self.master_ihm.log("ccm " + query)
        stdout = self._ccmCmd(query)
        # Set scrollbar at the bottom
        self.master_ihm.general_output_txt.see(END)
    def _getSessionStatus(self):
        '''
        Retrieve database used
        '''
        global session_started
        query = "status"
        self.master_ihm.log("ccm " + query)
        stdout = self._ccmCmd(query)
        # Set scrollbar at the bottom
        try:
            self.master_ihm.general_output_txt.see(END)
        except AttributeError:
            pass
        output = stdout.splitlines()
        for line in output:
            m = re.search(r'Database:(.*)',line)
            if m:
                database = m.group(1)
                self.master_ihm.log("Database used is:" + database)
                return_code = database
                break;
            else:
                return_code = False
        if not return_code:
            print "No Synergy database found"
        return return_code
    def _getCR(self,baseline="",cr_type="",cr_status="",extension=True):
        '''
            List CR
            Generate a csv file at the end
            get
                variables
                    previous_release,
                    impl_release,
                    baseline,
                    project
                    attribute ? ENcore utilisé ? pas sûr.
                methods
                    getTypeWorkflow
                    cr_for_review_var
            from ThreadQuery <=== Interface class
            set
                methods
                    setPreviousRelease
                    setRelease
                    setBaseline
                    setProject
            to BuildDoc
        '''
        output = ""
        filename = "log_" + cr_type + "_%d" % floor(time.time()) + ".csv"
        find_status = False
        # Pas terrible 'aller prendre la globale interface
        self.log.setPreviousRelease(self.master_ihm.previous_release) # Attention c'est en fait detect_release, a corriger
        self.log.setRelease(self.master_ihm.impl_release)
        self.log.setBaseline(self.master_ihm.baseline)
        self.log.setProject(self.master_ihm.project)
        self.log.ccb_type = cr_type
        # query with no numbering of the line and sorted by problem_number
        query = 'query -u -sby problem_number '
        # Compute filtering
        # Get worflow type Old/New
        old_cr_workflow = self.master_ihm.getTypeWorkflow()
        # Get filter attributes
        #
        # Default = CR_implemented_for
        # Detected on
        # Implemented for
        # Applicable Since
        #
        attribute = self.master_ihm.attribute
        # Compute baseline to look for
        implemented = ""
        if baseline not in ("","All"):
            # get standard
            list_sub_std = []
            if self.master_ihm.dico_std.has_key(baseline):
                #
                # Cette partie ne marche plus, a checker
                #
                condition = '"(cvtype=\'problem\') '
                filter_cr = ""
                list_sub_std = self.master_ihm.dico_std[baseline]
                find_std = False
                implemented = ""
                num = 0
                if self.master_ihm.dico_list_std.has_key(baseline):
                    # Est-ce un standard avion ou un sous-standard projet ?
                    pass
                else:
                    delta_implemented,find_std = self.createCrImplemented(baseline,find_std,filter_cr)
                    implemented += delta_implemented
                for sub_std in list_sub_std:
                        delta_implemented,find_std = self.createCrImplemented(sub_std,find_std,filter_cr)
                        implemented += delta_implemented
                if find_std == True:
                    implemented +=  ') '
                condition += implemented
            else:
                pass
        release = self.master_ihm.impl_release
        condition,detect_attribut = self.log._createConditionStatus(release,old_cr_workflow,attribute)
        try:
            for_review_on = self.master_ihm.cr_for_review_var.get()
            cr_with_parent = self.master_ihm.cr_with_parent.get()
            log_on = self.master_ihm.log_on_var.get()
        except AttributeError:
            for_review_on = True
            cr_with_parent = False
            log_on = False
        if log_on:
            transition_log = ";%transition_log"
        else:
            transition_log = ""
        if for_review_on:
            header = "CR ID;Synopsis;Severity;Status;Comment/Impact/Risk\n"
            if not old_cr_workflow:
                classification = '%CR_ECE_classification'
            else:
                classification = '%Severity'
            attributes = '-f "%problem_number;%problem_synopsis;' + classification + ';%crstatus;%void"'
        else:
            if not old_cr_workflow:
                # New problem report workflow
                if extension:
                    implementation_baseline = "Implementation baseline;"
                    implementation_baseline_f = ";%CR_implementation_baseline"
                else:
                    implementation_baseline_f = ""
                    implementation_baseline = ""
                if cr_with_parent:
                    header = "id;Type;Synopsis;Level;Status;Detect;Implemented;" + implementation_baseline + "Modified time;Impact analysis;Parent CR;Parent CR status;Parent CR synopsis\n"
                else:
                    header = "id;Type;Synopsis;Level;Status;Detect;Implemented;" + implementation_baseline + "Modified time;Impact analysis\n"
                attributes = '-f "%problem_number;%CR_request_type;%problem_synopsis;%crstatus;' + detect_attribut + implementation_baseline_f + ';%modify_time<impact>%impact_analysis</impact>"'
            else:
                # Old problem report workflow
                header = "id;Synopsis;Status;Detect;Implemented;Modified time\n"
                attributes = '-f "%problem_number;%problem_synopsis;%crstatus;'+detect_attribut+';%modify_time"'
        query = query + condition + attributes
        self.master_ihm.log('ccm ' + query)
        self.master_ihm.defill()
        # remove \n
        text = re.sub(r"\n",r"",query)
        stdout,stderr = self.ccm_query(text,'Synergy command')
        result = ""
        list_change_requests = []
        if stdout != "":
            # remove CRLF
            if 0 == 1:
                char = (r'\x92',r'\x93',r'\x94',r'\x96',r'\xB0',r'\xB2',r'\xB2'r'\xE9')
                for repl in char:
                    stdout = re.sub(repl,r"",stdout)
                output = stdout.splitlines()
                for line in output:
                     line_tr = line.encode('iso8859-1')
                     print line_tr
            self.master_ihm.log(stdout,False)
            # manage <br />
            stdout = self.replaceBeacon(stdout)
            result = re.sub(r"<br ?\/>",r", ",stdout)
            # remove \r
            result = re.sub(r"\r\n",r"\n",result)
            # remove Record Separator
            result = re.sub(r"\x1E",r"----------\n",result)
            # remove File Separator
            result = re.sub(r"\x1C",r"\n",result)
            # remove <void>
            result = re.sub(r"<void>",r"",result)
            # Split CR status on case all CR are displayed
            if not for_review_on:
                result = re.sub(r'(.*);(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*);(.*)', r'\1;\2;\3;\4', result)
            else:
                #  Discard CR status prefix
                result = re.sub(r'(.*);(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*);(.*)', r'\1;\3;\4', result)
            self.master_ihm.log(result)
            output = result.splitlines()
##            if cr_with_parent:
            result = ""
            for line in output:
                match_impact_analysis = re.match(r'^(.*)<impact>(.*)<\/impact>',line)
                if match_impact_analysis:
                    line_start = match_impact_analysis.group(1)
                    impact_analysis = match_impact_analysis.group(2)
                    impact_analysis = re.sub(r", ?$",r"",impact_analysis)
                    # Remove comma separator
                    impact_analysis = re.sub(r";",r",",impact_analysis)
                    print "IMPACT ANALYSIS:",impact_analysis
                    import html2text
                    impact_analysis_plain_txt = html2text.html2text(self.removeNonAscii(impact_analysis))
                    impact_analysis_plain_txt = re.sub(r"\r",r" ",impact_analysis_plain_txt)
                    impact_analysis_plain_txt = re.sub(r"\n",r" ",impact_analysis_plain_txt)
                    print "line_start",line_start
                    print "impact_analysis_plain_txt",impact_analysis_plain_txt
                    line = self.removeNonAscii(line_start) + ";" + impact_analysis_plain_txt
                m = re.match(r'^([0-9]*);(.*);(.*);(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR);(.*)',line)
                # Replace tag <br /> by carriage return fo excel
                if m:
                    cr_id = m.group(1)
                    cr_synopsis = m.group(3)
                    list_change_requests.append(cr_id + ") " + cr_synopsis)
                    # For CLI
                    print line
                    if cr_with_parent:
                        parent_cr_id = self._getParentCR(cr_id)
                        if parent_cr_id:
                            #
                            # Get parent ID informations
                            #
                            parent_cr = self._getParentInfo(parent_cr_id)
                            if parent_cr:
                                parent_decod = self._parseCRParent(parent_cr)
                                print "parent_decod",parent_decod
                                text = self.removeNonAscii(parent_decod[4])
                                line += ";"+ parent_decod[0] + " " + parent_decod[1] + " " + parent_decod[2] +";" + self.discardCRPrefix(parent_decod[3]) +";" + text
                    result += line + "\n"
                else:
                    print "Pb match CR"
        self.queue.put("RELOAD_CRLISTBOX") # action to get projects
        self.queue.put(list_change_requests)
        if stderr:
            print time.strftime("%H:%M:%S", time.localtime()) + " " + stderr
             # remove \r
            result = re.sub(r"\r\n",r"\n",stderr)
            self.master_ihm.log(result)
        with open(self.gen_dir + filename, 'w') as of:
            ccm_query = 'ccm ' + query + '\n\n'
##            header = "'ID;Type;Synopsis;Level;Status;Detect;Implemented;Modified time\n"
##            header = "'ID;Type;Synopsis;Level;Status;Detect;Appl since;Implemented;Modified time\n"
            of.write(header)
            of.write(result)
        self.master_ihm.log("Command executed.")
##        log = BuildDoc()
        self.log.docx_filename = filename
        try:
            self.master_ihm.general_output_txt.tag_configure("hlink", foreground='yellow', underline=1)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Button-1>", self.log.openHLink_ccb)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Enter>", self.log.onLink)
            self.master_ihm.general_output_txt.tag_bind("hlink", "<Leave>", self.log.outsideLink)
            self.master_ihm.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) +  " Log created.\n")
            self.master_ihm.general_output_txt.insert(END, "Available here: ")
            self.master_ihm.general_output_txt.insert(END, filename, "hlink")
            self.master_ihm.general_output_txt.insert(END, "\n")
        except AttributeError:
            pass
        # Set scrollbar at the bottom
        self.master_ihm.defill()
        # For debug purpose
        return output

    def run(self):
        # sleep to enables the GUI to finish its setting
        import time
##        print time.strftime("%H:%M:%S", time.localtime()) + " Start thread " + self.name_id + "\n"
        time.sleep(2)
        self.periodicCall()
    def stop(self):
##        print time.strftime("%H:%M:%S", time.localtime()) + " Stop thread " + self.name_id + "\n"
        self.terminated = True
class Login (Frame,Tool):
    def _readConfig(self):
        '''
         Read csv config file
        '''
        # read config file
        config_parser = ConfigParser()
        config_parser.read('docid.ini')
        try:
            self.login = config_parser.get("User","login")
            self.password = config_parser.get("User","password")
            if config_parser.has_section("Default"):
                self.system = self.getOptions("Default","system")
                self.item = self.getOptions("Default","item")
                start = self.getOptions("Default","start")
                if start == "auto":
                    self.auto_start = True
                else:
                    self.auto_start = False
        except IOError as exception:
            print "Config reading failed:", exception
    def __init__(self, fenetre, **kwargs):
        '''
        init login class
             - create GUI
             - invoke sqlite query SELECT name FROM systems ORDER BY systems.name ASC
                 to populate system listbox
        '''
        global background
        global foreground
        global system
        global item
        Tool.__init__(self)
        self.auto_start = False
        self.system = ""
        self.item = ""
        self.item_id = ()
        # read config file
        self._readConfig()
        system = self.system
        item = self.item
        # Create widgets
        entry_size = 30
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, fenetre, width=768, height=576,relief =GROOVE,**kwargs)
        self.pack(fill=BOTH,ipady=10)
        all_frame = Frame(self)
        all_frame.pack(side=LEFT);
        login_frame = Frame(all_frame)
        login_frame.pack();
        # Login
        self.login_txt = Label(login_frame, text='Login:', fg=foreground,justify=LEFT)
        self.login_entry = Entry(login_frame, state=NORMAL,width=20)
        self.login_entry.insert(END, self.login)
        self.login_txt.pack(side=LEFT)
        self.login_entry.pack()
        # Password
        password_frame = Frame(all_frame)
        password_frame.pack();
        self.password_txt = Label(password_frame, text='Password:', fg=foreground,justify=LEFT)
        self.password_entry = Entry(password_frame, state=NORMAL,width=17)
        self.password_entry.configure(show='*')
        self.password_entry.insert(END, self.password)
        self.password_txt.pack(side=LEFT)
        self.password_entry.pack(fill=X,ipadx=0)
        #Systems
        system_frame = Frame(all_frame)
        system_frame.pack()
        self.listbox_txt = Label(system_frame, text='Systems:', fg=foreground,width=40,anchor=W,padx=20)
        self.listbox_frame = Frame(system_frame)
        self.vbar_1 = vbar_1 = Scrollbar(self.listbox_frame, name="vbar_1")
        self.vbar_1.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(self.listbox_frame,height=6,width=entry_size,exportselection=0,yscrollcommand=vbar_1.set)
        self.listbox.pack()
        self.populate_listbox('SELECT name FROM systems ORDER BY systems.name ASC',self.listbox,"None")
        # Tie listbox and scrollbar together
        vbar_1["command"] = self.listbox.yview
        # Bind events to the list box
        self.listbox.bind("<ButtonRelease-1>", self.select_system)
        self.listbox.bind("<Key-Up>", lambda event, arg=self.listbox: self.up_event(event, arg))
        self.listbox.bind("<Key-Down>", lambda event, arg=self.listbox: self.down_event(event, arg))
        self.listbox_txt.pack()
        self.listbox_frame.pack()
        self.vbar_1.pack()
        # Items
        self.items_txt = Label(system_frame, text='Items:', fg=foreground,width=40,anchor=W,padx=20)
        self.itemslistbox_frame = Frame(system_frame)
        self.vbar_2 = vbar_2 = Scrollbar(self.itemslistbox_frame , name="vbar_2")
        self.vbar_2.pack(side=RIGHT, fill=Y)
        self.itemslistbox = Listbox(self.itemslistbox_frame ,height=3,width=entry_size,exportselection=0,yscrollcommand=vbar_2.set)
        self.itemslistbox.pack()
        self.itemslistbox.insert(END, "All")
        vbar_2["command"] = self.itemslistbox.yview
        self.itemslistbox.bind("<ButtonRelease-1>", self.select_item)
        self.itemslistbox.bind("<Key-Up>", lambda event, arg=self.itemslistbox: self.up_event(event, arg))
        self.itemslistbox.bind("<Key-Down>", lambda event, arg=self.itemslistbox: self.down_event(event, arg))
        self.items_txt.pack()
        self.itemslistbox_frame.pack()
        self.vbar_2.pack()
        #Drawing
        self.can = Canvas(self, width =64, height =196, highlightthickness=0)
        bitmap = PhotoImage(file="img/doc.gif")
        try:
            self.can.create_image(32,32,image =bitmap)
            self.can.bitmap = bitmap
        except TclError as exception:
            print "TCL error:", exception
        self.can.pack(fill=Y,pady=20)
        # Build & Quit
        self.button_select = Button(self, text='OK', state=DISABLED, command = self.click_select)
        self.button_quit = Button(self, text='Quit', command = self.click_quit)
        self.button_select.pack(side=LEFT)
        self.button_quit.pack(side=LEFT)
    def changeColour(self, colour):
        print 'Colour: ' + colour
        self.listbox_txt.configure(background = colour)
    def select_item(self, event):
        ''' select item '''
        item_id = self.itemslistbox.curselection()
        self.item_id = item_id
    def select_system(self, event):
        self.button_select.configure(state=NORMAL)
        # populate items listbox
        system_id = self.listbox.curselection()
        if system_id != () and '0' not in system_id:
            self.system = self.listbox.get(system_id)
            # Populate items list box
            query = 'SELECT items.name FROM items LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE systems.name LIKE \'' + self.system + '\' ORDER BY items.name ASC'
            self.populate_listbox(query,self.itemslistbox,"All")
            self.listbox.activate(system_id)
        else:
            pass
##            self.itemslistbox.delete(0, END)
    def press_start_apache(self,event):
        config= "httpd_ece.conf"
        self.apache_start(config)
        pass
    def press_bypass_start_session(self,event):
        '''
        Bypass login. No message START_SESSION sent.
        '''
        global login_success
        global login
        global password
        global no_start_session
        global system
        global item
        global item_id
        if self.system != "":
            system = self.system
        else:
            system = ""
        if self.item_id != () and '0' not in self.item_id:
            item = self.itemslistbox.get(self.item_id)
            item_id = self.item_id
        else:
            item=""
            item_id=()
        login_success = True
        login = ""
        password = ""
##        no_start_session = True
        self.destroy()
        login_window.destroy()
    def click_bypass(self):
        global login_success
        global login
        global password
        global item
        global item_id
        global system
        system = self.system
        # Get login and password information
        login = self.login
        password = self.password
        item_id=()
        login_success = True
        self.destroy()
    def click_select(self):
        '''
         Click OK button and launch the doCID GUI
        '''
        global login_success
        global login
        global password
        global item
        global item_id
        global system
        system = self.system
        # Get login and password information
        login = self.login_entry.get()
        if login =="":
            login = "anonymous"
        password = self.password_entry.get()
        if password == "":
            password = "password"
        if self.item_id != () and '0' not in self.item_id:
            item = self.itemslistbox.get(self.item_id)
            item_id = self.item_id
        else:
            item=""
            item_id=()
        login_success = True
        self.destroy()
        login_window.destroy()
    def click_quit(self):
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit now?"):
            self.destroy()
            login_window.destroy()

    def changeColour(self, colour):
        print 'Colour: ' + colour
        self.target.configure(background = colour)

    def changeText(self, text):
        print 'Text: ' + text
        self.target.configure(text = text)
class Interface (Frame,Tool,Review,ActionGui):
    def resetReleaseListbox(self):
        self.releaselistbox.delete(0, END)
        self.releaselistbox.configure(bg="gray")
        self.releaselistbox.configure(state=DISABLED)
    def resetBaselineListbox(self):
        self.baselinelistbox.delete(0, END)
        self.baselinelistbox.configure(bg="gray")
        self.baselinelistbox.configure(state=DISABLED)
    def resetProjectListbox(self):
        self.projectlistbox.delete(0, END)
        try:
            self.projectlistbox.configure(bg="gray")
            self.projectlistbox.configure(state=DISABLED)
        except TclError as exception:
            print "TCL Error:", exception
    def _find_projects(self):
        global session_started
        self.projectlistbox.delete(0, END)
        self.projectlistbox.insert(END, "Looking for projects ...")
        if session_started:
            self.projectlistbox.configure(state=NORMAL)
            self.projectlistbox.delete(0, END)
            self.log("Get available projects...")
            if self.release not in ("","All",None,"None"):
                query = 'query -release '+ self.release +' "(cvtype=\'project\')" -f "%name-%version;%in_baseline"'
            elif self.baseline not in ("","All",None,"None"):
                query = 'baseline -u -sby project -sh projects  ' + self.baseline + ' -f "%name-%version"'
            else:
                query = 'query "(cvtype=\'project\')" -f "%name-%version"'
            self.queue.put("GET_PROJECTS") # action to get projects
            self.queue.put(query)
            self.queue.put(self.baseline)
            self.queue.put(self.release)
        else:
            self.log("No session started.")
    def find_baselines(self):
        global session_started
        self.baselinelistbox.delete(0, END)
        self.baselinelistbox_1.delete(0, END)
        self.baselinelistbox_2.delete(0, END)
        #self._resetProjectListbox()
        self.baselinelistbox.configure(state=NORMAL)
        self.baselinelistbox.delete(0, END)
        self.baselinelistbox.insert(END, "Looking for baselines ...")
        if session_started:
            self.log("Get available baselines ...")
            if self.release not in ("","All",None,"None"):
                query = 'baseline -l -release ' + self.release + ' -f "%name"'
            else:
                query = 'baseline -l -f "%name"'
            self.log("ccm " + query)
            self.queue.put("GET_BASELINES") # action to get baselines
            self.queue.put(query)
            self.baseline = "All"
        else:
            self.log("No session started.")
    def find_releases(self):
        '''
         Display Synergy releases or from file  in the GUI
        '''
        global session_started
        # Display release
        self.releaselistbox.delete(0, END)
        self.releaselistbox.insert(END, "Looking for releases ...")
        list_releases = []
        if self.partnumber not in ("All","") or self.standard not in ("All",""):
            if self.dico_list_pn != {}:
                self.releaselistbox.delete(0, END)
                if self.partnumber not in ("All",""):
                    self.releaselistbox.insert(END, "All")
                    if self.dico_pn_vs_rl.has_key(self.partnumber):
                        list_releases = self.dico_pn_vs_rl[self.partnumber]
                        for release in self.dico_pn_vs_rl[self.partnumber]:
                            self.releaselistbox.insert(END, release)
                else:
                    # Display all releases
                    self.display_release()
                self.releaselistbox.configure(bg="white")
                self.releaselistbox.selection_set(first=0)
        else:
            # Get list of releases from Synergy
            if session_started:
                self.log("Get available releases...")
                active = self.active_release_var.get()
                if active:
                    query = "release -active -u -l"
                else:
                    query = "release -u -l"
                self.log("ccm " + query)
                self.queue.put("GET_RELEASES") # action to get releases
                self.queue.put(query)
                regexp = self.release_regexp #'^SW_(.*)/(.*)$'
                self.queue.put(regexp)
            else:
                self.log("No session started.")
    def select_baseline(self, event):
##        self.releaselistbox.configure(state=DISABLED)
##        self.baselinelistbox.configure(state=DISABLED)
        self.clear_project()
        index = self.baselinelistbox.curselection()
        if index in (0,()):
            self.baseline = ""
            self.setBaselineSynergy(self.baseline)
        else:
            self.baseline = self.baselinelistbox.get(index)
            if self.baseline == "All":
                self.setBaselineSynergy("None")
                self.log("All baselines selected")
            else:
                self.setBaselineSynergy(self.baseline)
                self.log("Selected baseline: " + self.baseline)
                self.projectlistbox.configure(state=NORMAL)
                self.button_find_projects.configure(state=NORMAL)
##                self.button_select.configure(state=NORMAL)
                self.button_list_items.configure(state=NORMAL)
                self.button_list_tasks.configure(state=NORMAL)
                self._find_release_vs_baseline()
##            self._find_projects()
    def select_release(self, event):
        global session_started
        self.clear_baselines()
        self.clear_project()
        index = self.releaselistbox.curselection()
        if index in (0,()):
            self.release = ""
            self.log("All releases selected")
            self.setBaseline("None")
        else:
##            interface.button_select.configure(state=NORMAL)
            self.release = self.releaselistbox.get(index)
            if self.release == "All":
                self.setBaseline("None")
                self.log("All releases selected")
            else:
                self.log("Selected release: " + self.release)
                self.setBaseline(self.release)
                self.button_select.configure(state=NORMAL)
                self.button_list_items.configure(state=NORMAL)
                self.button_list_tasks.configure(state=NORMAL)
##        self.general_output_txt.see(END)
##        if session_started:
##            self.releaselistbox.configure(state=DISABLED)
##            self.find_baselines()
    def select_project(self, event):
        global list_projects
        index = self.projectlistbox.curselection()
        if index in (0,()):
            project = ""
            self.setProject("None")
        else:
            project = self.projectlistbox.get(index)
            if project == "All":
                self.setProject("All")
                self.log("All projects selected")
            else:
                self.setProject(project)
                list_projects = []
                self.button_select.configure(state=NORMAL)
                self.button_list_items.configure(state=NORMAL)
                self.button_list_tasks.configure(state=NORMAL)
                self.log("Selected project: " + project)
        self.project = project
    def set_baselines(self):
        '''
        Called when set project is clicked
        - Update self.project_list array with [release,baseline,project]
        - UPdate baseline_set_box listbox with project name
        '''
        if self.project == "All":
            if tkMessageBox.showinfo("All projects not accepted", "Please select one project."):
                self.log("No project selected.")
        elif self.project != "":
            project = self.project
            release = self.release
            baseline = self.baseline
            self.project_list.append([release,baseline,project])
##            self.release_list.append(release)
##            self.baseline_list.append(baseline)
            self.baseline_set_box.insert(END, project)
        else:
            if tkMessageBox.showinfo("Missing project selection", "Please select a project."):
                self.log("No project selected.")
    def setBaseline(self,release):
        '''
         set CM Synergy release
        '''
        self.baseline_change = release
        self.release = release
        self.baseline_txt.configure(text=release)
        self.release_entry.delete(0,END)
        self.release_entry.insert(END, release)
        self.impl_cr.configure(text="CR implemented for release " + self._splitComma(self.impl_release))
        self.list_items_explain.configure(text="Export items listing linked to a release " + self.release + " (directories and executable objects are discarded)")
        self.list_tasks_explain.configure(text="Export tasks listing linked to a release " + self.release + " (automatic tasks and components tasks are discarded)")
        self.list_history_explain.configure(text="Export history listing linked to a release " + self.release)
        self.log("Selected release:" + release)
        self.clear_baselines()
        self.clear_project()
    def setBaselineSynergy(self,baseline_synergy):
        '''
         set CM Synergy baseline
        '''
        self.baseline = baseline_synergy
        # in build_checklist folder
        self.baseline_entry.delete(0, END)
        self.baseline_entry.insert(END,baseline_synergy)

        self.baseline_synergy_txt.configure(text=baseline_synergy)
        self.list_items_explain.configure(text="Export items listing linked to a baseline " + baseline_synergy +" (directories and executable objects are discarded)")
        self.list_tasks_explain.configure(text="Export tasks listing linked to a baseline " + baseline_synergy + " (automatic tasks and components tasks are discarded)")
        self.list_history_explain.configure(text="Export history listing linked to a baseline " + baseline_synergy)
    def setProject(self,project):
        self.project = project
        self.project_txt.configure(text=project)
        # in build_checklist folder
        self.project_entry.delete(0, END)
        self.project_entry.insert(END,project)
    def unsetRelease(self):
        self.baseline_change = ""
        self.baseline_txt.configure(text="None")
        self.impl_cr.configure(text="CR implemented for all releases ")
    def unsetBaselineSynergy(self):
        self.baseline_synergy_txt.configure(text="None")
    def unsetProject(self):
        self.project_txt.configure(text="None")
    def clear_releases(self):
        self.release = "All"
        self.unsetRelease()
        self.releaselistbox.selection_clear(first=0,last=END)
##        self.clear_baselines()
    def clear_baselines(self):
        self.baseline = "All"
        self.unsetBaselineSynergy()
        self.baselinelistbox.selection_clear(first=0,last=END)
        self.list_items_explain.configure(text="Export items listing (directories and executable objects are discarded)")
        self.list_tasks_explain.configure(text="Export tasks listing (automatic tasks and components tasks are discarded)")
        self.list_history_explain.configure(text="Export history listing")
    def clear_project(self):
        '''
        Clear project listbox
        '''
        self.project = "All"
        self.unsetProject()
        self.projectlistbox.selection_clear(first=0,last=END)
    def clear_project_set(self):
        '''
        Clear Projects set
        '''
        self.baseline_set_box.delete(0, END)
        del self.project_list[0:]
        self.project_entry.delete(0, END)
        self.project_entry.insert(END, self.project)
        self.baseline_entry.delete(0, END)
        self.baseline_entry.insert(END, self.baseline)
        self.release_entry.delete(0, END)
        self.release_entry.insert(END, self.release)
##        del self.release_list[0:]
##        del self.baseline_list[0:]
    def select_project_to_delete(self,event):
        index = self.baseline_set_box.curselection()
        print "INDEX",index
        if index in (0,()):
            self.project_to_delete = ""
        else:
            self.project_to_delete = self.baseline_set_box.get(index[0])

    def del_project(self):
        index = self.baseline_set_box.curselection()
        if self.project_to_delete != "":
            print "Project to delete",self.project_to_delete
            print "Project list",self.project_list
            self.baseline_set_box.delete(0, END)
            new_project_list = []
            for release, baseline,project in self.project_list:
                if project == self.project_to_delete:
##                    self.project_list.remove(release,sbaseline,elf.project_to_delete)
##                    for release, baseline,project in self.project_list:
                    pass
                else:
                    self.baseline_set_box.insert(END, project)
                    new_project_list.append([release,baseline,project])
            self.project_list = new_project_list

    def save_projects(self):
        self.sqlite_save_projects(self.project_list)
        self.log("Set of project saved in SQLite databsae ")
    def restore_projects(self):
        del self.project_list[0:]
        # Clear box
        self.clear_project_set()
        self.project_list = self.sqlite_restore_projects()
        # Display projects
        # Extract list of baselines
        # Extract list of releases
        baselines_tbl = []
        releases_tbl = []
        for release, baseline,project in self.project_list:
            self.baseline_set_box.insert(END, project)
            baselines_tbl.append(baseline)
            releases_tbl.append(release)
        baselines_list_str = ", ".join(map(str, baselines_tbl))
        # Update GUI in notebook QA report
        self.baseline_entry.delete(0, END)
        self.baseline_entry.insert(END,baselines_list_str)
        releases_list_str = ", ".join(map(str, releases_tbl))
        # Update GUI in notebook QA report
        self.release_entry.delete(0,END)
        self.release_entry.insert(END, releases_list_str)
        if self.project_list != None:
            self.button_select.configure(state=NORMAL)
        self.log("Set of project restored from SQLite databsae ")

    def getTypeWorkflow(self):
        if self.type_cr_workflow in ("Old","New"):
            if self.type_cr_workflow == "Old":
                old_cr_workflow = True
            else:
                old_cr_workflow = False
        else:
            old_cr_workflow = self.status_old_workflow.get()
        self.old_cr_workflow = old_cr_workflow
        return(old_cr_workflow)
    def display_standard(self):
        # Insert standards if exist
        if self.dico_list_std != {}:
            self.stdlistbox.insert(END, "All")
            list_stds = self.dico_list_std.keys()
            list_stds.sort()
##            std_index = 0
            for key in list_stds:
                self.stdlistbox.insert(END, key)
##                std_index += 1
                self.stdlistbox.itemconfig(END, bg='white', fg='black')
##                num = 0
                for value in self.dico_list_std[key]:
##                    if num > 0:
                        self.stdlistbox.insert(END, value)
                        self.stdlistbox.itemconfig(END, bg='grey', fg='white')
##                    num += 1
            self.stdlistbox.configure(bg="white")
            self.stdlistbox.selection_set(first=0)
    def display_partnumber(self):
        # Insert part number if exist
        if self.dico_list_pn != {}:
            self.pnlistbox.insert(END, "All")
            list_pns = self.dico_list_pn.keys()
            list_pns.sort()
            for key in list_pns:
                self.pnlistbox.insert(END, key)
            self.pnlistbox.configure(bg="white")
            self.pnlistbox.selection_set(first=0)
    def display_release(self):
        # Insert releases if exist
        if self.dico_rl_vs_pn != {}:
            self.releaselistbox.insert(END, "All")
            list_rls = self.dico_rl_vs_pn.keys()
            list_rls.sort()
            # besoin de comparer ici la liste self.current_list_partnumber avec la liste self.dico_rl_vs_pn
            for key in list_rls:
                if list(set(self.current_list_partnumber).intersection(self.dico_rl_vs_pn[key])) != []:
                    self.releaselistbox.insert(END, key)
            self.releaselistbox.configure(bg="white")
            self.releaselistbox.selection_set(first=0)
    def __invert_dol_nonunique(self,d):
        '''
         To reverse dictionnary
        '''
        newdict = {}
        for k in d:
            for v in d[k]:
                newdict.setdefault(v, []).append(k)
        return newdict
    def _readConfig(self):
        '''
         Read csv config file
        '''
        # read config file
##        self.log("Read docid.ini config file.",False)
        self.config_parser = ConfigParser()
        try:
            self.config_parser.read('docid.ini')
            self.login = self.getOptions("User","login")
            self.password = self.getOptions("User","password")
            self.author = self.getOptions("User","author")
            if self.config_parser.has_section("Default"):
                self.default_template_type = self.getOptions("Default","template")
                self.reference = self.getOptions("Default","reference")
                self.revision = self.getOptions("Default","issue")
                self.part_number = self.getOptions("Default","part_number")
                self.board_part_number = self.getOptions("Default","board_part_number")
                self.checksum = self.getOptions("Default","checksum")
                self.dal = self.getOptions("Default","dal")
                self.previous_baseline = self.getOptions("Default","previous_baseline")
                self.verbose = self.getOptions("Default","verbose")
                self.release_regexp = self.getOptions("Default","release_regexp")
                # Release
                self.release = self.getOptions("Default","release")
                # Detect on
                self.previous_release = self.getOptions("Default","detect_release")
                # Implemented on
                self.impl_release = self.getOptions("Default","impl_release")
                self.baseline_change = self.release
                # Baseline
                self.baseline = self.getOptions("Default","baseline")
                self.baseline_delivery = self.getOptions("Default","baseline_delivery")
                # Project
                self.project = self.getOptions("Default","project")
            else:
                self.default_template_type = ""
                self.reference = ""
                self.revision = ""
                self.part_number = ""
                self.board_part_number = ""
                self.checksum = ""
                self.dal = ""
                self.previous_release = ""
                self.verbose = "no"
                self.release_regexp = ""
                # Release
                self.release = ""
                self.impl_release = ""
                self.baseline_change = ""
                # Baseline
                self.baseline = ""
                self.baseline_delivery = ""
                # Project
                self.project = ""
            # get A/C standards
            self.dico_rl_vs_pn = {}
            if self.config_parser.has_section("Standards"):
                if self.config_parser.has_option("Standards","file"):
                    file_csv_name = self.config_parser.get("Standards","file")
                    self.dico_std = {}
                    self.dico_list_std_vs_stdac = {}
                    self.dico_list_std = {}
                    self.dico_list_pn = {}
                    self.dico_list_pn_modified = {}
                    self.dico_list_pn_vs_stdac = {}
                    self.dico_list_pn_reverted = {}
                    self.dico_list_pn_modified_reverted = {}
                    self.dico_std_vs_pn = {}
                    # Standards avion versus PN
                    self.dico_std_ac_vs_pn = {}
                    self.dico_pn_vs_rl = {}
                    with open(file_csv_name, 'rb') as file_csv_handler:
                        reader = csv.reader (self.CommentStripper (file_csv_handler))
                        for row in reader:
                            num=0
                            list_all = []
                            # List of standards
                            list_std = []
                            # list of part numbers
                            list_pn = []
                            # List of release
                            list_rl = []
                            attr = []
                            ci_name = ""
                            type_id = ""
                            for col in row:
                                if num == 0:
                                    # Tag appearing in release box
                                    tag = col
                                elif num == 1:
                                    # Type of identification: Standard, Part Nunmber
                                    type_id = col
                                    attr.append(type_id)
                                elif num == 2:
                                    # Name of Configuration Item: ATUPU,ENMU etc ...
                                    ci_name = col
                                    attr.append(ci_name)
    ##                                list_all.append(attr)
                                else:
                                    list_all.append(col)
                                    if type_id in ("PN","SW"):
                                        list_pn.append(col)
                                    elif type_id == "STD":
                                        list_std.append(col)
                                    elif type_id == "RL":
                                        list_rl.append(col)
                                    else:
                                        pass
                                num += 1
                            if type_id in ("PN","SW"):
                                self.dico_list_pn[tag] = list_pn
                            elif type_id == "STD":
                                # STD
                                self.dico_list_std[tag] = list_std
##                                self.dico_std_ac_vs_pn[tag] = list_std
                            elif type_id == "RL":
                                self.dico_rl_vs_pn[tag] = list_rl
                            else:
                                pass
                            self.dico_std[tag] = list_all
                    self.dico_pn_vs_rl = self.__invert_dol_nonunique(self.dico_rl_vs_pn)
                    self.dico_list_std_vs_stdac = self.__invert_dol_nonunique(self.dico_list_std)
                    #
                    # Dans la liste des part numbers remplacer les standards avions par les sous-standards projets
                    #
                    for key_pn, values_std in self.dico_list_pn.iteritems() :
    ##                    print values_std
                        list_pn_vs_std = []
                        list_pn_vs_stdac = []
                        for value_std in values_std:
    ##                        print value_std
                            if self.dico_list_std.has_key(value_std):
                                # value_std est un standard avion
                                # on remplace le standard avion par les sous-standards projet
                                list_pn_vs_std.extend(self.dico_list_std[value_std])
                                list_pn_vs_stdac.append(value_std)
                            else:
                                list_pn_vs_stdac.extend(self.dico_list_std_vs_stdac[value_std])
                                list_pn_vs_std.append(value_std)
                        self.dico_list_pn_vs_stdac[key_pn] = list_pn_vs_stdac
                        self.dico_list_pn_modified[key_pn] = list_pn_vs_std
                    self.dico_list_stdac_vs_pn = self.__invert_dol_nonunique(self.dico_list_pn_vs_stdac)
##                    print self.dico_list_stdac_vs_pn
                    # Inverse le dictionnaire des part_numbers
                    self.dico_list_pn_modified_reverted = self.__invert_dol_nonunique(self.dico_list_pn_modified)
                    # Met à jour la liste des standards aves les sous-standards
                    self.dico_std.update(self.dico_list_pn_modified_reverted)
##                    print self.dico_std
                    # revert dico to update dictionary with part numbers
                    self.dico_list_pn_reverted = self.__invert_dol_nonunique(self.dico_list_pn)
                    for key_std, value_pn in self.dico_list_pn_reverted.iteritems() :
                        for key_std_aircraft, value_std in self.dico_list_std.iteritems() :
                            if key_std in self.dico_list_std[key_std_aircraft]:
                                # le sous-standard key_std est-il associé à un standard key_std_aircraft ?
                                # Example:
                                #   dico_list_std => Standard 1,STD,EPDS,S1,S1.1
                                #   dico_list_pn => 955CE05Y03:S1
                                #                   335CE06YXX:S1
                                #   dico_list_pn_reverted => S1:955CE05Y03,335CE06YXX
                                #   Ici S1 fait partie du Standard 1 donc on ajoute la liste des part number à dico_std_vs_pn
                                #   dico_std_vs_pn => Standard 1,955CE05Y03,335CE06YXX
                                #
                                self.dico_std[key_std_aircraft].extend(self.dico_list_pn_reverted[key_std])
                                self.dico_std_vs_pn[key_std_aircraft] = self.dico_list_pn_reverted[key_std]
                            elif key_std == key_std_aircraft:
                                self.dico_std[key_std_aircraft].extend(self.dico_list_pn_reverted[key_std])
                                self.dico_std_vs_pn[key_std_aircraft] = self.dico_list_pn_reverted[key_std]
                    # Create table Standard, sub-standard versus part number
                    self.dico_std_vs_pn.update(self.dico_list_pn_modified_reverted)
                    self.current_list_partnumber = self.dico_list_pn.keys()
                    self.std_exists = True
                else:
                    self.std_exists = False
        except KeyError as exception:
            print "A/C standards determination failed:", exception
        except IOError as exception:
            print "A/C standards determination failed:", exception
    def getStandard(self):
        return self.std_exists
    def click_update_pn_csv(self):
        self._readConfig()
        self.releaselistbox.delete(0, END)
        self.queue.put("GET_RELEASES") # action to get releases
    def click_update_config(self):
        # read config file
        self._readConfig()
        self.queue.put("RELOAD_CONFIG")
    def __init__(self, notebook,queue,system,item, **kwargs):
        global background
        global foreground
        global entry_size
        global item_id
        ActionGui.__init__(self)
##        Action.__init__(self)
        self.std_exists = False
        self.current_list_partnumber = []
        self.dico_std = {}
        self.checkbutton_all = False
        # read config file
        self.default_template_type = "SCI"
        self.reference = "" #"ET1234-V"
        self.revision = "" #"1D1"
        self.release = ""
        self.baseline_change = ""
        self.baseline = ""
        self.previous_baseline = ""
        self.detect_release = ""
        self.project = ""
        self.verbose = "no"
        # Read config
        self._readConfig()
        # Set logging
        self.loginfo = logging.getLogger(__name__)
        if self.verbose == "yes":
            out_hdlr = logging.FileHandler(filename='docid.log')
        else:
            out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        out_hdlr.setLevel(logging.INFO)
        self.loginfo.addHandler(out_hdlr)
        self.loginfo.setLevel(logging.INFO)
        self.loginfo.debug("NO")
        self.system = system
        self.item = item
        self.component = ""
        self.cr_type = ""
        self.review_qams_id = ""
        self.project_to_delete = ""
        # Get
        #       - Database
        #       - Aircraft
        #
        if self.item != "":
            self.database,self.aircraft = self.get_sys_item_database(self.system,self.item)
            if self.database == None:
                self.database,self.aircraft = self.get_sys_database()
        else:
            self.database,self.aircraft = self.get_sys_database()
        self.standard = ""
        self.partnumber = "" # Warning, P/N managed by the listbox pnlistbox in the GUI class
##        self.board_part_number = ""
        self.item_id = item_id
        self.session_started = False
        self.queue = queue
        self.project_list = []
        self.attribute = "CR_implemented_for"
##        self.release_list = []
##        self.baseline_list = []
        self.type_cr_workflow = "None"
        # Create widgets
        entry_size = 40
        # Add pages to the notebook.
        page_create_cid = notebook.add('Create configuration index document')
        page_create_ccb = notebook.add('Change Requests query')
        page_check_baseline = notebook.add('Synergy specific commands')
        page_synergy_cli = notebook.add('Synergy easy Command Line Interface')
##        page_create_sqap = notebook.add('Create SQAP')
##        self.hidepage(page_create_sqap)
        page_create_checklist = notebook.add('Create AQ report')
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, page_create_cid, width=700, height=576,relief =GROOVE,**kwargs)
        self.pack(fill=BOTH)
        self.cid_config = Frame(self)
        row_index = 1
        self.cid_config.pack(side=LEFT)
        # Type of CID
        row_index = 1
        self.cid_type_txt = Label(self.cid_config, text='CID type:', fg=foreground)
        self.cid_var_type = StringVar()
        self.hcmr_var_type = StringVar()
        self.radiobutton_sci = Radiobutton(self.cid_config, indicatoron=0,width = 12,text="SCI", variable=self.cid_var_type,value="SCI",fg=foreground,command=self.cid_type)
        self.radiobutton_hci = Radiobutton(self.cid_config, indicatoron=0,width = 12,text="HCMR", variable=self.cid_var_type,value="HCMR",fg=foreground,command=self.cid_type)
        self.radiobutton_cid = Radiobutton(self.cid_config, indicatoron=0,width = 12,text="CID", variable=self.cid_var_type,value="CID",fg=foreground,command=self.cid_type)
        self.radiobutton_hci_pld =Radiobutton(self.cid_config, text="HCMR PLD", variable=self.hcmr_var_type,value="HCMR_PLD",fg=foreground,command=self.cid_type)
        self.radiobutton_hci_board =Radiobutton(self.cid_config, text="HCMR BOARD", variable=self.hcmr_var_type,value="HCMR_BOARD",fg=foreground,command=self.cid_type)
        self.cid_var_type.set(self.default_template_type) # initialize
        self.hcmr_var_type.set("HCMR_PLD") # initialize
        self.cid_type_txt.grid(row =row_index,sticky='E')
        self.radiobutton_sci.grid(row =row_index, column =1, padx=10,sticky='W')
        self.radiobutton_hci.grid(row =row_index, column =1, padx=88,sticky='W')
        self.radiobutton_cid.grid(row =row_index, column =1, padx=10,sticky='E')
        row_index += 1
        self.radiobutton_hci_pld.grid(row =row_index, column =1, padx=10,sticky='W')
        self.radiobutton_hci_board.grid(row =row_index, column =1, padx=10,sticky='E')
        # Author
        row_index += 1
        author_txt = Label(self.cid_config, text='Author:', fg=foreground)
        author_txt.grid(row =row_index,sticky='E')
        self.author_entry = Entry(self.cid_config, state=NORMAL,width=entry_size)
        self.author_entry.insert(END, self.author)
        self.author_entry.grid(row = row_index, column =1,sticky='E')
        # Reference
        row_index += 1
        reference_txt = Label(self.cid_config, text='Reference:', fg=foreground)
        self.reference_entry = Entry(self.cid_config, state=NORMAL,width=entry_size)
        self.reference_entry.insert(END, self.reference)
        reference_txt.grid(row =row_index,sticky='E')
        self.reference_entry.grid(row = row_index, column =1,sticky='E')
        # Issue
        row_index += 1
        revision_txt = Label(self.cid_config, text='Issue:', fg=foreground)
        self.revision_entry = Entry(self.cid_config, state=NORMAL,width=entry_size)
        self.revision_entry.insert(END, self.revision)
        revision_txt.grid(row =row_index,sticky='E')
        self.revision_entry.grid(row =row_index, column =1,sticky='E')
        # Part number
        row_index += 1
        part_number_txt = Label(self.cid_config, text='Part Number:', fg=foreground)
        self.part_number_entry = Entry(self.cid_config, state=NORMAL,width=entry_size)
        self.part_number_entry.insert(END, self.part_number)
        part_number_txt.grid(row =row_index,sticky='E')
        self.part_number_entry.grid(row =row_index, column =1,sticky='E')
        # Board Part number
        row_index += 1
        board_part_number_txt = Label(self.cid_config, text='Board P/N:', fg=foreground)
        self.board_part_number_entry = Entry(self.cid_config, state=NORMAL,width=entry_size)
        self.board_part_number_entry.insert(END, self.board_part_number)
        board_part_number_txt.grid(row =row_index,sticky='E')
        self.board_part_number_entry.grid(row =row_index, column =1,sticky='E')
        # Checksum
        row_index += 1
        checksum_txt = Label(self.cid_config, text='Checksum:', fg=foreground)
        self.checksum_entry = Entry(self.cid_config, state=NORMAL,width=entry_size)
        self.checksum_entry.insert(END, self.checksum)
        checksum_txt.grid(row =row_index,sticky='E')
        self.checksum_entry.grid(row =row_index, column =1,sticky='E')
        # DAL
        row_index += 1
        dal_txt = Label(self.cid_config, text='DAL:', fg=foreground)
        self.dal_entry = Entry(self.cid_config, state=NORMAL,width=entry_size)
        self.dal_entry.insert(END, self.dal)
        dal_txt.grid(row =row_index,sticky='E')
        self.dal_entry.grid(row =row_index, column =1,sticky='E')
        # Previous baseine
        row_index += 1
        previous_baseline_txt = Label(self.cid_config, text='Previsou Baseline:', fg=foreground)
        self.previous_baseline_entry = Entry(self.cid_config, state=NORMAL,width=entry_size)
        self.previous_baseline_entry.insert(END, self.previous_baseline)
        previous_baseline_txt.grid(row =row_index,sticky='E')
        self.previous_baseline_entry.grid(row =row_index, column =1,sticky='E')
        # Build
        row_index += 1
        self.button_select = Button(self.cid_config, text='Generate', state=DISABLED, command = self.click_build_cid)
        self.button_select.grid(row =row_index, column =1,pady=5,sticky='E')
        self.button_cancel = Button(self.cid_config, text='Cancel', command = self.click_cancel_build_cid)
        self.button_cancel.grid(row =row_index, column =1,pady=5,sticky='W')
        # Check buttons
        row_index += 1
        self.objects_txt = Label(self.cid_config, text='Objects:', fg=foreground)
        self.status_released = IntVar()
        self.check_button_status_released = Checkbutton(self.cid_config, text="Only in state 'Released'", variable=self.status_released,fg=foreground,command=self.cb_released)
        self.status_integrate = IntVar()
        self.check_button_status_integrate = Checkbutton(self.cid_config, text="Only in state 'Integrate'", variable=self.status_integrate,fg=foreground,command=self.cb_integrate)
        self.objects_txt.grid(row =row_index,sticky='E')
        self.check_button_status_released.grid(row =row_index, column =1, padx=10,sticky='W')
        row_index += 1
        self.check_button_status_integrate.grid(row =row_index, column =1,padx=10,sticky='W')
        #
        # Projects set
        #
        self.cid_config_middle = Frame(self)
        row_index = 1
        self.cid_config_middle.pack(side=LEFT)
        row_index += 1
        items_txt = Label(self.cid_config_middle, text='Projects set:', fg=foreground,width=40,anchor=W,padx=20)
        items_txt.grid(row = row_index, sticky='E')
        row_index += 1
        self.baseline_set_frame = Frame(self.cid_config_middle)
        self.baseline_set_frame.grid(row = row_index, padx=30,sticky='W')
        self.vbar_baseline_set = vbar_baseline_set = Scrollbar(self.baseline_set_frame , name="vbar_baseline_set")
        self.vbar_baseline_set.pack(side=RIGHT, fill=Y)
        self.baseline_set_box = Listbox(self.baseline_set_frame ,height=8,width=30,exportselection=0,yscrollcommand=vbar_baseline_set.set)
        self.baseline_set_box.pack()
        vbar_baseline_set["command"] = self.baseline_set_box.yview
        self.baseline_set_box.bind("<ButtonRelease-1>", self.select_project_to_delete)
        row_index += 1
        self.button_clear_projects = Button(self.cid_config_middle, text='Clear', state=NORMAL, command = self.clear_project_set)
        self.button_clear_projects.grid(row = row_index, padx=50, sticky='E')
        self.button_del_project = Button(self.cid_config_middle, text='Del', state=NORMAL, command = self.del_project)
        self.button_del_project.grid(row = row_index, padx=20, sticky='E')
        self.button_save_projects = Button(self.cid_config_middle, text='Save', state=NORMAL, command = self.save_projects)
        self.button_save_projects.grid(row = row_index, padx=20, sticky='W')
        self.button_restore_projects = Button(self.cid_config_middle, text='Restore', state=NORMAL, command = self.restore_projects)
        self.button_restore_projects.grid(row = row_index, padx=60, sticky='W')
        row_index += 1
        self.items_explain_txt = Label(self.cid_config_middle, text='This listbox displays projects selected for CID\n generation by the "Set" button below.', fg=foreground,width=40,anchor=W,padx=20)
        self.items_explain_txt.grid(row = row_index, sticky='E')
        #
        # Right
        #
        self.cid_config_right = Frame(self)
        row_index = 1
        self.cid_config_right.pack(side=LEFT)
        # Description of the selected project
        self.project_description = Label(self.cid_config_right,text='System:' + self.system, fg=foreground)
        self.project_description.grid(row =row_index,padx =0,sticky='W')
        # Items
        row_index += 1
        items_txt = Label(self.cid_config_right, text='Board items:', fg=foreground,width=40,anchor=W,padx=0)
        items_txt.grid(row = row_index, sticky='W')
        row_index += 1
        self.itemslistbox_frame = Frame(self.cid_config_right)
        self.itemslistbox_frame.grid(row = row_index, padx=0,sticky='W')
        self.vbar_2 = vbar_2 = Scrollbar(self.itemslistbox_frame , name="vbar_2")
        self.vbar_2.pack(side=RIGHT, fill=Y)
        self.itemslistbox = Listbox(self.itemslistbox_frame ,height=3,width=30,exportselection=0,yscrollcommand=vbar_2.set)
        self.itemslistbox.pack()
        self.itemslistbox.insert(END, "All")
        vbar_2["command"] = self.itemslistbox.yview
        self.itemslistbox.bind("<ButtonRelease-1>", self.select_item)
        self.itemslistbox.bind("<Key-Up>", lambda event, arg=self.itemslistbox: self.up_event(event, arg))
        self.itemslistbox.bind("<Key-Down>", lambda event, arg=self.itemslistbox: self.down_event(event, arg))
        # Components
        row_index += 1
        components_txt = Label(self.cid_config_right, text='Software or PLD components:', fg=foreground,width=40,anchor=W,padx=0)
        components_txt.grid(row = row_index, sticky='W')
        row_index += 1
        componentslistbox_frame = Frame(self.cid_config_right)
        componentslistbox_frame.grid(row = row_index, padx=0,sticky='W')
        self.vbar_components = vbar_components = Scrollbar(componentslistbox_frame , name="vbar_components")
        self.vbar_components.pack(side=RIGHT, fill=Y)
        self.componentslistbox = Listbox(componentslistbox_frame ,height=3,width=30,exportselection=0,yscrollcommand=vbar_components.set)
        self.componentslistbox.pack()
        self.componentslistbox.insert(END, "All")
        vbar_components["command"] = self.componentslistbox.yview
        self.componentslistbox.bind("<ButtonRelease-1>", self.select_component)
        self.componentslistbox.bind("<Key-Up>", lambda event, arg=self.componentslistbox: self.up_event(event, arg))
        self.componentslistbox.bind("<Key-Down>", lambda event, arg=self.componentslistbox: self.down_event(event, arg))
##        row_index += 1
##        detect_cr_txt = "CR detected in release " + self.previous_release
##        self.detect_cr = Label(self.cid_config_right, text=detect_cr_txt, fg=foreground,width=40,anchor=W,padx=0)
##        self.detect_cr.grid(row = row_index, sticky='W')
##        row_index += 1
##        impl_cr_txt = "CR implemented for release " + self.release
##        self.impl_cr = Label(self.cid_config_right, text=impl_cr_txt, fg=foreground,width=40,anchor=W,padx=0)
##        self.impl_cr.grid(row = row_index, sticky='W')
        # Check new/old CR workflow
        row_index += 1
        self.workflow_txt = Label(self.cid_config_right, text='CR workflow:', fg=foreground)
        self.status_old_workflow = IntVar()
        self.check_cr_workflow_status = Checkbutton(self.cid_config_right, text="Old", variable=self.status_old_workflow,fg=foreground,command=self.cb_old_workflow)
##        print "TEST",self.system,self.item
        old_workflow = self.get_sys_item_old_workflow(self.system,self.item)
        if old_workflow:
            self.check_cr_workflow_status.select()
        self.workflow_txt.grid(row =row_index,sticky='W')
        self.check_cr_workflow_status.grid(row =row_index, padx=70,sticky='W')
        self.workflow_txt.grid_forget()
        self.check_cr_workflow_status.grid_forget()
        self.cid_config_right_spare = Frame(self,width=120)
        # Image
        self.can = Canvas(self.cid_config_right_spare, width =240, height =116,highlightthickness=0)
##        bitmap = PhotoImage(file="img/earhart12_240x116.gif")
##        self.can.create_image(120,58,image =bitmap)
##        self.can.bitmap = bitmap
        # Display aircraft image
        if self.aircraft not in ("",None,"None"):
            aircraft_img = self.get_image(self.aircraft)
            try:
                bitmap = PhotoImage(file="img/"+ aircraft_img)
            except TclError as exception:
                print "TCL error:", exception
                bitmap = PhotoImage(file="img/earhart12_240x116.gif")
        else:
            bitmap = PhotoImage(file="img/earhart12_240x116.gif")
        row_index += 1
        try:
            self.can.create_image(120,58,image =bitmap)
            self.can.bitmap = bitmap
            self.can.grid(row =row_index, rowspan =5, padx =20, pady =30,sticky='W')
        except TclError as exception:
                print "TCL error:", exception
        self.cid_config_right_spare.pack()
        # Build SQAP folder in the notebook
##        self._build_sqap_folder(page_create_sqap,**kwargs)
        # Build checklist folder in the notebook
        self._build_checklist_folder(page_create_checklist,**kwargs)
        # Build CCB folder in the notebook
        self._build_ccb_folder(page_create_ccb,**kwargs)
        self.cid_type()
        # Build checklist folder in the notebook
        self._check_baseline_folder(page_check_baseline,**kwargs)
        # Build Synergy CLI folder in the notebook
        self._synergy_cli(page_synergy_cli,**kwargs)
        # Populate items list box
        self.item = self.populate_specific_listbox(self.itemslistbox,self.item_id,self.system)
        # Populate components list box
        self.populate_components_listbox(self.componentslistbox,(),self.item,self.system)
##        page_create_checklist = notebook.delete('Create checklist')
        # OAP_review  self.hidepage(notebook,'Create checklist')
    def _setPreviousRelease(self,event=""):
        '''
        Set detected on parameter for change request query
        '''
        self.previous_release = self.previous_release_entry.get()
        self.detect_release = self.previous_release

        if self.previous_release == "":
            text = "CR detected in all releases "
        else:
            text = "CR detected in release " + self._splitComma(self.previous_release)
        self.detect_cr.configure(text=text)
        self.log(text,False)
        self.defill()
    def _setImplRelease(self,event=""):
        '''
        Set implemented for parameter for change request query
        '''
        self.impl_release = self.impl_release_entry.get()
        self.target_release_entry.delete(END)
        self.target_release_entry.insert(END,self.impl_release)
        if self.impl_release == "":
            text = "CR implemented in all releases "
        else:
            text = "CR implemented in release " + self._splitComma(self.impl_release)
        self.impl_cr.configure(text=text)
        self.log(text,False)
        self.defill()
    def _setCRType(self,event=""):
        '''
        Set implemented for parameter for change request query
        '''
        self.cr_type = self.cr_type_entry.get()
        if self.cr_type == "":
            text = "All CR types "
        else:
            text = "CR type selected: " + self.cr_type
        self.log(text,False)
        self.defill()
    def hidepage(self, notebook,pageName):
##        pass
        """New method hidepage"""
        # hide is not possible if only one page present
        if len(notebook._pageNames) == 1:
            return
        pageInfo = notebook._pageAttrs[pageName]
##        print "pageInfo",pageInfo
        # attribute visible does not exist in PMW v1.3.0
##        # return, if already hidden
##        if pageInfo['visible'] == 0:
##            return
##
##        pageInfo['visible'] = 0
        pageIndex = notebook.index(pageName)
        if pageIndex == 0:
            newTopIndex = 1
        else:
            newTopIndex = 1#pageIndex - 1
        if newTopIndex >=  0:
            newTopPage = notebook._pageNames[newTopIndex]
            notebook.selectpage(newTopPage)
        if notebook._withTabs:
            notebook._pending['tabs'] = 1
            notebook._layout()
##    def select_item(self, event):
##        ''' select item and enable OK button to goto the next popup window'''
##        item_id = self.itemslistbox.curselection()
##        self.item_id = item_id
    def changeColour(self, colour):
        print colour
##        self.listbox_txt.configure(background = colour)
    def _synergy_cli(self,page,**kwargs):
        Frame.__init__(self, page, width=768, height=576,relief =GROOVE, **kwargs)
        self.pack(fill=BOTH,expand=1)
        # command
        row_index = 1
        command_frame = LabelFrame(self, text='Synergy command:',bd=0)
        command_frame.pack(fill=BOTH,expand=1,ipadx=5,ipady=5)
##        self.command_label = Label(command_frame, text='Synergy command:',fg=foreground)
##        self.command_label.pack(fill=X);
        self.command_txt = Text(command_frame,wrap=WORD, height = 6)
        self.command_txt.pack(fill=X,expand=1)
        self.command_ex = Text(command_frame, fg=foreground,bg="grey", height = 6)
        self.command_ex.insert(END,'Examples:\n=========\n')
##        if self.release != "":
        self.command_ex.insert(END,'task -u -qu -rel SW_PLAN/01 -f "%displayname %status %task_synopsis"\n')
        self.command_ex.insert(END,'task -show objects 602\n')
        self.command_ex.insert(END,'task -show info 21\n')
        self.command_ex.insert(END,'task -show change_request 68\n')
        self.command_ex.insert(END,'query -sby name -ch -n "SQAP_SW_PLAN_PQ 0.1.0.155.docx" -release SW_PLAN/01 -f "%name %version %task %task_synopsis %change_request %change_request_synopsis"\n')
        self.command_ex.insert(END,'query -sby name -ch -n *.* -release A267/11  -f "%name %version %modify_time %status %task %change_request"\n')
        self.command_ex.insert(END,'dir SW_PLAN_WDS\PSAC@SW_PLAN_WDS:doc\n')
        self.command_ex.insert(END,'baseline -c SW_PLAN_SQA_01_01 -d "Create planning review baseline" -r SW_PLAN/01 -purpose "For planning review actions tracking" -p SW_PLAN_SQA-1.0')
        self.command_ex.pack(fill=X,expand=1);
        # send command
        self.button_send_cmd = Button(command_frame, text='Exec', command = self.click_send_cmd)
        self.button_send_cmd.pack(side=RIGHT,fill=X,padx=5)
    def _check_baseline_folder(self,page,**kwargs):
        Frame.__init__(self, page, width=768, height=576,relief =GROOVE,**kwargs)
        self.pack(fill=BOTH)
        baseline_frame = LabelFrame(self, text='Baseline',bd=1,padx=10,pady=10)
        baseline_frame.pack(fill=BOTH,expand=1,ipadx=5,ipady=5)
        # Previous baseline
        self.baseline_txt_1 = LabelFrame(baseline_frame, text='Previous baseline:', fg=foreground,bd=0)
        self.baseline_txt_1.pack(side=LEFT);
        self.baselinelistbox_1 = Listbox(self.baseline_txt_1,height=6,width=entry_size,exportselection=0)
        self.vbar_5_1 = vbar_5_1 = Scrollbar(self.baseline_txt_1, width=16,name="vbar_5_1")
        vbar_5_1["command"] = self.baselinelistbox_1.yview
        self.baselinelistbox_1["yscrollcommand"] = vbar_5_1.set
        self.vbar_5_1.pack(side=RIGHT, fill=Y)
        self.baselinelistbox_1.bind("<ButtonRelease-1>", self.select_baseline_prev)
        self.baselinelistbox_1.bind("<Key-Up>", lambda event, arg=self.baselinelistbox_1: self.up_event(event, arg))
        self.baselinelistbox_1.bind("<Key-Down>", lambda event, arg=self.baselinelistbox_1: self.down_event(event, arg))
        self.baselinelistbox_1.pack();
        # Current baseline
        self.baseline_txt_2 = LabelFrame(baseline_frame, text='Current baseline:', fg=foreground,bd=0)
        self.baseline_txt_2.pack(side=LEFT);
        self.baselinelistbox_2 = Listbox(self.baseline_txt_2,height=6,width=entry_size,exportselection=0)
        self.vbar_5_2 = vbar_5_2 = Scrollbar(self.baseline_txt_2,width=16, name="vbar_5_2")
        vbar_5_2["command"] = self.baselinelistbox_2.yview
        self.baselinelistbox_2["yscrollcommand"] = vbar_5_2.set
        self.vbar_5_2.pack(side=RIGHT, fill=Y)
        self.baselinelistbox_2.bind("<ButtonRelease-1>", self.select_baseline_cur)
        self.baselinelistbox_2.bind("<Key-Up>", lambda event, arg=self.baselinelistbox_2: self.up_event(event, arg))
        self.baselinelistbox_2.bind("<Key-Down>", lambda event, arg=self.baselinelistbox_2: self.down_event(event, arg))
        self.baselinelistbox_2.pack();
        # Diff
        self.button_make_diff = Button(baseline_frame, text='Diff baselines', state=DISABLED, command = self.click_make_baseline_diff)
        self.button_make_diff.pack(side=LEFT,fill=Y,padx=5,pady=20);
        self.button_show_baseline = Button(baseline_frame, text='Show baseline', state=DISABLED, command = self.click_show_baseline)
        self.button_show_baseline.pack(side=LEFT,fill=Y,padx=5,pady=20);
        # List items and tasks
        commands_txt = LabelFrame(self, text='Miscelleanous commands:', fg=foreground,bd=0)
        commands_txt.pack(side=LEFT);
        button_frame = LabelFrame(commands_txt, fg=foreground,bd=0)
        button_frame.pack(side=LEFT);
        self.button_list_items = Button(button_frame, text='List items', state=NORMAL,width=18, command = self.list_items)
        self.button_list_items.pack()
        self.button_list_tasks = Button(button_frame, text='List tasks', state=NORMAL,width=18, command = self.click_list_tasks)
        self.button_list_tasks.pack();
        self.button_list_history = Button(button_frame, text='List history', state=NORMAL,width=18, command = self.click_list_history)
        self.button_list_history.pack(fill=X);
        self.history_scope = IntVar()
        self.with_cr = IntVar()
        checkbox_frame = LabelFrame(commands_txt, fg=foreground,bd=0)
        checkbox_frame.pack(side=LEFT);
        self.radio_scope_list_tasks = Checkbutton(checkbox_frame, text="With CR", variable=self.with_cr,fg=foreground)
        self.radio_scope_list_tasks.pack(fill=X,pady=10,anchor=W);
        self.radio_scope_list_tasks.config(state=NORMAL)
##        self.radio_scope_list_tasks.select()
        self.radio_scope_list_history = Checkbutton(checkbox_frame, text="Only source files",variable=self.history_scope,fg=foreground)
        self.radio_scope_list_history.pack(fill=X,anchor=W);
        self.radio_scope_list_history.config(state=NORMAL)
        self.radio_scope_list_history.select()
        explain_frame = LabelFrame(commands_txt, fg=foreground,bd=0)
        explain_frame.pack(fill=X);
        self.list_items_explain = Label(explain_frame, text="Export items listing linked to a release or a baseline (directories and executable objects are discarded)", fg=foreground,width=80,anchor=W,padx=50,pady=4)
        self.list_items_explain.pack(fill=X)
        self.list_tasks_explain = Label(explain_frame, text="Export tasks listing linked to a release or a baseline (automatic tasks and components tasks are discarded)", fg=foreground,width=80,anchor=W,padx=50,pady=4)
        self.list_tasks_explain.pack(fill=X)
        self.list_history_explain = Label(explain_frame, text="Export history of items linked to a release or a baseline", fg=foreground,width=80,anchor=W,padx=50,pady=4)
        self.list_history_explain.pack(fill=X)

    def _build_checklist_folder(self,page,**kwargs):
        '''
        Create page for review report generation
        '''
        self.var_review_type = IntVar()
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, page, width=256, height=576,relief =GROOVE, **kwargs)
        self.pack(fill=BOTH)
        review_list_frame = Frame(self,page,width=50)
        # Type of review
        review_type_txt = Label(review_list_frame, text='Review type:', fg=foreground)
        review_type_txt.pack()
        review_list = Review.getReviewList()
##        print review_list
        for id,text in review_list:
            b = Radiobutton(review_list_frame, indicatoron=0,width = 40, text=text,variable=self.var_review_type, value=id)
            if id not in (1,2,3,9):
                b.config(state=DISABLED)
            b.pack(anchor=W)
        self.var_review_type.set(1) # initialize

        spare = Label(review_list_frame)
        spare.pack()
        button_create_review = Button(review_list_frame, text='Create report', state=NORMAL, command = self.click_create_report,justify=LEFT)
        button_create_review.pack(fill=X)

        audit_list_frame = Frame(self,page,width=50)
        audit_type_txt = Label(audit_list_frame, text='Evaluation type:', fg=foreground,anchor=W)
        audit_type_txt.pack()
        audit_list = [(20,"Specification"),
                        (21,"Design"),
                        (22,"Coding"),
                        (23,"Tests"),
                        (24,"Delivery")]
##        print review_list
        for id,text in audit_list:
            b = Radiobutton(audit_list_frame, indicatoron=0,width = 40, text=text,variable=self.var_review_type, value=id)
            if id not in (20,):
                b.config(state=DISABLED)
            b.pack(anchor=W)
        info_frame = Frame(self,page,width=50)

        # Author
        author_txt = Label(info_frame, text='Author:', fg=foreground,width=40,anchor=W,padx=20)
        self.author_entry = Entry(info_frame, width=entry_size,state=NORMAL,bg="gray")
        self.author_entry.insert(END, self.author)
        author_txt.pack()
        self.author_entry.pack()
        # Part number
        part_number_txt = Label(info_frame, text='Part number:', fg=foreground,width=40,anchor=W,padx=20)
        self.ccb_part_number_entry = Entry(info_frame, width=entry_size,state=NORMAL,bg="gray")
        self.ccb_part_number_entry.insert(END, self.part_number)
        part_number_txt.pack()
        self.ccb_part_number_entry.pack()
        # Checksum
        checksum_txt = Label(info_frame, text='Checksum:', fg=foreground,width=40,anchor=W,padx=20)
        self.ccb_checksum_entry = Entry(info_frame, width=entry_size,state=NORMAL,bg="gray")
        self.ccb_checksum_entry.insert(END, self.checksum)
        checksum_txt.pack()
        self.ccb_checksum_entry.pack()
        # Release
        release_txt = Label(info_frame, text='Release:', fg=foreground,width=40,anchor=W,padx=20)
        self.release_entry = Entry(info_frame, width=entry_size,state=NORMAL,bg="gray")
        self.release_entry.insert(END, self.release)
        release_txt.pack()
        self.release_entry.pack()
        # Target release
        target_release_txt = Label(info_frame, text='Target release:', fg=foreground,width=40,anchor=W,padx=20)
        self.target_release_entry = Entry(info_frame, width=entry_size,state=NORMAL,bg="gray")
        self.target_release_entry.insert(END, self.previous_release)
        target_release_txt.pack()
        self.target_release_entry.pack()
        # Baseline
        baseline_txt = Label(info_frame, text='Baseline:', fg=foreground,width=40,anchor=W,padx=20)
        self.baseline_entry = Entry(info_frame, width=entry_size,state=NORMAL,bg="gray")
        baseline_txt.pack()
        self.baseline_entry.pack()

        # Project
        project_txt = Label(info_frame, text='Project:', fg=foreground,width=40,anchor=W,padx=20)
        self.project_entry = Entry(info_frame, width=entry_size,state=NORMAL,bg="gray")
        project_txt.pack()
        self.project_entry.pack()

        # Review QAMS ID
        review_qams_id_txt = Label(info_frame, text='Review QAMS ID:', fg=foreground,width=40,anchor=W,padx=20)
        self.review_qams_id_entry = Entry(info_frame, width=entry_size,state=NORMAL,bg="gray")
        review_qams_id_txt.pack()

        self.review_qams_id_entry.pack()
        list_review_frame = Frame(self,page,width=50)
        review_qams_id_txt = Label(list_review_frame, text='Review list:', fg=foreground,width=40,anchor=W,padx=20)
        review_qams_id_txt.pack()
        self.reviewlistbox = Listbox(list_review_frame,height=15,width=64,exportselection=0,state=DISABLED,bg="gray")
        self.reviewlistbox.insert(END, "All")
        self.vbar_reviewlisbox = vbar_reviewlisbox = Scrollbar(list_review_frame, name="vbar_reviewlisbox")
        self.vbar_reviewlisbox.pack(side=RIGHT, fill=Y)
        vbar_reviewlisbox["command"] = self.reviewlistbox.yview
        self.reviewlistbox["yscrollcommand"] = vbar_reviewlisbox.set
        self.reviewlistbox.bind("<ButtonRelease-1>", self.select_review_list)
        self.reviewlistbox.bind("<MouseWheel>", self.reviewlistbox_scrollEvent)
##        self.reviewlistbox.bind("<<ListboxSelect>>", self.reviewlistbox_onselect)
        self.reviewlistbox.bind("<Button-1>", self.reviewlistbox_onselect)
        self.reviewlistbox.bind("<Key-Up>", lambda event, arg=self.reviewlistbox: self.up_event(event, arg))
        self.reviewlistbox.bind("<Key-Down>", lambda event, arg=self.reviewlistbox: self.down_event(event, arg))
        self.reviewlistbox.pack()

        # Update list of project of GUI
        self.reviewlistbox.configure(state=NORMAL)
        self.reviewlistbox.delete(0, END)
        inter = 0
        from api_mysql import MySQL
        mysql = MySQL()
        list_review = mysql.exportReviewsList()
        for review_description in list_review:
            self.reviewlistbox.insert(END, review_description)
            if inter % 2 == 0:
                self.reviewlistbox.itemconfig(inter,{'bg':'darkgrey','fg':'white'})
            else:
                self.reviewlistbox.itemconfig(inter,{'bg':'lightgrey','fg':'black'})
            inter += 1
        self.reviewlistbox.configure(bg="white")

        review_list_frame.pack(side=LEFT)
        audit_list_frame.pack(side=LEFT)
        info_frame.pack(side=LEFT)
        list_review_frame.pack(side=LEFT)

    def click_create_report(self):
        self.queue.put("BUILD_REVIEW_REPORT") # action to get projects
        self.queue.put("PR")
        pass
    def _build_sqap_folder(self,page,**kwargs):
        global entry_size
        global project_item
        self.item = project_item
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, page, width=768, height=576,relief =GROOVE,**kwargs)
        self.pack(fill=BOTH)
        row_index = 1
        # Description of the selected project
        self.project_description_pg2 = Label(self, text="Project:",fg=foreground)
        self.project_description_pg2.grid(row =row_index,sticky='E')
        self.project_description_entry_pg2 = Entry(self,width=entry_size)
        self.project_description_entry_pg2.insert(END, self.getItemDescription(project_item))
        self.project_description_entry_pg2.grid(row =row_index,column =1,sticky='E')
        # Author
        row_index = row_index + 1
        self.author_txt_pg2 = Label(self, text='Author:', fg=foreground)
        self.author_txt_pg2.grid(row =row_index,sticky='E')
        self.author_entry_pg2 = Entry(self, state=NORMAL,width=entry_size)
        self.author_entry_pg2.insert(END, self.author)
        self.author_entry_pg2.grid(row = row_index, column =1,sticky='E')
        reference,revision,status = self.getDocInfo(project_item)
        # Reference
        row_index = row_index + 1
        self.reference_txt_pg2 = Label(self, text='Reference:', fg=foreground)
        self.reference_entry_pg2 = Entry(self, state=NORMAL,width=entry_size)
        self.reference_entry_pg2.insert(END, reference)
        self.reference_txt_pg2.grid(row =row_index,sticky='E')
        self.reference_entry_pg2.grid(row = row_index, column =1,sticky='E')
        # Revision
        row_index = row_index + 1
        self.revision_txt_pg2 = Label(self, text='Issue:', fg=foreground)
        self.revision_entry_pg2 = Entry(self, state=NORMAL,width=entry_size)
        self.revision_entry_pg2.insert(END, revision)
        self.revision_txt_pg2.grid(row =row_index,sticky='E')
        self.revision_entry_pg2.grid(row =row_index, column =1,sticky='E')
        # Status
        row_index = row_index + 1
        self.status_txt = Label(self, text='Status:', fg=foreground)
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
        page.bind('<MouseWheel>', self.log_scrollEvent)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.modif_log_label = Label(modif_log_frame, text='Modifications log:',fg=foreground)
        self.modif_log_label.pack(fill=X);
        self.modif_log = Text(modif_log_frame,wrap=WORD, yscrollcommand=scrollbar.set, width = 100, height = 10)
        self.modif_log.pack()
        scrollbar.config(command=self.modif_log.yview)
        self.modif_log.insert(END, modification_log_text)

    def _build_ccb_folder(self,page,**kwargs):
        '''
        Create folder for change requests
        '''
        global entry_size
        global project_item
        self.item = project_item
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, page, width=768, height=576,relief =GROOVE, **kwargs)
        self.pack(fill=BOTH)
        self.ccb_left = Frame(self)
        self.ccb_left.pack(side=LEFT)
        type_frame =Frame(self.ccb_left)
        type_frame.grid(row =1,column =1, sticky='W')
        row_index = 1
        self.ccb_type_txt = Label(type_frame, text='CR type:', fg=foreground)
        self.ccb_var_type = StringVar()
        self.radiobutton_ex = Radiobutton(type_frame, indicatoron=0,width = 8,text="Customer", variable=self.ccb_var_type,value="EXCR",fg=foreground,command=self.excr_type)
        self.radiobutton_sys = Radiobutton(type_frame, indicatoron=0,width = 8,text="System", variable=self.ccb_var_type,value="SyCR",fg=foreground,command=self.ccb_type)
        self.radiobutton_eqpt = Radiobutton(type_frame, indicatoron=0,width = 8,text="Eqpt", variable=self.ccb_var_type,value="ECR",fg=foreground,command=self.ccb_type)
        self.radiobutton_board = Radiobutton(type_frame, indicatoron=0,width = 8,text="Board", variable=self.ccb_var_type,value="SACR",fg=foreground,command=self.ccb_type)
        self.radiobutton_hw = Radiobutton(type_frame, indicatoron=0,width = 8,text="Hardware", variable=self.ccb_var_type,value="HCR",fg=foreground,command=self.ccb_type)
        self.radiobutton_pld = Radiobutton(type_frame, indicatoron=0,width = 8,text="PLD", variable=self.ccb_var_type,value="PLDCR",fg=foreground,command=self.ccb_type)
        self.radiobutton_sw = Radiobutton(type_frame, indicatoron=0,width = 8,text="Software", variable=self.ccb_var_type,value="SCR",fg=foreground,command=self.ccb_type)
        self.radiobutton_all = Radiobutton(type_frame, indicatoron=0,width = 8,text="All", variable=self.ccb_var_type,value="ALL",fg=foreground,command=self.ccb_type)
        self.ccb_var_type.set("PLDCR") # initialize
        self.ccb_type_txt.grid(row =row_index,sticky='E')
        self.radiobutton_ex.grid(row =row_index, column =1, padx=10,sticky='W')
        self.radiobutton_sys.grid(row =row_index, column =1, padx=75,sticky='W')
        self.radiobutton_eqpt.grid(row =row_index, column =1, padx=140,sticky='W')
        self.radiobutton_board.grid(row =row_index, column =1, padx=75,sticky='E')
        row_index = row_index + 1
        self.radiobutton_hw.grid(row =row_index, column =1, padx=10,sticky='W')
        self.radiobutton_pld.grid(row =row_index, column =1, padx=75,sticky='W')
        self.radiobutton_sw.grid(row =row_index, column =1, padx=140,sticky='W')
        self.radiobutton_all.grid(row =row_index, column =1, padx=75,sticky='E')
        context_frame =Frame(self.ccb_left)
        context_frame.grid(row =2,column =1, sticky='W')
        row_index = row_index + 1
        # Description of the selected project
        self.project_description_pg_ccb = Label(context_frame, text="Project:",fg=foreground)
        self.project_description_pg_ccb.grid(row =row_index,sticky='E')
        self.project_description_entry_pg_ccb = Entry(context_frame,width=entry_size)
        self.project_description_entry_pg_ccb.grid(row =row_index,column =1,sticky='E')
        # Author
        row_index += 1
        self.author_txt_pg_ccb = Label(context_frame, text='Author:', fg=foreground)
        self.author_txt_pg_ccb.grid(row =row_index,sticky='E')
        self.author_entry_pg_ccb = Entry(context_frame, state=NORMAL,width=entry_size)
        self.author_entry_pg_ccb.insert(END, self.author)
        self.author_entry_pg_ccb.grid(row = row_index, column =1,sticky='E')
        reference = ""
        revision = ""
        status = ""
        # Reference
        row_index += 1
        self.reference_txt_ccb = Label(context_frame, text='Reference:', fg=foreground)
        self.reference_entry_ccb = Entry(context_frame, state=NORMAL,width=entry_size)
        self.reference_entry_ccb.insert(END, reference)
        self.reference_txt_ccb.grid(row =row_index,sticky='E')
        self.reference_entry_ccb.grid(row = row_index, column =1,sticky='E')
        # Revision
        row_index += 1
        self.revision_txt_ccb = Label(context_frame, text='Issue:', fg=foreground)
        self.revision_entry_ccb = Entry(context_frame, state=NORMAL,width=entry_size)
        self.revision_entry_ccb.insert(END, revision)
        self.revision_txt_ccb.grid(row =row_index,sticky='E')
        self.revision_entry_ccb.grid(row =row_index, column =1,sticky='E')
        # Status
        row_index += 1
        self.status_txt = Label(context_frame, text='Status:', fg=foreground)
        self.status_entry = Entry(context_frame, state=NORMAL,width=entry_size)
        self.status_entry.insert(END, status)
        self.status_txt.grid(row =row_index,sticky='E')
        self.status_entry.grid(row =row_index, column =1,sticky='E')
        # Build
        row_index += 1
        button_select_ccb = Button(context_frame, text='Build CCB minutes', state=NORMAL, command = self.click_build_ccb)
        button_select_ccb.grid(row =row_index, column =1,pady=5,sticky='E')
        # Add an action
        button_add_action_ccb = Button(context_frame, text='Add action item', state=NORMAL, command = self.click_update_action_item)
        button_add_action_ccb.grid(row =row_index, column =1,pady=5,padx=50,sticky='W')
        row_index += 1
        button_edit_action_ccb = Button(context_frame, text='List action items', state=NORMAL, command = self.click_list_action_item)
        button_edit_action_ccb.grid(row =row_index, column =1,pady=5,padx=50,sticky='W')
        # right panel
        self.ccb_right = Frame(self)
        row_index = 2
        self.ccb_right.pack(side=LEFT)
        self.status_in_analysis = IntVar()
        self.status_in_review = IntVar()
        self.status_under_modif = IntVar()
        self.status_under_verif = IntVar()
        self.status_fixed = IntVar()
        self.status_closed = IntVar()
        self.status_postponed = IntVar()
        self.status_compl_analysis = IntVar()
        self.status_canceled = IntVar()
        self.status_rejected = IntVar()
        self.status_all = IntVar()
        state_frame = LabelFrame(self.ccb_right,text='Change requests state:')
        state_frame.grid(row =row_index,column =2, padx=10,sticky='W')
        self.check_button_status_in_analysis = Checkbutton(state_frame, text="In analysis", variable=self.status_in_analysis,fg=foreground)
        self.check_button_status_in_review = Checkbutton(state_frame, text="In review", variable=self.status_in_review,fg=foreground)
        self.check_button_status_under_modif = Checkbutton(state_frame, text="Under modification", variable=self.status_under_modif,fg=foreground)
        self.check_button_status_under_verif = Checkbutton(state_frame, text="Under verification", variable=self.status_under_verif,fg=foreground)
        self.check_button_status_fixed = Checkbutton(state_frame, text="Fixed", variable=self.status_fixed,fg=foreground)
        self.check_button_status_closed = Checkbutton(state_frame, text="Closed", variable=self.status_closed,fg=foreground)
        self.check_button_status_postponed = Checkbutton(state_frame, text="Postponed", variable=self.status_postponed,fg=foreground)
        self.check_button_status_compl_analysis = Checkbutton(state_frame, text="Complementary analysis", variable=self.status_compl_analysis,fg=foreground)
        self.check_button_status_canceled = Checkbutton(state_frame, text="Canceled", variable=self.status_canceled,fg=foreground)
        self.check_button_status_rejected = Checkbutton(state_frame, text="Rejected", variable=self.status_rejected,fg=foreground)
        self.check_button_status_all = Checkbutton(state_frame, text="All", variable=self.status_all,fg=foreground,command = self.click_status_all)
        self.check_button_status_in_analysis.grid(row =row_index+1, column =2, padx=10,sticky='W')
        self.check_button_status_in_review.grid(row =row_index+2, column =2, padx=10,sticky='W')
        self.check_button_status_under_modif.grid(row =row_index+3, column =2, padx=10,sticky='W')
        self.check_button_status_under_verif.grid(row =row_index+4, column =2, padx=10,sticky='W')
        self.check_button_status_fixed.grid(row =row_index+5, column =2, padx=10,sticky='W')
        self.check_button_status_closed.grid(row =row_index+6, column =2, padx=10,sticky='W')
        self.check_button_status_all.grid(row =row_index+7, column =2, padx=10,sticky='W')
        self.check_button_status_compl_analysis.grid(row =row_index+1, column =3, padx=10,sticky='W')
        self.check_button_status_postponed.grid(row =row_index+2, column =3, padx=10,sticky='W')
        self.check_button_status_rejected.grid(row =row_index+6, column =3, padx=10,sticky='W')
        self.check_button_status_canceled.grid(row =row_index+5, column =3, padx=10,sticky='W')
        self.ccb_type()
        # Attributes panel
        ccb_attributes = Frame(self)
        ccb_attributes.pack()
        # Attributes set
        row_index += 1
        if (0==1):
            self.atributes_txt = Label(ccb_attributes, text='Attribute set:', fg=foreground,width=40,anchor=W,padx=20)
            self.atributes_txt.grid(row = row_index, sticky='E')
            row_index += 1
            self.attributes_set_frame = Frame(ccb_attributes, bg = '#80c0c0')
            self.attributes_set_frame.grid(row = row_index, padx=30,sticky='W')
            self.vbar_attributes_set = vbar_attributes_set = Scrollbar(self.attributes_set_frame , name="vbar_attributes_set")
            self.vbar_attributes_set.pack(side=RIGHT, fill=Y)
            self.attributes_set_box = Listbox(self.attributes_set_frame ,height=3,width=30,exportselection=0,yscrollcommand=vbar_attributes_set.set)
            self.attributes_set_box.pack()
            vbar_attributes_set["command"] = self.attributes_set_box.yview
            self.attributes_set_box.bind("<ButtonRelease-1>", self.select_attribute)
            list_attributes = ["Default","Detected on","Implemented for","Applicable Since","None"]
            for line_attribute in list_attributes:
                self.attributes_set_box.insert(END, line_attribute)
            self.attributes_set_box.selection_set(first=0)
        # Previous release
        row_index += 1
        self.previous_release_txt = Label(ccb_attributes, text='Detected on release:', fg=foreground,width=40,anchor=W,padx=20)
        self.previous_release_entry = Entry(ccb_attributes, state=NORMAL,width=entry_size)
        self.previous_release_entry.insert(END, self.previous_release)
        self.previous_release_entry.bind("<Return>", self._setPreviousRelease)
##        self.previous_release_entry.bind("<FocusOut>", self._setPreviousRelease)
##        self.previous_release_entry.bind("<Leave>", self._setPreviousRelease)
        self.previous_release_txt.grid(row =row_index,sticky='E')
        row_index += 1
        self.previous_release_entry.grid(row =row_index,sticky='E')
        # Implemented for release
        row_index += 1
        impl_release_txt = Label(ccb_attributes, text='Implemented for release:', fg=foreground,width=40,anchor=W,padx=20)
        self.impl_release_entry = Entry(ccb_attributes, state=NORMAL,width=entry_size)
        self.impl_release_entry.insert(END, self.impl_release)
        self.impl_release_entry.bind("<Return>", self._setImplRelease)
##        self.impl_release_entry.bind("<FocusOut>", self._setImplRelease)
##        self.impl_release_entry.bind("<Leave>", self._setImplRelease)
        impl_release_txt.grid(row =row_index,sticky='E')
        row_index += 1
        self.impl_release_entry.grid(row =row_index,sticky='E')
        # CR type
        row_index += 1
        cr_type_txt = Label(ccb_attributes, text='CR type:', fg=foreground,width=40,anchor=W,padx=20)
        self.cr_type_entry = Entry(ccb_attributes, width=entry_size,state=NORMAL)
        self.cr_type_entry.insert(END, self.cr_type)
        self.cr_type_entry.bind("<Return>", self._setCRType)
##        self.cr_type_entry.bind("<FocusOut>", self._setCRType)
##        self.cr_type_entry.bind("<Leave>", self._setCRType)
        cr_type_txt.grid(row =row_index,sticky='E')
        row_index += 1
        self.cr_type_entry.grid(row =row_index,sticky='E')
        #
        # Button List CR
        #
        self.button_get_cr = Button(ccb_attributes, text='List CR', state=NORMAL, command = self.click_get_cr)
        self.button_clear_cr = Button(ccb_attributes, text='Clear', state=NORMAL, command = self.click_clean_cr)
        self.button_set = Button(ccb_attributes, text='Set', command = self.click_set_cr)

        # Checkbuttons
        self.log_on_var = IntVar()
        self.cr_for_review_var = IntVar()
        self.cr_with_parent = IntVar()
        self.with_tasks_var = IntVar()
        self.button_cr_for_review =  Checkbutton(ccb_attributes, text="Export CR for review report", variable=self.cr_for_review_var,fg=foreground,command=self.cb_cr_for_review)
        self.button_log_on = Checkbutton(ccb_attributes, text="Log on", variable=self.log_on_var,fg=foreground,command=self.cb_log_on)
        self.button_with_tasks = Checkbutton(ccb_attributes, text="With tasks", variable=self.with_tasks_var,fg=foreground,command=self.cb_with_tasks)
        self.button_cr_with_parent = Checkbutton(ccb_attributes, text="With parent CR", variable=self.cr_with_parent,fg=foreground,command=self.cb_with_parent_cr)
        row_index += 1
        self.button_clear_cr.grid(row =row_index,sticky='E')
        self.button_set.grid(row =row_index,pady=5,padx=40,sticky='E')
        row_index += 3
        self.button_log_on.grid(row =row_index,sticky='W')
##        self.button_with_tasks.grid(row =row_index,sticky='E')
        row_index += 1
        self.button_cr_for_review.grid(row =row_index,sticky='W')
        self.button_cr_with_parent.grid(row =row_index,sticky='E')
        row_index += 3
        self.button_get_cr.grid(row =row_index,sticky='E')
        row_index += 1
        list_cr_frame = LabelFrame(ccb_attributes,text="Change Requests found",bd=0)
        list_cr_frame.grid(row =row_index,sticky='E')
        sub_list_cr_frame = Frame(list_cr_frame)
        sub_list_cr_frame.pack()
        # crlistbox is updated thanks to RELOAD_CRLISTBOX keyword
        self.crlistbox = Listbox(sub_list_cr_frame,height=5,width=64,exportselection=0,state=DISABLED,bg="gray",selectmode=EXTENDED)
        self.crlistbox.insert(END, "All")
        self.vbar_crlisbox = vbar_crlisbox = Scrollbar(sub_list_cr_frame, name="vbar_crlisbox")
        self.vbar_crlisbox.pack(side=RIGHT, fill=Y)
        vbar_crlisbox["command"] = self.crlistbox.yview
        self.crlistbox["yscrollcommand"] = vbar_crlisbox.set
        self.crlistbox.bind("<ButtonRelease-1>", self.select_cr_list)
        self.crlistbox.bind("<MouseWheel>", self.crlistbox_scrollEvent)
##        self.crlistbox.bind("<<ListboxSelect>>", self.crlistbox_onselect)
        self.crlistbox.bind("<Double-Button-1>", self.crlistbox_onselect)
        self.crlistbox.bind("<Key-Up>", lambda event, arg=self.crlistbox: self.up_event(event, arg))
        self.crlistbox.bind("<Key-Down>", lambda event, arg=self.crlistbox: self.down_event(event, arg))
        self.crlistbox.pack()
    def crlistbox_scrollEvent(self,event):
        if event.delta >0:
            self.crlistbox.yview_scroll(-2,'units')
        else:
            self.crlistbox.yview_scroll(2,'units')

    def crlistbox_onselect(self,event):
        import webbrowser
        # Note here that Tkinter passes an event object to onselect()
        w = event.widget
        print "WIDGET:",w
        cr_index = self.crlistbox.curselection()[0]
        if cr_index != ():
            cr = self.crlistbox.get(cr_index)
            print cr
            m = re.match(r'^([0-9]{1,4})\) (.*)$',cr)
            if m:
                cr_id = m.group(1)
            else:
                cr_id = "None"
        print 'You selected CR %s: "%s"' % (cr_id, cr)
##        webbrowser.open("http://spar-syner1.in.com:8600/change/framesetLoader.do?frameName=panelAndDialog&temp_token=792414148515128161")
        self.queue.put("EXPORT_CR")
        self.queue.put(cr_id)

    def select_cr_list(self,event):
        pass

    def select_review_list(self,event):
        pass

    def reviewlistbox_scrollEvent(self,event):
        if event.delta >0:
            self.reviewlistbox.yview_scroll(-2,'units')
        else:
            self.reviewlistbox.yview_scroll(2,'units')

    def reviewlistbox_onselect(self,event):
        # Note here that Tkinter passes an event object to onselect()
        w = event.widget
        print "WIDGET:",w
        review_index = self.reviewlistbox.curselection()
        print"review_index",review_index
        if review_index != () and review_index[0] != ():
            review = self.reviewlistbox.get(review_index)
            print review
            m = re.match(r'^([0-9]{1,4})\) (.*)$',review)
            if m:
                review_id = m.group(1)
            else:
                review_id = "None"
            print 'You selected review %s: "%s"' % (review_id, review)
            self.review_qams_id = review_id
            self.review_qams_id_entry.delete(0,END)
            self.review_qams_id_entry.insert(END, review_id)
##        webbrowser.open("http://spar-syner1.in.com:8600/change/framesetLoader.do?frameName=panelAndDialog&temp_token=792414148515128161")

    def press_read_session_status(self,event):
        ''' Read status of synergy session
            CTRL + T '''
        self.queue.put("READ_STATUS") # order to read session status
    def press_close_session(self,event):
        ''' Close synergy session
            CTRL + W '''
        self.queue.put("CLOSE_SESSION") # order to read session status
    def press_ctrl_s(self,event):
        ''' Read items and give scope
            CTRL + S '''
        self.queue.put("SCOPE")
        self.queue.put(self.release)
        self.queue.put(self.project)
        self.queue.put(self.baseline)
    def press_start_apache(self,event):
        ''' Launch apache session
            CTRL + H '''
        self.queue.put("START_APACHE")
        config= "httpd_ece.conf"
        self.apache_start(config)
        pass
    def cid_type(self):
##        print "CID type is '{:s}'".format(self.cid_var_type.get())
        if self.cid_var_type.get() == "HCMR":
            if self.hcmr_var_type.get() == "HCMR_PLD":
                self.ccb_var_type.set("PLDCR")
            elif self.hcmr_var_type.get() == "HCMR_BOARD":
                self.ccb_var_type.set("HCR")
            print "HCMR type is '{:s}'".format(self.hcmr_var_type.get())
            self.radiobutton_hci_pld.grid(row =2, column =1, padx=10,sticky='W')
            self.radiobutton_hci_board.grid(row =2, column =1, padx=10,sticky='E')
        else:
            if self.cid_var_type.get() == "SCI":
                self.ccb_var_type.set("SCR")
            self.radiobutton_hci_pld.grid_forget()
            self.radiobutton_hci_board.grid_forget()
    def excr_type(self):
        # Customize EXCR workflow
        self.check_button_status_in_analysis.configure(text="Entered")
        self.check_button_status_under_modif.configure(text="In progress")
        self.check_button_status_fixed.configure(text="Implemented")
        self.check_button_status_postponed.configure(text="Workaround")
        self.check_button_status_compl_analysis.grid_forget()
        self.check_button_status_in_review.grid_forget()
        self.check_button_status_under_verif.grid_forget()
        self.check_button_status_canceled.grid_forget()
        self.cr_activate_all_button()
    def cr_activate_all_button(self):
            self.check_button_status_in_analysis.config(state=NORMAL)
            self.check_button_status_compl_analysis.config(state=NORMAL)
            self.check_button_status_in_review.config(state=NORMAL)
            self.check_button_status_postponed.config(state=NORMAL)
            self.check_button_status_under_modif.config(state=NORMAL)
            self.check_button_status_under_verif.config(state=NORMAL)
            self.check_button_status_fixed.config(state=NORMAL)
            self.check_button_status_closed.config(state=NORMAL)
            self.check_button_status_canceled.config(state=NORMAL)
            self.check_button_status_rejected.config(state=NORMAL)
            self.check_button_status_all.config(state=NORMAL)
    def cr_deactivate_all_button(self):
            self.check_button_status_in_analysis.config(state=DISABLED)
            self.check_button_status_compl_analysis.config(state=DISABLED)
            self.check_button_status_in_review.config(state=DISABLED)
            self.check_button_status_postponed.config(state=DISABLED)
            self.check_button_status_under_modif.config(state=DISABLED)
            self.check_button_status_under_verif.config(state=DISABLED)
            self.check_button_status_fixed.config(state=DISABLED)
            self.check_button_status_closed.config(state=DISABLED)
            self.check_button_status_canceled.config(state=DISABLED)
            self.check_button_status_rejected.config(state=DISABLED)
            self.check_button_status_all.config(state=DISABLED)
    def ccb_type(self):
        # Set [X]CR workflow
        row_index = 2
        old_workflow = self.status_old_workflow.get()
        if old_workflow == 1:
            # Old workflow requested
            self.check_button_status_in_analysis.configure(text="entered")
            self.check_button_status_under_modif.configure(text="assigned")
            self.check_button_status_fixed.configure(text="resolved")
            self.check_button_status_postponed.configure(text="postponed")
        else:
            self.check_button_status_in_analysis.configure(text="In analysis")
            self.check_button_status_under_modif.configure(text="Under modification")
            self.check_button_status_fixed.configure(text="Fixed")
            self.check_button_status_postponed.configure(text="Postponed")
        self.check_button_status_compl_analysis.grid(row =row_index+1, column =3, padx=10,sticky='W')
        self.check_button_status_in_review.grid(row =row_index+2, column =2, padx=10,sticky='W')
        self.check_button_status_under_verif.grid(row =row_index+4, column =2, padx=10,sticky='W')
        self.check_button_status_canceled.grid(row =row_index+5, column =3, padx=10,sticky='W')
##        print "CCB type is '{:s}'".format(self.ccb_var_type.get())
        if self.ccb_var_type.get() == "ALL":
            self.check_button_status_in_analysis.deselect()
            self.check_button_status_compl_analysis.deselect()
            self.check_button_status_in_review.deselect()
            self.check_button_status_postponed.deselect()
            self.check_button_status_under_modif.deselect()
            self.check_button_status_under_verif.deselect()
            self.check_button_status_fixed.deselect()
            self.check_button_status_closed.deselect()
            self.check_button_status_canceled.deselect()
            self.check_button_status_rejected.deselect()
            self.check_button_status_all.deselect()
            self.cr_deactivate_all_button()
            self.checkbutton_all = False
        else:
            self.check_button_status_in_analysis.select()
            self.check_button_status_compl_analysis.select()
            self.check_button_status_in_review.select()
            self.check_button_status_postponed.select()
            self.check_button_status_under_modif.select()
            self.check_button_status_under_verif.select()
            self.check_button_status_fixed.select()
            self.check_button_status_closed.select()
            self.check_button_status_canceled.select()
            self.check_button_status_rejected.select()
            self.check_button_status_all.select()
            self.cr_activate_all_button()
            self.checkbutton_all = True
    def cb_released(self):
        print "variable 'Released' is", self.status_released.get()
    def cb_active_release(self):
        print "variable 'Active released' is", self.status_old_workflow.get()
    def cb_log_on(self):
        print "variable 'Log on' is", self.log_on_var.get()
    def cb_with_tasks(self):
        print "variable 'With tasks' is", self.with_tasks_var.get()
    def cb_with_parent_cr(self):
        print "variable 'With parent CR' is", self.cr_with_parent.get()
    def cb_cr_for_review(self):
        print "variable 'Export CR for review' is", self.cr_for_review_var.get()
    def cb_integrate(self):
        print "variable 'Intergrate' is", self.status_integrate.get()
    def cb_old_workflow(self):
        old_workflow = self.status_old_workflow.get()
        if old_workflow == 1:
            # Old workflow requested
            self.check_button_status_in_analysis.configure(text="entered")
            self.check_button_status_under_modif.configure(text="assigned")
            self.check_button_status_fixed.configure(text="resolved")
            self.check_button_status_postponed.configure(text="postponed")
            self.check_button_status_closed.configure(text="concluded")
        else:
            # New workflow requested
            self.check_button_status_in_analysis.configure(text="In analysis")
            self.check_button_status_under_modif.configure(text="Under modification")
            self.check_button_status_fixed.configure(text="Fixed")
            self.check_button_status_postponed.configure(text="Postponed")
            self.check_button_status_closed.configure(text="Closed")
        print "variable 'Old CR workflow' is", old_workflow
    def click_status_all(self):
        print self.checkbutton_all
        if self.checkbutton_all == False:
            # checkbutton 'All' is selected
            self.check_button_status_in_analysis.select()
            self.check_button_status_postponed.select()
            self.check_button_status_under_modif.select()
            self.check_button_status_fixed.select()
            self.check_button_status_closed.select()
            self.check_button_status_rejected.select()
            if self.ccb_var_type.get() != "EXCR":
                self.check_button_status_canceled.select()
                self.check_button_status_under_verif.select()
                self.check_button_status_compl_analysis.select()
                self.check_button_status_in_review.select()
            else:
                self.check_button_status_canceled.deselect()
                self.check_button_status_under_verif.deselect()
                self.check_button_status_compl_analysis.deselect()
                self.check_button_status_in_review.deselect()
            self.checkbutton_all = True
            print "Select all"
        else:
            self.check_button_status_in_analysis.deselect()
            self.check_button_status_compl_analysis.deselect()
            self.check_button_status_in_review.deselect()
            self.check_button_status_postponed.deselect()
            self.check_button_status_under_modif.deselect()
            self.check_button_status_under_verif.deselect()
            self.check_button_status_fixed.deselect()
            self.check_button_status_closed.deselect()
            self.check_button_status_canceled.deselect()
            self.check_button_status_rejected.deselect()
            self.checkbutton_all = False
            print "Deselect all"
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
    def select_attribute(self, event):
        index = self.attributes_set_box.curselection()
        if index in (0,()):
            self.attribute = ""
        else:
            self.attribute = interface.attributes_set_box.get(index)
        self.log("Selected CR filter attribute: " + self.attribute,False)
    def select_item(self, event):
        item_id = self.itemslistbox.curselection()
        self.item_id = item_id
        if item_id != () and '0' not in item_id:
            self.item = self.itemslistbox.get(item_id)
            description = self.getItemDescription(self.item)
            cr_type = self._getItemCRType(self.item,self.system)
            self.cr_type = cr_type
            self.cr_type_entry.delete(0, END)
            self.cr_type_entry.insert(END, cr_type)
            self.ccb_var_type.set("SACR")
            self.log("Selected item: " + self.item + ": " + description)
            self.log("Selected CR type: " + self.cr_type)
            # Re populate components_listbox
            self.component = self.populate_components_listbox_wo_select(self.componentslistbox,self.item,self.system)
        else:
            self.log("No specific item selected")
            self.component = self.populate_components_listbox_wo_select(self.componentslistbox,"",self.system)
        self.defill()
    def select_component(self, event):
        ''' select component'''
        component_id = self.componentslistbox.curselection()
        if component_id != () and '0' not in component_id:
            self.component = self.componentslistbox.get(component_id)
            description = self.getComponentDescription(self.component)
            cr_type = self._getComponentCRType(self.component)
            self.cr_type = cr_type
            self.cr_type_entry.delete(0, END)
            self.cr_type_entry.insert(END, cr_type)
            m = re.match("^(SW|PLD)_(.*)",cr_type)
            if m:
                if m.group(1) == "SW":
                    self.radiobutton_hci_pld.grid_forget()
                    self.radiobutton_hci_board.grid_forget()
                    self.ccb_var_type.set("SCR")
                    self.cid_var_type.set("SCI")
                elif m.group(1) == "PLD":
                    self.radiobutton_hci_pld.grid(row =2, column =1, padx=10,sticky='W')
                    self.radiobutton_hci_board.grid(row =2, column =1, padx=10,sticky='E')
                    self.ccb_var_type.set("PLDCR")
                    self.cid_var_type.set("HCMR")
                    self.hcmr_var_type.set("HCMR_PLD")
            self.log("Selected component: " + self.component + ": " + description)
            self.log("Selected CR type: " + self.cr_type)
        else:
            self.log("No specific component selected")
        self.defill()
    def double_click_system(self, event):
        pass
    def list_items(self):
        self.queue.put("LIST_ITEMS") # action to get items according to release or project
        self.queue.put(self.release)
        self.queue.put(self.project)
        self.queue.put(self.baseline)
    def _find_release_vs_baseline(self):
        self.queue.put("GET_RELEASE_VS_BASELINE") # action to get projects
        self.queue.put((self.baseline))
    def select_baseline_prev(self, event):
        index = self.baselinelistbox_1.curselection()
        if index in (0,()):
            baseline = ""
        else:
            baseline = self.baselinelistbox_1.get(index)
            self.button_make_diff.configure(state=NORMAL)
        self.baseline_prev = baseline
    def select_baseline_cur(self, event):
        index = self.baselinelistbox_2.curselection()
        if index in (0,()):
            baseline = ""
        else:
            baseline = self.baselinelistbox_2.get(index)
            self.button_show_baseline.configure(state=NORMAL)
            self.setBaselineSynergy(baseline)
        self.baseline_cur = baseline

    def log(self,text="",display_gui=True):
        '''
        Log messages
        '''
        self.loginfo.info(text)
##        print time.strftime("%H:%M:%S", time.localtime()) + " " + text
        if display_gui:
            self.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) + " " + text + "\n")
    def defill(self):
        self.general_output_txt.see(END)
    def logrun(self,text,display_gui=True):
        '''
        Log messages
        '''
        self.loginfo.info(text)
        if display_gui:
            self.general_output_txt.insert(END, time.strftime("%H:%M:%S", time.localtime()) + " " + text)
    def __find_partnumber(self):
        # Display part numbers
        if self.standard != "":
            if self.dico_list_pn != {}:
                self.pnlistbox.delete(0, END)
                if self.standard != "All":
                    print self.standard
                    print "TEST2"
                    self.pnlistbox.insert(END, "All")
                    if self.dico_std_vs_pn.has_key(self.standard):
                        print "TEST3"
                        if self.dico_list_stdac_vs_pn.has_key(self.standard):
                            self.current_list_partnumber = self.dico_list_stdac_vs_pn[self.standard]
                        else:
                            self.current_list_partnumber = self.dico_std_vs_pn[self.standard]
##                        print self.current_list_partnumber
                        for pn in self.current_list_partnumber:
                            self.pnlistbox.insert(END, pn)
                else:
                    self.current_list_partnumber = self.dico_list_pn.keys()
                    self.display_partnumber()
                self.find_releases()
                self.pnlistbox.configure(bg="white")
                self.pnlistbox.selection_set(first=0)
    def getBaseline(self):
        '''
        Get baseline which may be:
            - A standard
            - A Part Number
            - A Synergy release
        '''
        return(self.baseline_change)
    def select_standard(self, event):
        '''
        Select standard
        Find related Part number
        Display baseline to applied for Change query
        '''
        index = self.stdlistbox.curselection()
        if index in (0,()):
            self.standard = ""
            self.partnumber = ""
            self.log("All standards selected")
        else:
            self.standard = self.stdlistbox.get(index)
            self.partnumber = "All"
            if self.standard == "All":
                self.log("All standards selected")
            else:
                self.log("Standard selected: " + self.standard)
        self.general_output_txt.see(END)
        self.__find_partnumber()
        self.setBaseline(self.standard)
    def select_partnumber(self, event):
        '''
        Select part number
        Find related Synergy release
        Display baseline to applied for Change query
        '''
        index = self.pnlistbox.curselection()
        if index == 0 or index == ():
            self.partnumber = ""
            self.log("All Part Numbers selected")
        else:
            self.partnumber = self.pnlistbox.get(index)
            if self.partnumber == "All":
                self.log("All Part Numbers selected")
            else:
                self.log("Part Number selected: " + self.partnumber)
        self.general_output_txt.see(END)
        self.find_releases()
        self.setBaseline(self.partnumber)
    def make_menu(self):
        menu = Menu(self.listbox, tearoff=0)
        self.menu = menu
        self.fill_menu()
    def log_scrollEvent(self,event):
##        print event.delta
        if event.delta >0:
##            print 'déplacement vers le haut'
            self.general_output_txt.yview_scroll(-2,'units')
        else:
##            print 'déplacement vers le bas'
            self.general_output_txt.yview_scroll(2,'units')
    def log_upEvent(self, event):
##        print event.delta
##        print 'déplacement vers le haut'
        self.general_output_txt.yview_scroll(-2,'units')
    def log_downEvent(self, event):
##        print event.delta
##        print 'déplacement vers le bas'
        self.general_output_txt.yview_scroll(2,'units')
    def click_clear(self):
        self.general_output_txt.delete(0.0, END)
    def click_quit(self):
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit now?"):
            if isinstance(thread_build_docx,ThreadQuery):
                thread_build_docx.stopSession()
##                if self.item != "":
##                    context = self.item
##                else:
                context = self.system
                thread_build_docx.storeSelection(self.project,context,self.release,self.baseline)
##            else:
##            self.storeSelection(self.project,thread_build_docx.item,self.release,self.baseline)
##            if queue.empty():
##                print "QUEUE EMPTY"
##            else:
##                print "QUEUE NOT EMPTY"
##            queue.join()
            self.destroy()
            fenetre.destroy()
    def click_logout(self):
        if tkMessageBox.askokcancel("Log out", "Do you really want to log out?"):
            thread_build_docx.stopSession()
            thread_build_docx.storeSelection(self.project,thread_build_docx.system,self.release,self.baseline)
            self.destroy()
            fenetre.destroy()
    def click_cancel_build_cid(self):
        global cancel_build
        cancel_build = True
        print "Abort CID generation."
    def getCIDType(self):
        cid_type = self.cid_var_type.get()
        if cid_type == "HCMR":
            if self.hcmr_var_type.get() == "HCMR_PLD":
                cid_type = "HCMR_PLD"
            elif self.hcmr_var_type.get() == "HCMR_BOARD":
                cid_type = "HCMR_BOARD"
        return cid_type
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
        part_number = self.part_number_entry.get()
        board_part_number = self.board_part_number_entry.get()
        checksum = self.checksum_entry.get()
        dal = self.dal_entry.get()
        previous_release = self.previous_release_entry.get()
        revision = self.revision_entry.get()
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
        self.queue.put([author,
                        reference,
                        revision,
                        release,
                        project,
                        baseline,
                        self.status_released.get(),
                        self.status_integrate.get(),
                        self.getCIDType(),
                        self.item,
                        part_number,
                        checksum,
                        dal,
                        board_part_number,
                        previous_release])
    def click_make_baseline_diff(self):
        self.queue.put("MAKE_DIFF") # order to make diff
        self.queue.put([self.baseline_prev,self.baseline_cur])
    def click_show_baseline(self):
        self.queue.put("SHOW_BASELINE") # order to make diff
        self.queue.put([self.baseline_cur])
    def click_list_tasks(self):
        '''
         Order to list tasks in the release or baseline
        '''
        self.queue.put("LIST_TASKS")
        self.queue.put(self.release)
        self.queue.put(self.baseline)
    def click_list_history(self):
        '''
         Order to list history in the release or baseline
        '''
        self.queue.put("LIST_HISTORY")
        self.queue.put(self.release)
        self.queue.put(self.baseline)
        self.queue.put(self.project)
    def click_send_cmd(self):
        '''
        Function which put SEND_CMD in the queue
        to execute Synergy CLI command written in
        the Synergy command text area
        '''
        self.queue.put("SEND_CMD") # order to send synergy CLI
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
    def click_build_ccb(self):
        '''
        Function which put
        - author
        - reference
        - revision
        - release
        - baseline
        - project
        - cr type
        into the queue
        called when the user press the Build button
        '''
        # Get author
        author = self.author
        # Get reference
        reference = self.reference_entry_ccb.get()
        if reference == "":
            reference = "TBD"
        # Get revision
        revision = self.revision_entry_ccb.get()
        if revision == "":
            revision = "TBD"
        self.queue.put("BUILD_CCB") # order to build docx
        self.queue.put([author,reference,revision,self.release,self.baseline,self.project,self.ccb_var_type.get(),self.previous_release,self.impl_release])
    def click_get_cr(self):
        '''
        Function which put
        - GET_CR command
        - baseline
        - cr type
        into the queue
        called when the user press the "List CR" button in folder "Change Requests query"
        '''
        self.queue.put("GET_CR") # order to get CR
        self.queue.put([self.getBaseline(),self.ccb_var_type.get()])
    def click_clean_cr(self):
        self.previous_release_entry.delete(0,END)
        self.impl_release_entry.delete(0,END)
        self.cr_type_entry.delete(0, END)
        self.previous_release = ""
        self.detect_cr.configure(text="")
        self.impl_release = ""
        text = "Clean CR implemented in release and CR detected in release and CR_type."
        self.impl_cr.configure(text="")
        self.target_release_entry.delete(0,END)
##        self.cr_type_entry.configure(text="")
        self.cr_type = ""
        self.log(text)
        self.defill()

    def click_set_cr(self):
        self._setPreviousRelease()
        self._setImplRelease()
        self._setCRType()

class Console(Interface,Tool):
    def getTypeWorkflow(self):
        return False
    def defill(self):
        pass
    def log(self,text,display_gui=False):
        Interface.log(self,text,False)
    def _readConfig(self):
        Interface._readConfig(self)
    def __init__(self, master,queue,system,item, **kwargs):
        global item_id
##        self.tk = master
        self.std_exists = False
        self.current_list_partnumber = []
        self.dico_std = {}
        self.checkbutton_all = False
        # read config file
        self.default_template_type = "SCI"
        self.reference = "" #"ET1234-V"
        self.revision = "" #"1D1"
        self.release = ""
        self.baseline_change = ""
        self.baseline = ""
        self.previous_baseline = ""
        self.project = ""
        # Read config
        self._readConfig()
        # Set logging
        self.loginfo = logging.getLogger(__name__)
        if self.verbose == "yes":
            out_hdlr = logging.FileHandler(filename='docid_cli.log')
        else:
            out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        out_hdlr.setLevel(logging.INFO)
        self.loginfo.addHandler(out_hdlr)
        self.loginfo.setLevel(logging.INFO)
        self.loginfo.debug("NO")
        self.system = system
        self.item = item
        self.cr_type = ""
        # Get
        #       - Database
        #       - Aircraft
        #
        if self.item != "":
            self.database,self.aircraft = self.get_sys_item_database(self.system,self.item)
            if self.database == None:
                self.database,self.aircraft = self.get_sys_database()
        else:
            self.database,self.aircraft = self.get_sys_database()
        self.standard = ""
        self.partnumber = "" # Warning, P/N managed by the listbox pnlistbox in the GUI class
##        self.board_part_number = ""
        self.item_id = item_id
        self.session_started = False
        self.queue = queue
        self.project_list = []
        self.attribute = "CR_implemented_for"
##        self.release_list = []
##        self.baseline_list = []
        self.type_cr_workflow = "None"
def destroy_app():
    global thread_build_docx
    if tkMessageBox.askokcancel("Quit", "Do you really want to quit now?"):
        thread_build_docx.stopSession()
        thread_build_docx.storeSelection(thread_build_docx.master_ihm.project,thread_build_docx.item,thread_build_docx.master_ihm.release,thread_build_docx.master_ihm.baseline)
        thread_build_docx.stop()
##        interface.destroy()
        fenetre.destroy()
if __name__ == '__main__':
    no_start_session = False
    try:
        # command line option ?
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--cli", help="launch doCID in command line input mode",action="store_true")
        parser.add_argument("-system", help="System")
        parser.add_argument("-item", help="Item")
        parser.add_argument("-release", help="Target release")
        parser.add_argument("-cr_type", help="Component selected (ex: SW_ENM etc.)")
        parser.add_argument("-baseline", nargs='?', help="Baseline selected (ex: SW_ENM_02_06 etc.)")
        args = parser.parse_args()
        if args.cli:
##            text = "Launching doCID in CLI mode"
##            sys.stdout.write(text + '\n')
##            sys.stdout.write("Implemented for: " + args.release + '\n')
##            sys.stdout.write("CR scope: " + args.cr_type + '\n')
##            sys.stdout.write("System: " + args.system + '\n')
##            sys.stdout.write("Item: " + args.item + '\n')
            # Begin DoCID in GUI mode
            no_start_session = False
            session_started = False
            project_item = ""
            system = args.system #"Dassault F5X PDS"
            item = args.item #"ESSNESS"
            item_id = 1
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
             # instance threads
            queue = Queue.Queue()
##            fenetre = Tk()
            interface = Console("",queue,system,item)
            interface.cr_type = args.cr_type
            interface.previous_release = "" # detect_release
            interface.impl_release = args.release
            interface.baseline = ""
            interface.project = ""
##            print "Instantiate ThreadQuery\n"
            thread_docid = ThreadQuery("doc",interface,queue)
            if thread_docid.launch_session:
                # Wait Synergy session begin
##                print "Wait Synergy session begin\n"
                while not session_started and not thread_docid.start_session_failed:
                    pass
                if not thread_docid.start_session_failed:
##                    print "ARG",args.baseline
                    if args.baseline != None:
                        output = thread_docid._getItems(args.release,args.baseline)
                        text  = "List of objects exported."
                        print output
##                        print "Launch Synergy get objects query\n"
                    else:
                        output = thread_docid._getCR("","SCR")
                        text  = "List of CR exported."
                        print output
##                        print "Launch Synergy get cr query\n"
                    test_log = open("test.log", "w")
                    message = text
                    test_log.write(message)
                    test_log.close()
                else:
                    print "Synergy session login failed\n"
            sys.stdout.flush();
        else:
            # Begin DoCID in GUI mode
            session_started = False
            project_item = ""
            system = "None"
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
    ##        verrou = threading.Lock()
            login_window = Tk()
    ##        gui = Gui()
            Pmw.initialise(login_window)
            login_window.iconbitmap("qams.ico")
            login_window.title("Login")
            login_window.resizable(False,False)
            # Create login interface
            interface_login = Login(login_window)
            if interface_login.auto_start:
                interface_login.click_bypass()
                login_window.destroy()
            else:
                # create a toplevel menu
                mainmenu = Menu(login_window)
                menubar = Menu(mainmenu)
    ##            menubar.add_command(label = "Help", command=gui.help)
    ##            menubar.add_separator()
    ##            menubar.add_command(label = "Quit", command=interface_login.click_quit)
    ##            mainmenu.add_cascade(label = "Home", menu = menubar)
    ##            mainmenu.add_command(label = "About", command=gui.about)
                # Bind control keys
                mainmenu.bind_all("<Control-b>", interface_login.press_bypass_start_session)
                mainmenu.bind_all("<Control-h>", interface_login.press_start_apache)
                # display the menu
                login_window.configure(menu = mainmenu)
                # infinite loop
                interface_login.mainloop()
            # Login succeeded ?
            if login_success:
        ##        sys.exit()
                fenetre = Tk()
                #
                # Tk =====> Gui
                #    =====> ThreadQuery
                #
                Pmw.initialise(fenetre)
                fenetre.iconbitmap("qams.ico")
                fenetre.title("doCID: Just create a configuration index document in one click")
                # enable height window resize
                fenetre.resizable(False,False)
                 # instance threads
                queue = Queue.Queue()
                #
                # Queue =====> Gui
                #       =====> ThreadQuery
                #
                gui = Gui(fenetre,queue,system,item)
                # gui instanciates class Interface by "interface" which is global ... not cool
                # gui creates a "notebook" with "fenetre" then
                #     creates an "interface" with "notebook"
                #
                # Gui =====> Interface
                #
                thread_build_docx = ThreadQuery("doc",gui.ihm,queue)
                # fenetre is just used here for polling processIncoming
                # See: self.master.after(1000, self.periodicCall)
                #
                # ThreadQuery <===== Interface
                #             =====> BuildDoc
                #
                # create a toplevel menu
                mainmenu = Menu(fenetre)
                menubar = Menu(mainmenu)
                menubar.add_command(label="Change Requests query", command=gui.ihm.ccb_minutes)
                menubar.add_separator()
                menubar.add_command(label="Create Plan Review minutes", command=gui.ihm.plan_review_minutes)
                menubar.add_command(label="Create Specification Review minutes", command=gui.ihm.spec_review_minutes)
                menubar.add_separator()
                menubar.add_command(label="Reload config file", command=gui.ihm.click_update_config)
                menubar.add_command(label="Reload PN csv file", command=gui.ihm.click_update_pn_csv)
                menubar.add_separator()
                menubar.add_command(label="Log out", command=gui.ihm.click_logout)
                menubar.add_separator()
                menubar.add_command(label="Quit", command=gui.ihm.click_quit)
                mainmenu.add_cascade(label="Home", menu = menubar)
                mainmenu.add_command(label="About", command=gui.about)
                mainmenu.add_command(label="Help", command=gui.help)
                # Bind control keys
                mainmenu.bind_all("<Control-s>", gui.ihm.press_ctrl_s)
                mainmenu.bind_all("<Control-t>", gui.ihm.press_read_session_status)
                mainmenu.bind_all("<Control-w>", gui.ihm.press_close_session)
                mainmenu.bind_all("<Control-h>", gui.ihm.press_start_apache)
                # display the menu
                fenetre.configure(menu = mainmenu)
                # --------------------------
                # to bind the window manager's CLOSE event to a fn
                # --------------------------
                fenetre.protocol( "WM_DELETE_WINDOW", destroy_app )
                #
                # Start thread ThreadQuery
                #
                thread_build_docx.start()
                #
                # Start GUI Interface
                #
                gui.ihm.mainloop()
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e
