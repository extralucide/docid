#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from Tkconstants import DISABLED
import csv
from math import floor
import os
from os.path import join
import re
import string
import sys
import time
import zipfile

try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")

from synergy import Synergy
from tool import Tool
from ccb import CCB
from datetime import datetime
from conf import VERSION
import json
import webbrowser

__author__ = 'olivier'
class BuildDoc(Synergy):
    tiny_header = ["Name","Version","Release"]
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

    def __init__(self,
                 ihm=None,
                 dico_parameters={},
                 preview=False,
                 **kwargs):
        """
        :param ihm:
        :param kwargs:
        :return:
        """
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
        if "session_started" in self.__dict__:
            Synergy.__init__(self,self.session_started)
        if ihm is not None:
            self.ihm = ihm
            self.old_cr_workflow = self.ihm.getTypeWorkflow()
        #self.session_started = session_started
        self.ccb_type = "SCR"
        self.list_cr_for_ccb_available = False
        self.preview = preview
        try:
            if "cid_type" in self.__dict__:
                self.cid_type = self.__dict__["cid_type"]
            else:
                if ihm is not None:
                    self.cid_type = self.ihm.getCIDType()
                else:
                    self.cid_type = ""
            self.tableau_pr = []
            self.docx_filename = ""
            self.object_released = ""
            self.object_integrate = ""
            self.author = dico_parameters["author"]
            self.reference = dico_parameters["reference"]
            self.revision = dico_parameters["issue"]
            self.release = dico_parameters["release"]
            if "aircraft" in dico_parameters:
                self.aircraft = dico_parameters["aircraft"]
            else:
                self.aircraft = "Unknown A/C"
            self.system = dico_parameters["system"]
            self.item = dico_parameters["item"]
            self.component = dico_parameters["component"]
            self.project = dico_parameters["project"]
            self.baseline = dico_parameters["baseline"]
            self.part_number = dico_parameters["part_number"]
            self.board_part_number = dico_parameters["board_pn"]
            self.checksum = dico_parameters["checksum"]
            self.dal = dico_parameters["dal"]
            self.previous_release = self.ihm.previous_release_entry.get()
            self.impl_release = dico_parameters["implemented"]
            self.detect_release = dico_parameters["detect"]
            self.target_release = dico_parameters["implemented"]
        except KeyError,e:
            print "KeyError:",e
            self.target_release = ""
        except AttributeError,e:
            print "AttributeError:",e
            self.author = ""
            self.reference = ""
            self.revision = ""
            self.release = ""
            self.aircraft = ""
            self.system = ""
            self.item = ""
            self.component = ""
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
            self.target_release = ""
            self.detect_release = ""
            self.object_released = ""
            self.object_integrate = ""
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
        if "config_parser" in self.__dict__:
            result = self._loadConfig()
        self.protocol_interface_index = "0"
        self.data_interface_index = "0"
        self.ref_index = 1
        # Read user cid tags (json format)
        self.dico_onw_user_cid_tags = {}
        try:
            src_file = join("conf","user_cid_tags.json")
            with open(src_file) as src:
                try:
                    self.dico_own_user_cid_tags = json.load(src)
                except ValueError as exception:
                    print ("Json file error:",str(exception))
                #print "IN:",self.dico_own_user_cid_tags
        except IOError as e:
            print (e)
            self.dico_oww_user_cid_tags = {}
        self._initTables()
        self._initTablesSrc()

    def getCIDType(self):
        return self.cid_type
        #webbrowser.open

    def getSpecificBuild(self,
                         release="",
                         baseline="",
                         project="",
                         filters=["BUILD"],
                         list_found_items=[]):
        """
            Get file in  BUILD folder under a Synergy project
        """
        table = []
        result = []
        for keyword in filters:
            self.getItemsInFolder(keyword,
                                   project,
                                   baseline,
                                   release,
                                   only_name=True,
                                   with_extension=True,
                                   mute=True,
                                   converted_list=result,
                                   list_found_items = list_found_items
                                   )
            if result:
                table = result
                break
        return table
        type_items = "(cvtype='shsrc' or cvtype='executable' or cvtype='ascii' or cvtype='makefile')"
        stdout = self._runFinduseQuery(release,project,type_items,True)
        #if stdout:
        if stdout not in ("",False):
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
            self.ihm.log('No build files found in BUILD folder.')
        return table

    def getSpecificData(self,
                        release="",
                        baseline="",
                        project="",
                        filters=["INPUT_DATA","REVIEW","VTPR",""],
                        source=False):
        """
            Use finduse command of Synergy to find path
        """
        if source:
            table = []
            type_items = "(cvtype='ascii' or cvtype='csrc' or cvtype='incl')"
        else:
            table = [[],[],[],[]]
            type_items = "(cvtype='xls' or cvtype='doc' or cvtype='pdf' or cvtype='ascii' or cvtype='csrc' or cvtype='incl')"
        enabled = True
        for list_filter in filters:
            if self._is_array(list_filter):
                for keyword in list_filter:
                    self.ihm.log('Search folder containing keyword: ' + keyword)
            else:
                self.ihm.log('Search folder containing keyword: ' + list_filter)
        stdout = self._runFinduseQuery(release,project,type_items,enabled)
        #print "STDOUT",stdout

        if not stdout:
            if source:
                print "FILTER/PROJECT",list_filter,project
                result = []
                if self._is_array(list_filter):
                    for keyword in list_filter:
                        self.getItemsInFolder(keyword,
                                                       project,
                                                       baseline,
                                                       release,
                                                       only_name=True,
                                                       with_extension=True,
                                                       mute=True,
                                                       recur=True,
                                                       converted_list=result)
                        if result:
                            break
                else:
                    self.getItemsInFolder(list_filter,
                                                   project,
                                                   baseline,
                                                   release,
                                                   only_name=True,
                                                   with_extension=True,
                                                   mute=True,
                                                   recur=True,
                                                   converted_list=result)
                if result:
                    table = result
            else:
                index = 0
                for list_filter in filters:
                    result = []
                    if self._is_array(list_filter):
                        for keyword in list_filter:
                            print ("KEYWORD:",index,keyword)
                            self.getItemsInFolder(keyword,
                                                           project,
                                                           baseline,
                                                           release,
                                                           only_name=True,
                                                           with_extension=True,
                                                           mute=True,
                                                           recur=True,
                                                           converted_list=result)
                            if result:
                                table[index].extend(result)
                    else:
                        print ("KEYWORD2:",list_filter)
                        self.getItemsInFolder(list_filter,
                                                       project,
                                                       baseline,
                                                       release,
                                                       only_name=True,
                                                       with_extension=True,
                                                       mute=True,
                                                       recur=True,
                                                       converted_list=result)
                        if result:
                            table[index] = result
                    index += 1
            print "OLD TABLE",table
            return table
        else:
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
        m = re.match(r"(.*)\.(cof|hex|srec|elf|map|txt)",filename)
        if m:
            output_file = filename
        else:
            output_file = ""
        return output_file

    @staticmethod
    def _getSwProg(filename):
        """
        return filename if filename match regular expression
        "(.*)\.(bat|sh|log|gld|txt|exe)"
        or
        "(m|Makefile)"
        :param filename:
        :return:
        """
        m = re.match(r"(.*)\.(bat|sh|log|gld|txt|exe|gproc|ld|cpcmd)",filename)
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
        m = re.match(r"(.*)\.(hex|srec)",filename)
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

    def _createTblUserDocument(self,
                               m,
                               list_tags):
        '''
            Add a "type_doc" document in table of "type_doc" if
            - the name of the document match the name in user dictionary
            - the type of the document is doc or pdf
        '''
        result = False
        release_item = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        tbl_doc = None
        if type in ('doc','pdf','xls'):
            doc_name = self.getDocName(m)
            #doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for dico in list_tags:
                tag         = dico["tag"]
                key         = dico["keyword"]
                description = dico["description"]
                reference   = dico["ref"]
                print ("KEY:",key,doc_name)
                if key in doc_name:
                    if self.getCIDType() not in ("SCI"):
                        tbl_doc = [release_item + ":" + project,document,version,description,task]
                    else:
                        if reference == "":
                            reference = self._getReference(document)
                        if tag == u'PRR':
                            tbl_doc = [document,version,release_item]
                        #elif tag == u'CCB':
                        #    tbl_doc = [description,doc_name,version,type,instance,release_item]
                        #    self.tbl_ccb = [description,doc_name,version,type,instance,release_item]
                        else:
                            # Remove CR not in user list
                            res_tbl = []
                            all_tbl_cr = cr.split(",")
                            res_tbl.extend(all_tbl_cr)
                            Tool.removeCRs(res_tbl,self.list_only_include_cr)
                            if len(res_tbl) > 1:
                                list
                                filter_cr = ",".join(res_tbl)
                            else:
                                filter_cr = "".join(res_tbl)
                            tbl_doc = [description,reference,document,version,type,instance,release_item,filter_cr]
                    result = tag
                    #print "tbl_doc",result,tbl_doc
                    break
        return result,tbl_doc

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

    def _createTblSourcesHistory(self,tbl_decod,source_only=True):
        result = False
        document = tbl_decod[0]
        version = tbl_decod[1]
        task = tbl_decod[2]
        task_synopsis = tbl_decod[3]
        cr = tbl_decod[4]
        cr_synopsis = tbl_decod[5]
        type = tbl_decod[6]
        owner = tbl_decod[7]
        line = False
        if source_only:
            list_type_src = self.getSrcType()
            condition = (type in list_type_src and self._isSourceFile(document))
        else:
            condition = type not in ("folder","dir","task","project_grouping","process_rule","baseline")
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
                    #text_summoning = "find CRs"
                    # if the command has already be executed  go get the cache instead
                    if task_id_str not in self.cache_array:
                        stdout,stderr = self.getCR_linked_to_Task(task_id_str)
                        #query = "task -show change_request " + task_id_str
                        #self.ihm.log("ccm " + query)
                        #stdout,stderr = self.ccm_query(query,text_summoning)
                        # Set scrollbar at the bottom
                        #self.ihm.defill()
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
                        line.append(document + ";" + version + ";" + list_tasks[index] + ";" + list_task_synopsis[index] + ";" + list_cr[index_cr] + ";" + list_cr_synopsis[index_cr] + ";" + owner)
                else:
                    line.append(document + ";" + version + ";" + list_tasks[index] + ";" + list_task_synopsis[index] + ";;;" + owner)
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
            if self.getCIDType() not in ("SCI"):
                description,reference = self._getDescriptionDoc(document)
                self.tableau_prog.append([release_item + ":" + project,document,issue,description,task])
            else:
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
        def readEOC(document,
                    issue,
                    type,
                    instance):
            query = 'cat {:s}-{:s}:{:s}:{:s}'.format(document,issue,type,instance)
            self.ihm.log("ccm " + query)
            stdout,stderr = self.ccm_query(query,"Read {:s} issue {:s}".format(document,issue))
            if stdout != "":
                #print "HEX:",stdout
                hex_file = stdout.splitlines()
                pn_found = Tool.getPN(hex_file)
                print "PART NUMBER found:",pn_found
                self.ihm.log("PART NUMBER found:" + pn_found,color="white")
                if self.part_number == pn_found:
                    self.ihm.log("PN found in the {:s}.{:s} EOC matches the PN given.".format(document,issue),color="white")
                else:
                    self.ihm.log("Warning: PN found in the {:s}.{:s} EOC mismatches the PN given.".format(document,issue),color="red")
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
            #if self.getCIDType() == "SCI":
            #    readEOC(document,issue,type,instance)
            self.tbl_sw_eoc.append([document,issue,type,instance,release_item])

    def _createTblConstraint(self,match):
        # For PLD/FGPA synthesis
        seek_file = self._getConstraintFile(match.group(2))
        if seek_file not in ("",None):
            self.tbl_constraint_file.append([match.group(2),match.group(3),match.group(1)])

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
        doc_name = re.sub(r"(.*)\.(.*)",r"\1",document)
        # Check if the release basename is the same by removing /01 etc
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
                        self.tbl_plans.append([release_item + ":" + project,document,version,description,task])
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

    def _createTblCcb(self,m,target_release=""):
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
        if type in ('doc','pdf','xls'):
            dico = {"CCB_Minutes":"CCB meeting report",
                    "CCB":"CCB meeting report",
                    "CCB_Actions":"CCB Actions list"}
            # doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            doc_name = self.getDocName(m)
            for key in dico:
                if key in doc_name:
                    ccb_release = self.getDocRelease(m)
                    if target_release == "" or \
                        ccb_release == target_release:
                        description = dico[key]
                        if self.getCIDType() not in ("SCI"):
                            self.tbl_ccb.append([release_item + ":" + project,doc_name,version,description,m.group(4)])
                        else:
                            self.tbl_ccb.append([description,doc_name,version,type,instance,release_item])
                        result = True
                    else:
                        # Discard CCB minutes
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

    def _createTblScod(self,m):
        '''
            Add a SCOD document in table of SCOD if
            - the name of the document match the name in SCOD dictionary
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
            dico = {"SCOD":"Software Coding Output Document"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description,reference = self._getDescriptionDoc(document)
                    description = dico[key]
                    if self.getCIDType() not in ("SCI"):
                        self.tbl_scod.append([m.group(1) + ":" + m.group(7),m.group(2),m.group(3),description,m.group(4)])
                    else:
                        self.tbl_scod.append([description,reference,document,version,type,instance,release_item,cr])
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
        if type in ('xls',"doc"):
            dico = {"IS_":"Inspection Sheet",
                    "FDL":"Fiche de Lecture",
                    "PRR":"Peer Review Register",
                    "Comment":"Peer Review"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description = dico[key]
                    if self.getCIDType() not in ("SCI"):
                        self.tbl_inspection_sheets.append([release + ":" + project,document,version,description,task])
                    else:
                        self.tbl_inspection_sheets.append([document,version,release])
                    result = True
        return result

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
        gen_dir = join(os.path.dirname("."), self.gen_dir)
        self.docx_filename = join(gen_dir, self.aircraft + "_" + self.item + "_" + template_type + "_" + self.reference + ".docx")
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
        """
        :return:
        """
        # Get config
        tool = Tool()
        read_config = True

        # init values
        self.func_chg = ""
        self.oper_chg = ""
        self.dico_descr_docs = {}
        self.dico_descr_docs_ref = {}
        self.dico_descr_docs_default = {}
        self.list_type_src_sci = ()
        self.list_type_src_hcmr = ("ascii")
        self.list_type_prog = ()
        self.list_type_outputs = ("ascii")
        self.input_data_filter = []
        self.peer_reviews_filter = []
        self.verif_filter = []
        self.exclude_filter = []
        self.sources_filter= []

        try:
            self.previous_baseline = tool.getOptions("Default","previous_baseline")
            only_include_cr = tool.getOptions("Generation","only_include_cr")
            for self.list_only_include_cr in csv.reader([only_include_cr]):
                pass
            self.list_only_include_cr = map((lambda x: str(x)),self.list_only_include_cr)
            #print "list_only_include_cr",self.list_only_include_cr
            #exit()
            self.finduse = tool.getOptions("Generation","finduse")
             # get generation directory
            self.gen_dir = tool.getOptions("Generation","dir")
            self.input_data_filter = tool._getOptionArray("Generation","input_data")
            self.peer_reviews_filter = tool._getOptionArray("Generation","peer_reviews")
            self.verif_filter = tool._getOptionArray("Generation","verification")
            self.exclude_filter = tool._getOptionArray("Generation","exclude")
            self.sources_filter= tool._getOptionArray("Generation","sources")
            self.build_filter= tool._getOptionArray("Generation","build")
            # read dictionary of doc for project
            # 3 columns separated by comma
            self.protocol_interface = tool.getOptions("Generation","protocol_interface")
            self.data_interface = tool.getOptions("Generation","data_interface")
            # get CR workflow type
            if self.config_parser.has_section("Workflow"):
                self.ihm.check_cr_workflow_status.config(state=DISABLED)
                self.ihm.type_cr_workflow = self.config_parser.get("Workflow","CR")
            else:
                try:
                    self.ihm.type_cr_workflow = "None"
                except:
                    pass
                # read object type
            type_doc = tool.config_parser.get("Objects","type_doc")
            for self.list_type_doc in csv.reader([type_doc]):
                pass
            if tool.config_parser.has_option("Objects","type_src"):
                type_src = tool.config_parser.get("Objects","type_src")
                if type_src:
                    for self.list_type_src_sci in csv.reader([type_src]):
                        pass
                else:
                    self.list_type_src_sci = ("csrc","asmsrc","incl","macro_c","library")
            elif tool.config_parser.has_option("Objects","sw_src"):
                type_src = tool.config_parser.get("Objects","sw_src")
                if type_src:
                    for self.list_type_src_sci in csv.reader([type_src]):
                        pass
                else:
                    self.list_type_src_sci = ()
            else:
                self.list_type_src_sci = ()

            if tool.config_parser.has_option("Objects","sw_prog"):
                type_prog = tool.config_parser.get("Objects","sw_prog")
                if type_prog:
                    for self.list_type_prog in csv.reader([type_prog]):
                        pass
                else:
                    self.list_type_prog = ()
            else:
                self.list_type_prog = ()

            if tool.config_parser.has_option("Objects","sw_ouputs"):
                type_outputs = tool.config_parser.get("Objects","sw_outputs")
                if type_outputs:
                    for self.list_type_outputs in csv.reader([type_outputs]):
                        pass
                else:
                    self.list_type_outputs = ("ascii")
            else:
                self.list_type_outputs = ("ascii")
            if tool.config_parser.has_option("Objects","type_src"):
                type_src = tool.config_parser.get("Objects","type_src")
                if type_src:
                    for self.list_type_src_hcmr in csv.reader([type_src]):
                        pass
                else:
                    self.list_type_src_hcmr = ("ascii")
            elif tool.config_parser.has_option("Objects","hw_src"):
                type_src = tool.config_parser.get("Objects","hw_src")
                if type_src:
                    for self.list_type_src_hcmr in csv.reader([type_src]):
                        pass
                else:
                    self.list_type_src_hcmr = ("ascii")
            else:
                self.list_type_src_hcmr = ("ascii")
        except KeyError as exception:
            self.ihm.log("Key missing in config file")
            read_config = False

        try:
            if tool.config_parser.has_option("Generation","description_docs"):
                file_descr_docs = tool.config_parser.get("Generation","description_docs")
                file_descr_docs = join("conf",file_descr_docs)
                with open(file_descr_docs, 'rb') as file_csv_handler:
                    reader = csv.reader (self.CommentStripper (file_csv_handler))
                    for tag,description,reference in reader:
                        #print "Y",description,reference
                        self.dico_descr_docs[tag] = description
                        self.dico_descr_docs_ref[tag] = reference
        except IOError as exception:
            self.ihm.log("Generation description_docs config reading failed: {:s}".format(file_descr_docs))
            read_config = False
        except ValueError as exception:
            try:
                self.ihm.log("Error values in configuration file description_docs")
            except:
                pass
            # read dictionary of generic description for doc
            # 2 columns separated by comma
        try:
            if tool.config_parser.has_option("Generation","glossary"):
                file_glossary = tool.config_parser.get("Generation","glossary")
                file_glossary = join("conf",file_glossary)
                with open(file_glossary, 'rb') as file_csv_handler:
                    reader = csv.reader (self.CommentStripper (file_csv_handler))
                    for tag,description in reader:
                        self.dico_descr_docs_default[tag] = description
        except IOError as exception:
            self.ihm.log("Generation glossary config reading failed: {:s}".format(file_glossary))
            read_config = False

        try:
            func_chg_filename = tool.getOptions("Generation","func_chg_filename")
            func_chg_filename = join("conf",func_chg_filename)
            if func_chg_filename != "":
                fichier = open(func_chg_filename, "r")
                func_chg_tbl = fichier.readlines()
                self.func_chg = []
                for line in func_chg_tbl:
                    self.func_chg.append((Tool.replaceNonASCII(line),'r'))
            else:
                self.func_chg = ""
        except IOError as exception:
            self.ihm.log("Generation func_chg_filename config reading failed: {:s}".format(func_chg_filename))
            read_config = False
        try:
            oper_chg_filename = tool.getOptions("Generation","oper_chg_filename")
            oper_chg_filename = join("conf",oper_chg_filename)
            if oper_chg_filename != "":
                fichier = open(oper_chg_filename, "r")
                oper_chg_tbl = fichier.readlines()
##                self.oper_chg = oper_chg_tbl
                self.oper_chg = []
                for line in oper_chg_tbl:
                    self.oper_chg.append((Tool.replaceNonASCII(line),'r'))
            else:
                self.oper_chg = ""
        except IOError as exception:
            self.ihm.log("Generation func_chg_filename config reading failed: {:s}".format(oper_chg_filename))
            read_config = False

        #self.ihm.defill()
        return read_config

    def _setOuptutFilename(self,template_type):
        """
        :return:
        """
        self.docx_filename = "{:s}_".format(self.system)
        if self.item != "":
            self.docx_filename += "{:s}_".format(self.item)
        if self.component != "":
            self.docx_filename += "{:s}_".format(self.component)
        self.docx_filename += template_type + "_" + self.reference + "_%d" % floor(time.time()) + ".docx"
        self.ihm.log("Preparing " + self.docx_filename + " document.")
        return self.docx_filename

    def _getAllProg(self,release,baseline,project):
        '''
            Looking for programming files according to self.list_type_prog
        '''
        output = self.getArticles(self.list_type_prog,
                                  release,
                                  baseline,
                                  project,
                                  True)
        index_prog = 0
        index_sw_outputs = 0
        index_sw_eoc = 0
        for line in output:
            line = re.sub(r"<void>",r"",line)
            m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
            if m:
                result = self._createTblSoftwareProgramming(m)
                if result:
                    self.ihm.log("Found programming files: "+line,False)
                    index_prog +=1
                result = self._createTblSoftwareOutputs(m)
                if result:
                    self.ihm.log("Found software outputs: "+line,False)
                    index_sw_outputs +=1
                result = self._createTblSoftwareEOC(m)
                if result:
                    self.ihm.log("Found software EOC: "+line,False)
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

    def _getAllSourcesHistory(self,
                              release,
                              baseline,
                              project):
        '''
            Looking for source files according to self.list_type_src
        '''
        output = self.getArticles(self.list_type_src,
                                  release,
                                  baseline,
                                  project,
                                  True)
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

    def _getAllSources(self,
                       release,
                       baseline,
                       project):
        '''
            Looking for source files according to self.list_type_src
        '''
        output = self.getArticles(self.list_type_src,
                                  release,
                                  baseline,
                                  project,
                                  True)
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

    def _getAllDocuments(self,
                         release,
                         baseline,
                         project):
        # Patch
        if project == "All":
            project = ""
        output = self.getArticles(self.list_type_doc,
                                  release,
                                  baseline,
                                  project,
                                  source=False,
                                  recursive=True,
                                  exclude=self.exclude_filter)
        self._parseSynergyOutput(output)

    def _parseSynergyOutput(self,output):
        # patch temp
        header = ["Title","Reference","Synergy Name","Version","Type","Instance","Release","CR"]
        index_doc   = 0
        index_user  = 0
        index_input = 0
        index_plan  = 0
        index_std   = 0
        index_sas   = 0
        index_seci  = 0
        index_scod  = 0
        index_ccb   = 0
        index_is    = 0
        index_icd_protocol  = 0
        index_icd_data      = 0
        link_id = 1

        for line in output:
            line = re.sub(r"<void>",r"",line)
            self.ihm.log("Found doc: " + line,display_gui=False)
            # release;filename;tasks;?;type;project;instance
            m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
            if m:
                # first inspection files
                if "Reviews" in self.dico_own_user_cid_tags:
                    list_tags = self.dico_own_user_cid_tags["Reviews"]
                    result,tbl_doc_found = self._createTblUserDocument(m,
                                                                       list_tags)
                else:
                    result = False
                if result:
                    index_is +=1
                    self.tbl_inspection_sheets.append(tbl_doc_found[:])
                else:
                    # then plans
                    if "Plans" in self.dico_own_user_cid_tags:
                        list_tags = self.dico_own_user_cid_tags["Plans"]
                        result,tbl_doc_found = self._createTblUserDocument(m,
                                                                           list_tags)
                    else:
                        result = False
                    if result:
                        index_plan +=1
                        self.tbl_plans.append(tbl_doc_found[:])
                    else:
                        # then other documents
                        if "Documents" in self.dico_own_user_cid_tags:
                            list_tags = self.dico_own_user_cid_tags["Documents"]
                            tag,tbl_doc_found = self._createTblUserDocument(m,
                                                                              list_tags)
                            if tag:
                                # User tag
                                index_user += 1
                                if tag not in self.tbl_user:
                                    self.tbl_user[tag] = [header]
                                self.tbl_user[tag].append(tbl_doc_found[:])
                        else:
                            result = False
                        if not result:
                            if  self.protocol_interface in m.group(2):
                                self.protocol_interface_index = m.group(3)
                                index_icd_protocol +=1
                            elif self.data_interface in m.group(2) :
                                self.data_interface_index = m.group(3)
                                index_icd_data +=1
                            result = self._createTblDocuments(m,
                                                              self.tableau_items,
                                                              link_id,
                                                              for_sci=True)
                            if result:
                                index_doc +=1
        self.ihm.log("Amount of other documents found: {:d}".format(index_doc),False)
        self.ihm.log("Amount of user data found: {:d}".format(index_user),False)
        self.ihm.log("Amount of input data found: {:d}".format(index_input),False)
        self.ihm.log("Amount of inspection sheets found: {:d}".format(index_is),False)
        self.ihm.log("Amount of plans found: {:d}".format(index_plan),False)
        self.ihm.log("Amount of standards found: {:d}".format(index_std),False)
        self.ihm.log("Amount of CCB minutes found: {:d}".format(index_ccb),False)
        self.ihm.log("Amount of SAS found: {:d}".format(index_sas),False)
        self.ihm.log("Amount of SECI found: {:d}".format(index_seci),False)
        self.ihm.log("Amount of SCOD found: {:d}".format(index_scod),False)
        self.ihm.log("Amount of protocol interface document found: {:d}".format(index_icd_protocol),False)
        self.ihm.log("Amount of data interface document found: {:d}".format(index_icd_data),False)

    def isCodeOnly(self,tag):
        '''
        Check baseline name for CODE keyword
        '''
        #tag_code_only = re.match(r'^CODE_(.*)',tag) or re.match(r'(.*)VHDL(.*)',tag)
        if "VHDL" in tag or "CODE" in tag:
            tag_code_only = True
        else:
            tag_code_only = False
        #if tag_code_only is None:
        #    return False
        #else:
        #    return True
        return tag_code_only

    def isBoardOnly(self,tag):
        '''
        Check baseline name for BOARD keyword
        '''
        tag_only = re.match(r'^BOARD_(.*)',tag)
        if tag_only is None:
            return False
        else:
            return True

    def isHwOnly(self,tag):
        '''
        Check baseline name for HW keyword
        '''
        tag_only = re.match(r'^HW_(.*)',tag)
        if tag_only is None:
            return False
        else:
            return True

    def _initTables(self):
        '''
        '''
        # Header for documents
        if self.getCIDType() not in ("SCI"):
            # FPGA
            # Header for sources
            header_soft_sources = ["Release:Project","Data","Issue","Tasks","Change Request"]
            header = ["Release:Project","Data","Issue","Tasks","Change Request"]
            self.tbl_build = [header]
            header = ["Release:Project","Document","Issue","Description","Tasks"]
            header_input = ["Release:Project","Document","Issue","Description","Tasks"]
            header_ccb_input = ["Release:Project","Document","Issue","Description","Tasks"]
            header_prr = header
        else:
            # software
            # Header for sources
            header_soft_sources = ["File Name","Version","Type","Instance","Release","CR"]
            self.tbl_build = [header_soft_sources]
            header_input = ["Title","Reference","Synergy Name","Version","Type","Instance","Release"]
            header_ccb_input = ["Title","Reference","Synergy Name","Version","Type","Instance","Release"]
            header = ["Title","Reference","Synergy Name","Version","Type","Instance","Release","CR"]
            header_prr = ["Name","Version","Release"]
        # Header for delivery
        header_delivery = ["File Name","Version","Type","Instance","Release"]
        self.tableau_items = []
        self.tbl_items_filtered = [header]
        self.tbl_input_data = [header_input]
        self.tbl_plans = []
        self.tbl_stds = [header]
        self.tbl_ccb = [header_ccb_input]
        #self.tbl_ccb.append(header_ccb_input)
        self.tableau_prog = []
        self.tbl_program_file = [self.tiny_header]
        self.tbl_synthesis_file = [self.tiny_header]
        self.tbl_constraint_file = [self.tiny_header]
        # Specific Software
        self.tbl_inspection_sheets = []
        self.tbl_sas = [header]
        self.tbl_seci = [header]
        self.tbl_scod = [header]
        # Split table of items with input data and peer reviews
        self.tbl_verif = [header]
        self.tbl_exclude = [header]
        self.tbl_peer_reviews = [header_prr]
        self.tbl_user = {}

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
        self.tbl_build = [header_soft_sources]
##            tbl_sources.append(header)
        self.tbl_sources = [header_soft_sources]
        self.tableau_items = []
##        self.tableau_items.append(header_soft_sources)
        self.tableau_prog = []
        self.tableau_src = []
        self.tbl_program_file = [self.tiny_header]
        self.tbl_synthesis_file = [self.tiny_header]
        self.tbl_constraint_file = [self.tiny_header]
        # Specific Software
        self.tbl_sw_outputs = [header_delivery]
        self.tbl_sw_eoc = [header_delivery]

    def getSrcType(self):
        # Get expected type of sources according to CID type
        if self.cid_type == "SCI":
            list_type_src = self.list_type_src_sci
            # self.ccb_type = "SCR"
        elif self.cid_type == "HCMR_PLD":
            list_type_src = self.list_type_src_hcmr
            # self.ccb_type = "PLDCR"
        elif self.cid_type == "HCMR_BOARD":
            list_type_src = ()
            # self.ccb_type = "HCR"
        else:
            # self.ccb_type = "ALL"
            list_type_src = ()
##        print self.cid_type,list_type_src
        return list_type_src

    def _getInfo(self):
        item = self.item
        if self.author == "":
             name,mail,tel,service,qams_user_id = self.get_user_infos(self.login)
             if name:
                 author = Tool.replaceNonASCII(name)
        else:
            author = Tool.replaceNonASCII(self.author)
        if self.item == "":
            database,aircraft = self.get_sys_database()
            item = "Unidentified"
            item_description = "Unknown"
            ci_identification = "A000"
        else:
            database,aircraft = self.get_sys_item_database(self.system,
                                                           self.item)
            if database is None:
                database,aircraft = self.get_sys_database()
            item_description = self.getItemDescription(self.item)
            ci_identification = self.get_ci_sys_item_identification(self.system,
                                                                    self.item)
        if aircraft is not None and self.system is not None:
            program = "{:s} {:s}".format(aircraft,self.system)
        else:
            program = None
        return author,\
               item,\
               database,\
               aircraft,\
               item_description,\
               ci_identification,program

    def getSubject(self,
                   system,
                   item,
                   component,
                   template_type):
        """
        :param system:
        :param item:
        :param template_type:
        :return:
        """
        if component != "":
            title   = "{:s} {:s} {:s}".format(system,component,template_type)
            subject = "{:s} {:s} {:s}".format(system,component,self.getTypeDocDescription(template_type))
        elif item != "":
            title   = "{:s} {:s} {:s}".format(system,item,template_type)
            subject = "{:s} {:s} {:s}".format(system,item,self.getTypeDocDescription(template_type))
        else:
            title   = "{:s} {:s}".format(system,template_type)
            subject = "{:s} {:s}".format(system,self.getTypeDocDescription(template_type))
        return title,subject

    def getBoardData(self,
                     tbl_other_doc,
                     ccb_doc,
                     plans_doc,
                     has_doc,
                     cid_doc,
                     output,
                     link_id):
        index_doc = 0
        index_is = 0
        target_release = self.target_release
        for line in output:
            line = re.sub(r"<void>", r"", line)
            self.ihm.log("Found doc: " + line, display_gui=False)
            m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)', line)
            if m:
                # Look for IS and PRR first
                if self._createTblInspectionSheets(m):
                    index_is +=1
                 # CCB minutes
                elif self._getSpecificDoc(m, "_CCB_", ("doc")):
                    index_doc += 1
                    name = self.getDocName(m)
                    ccb_release = self.getDocRelease(m)
                    if target_release == "" or ccb_release == target_release:
                        link_id = self._createTblDocuments(m, ccb_doc, link_id,for_sci=True)
                        #if name not in ccb_doc:
                        #    ccb_doc.append(name)
                elif self._getSpecificDoc(m, "HMP_", ("doc","pdf")) or \
                        self._getSpecificDoc(m, "PHAC_", ("doc","pdf")):
                    # Plans
                    index_doc += 1
                    name = self.getDocName(m)
                    link_id = self._createTblDocuments(m, plans_doc, link_id,for_sci=True)
                elif self._getSpecificDoc(m, "HAS_", ("doc","pdf")):
                    # Accomplishment summary
                    index_doc += 1
                    name = self.getDocName(m)
                    link_id = self._createTblDocuments(m, has_doc, link_id,for_sci=True)
                elif self._getSpecificDoc(m, "SCI_", ("doc","pdf")) or self._getSpecificDoc(m, "HCMR_", ("doc","pdf")):
                    # Configuration index documents
                    index_doc += 1
                    name = self.getDocName(m)
                    link_id = self._createTblDocuments(m, cid_doc, link_id,for_sci=True)
                # Upper documents
                # elif self._getSpecificDoc(m, "SSCS", ("doc", "pdf","xls")) or \
                #     self._getSpecificDoc(m, "SDTS", ("doc", "pdf","xls")) or \
                #     self._getSpecificDoc(m, "SES", ("doc", "pdf","xls")) or \
                #     self._getSpecificDoc(m, "CAN", ("doc", "pdf","xls")) or \
                #     self._getSpecificDoc(m, "IRD", ("doc", "pdf","xls")) or \
                #     self._getSpecificDoc(m, "SPI", ("doc", "pdf","xls")):
                #     index_doc += 1
                #     name = self.getDocName(m)
                #     link_id = self._createTblDocuments(m, tbl_upper_doc, link_id)
                # elif self._getSpecificDoc(m, "ATS", ("doc", "pdf","xls")) or \
                #     self._getSpecificDoc(m, "ATP", ("doc", "pdf","xls")) or \
                #     self._getSpecificDoc(m, "ATR", ("doc", "pdf","xls")) or \
                #     self._getSpecificDoc(m, "HVVPR", ("doc", "pdf","xls")):
                #     index_doc += 1
                #     name = self.getDocName(m)
                #     link_id = self._createTblDocuments(m, tbl_verif_doc, link_id)
                elif self._createTblSoftwareProgramming(m):
                    self.ihm.log("Found programming files: "+line,False)
                elif self._createTblSoftwareOutputs(m):
                    self.ihm.log("Found software outputs: "+line,False)
                elif self._createTblSoftwareEOC(m):
                    self.ihm.log("Found software EOC: "+line,False)
                else:
                    link_id = self._createTblDocuments(m, tbl_other_doc, link_id,for_sci=True)
        return link_id

    @staticmethod
    def sortByName(tbl_in,
                   tbl_out,
                   index=2,
                   index_version=3,
                   index_cr=7,
                   with_cr=True,
                   line_empty=["--","--","--","--","--","--","--","--"]):
        dico = {}
        for doc in tbl_in:
            synergy_name = doc[index]
            synergy_name_suffix = re.sub(r"(.*)\.(.*)$", r"\1", synergy_name)
            #if "MC21_ENMU" in synergy_name:
            #    print "synergy_name",synergy_name
            #    print "synergy_name_suffix",synergy_name_suffix
            if synergy_name_suffix not in dico:
                if with_cr:
                    dico[synergy_name_suffix] = [doc[0:8]]
                else:
                    dico[synergy_name_suffix] = [doc[0:7]]
            else:
                if with_cr:
                    dico[synergy_name_suffix].append(doc[0:8])
                else:
                    dico[synergy_name_suffix].append(doc[0:7])
        #if "MC21_ENMU" in dico:
        #    print "DICO",dico
        #tbl_in = sorted(tbl_in,key=lambda x: x[index])
        tbl_input_data_unsorted = []
        for name,doc in dico.iteritems():
            # sort input data in reverse order by version
            #print "DOC",doc
            doc = sorted(doc,key=lambda x: x[index_version])#,reverse=True)
            # get the first data only
            #print "Name",name
            iter = 1
            nb_version = len(doc)
            list_cr = []
            for object in doc:
                type_obj = object[2]
                if with_cr:
                    # Concatenate all applicable CRs for the last version of document
                    cr_implemented = object[index_cr]
                    #print "CR",cr_implemented
                    if cr_implemented != "":
                        list_cr.append(cr_implemented)

                    if iter >= nb_version or (type_obj not in ("pdf","doc")):
                        # Remove redundant data
                        list_cr_str = ",".join(set(list_cr))
                        object[index_cr] = list_cr_str
                        tbl_input_data_unsorted.append(object)

                else:
                     if iter >= nb_version or (type_obj not in ("pdf","doc")):
                        tbl_input_data_unsorted.append(object)
                iter += 1
        tbl_input_data_unsorted = sorted(tbl_input_data_unsorted,key=lambda x: x[index])
        tbl_out.extend(tbl_input_data_unsorted)
        if len(tbl_out) == 1 and line_empty:
            tbl_out.append(line_empty)

    def sortData(self,
                 # Inputs
                 table_input_data,
                 list_llr_document=[],
                 table_peer_reviews=[],
                 table_verif=[],
                 table_exclude=[],
                 tbl_build_finduse=[],
                 tableau_sources_finduse=[],
                 # Outputs
                 tbl_input_data=[],
                 tbl_life_cycle_data=[],
                 tbl_plans=[],
                 tbl_verif=[],
                 tbl_src=[],
                 tbl_exclude=[],
                 tbl_peer_reviews=[],
                 tbl_build=[],
                 ):
        """
        Populate
        :param table_input_data:
        :param list_llr_document:
        :param table_peer_reviews:
        :param table_verif:
        :param table_exclude:
        :param tbl_build_finduse:
        :param tableau_sources_finduse:
        :param tbl_input_data:
        :return:
        """
        if self.getCIDType() not in ("SCI"):
            # HCMR board, etc.
            # tableau_items [release + ":" + project,document,version,description,task]
            index_description = 3
            index = 1
            index_src = 1
            index_version_src = 2
            index_src_cr = 4
            index_version = 2
            index_prr = 1
            index_version_prr = 2
            plans_with_cr = False
            life_cycle_data_with_cr = False
            verif_with_cr = False
            source_with_cr = False
            line_sw_eoc_empty = ["--","--","--","--","--"]
            line_src_empty = ["--","--","--","--","--"]
            line_ccb_empty = ["--","--","--","--","--"]
            line_other_empty = ["--","--","--","--","--"]
            line_inputs_empty = ["--","--","--","--","--"]
            line_prr_empty = ["--","--","--","--","--"]
            # header
            # ["Release:Project","Document","Issue","Description","Tasks"]
        else:
            # Only for Software SCI
            # tableau_items [description,reference,document,version,type_doc,instance,release,cr]
            index_description = 0
            index = 2
            index_src = 0
            index_version_src = 1
            index_src_cr = 5
            index_version = 3
            index_prr = 0
            index_version_prr = 1
            plans_with_cr = True
            life_cycle_data_with_cr = True
            verif_with_cr = True
            source_with_cr = True
            line_sw_eoc_empty = ["--","--","--","--","--"]
            line_src_empty = ["--","--","--","--","--","--"]
            line_ccb_empty = ["--","--","--","--","--","--","--"]
            line_other_empty = ["--","--","--","--","--","--","--","--"]
            line_inputs_empty = ["--","--","--","--","--","--","--"]
            line_prr_empty = ["--","--","--"]
            # header
            # ["Title","Reference","Synergy Name","Version","Type","Instance","Release"]

        # Example
        # tableau_items = [
        #                   [' SMS ESSNESS Supplier Specific Component Specification (SSCS)', 'ET2788-S', 'SSCS_ESSNESS_ET2788_S.pdf', '6', 'pdf', '4', 'BOARD_ESSNESS/01', ''],
        #                   [' SMS ESSNESS Supplier Specific Component Specification (SSCS)', 'ET2788-S', 'SSCS_ESSNESS_ET2788_S.doc', '8', 'doc', '2', 'BOARD_ESSNESS/01', '']
        #                 ]
        dico_data = {"sources":[],              # Source code files:    self.tableau_src            tableau_sources_finduse
                     "verif":[],                # Verif:                self.tableau_items          table_verif
                     "inputs":[],               # Inputs:               self.tableau_items          table_input_data
                     "items":[],                # Life cycle data:      self.tableau_items          list_llr_document
                     "plans":self.tbl_plans,    # Plans:                self.tbl_plans              None
                     "build":[],                # Build:                self.tableau_prog           None
                     "peer_reviews":[]}         # Peer reviews:         self.tbl_inspection_sheets  table_peer_reviews

        for doc in self.tableau_items:
            #print "doc[index]:",doc[index]
            # index 2 correspond to Synergy name of the document
            synergy_name = doc[index]
            # object_type = doc[index_type]
            #object_version = doc[index_version]
            if synergy_name in table_input_data:
                # Example: SSCS_ESSNESS_ET2788_S.pdf
                #          SSCS_ESSNESS_ET2788_S.doc
                print "match input_data:",synergy_name
                dico_data["inputs"].append(doc[0:7])
            elif synergy_name in list_llr_document:
                print "match LLR:",doc
                doc[index_description] = "Low Level Requirements Document"
                dico_data["items"].append(doc)
            elif synergy_name in table_verif:
                print "match verif:",synergy_name
                dico_data["verif"].append(doc)
            elif synergy_name in table_exclude:
                print "match exclude:",synergy_name
                tbl_exclude.append(doc)
            else:
                # Everything else
                dico_data["items"].append(doc)
        # Plans
        self.sortByName(dico_data["plans"],
                        tbl_plans,
                        index,
                        index_version,
                        with_cr=plans_with_cr,
                        line_empty=line_other_empty)
        # Sources
        if tableau_sources_finduse != []:
            for src in self.tableau_src:
                synergy_name = src[index_src]
                # index 0 correspond to Synergy name of the source file
                if src[index_src] in tableau_sources_finduse:
                    print "match source:",synergy_name
                    dico_data["sources"].append(src)
                else:
                    pass
        else:
            # par default on prend tout
            dico_data["sources"].extend(self.tableau_src)

        self.sortByName(dico_data["sources"],
                        tbl_src,
                        index=index_src,
                        index_version=index_version_src,
                        index_cr=index_src_cr,
                        with_cr=source_with_cr,
                        line_empty=line_src_empty)

        # Peer reviews
        if table_peer_reviews != []:
            for doc in self.tbl_inspection_sheets:
                synergy_name = doc[index_prr]
                # index 0 correspond to Synergy name of the source file
                if synergy_name in table_peer_reviews:
                    print "match peer review:",synergy_name
                    if self.getCIDType() not in ("SCI"):
                        dico_data["peer_reviews"].append(doc)
                    else:
                        dico_data["peer_reviews"].append(doc[0:3])
                else:
                    pass
        else:
            # par default on prend tout
            dico_data["peer_reviews"].extend(self.tbl_inspection_sheets)

        # Peer review
        self.sortByName(dico_data["peer_reviews"],      # Input
                        tbl_peer_reviews,               # Output
                        index_prr,
                        index_version_prr,
                        with_cr=False,
                        line_empty=line_prr_empty)

        # Scripts trouves dans les repertoire attendu BUILD
        # Example: ['Builder.sh', 'Makefile', 'build.bat', 'checksum.exe', 'compilation.log', 'csu_list.txt', 'p33FJ256GP710A.gld']
        if tbl_build_finduse != []:
            for src in self.tableau_prog:
                synergy_name = src[index_src]
                if synergy_name in tbl_build_finduse:
                    print "match build:",synergy_name
                    dico_data["build"].append(src)
                else:
                    print "miss build:",synergy_name
        else:
            dico_data["build"].extend(self.tableau_prog)

        #tbl_input_data = sorted(tbl_input_data,key=lambda x: x[2])
        # Input data
        self.sortByName(dico_data["inputs"],    # Input
                        tbl_input_data,         # Output
                        index,
                        index_version,
                        with_cr=False,
                        line_empty=line_inputs_empty)

        # Life cycle data
        self.sortByName(dico_data["items"],      # Input
                        tbl_life_cycle_data,     # Output
                        index,
                        index_version,
                        with_cr=life_cycle_data_with_cr,
                        line_empty=line_other_empty)

        # Build
        if self.getCIDType() not in ("SCI"):
            self.sortByName(dico_data["build"],      # Input
                            tbl_build,               # Output
                            index_src,
                            index_version,
                            with_cr=False,
                            line_empty=line_src_empty)
        else:
            self.sortByName(dico_data["build"],      # Input
                            tbl_build,               # Output
                            index_src,
                            index_version,
                            index_cr=5,
                            line_empty=line_src_empty)

        # Verification data
        self.sortByName(dico_data["verif"],      # Input
                        tbl_verif,               # Output
                        index,
                        index_version,
                        with_cr=verif_with_cr,
                        line_empty=line_other_empty)
    @staticmethod
    def setCellBorder(colw):
        cell_borders = {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single'}}
        fmt =  {'heading': True,
                'colw': colw,
                'cwunit': 'pct',
                'tblw': 5000,
                'twunit': 'pct',
                'borders': cell_borders}
        return fmt

    def getContext(self,
                   list_projects,
                   cid_type=False):
        print "getContext",cid_type
        if cid_type not in ("SCI") or self.project == "":
            release_list = []
            baseline_list = []
            project_list = []
            for release,baseline,project in list_projects:
                release_list.append(release)
                baseline_list.append(baseline)
                project_list.append(project)
            # 'set' instruction is used to remove doublons
            list_unique = set(release_list)
            release_text = "\n ".join(map(str, list_unique))
            list_unique = set(baseline_list)
            baseline_text = "\n ".join(map(str, list_unique))
            list_unique = set(project_list)
            project_text = "\n ".join(map(str, list_unique))
        else:
            release_text = self.release
            baseline_text = self.baseline
            project_text = self.project
        return release_text,baseline_text,project_text

    def formatDocTable(self,tbl_output,tbl_input):
        fmt = self.setCellBorder([700,2300,200,2000])
        header = True
        for line in tbl_input:
            filename = line[1]
            issue = line[2]
            description = line[3]
            if header:
                header = False
                reference = "Ref."
            elif line[1] == "-":
                reference = "-"
            else:
                reference = "[R{:d}] {:s}".format(self.ref_index,Tool._getReference(filename))
                self.ref_index += 1
            tbl_output.append((reference,filename,issue,description))
        return fmt

    def createCID(self,
                  project_set_list=[],
                  header_image=True,
                  list_cr_type=[],
                  list_cr_status=[],
                  list_cr_doamin=[],
                  **kwargs):
        """
        This function creates the document based on the template
        - open template docx
        - get sections of the template
        - replace tag in document
        - create zip
         . copy unmodified section
         . copy modified section
        """
        # Launch clock
        dico_timestamp={}
        dico_timestamp["begin_script"] = datetime.now()
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        self.list_type_src = self.getSrcType()
        # get CID template name
        template_name = self._getTemplate(self.cid_type)
        # test presence of template
        if not os.path.exists(template_name):
            # warn user that template is not found
            self.ihm.popup('Specified template in docid.ini configuration file does not exists.')
            # abort cid generation
            return "",None
        self.ihm.log("Use template {:s}.".format(template_name))
        if self.cid_type in ("HCMR_PLD","HCMR_BOARD"):
            template_type = "HCMR"
        else:
            template_type = self.cid_type
        # Prepare output file
        docx_filename = self._setOuptutFilename(template_type)
        eoc_filename = None
        #
        # Documentations
        #
        self.ihm.log("Items query in progress...")
        #self.ihm.defill()
        self._initTables()
        self._initTablesSrc()
        # Header for documents
        cid_type = self.getCIDType()
        if cid_type not in ("SCI"):
            cr_parent= True
            header = ["Release:Project","Document","Issue","Description","Tasks"]
            line_empty_input = ["--","--","--","--","--"]
            line_empty = ["--","--","--","--","--"]
            line_cid_empty = ["--","--","--","--","--"]
            header_input = ["Release:Project","Document","Issue","Description","Tasks"]
            # Header for sources
            # FPGA
            header_soft_sources = ["Release:Project","Data","Issue","Tasks","Change Request"]
            header_prr = header
            line_sw_eoc_empty = ["--","--","--","--","--"]
            line_src_empty = ["--","--","--","--","--"]
            line_ccb_empty = ["--","--","--","--","--"]
            line_other_empty = ["--","--","--","--","--"]
            tbl_build = [header]
            fmt = self.setCellBorder([1000,2300,200,1000,500,500,500])
            fmt_ccb = self.setCellBorder([1000,2300,200,1000,1500])
            fmt_cid = self.setCellBorder([1000,2300,200,500,500])
            fmt_src = self.setCellBorder([2500,500,500,500,500,500])
            fmt_build = self.setCellBorder([3000,500,500,500,500])
            fmt_prr = self.setCellBorder([1000,2300,200,1000,500,500,500])
            fmt_small = self.setCellBorder([500,2000,500,500,500,500,500,500])
            fmt_tiny = self.setCellBorder([4000,500,500])
            fmt_tiny_sw = self.setCellBorder([3000,500,500,500,500])
        else:
            cr_parent= False
            line_empty_input = ["--","--","--","--","--","--","--"]
            line_empty = ["--","--","--","--","--","--","--","--"]
            header = ["Title","Reference","Synergy Name","Version","Type","Instance","Release","CR"]
            header_input = ["Title","Reference","Synergy Name","Version","Type","Instance","Release"]
            # software
            header_soft_sources = ["File Name","Version","Type","Instance","Release","CR"]
            header_prr = ["Name","Version","Release"]
            line_sw_eoc_empty = ["--","--","--","--","--"]
            line_cid_empty = ["--","--","--","--","--"]
            line_src_empty = ["--","--","--","--","--","--"]
            line_ccb_empty = ["--","--","--","--","--","--","--"]
            line_other_empty = ["--","--","--","--","--","--","--","--"]
            tbl_build = [header_soft_sources]
            fmt = self.setCellBorder([1000,2300,200,500,500,500,500,500])
            fmt_ccb = self.setCellBorder([1000,2300,200,500,500,500,500])
            fmt_cid = self.setCellBorder([1000,2300,200,500,500])
            fmt_src = self.setCellBorder([2500,500,500,500,500,500])
            fmt_build = self.setCellBorder([2500,500,500,500,500,500])
            fmt_prr = self.setCellBorder([4000,500,500])
            fmt_small = self.setCellBorder([500,2500,500,500,500,500,500])
            fmt_tiny = self.setCellBorder([4000,500,500])
            fmt_tiny_sw = self.setCellBorder([3000,500,500,500,500])
        line_empty_three_columns = ["--","--","--"]
        table_input_data = []
        table_peer_reviews = []
        table_verif = []
        table_exclude = []
        tableau_sources_finduse = []
        tbl_build_finduse = []
        # Split table of items with sources
        items_filter_src = [self.sources_filter]
        items_filter_build = [self.build_filter]
        items_filter = [self.input_data_filter,
                        self.peer_reviews_filter,
                        self.verif_filter,
                        self.exclude_filter]

        # Document part
        include_code = False
        if project_set_list != []:
            # Projects are available in GUI
            self.ihm.log("Use project set list to create CID for documents",False)
            # Project set in GUI
            list_projects = project_set_list #self.ihm.project_set_list
            # List of projects from GUI
            #release_text,baseline_text,project_text = self.getContext(list_projects,
            #                                                          cid_type)
        else:
            project = self.project
            # [self.release,self.baseline,self.project]]
            if Tool.isAttributeValid(project):
                find_sub_projects = True
                list_projects = [[self.release,self.baseline,project]]
                prj_name, prj_version = self.getProjectInfo(project)
                self.findSubProjects(prj_name,
                                     prj_version,
                                     list_projects,
                                     mute = True)
                #print "TBL",list_projects
                for sub_release,sub_baseline,sub_project in list_projects:
                    if project != sub_project:
                        self.ihm.log("Find sub project {:s}".format(sub_project))
            else:
                #Valid baseline ?
                if Tool.isAttributeValid(self.baseline):
                    list_projects = self.getProjectsInBaseline(self.baseline)
                else:
                    list_projects = [[self.release,"",""]]
                    # No project nor baseline
                    # Patch: Looking for only release
                    print "INCLUDE_CODE"
                    include_code = True
        release_text,baseline_text,project_text = self.getContext(list_projects,
                                                                  cid_type)

        tbl_plans = [header]
        tbl_life_cycle_data = [header]
        tbl_verif = [header]
        tbl_peer_reviews = [header_prr]

        tbl_src = [header_soft_sources]
        header = ["Ref", "Name", "Reference", "Version", "Description"]
        self.tbl_cid = [header]
        tbl_input_data = [header_input]
        dico_tags = {"part_number":self.part_number,
                     "eoc_id":"",
                     "checksum":self.checksum,
                     "hw_sw_compatibility":""}
        #print "Type CID",self.cid_type
        if cid_type == "HCMR_BOARD" or cid_type == "CID":
            # HCMR BOARD or ECMR
            self._clearDicofound()
            tbl_upper_doc = [header]
            self.tbl_sas.append(["R1","Design Assurance Guidance for AEH","DO-254/ED-80","April 19th 2000",""])
            self.tbl_sas.append(["R2","Guidelines for Development of Civil Aircraft and Systems","ARP-4754A/ED-79A","December 6th 2010",""])

            link_id = 3
            list_llr_document = []
            for release,baseline,project in list_projects:
                if  Tool.isAttributeValid(release) or Tool.isAttributeValid(baseline) or Tool.isAttributeValid(project):
                    self.ihm.log("Use release " + release,False)
                    self.ihm.log("Use baseline " + baseline,False)
                    self.ihm.log("Use project " + project,False)
                    # Patch
                    if project == "All":
                        project = ""
                    type_objects = self.list_type_doc
                    type_objects.extend(self.list_type_src)
                    type_objects.extend(self.list_type_prog)
                    output = self.getArticles(type_objects,
                                              release,
                                              baseline,
                                              project,
                                              source = False,
                                              recursive=False)
                    #print "list_type_doc",self.list_type_doc
                    #print "TEST HCI:",output
                    link_id = self.getBoardData(self.tableau_items,
                                                self.tbl_ccb,
                                                self.tbl_plans,
                                                self.tbl_sas,
                                                self.tbl_cid,
                                                output,
                                                link_id)
                    # finduse
                    l_table_input_data,l_table_peer_reviews,l_table_verif,l_table_exclude = self.getSpecificData(release,
                                                                                                                 baseline,
                                                                                                                 project,
                                                                                                                 items_filter,
                                                                                                                 False)
                    l_tbl_program_file = self.getSpecificBuild(release,
                                                                   baseline,
                                                                   project,
                                                                   filters=items_filter_build)
                    print "l_tbl_program_file",l_tbl_program_file
                    tbl_build_finduse.extend(l_tbl_program_file)
                    table_input_data.extend(l_table_input_data)
                    table_peer_reviews.extend(l_table_peer_reviews)
                    table_verif.extend(l_table_verif)
                    table_exclude.extend(l_table_exclude)
        else:
            list_llr_document = []
            # self.tableau_items array is filled by invoking
            #
            # - _getAllDocuments (class BuildDoc)
            # -     _getArticles (class Synergy)
            #
            table_life_cycle_data = []
            for tag in ("INPUT_DATA","CODE","TEST","SPEC","CCB"):
                if tag in self.dico_onw_user_cid_tags:
                    table_life_cycle_data[tag] = self.dico_onw_user_cid_tags[tag]
                else:
                    print "X:",tag
                    print "Y:",self.dico_onw_user_cid_tags
            for release,baseline,project in list_projects:
                if  Tool.isAttributeValid(release) or Tool.isAttributeValid(baseline) or Tool.isAttributeValid(project):
                    self.ihm.log("Use release " + release,False)
                    self.ihm.log("Use baseline " + baseline,False)
                    self.ihm.log("Use project " + project,False)

                    baseline_code_only = self.isCodeOnly(baseline)
                    project_code_only = self.isCodeOnly(project)

                    if not baseline_code_only and not project_code_only:
                        # baseline or project name begin with CODE
                        # populates self.tbl_plans
                        self._getAllDocuments(release,
                                              baseline,
                                              project)
                        # finduse
                        l_table_input_data,l_table_peer_reviews,l_table_verif,l_table_exclude = self.getSpecificData(release,
                                                                                                                     baseline,
                                                                                                                     project,
                                                                                                                     items_filter,
                                                                                                                     False)
                        table_input_data.extend(l_table_input_data)
                        table_peer_reviews.extend(l_table_peer_reviews)
                        #print "l_table_peer_reviews",l_table_peer_reviews
                        table_verif.extend(l_table_verif)
                        table_exclude.extend(l_table_exclude)
                        #print "l_table_exclude",l_table_exclude

                        if cid_type in ("SCI"):
                            #Input Data
                            if self._is_array(table_life_cycle_data["INPUT_DATA"]["keyword"]):
                                for keyword in table_life_cycle_data["INPUT_DATA"]["keyword"]:
                                    self.getObjectsPerFolder(keyword=keyword,
                                             project = project,
                                             baseline = baseline,
                                             release = release,
                                             list_tbl = table_life_cycle_data["INPUT_DATA"]["table"]
                                            )
                            else:
                                self.getObjectsPerFolder(keyword=table_life_cycle_data["INPUT_DATA"]["keyword"],
                                         project = project,
                                         baseline = baseline,
                                         release = release,
                                         list_tbl = table_life_cycle_data["INPUT_DATA"]["table"]
                                        )
                            #CCB Minutes
                            if self._is_array(table_life_cycle_data["CCB"]["keyword"]):
                                for keyword in table_life_cycle_data["CCB"]["keyword"]:
                                    self.getObjectsPerFolder(keyword=keyword,
                                             project = project,
                                             baseline = baseline,
                                             release = release,
                                             list_tbl = table_life_cycle_data["CCB"]["table"])
                            else:
                                self.getObjectsPerFolder(keyword=table_life_cycle_data["CCB"]["keyword"],
                                         project = project,
                                         baseline = baseline,
                                         release = release,
                                         list_tbl = table_life_cycle_data["CCB"]["table"])
                            # Specifications
                            if self._is_array(table_life_cycle_data["SPEC"]["keyword"]):
                                for keyword in table_life_cycle_data["SPEC"]["keyword"]:
                                    print "keyword",keyword
                                    self.getObjectsPerFolder(keyword=keyword,
                                         project = project,
                                         baseline = baseline,
                                         release = release,
                                         list_tbl = table_life_cycle_data["SPEC"]["table"],
                                         header = ["Reference","Synergy Name","Version","Type","Instance","Release","CR"],
                                         with_cr=True,
                                         cr_included=self.list_only_include_cr
                                        )
                            else:
                                self.getObjectsPerFolder(keyword=table_life_cycle_data["SPEC"]["keyword"],
                                         project = project,
                                         baseline = baseline,
                                         release = release,
                                         list_tbl = table_life_cycle_data["SPEC"]["table"],
                                         header = ["Reference","Synergy Name","Version","Type","Instance","Release","CR"],
                                         with_cr=True,
                                         cr_included=self.list_only_include_cr
                                        )
                            # Get LLR
                            design_keyword = "S[w|W]DD"
                            self.ihm.log("Looking for Low Level requirement in SwDD folder ...")
                            #self.ihm.defill()
                            self.getItemsInFolder(design_keyword,
                                                 project=project,
                                                 baseline=baseline,
                                                 release=release,
                                                 only_name=True,
                                                 #exclude=["SwDD_"],
                                                 with_extension=True,
                                                 mute=False,
                                                 recur=True,
                                                 converted_list=list_llr_document)




                    if baseline_code_only or project_code_only or include_code:
                        # Specific command for source code. TODO: To be optimized
                        self.display_attr = ' -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"' # %task_synopsis
                        # self.display_attr is used in _getAllSources
                        # _getAllSources populates self.tableau_src
                        # Source code
                        if Tool.isAttributeValid(project) and cid_type in ("SCI"):
                            self.getObjectsPerFolder(keyword=table_life_cycle_data["CODE"]["keyword"],
                                     project = project,
                                     baseline = baseline,
                                     release = release,
                                     list_tbl = table_life_cycle_data["CODE"]["table"],
                                     header = ["Synergy Name","Version","Type","Instance","Release","CR"],
                                     with_cr=True,
                                     code=True,
                                     cr_included=self.list_only_include_cr
                                    )
                            tableau_sources_finduse = table_life_cycle_data["CODE"]["table"]
                        else:
                            tableau_sources_finduse = []
                            self._getAllSources(release,
                                                baseline,
                                                project)

                        # _getAllProg populates self.tableau_prog, self.tbl_sw_outputs and self.tbl_sw_eoc methods
                        self._getAllProg(release,
                                         baseline,
                                         project)
                        if cid_type not in ("SCI"):
                            # TODO: Replace with self.getSpecificBuild(release,baseline,project,filters=["BIN"])
                            # Second chance to find sources in specific folder like SRC
                            l_table_sources = self.getSpecificData(release,
                                                                   baseline,
                                                                   project,
                                                                   filters=items_filter_src,
                                                                   source=True)
                            tableau_sources_finduse.extend(l_table_sources)
                        # For software get build script in specific folder BUILD
                        list_found_build_items = []
                        l_tbl_program_file = self.getSpecificBuild(release,
                                                                   baseline,
                                                                   project,
                                                                   filters=["BUILD"],
                                                                   list_found_items=list_found_build_items)
                        tbl_build_finduse.extend(l_tbl_program_file)
                        #print "tbl_build_finduse:",tbl_build_finduse
                        #print "list_found_build_items",list_found_build_items
                        list_found_items = []
                        l_tbl_bin_file = self.getSpecificBuild(release,
                                                                  baseline,
                                                                  project,
                                                                  filters=["BIN","EXE"],
                                                                  list_found_items=list_found_items)

                        eoc_filename = self.get_eoc_infos(list_found_items,dico_tags)

            if list_llr_document != []:
                for llr in list_llr_document:
                    self.ihm.log("Found LLR: {:s}".format(llr),display_gui=False)
                    #self.ihm.defill()
            else:
                    self.ihm.log("Found no LLR.",display_gui=False)
                    #self.ihm.defill()
        self.sortData(table_input_data=table_input_data,
                      table_verif=table_verif,
                      list_llr_document=list_llr_document,
                      table_peer_reviews=table_peer_reviews,
                      table_exclude=table_exclude,
                      tbl_build_finduse=tbl_build_finduse,
                      tableau_sources_finduse=tableau_sources_finduse,
                      tbl_input_data=tbl_input_data,
                      tbl_life_cycle_data=tbl_life_cycle_data,
                      tbl_plans=tbl_plans,
                      tbl_verif=tbl_verif,
                      tbl_src=tbl_src,
                      tbl_peer_reviews=tbl_peer_reviews,
                      tbl_build=tbl_build)

        # TODO: Split input data and life cycle data for board and hardware
        # TODO: Make 2 query for SACR and HCR

        # Manage Change Requests and Problem Reports
        self.ihm.log("Change Request query in progress...")
        ccb = CCB(self.ihm)

        dico_tableau_pr = {"all":[],
                           "open":[],
                           "closed":[]}

        ccb.getPR(dico_tableau_pr,
                  #self.detect, # derprecated
                  #self.target_release, # derprecated
                  #self.cr_type, # derprecated
                  cr_with_parent=cr_parent,
                  list_cr_type=list_cr_type,
                  list_cr_status=list_cr_status,
                  list_cr_doamin=list_cr_doamin)

        self.tbl_sas = self._removeDoublons(self.tbl_sas)
        self.tbl_seci = self._removeDoublons(self.tbl_seci)
        self.tbl_scod = self._removeDoublons(self.tbl_scod)
        self.tbl_sw_eoc = self._removeDoublons(self.tbl_sw_eoc)
        self.tbl_sw_outputs = self._removeDoublons(self.tbl_sw_outputs)
        self.tableau_prog = self._removeDoublons(self.tableau_prog)
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
        if len(self.tbl_scod) == 1:
            self.tbl_scod.append(line_other_empty)
        if len(self.tableau_prog) == 1:
            self.tableau_prog.append(line_empty)
        if len(self.tableau_src) == 1:
            self.tableau_src.append(line_empty)
        if len(self.tbl_sw_outputs) == 1:
            line_sw_output_empty = ["--","--","--","--","--"]
            self.tbl_sw_outputs.append(line_sw_output_empty)
        if len(self.tbl_sw_eoc) == 1:
            self.tbl_sw_eoc.append(line_sw_eoc_empty)
        if len(self.tbl_build) == 1:
            self.tbl_build.append(line_src_empty)
        if len(self.tbl_sources) == 1:
            self.tbl_sources.append(line_src_empty)
        if len(tbl_plans) == 1:
            tbl_plans.append(line_other_empty)
        if len(self.tbl_stds) == 1:
            self.tbl_stds.append(line_other_empty)
        if len(self.tbl_ccb) == 1:
            self.tbl_ccb.append(line_ccb_empty)
        if len(self.tbl_constraint_file) == 1:
            self.tbl_constraint_file.append(line_empty_three_columns)
        if len(tbl_input_data) == 1:
            tbl_input_data.append(line_empty_input)
        if len(self.tbl_verif) == 1:
            self.tbl_verif.append(line_empty)
        if len(self.tbl_items_filtered) == 1:
            self.tbl_items_filtered.append(line_empty)
        if len(self.tbl_cid) == 1:
            self.tbl_cid.append(line_cid_empty)

        # Prepare information to put instead of tags
        title,subject = self.getSubject(self.system,
                                         self.item,
                                         self.component,
                                         template_type)
        doc_type = self.getTypeDocDescription(template_type)

        author,item,database,aircraft,item_description,ci_identification,program = self._getInfo()

        # Replace some tags
        self.protocol_compat = "TDB"
        self.data_compat = "TDB"
        if self.revision == "":
            version = "1"
        else:
            version = self.revision
        # Patch new ECMR template
        tbl_input_data_new = []
        tbl_life_cycle_data_new = []
        tbl_verif_new = []
        tbl_plans_new = []
        tbl_peer_reviews_new = []

        if cid_type == "HCMR_BOARD" or cid_type == "CID":
            fmt_life_cycle_data = self.formatDocTable(tbl_life_cycle_data_new,
                                tbl_life_cycle_data)
            fmt_input_data = self.formatDocTable(tbl_input_data_new,
                                tbl_input_data)
            fmt_verif = self.formatDocTable(tbl_verif_new,
                                tbl_verif)
            fmt_plans = self.formatDocTable(tbl_plans_new,
                                tbl_plans)
            fmt_prr = self.formatDocTable(tbl_peer_reviews_new,
                                tbl_peer_reviews)

            list_tags = {
                        'TABLEITEMS':{'type':'tab','text':tbl_life_cycle_data_new,'fmt':fmt_life_cycle_data},
                        'TABLEINPUTDATA':{'type':'tab','text':tbl_input_data_new,'fmt':fmt_input_data},
                        'TABLEPEERREVIEWS':{'type':'tab','text':tbl_peer_reviews_new,'fmt':fmt_prr},
                        'TABLESOURCE':{'type':'tab','text':tbl_src,'fmt':fmt_src},
                        'TABLEBUILD':{'type':'tab','text':tbl_build,'fmt':fmt_build},
                        'TABLEEOC':{'type':'tab','text':self.tbl_sw_eoc,'fmt':fmt_tiny_sw},
                        'TABLEEOCID':{'type':'tab','text':self.tbl_sw_eoc,'fmt':fmt_tiny_sw},
                        'TABLEOUPUTS':{'type':'tab','text':self.tbl_sw_outputs,'fmt':fmt_tiny_sw},
                        'TABLEVERIF':{'type':'tab','text':tbl_verif_new,'fmt':fmt_verif},
                        'TABLEPLAN':{'type':'tab','text':tbl_plans_new,'fmt':fmt_plans},
                        #'TABLESTD':{'type':'tab','text':self.tbl_stds,'fmt':fmt},
                        #'TABLECCB':{'type':'tab','text':self.tbl_ccb,'fmt':fmt_ccb},
                        #'TABLESAS':{'type':'tab','text':self.tbl_sas,'fmt':fmt},
                        #'TABLESECI':{'type':'tab','text':self.tbl_seci,'fmt':fmt},
                        #'TABLESCOD':{'type':'tab','text':self.tbl_scod,'fmt':fmt},
                        'TABLECID':{'type':'tab','text':self.tbl_cid,'fmt':fmt_cid},
                        'TABLEPRS':{'type':'tab','text':dico_tableau_pr["all"],'fmt':fmt_small},
                        'TABLECLOSEPRS':{'type':'tab','text':dico_tableau_pr["closed"],'fmt':fmt_small},
                        'TABLEOPR':{'type':'tab','text':dico_tableau_pr["open"],'fmt':fmt_small},
                        'PROGRAMING_FILE':{'type':'tab','text':self.tbl_program_file,'fmt':fmt_tiny},
                        'SYNTHESIS_FILES':{'type':'tab','text':self.tbl_synthesis_file,'fmt':fmt_tiny},
                        'CONSTRAINT_FILES':{'type':'tab','text':self.tbl_constraint_file,'fmt':fmt_tiny}
                        }
        else:
            # Software
            tbl_life_cycle_data_new =  self._removeDoublons(tbl_life_cycle_data)
            tbl_input_data_new = self._removeDoublons(tbl_input_data)
            tbl_verif_new =  self._removeDoublons(tbl_verif)
            tbl_plans_new = self._removeDoublons(tbl_plans)
            tbl_peer_reviews_new = self._removeDoublons(tbl_peer_reviews)
            fmt_input_data = fmt
            fmt_life_cycle_data = fmt
            fmt_verif = fmt
            fmt_plans = fmt

            list_tags = {
                        'TABLEPEERREVIEWS':{'type':'tab','text':tbl_peer_reviews_new,'fmt':fmt_prr},
                        'TABLEBUILD':{'type':'tab','text':tbl_build,'fmt':fmt_build},
                        'TABLEEOC':{'type':'tab','text':self.tbl_sw_eoc,'fmt':fmt_tiny_sw},
                        'TABLEEOCID':{'type':'tab','text':self.tbl_sw_eoc,'fmt':fmt_tiny_sw},
                        'TABLEOUPUTS':{'type':'tab','text':self.tbl_sw_outputs,'fmt':fmt_tiny_sw},
                        'TABLEVERIF':{'type':'list','text':table_life_cycle_data["TEST"]["table"],'fmt':fmt_verif},
                        'TABLEPLAN':{'type':'tab','text':tbl_plans_new,'fmt':fmt_plans},
                        #'TABLESTD':{'type':'tab','text':self.tbl_stds,'fmt':fmt},
                        #'TABLESAS':{'type':'tab','text':self.tbl_sas,'fmt':fmt},
                        #'TABLESECI':{'type':'tab','text':self.tbl_seci,'fmt':fmt},
                        #'TABLESCOD':{'type':'tab','text':self.tbl_scod,'fmt':fmt},
                        'TABLECID':{'type':'tab','text':self.tbl_cid,'fmt':fmt_cid},
                        'TABLEPRS':{'type':'tab','text':dico_tableau_pr["all"],'fmt':fmt_small},
                        'TABLECLOSEPRS':{'type':'tab','text':dico_tableau_pr["closed"],'fmt':fmt_small},
                        'TABLEOPR':{'type':'tab','text':dico_tableau_pr["open"],'fmt':fmt_small},
                        'PROGRAMING_FILE':{'type':'tab','text':self.tbl_program_file,'fmt':fmt_tiny},
                        'SYNTHESIS_FILES':{'type':'tab','text':self.tbl_synthesis_file,'fmt':fmt_tiny},
                        'CONSTRAINT_FILES':{'type':'tab','text':self.tbl_constraint_file,'fmt':fmt_tiny}
                        }
            if table_life_cycle_data["INPUT_DATA"]["table"] != []:
                list_tags.update({'TABLEINPUTDATA':{'type':'list','text':table_life_cycle_data["INPUT_DATA"]["table"],'fmt':fmt_input_data}})
            else:
                list_tags.update({'TABLEINPUTDATA':{'type':'tab','text':tbl_input_data_new,'fmt':fmt_input_data}})
            if table_life_cycle_data["SPEC"]["table"] != []:
                list_tags.update({'TABLEITEMS':{'type':'list','text':table_life_cycle_data["SPEC"]["table"],'fmt':fmt_life_cycle_data}})
            else:
                list_tags.update({'TABLEITEMS':{'type':'tab','text':tbl_life_cycle_data_new,'fmt':fmt_life_cycle_data}})
            if table_life_cycle_data["CCB"]["table"] != []:
                list_tags.update({'CCB':{'type':'list','text':table_life_cycle_data["CCB"]["table"],'fmt':fmt_ccb}})
            else:
                list_tags.update({'CCB':{'type':'tab','text':self.tbl_ccb,'fmt':fmt_ccb}})
            if table_life_cycle_data["CODE"]["table"] != []:
                list_tags.update({'TABLESOURCE':{'type':'list','text':table_life_cycle_data["CODE"]["table"],'fmt':fmt_src}})
            else:
                list_tags.update({'TABLESOURCE':{'type':'tab','text':tbl_src,'fmt':fmt_src}})
            #print "TEST1",self.tbl_ccb
            #print 'TEST2',fmt_ccb
        if eoc_filename is not None:
            self.ihm.displayEOC_Info((dico_tags["hw_sw_compatibility"],
                                  dico_tags["part_number"],
                                  dico_tags["checksum"],dico_tags["failed"]))
            if dico_tags["part_number"] == self.part_number:
                self.ihm.log("PN found in the {:s} EOC matches the PN given.".format(eoc_filename),color="white")
            else:
                self.ihm.log("Warning: PN found in the {:s} EOC mismatches the given PN.".format(eoc_filename),color="red")
            if dico_tags["checksum"] == self.checksum:
                self.ihm.log("Checksum found in the {:s} EOC matches the given checksum.".format(eoc_filename),color="white")
            else:
                self.ihm.log("Warning: Checksum found in the {:s} EOC mismatches the given checksum.".format(eoc_filename),color="red")
        #if self.part_number != "":
        #    dico_tags["part_number"] = self.part_number
        #if self.checksum != "":
        #    dico_tags["checksum"] = self.checksum # Ex: 0x6b62
        list_tags.update({
                    'SYSTEM':{'type':'str','text':self.system,'fmt':{}},
                    'SUBJECT':{'type':'str','text':subject,'fmt':{}},
                    'DOCID':{'type':'str','text':"Generated by doCID version {:s}".format(VERSION),'fmt':{}},
                    'TYPE':{'type':'str','text':doc_type,'fmt':{}},
                    'TITLE':{'type':'str','text':title,'fmt':{}},
                    'CI_ID':{'type':'str','text':ci_identification,'fmt':{}},
                    'REFERENCE':{'type':'str','text':self.reference,'fmt':{}},
                    'ISSUE':{'type':'str','text':version,'fmt':{}},
                    'ITEM':{'type':'str','text':item,'fmt':{}},
                    'COMPONENT':{'type':'str','text':self.component,'fmt':{}},
                    'ITEM_DESCRIPTION':{'type':'str','text':item_description,'fmt':{}},
                    'DATE':{'type':'str','text':time.strftime("%d %b %Y", time.localtime()),'fmt':{}},
                    'PROJECT':{'type':'str','text':project_text,'fmt':{}},
                    'RELEASE':{'type':'str','text':release_text,'fmt':{}},
                    'PREVIOUS_BASELINE':{'type':'str','text':self.previous_baseline,'fmt':{}},
                    'BASELINE':{'type':'str','text':baseline_text,'fmt':{}},
                    'WRITER':{'type':'str','text':author,'fmt':{}},
                    'PART_NUMBER':{'type':'str','text':dico_tags["part_number"],'fmt':{}},
                    'BOARD_PART_NUMBER':{'type':'str','text':self.board_part_number,'fmt':{}},
                    'MAIN_BOARD_ PART_NUMBER':{'type':'str','text':"",'fmt':{}},
                    'MEZA_BOARD_ PART_NUMBER':{'type':'str','text':"",'fmt':{}},
                    'TGT_REL': {'type': 'str', 'text': self.target_release, 'fmt': {}},
                    'CHECKSUM':{'type':'str','text':dico_tags["checksum"],'fmt':{}},
                    'DATABASE':{'type':'str','text':database,'fmt':{}},
                    'PROGRAM':{'type':'str','text':program,'fmt':{}},
                    'FUNCCHG':{'type':'par','text':self.func_chg,'fmt':{}},
                    'OPCHG':{'type':'par','text':self.oper_chg,'fmt':{}},
                    'PROTOCOL_COMPAT':{'type':'str','text':self.protocol_interface_index,'fmt':{}},
                    'DATA_COMPAT':{'type':'str','text':self.data_interface_index,'fmt':{}},
                    'HW_COMPAT':{'type':'str','text':dico_tags["hw_sw_compatibility"],'fmt':{}},
                    'TOP_PLD_PRJ':{'type':'str','text':"",'fmt':{}}})
        for dico in self.dico_own_user_cid_tags["Documents"]:
            #print "X:",dico
            tag = dico["tag"]
            if tag in self.tbl_user:
                #tbl_cleanup = self._removeDoublons(self.tbl_user[tag])
                list_tags.update({tag:{'type':'tab','text':self.tbl_user[tag],'fmt':fmt}})
        for x,y in self.tbl_user.iteritems():
            print "C:",x,y
        if u'SAS' not in self.tbl_user:
            list_tags.update({'SAS':{'type':'tab','text':self.tbl_sas,'fmt':fmt}})
        if header_image:
            image_name = self.get_image(self.aircraft)
        else:
            image_name = None
        self.ihm.docx_filename = docx_filename
        for x,y in list_tags.iteritems():
            print "TAG:",x,y
        self.docx_filename,exception = self._createDico2Word(list_tags,
                                                             template_name,
                                                             docx_filename,
                                                             image_name)

        dico_timestamp["end_script"] = datetime.now()
        duree_execution_script = dico_timestamp["end_script"] - dico_timestamp["begin_script"]
        self.ihm.log("Execution time for script: {:d} seconds".format(duree_execution_script.seconds))
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

if __name__ == '__main__':
    classe = BuildDoc(session_started=True)
    output = ["SW_PLAN/01;ECE_BD700_DT3349_PSSA.pdf;3;135;<void>;pdf;SW_PLAN;1",
              "SW_ACENM/01;SCOD_ACENM_ET3314.pdf;1.1;5724;<void>;pdf;SW_ACENM;1"]
    classe._parseSynergyOutput(output)
    exit()
    tbl_doc_found=[]
    for line in output:
            line = re.sub(r"<void>",r"",line)
            print "Found doc: ",line
            # release;filename;tasks;?;type;project;instance
            m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
            if m:
                for dico in classe.dico_own_user_cid_tags["Documents"]:
                    keyword = dico["keyword"]
                    description = dico["description"]
                    result = classe._createTblUserDocument(m,keyword,description,tbl_doc_found)
    print "tbl_doc_found",tbl_doc_found
    exit()
    print "TEST",classe.dico_onw_user_cid_tags
    for x in classe.dico_onw_user_cid_tags:
        print "X",x
