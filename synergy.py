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

class Synergy(Tool):
    def synergy_log(self,text="",display_gui=True):
        '''
        Log messages
        '''
        self.loginfo.info(text)
    def defill(self):
        pass
    def __init__(self,session_started):
        self.session_started = session_started
        self.verbose = "yes"
        # Set logging
        self.loginfo = logging.getLogger(__name__)
        if self.verbose == "yes":
            out_hdlr = logging.FileHandler(filename='synergy.log')
        else:
            out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        out_hdlr.setLevel(logging.INFO)
        self.loginfo.addHandler(out_hdlr)
        self.loginfo.setLevel(logging.INFO)
        self.loginfo.debug("NO")
        Tool.__init__(self)

    def _ccmCmd(self,cmd_txt,print_log=True):
        # remove \n
        text = re.sub(r"\n",r"",cmd_txt)
        stdout = ""
        result = ""
        if text != "":
            stdout,stderr = self.ccm_query(text,'Synergy command')
##            self.master_ihm.defill()
            if stderr:
                self.synergy_log(stderr)
##                print time.strftime("%H:%M:%S", time.localtime()) + " " + stderr
                 # remove \r
                result = stderr
                text = re.sub(r"\r\n",r"\n",stderr)
                m = re.match('Undefined command|Warning: No sessions found.',text)
                if m:
                    result = None
                self.synergy_log(text)
            if stdout != "":
##                print time.strftime("%H:%M:%S", time.localtime())
##                print stdout
                # remove <void>
                result = re.sub(r"<void>",r"",stdout)
                # remove \r
                text = re.sub(r"\r\n",r"\n",result)
                if print_log:
                    self.synergy_log(text)
        else:
            result = ""
        return result

    def discardCRPrefix(self,text):
        '''
        Remove Change Request prefix
        '''
        result = re.sub(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)', r'\2', text)
        return result

    def _getParentInfo(self,parent_cr_id):
        result = False
        #
        # Get parent ID informations
        #
        query = "query -t problem \"(problem_number='" + parent_cr_id + "')\" -u -f \"<td><IMG SRC=\"../img/changeRequestIcon.gif\">%CR_domain</td><td>%CR_type</td><td>%problem_number</td><td>%crstatus</td><td>%problem_synopsis</td>\""
        ccm_query = 'ccm ' + query + '\n'
        print ccm_query
        parent_cr = self._ccmCmd(query)
        if parent_cr != "":
            self.synergy_log("parent CR:" + parent_cr,False)
            result = parent_cr
        else:
            self.synergy_log("No result for _getParentInfo.",False)
        return result

    def _getParentCR(self,cr_id):
        query = "query -t problem \"has_child_CR(cvtype='problem' and problem_number='" + cr_id + "')\" -u -f \
                 \"%problem_number\" "
        executed = True
        if query != "":
            ccm_query = 'ccm ' + query + '\n'
            cmd_out = self._ccmCmd(query)
##            print "TEST has_child_CR"
            if cmd_out == "":
                self.synergy_log("No result.")
                executed = False
            else:
                # parent CR id
                # Remove carriage return
                # remove \n
                executed = re.sub(r"\n",r"",cmd_out)
                executed = re.sub(r"\r",r"",executed)
##                print "TEST PARENT CR ID",executed
        return executed

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
                self.synergy_log(text_summoning + baseline)
                self.synergy_log("ccm " + query)
                self.defill()
                stdout,stderr = self.ccm_query(query,text_summoning + baseline)
                # Set scrollbar at the bottom
                self.defill()
##                print stdout
                if stdout != "":
##                    print "TEST_BASELINE"
##                    print stdout
                    output = stdout.splitlines()
                    return output
                else:
                    self.synergy_log("No items found")
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
                self.synergy_log("ccm " + query)
                self.synergy_log("Get items from " + text + ": " + param)
                stdout,stderr = self.ccm_query(query,"Get items from " + text + ": " + param)
                # Set scrollbar at the bottom
                self.defill()
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
                self.synergy_log("ccm " + query)
                self.synergy_log("Get items from " + text + ": " + param)
                stdout,stderr = self.ccm_query(query,"Get items from " + text + ": " + param)
                # Set scrollbar at the bottom
                self.defill()
                if stdout != "":
                    output = stdout.splitlines()
                    return output
                else:
                    self.ihm.log("No items found.")
                    return ""
            else:
                print "Bug: problème avec la recherche d'objets."
        else:
            self.synergy_log("Session not started.",False)
        # Set scrollbar at the bottom
        self.defill()
        return ""

def main():
    pass

if __name__ == '__main__':
    main()
