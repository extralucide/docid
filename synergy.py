#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Olivier.Appere
#
# Created:     15/06/2014
# Copyright:   (c) Olivier.Appere 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from tool import Tool
import sys
import logging
# For regular expressions
import re
import string
# system
import os
from os.path import join
import time
from math import floor

class Synergy(Tool):
    def synergy_log(self,text="",display_gui=True):
        """
        Log messages
        """
        self.loginfo.info(text)

    def setSessionStarted(self):
        self.session_started = True

    def getSessionStarted(self):
        return self.session_started

    def _loadConfigSynergy(self):
        self.gen_dir = "result"
        try:
            # get generation directory
            self.gen_dir = self.getOptions("Generation","dir")
            # Get Synergy information
            self.login = self.getOptions("User","login")
            self.password = self.getOptions("User","password")
            self.ccm_server = self.getOptions("Synergy","synergy_server")
            conf_synergy_dir = self.getOptions("Synergy","synergy_dir")
            self.ccm_exe = os.path.join(conf_synergy_dir, 'ccm')
            self.ccb_cr_sort = self.getOptions("Generation","ccb_cr_sort")
            self.ccb_cr_parent = self.getOptions("Generation","ccb_cr_parent")
            print "Synergy config reading succeeded"
        except IOError as exception:
            print "Synergy config reading failed:", exception

    def __init__(self,
                 session_started=False,
                 ihm=None):
        global out_hdlr
        if ihm is not None:
            self.ihm = ihm
        else:
            self.ihm = None
        self.init_done = True
        self.session_started = session_started
        self.deactivate_history_cr = False
        # Set logging
        self.loginfo = logging.getLogger(__name__)

        if ihm is not None and ihm.verbose == "yes":
            out_hdlr = logging.FileHandler(filename='synergy.log')
        else:
            out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        out_hdlr.setLevel(logging.INFO)
        #print "out_hdlr",out_hdlr
        self.loginfo.addHandler(out_hdlr)
        self.loginfo.setLevel(logging.INFO)
        self.loginfo.debug("NO")
        Tool.__init__(self)
        self._loadConfigSynergy()
        self.preview = False

    def _ccmCmd(self,cmd_txt,print_log=True):
        # remove \n
        text = re.sub(r"\n",r"",cmd_txt)
        stdout = ""
        result = ""
        if text != "":
            stdout,stderr = self.ccm_query(text,'Synergy command')
##            self.master_ihm.defill()
            if stderr:
                if self.ihm is not None:
                    self.ihm.log(stderr)
##                print time.strftime("%H:%M:%S", time.localtime()) + " " + stderr
                 # remove \r
                result = stderr
                text = re.sub(r"\r\n",r"\n",stderr)
                m = re.match('Undefined command|Warning: No sessions found.',text)
                if m:
                    result = None
                if self.ihm is not None:
                    self.ihm.log(text)
            if stdout != "":
##                print time.strftime("%H:%M:%S", time.localtime())
##                print stdout
                # remove <void>
                result = re.sub(r"<void>",r"",stdout)
                # remove \r
                text = re.sub(r"\r\n",r"\n",result)
                if print_log and self.ihm is not None:
                    self.ihm.log(text)
        else:
            result = ""
        return result

    def _getReleaseInfo(self,release):
        """
        :param release:
        :return:
        """
        query = "release -show information {:s} ".format(release)
        ccm_query = 'ccm ' + query + '\n'
        self.ihm.log(ccm_query)
        self.ihm.defill()
        cmd_out = self._ccmCmd(query)
        if cmd_out == "":
            return False
        else:
            return True
    def _getBaselineInfo(self,baseline):
        """
        :param baseline:
        :return:
        """
        query = "baseline -show information {:s} -f \"%status\"".format(baseline)
        ccm_query = 'ccm ' + query + '\n'
        self.ihm.log(ccm_query)
        self.ihm.defill()
        cmd_out = self._ccmCmd(query)
        if cmd_out == "":
            return False
        else:
            return True
        # m = re.match(r'^(.*);(.*)$',result)
        # if m:
        #     status = m.group(1)
        #     release = m.group(2)
        #     return status,release
        # else:
        #     return False

    def _getParentInfo(self,parent_cr_id):
        """

        :param parent_cr_id:
        :return: ex:
            <td><IMG SRC=../img/changeRequestIcon.gif>SyCR</td>
            <td>PDS</td>
            <td>1</td>
            <td>SyCR_Under_Modification</td>
            <td>A429 Rx GPBUS variable used in PPDB logics</td>
        """
        result = False
        #
        # Get parent ID informations
        #
        query = "query -t problem \"(problem_number='" + parent_cr_id + "')\" -u -f \"<tr><td><IMG SRC=\"../img/changeRequestIcon.gif\">%CR_domain</td>" \
                                                                        "<td>%CR_type</td>" \
                                                                        "<td>%problem_number</td>" \
                                                                        "<td>%crstatus</td>" \
                                                                        "<td>%problem_synopsis</td>" \
                                                                        "<td>%CR_implemented_for</td>" \
                                                                        "<td>%CR_AC_milestones</td></tr>"
        ccm_query = 'ccm ' + query + '\n'
        self.ihm.log(ccm_query)
        result = self._ccmCmd(query)
        if result not in ("",None,"Lost connection to server"):
            if self.ihm is not None:
                pass
                #self.ihm.log("parent CR:" + parent_cr,False)
            result = result
        else:
            if self.ihm is not None:
                pass
                #self.ihm.log("No result for _getParentInfo.",False)
        return result

    def patchCR(self,cr_decod):
        # ID
        cr_id = cr_decod[0]
        # Patch to get CR domain from CR status
        cr_domain = self.getStatusPrefix(cr_decod[3])
        cr_decod[0] = "{:s} {:s}".format(cr_domain,cr_decod[0])
        # Synopsis
        cr_decod[2] = self.replaceNonASCII(cr_decod[2])
        # Status
        cr_decod[3] = self.removeStatusPrefix(cr_decod[3])
        # Impact analysis
        cr_decod[9] = self.cleanImpactAnalysis(cr_decod[9])
        cr_id = cr_decod[0]
        cr_synopsis = cr_decod[2]
        cr_status = cr_decod[3]
        return cr_id,cr_synopsis,cr_status

    def _getParentCR(self,
                     cr_id,
                     type_cr="parent",
                     full_info=False):
        """
        :param cr_id: ex: 809 (SACR)
        :return: ex: ['1', '162'] (SYCR)
        """
        if type_cr == "parent":
            # to get parents
            keyword = "has_child_CR"
        elif type_cr == "child":
            # to get children
            keyword = "is_child_CR_of"
        else:
            keyword = "is_information_CR_of"
        if not full_info:
            query = "query -t problem \"{:s}(cvtype='problem' and problem_number='{:s}')\" -u -f \"%problem_number\" ".format(keyword,cr_id)
        else:
            query = "query -t problem \"{:s}(cvtype='problem' and problem_number='{:s}')\" -u -f \"<tr>" \
                    "<td>%CR_domain</td>" \
                    "<td>%CR_type</td>" \
                    "<td>%problem_number</td>" \
                    "<td>%crstatus</td>" \
                    "<td>%problem_synopsis</td>" \
                    "<td>%CR_implemented_for</td>" \
                    "<td>%CR_AC_milestones</td>" \
                    "<td>%CR_customer_classification</td>" \
                    "</tr>".format(keyword,cr_id)

        executed = True
        if query != "":
            ccm_query = 'ccm ' + query
            #if self.ihm is not None:
            #    self.ihm.log(ccm_query)
                #self.ihm.defill()
            ccm_query += '\n'
            cmd_out = self._ccmCmd(query,False)
            if cmd_out in ("",None):
                if self.ihm is not None:
                    self.ihm.log("No {:s} CR found for CR {:s}.".format(type_cr,cr_id))
                executed = False
            else:
                if full_info:
                    cmd_out = Tool.adjustCR(cmd_out)
                    tbl_decod = self._parseMultiCRParent(cmd_out)
                    found_parent_cr_info = []
                    found_display = []
                    for parent_decod in tbl_decod:
                        #self.patchCR(parent_decod)
                        cr_info = parent_decod[0] + " " + parent_decod[1] + " " + parent_decod[2]
                        parent_cr_status = Tool.discardCRPrefix(parent_decod[3])
                        cr_synopsis = Tool.replaceNonASCII(parent_decod[4])
                        cr_implemented_for = parent_decod[5]
                        cr_ac_milestone = parent_decod[6]
                        cr_classif = parent_decod[7]
                        found_parent_cr_info.append([cr_info,parent_cr_status,cr_synopsis,cr_implemented_for,cr_ac_milestone,cr_classif])
                        found_display.append(parent_decod[2])
                    found_display_txt = ",".join(found_display)
                    self.ihm.log("Found {:s} CR {:s} for CR {:s}.".format(type_cr,found_display_txt,cr_id))
                    executed = found_parent_cr_info
                else:
                    if cmd_out is not None:
                        executed = cmd_out.splitlines()
                        found_display = []
                        for parent_cr_id in executed:
                            found_display.append(parent_cr_id)
                            #self.ihm.log("Found {:s} CR {:s} for CR {:s}.".format(type_cr,parent_cr_id,cr_id))
                        found_display_txt = ",".join(found_display)
                        self.ihm.log("Found {:s} CR {:s} for CR {:s}.".format(type_cr,found_display_txt,cr_id))
                    else:
                        executed = False
        return executed

    def get_eoc_infos(self,
                      list_found_items,
                      dico_tags):
        if list_found_items != []:
            print "list_found_items",list_found_items
            for object in list_found_items:
                m = re.match(r'^(.*)\.(.*)-(.*):(.*):([0-9]*)$',object)
                if m:
                    filename = m.group(1)
                    ext = m.group(2)
                    print "EXT",ext
                    if (ext == "hex") or (ext == "srec"):
                        eoc_filename = "eoc" + "_%d" % floor(time.time()) + "." + ext
                        # Call synergy command
                        self.catEOC(object,eoc_filename)
                        dico_addr = self.getEOCAddress()
                        hw_sw_compatibility,pn,checksum,failed = self._readEOC(join("result",eoc_filename),dico_addr)
                        dico_tags["part_number"] = pn # Ex: ECE3E-A338-0501
                        dico_tags["checksum"] = checksum # Ex: 0x6b62
                        dico_tags["eoc_id"] =  re.sub(r'ECE[A-Z0-9]{2}-A([0-9]{3})-([0-9]{4})',r'A\1L\2',pn)
                        dico_tags["hw_sw_compatibility"] = hw_sw_compatibility # Ex 0x100
                        dico_tags["failed"] = failed
                        return "{:s}.{:s}".format(filename,ext)

    def catEOC(self,object,filename):
        query = 'cat {:s}'.format(object)
        self.ihm.log("ccm " + query)
        stdout,stderr = self.ccm_query(query,"Read {:s}".format(object))
        if stdout != "":
             with open(join(self.gen_dir,filename), 'w') as of:
                of.write(stdout)

    def getDataSheetFolderName(self):
        query = 'query -u -n "*Data*sheet*" -t dir  -f "%name-%version:dir:%instance"'
        self.ihm.log("ccm " + query)
        stdout,stderr = self.ccm_query(query,"Get datasheet folder")
        # remove \r
        stdout = re.sub(r"\r",r"",stdout)
        stdout = re.sub(r"\n",r"",stdout)
        return stdout

    def getProjectsInBaseline(self,baseline):
        tbl_projects = []
        query = 'baseline -u -show projects -f "%name-%version:%type:%instance" {:s}'.format(baseline)
        stdout,stderr = self.ccm_query(query,"Get projects in baseline {:s}".format(baseline))
        if stderr:
           print "Error"
        if stdout != "":
            output = stdout.splitlines()
            for line in output:
                print "LINE",line
                m = re.match(r'(.*):project:[0-9]*$',line)
                if m:
                    project_obj = m.group(1)
                    tbl_projects.append(["",baseline,project_obj])
        return tbl_projects

    def getFolderName(self,
                      folder="*",
                      project="",
                      baseline="",
                      release="",
                      mute=False,
                      extra_info=""):
        """
        Search directory information and sub-directories list

        Example
        -------

        folder = "BIN"
        release = "SW_ENM/06"
        baseline = "SW_ENM_06_06"
        project = "CODE_SW_ENM-6.1"
        ccm query -u "is_member_of('CODE_SW_ENM-6.1')" -n "*BIN*" -t dir -f "%name-%version:dir:%instance"
        return ['BIN-1.0:dir:12']

        :param folder:
        :param project:
        :param baseline:
        :param release:
        :param mute:
        :return:
        """
        baseline_query = False
        if not Tool.isAttributeValid(project):
            # Project not valid
            if Tool.isAttributeValid(baseline):
                query = 'baseline -u -show objects -f "%name-%version:%type:%instance{:s}" {:s}'.format(extra_info,baseline)
                baseline_query = True
            else:
                if Tool.isAttributeValid(release):
                    query = 'query -u -n "*{:s}" -t dir -release {:s} -f "%name-%version:%type:%instance{:s}"'.format(folder,release,extra_info)
                else:
                    query = 'query -u -n "*{:s}" -t dir  -f "%name-%version:%type:%instance{:s}"'.format(folder,extra_info)
        else:
            query = 'query -u "is_member_of(\'{:s}\')" -n "*{:s}" -t dir -f "%name-%version:%type:%instance{:s}"'.format(project,folder,extra_info)
        if "ihm" in self.__dict__ and not mute:
            self.ihm.log("ccm " + query)
        else:
            print "ccm " + query
        stdout,stderr = self.ccm_query(query,"Get {:s} folder".format(folder))
        if stderr:
            m = re.match(r'Project name is either invalid or does not exist',stderr)
            if m:
                self.ihm.log("Project name is either invalid or does not exist.")
        output = stdout.splitlines()
        if output != []:
            if baseline_query:
                object_filtered = []
                if extra_info == "":
                    regexp = r'^(.*{:s}.*)-(.*):(.*):([0-9]*)$'.format(folder)
                else:
                    regexp = r'^(.*{:s}.*)-(.*):(.*):([0-9]*):(.*):(.*)$'.format(folder)
                for object in output:
                    print regexp,object
                    m = re.match(regexp,object,re.IGNORECASE)
                    if m:
                        if extra_info == "":
                            object_filtered.append("{:s}-{:s}:{:s}:{:s}".format(m.group(1),m.group(2),m.group(3),m.group(4)))
                        else:
                            object_filtered.append("{:s}-{:s}:{:s}:{:s}:{:s}:{:s}".format(m.group(1),m.group(2),m.group(3),m.group(4),m.group(5),m.group(6)))
                        print "DIR BASELINE:",object_filtered
                return object_filtered
            else:
                # Not a baseline query. Take first index
                return output
        return False

    def getFoldersList_essai_un(self,
                      folder="*",
                      project="",
                      baseline="",
                      release="",
                      mute=False,
                      exclude=[]):
        """
        Search directory information and sub-directories list

        Example
        -------

        folder = "BIN"
        release = "SW_ENM/06"
        baseline = "SW_ENM_06_06"
        project = "CODE_SW_ENM-6.1"
        ccm query -u "is_member_of('CODE_SW_ENM-6.1')" -n "*BIN*" -t dir -f "%name-%version:dir:%instance"
        return ['BIN-1.0:dir:12']

        :param folder:
        :param project:
        :param baseline:
        :param release:
        :param mute:
        :return:
        """
        baseline_query = False
        if not Tool.isAttributeValid(project):
            # Project not valid
            if Tool.isAttributeValid(baseline):
                query = 'baseline -u -show objects -f "%name-%version:dir:%instance;%type" {:s}'.format(baseline)
                baseline_query = True
            else:
                if Tool.isAttributeValid(release):
                    query = 'query -u -n "{:s}" -t dir -release {:s} -f "%name-%version:dir:%instance"'.format(folder,release)
                else:
                    query = 'query -u -n "{:s}" -t dir  -f "%name-%version:dir:%instance"'.format(folder)
        else:
            query = 'query -u "is_member_of(\'{:s}\')" -n "{:s}" -t dir -f "%name-%version:dir:%instance"'.format(project,folder)
        if "ihm" in self.__dict__ and not mute:
            self.ihm.log("ccm " + query)
        else:
            print "ccm " + query
        stdout,stderr = self.ccm_query(query,"Get {:s} folder".format(folder))
        if stderr:
            m = re.match(r'Project name is either invalid or does not exist',stderr)
            if m:
                self.ihm.log("Project name is either invalid or does not exist.")
        output = stdout.splitlines()
        output_filtered = []
        if output != []:
            for object in output:
                m = False
                print "object:",object
                if folder == "*":
                    folder = ".*"
                if baseline_query:
                    m = re.match(r'^({:s})-(.*):(.*):([0-9]*);dir$'.format(folder),object,re.IGNORECASE)
                else:
                    m = re.match(r'^({:s})-(.*):(.*):([0-9]*)$'.format(folder),object,re.IGNORECASE)
                if m:
                    directory_name = m.group(1)
                    if directory_name not in exclude:
                        object_filtered = "{:s}-{:s}:{:s}:{:s}".format(directory_name,m.group(2),m.group(3),m.group(4))
                        output_filtered.append(object_filtered)
                    else:
                        print "Exclude: {:s}".format(directory_name)
            return output_filtered
        return False

    def deactivate_getPredecessor(self):
        self.deactivate_history_cr =True

    def getPredecessor(self,
                       object_name,
                       tbl=[],
                       recur=False,
                       mute=False):

        def extractMajorIssue(object_name):
            major_issue = False
            m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',object_name,re.IGNORECASE)
            if m:
                name = m.group(1)
                version = m.group(2)
                major_issue = re.sub(r'([0-9]{1,2})\.([0-9]{1,2})',r'\1',version)
            return major_issue

        if not self.deactivate_history_cr:
            top_major_issue = extractMajorIssue(object_name)
            query = "query -u \"is_predecessor_of('{:s}')\" -f \"%name-%version:%type:%instance:%change_request\"".format(object_name)
            if "ihm" in self.__dict__ and not mute:
                self.ihm.log("ccm " + query)
            else:
                print "ccm " + query
            stdout,stderr = self.ccm_query(query,"Get {:s} predecessors".format(object_name))
            if stderr:
                print "ERROR:",stderr
            output = stdout.splitlines()
            if output != []:
                for object in output:
                    object = re.sub(r"<void>",r"",object)
                    #print "X:",object
                    m = re.match(r'^(.*)-(.*):(.*):([0-9]*):(.*)$',object,re.IGNORECASE)
                    if m:
                        name = m.group(1)
                        version = m.group(2)
                        major_issue = re.sub(r'([0-9]{1,2})\.([0-9]{1,2})',r'\1',version)
                        type = m.group(3)
                        instance = m.group(4)
                        cr = m.group(5)
                        if major_issue == top_major_issue:
                            tbl.append((version,cr))
                            if recur:
                                self.getPredecessor("{:s}-{:s}:{:s}:{:s}".format(name,version,type,instance),
                                                    tbl,
                                                    recur=True)

    def getFoldersList(self,
                      folder="*",
                      project="",
                      baseline="",
                      release="",
                      mute=False,
                      exclude=[]):
        """
        Search directory information and sub-directories list

        Example
        -------

        folder = "BIN"
        release = "SW_ENM/06"
        baseline = "SW_ENM_06_06"
        project = "CODE_SW_ENM-6.1"
        ccm query -u "is_member_of('CODE_SW_ENM-6.1')" -n "*BIN*" -t dir -f "%name-%version:dir:%instance"
        return ['BIN-1.0:dir:12']

        :param folder:
        :param project:
        :param baseline:
        :param release:
        :param mute:
        :return:
        """
        baseline_query = False
        if Tool.isAttributeValid(project):
            prj_name, prj_version = self.getProjectInfo(project)
            query = 'query -u "is_child_of(\'{:s}\',\'{:s}\')" -t dir -f "%name-%version:dir:%instance"'.format(prj_name,project)
        if "ihm" in self.__dict__ and not mute:
            self.ihm.log("ccm " + query)
        else:
            print "ccm " + query
        stdout,stderr = self.ccm_query(query,"Get {:s} folder".format(folder))
        if stderr:
            m = re.match(r'Project name is either invalid or does not exist',stderr)
            if m:
                self.ihm.log("Project name is either invalid or does not exist.")
        output = stdout.splitlines()
        output_filtered = []
        if output != []:
            for object in output:
                m = False
                #print "object:",object
                if folder == "*":
                    folder = ".*"
                m = re.match(r'^({:s})-(.*):(.*):([0-9]*)$'.format(folder),object,re.IGNORECASE)
                if m:
                    directory_name = m.group(1)
                    if directory_name not in exclude:
                        object_filtered = "{:s}-{:s}:{:s}:{:s}".format(directory_name,m.group(2),m.group(3),m.group(4))
                        output_filtered.append(object_filtered)
                    else:
                        print "Exclude: {:s}".format(directory_name)
            return output_filtered
        return False

    def isInspection(self,name,type):
        found_is = False
        if type in ('xls',"doc"):
            dico = {"IS_":"Inspection Sheet",
                    "FDL":"Fiche de Lecture",
                    "PRR":"Peer Review Register"}
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",name)
            for key in dico:
                if key in doc_name:
                    found_is = True
        return found_is

    def addInList(self,
                  tbl_tables,
                  exclude_is,
                  name,
                  version,
                  type,
                  instance,
                  release,
                  cr,
                  with_cr=False,
                  code=False):
        if not (self.isInspection(name,type) and exclude_is):
            description,reference = self._getDescriptionDoc(name)
            if with_cr:
                if not code:
                    tbl_tables.append((reference,name,version,type,instance,release,cr))
                else:
                    tbl_tables.append((name,version,type,instance,release,cr))
            else:
                tbl_tables.append((description,reference,name,version,type,instance,release))

    def getListCR(self,
             name,
             version,
             type,
             instance,
             last_cr="",
             with_cr=True,
             cr_included=()):
        """

        :param name:
        :param version:
        :param type:
        :param instance:
        :return: list of CR
        """

        def crCarriageReturn(cr_txt):
            tbl_cr = cr_txt.split(",")
            if tbl_cr != []:
                if len(tbl_cr) > 1:
                    list_cr = ",\n".join(tbl_cr)
                else:
                    list_cr = "\n".join(tbl_cr)
            return list_cr

        # def removeCRs(res_tbl,cr_included):
        #     #Remove unexpected CRs
        #     if cr_included != [] or cr_included != ():
        #         for cr in res_tbl[:]:
        #             print "CR:",cr
        #             if str(cr) not in cr_included:
        #                 print "TEST",cr,cr_included
        #                 res_tbl.remove(cr)
        #                 #exit()
        object_name = "{:s}-{:s}:{:s}:{:s}".format(name,version,type,instance)
        tbl = []
        res_tbl = []
        #print "object_name",object_name
        if not self.preview and with_cr:
            # get previous version of objet
            self.getPredecessor(object_name,
                                tbl,
                                recur=True)
            for cr_tuple in tbl:
                if cr_tuple[1] != "":
                    cr = cr_tuple[1].split(",")
                    res_tbl.extend(cr)
        if last_cr != "":
            last_tbl_cr = last_cr.split(",")
            res_tbl.extend(last_tbl_cr)

        if res_tbl != []:
            res_tbl = map((lambda x: str(x)),res_tbl)
            #Remove unexpected CRs
            Tool.removeCRs(res_tbl,cr_included)
            res_tbl = Tool._removeDoublons(res_tbl)
            if len(res_tbl) > 1:
                list_cr = ",".join(res_tbl)
            else:
                list_cr = "".join(res_tbl)
        else:
            list_cr = ""
        return list_cr

    def getObjectsPerFolder(self,
                            keyword = "Input_Data",
                            project="",
                            baseline="",
                            release="",
                            list_tbl=[],
                            header=["Title","Reference","Synergy Name","Version","Type","Instance","Release"],
                            with_cr=False,
                            exclude_is=True,
                            code=False,
                            cr_included=()):

        list_objects = []
        list_file_specs = []
        list_obj_light = []
         #"S[w|W]DD"
        user_exclude = []
        self.ihm.log("Looking for {:s} folder ...".format(keyword))
        folder_found = self.getItemsInFolder(keyword,
                                             project = project,
                                             baseline = baseline,
                                             release = release,
                                             only_name=True,
                                             exclude=user_exclude,
                                             with_extension=True,
                                             mute=False,
                                             converted_list=list_objects,
                                             list_found_items=list_file_specs,
                                             extra_info = ":%change_request:%release",
                                             folder_found = True)
        if not folder_found:
            folder_found = "Miscelleanous"
        #list_tbl = []
        tbl_tables_misc =  [header]
        found_objects = False
        found_dir = False
        list_folders = []
        for folder_info in list_file_specs:
            print "getObjectsPerFolder:folder_info",folder_info
            top_name,version,type,instance,last_cr,release = self.getObjectInfos(folder_info,extra_info=True)
            object_name = "{:s}-{:s}:{:s}:{:s}".format(top_name,version,type,instance)
            if type == "dir":
                del(list_folders[:])
                print "------------------------"
                print "Found sub directory {:s}".format(folder_info)
                print "------------------------"

                result = self.getFromFolder(folder_info,
                                                  project = project,
                                                  exclude=user_exclude,
                                                  mute=False,
                                                  recur=True,
                                                  negate=False,
                                                  tbl=list_folders,
                                                  only_dir=False,
                                                  extra_info = ":%change_request:%release"
                                                  )
                tbl_tables = [header]
                for object_name_with_extra in list_folders:
                    print "object_name_with_extra",object_name_with_extra
                    name,version,type,instance,last_cr,release = self.getObjectInfos(object_name_with_extra,extra_info=True)
                    if type != "dir":
                        #print "Name",name
                        list_cr = self.getListCR(name,
                                                 version,
                                                 type,
                                                 instance,
                                                 last_cr,   # CRs list from the current object version
                                                 with_cr=with_cr,
                                                 cr_included=cr_included
                                                 )
                        self.addInList(tbl_tables,
                                       exclude_is,
                                       name,
                                       version,
                                       type,
                                       instance,
                                       release,
                                       list_cr,
                                       with_cr,
                                       code=code)
                        list_obj_light.append(name + " version " + version)
                        found_dir = True
                if found_dir:
                    print "folder_found::",folder_found
                    list_tbl.append((folder_found + "/" + top_name,tbl_tables[:]))
            else:
                list_cr = self.getListCR(top_name,
                                         version,
                                         type,
                                         instance,
                                         last_cr,
                                         with_cr=with_cr,
                                         cr_included=cr_included)
                self.addInList(tbl_tables_misc,
                               exclude_is,
                               top_name,
                               version,
                               type,
                               instance,
                               release,
                               list_cr,
                               with_cr,
                               code=code)
                list_obj_light.append(top_name + " version " + version)
                found_objects = True
        if found_objects:
            list_tbl.append((folder_found,tbl_tables_misc[:]))
        return list_obj_light

    def getItemsInFolder(self,
                         folder_keyword="*",
                         project="",
                         baseline="",
                         release="",
                         only_name=False,
                         exclude=[],
                         with_extension=False,
                         mute=False,
                         converted_list=[],
                         list_found_items=[],
                         recur=False,
                         negate=False,
                         only_dir=False,
                         extra_info="",
                         folder_found="",
                         exclude_dir=False):
        """
        Gives list of files included in folders
        :param folder_keyword:
        :param project:
        :param only_name:
        :return:
        """
        folder_info_list = self.getFolderName(folder_keyword,
                                             project,
                                             baseline,
                                             release,
                                             mute=mute,
                                             extra_info=extra_info
                                             )
        #folder_found = False
        folder_info = False
        if folder_info_list:
            for folder_info in folder_info_list:
                if folder_info:
                    print "getItemsInFolder::folder_info",folder_info
                    # getFromFolder method needs a project
                    try:
                        if project == "":
                            raise ValueError("Project cannot be empty")
                    except ValueError:
                        print "Project cannot be empty"
                    list_folders = []
                    result = self.getFromFolder(folder_info,
                                                      project,
                                                      exclude=exclude,
                                                      mute=mute,
                                                      recur=recur,
                                                      negate=negate,
                                                      tbl=list_folders,
                                                      only_dir=only_dir,
                                                      extra_info=extra_info,
                                                      exclude_dir=exclude_dir
                                                      )
                    for folder in list_folders:
                        #print "ITEMS:",folder
                        #m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',folder)
                        document,issue,type_object,instance,cr,release = self.getObjectInfos(folder,extra_info=extra_info)
                        if document:
                            #document = m.group(1)
                            #issue = m.group(2)
                            #type_object = m.group(3)
                            remove_object = False
                            if exclude != []:
                                for key in exclude:
                                    if key in document:
                                        remove_object = True
                            if not remove_object:
                                if type_object == "project":
                                    # Found a project
                                    print "Found project:",document
                                else:
                                    # Discard object of type "project"
                                    if only_name:
                                        if with_extension:
                                            doc = document
                                        else:
                                            doc = re.sub(r"(.*)\.(.*)",r"\1",document)
                                    else:
                                        doc = "{:s} issue {:s}".format(document,issue)
                                    converted_list.append(doc)
                                    list_found_items.append(folder)
        if folder_found and folder_info:
            folder_name,version,type,instance,cr,release = self.getObjectInfos(folder_info,
                                                                               extra_info=extra_info)
            return folder_name
        else:
            return converted_list

    def createListRelBasProj(self,
                             project_set_list):
        include_code = False
        if project_set_list != []:
            # Projects are available in GUI
            self.ihm.log("Use project set list to create CID for documents",False)
            # Project set in GUI
            list_projects = self.ihm.project_set_list
        else:
            project = self.ihm.project
            # [self.release,self.baseline,self.project]]
            if Tool.isAttributeValid(project):
                find_sub_projects = True
                list_projects = [[self.ihm.release,self.ihm.baseline,project]]
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
                if Tool.isAttributeValid(self.ihm.baseline):
                    list_projects = self.getProjectsInBaseline(self.ihm.baseline)
                else:
                    list_projects = [[self.ihm.release,"",""]]
                    # No project nor baseline
                    # Patch: Looking for only release
                    print "INCLUDE_CODE"
                    include_code = True
        return include_code

    def _defineProjectQuery(self,
                            release,
                            baseline):
        """
        :param release:
        :param baseline:
        :return:
        """
        # First check for projects in baseline then in release
        if Tool.isAttributeValid(baseline):
            query = 'baseline -u -sby project -sh projects  {:s} -f "%name-%version"'.format(baseline)
        elif Tool.isAttributeValid(release):
            query = 'query -release {:s} "(cvtype=\'project\')" -f "%name-%version;%in_baseline"'.format(release)
        else:
            query = 'query "(cvtype=\'project\')" -f "%name-%version"'
        return query

    def findSubProjects(self,
                        prj_name,
                        prj_version,
                        tbl=[],
                        mute=False):
        """

        :param prj_name:
        :param prj_version:
        :param tbl:
        :return:
        """
        query = 'query -u "(cvtype=\'project\') and is_member_of( name=\'{:s}\' and version=\'{:s}\')"' \
                                                            '  -f "%name;%version;%release" '.format(prj_name,prj_version)
        if not mute:
            try:
                self.ihm.log("ccm " + query)
            except AttributeError,e:
                print "ccm " + query
        stdout,stderr = self.ccm_query(query,"Get sub-projects for {:s} version {:s}".format(prj_name,prj_version))
        tbl_projects = []
        if stdout == "":
            print "empty result"
            result = False
        else:
            output = stdout.splitlines()
            for line in output:
                print "LINE",line
                m = re.match(r'(.*);(.*);(.*)$',line)
                if m:
                    project_name = m.group(1)
                    project_version = m.group(2)
                    release = m.group(3)
                    project = "{:s}-{:s}".format(project_name,project_version)
                    tbl.append([release,"",project])
                    tbl_projects.append(project)
                    # Recursif
                    sub_tbl_projects = self.findSubProjects(project_name,
                                                            project_version,
                                                            tbl=tbl,
                                                            mute=mute)
                    tbl_projects.extend(sub_tbl_projects)
        return tbl_projects

    def _getProjectsList_wo_ihm(self,
                             release,
                             baseline_selected):
        """
        :param release:
        :param baseline_selected:
        :return list_projects:
        """
        # Here the list of projects is set
        list_projects = []
        if self.session_started:
            query = self._defineProjectQuery(release,baseline_selected)
            print "_getProjectsList_wo_ihm",query
            stdout,stderr = self.ccm_query(query,"Get projects")
            if stderr != "":
                # Ex if not in the correct database:
                # Invalid value 'SW_DCENM_01_23' for the baseline_spec argument.
                print "STDERR",stderr
            if stdout != "":
                output = stdout.splitlines()
                if Tool.isAttributeValid(baseline_selected):
                    if Tool.isAttributeValid(release):
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
            else:
                pass
            return list_projects

    def _getProjectsList_new(self,
                             release,
                             baseline_selected):
        """
        :param release:
        :param baseline_selected:
        :return:
        """
        if self.session_started:
            query = self._defineProjectQuery(release,baseline_selected)
            stdout,stderr = self.ccm_query(query,"Get projects")
            if stdout != "":
                self.ihm.projectlistbox.delete(0, END)
                output = stdout.splitlines()
                # Here the list of projects is set
                self.list_projects = []
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
                                        self.list_projects.append(project)
                                        break
                            else:
                                m = re.match(r'^Baseline(.*):$',line)
                                if not m:
                                    project = line
                                    self.list_projects.append(project)
                    else:
                        num = 0
                        for project in output:
                            if num > 0:
                                self.list_projects.append(project)
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
                        self.list_projects.append(project)
                # Update list of project of GUI
                self.ihm.projectlistbox.delete(0, END)
                if len(self.list_projects) > 1:
                    self.ihm.projectlistbox.insert(END, "All")
                for project in self.list_projects:
                    self.ihm.projectlistbox.insert(END, project)
                if len(self.list_projects) > 1:
                    self.ihm.projectlistbox.selection_set(first=0)
                self.ihm.projectlistbox.configure(bg="white")
            else:
                pass
            if self.list_projects != []:
                self.ihm.log("Available projects found:")
                for project in self.list_projects:
                    self.ihm.log( "     " + project)
                self.ihm.defill()
            else:
                self.ihm.log("No available projects found.")
                self.ihm.resetProjectListbox()
            self.ihm.releaselistbox.configure(state=NORMAL)
            self.ihm.baselinelistbox.configure(state=NORMAL)
            # Set scrollbar at the bottom
            self.ihm.general_output_txt.see(END)
            self.ihm.button_select.configure(state=NORMAL)
            self.ihm.setProject("All")
            return self.list_projects

    def _runFinduseQuery(self,
                         release,
                         project,
                         type_items,
                         enabled=False):
        '''
            Synergy finduse
            No baseline used, only project and release
        :rtype : object
        '''
        if self.finduse == "skip":
            enabled = False
            self.ihm.log("Finduse disabled.",False)
            return False
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
            if self.session_started:
                stdout,stderr = self.ccm_query(query,text)
            else:
                stdout = ""
        else:
            stdout = ""
        return stdout

    def getObjectInfos(self,line,extra_info=False):
        #print "LINE",line,extra_info
        name = ""
        version = ""
        type = ""
        instance = ""
        cr = ""
        release = ""
        line = re.sub(r"<void>",r"",line)
        if not extra_info:
            m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',line,re.IGNORECASE)
            if m:
                name = m.group(1)
                version = m.group(2)
                type = m.group(3)
                instance = m.group(4)
        else:
            m = re.match(r'^(.*)-(.*):(.*):([0-9]*):(.*):(.*)$',line,re.IGNORECASE)
            if m:
                name = m.group(1)
                version = m.group(2)
                type = m.group(3)
                instance = m.group(4)
                cr = m.group(5)
                release = m.group(6)
        return name,version,type,instance,cr,release
        #print "M",m

    def getFromFolder(self,
                      object_name="*",
                      project="",
                      recur=True,
                      exclude=[],
                      mute=False,
                      negate=False,
                      tbl=[],
                      only_dir=False,
                      extra_info="",
                      exclude_dir=False):

        output_filtered = []
        print "getFromFolder:",object_name
        #if extra_info == "":
        #    m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',object_name)
        #else:
        #    m = re.match(r'^(.*)-(.*):(.*):([0-9]*):(.*):(.*)$',object_name)
        folder_name,issue,type_object,instance,cr,release = self.getObjectInfos(object_name,extra_info)
        if folder_name:
            object_name_synergy = "{:s}-{:s}:{:s}:{:s}".format(folder_name,issue,type_object,instance)
            #folder_name = m.group(1)
            if Tool.isAttributeValid(project): # and folder_name not in exclude:
                #print "GO"
                prj_name, prj_version = self.getProjectInfo(project)
                if only_dir:
                    filter_dir = " -t dir "
                else:
                    filter_dir = ""
                query = "query -u \"is_child_of('{:s}', cvtype='project' and name='{:s}' and version='{:s}')\" {:s} -f \"%name-%version:%type:%instance{:s}\"".format(object_name_synergy,prj_name,prj_version,filter_dir,extra_info)
                if not mute:
                    self.ihm.log("ccm " + query)
                    #self.ihm.defill()
                stdout,stderr = self.ccm_query(query,"Get from folder")
                if stdout != "":
                    if not mute:
                        self.ihm.log(stdout,display_gui=False)
                        #self.ihm.defill()
                    output = stdout.splitlines()
                    if not recur:
                        for line in output:
                            directory_name,version,type,instance,cr,release = self.getObjectInfos(line,extra_info)
                            if negate:
                                if directory_name in exclude:
                                    output_filtered.append(line)
                                    print "TBL_1:",line
                                    tbl.append(line)
                            else:
                                if directory_name not in exclude:
                                    output_filtered.append(line)
                                    print "TBL_2:",line
                                    tbl.append(line)
                        #print "No recur"
                        return output_filtered
                    else:
                        for line in output:
                            directory_name,version,type,instance,cr,release =  self.getObjectInfos(line,extra_info)
                            if negate:
                                if directory_name in exclude:
                                    output_filtered.append(line)
                            else:
                                if directory_name not in exclude:
                                    output_filtered.append(line)
                        for item in output_filtered:
                            name,version,type,instance,cr,release =  self.getObjectInfos(item,extra_info)
                            if type:
                                if type == "dir":
                                    if not exclude_dir:
                                        tbl.append(item)
                                    print "TBL_3:",item
                                    if negate:
                                        recur_output = self.getFromFolder(object_name=item,
                                                                          project=project,
                                                                          mute=mute,
                                                                          tbl=tbl,
                                                                          recur = recur,
                                                                          only_dir=only_dir,
                                                                          extra_info=extra_info,
                                                                          exclude_dir=exclude_dir)
                                    else:
                                        recur_output = self.getFromFolder(object_name=item,
                                                                          project=project,
                                                                          exclude=exclude,
                                                                          mute=mute,
                                                                          tbl=tbl,
                                                                          recur = recur,
                                                                          only_dir=only_dir,
                                                                          extra_info=extra_info,
                                                                          exclude_dir=exclude_dir)
                                    if 0==1:
                                        if recur_output != []:
                                            print "TBL_4:",recur_output
                                            tbl.extend(recur_output)
                                        else:
                                            pass
                                else:
                                    print "TBL_5:",item
                                    tbl.append(item)
                else:
                    self.ihm.log(stderr)
                    self.ihm.log("No items found")
        return output_filtered

    def getCRInfo(self,
                  cr_id,
                  dico_cr,
                  parent=True):
        """
        To get "domain" information of the CR and information on parent CR
        :param cr_id: INPUT Ex "810"
        :param dico_cr: OUTPUT Ex: {'810': ('SACR', '<td><IMG SRC=../img/changeRequestIcon.gif>SyCR</td><td>PDS</td><td>806</td><td>SyCR_Under_Verification</td><td>Precision of 115V measurement on bus bar</td><td>S1.6%</td>\r\n')}
        :param parent: True/False
        """
        tbl_parent_cr = []
        query = "query -t problem \"(problem_number='{:s}') \" -u -f \"%CR_domain\"".format(cr_id)
        ccm_query = 'ccm ' + query + '\n'
        stdout = self._ccmCmd(query,True)
        if stdout not in("",None):
            output = stdout.splitlines()
            for cr_domain in output:
                if cr_domain != "":
                    break
            #print "CR_DOMAIN:",cr_domain
            # Get parent CR
            if parent:
                tbl_parent_cr_id = self._getParentCR(cr_id)
            else:
                tbl_parent_cr_id = False
            if tbl_parent_cr_id:
                # Get parent ID information
                parent_cr = ""
                for parent_cr_id in tbl_parent_cr_id:
                    res_parent_cr = self._getParentInfo(parent_cr_id)
                    if res_parent_cr:
                        tbl_parent_cr.append(res_parent_cr)
                list_parent_cr = ",".join(tbl_parent_cr)
                dico_cr[cr_id] = (cr_domain,list_parent_cr)
            else:
                dico_cr[cr_id] = (cr_domain,)

    def getParentCR(self,cr_id):
        """

        :param cr_id: ex: 809 (SACR)
        :return:
        """
        info_parent_cr = ""
        tbl_parent_cr_id = self._getParentCR(cr_id)
        # tbl_parent_cr_id = ex: ['1', '162']
        if tbl_parent_cr_id:
            #
            # Get parent ID information
            #
            for parent_cr_id in tbl_parent_cr_id:
                parent_cr = self._getParentInfo(parent_cr_id)
                if parent_cr:
                    parent_decod = self._parseCRParent(parent_cr)
                    # parent_decod = ex: ['SyCR', 'PDS', '1', 'SyCR_Under_Modification', 'A429 Rx GPBUS variable used in PPDB logics', '\r\n']
                    # parent_decod = ex: ['SyCR', 'EPDS', '162', 'SyCR_Under_Verification', 'ARINC 429 - Data missing -  ARINC_RX_FAIL', '\r\n']
                    text = self.removeNonAscii(parent_decod[4])
                    parent_status = self.discardCRPrefix(parent_decod[3])
                    # ID | ??? | ??? | synopsis | status |
                    info_parent_cr += "{:s} {:s} {:s}: {:s} [{:s}]\n\n".format(parent_decod[0],parent_decod[1],parent_decod[2],text,parent_status)
            print "TEST info_parent_cr",info_parent_cr
        return info_parent_cr

    def getPR_CCB(self,
                  cr_status="",
                  for_review=False,
                  cr_with_parent=False,
                  old_cr_workflow=False,
                  ccb_type="SCR",
                  list_cr_for_ccb=[],
                  detect_release="",
                  impl_release="",
                  ihm=None):
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
        tableau_pr = []
        # Header
        if self.session_started and \
                        cr_status is not None:
    ##        proc = Popen(self.ccm_exe + ' query -sby crstatus -f "%problem_number;%problem_synopsis;%crstatus" "(cvtype=\'problem\') and ((crstatus=\'concluded\') or (crstatus=\'entered\') or (crstatus=\'in_review\') or (crstatus=\'assigned\') or (crstatus=\'resolved\') or (crstatus=\'deferred\'))"', stdout=PIPE, stderr=PIPE)
            query_root = 'query -sby crstatus  '
            condition = '"(cvtype=\'problem\')'
            if old_cr_workflow:
                detection_word = "detected_on"
                impl_word = "implemented_in"
            else:
                detection_word = "CR_detected_on"
                impl_word = "CR_implemented_for"
            # detected
            if detect_release != "":
                condition += ' and '
                condition += self._createImpl(detection_word,detect_release)
            # implemented
            if impl_release != "":
                condition += ' and '
                condition += self._createImpl(impl_word,impl_release)
            # cr type already done in _createConditionStatus
            if cr_status != "":
                condition +=  ' and (crstatus=\'{:s}\') '.format(cr_status)
                condition_func_root = condition
                condition += '" '
            else:
                sub_cond = ihm.getStatusCheck()
                #gros patch
                condition += sub_cond[19:]
            condition_func_root = condition[0:-2]
            # Ajouter la gestion de l'ancien workflow
            query = query_root + condition + '-f "%problem_number;%CR_type;%problem_synopsis;%crstatus;%CR_ECE_classification;%CR_request_type;%CR_domain;%CR_detected_on;%CR_implemented_for"' # ;%CR_functional_impact
            stdout,stderr = self.ccm_query(query,"Get PRs")
            self.ihm.log(query + " completed.")
            self.ihm.defill()
            if stdout != "":
                output = stdout.splitlines()
                if list_cr_for_ccb == []:
                    list_cr_for_ccb_available = False
                else:
                    list_cr_for_ccb_available = True
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    line = re.sub(r"^ *[0-9]{1,3}\) ",r"",line)
                    m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
                    if m:
                        cr_type = m.group(2)
                        # remove ASCI control character
                        cr_synopsis = filter(string.printable[:-5].__contains__,m.group(3))
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

                        if list_cr_for_ccb_available:
                            if cr_id in list_cr_for_ccb:
                                info_parent_cr = ""
                                if cr_with_parent:
                                    info_parent_cr = self.getParentCR(cr_id)
                                if for_review:
                                    # For SQA or HPA review records
                                    tableau_pr.append([cr_id,cr_synopsis,cr_severity,status,info_parent_cr])
                                else:
                                    if ccb_type == "SCR":
                                        tableau_pr.append([cr_domain,cr_type,cr_id,status,cr_synopsis,cr_severity])
                                    else:
                                        # Specific for PLDCR
                                        tableau_pr.append([cr_domain,cr_type,cr_id,status,cr_synopsis,cr_severity,cr_detected_on,cr_implemented_for])
                            else:
                                print "CR discarded",cr_id
                        else:
                            # Update list_cr_for_ccb with all CR
                            list_cr_for_ccb.append(cr_id)
                            info_parent_cr = ""
                            if cr_with_parent:
                                info_parent_cr = self.getParentCR(cr_id)
                            if for_review:
                                # For SQA or HPA review records
                                tableau_pr.append([cr_id,cr_synopsis,cr_severity,status,info_parent_cr])
                            else:
                                if ccb_type == "SCR":
                                    tableau_pr.append([cr_id,cr_synopsis,cr_severity,status,info_parent_cr])
                                else:
                                     # Specific for PLDCR
                                    tableau_pr.append([cr_domain,cr_type,cr_id,status,cr_synopsis,cr_severity,cr_detected_on,cr_implemented_for])
                    else:
                        # Remove ASCII control characters
                        filtered_line = filter(string.printable[:-5].__contains__,line)
                        print "Functional impact:",filtered_line
                        if ccb_type == "SCR":
                            if for_review:
                                tableau_pr.append(["","","","",""])
                            else:
                                tableau_pr.append(["","","","","",""])
                        else:
                            tableau_pr.append(["","","","","","","",""])
        if len(tableau_pr) == 0:
            if ccb_type == "SCR":
                if for_review:
                    tableau_pr.append(["--","--","--","--","--"])
                else:
                    tableau_pr.append(["--","--","--","--","--","--"])
            else:
                tableau_pr.append(["--","--","--","--","--","--","--","--"])
        # Set scrollbar at the bottom
        return(tableau_pr)

    def getCR_linked_to_Task(self,task_id_str):
        stdout = ""
        stderr = ""
        text_summoning = "find CRs"
        query = "task -show change_request " + task_id_str
        self.ihm.log("ccm " + query)
        stdout,stderr = self.ccm_query(query,text_summoning)
        return stdout,stderr

    def getArticles(self,
                    type_object=(),
                    release="",
                    baseline="",
                    project="",
                    source=False,
                    recursive=True,
                    exclude=False,
                    cid_type=None):
        """
         Function to get list of items in Synergy with a specific release or baseline

         Example
         -------

         ccm query -sby name -n *.* -u "( (cvtype='csrc')  or  (cvtype='asmsrc')  or  (cvtype='incl')  or  (cvtype='macro_c')  or  (cvtype='library') ) and  recursive_is_member_of(cvtype='project' and name='SW_ENM' and version='6.4' , 'none')"  -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"

        :param type_object:
        :param release:
        :param baseline:
        :param project:
        :param source:
        :return: list of objects found
        """
        def dico(keyword,object_name,project):
            txt = "{:s}('{:s}','{:s}')".format(keyword,object_name,project)
            return txt
        additional_conditions = ""
        if self.session_started:
            # Create filter for item type
            query_cvtype = "\""
            query_cvtype_and = ""
            status = False
            if type_object != ():
                #query_cvtype = "\"("+Tool._createImpl("cvtype",type_object,with_and=False)+")"
                query_cvtype += Tool._createImpl("cvtype",type_object,with_and=False)
                query_cvtype += self.makeobjectsFilter(self.object_released,
                                                       self.object_integrate)
                query_cvtype_and = ' and '

            if source:
                # get task and CR for source code
                sortby = "name"
                text_summoning = "Get source files from "
                if cid_type is None:
                    cid_type = self.getCIDType()
                if cid_type not in ("SCI"):
                    display_attr = ' -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"' # %task_synopsis
                else:
                    display_attr = self.display_attr
            else:
                text_summoning = "Get documents from "
                sortby = "project"
                display_attr = ' -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"'
            if Tool.isAttributeValid(project):
                # Project
                prj_name, prj_version = self.getProjectInfo(project)
                # Get valid directories
                if exclude:
                    list_found_items = []
                    list_dir = self.getItemsInFolder(folder_keyword=prj_name,
                                                    project=project,
                                                    exclude=exclude,
                                                    negate=True,
                                                    recur=True,
                                                    list_found_items=list_found_items,
                                                    only_dir=True
                                                     )
                    if list_found_items:
                        #for folder in list_found_items:
                        #    print "folder",folder

                        keyword = "not is_child_of"
                        if not Tool._is_array(list_found_items):
                            # Split string with comma as separator
                            list_rel = list_found_items.split(",")
                        else:
                            # Keep list
                            list_rel = list_found_items
                        keywords_tbl = map((lambda x: keyword),list_rel)
                        keywords_prj = map((lambda x: project),list_rel)
                        additional_conditions = " and ".join(map(dico,keywords_tbl, list_rel,keywords_prj))
                        additional_conditions = " and " + additional_conditions
                    #exit(0)
                text_summoning += "project: {:s}".format(project)
                query = 'query -sby {:s} -n * -u '.format(sortby)
                query += query_cvtype + query_cvtype_and

                #prj_name, prj_version = self.getProjectInfo(project)
                #% option possible: ccm query "recursive_is_member_of('projname-version','none')"
                #if need_and:
                #     query += ' and '
                if not recursive:
                    query += ' is_member_of(cvtype=\'project\' and name=\'{:s}\' and version=\'{:s}\') {:s} " '.format(prj_name,prj_version,additional_conditions)
                else:
                    query += ' recursive_is_member_of(cvtype=\'project\' and name=\'{:s}\' and version=\'{:s}\' , \'none\') {:s}" '.format(prj_name,prj_version,additional_conditions)
                query += display_attr
                self.ihm.log("ccm " + query,color="white")
                stdout,stderr = self.ccm_query(query,text_summoning)
                # Set scrollbar at the bottom
                #self.ihm.defill()
                if stdout != "":
                    self.ihm.log(stdout)
                    #self.ihm.defill()
                    output = stdout.splitlines()
                    return output
                else:
                    self.ihm.log(stderr)
                    self.ihm.log("No items found.")
                    return ""
            elif Tool.isAttributeValid(baseline):
                # Baseline
                #
                #  -sh: show
                #   -u: unnumbered
                # -sby: sort by
                #
                text_summoning += "baseline: {:s}".format(baseline)
                query = 'baseline -u -sby {:s} -sh objects  {:s} {:s}'.format(sortby,baseline,display_attr)
                self.ihm.log(text_summoning)
                self.ihm.log("ccm " + query,color="white")
                self.ihm.defill()
                stdout,stderr = self.ccm_query(query,text_summoning)
                # Set scrollbar at the bottom
                self.ihm.log(stdout + stderr)
                self.ihm.defill()
                if stdout != "":
                    output = stdout.splitlines()
                    return output
                else:
                    self.ihm.log("No items found")
                    return ""
            elif  Tool.isAttributeValid(release):
                # Release
                text_summoning += "release: {:s}".format(release)
                query = 'query -sby {:s} -n * -u -release {:s} '.format(sortby,release)
                query += query_cvtype

                if Tool.isAttributeValid(project):
                    # Project
                    prj_name, prj_version = self.getProjectInfo(project)
                    #% option possible: ccm query "recursive_is_member_of('projname-version','none')"
                    query += query_cvtype_and + ' recursive_is_member_of(cvtype=\'project\' and name=\'{:s}\' and version=\'{:s}\' , \'none\')" '.format(prj_name,prj_version)
                    text = "project"
                    param = project
                else:
                    query += '"'
                    text = "release"
                    param = release
                query += display_attr
                self.ihm.log("ccm " + query,color="white")
                self.ihm.log("Get items from " + text + ": " + param)
                stdout,stderr = self.ccm_query(query,text_summoning)
                # Set scrollbar at the bottom
                self.ihm.defill()
                if stdout != "":
                    self.ihm.log(stdout)
                    output = stdout.splitlines()
                    return output
                else:
                    self.ihm.log(stderr)
                    self.ihm.log("No items found.")
                    return ""
            else:
                print "Bug: probleme avec la recherche d objets."
        else:
            self.ihm.log("Session not started.",False)
        # Set scrollbar at the bottom
        self.ihm.defill()
        return ""

def main():
    pass

if __name__ == '__main__':
    main()
