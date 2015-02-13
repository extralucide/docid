__author__ = 'Olivier.Appere'
import time
from synergy import Synergy
from tool import Tool
# For regular expressions
import re
import string
from datetime import datetime

class CCB(Synergy,Tool):
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
    # [["Action ID","Context","Description","Assignee","Date open"]]
    tbl_actions_header = [["Action ID","Description","Responsible","State","Planned for","Comment"]]
    colw_actions = [500,2500,1000,500,1000,500]
    list_cr_for_ccb = {}
    list_cr_for_ccb_available = False
    detect_release = ""
    impl_release = ""

    @staticmethod
    def getClassif(old_cr_workflow):
        if not old_cr_workflow:
            classification = '%CR_ECE_classification'
        else:
            classification = '%Severity'
        return classification

    def setDetectRelease(self,detect_release):
        self.detect_release = detect_release
    def setImplRelease(self,impl_release):
        self.impl_release = impl_release
    def setGui(self,ihm):
        self.ihm = ihm

    def __init__(self,
                 ihm=None,
                 **kwargs):
        """
        :param ihm:
        :param kwargs:
        :return:
        """
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
        self.ihm = ihm
        Tool.__init__(self)
        self._loadConfigSynergy()
        if "system" in self.__dict__ and "item" in self.__dict__:
            self.old_cr_workflow = self.get_sys_item_old_workflow(self.__dict__["system"],self.__dict__["item"])
        else:
            self.old_cr_workflow = False
        if "detect" in self.__dict__:
            self.setDetectRelease(self.__dict__["detect"])
        if "implemented" in self.__dict__:
            self.setImplRelease(self.__dict__["implemented"])
        if "cr_domain" in self.__dict__:
            self.setDomain(self.__dict__["cr_domain"])
        self.list_change_requests = []

    def setListCR(self,
                  list,
                  status):
        """

        :param list:
        :param status:
        :return:
        """
        self.list_cr_for_ccb = list
        self.list_cr_for_ccb_available = status

    def createChecklist(self,
                        cr_domain,
                        for_review=False,
                        timeline={},
                        list_candidate_cr=[]):
        """
        Create checklist

        :param domain:
        :param for_review:
        :return:
        """
        #
        # Checklist
        #
        dico_cr_checklist ={'domain':cr_domain,
                            'sort':self.ccb_cr_sort,
                            'timeline':timeline}
        for cr_id in self.list_cr_for_ccb:
            cr_status = self._getCRStatus(cr_id,
                                          for_review)
            #print "createChecklist:cr_status:",cr_status
            #cr_domain = self.getStatusPrefix(cr_status)
            if cr_domain == "SCR":
                tbl_chk = self._getCRChecklist(cr_status)
            else:
                tbl_chk = self._getCRChecklist(cr_status,sw=False)

            if tbl_chk is not None:
                list_candidate_cr.append(cr_id)
                table_cr_checklist = []
                table_cr_checklist.append(["Check","Status","Remark"])
                for chk_item in tbl_chk:
                    table_cr_checklist.append([chk_item[0],"",""])
                # Add generic tokens
                if len(table_cr_checklist) == 1:
                    table_cr_checklist.append(["--","--","--"])
                dico_cr_checklist['checklist',cr_id,cr_status] = table_cr_checklist
        return dico_cr_checklist

    def createTblPreviousActionsList(self,list_action_items,ccb_time=False):
        tbl_actions = list(self.tbl_actions_header)
        if list_action_items:
            for action_item in list_action_items:
                #print " Previous action",action_item
                action_id = action_item[0]
                description = action_item[1]
                context = action_item[2]
                responsible = action_item[3]
                # Format date: 2015-01-13
                date_open = action_item[4]
                date_closure = action_item[5]
                # Format Open Close
                status = action_item[6]
                planned_for = action_item[7]
                comment =action_item[8]
                date_open_obj = datetime.strptime(date_open, '%Y-%m-%d')
                if not ccb_time:
                    ccb_time_obj = datetime.now()
                else:
                    ccb_time_obj = datetime.strptime(ccb_time, '%Y/%m/%d %H:%M:%S')
                    #date_now_converted = "{:d}-{:d}-{:d}".format(date_now.year,
                    #                                                 date_now.month,
                    #                                                 date_now.day)
                #print "date_open_obj",date_open_obj
                #print "ccb_time_obj",ccb_time_obj
                if date_open_obj.date() < ccb_time_obj.date() and status == "Open":
                    tbl_actions.append(["{:d}".format(action_id),
                                        description,
                                        responsible,
                                        status,
                                        planned_for,
                                        comment])
        if len(tbl_actions) == 1:
            tbl_actions.append(["--","--","--","--","--","--"])
        return tbl_actions

    def createTblActionsList(self,list_action_items,ccb_time=False):
        #print "self.tbl_actions_header",self.tbl_actions_header
        tbl_actions = list(self.tbl_actions_header)
        #print "tbl_actions_before",tbl_actions
        if list_action_items:
            for action_item in list_action_items:
                #print "Current action",action_item
                action_id = action_item[0]
                description = action_item[1]
                context = action_item[2]
                responsible = action_item[3]
                # Format date: 2015-01-13
                date_open = action_item[4]
                date_closure = action_item[5]
                # Format Open Close
                status = action_item[6]
                planned_for = action_item[7]
                comment =action_item[8]
                date_open_obj = datetime.strptime(date_open, '%Y-%m-%d')
                if not ccb_time:
                    ccb_time_obj = datetime.now()
                else:
                    ccb_time_obj = datetime.strptime(ccb_time, '%Y/%m/%d %H:%M:%S')
                    #date_now_converted = "{:d}-{:d}-{:d}".format(date_now.year,
                    #                                                 date_now.month,
                    #                                                 date_now.day)
                #print "date_open_obj",date_open_obj
                #print "ccb_time_obj",ccb_time_obj
                if date_open_obj.date() >= ccb_time_obj.date():
                    tbl_actions.append(["{:d}".format(action_id),
                                        description,
                                        responsible,
                                        status,
                                        planned_for,
                                        comment])
        #print "tbl_actions after",tbl_actions
        #print "len(tbl_actions)",len(tbl_actions)
        if len(tbl_actions) == 1:
            tbl_actions.append(["--","--","--","--","--","--"])
        return tbl_actions

    def fillPRTable(self,
                     for_review,
                     cr_with_parent,
                     dico={}):
        tbl_cr_for_ccb = []
        if dico == {}:
            dico = {"cr_id":"",
                    "cr_synopsis":"",
                    "cr_severity":"",
                    "status":"",
                    "info_parent_cr":"",
                    "cr_domain":"",
                    "cr_type":"",
                    "cr_detected_on":"",
                    "cr_implemented_for":""}
        if dico["cr_id"] != "":
            cr_id = dico["cr_id"].zfill(4)
        else:
            cr_id = ""
        if for_review:
            tbl_cr_for_ccb = [cr_id,
                              dico["cr_synopsis"],
                              dico["cr_severity"],
                              dico["status"],
                              dico["info_parent_cr"]]
        elif self.ccb_type == "SCR": # and not cr_with_parent:
            tbl_cr_for_ccb = [dico["cr_domain"],
                              dico["cr_type"],
                              cr_id,
                              dico["status"],
                              dico["cr_synopsis"],
                              dico["cr_severity"]]
        elif cr_with_parent:
            tbl_cr_for_ccb = [dico["cr_domain"],
                              dico["cr_type"],
                              cr_id,
                              dico["status"],
                              dico["cr_synopsis"],
                              dico["cr_severity"],
                              dico["cr_detected_on"],
                              dico["cr_implemented_for"],
                              dico["info_parent_cr"]]
        else:
            tbl_cr_for_ccb = [dico["cr_domain"],
                              dico["cr_type"],
                              cr_id,
                              dico["status"],
                              dico["cr_synopsis"],
                              dico["cr_severity"],
                              dico["cr_detected_on"],
                              dico["cr_implemented_for"]]

        return tbl_cr_for_ccb

    @staticmethod
    def createCRlist(cr_id,
                     cr_synopsis,
                     list_change_requests):
        list_change_requests.append("{:s}) {:s}".format(cr_id.zfill(4),cr_synopsis))

    def getPR_CCB(self,
                  cr_status="",
                  for_review=False,
                  cr_with_parent=False,
                  cr_type=""):
        """
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
        :param cr_status:
        :param for_review:
        :param cr_with_parent:
        :param cr_type:
        :return: tableau_pr,found_cr
        """
        tableau_pr = []
        found_cr = False
        # Header
        if cr_status is not None:
            query = 'query -sby crstatus  '
            #TODO: Call to TKinter inside _createConditionStatus not good here
            condition,detect_attribut = self.ihm._createConditionStatus(detect_release=self.detect_release,
                                                                        impl_release=self.impl_release,
                                                                        cr_type=cr_type,
                                                                        old_cr_workflow=self.old_cr_workflow,
                                                                        cr_status=cr_status)

            # Ajouter la gestion de l'ancien workflow
            classification = self.getClassif(self.old_cr_workflow)
            detect_attribut_tag = re.sub(r";","</cell><cell>",detect_attribut)
            attributes = '-f "<cell>%problem_number</cell>' \
                         '<cell>%CR_type</cell>' \
                         '<cell>%problem_synopsis</cell>' \
                         '<cell>%crstatus</cell>' \
                         '<cell>{:s}</cell>' \
                         '<cell>%CR_request_type</cell>' \
                         '<cell>%CR_domain</cell>' \
                         '<cell>{:s}</cell>"'.format(classification,detect_attribut_tag)
            query += " {:s} {:s} ".format(condition,attributes)
            stdout,stderr = self.ccm_query(query,"Get PRs")
            self.ihm.log(query + " completed.")
            self.list_change_requests = []
            if stdout != "":
                output = stdout.splitlines()
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    cr_decod = self._parseCRCell(line)
                    if cr_decod != []:
                        found_cr = True
                        dico = {}
                        dico["cr_id"] = cr_decod[0]
                        dico["cr_type"] = cr_decod[1]
                        # remove ASCI control character
                        dico["cr_synopsis"] = filter(string.printable[:-5].__contains__,cr_decod[2])
                        dico["status"] = self.discardCRPrefix(cr_decod[3])
                        dico["cr_request_type"] = cr_decod[5]
                        dico["cr_domain"] = cr_decod[6]
                        dico["cr_detected_on"] = cr_decod[7]
                        dico["cr_implemented_for"] = cr_decod[8]
                        #if dico["cr_request_type"] == "Evolution":
                        #    dico["cr_severity"] = "N/A"
                        #else:
                        severity = re.sub(r"<void>",r"",cr_decod[4])
                        dico["cr_severity"] = severity
                        dico["info_parent_cr"] = ""
                        self.createCRlist(dico["cr_id"],
                                          dico["cr_synopsis"],
                                          self.list_change_requests)
                        # Get User selection ?
                        if self.list_cr_for_ccb_available:
                            if dico["cr_id"] in self.list_cr_for_ccb:
                                if cr_with_parent:
                                    info_parent_cr = self.getParentCR(dico["cr_id"])
                                    dico["info_parent_cr"] = info_parent_cr
                                result = self.fillPRTable(for_review,
                                                          cr_with_parent,
                                                          dico)
                                tableau_pr.append(result)
                            else:
                                print "CR discarded",dico["cr_id"]
                        else:
                            # No, get all CR from query
                            self.list_cr_for_ccb.append(dico["cr_id"])
                            if cr_with_parent:
                                info_parent_cr = self.getParentCR(dico["cr_id"])
                                dico["info_parent_cr"] = info_parent_cr
                            result = self.fillPRTable(for_review,
                                                            cr_with_parent,
                                                            dico)
                            tableau_pr.append(result)
                    else:
                        # Remove ASCII control characters
                        filtered_line = filter(string.printable[:-5].__contains__,line)
                        print "Functional impact:",filtered_line
                        result = self.fillPRTable(for_review,
                                                  cr_with_parent)
                        tableau_pr.append(result)
                self.list_cr_for_ccb.sort()
                self.list_change_requests.sort()
        if len(tableau_pr) == 0:
            result = self.fillPRTable(for_review,
                                      cr_with_parent)
            tableau_pr.append(result)
        # Set scrollbar at the bottom
        self.ihm.defill()
        return tableau_pr,found_cr

    def _getSpecificCR(self,cr_status=""):
        """
        To get info from a CR, TBD
        """
        tableau_pr = []
        # Header
        tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis"])
        if cr_status is not None:
            query_root = 'query -sby crstatus  '
            condition = '"(cvtype=\'problem\')'
            old_cr_workflow = self.ihm.getTypeWorkflow()
            condition,detect_attribut = self.ihm._createConditionStatus(detect_release=self.target_release,
                                                                        impl_release="",
                                                                        cr_type="",
                                                                        old_cr_workflow=old_cr_workflow)
            condition += ' -f "%problem_number;%problem_synopsis;%crstatus;' + detect_attribut + '"'
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
            if cr_status != "":
                condition +=  ' and (crstatus=\''+ cr_status +'\') '
                condition_func_root = condition
                condition += '" '
            else:
                sub_cond = self.getStatusCheck()
                #gros patch
                condition += sub_cond[19:]
            condition_func_root = condition[0:-2]
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
        return tableau_pr

    @staticmethod
    def discardCRPrefix(text):
        '''
        Remove Change Request prefix
        '''
        result = re.sub(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)', r'\2', text)
        # Replace underscore by space, prettier
        result = re.sub(r'_',r' ',result)
        return result

    def getPR(self,
              dico_pr,
              detect_in,
              implemented_for,
              cr_type,
              cr_with_parent=False):
        """
            Run a Change Request query
            Remove prefix to make generic status name
            The result is put in the table self.tableau_pr with the following columns:
            --------------------------------------------------------------------
            | ID | Synopsis | Type | Status | Detected on | Implemented in/for |
            --------------------------------------------------------------------
            or if parent CR is requested
            --------------------------------------------------------------------------------
            | ID | Synopsis | Type | Status | Detected on | Implemented in/for | Parent CR |
            --------------------------------------------------------------------------------
            Used by CreateCID function
        """
        # Header
        empty_line = ["--","--","--","--","--","--"]
        if not cr_with_parent:
            header = ["ID","Synopsis","Type","Status","Detected on","Implemented in/for"]
            tableau_pr = [header]
            tableau_closed_pr = [header]
            tableau_opened_pr = [header]
        else:
            header = ["ID","Synopsis","Type","Status","Detected on","Implemented in/for","Parent CR"]
            empty_line.extend(["--"])
            tableau_pr = [header]
            tableau_closed_pr = [header]
            tableau_opened_pr = [header]
        old_cr_workflow = self.ihm.getTypeWorkflow()
        condition,detect_attribut = self.ihm._createConditionStatus(detect_release=detect_in,
                                                                    impl_release=implemented_for,
                                                                    cr_type=cr_type,
                                                                    old_cr_workflow=old_cr_workflow)

        implementation_baseline_f = "%CR_implementation_baseline"
        # new with tags
        detect_attribut_tag = re.sub(r";","</cell><cell>",detect_attribut)
        classification = CCB.getClassif(old_cr_workflow)
        attributes = '-f "<cell>%problem_number</cell>' \
                     '<cell>%problem_synopsis</cell>' \
                     '<cell>%CR_request_type</cell>' \
                     '<cell>%crstatus</cell>' \
                     '<cell>{:s}</cell>"'.format(detect_attribut_tag)
        # query sorted by CR status
        query = "query -sby crstatus {:s} {:s} ".format(condition,attributes)
        #self.ihm.cr_activate_all_button()
        #self.ihm.checkbutton_all = True
        stdout,stderr = self.ccm_query(query,"Get CRs for CID creation")
        self.ihm.log(query + " completed.")
        # Set scrollbar at the bottom
        #self.ihm.defill()
        list_change_requests = []
        if stdout != "":
            output = stdout.splitlines()
            for line in output:
                line = re.sub(r"<void>",r"",line)
                cr_decod = self._parseCRCell(line)
                cr_id = cr_decod[0]
                cr_synopsis = cr_decod[1] #ThreadQuery.extractCR(cr_decod)
                type = cr_decod[2]
                cr_decod[3] = self.discardCRPrefix(cr_decod[3])
                status = cr_decod[3]
                detected_on = cr_decod[4]
                implemented_for = cr_decod[5]
                #  Used to fill UI CR list box
                list_change_requests.append("{:s}) {:s}".format(cr_id.zfill(4),cr_synopsis))
                # For CLI
                #print line
                #tableau_pr.append([cr_id,cr_synopsis,type,status,detected_on,implemented_for])
                if cr_with_parent:
                    tbl_parent_cr_id = self._getParentCR(cr_id)
                    #print "tbl_parent_cr_id",tbl_parent_cr_id
                    if tbl_parent_cr_id:
                        #print "tbl_parent_cr_id",tbl_parent_cr_id
                        if Tool._is_array(tbl_parent_cr_id):
                            found_parent_cr_id_str = ", ".join(tbl_parent_cr_id)
                        else:
                            found_parent_cr_id_str = tbl_parent_cr_id
                        cr_decod.extend([found_parent_cr_id_str])
                    else:
                        cr_decod.extend([""])
                else:
                    pass
                    #cr_decod.extend([""])
                tableau_pr.append(cr_decod)
                if status in ("Closed","Fixed"):
                    tableau_closed_pr.append(cr_decod)
                else:
                    tableau_opened_pr.append(cr_decod)

        if len(tableau_pr) == 1:
             tableau_pr.append(empty_line)
        if len(tableau_closed_pr) == 1:
             tableau_closed_pr.append(empty_line)
        if len(tableau_opened_pr) == 1:
             tableau_opened_pr.append(empty_line)
        dico_pr["all"]=tableau_pr
        dico_pr["open"]=tableau_opened_pr
        dico_pr["closed"]=tableau_closed_pr

    def getPR_Log(self,cr_status=""):
        # Header
        tableau_pr = [["id","Log"]]
        if cr_status is not None:
            condition = '"(cvtype=\'problem\') '
            if self.release not in ("","All"):
                condition = condition + '"(cvtype=\'problem\') and (CR_implemented_for=\'{:s}\') '.format(self.release)
            if cr_status != "":
                condition = condition + '"(cvtype=\'problem\') and (crstatus=\'{:s}\') '.format(cr_status)
            condition = condition + '" '
            query = 'query -sby crstatus ' + condition + '-f "%problem_number;%transition_log"'
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

    def _getCRStatus(self,
                     cr_id,
                     for_review=False):
        cr_status = ""
        for pr in self.tableau_pr:
            if for_review:
                index = 0
            else:
                index = 2
            #print "PR:",pr_index
            # Remove zeros on the left only
            pr_index = pr[index].lstrip('0')
            if pr_index == cr_id:
                cr_status = pr[3]
                break
        #print "cr_status",cr_status
        return cr_status

    def _getSeverity(self,cr):
        if cr not in ("","0000"):
            scores_default = {'Blocking': 1, 'Major': 2, 'Minor': 3, 'Enhancement': 4 , 'N/A' : 5}
            scores_sw = {'Showstopper': 1, 'Severe': 2, 'Medium': 3, 'Minor': 4 , 'N/A' : 5}
            if self.isSwDomain():
                scores = scores_sw
            else:
                scores = scores_default
            print "CR",cr
            if cr[5] in scores:
                return scores[cr[5]]
            else:
                return 5
        else:
            return False

    def setDomain(self,domain):
        self.ccb_type=domain
        print "self.ccb_type",self.ccb_type

    def getDomain(self):
        return self.ccb_type

    def setWorkflow(self,type):
        print "TEST setWorkflow",type
        if type == "New":
            self.old_cr_workflow = False
        elif type == "Old":
            self.old_cr_workflow = True
    def setRelease(self,release):
        self.release = release
        self.impl_release = release
    def setPreviousRelease(self,release):
        self.previous_release = release
    def setBaseline(self,baseline):
        self.baseline = baseline
    def setProject(self,project):
        self.project = project

    def isSwDomain(self):
        if "SCR" in self.ccb_type:
            result = True
        else:
            result = False
        return result

    def createCCB(self,
                  list_projects,
                  cr_domain,
                  list_action_items,
                  cr_with_parent,
                  dico,
                  list_cr_for_ccb,  # User selection list from _getListCRForCCB
                  status_list,      # User selection availability flag _getListCRForCCB
                  ccb_time=False,
                  dico_former_cr_status_list={},
                  tableau_pr_unsorted=[],
                  found_cr=False,
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
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
        if "system" not in self.__dict__:
            if "system" in dico:
                self.system = dico["system"]
            else:
                self.system = "Default"
                print "Missing system name"
        if self.ccb_cr_parent == "yes":
            cr_with_parent = True
        name,mail,tel,service,qams_user_id = self.get_user_infos(dico["login"])
        if dico["author"] in ("","Nobody"):
            dico["author"] = Tool.replaceNonASCII(name)
        #self.old_cr_workflow = self.get_sys_item_old_workflow(dico["system"],
        #                                                        dico["item"])
        #self.setDetectRelease(dico["detect"])
        #self.setImplRelease(dico["implemented"])
        #self.ccb_type = cr_domain
        cr_domain = self.getDomain()
        if self._is_array(cr_domain):
            list_cr_domain_str = ",".join(cr_domain)
        else:
            list_cr_domain_str = cr_domain

        self.setListCR(list_cr_for_ccb,
                       status_list)

        # CR list created based on list self.tableau_pr
        #tableau_pr_unsorted,found_cr = self.getPR_CCB(cr_with_parent=cr_with_parent,
        #                                              cr_type=dico["cr_type"])
        # if time capsule is activated
        #print "dico_former_cr_status_list",dico_former_cr_status_list
        dico_time_capsule = {}
        #print "tableau_pr_unsorted",tableau_pr_unsorted
        for cr in tableau_pr_unsorted:
            #cr_id = cr[2]
            cr_id = cr[2].lstrip('0')
            #print "CR_ID__",cr_id
            current_cr_status = cr[3]
            if cr_id in dico_former_cr_status_list:
                # update status with former status in the past
                former_cr_status = dico_former_cr_status_list[cr_id]
                dico_time_capsule[cr_id] = {"current":current_cr_status,
                                            "former":former_cr_status}
                cr[3] = former_cr_status
        #print "dico_time_capsule",dico_time_capsule
        # Sort CR according to ID, status or severity column
        # by default CR are sorted by severity
        if found_cr:
            if self.ccb_cr_sort == "":
                tableau_pr_sorted = sorted(tableau_pr_unsorted,key=self._getSeverity)
            else:
                if self.ccb_cr_sort == "id":
                    tableau_pr_sorted = sorted(tableau_pr_unsorted,key=lambda x: x[2])
                elif self.ccb_cr_sort == "status":
                    tableau_pr_sorted = sorted(tableau_pr_unsorted,key=lambda x: x[3])
                elif self.ccb_cr_sort == "severity":
                    tableau_pr_sorted = sorted(tableau_pr_unsorted,key=self._getSeverity)
                else:
                    tableau_pr_sorted = tableau_pr_unsorted
        else:
            tableau_pr_sorted = tableau_pr_unsorted

        # Checklist
        list_candidate_cr=[]
        if found_cr:
            self.tableau_pr = tableau_pr_sorted
            # Dictionary containing checklist for each CR, not sorted.
            if self.isSwDomain():
                cr_domain = "SCR"
            else:
                cr_domain = "CR"
            dico_cr_checklist = self.createChecklist(cr_domain,
                                                     timeline=dico_time_capsule,
                                                     list_candidate_cr=list_candidate_cr)
        else:
            dico_cr_checklist ={'domain':'SCR'}

        tableau_pr= []
        list_cr_annex = []
        if self.isSwDomain():
            # Software domain
            tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity"])
            # Annex
            num_begin = ord("a")
            num_end = ord("z")
            num = num_begin
            prefix = ""
            for cr_domain,cr_type,cr_id,cr_status,cr_synopsis,cr_severity in tableau_pr_sorted:
                # Patch
                if cr_id in list_candidate_cr:
                    line = "{:s}{:s}) Extract {:s} - {:s}".format(prefix,chr(num),cr_domain,cr_id)
                    num += 1
                    if num > num_end:
                        prefix += "a"
                        num = num_begin
                    list_cr_annex.append((line,'rb'))
                    list_cr_annex.append(('','r'))
        elif cr_with_parent:
            tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity","Detected on","Implemented for","Parent CR"])
        else:
            tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity","Detected on","Implemented for"])
        tableau_pr.extend(tableau_pr_sorted)

        tableau_log = [["id","Log"],["--","--"]]

        # Action_items
        # Previous actions
        tbl_previous_actions = self.createTblPreviousActionsList(list_action_items,ccb_time)
        # Current actions
        tbl_current_actions = self.createTblActionsList(list_action_items,ccb_time)
        template_type = "CCB"
        item_description = self.getItemDescription(dico["item"])
        ci_identification = self.get_ci_sys_item_identification(dico["system"],
                                                                dico["item"])
        if dico["component"] != "":
            title   = "{:s} {:s} {:s} {:s}".format(self.system,dico["item"],dico["component"],template_type)
            subject = "{:s} {:s} {:s} {:s}".format(self.system,dico["item"],dico["component"],self.getTypeDocDescription(template_type))
        elif dico["item"] != "":
            title   = "{:s} {:s} {:s}".format(self.system,dico["item"],template_type)
            subject = "{:s} {:s} {:s}".format(self.system,dico["item"],self.getTypeDocDescription(template_type))
        else:
            title   = "{:s} {:s}".format(self.system,template_type)
            subject = "{:s} {:s}".format(self.system,self.getTypeDocDescription(template_type))
        project_text = "The project is not defined"
        if dico["project"] != "":
            if len(list_projects) in (0,1) :
                project_text = "The project is {:s}".format(dico["project"])
            else:
                text = "The projects are: "
                project_text = text + ", ".join(map(str, list_projects))

        if dico["reference"] == "":
            if dico["component"] != "":
                tag_id = dico["component"]
            elif dico["item"] != "":
                tag_id = dico["item"]
            else:
                tag_id = dico["system"]
            reference = "CCB_Minutes_{:s}_001".format(tag_id)
        else:
            reference = dico["reference"]

        if self.isSwDomain():
            template_name = self._getTemplate("CCB")
            if not cr_with_parent:
                colw_pr = [500,      # Domain
                            500,     # CR Type
                            500,     # ID
                            500,     # Synopsis
                            2500,
                            500] # 5000 = 100%
            else:
                colw_pr = [300,      # Domain
                            300,     # CR Type
                            300,     # ID
                            500,     # Status
                            2000,    # Synopsis
                            400,
                            400,400,400,300] # 5000 = 100%
        else:
            template_name = self._getTemplate("CCB_PLD","CCB_Minutes_HW_PLD_template.docx")
            colw_pr = [300,      # Domain
                        300,     # CR Type
                        300,     # ID
                        500,     # Status
                        2000,    # Synopsis
                        400,
                        400,400,400,300] # 5000 = 100%
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
                    'colw': self.colw_actions, # 5000 = 100%
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
        if dico["issue"] == "":
            issue = "1"
        else:
            issue = dico["issue"]
        list_tags = {
                    'SUBJECT':{'type':'str','text':subject,'fmt':{}},
                    'TITLE':{'type':'str','text':title,'fmt':{}},
                    'CI_ID':{'type':'str','text':ci_identification,'fmt':{}},
                    'REFERENCE':{'type':'str','text':reference,'fmt':{}},
                    'ISSUE':{'type':'str','text':issue,'fmt':{}},
                    'ITEM':{'type':'str','text':dico["item"],'fmt':{}},
                    'ITEM_DESCRIPTION':{'type':'str','text':item_description,'fmt':{}},
                    'DATE':{'type':'str','text':time.strftime("%d %b %Y", time.localtime()),'fmt':{}},
                    'PROJECT':{'type':'str','text':project_text,'fmt':{}},
                    'RELEASE':{'type':'str','text':dico["release"],'fmt':{}},
                    'BASELINE':{'type':'str','text':dico["baseline"],'fmt':{}},
                    'DOMAIN':{'type':'str','text':list_cr_domain_str,'fmt':{}},
                    'WRITER':{'type':'str','text':dico["author"],'fmt':{}},
                    'MAIL':{'type':'str','text':mail,'fmt':{}},
                    'TEL':{'type':'str','text':tel,'fmt':{}},
                    'SERVICE':{'type':'str','text':service,'fmt':{}},
                    'COPIES':{'type':'str','text':"Nobody",'fmt':{}},
                    'MISSING':{'type':'str','text':"Nobody",'fmt':{}},
                    'TABLECHECKLIST':{'type':'mix','text':dico_cr_checklist,'fmt':self.fmt_chk},
                    'TABLEPRS':{'type':'tab','text':tableau_pr,'fmt':fmt_pr},
                    'PREVIOUS_ACTIONS':{'type':'tab','text':tbl_previous_actions,'fmt':fmt_actions},
                    'CURRENT_ACTIONS':{'type':'tab','text':tbl_current_actions,'fmt':fmt_actions},
                    'TABLELOGS':{'type':'tab','text':tableau_log,'fmt':fmt_log},
                    'TABLEANNEX':{'type':'par','text':list_cr_annex,'fmt':{}}
                        }
        if dico["item"] != "":
            docx_filename = dico["system"] + "_" + dico["item"] + "_CR_" + template_type + "_Minutes_" + dico["reference"] + "_%f" % time.time() + ".docx"
        else:
            docx_filename = dico["system"] + "_CR_" + template_type + "_Minutes_" + dico["reference"] + "_%f" % time.time() + ".docx"
        self.ihm.docx_filename = docx_filename
        self.docx_filename,exception = self._createDico2Word(list_tags,
                                                             template_name,
                                                             docx_filename)
        return self.docx_filename,exception

if __name__ == '__main__':
    pass
