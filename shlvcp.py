#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
import warnings
try:
    import win32api
    import win32com.client as win32
    import pythoncom
    from win32com.client import constants
except ImportError as e:
    warnings.warn(str(e))
import pkgutil
import xml.etree.ElementTree as ET
from tool import Tool
from excel import Excel,Style
import re
from conf.check_conf import Conf
from os.path import join
import sys
import os
from math import floor
import time

class Word():
    def __init__(self):
        self.doc = None
        try:
            pythoncom.CoInitialize()
            if "nogencache" not in self.__dict__:
                # from http://www.py2exe.org/index.cgi/UsingEnsureDispatch
                if win32.gencache.is_readonly == True:
                    #allow gencache to create the cached wrapper objects
                    win32.gencache.is_readonly = False
                    # under p2exe the call in gencache to __init__() does not happen
                    # so we use Rebuild() to force the creation of the gen_py folder
                    win32.gencache.Rebuild()
                    # NB You must ensure that the python...\win32com.client.gen_py dir does not exist
                    # to allow creation of the cache in %temp%
            else:
                print "no gencache"
            self.word = win32.gencache.EnsureDispatch('Word.Application')
            self.word.Visible = False
            self.word.DisplayAlerts = False
        except NameError as exception:
            self.word = None
            warnings.warn(str(exception))

    def find(self,sel,style=""):
        self.current_find = sel.Find
        self.current_find.ClearFormatting()
        #self.current_find.Wrap = constants.wdFindContinue
        self.current_find.Style = style
        self.current_find.Forward = True
        self.current_find.Execute()
        found = self.current_find.Found
        #self.current_find.ClearFormatting()
        return found

    def find_set(self,sel,style=""):
        self.current_find = sel.Find
        self.current_find.ClearFormatting()
        #self.current_find.Wrap = constants.wdFindContinue
        self.current_find.Style = style
        self.current_find.Forward = True

    def set_style(self,style):
        self.current_find.Style = style

    def find_execute(self):
        try:
            self.current_find.Execute()
            found = self.current_find.Found
        except Exception as e:
            found = False
            print e
        return found

    def set_doc(self,doc):
        self.doc = doc

    def get_nb_pages(self):
        nb_pages = self.doc.ActiveWindow.Selection.Information(constants.wdNumberOfPagesInDocument)
        return nb_pages

class Shlvcp(Word,Excel,Conf):
    def __init__(self,**kwargs):
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
        if "callback" in self.__dict__:
            self.callback = self.__dict__["callback"]
        else:
            self.callback = False
        self.func_ptr = self.load
        self.log_handler = None
        self.active_dbg = True
        self.tbl_req_vs_section = dict()
        self.tbl_file_llr_wo_del = dict()
        self.tbl_file_llr= dict()
        self.tbl_file_nb_llr = dict()
        self.tbl_file_nb_pages = dict()
        self.tbl_file_dir = dict()
        self.stack = []
        self.dico_proc = dict()
        self.dico_errors = dict()
        self.dico_warnings = dict()
        self.tbl_list_llr = dict()
        self.dico_debug = dict()
        self.list_proc = []
        self.nb_reqs = 0
        self.nb_reqs_in_file = 0
        self.nb_reqs_modified = 0
        self.current_folder = ""
        self.nb_debug = 0
        self.nb_deleted_req = 0
        self.nb_derived_req = 0
        self.dico_tc_vs_proc = dict()
        self.doc_version = 0
        self.depth = 0
        self.enable_check_bproc =False
        Word.__init__(self)

    @staticmethod
    def getAtribute(dico,attr):
        if attr in dico:
            value = Tool.removeNonAscii(dico[attr])
            # Remove tabulation
            value = re.sub(r"\t",r"",value)
        else:
            value = "None"
        return value

    def invert(self):
        """
        Get requirement versus file
        ex:
        Input:
            {'SSCS_ESSNESS_ET2788_S-6D1': [u'SSCS_ESSNESS_0001', etc.
        Output:
            {'SSCS_ESSNESS_9020': ['SSCS_ESSNESS_ET2788_S-6D1'], 'SSCS_ESSNESS_9141': ['SSCS_ESSNESS_ET2788_S-6D1'],
        :return:
        """
        self.list_llr_vs_file = Tool._invert_dol(self.tbl_file_llr)

    def extract(self,
                dirname="",
                type=("SWRD","PLDRD"),
                component="SW_ENM",
                log_handler=None,
                enable_check_bproc=False):
        """
        This function call listDir to parse each files in folder and collect all requirements with their attributes.
        self.list_upper_req contains all upper requirements reference
        :param dirname: directory where to search files
        :param type: type of specification document
        :param component: came form IHM
        :return:
        """
        # TODO: Create xlsx file instead of csv file
        if log_handler is not None:
            self.log_handler = log_handler
        # Recursive function to parse directory to find documents
        # Parse document to extract requirements or test cases
        #self.listDir(dirname,
        #             type,
        #             component)
        self.invert()
        # Summary
        type_tag = "test cases"
        derived = "forward"
        verify = "verified"
        nb_proc_linked = 0
        for tc,dico_attributes in self.tbl_list_llr.iteritems():
            if "proc" in dico_attributes:
                list_proc = dico_attributes["proc"]
                nb_proc_linked += len(list_proc)
                self.dico_tc_vs_proc[tc]=list_proc
        #for tc,tps in self.dico_tc_vs_proc.iteritems():
        #    nb_proc_linked += len(self.dico_tc_vs_proc[tc])
        nb_proc_in_folder = len(self.list_proc)
        # revert dico
        dico_proc_vs_tc = Tool._invert_dol(self.dico_tc_vs_proc)
        self.log("Found {:d} procedures in document body.".format(nb_proc_linked),gui_display=True)
        self.log("Found {:d} procedures in folder.".format(nb_proc_in_folder),gui_display=True)
        if enable_check_bproc:
            for procedure in dico_proc_vs_tc:
                if procedure not in self.list_proc:
                    self.log("Procedure {:s} found in SHLVCP but not in procedures folder.".format(procedure),gui_display=True)
            for procedure in self.list_proc:
                if procedure not in dico_proc_vs_tc:
                    self.log("Procedure {:s} found in procedures folder but not in SHLVCP.".format(procedure),gui_display=True)
            print "Procedures in folder:"
            for x in self.list_proc:
                print "Folder:",x
        print "Procedures in SHLVCP:"
        for x in dico_proc_vs_tc:
            print "SHLVCP:",x

        #union = set(dico_proc_vs_tc) & set(self.list_proc)
        #exclusion = set(dico_proc_vs_tc) ^ set(self.list_proc)
        #print "UNION",union
        #for x in exclusion:
        #    print "EXCLUSION:",x

        #nb_upper_req = 0
        self.log("Found {:d} {:s} in document body.".format(self.nb_reqs,type_tag),gui_display=True)
        self.log("Found {:d} {:s} modified in document body.".format(self.nb_reqs_modified,type_tag),gui_display=True)
        self.log("Found {:d} {:s} {:s} in document body.".format(self.nb_derived_req,derived,type_tag),gui_display=True)
        self.log("Found {:d} deleted {:s} in document body.".format(self.nb_deleted_req,type_tag),gui_display=True)
        #self.log("Found {:d} {:s} requirements in document body.".format(nb_upper_req,verify),gui_display=True)

        for list,error in self.dico_errors.iteritems():
            rule_tag = list[1]
            self.log("ERROR: {:s}: {:s}".format(rule_tag,error[0]),gui_display=True)
        self.log("{:d} warnings found in document.".format(len(self.dico_warnings)),gui_display=True)
        for list,error in self.dico_warnings.iteritems():
            rule_tag = list[1]
            self.log("WARNING: {:s}: {:s}".format(rule_tag,error[0]),gui_display=True)
        filename = "test_cases_%d.xlsx" % floor(time.time())
        filename_tc_vs_tp = "test_cases_vs_procedures_%d.xlsx" % floor(time.time())
        file_check_filename = "test_cases_file_check_%d.csv" % floor(time.time())
        attr_check_filename = "test_cases_attr_check_%d.csv" % floor(time.time())
        with open(join("result",file_check_filename), 'w') as of:
            of.write("{:s};{:s};{:s};{:s}\n".format("Dir","Files","nb reqs","pages"))
            for file in self.tbl_file_llr:
                # dir not sorted here !
                dir = self.tbl_file_dir[file]
                of.write("{:s};{:s};{:};{:}\n".format(dir,                    # Folder
                                                   file,                        # File
                                                   self.tbl_file_nb_llr[file],  # nb requirements
                                                   self.tbl_file_nb_pages[file]                           # nb pages
                                                  )
                        )
                #for reqs in llr.tbl_file_llr[file]:
                #    of.write("   " + reqs + "\n")

        with open(join("result",attr_check_filename), 'w') as of:
            ws,wb = self.createWorkBook("Test Cases",["Test cases","Nb links","Nb used I/O"])
            ws2,wb2 = self.createWorkBook("Test Cases vs Procedures",["Test cases","Procedures"])
            of.write("{:s};{:s};{:s};{:s};{:s};{:s};{:s};{:s};{:s}\n".format("File","Req tag","Objective","Verifies","Rationale","Forward","Issue","Status","Used IO"))
            # get all test cases from self.tbl_list_llr
            row = 10
            row_proc = 10
            for req,value in self.tbl_list_llr.iteritems():
                #list_verify,list_constraints = self.getLLR_Trace(value,keyword="verify")
                # File,Req,Refer_to,Constraint,Derived,Rationale,Additional
                req_txt = str(req)
                if req_txt in self.list_llr_vs_file:
                    file = self.list_llr_vs_file[req_txt][0]
                else:
                    file = "None"

                rationale = self.getAtribute(value,"rationale")
                forward = self.getAtribute(value,"forward")
                issue = self.getAtribute(value,"issue")
                status = self.getAtribute(value,"status")
                objective = self.getAtribute(value,"objective")
                if "used_io" in value:
                    used_io = ",".join(value["used_io"])
                else:
                    used_io = ""
                if not re.search(r'DELETED',status):
                    nb_link = len(value["verify"])
                    if "used_io" in value:
                        nb_used_io = len(value["used_io"])
                    else:
                        nb_used_io = 0
                    line = (req_txt,nb_link,nb_used_io)
                    for col_idx in range(1,len(line)+1):
                        Style.setCell(ws,line,row,col_idx)
                    row += 1
                    for verify in value["verify"]:
                        of.write("{:s};{:s};{:s};{:s};{:s};{:s};{:s};{:s};{:s}\n".format(file,
                                                                                req,
                                                                                objective,
                                                                                verify,
                                                                                rationale,
                                                                                forward,
                                                                                issue,
                                                                                status,
                                                                                used_io
                                                                                ))
                    if "proc" in value:
                        for proc in value["proc"]:
                            line = (req_txt,proc)
                            for col_idx in range(1,len(line)+1):
                                Style.setCell(ws2,line,row_proc,col_idx)
                            row_proc += 1

            wb.save(join("result",filename))
            wb2.save(join("result",filename_tc_vs_tp))

        return attr_check_filename,file_check_filename

    def listDir(self):
        """
        Recursive function to find files in directories.
        Treatment for Excel and Word file is different
        :return:
        """
        self.depth += 1
        new_concat_dirname = self.basename
        for dir in self.stack:
            new_concat_dirname = join(new_concat_dirname,dir)
            if sys.platform.startswith('win32'):
                new_concat_dirname = "{:s}\\".format(new_concat_dirname)
            else:
                new_concat_dirname = "{:s}/".format(new_concat_dirname)

        try:
            isdir = os.path.isdir(new_concat_dirname)
            if isdir:
                list_dir = os.listdir(new_concat_dirname)
            else:
                list_dir = [new_concat_dirname]
        except OSError as e:
            try:
                self.log("{:s}".format(str(e)))
            except UnicodeEncodeError as exception:
                pass
            list_dir = []

        for found_dir in list_dir:
            path_dir = os.path.join(new_concat_dirname, found_dir)
            isdir = os.path.isdir(path_dir)
            if isdir:
                self.stack.append(found_dir)
                self.listDir()
                self.stack.pop()
            else:
                void = re.sub(r"(~\$)(.*)\.(.*)",r"\1",found_dir)
                extension = Shlvcp.getFileExt(found_dir)
                type = Tool.getType(found_dir)
                if "doc" in extension and void != "~$":
                    self.log("Parse {:s}".format(found_dir),gui_display=True)
                    filename = join(new_concat_dirname,found_dir)
                    self.func_ptr(filename)
                elif extension in ("bproc") and void != "~$":
                    self.log("Parse {:s} type {:s}".format(found_dir,type),gui_display=True)
                    filename = join(new_concat_dirname,found_dir)
                    if self.enable_check_bproc:
                        dico = self.readProc(filename)
                        if not dico:
                            self.log("Reject {:s} as a generic".format(found_dir),gui_display=True)
                    else:
                        print "Exclude BPROC procedure:",filename
                else:
                    self.log("Discard {:s}".format(found_dir),gui_display=True)
                    # Wrong Word format, only openxml
                    text = "Unexpected format for {:s}, only ('doc','docx','docm','bproc') accepted".format(found_dir)
                    self.log(text)
        self.depth -= 1

    def openLog(self,type="specification"):
        self.log_filename = "check_{:s}_{:d}.txt".format(type,int(floor(time.time())))
        self.log_handler = open(join("result",self.log_filename), 'w')

    def closeLog(self):
        # Close opened file
        if self.log_handler is not None:
            self.log_handler.close()

    def log(self,
            text,
            error=False,
            gui_display=True):
        if self.log_handler is not None:
            self.log_handler.write(text + "\n")
        else:
            print text
        if self.callback and gui_display:
            if error:
                self.callback(text,color = "yellow",display_gui=gui_display)
            else:
                self.callback(text,display_gui=gui_display)
        else:
            pass

    def debug(self,text):
        if self.active_dbg:
            self.log(text)

    @staticmethod
    def findGenericBproc(filename):
        m = re.match(r'^GEN_SEQ.*\.bproc$',filename)
        print "M:",m
        return m

    def readProc(self,filename):
        dico = dict()
        m = Shlvcp.findGenericBproc(filename)
        if not m:
            # No generic procedures
            small_filename = Tool.getFileNameAlone(filename)
            self.list_proc.append(small_filename)
            tree = ET.parse(filename)
            root = tree.getroot()
            execution_info = root.find('ExecutionInfo')
            dico= dict()
            for element in execution_info:
                dico[element.tag]=element.text
            print "{:s} {:s} {:s}".format(dico["Tester"],dico["SanctionAuto"],dico["ExecutionDate"])
            self.dico_proc[small_filename] = dico
        return dico

    @staticmethod
    def getDocVersion(doc_name):
        m = re.match(r'.*-([0-9]{1,2})\..*',doc_name)
        if m:
            version = m.group(1)
        else:
            version = False
        return version

    @staticmethod
    def getVersion(issue):
        version = re.sub(r"(.*)\.(.*)", r"\1", str(issue))
        return version

    @staticmethod
    def getFileName(filename):
        doc_name = re.sub(r"^.*(\/|\\)(.*)\.([a-zA-Z]){1,6}$", r"\2", filename)
        return doc_name

    @staticmethod
    def getFileExt(filename):
        extension = re.sub(r"(.*)\.(.*)",r"\2",filename)
        return extension

    def load(self,
             full_filename,
             type = ("SHLVCP",)):

        pythoncom_loader = pkgutil.find_loader('pythoncom')
        found_pythoncom = pythoncom_loader is not None
        if found_pythoncom:
            start_area_req = 0
            end_area_req = 0
            try :
                print "FILE:",full_filename
                doc = self.word.Documents.Open(full_filename)
                doc.TrackFormatting = False
                doc.TrackMoves = False
                doc.TrackRevisions = False
                doc.ScreenUpdating  = False
                # Active Show All
                self.word.ActiveWindow.ActivePane.View.ShowAll = True
                doc.TrackFormatting = False
                doc.TrackMoves = False
                doc.TrackRevisions = False
                doc.ScreenUpdating  = False

                self.set_doc(doc)
                # TODO: Parse list of modifications

                # Looking for "Title 4" for SwRD
                tbl_req_tag = []
                tbl_req_tag_wo_del = []

                filename = Shlvcp.getFileName(full_filename)
                # get major version of the document
                doc_version = self.getDocVersion(filename)
                if doc_version:
                    self.doc_version = doc_version
                    self.log("Major version found: {:s}".format(self.doc_version),gui_display=True)
                start_area_req,end_area_req = self.getReqInfos(new_tab_req=self.tbl_req_vs_section,
                                                                 type=type,
                                                                 tbl_req_tag=tbl_req_tag,
                                                                 tbl_req_tag_wo_del=tbl_req_tag_wo_del,
                                                                 table_enabled=False,
                                                                 filename=filename)

                ReqPart = doc.Range(start_area_req,end_area_req)
                txt = Tool.replaceNonASCII(ReqPart.Text)
                self.tbl_file_llr[filename] = tbl_req_tag
                self.tbl_file_llr_wo_del[filename] = tbl_req_tag_wo_del
                self.tbl_file_nb_llr[filename] = self.nb_reqs_in_file
                self.tbl_file_nb_pages[filename] = self.get_nb_pages
                self.tbl_file_dir[filename] = "/".join(self.stack)

            except pythoncom.com_error as e:
                txt = ""
                print e
                print "Treat:",start_area_req,end_area_req

            try:
                doc.Close()
                del doc
            except pythoncom.com_error as e:
                print "Error in closing Word document:",e
            except UnboundLocalError as e:
                print e
        return True

    def getSplitAttribute(self,str_refer,type="SWRD_[\w-]*"):
        # Attention [ est inclus dans .* mais pas dans \w c'est pour ça que ça marche pour HSID mais pas pour SWRD
        list = re.findall(r'\[({:s})\]'.format(type), str_refer)
        return list

    def extractAttribute(self,
                         key,
                         line,
                         error_attributes,
                         warning_attributes):

        attrs = self.dico_attributes[key]
        if Tool._is_array(attrs):
            for attr in attrs:
                attr_value_found = self.matchAttribute(line,
                                                       attr,
                                                       error_attributes,
                                                       warning_attributes)
                if attr_value_found:
                    break
        else:
            attr_value_found = self.matchAttribute(line,
                                                   attrs,
                                                   error_attributes,
                                                   warning_attributes)
        if attr_value_found:
            text = Tool.replaceNonASCII(attr_value_found,html=True)
        else:
            text = ""
        return text

    def parse_body_attr(self,
                        start_delimiter,    # Requirement ID
                        start,              # Range.Start
                        end,                # Range.End
                        list_attributes = {}):
        """

        :param start_delimiter:
        :param start:
        :param end:
        :param list_attributes:
        :return:
        """
        error_attributes = []
        warning_attributes = []
        #print "START_TAG",start_delimiter,start,end

        for style,key in self.dico_styles.iteritems():
            if key in self.dico_types["SHLVCP"]:
                try:
                    # New Style to be found
                    # range must be reevaluated at each iteration
                    range = self.doc.Range(start,end)
                    index = 0
                    if key == "body":
                        found = True
                    else:
                        found = self.find(range,style=style)

                    while found and index < 50:
                        index += 1
                        line = range.Text
                        if key == "issue":
                            # First attribute
                            parsed_line = self.extractAttribute(key,line,error_attributes,warning_attributes)
                            list_attributes["issue"] = parsed_line
                            if Shlvcp.getVersion(list_attributes["issue"]) == self.doc_version:
                                self.nb_reqs_modified += 1
                            first_attribute_start = range.Start
                            list_attributes["body"] = self.doc.Range(start,first_attribute_start).Text
                            list_procedures = self.getProcInBody(list_attributes["body"])
                            if list_procedures:
                                list_attributes["proc"] = list_procedures
                            objective = self.getObjectiveInBody(list_attributes["body"])
                            if objective:
                                list_attributes["objective"] = re.sub(r"\r","",objective)
                            break
                        elif key == "verify":
                            list_attributes["verify"] = self.getSplitAttribute(line,type="[A-Z]*_[\w-]*")
                            if self.active_dbg:
                                    self.log("Requirement {:s}: Found attribute {:s}:{:s}".format(start_delimiter,
                                                                                                 style,
                                                                                                 list_attributes["verify"]),
                                                                                                 gui_display=True)
                            break
                        elif key == "additional":
                            parsed_line = self.extractAttribute(key,line,error_attributes,warning_attributes)
                            list_attributes["additional"] = parsed_line
                            used_io = self.getUsedIOInBOdy(list_attributes["additional"])
                            if used_io:
                                list_used_io = self.getSplitAttribute(line,type="[A-Z]*_[\w-]*")
                                list_attributes["used_io"] = list_used_io
                                if self.active_dbg:
                                    self.log("Requirement {:s}: Found attribute {:s}:{:s}".format(start_delimiter,
                                                                                                 style,
                                                                                                 list_attributes["used_io"]),
                                                                                                 gui_display=True)
                            break
                        elif key == "body":
                            break
                        else:
                            # remove not related key for SHLVCP
                            attrs = self.dico_attributes[key]
                            if Tool._is_array(attrs):
                                for attr in attrs:
                                    attr_value_found = self.matchAttribute(line,
                                                                           attr,
                                                                           error_attributes,
                                                                           warning_attributes)
                                    if attr_value_found:
                                        break
                            else:
                                attr_value_found = self.matchAttribute(line,
                                                                       attrs,
                                                                       error_attributes,
                                                                       warning_attributes)
                            if range.End == end:
                                # No more attribute with Style is to be found, leave
                                break
                            range = self.doc.Range(range.End,end)
                            # Remove carriage return
                            if attr_value_found:
                                text = Tool.replaceNonASCII(attr_value_found,html=True)
                                if self.active_dbg:
                                    self.log("Requirement {:s}: Found attribute {:s}:{:s}".format(start_delimiter,
                                                                                                 style,
                                                                                                 text),
                                                                                                 gui_display=True)
                                if key not in list_attributes:
                                    list_attributes[key] = text
                                else:
                                    list_attributes[key] += text

                            found = self.find_execute()
                except pythoncom.com_error as exception:
                    print exception
                    print "KEY/Style",key,style

    def matchEndLLR(self,data):
        error_attributes = []
        warning_attributes = []
        debug_attributes = []
        attrs = self.dico_attributes["end"]
        #print "DEBUG DATA",data
        #print "DEBUG ATTRS:",attrs
        if Tool._is_array(attrs):
            for attr in attrs:
                attr_value_found = self.matchAttribute(data,
                                                       attr,
                                                       error_attributes,
                                                       warning_attributes)
                #print "DEBUG attr_value_found:",attr_value_found
                if attr_value_found:
                    break
        else:
            attr_value_found = self.matchAttribute(data,
                                                   attrs,
                                                   error_attributes,
                                                   warning_attributes,
                                                   debug_attributes)
        if attr_value_found:
            end_delimiter =attr_value_found
            #self.debug("End delimiter found:{:s}".format(Tool.removeNonAscii(end_delimiter)))
            result = True
        else:
            result = False
        return result

    def getProcInBody(self,data):
        #m = re.match(r'^\s*(.*)', data)
        # Search for test procedures
        plain_data = Tool.removeNonAscii(data)
        list_found_procedures = re.findall(r'SHLVCP_[A-Z_]*_[0-9]{4}_PROC_?[0-9]{0,3}\.bproc',plain_data)
        #self.debug("Body found:{:s}".format(plain_data))
        #self.debug("End Body found")
        return list_found_procedures

    def getObjectiveInBody(self,data):
        plain_data = Tool.removeNonAscii(data)
        m = re.search(r'Objective:(.*)Test diagram',plain_data)
        if m:
            objective =m.group(1)
        else:
            objective = False
        return objective

    def getUsedIOInBOdy(self,data):
        plain_data = Tool.removeNonAscii(data)
        m = re.search(r'Used I/O:(.*)',plain_data)
        if m:
            used_io =m.group(1)
        else:
            used_io = False
        return used_io

    def matchBegin(self,
                   data,
                   type):
       # print "DEBUG DATA:",data
        if data not in (None,0):
            # Regex
            # \s : Matches any whitespace character like a blank space, tab, and the like.
            m = re.match(r'^\s*\[({:s}.*)\]'.format(type), data)
            if m:
                start_delimiter = m.group(1)
                #print "DEBUG start_delimiter:",start_delimiter
                self.debug("Start delimiter found:{:s} beginning with {:s}".format(Tool.removeNonAscii(start_delimiter),type))
                result = start_delimiter
            else:
                result = False
        else:
            result = False
        return result

    def testStatusDeleted(self,start_delimiter,list_attributes):
        # Test status attribute
        if "status" in list_attributes:
            if re.search("DELETED", list_attributes["status"]):
                self.dico_debug["status","S_3",self.current_folder,start_delimiter,""] = \
                    ["The requirement {:s} is tagged DELETED in order to prevent ID reuse.".format(start_delimiter)]
                self.nb_debug +=1
                #tbl_req_tag_wo_del.remove(start_delimiter)
                # Deleted found
                self.nb_deleted_req += 1
                return True
            else:
                self.nb_reqs +=1
                self.nb_reqs_in_file +=1
                return False
        else:
            print "Missing status"
            return  False

    def matchAttribute(self,
                       data,
                       attr,
                       error_attributes=[],
                       warning_attributes=[],
                       debug_attributes=[]):
        #print "Atribute selected:",attr,
        m = re.match("^\s*" + attr + "\s*(.*)", data)
        if m:
            attr_value_found = m.group(1)
            self.debug("Attributes found {:s} {:s}".format(attr,Tool.removeNonAscii(attr_value_found)))
            #print "Attributes found ",attr,attr_value_found
            # test semi colon presence
            m = re.search(';', attr_value_found)
            if m:
                value_filtered = re.sub(r";",r",",attr_value_found)
                debug_attributes.append("Unexpected semi-colon found in \"{:s}\" attribute.".format(attr))
                #print "ERROR",error
            else:
                value_filtered = attr_value_found
            # test missing missing comma in "Refer to" attribute
            if attr == "Refers to:" or attr == "Constraint by:":
                char = {r'\t':'',r' ':''}
                for before, after in char.iteritems():
                    value_filtered = re.sub(before,after,value_filtered)
                #print "TEST:",attr_value_found
                # Find double brackets
                m = re.search(r'\]\]', value_filtered)
                if m:
                    error_attributes.append("Double brackets in {:s} attribute.".format(attr))
                    value_filtered = re.sub(r"\]\]",r"]",value_filtered)
                m = re.search(r'\[\[', value_filtered)
                if m:
                    error_attributes.append("Double brackets in  {:s} attribute.".format(attr))
                    value_filtered = re.sub(r"\[\[",r"[",value_filtered)
                m = re.match(r'^\[(.*)\]', value_filtered)
                if m:
                    inside_brackets = m.group(1)
                    # Between brackets
                    # Find brackets without separator
                    m = re.match(r'(.*)\] ?\[(.*)', inside_brackets)
                    if m:
                        debug_attributes.append("Missing comma in \"{:s}\" attribute.".format(attr))
                        result = re.sub(r"\] ?\[",r"],[",value_filtered)
                    else:
                        result = value_filtered
                    #print "TEST2:",result
                else:
                    result = value_filtered
            else:
                result = value_filtered
            if result == "":
                result = "EMPTY"
        else:
            #print "UNKNOWN:",data
            result = False
        return result

    def parseTable(self,
                   start,
                   end,
                   list_tbl_tables=[]):
        try:
            doc_range = self.doc.Range(start,end)
            nb_tables = doc_range.Tables.Count
            tables_counter = 1
            while tables_counter <= nb_tables:
                print "Process table:",tables_counter
                self.log("Process table:{:d}".format(tables_counter))
                tbl = doc_range.Tables(tables_counter)
                nb_rows = len(tbl.Rows) + 1
                #print "NB_ROWS",nb_rows
                nb_cols = len(tbl.Columns) + 1
                tbl_tables = []
                del(tbl_tables[:])
                header = True
                for row in range(1, nb_rows):
                    line = []
                    del(line[:])
                    for col in range(1, nb_cols):
                        try:
                            txt = Tool.replaceNonASCII(tbl.Cell(row, col).Range.Text)

                            line.append(txt)
                        except:
                            #print "Warning, encounter joined cells."
                            self.log("Warning, encounter joined cells.")
                            pass  # exception for joined cells
                    if header:
                        str_line = "|".join(line)
                        self.log("Table found:{:s}".format(str_line))
                        header = False
                    tbl_tables.append(line)
                #list_attributes["table"] = tbl_tables
                #print "inside tbl",tbl_tables
                # TODO: rendre applicable qunad plus d'un document est parsé
                if tables_counter in list_tbl_tables:
                    # Already exists
                    list_tbl_tables[tables_counter].extend(tbl_tables[:])
                else:
                    # New table
                    list_tbl_tables[tables_counter] = tbl_tables[:]
                tables_counter += 1
            else:
                pass
                #list_attributes["table"] = None
        except pythoncom.com_error as e:
            print "UN:",e
            #print "DEUX:",e.excepinfo[5]
            #print(win32api.FormatMessage(e.excepinfo[5]))
            #print "Treat:",start_delimiter,start,end
            #list_attributes["table"] = None
        return nb_tables

    def extractReqType(self,start_delimiter):
        m = re.match(r'^(S[w|W|H|S][R|D|L|C][D|V|S][CP]*)_.*', start_delimiter)
        if m:
            type = m.group(1)
            #print "start_delimiter",start_delimiter
            tag_req = type + "_"
        else:
            m = re.match(r'^(PLD[R|D]D)_\w*', start_delimiter)
            if m:
                type = m.group(1)
                #print "start_delimiter",start_delimiter
                tag_req = type + "_"
            else:
                print "Match r'^(S[w|W|H|S][R|D|L|C][D|V|S][CP]*)_.*' failed"
                type = ""
                tag_req = ""
        return type,tag_req

    def getDerived(self,
                   type,
                   refer,
                   derived,
                   found_dir,
                   start_delimiter,
                   key="derived"):
        """
        :param type:
        :param refer:
        :param derived:
        :param found_dir:
        :param start_delimiter:
        :return:
        """
        def isDerived(found,expected):
            found = found.upper()
            expected = expected.upper()
            #print "DERIVED",found,expected
            if found == expected:
                result = True
            else:
                result = False
            return result
        def testPartiallyDerived(refer):
            if refer in ("N/A","EMPTY","NO"):
                result = False
            else:
                result = True
            return result
        # Test derived requirements
        result = False
        #print "DERIVED TYPE",type
        #print "derived",derived
        if type in self.dico_specifications:
            expected_derived_list = self.dico_specifications[type][key]
            #print "expected_derived_list",expected_derived_list
            if Tool._is_array(expected_derived_list):
                for expected_derived in expected_derived_list:
                    result = isDerived(derived,
                                       expected_derived)
                    if result:
                        break
            else:
                result = isDerived(derived,
                                   expected_derived_list)
            if result:
                if key == "derived":
                    partially_derived = testPartiallyDerived(refer)
                    if partially_derived:
                        self.dico_errors["derived","S_2",found_dir,start_delimiter,""] = ["Derived requirement with traceability."]
                        self.nb_error += 1
        return result

    def parse_req(self,
                  tbl_req=[],
                  type="SWRD"):
        #
        # This function find all requirements in the document
        # a table is populated with
        #  tag, start position, end position, section (Title 3)
        #
        myRange = self.doc.Content
        save_start_pointer = myRange.Start
        sel = self.doc.Application.Selection
        # Looking for the first requirement
        try:
            found = self.find(myRange,
                              style='REQ_Id')
        except pythoncom.com_error as e:
            print e
            found = False

        start_first_req_part =  myRange.Start
        if found:
            txt = myRange.Text
            print "Found REQ_Id/Start/End",txt,myRange.Start,myRange.End
            result = self.matchBegin(txt,type)
            #print 'RESULT',result
            if not result:
                print "not a valid req ID start:",txt,type
                myRange.Start = save_start_pointer
                start_first_req_part = save_start_pointer
                found = False
        else:
            print "Missing REQ_Id style in document."
            print "Start:",myRange.Start
            print "End:",myRange.End
        # First requirement is found
        while found:
            txt = myRange.Text
            #print 'TXT',txt
            m = re.match(r'^\s*\[(S[HW][LRD][VD]C?P?_.*)\]', txt)
            m_pld = re.match(r'^\s*\[(PLD[R|D]D_.*)\]', txt)
            if m or m_pld:
                if m:
                    txt = m.group(1)
                else:
                    txt = m_pld.group(1)
                #print "Found REQ_body:",txt
                start = myRange.Start  # start REQ ID tag"
                end = myRange.End # end REQ ID tag
                tbl_req.append([txt,start,end])
                if self.active_dbg:
                    self.log("Requirement {:s} found.".format(txt),gui_display=True)
            #print "TXT:",txt
            found = self.find_execute()
        end_req_part = myRange.End
        return start_first_req_part

    def parse_end_req(self,
                      tbl_req=[],       # Input
                      tbl_output=[]):   # Output
        iter_list = iter(tbl_req)
        myRange = self.doc.Content
        sel = self.doc.Application.Selection
        found = self.find(myRange,style='REQ_End')
        start_first_req_part =  myRange.Start
        if not found:
            print "Missing REQ_End style in document."
            print "Start:",myRange.Start
            print "End:",myRange.End
        req_id = "0"
        while found:
            error = False
            txt = myRange.Text
            #m = re.match(r'^\s*\[End Requirement\]',txt)
            m = self.matchEndLLR(txt)
            if m:
                # Style is coherent with tag text
                self.debug("Found REQ_end: {:s}".format(txt))
                start_req_end = myRange.Start
                end_req_end = myRange.End
            else:
                self.debug("Style is not coherent with tag text: {:s}".format(Tool.removeNonAscii(txt)))
                error = True
            try:
                req_id,start_tag,end_tag = iter_list.next()
                if not error:
                    tbl_output.append((req_id,end_tag,end_req_end))
                #print "REQ:",req_id,start,end_req_end
                #print "TXT:",txt
                found = self.find_execute()
            except StopIteration:
                print "End iterations on requirement {:s}".format(req_id)
                # End of iteration
                break
        end_req_part = myRange.End
        return end_req_part

    def getReqInfos(self,
                    new_tab_req=[],
                    type=("SWRD",),
                    tbl_req_tag=[],
                    tbl_req_tag_wo_del=[],
                    table_enabled=False,
                    filename=""):
        #print "Call getReqInfos"
        # Looking for "Title 4" for SwRD
        tbl_req = []
        tbl_section = []
        tbl_output = []

        start_area_req = self.parse_req(tbl_req,type="SHLVCP")

        # start is the beginning of requirements zone
        if table_enabled:
            self.nb_tables += self.parseTable(0,start_area_req,self.list_tbl_tables_begin)
            print "nb_tables",self.nb_tables

        # Find end f requirement
        end_area_req = self.parse_end_req(tbl_req,
                                          tbl_output)

        for req_id,start,end in tbl_output:
            print req_id,",",start,",",end
        #exit()
        index = 0
        for start_delimiter,start,end in tbl_output:
            list_attributes = dict() #Caution, this a dictionary
            if table_enabled:
                tbl_tables = []
                try:
                    doc_range = self.doc.Range(start,end)
                    nb_tables = doc_range.Tables.Count
                    if nb_tables > 0:
                        tbl = doc_range.Tables(1)
                        nb_rows = len(tbl.Rows) + 1
                        nb_cols = len(tbl.Columns) + 1
                        for row in range(1, nb_rows):
                            line = []
                            for col in range(1, nb_cols):
                                try:
                                    line.append(Tool.replaceNonASCII(tbl.Cell(row, col).Range.Text))
                                except:pass  # exception for joined cells
                            tbl_tables.append(line)
                        list_attributes["table"] = tbl_tables
                    else:
                        list_attributes["table"] = None
                except pythoncom.com_error as e:
                    print "UN:",e
                    print "Treat:",start_delimiter,start,end
                    list_attributes["table"] = None
            self.parse_body_attr(start_delimiter,
                                 start,
                                 end,
                                 list_attributes)
            type,tag_req = self.extractReqType(start_delimiter)
            self.tbl_list_llr[start_delimiter] = list_attributes
            tbl_req_tag.append(start_delimiter)

            deleted = self.testStatusDeleted(start_delimiter,list_attributes)
            if not deleted:
                tbl_req_tag_wo_del.append(start_delimiter)
            # Forward
            if "verify" in list_attributes and "forward" in list_attributes:
                result = self.getDerived(type,
                                         list_attributes["verify"],
                                         list_attributes["forward"],
                                         filename,
                                         start_delimiter,
                                         key="forward")
            else:
                print "Missing verify or forward attribute"
                result = False

            if result:
                # Derived found
                self.nb_derived_req += 1
            #if index > 50:
            #    break
            index += 1
        # Loop to link section with requirement
        for req_id,start_pos,end_pos in tbl_req:
            found_section = False
            prev_section_text = ""
            for section_text,section_start_pos,section_end_pos in tbl_section:
                if section_start_pos < start_pos:
                    prev_section_text = section_text
                else:
                    req_id_str = str(req_id)
                    found_section = True
                    if req_id_str not in new_tab_req:
                        new_tab_req[req_id_str] = prev_section_text
                        #new_tab_req.append([str(req_id),start_pos,end_pos,prev_section_text])
                    break
        #for req in new_tab_req:
        #    print "tbl_req",req
        return (start_area_req,end_area_req)