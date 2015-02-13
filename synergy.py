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
import os
from os.path import join

# For Unit Tests
from Tkinter import *
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
        query = "query -t problem \"(problem_number='" + parent_cr_id + "')\" -u -f \"<td><IMG SRC=\"../img/changeRequestIcon.gif\">%CR_domain</td>" \
                                                                        "<td>%CR_type</td>" \
                                                                        "<td>%problem_number</td>" \
                                                                        "<td>%crstatus</td>" \
                                                                        "<td>%problem_synopsis</td>" \
                                                                        "<td>%CR_implemented_for%</td>\""
        ccm_query = 'ccm ' + query + '\n'
        self.ihm.log(ccm_query)
        parent_cr = self._ccmCmd(query)
        if parent_cr not in ("",None,"Lost connection to server"):
            if self.ihm is not None:
                pass
                #self.ihm.log("parent CR:" + parent_cr,False)
            result = parent_cr
        else:
            if self.ihm is not None:
                pass
                #self.ihm.log("No result for _getParentInfo.",False)
        return result

    def _getParentCR(self,cr_id):
        """
        :param cr_id: ex: 809 (SACR)
        :return: ex: ['1', '162'] (SYCR)
        """
        query = "query -t problem \"has_child_CR(cvtype='problem' and problem_number='{:s}')\" -u -f \"%problem_number\" ".format(cr_id)
        executed = True
        if query != "":
            ccm_query = 'ccm ' + query
            if self.ihm is not None:
                self.ihm.log(ccm_query)
                self.ihm.defill()
            ccm_query += '\n'
            cmd_out = self._ccmCmd(query,False)
            if cmd_out == "":
                if self.ihm is not None:
                    self.ihm.log("No parent CR found for CR {:s}.".format(cr_id))
                    self.ihm.defill()
                executed = False
            else:
                executed = cmd_out.splitlines()
                for parent_cr_id in executed:
                    self.ihm.log("Parent CR {:s} found for CR {:s}.".format(parent_cr_id,cr_id))
                    self.ihm.defill()
        return executed

    def get_eoc_infos(self,
                      list_found_items,
                      dico_tags):
        if list_found_items != []:
            print "list_found_items",list_found_items
            for object in list_found_items:
                m = re.match(r'^(.*)\.(.*)-(.*):(.*):([0-9]*)$',object)
                if m:
                    ext = m.group(2)
                    print "EXT",ext
                    if (ext == "hex") or (ext == "srec"):
                        eoc_filename = "eoc" + "_%d" % floor(time.time()) + "." + ext
                        # Call synergy command
                        self.catEOC(object,eoc_filename)
                        dico_addr = self.getEOCAddress()
                        hw_sw_compatibility,pn,checksum = self._readEOC(join("result",eoc_filename),dico_addr)
                        dico_tags["part_number"] = pn # Ex: ECE3E-A338-0501
                        dico_tags["eoc_id"] =  re.sub(r'ECE[A-Z0-9]{2}-A([0-9]{3})-([0-9]{4})',r'A\1L\2',pn)
                        dico_tags["checksum"] = checksum # Ex: 0x6b62
                        dico_tags["hw_sw_compatibility"] = hw_sw_compatibility # Ex 0x100
                        break

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

    def getFolderName(self,
                      folder="",
                      project="",
                      baseline="",
                      release="",
                      mute=False):
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
        #print "DEBUG getFolderName",folder,release,baseline,project
        baseline_query = False
        if project in ("*","All",""):
            if baseline not in ("","All",None,"None"):
                query = 'baseline -u -show objects -f "%name-%version:dir:%instance;%type" {:s}'.format(baseline)
                baseline_query = True
            else:
                if release not in ("","All",None,"None"):
                    query = 'query -u -n "*{:s}*" -t dir -release {:s} -f "%name-%version:dir:%instance"'.format(folder,release)
                else:
                    query = 'query -u -n "*{:s}*" -t dir  -f "%name-%version:dir:%instance"'.format(folder)
        else:
            query = 'query -u "is_member_of(\'{:s}\')" -n "*{:s}*" -t dir -f "%name-%version:dir:%instance"'.format(project,folder)
        if "ihm" in self.__dict__ and not mute:
            self.ihm.log("ccm " + query)
        stdout,stderr = self.ccm_query(query,"Get {:s} folder".format(folder))
        if stderr:
            m = re.match(r'Project name is either invalid or does not exist',stderr)
            if m:
                self.ihm.log("Project name is either invalid or does not exist.")
        output = stdout.splitlines()
        if output != []:
                if baseline_query:
                    object_filtered = ""
                    for object in output:
                        m = re.match(r'^({:s})-(.*):(.*):([0-9]*);dir$'.format(folder),object,re.IGNORECASE)
                        if m:
                            object_filtered = "{:s}-{:s}:{:s}:{:s}".format(m.group(1),m.group(2),m.group(3),m.group(4))
                            #print "DIR BASELINE:",object_filtered
                    return object_filtered
                else:
                    #print "DIR PROJECT:",output
                    return output[0]
        return False

    def getItemsInFolder(self,
                         folder_keyword="",
                         project="",
                         baseline="",
                         release="",
                         only_name=False,
                         exclude=[],
                         with_extension=False,
                         mute=False,
                         converted_list=[],
                         list_found_items=[]):
        """
        Gives list of files included in folders
        :param folder_keyword:
        :param project:
        :param only_name:
        :return:
        """
        folder_info = self.getFolderName(folder_keyword,
                                         project,
                                         baseline,
                                         release,
                                         mute=mute
                                         )
        if folder_info:
            # getFromFolder method needs a project
            try:
                if project == "":
                    raise ValueError("Project cannot be empty")
            except ValueError:
                print "Project cannot be empty"
            list_folders = self.getFromFolder(folder_info,
                                              project,
                                              exclude=exclude,
                                              mute=mute
                                              )
            for folder in list_folders:
                print "ITEMS:",folder
                m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',folder)
                if m:
                    document = m.group(1)
                    issue = m.group(2)
                    type_object = m.group(3)
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
        return converted_list

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
            self.ihm.log("ccm " + query)
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
            stdout,stderr = self.ccm_query(query,"Get projects")
            if stdout != "":
                output = stdout.splitlines()
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

    def getFromFolder(self,
                      object_name,
                      project="",
                      recur=True,
                      exclude=[],
                      mute=False):
        result = []
        m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',object_name)
        if m:
            folder_name = m.group(1)
            #print "folder_name",folder_name
            #print "exclude",exclude
        if Tool.isAttributeValid(project) and folder_name not in exclude:
            prj_name, prj_version = self.getProjectInfo(project)
            query = "query -u \"is_child_of('{:s}', cvtype='project' and name='{:s}' and version='{:s}')\" -f \"%name-%version:%type:%instance\"".format(object_name,prj_name,prj_version)
            if not mute:
                self.ihm.log("ccm " + query)
                self.ihm.defill()
            stdout,stderr = self.ccm_query(query,"Get from folder")
            if stdout != "":
                if not mute:
                    self.ihm.log(stdout,display_gui=False)
                    #self.ihm.defill()
                output = stdout.splitlines()
                if not recur:
                    return output
                for item in output:
                    m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',item)
                    if m:
                        type = m.group(3)
                        if type == "dir":
                            if item:
                                recur_output = self.getFromFolder(object_name=item,
                                                                  project=project,
                                                                  exclude=exclude,
                                                                  mute=mute)
                                result.extend(recur_output)
                        else:
                            result.append(item)
            else:
                self.ihm.log(stderr)
                self.ihm.log("No items found")
        return result

    def getCRInfo(self,cr_id,dico_cr,parent=True):
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
        #print "tbl_parent_cr",tbl_parent_cr
        #return dico_cr

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

    def getArticles(self,
                    type_object,
                    release,
                    baseline,
                    project="",
                    source=False,
                    recursive=True):
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
        if self.session_started:
            # Create filter for item type
            query_cvtype = ""
            status = False
            if type_object != ():
                query_cvtype = "\"("+Tool._createImpl("cvtype",type_object)+")"
                query_cvtype += self.makeobjectsFilter(self.object_released,
                                                       self.object_integrate)
            if source:
                # get task and CR for source code
                sortby = "name"
                text_summoning = "Get source files from "
                if self.getCIDType() not in ("SCI"):
                    display_attr = ' -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"' # %task_synopsis
                else:
                    display_attr = self.display_attr
            else:
                text_summoning = "Get documents from "
                sortby = "project"
                display_attr = ' -f "%release;%name;%version;%task;%change_request;%type;%project;%instance"'
            if Tool.isAttributeValid(project):
                # Project
                text_summoning += "project: {:s}".format(project)
                query = 'query -sby {:s} -n * -u '.format(sortby)
                if query_cvtype != "":
                    query += query_cvtype
                    need_and = True
                else:
                    need_and = False
                prj_name, prj_version = self.getProjectInfo(project)
                #% option possible: ccm query "recursive_is_member_of('projname-version','none')"
                if need_and:
                     query += ' and '
                if not recursive:
                    query += ' is_member_of(cvtype=\'project\' and name=\'{:s}\' and version=\'{:s}\')" '.format(prj_name,prj_version)
                else:
                    query += ' recursive_is_member_of(cvtype=\'project\' and name=\'{:s}\' and version=\'{:s}\' , \'none\')" '.format(prj_name,prj_version)
                query += display_attr
                self.ihm.log("ccm " + query,color="white")
                stdout,stderr = self.ccm_query(query,text_summoning)
                # Set scrollbar at the bottom
                self.ihm.defill()
                if stdout != "":
                    self.ihm.log(stdout)
                    self.ihm.defill()
                    output = stdout.splitlines()
                    return output
                else:
                    self.ihm.log(stderr)
                    self.ihm.log("No items found.")
                    return ""
            elif  Tool.isAttributeValid(baseline):
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
                if query_cvtype != "":
                    query += query_cvtype
                    need_and = True
                else:
                    need_and = False
                if Tool.isAttributeValid(project):
                    # Project
                    prj_name, prj_version = self.getProjectInfo(project)
                    #% option possible: ccm query "recursive_is_member_of('projname-version','none')"
                    if need_and:
                         query += ' and '
                    query += ' recursive_is_member_of(cvtype=\'project\' and name=\'{:s}\' and version=\'{:s}\' , \'none\')" '.format(prj_name,prj_version)
                    text = "project"
                    param = project
                else:
                    # peut mieux faire
                    if query_cvtype != "":
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

class Gui(Frame):
    def log(self,txt,test=False):
        print txt
    def defill(self):
        pass
    def __init__(self,window):
        self.type_cr_workflow = False
    def getTypeWorkflow(self):
        return False
def main():
    output = "Dspic33fj256GP710a-1.0:dir:1"
    m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',output)
    if m:
        type = m.group(3)
        print type
    # test = Synergy()
    fenetre = Tk()
    gui = Gui(fenetre)
    # test = Synergy(ihm=gui)
    # Test Folder filtering
    thread = synergy_thread.ThreadQuery(master=gui,
                                        login="appereo1",
                                        password="jeudi2009",
                                        system="Dassault F5X PDS",
                                        item="ESNESS")
    print "T2",thread.session_started
    while not thread.getSessionStarted():
        print "T3",thread.session_started
        pass
    time.sleep(5)
    # docid.startSession("","db_sms_pds","appereo1","jeudi2009","SMS")
    result = thread.getFolderName("*Data*sheet*","SW_WHCC-2.4")
    print result
    result = thread.getItemsInFolder("*Data*sheet*","SW_ENM-3.6")
    print result
    result = thread.getFolderName("*Input*Data*")
    print "getFolderName",result
    result = thread.getItemsInFolder("*Input*Data*","SW_ENM-3.6")
    # thread.getDataSheetFolderName()
    # result = thread. _getParentCR("704")
    print "getItemsInFolder",result
    project = "SW_WHCC-2.4"
    list_datasheets = []
    folder_info = thread.getFolderName("Input*Data",project)
    # result should like this Input Data-1:dir:2
    if folder_info:
        #print "folder_info",folder_info
        list_folders = thread.getFromFolder(folder_info,project,recur=False)
        #print "LISTFOLDERS",list_folders
        for sub_folder_info in list_folders:
            m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',sub_folder_info)
            if m:
                dirname = m.group(1)
                #print "DIRNAME",dirname
                m = re.match(r'Data ?sheet',dirname,re.IGNORECASE)
                if m:
                    sub_list_folders = thread.getFromFolder(sub_folder_info,project)
                    print "LISTFOLDERSTEST",sub_list_folders
                    for sub_folder in sub_list_folders:
                        m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',sub_folder)
                        if m:
                            doc = "{:s} issue {:s}".format(m.group(1),m.group(2))
                            list_datasheets.append(doc)
                    # we found Datasheet folder
                    break
    print "list_datasheets",list_datasheets
if __name__ == '__main__':
    main()
