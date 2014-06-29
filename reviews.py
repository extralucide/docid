#!/usr/bin/env python 2.7.3
## -*- coding: latin-1 -*-
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Olivier.Appere
#
# Created:     14/06/2014
# Copyright:   (c) Olivier.Appere 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# TODO: Create tables from SQLite database in templates
#
#           review_checklists_dispatch
#           review_checklists
#           category_checklist

from tool import Tool
from synergy import Synergy
from api_mysql import MySQL
import time
# For ToolPatchReview
import sys
##sys.path.append("python-docx")
##import docx
import re
import zipfile
from lxml import etree
# patch docx
nsprefixes = {
    'mo': 'http://schemas.microsoft.com/office/mac/office/2008/main',
    'o':  'urn:schemas-microsoft-com:office:office',
    've': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    # Text Content
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    # Drawing
    'a':   'http://schemas.openxmlformats.org/drawingml/2006/main',
    'm':   'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'mv':  'urn:schemas-microsoft-com:mac:vml',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'v':   'urn:schemas-microsoft-com:vml',
    'wp':  'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    # Properties (core and extended)
    'cp':  'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dc':  'http://purl.org/dc/elements/1.1/',
    'ep':  'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    # Content Types
    'ct':  'http://schemas.openxmlformats.org/package/2006/content-types',
    # Package Relationships
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'pr':  'http://schemas.openxmlformats.org/package/2006/relationships',
    # Dublin Core document properties
    'dcmitype': 'http://purl.org/dc/dcmitype/',
    'dcterms':  'http://purl.org/dc/terms/'}

def advReplace(document,search,replace,bs=3):
    '''Replace all occurences of string with a different string, return updated document

    This is a modified version of python-docx.replace() that takes into
    account blocks of <bs> elements at a time. The replace element can also
    be a string or an xml etree element.

    What it does:
    It searches the entire document body for text blocks.
    Then scan those text blocks for replace.
    Since the text to search could be spawned across multiple text blocks,
    we need to adopt some sort of algorithm to handle this situation.
    The smaller matching group of blocks (up to bs) is then adopted.
    If the matching group has more than one block, blocks other than first
    are cleared and all the replacement text is put on first block.

    Examples:
    original text blocks : [ 'Hel', 'lo,', ' world!' ]
    search / replace: 'Hello,' / 'Hi!'
    output blocks : [ 'Hi!', '', ' world!' ]

    original text blocks : [ 'Hel', 'lo,', ' world!' ]
    search / replace: 'Hello, world' / 'Hi!'
    output blocks : [ 'Hi!!', '', '' ]

    original text blocks : [ 'Hel', 'lo,', ' world!' ]
    search / replace: 'Hel' / 'Hal'
    output blocks : [ 'Hal', 'lo,', ' world!' ]

    @param instance  document: The original document
    @param str       search: The text to search for (regexp)
    @param mixed replace: The replacement text or lxml.etree element to
                          append, or a list of etree elements
    @param int       bs: See above

    @return instance The document with replacement applied

    '''
    # Enables debug output
    DEBUG = False

    newdocument = document

    # Compile the search regexp
    searchre = re.compile(search)

    # Will match against searchels. Searchels is a list that contains last
    # n text elements found in the document. 1 < n < bs
    searchels = []

    for element in newdocument.iter():
        if element.tag == '{%s}t' % nsprefixes['w']: # t (text) elements
            if element.text:
                # Add this element to searchels
                searchels.append(element)
                if len(searchels) > bs:
                    # Is searchels is too long, remove first elements
                    searchels.pop(0)

                # Search all combinations, of searchels, starting from
                # smaller up to bigger ones
                # l = search lenght
                # s = search start
                # e = element IDs to merge
                found = False
                for l in range(1,len(searchels)+1):
                    if found:
                        break
                    #print "slen:", l
                    for s in range(len(searchels)):
                        if found:
                            break
                        if s+l <= len(searchels):
                            e = range(s,s+l)
                            #print "elems:", e
                            txtsearch = ''
                            for k in e:
                                txtsearch += searchels[k].text

                            # Searcs for the text in the whole txtsearch
                            match = searchre.search(txtsearch)
                            if match:
                                found = True

                                # I've found something :)
                                if DEBUG:
                                    print "Found element!"
                                    print "Search regexp:", searchre.pattern
                                    print "Requested replacement:", replace
                                    print "Matched text:", txtsearch
                                    print "Matched text (splitted):", map(lambda i:i.text,searchels)
                                    print "Matched at position:", match.start()
                                    print "matched in elements:", e
                                    if isinstance(replace, etree._Element):
                                        print "Will replace with XML CODE"
                                    elif type(replace) == list or type(replace) == tuple:
                                        print "Will replace with LIST OF ELEMENTS"
                                    else:
                                        print "Will replace with:", re.sub(search,replace,txtsearch)

                                curlen = 0
                                replaced = False
                                for i in e:
                                    curlen += len(searchels[i].text)
                                    if curlen > match.start() and not replaced:
                                        # The match occurred in THIS element. Puth in the
                                        # whole replaced text
                                        if isinstance(replace, etree._Element):
                                            # If I'm replacing with XML, clear the text in the
                                            # tag and append the element
                                            searchels[i].text = re.sub(search,'',txtsearch)
                                            searchels[i].append(replace)
                                        elif type(replace) == list or type(replace) == tuple:
                                            # I'm replacing with a list of etree elements
                                            searchels[i].text = re.sub(search,'',txtsearch)
                                            for r in replace:
                                                searchels[i].append(r)
                                        else:
                                            # Replacing with pure text
                                            searchels[i].text = re.sub(search,replace,txtsearch)
                                        replaced = True
                                        if DEBUG:
                                            print "Replacing in element #:", i
                                    else:
                                        # Clears the other text elements
                                        searchels[i].text = ''
    return newdocument

class ToolPatchReview(Tool):
    def __init__(self):
        Tool.__init__(self)

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
            return advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl),relationshiplist
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
        result = advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl,6)
##        result = docx.advReplace_new(doc, '\{\{'+re.escape(tag)+'\}\}', repl,6)
        return result

class Log():
    def log(self,text="",display_gui=True):
        '''
        Log messages
        '''
        print text
class SynergyPatchReview(ToolPatchReview):
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
        ToolPatchReview.__init__(self)

class Review(Synergy):
    def __init__(self,
                review_number=1,
                detect_release="",
                impl_release="",
                tbl_cr_for_ccb=["","","","",""],
                session_started=False,
##                environment={"System":"Dassault F5X PDS","Item":"ESSNESS","Component":"ENM"},
                **kwargs
                ):

        self.detect_release = detect_release
        self.impl_release = impl_release
        self.tbl_cr = tbl_cr_for_ccb
##        self.system = environment["System"]
##        self.item = environment["Item"]
##        self.component = environment["Component"]
        self.review_number = review_number
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
##        ToolPatchReview.__init__(self)
        Synergy.__init__(self,session_started)
        self.ihm = Log()

    def getChecks(review_id=3,category_id=1):
        '''
            from SQLite tables review_checklists_dispatch and review_checklists and review_types
        '''
        query = "SELECT review_checklists_dispatch.rank,review_checklists.name,review_checklists_dispatch.sub_category FROM review_checklists \
                    LEFT OUTER JOIN review_checklists_dispatch ON review_checklists_dispatch.check_id = review_checklists.id \
                    LEFT OUTER JOIN review_types ON review_checklists_dispatch.review_id = review_types.id \
                    WHERE review_types.id LIKE '{:d}' AND review_checklists_dispatch.category_id LIKE '{:d}' ".format(review_id,category_id)
        result = Tool.sqlite_query(query)
##        if result == None:
##            description = "None"
##        else:
##            description = result[0]
        print "RESULT",result
        return result

    def getReviewList(id=""):
        '''
        static method to get list of reviews (PR,SRR,etc.)
        '''
        if id == "":
            query = "SELECT id,description FROM review_types"
            result = Tool.sqlite_query(query)
            if result == None:
                list = "None"
            else:
                list = result
            return list
        else:
            query = "SELECT description FROM review_types WHERE id LIKE '{:d}'".format(id)
            result = Tool.sqlite_query_one(query)
            if result == None:
                description = "None"
            else:
                description = result[0]
            return description

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

    def createReviewReport(self):
        '''
        Create review report using docx module
        '''
        reference = self.reference
        issue = self.issue
        target_release = self.impl_release
##        release = self.release
##        baseline =  self.baseline
        review_number = self.review_number
    ##        baseline_deliv = self.ihm.baseline_deliv_entry.get()

        sci_doc = "None"
        seci_doc = "None"
        sas_doc = "None"
        sci_is = "None"
        seci_is = "None"
        sas_is = "None"
##        tbl_copies.append(["",""])
        # List CR for review
        # A modifier pour avoir le tableau correct
        self.ccb_type = "SCR"#self.ihm.ccb_var_type.get()
##        self.detect_release = self.ihm.previous_release
##        self.impl_release = self.ihm.impl_release
##        self.cr_type = self.ihm.cr_type
##        tbl_cr = self.getPR_CCB("",True)
        tableau_pr = []
    ##        if self.ccb_type == "SCR":
        tableau_pr.append(["CR ID","Synopsis","Severity","Status","Comment/Impact/Risk"])
    ##            tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity"])
    ##        else:
    ##            tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity","Dectected on","Implemented for"])
    ##        tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity"])
        tableau_pr.extend(self.tbl_cr)

        if self.component != "":
            ci_identification = self.getComponentID(self.component)
        else:
            ci_identification = self.get_ci_sys_item_identification(self.system,self.item)
        date_meeting = time.strftime("%d %b %Y", time.localtime())
##        review_number = self.ihm.var_review_type.get()
##        print "var_review_type",review_number
        colw_pr = [500,     # CR ID
                    2500,   # Synopsis
                    500,    # Severity
                    500,    # Status
                    1000]   # Comment

        colw_baseline = [500,     # Ref ID
                        1000,   # Name
                        500,    # Reference
                        500,    # Version
                        2500]   # Description

        colw_inputs_check = [500,     # Ref ID
                            500,   # Name
                            2000,    # Reference
                            500,    # Version
                            1000,
                            500]   # Description

        colw_action = [250,     # ID
                    500,    # Origin
                    2000,    # Action
                    500,    # Impact
                    250,   # Severity
                    250,    # Assignee
                    500,    # Closure
                    250,    # Status
                    1000] # 5000 = 100%
        fmt_pr =  {
                    'heading': True,
                    'colw': colw_pr, # 5000 = 100%
                    'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }
        fmt_baseline =  {
                    'heading': True,
                    'colw': colw_baseline, # 5000 = 100%
                    'cwunit': 'pct','tblw': 5000,'twunit': 'pct','borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }

        fmt_inputs_check=  {
                    'heading': True,
                    'colw': colw_inputs_check, # 5000 = 100%
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
        part_number = self.part_number
        checksum = self.checksum
        subject = self.subject
        # Documents dictionary set
        dico_plan_doc = {"PSAC":"Plan for Software Aspect of Certification",
                    "SDP":"Software Development Plan",
                    "SVP":"Software Verification Plan",
                    "SCMP":"Software Configuration Management Plan",
                    "SQAP":"Software Quality Assurance Plan",
                    "SRTS":"Software Requirement Test Standard",
                    "SDTS":"Software Design Test Standard",
                    "SCS":"Software Coding Standard"}
        dico_sas = {"SAS":"Software Accomplishment Summary"}
        dico_sci = {"SCI":"Software Configuration Index"}
        dico_seci = {"SECI":"Software Environment Configuration Index"}
        dico_spec = {"SWRD":"Software Requirements Data"}
        dico_upper = {"SPI":"SPI Interface Document",
                        "ICD":"Interface Control Document",
                        "HSID":"Hardware Software Interface Document",
                        "SSCS":"Board Specification Document"}
        # Inspection sheets dictionary set
        dico_is = {"IS_PSAC":"PSAC Inspection Sheet",
                    "IS_SDP":"SDP Inspection Sheet",
                    "IS_SVP":"SVP Inspection Sheet",
                    "IS_SCMP":"SVP Inspection Sheet",
                    "IS_SQAP":"SQAP Inspection Sheet",
                    "IS_SCI":"SCI Inspection Sheet",
                    "IS_SAS":"SAS Inspection Sheet",
                    "IS_SECI":"SECI Inspection Sheet",
                    "IS_SWRD":"SwRD Inspection Sheet"}
        # Voir si on peu pas faire mieux
        self.dico_doc={}
        self.dico_doc.update(dico_plan_doc)
        self.dico_doc.update(dico_sas)
        self.dico_doc.update(dico_sci)
        self.dico_doc.update(dico_seci)
        self.dico_doc.update(dico_spec)
        self.dico_doc.update(dico_upper)
        self.dico_doc.update(dico_is)
        # Patch: dico_descr_docs est dans las classe Tool
        self.dico_descr_docs = self.dico_doc

        # Documents default reset
        # Plans
        psac_doc = []
        sdp_doc = "No " + dico_plan_doc["SDP"]
        svp_doc = "No " + dico_plan_doc["SVP"]
        scmp_doc = "No " + dico_plan_doc["SCMP"]
        sqap_doc = "No " + dico_plan_doc["SQAP"]
        upper_doc = []

        # Standards
        srts_doc = "No " + dico_plan_doc["SRTS"]
        sdts_doc = "No " + dico_plan_doc["SDTS"]
        scs_doc = "No " + dico_plan_doc["SCS"]

        # Specification
        swrd_doc = []
        # Design
        swdd_doc = []

        # Delivery documents
        sci_doc = "No " + dico_sci["SCI"]
        seci_doc = "No " + dico_seci["SECI"]
        sas_doc = "No " + dico_sas["SAS"]

        # Checksum
        dico_log = {"checksum":"checksum"}
        make_log = "No " + dico_log["checksum"]


        # Counter reset
        index_sci = 0
        index_seci = 0
        index_sas = 0

        index_is = 0
        index_doc = 0

        index_log = 0
        index_plans = 0
        index_stds = 0

        # inspection sheets
        psac_is = []
        sdp_is = []
        svp_is = []
        scmp_is = []
        sqap_is = []
        swrd_is = []
        swdd_is = []
        sys_doc = []
        self.tbl_inspection_sheets = []

        mysql = MySQL()
        # Liste d'actions vierge

        # Accès base MySQL QAMS pour les actions
        tbl_previous_actions_whdr = []
        tbl_current_actions_whdr = []
        header = ["Action item ID","Origin","Action","Impact","Severity","Assignee","Closure due date","Status","Closing proof"]
        tbl_previous_actions_whdr.append(header)
        tbl_current_actions_whdr.append(header)

        tbl_previous_actions = mysql.exportPreviousActionsList(self.review_qams_id)
        if tbl_previous_actions == []:
            tbl_previous_actions_whdr.append(["--","--","--","--","--","--","--","--","--"])
        else:
            tbl_previous_actions_whdr.extend(tbl_previous_actions)

        tbl_actions = mysql.exportActionsList(self.review_qams_id)
        print "tbl_actions",tbl_actions
        if tbl_actions == []:
            tbl_current_actions_whdr.append(["--","--","--","--","--","--","--","--","--"])
        else:
            tbl_current_actions_whdr.extend(tbl_actions)

        # Accès base MySQL QAMS pour les personnes qui assistent à la réunion
        # List of attendees
##        tbl_attendees = []
        tbl_attendees = mysql.exportAttendeesList(self.review_qams_id)
##        tbl_attendees.append(["Olivier Appere","SQA manager"])
##        tbl_attendees.append(["",""])
        # List of missing
        tbl_missing = mysql.exportAttendeesList(self.review_qams_id,True)
##        tbl_missing.append(["David Bailleul","Board manager"])
##        tbl_missing.append(["",""])
        # List of copies
        tbl_copies = []
        tbl_copies.append(["Marc Maufret","QA team leader"])

        list_tags_basics = {
                    'Name':{'type':'str','text':"O. Appere",'fmt':{}},
                    'DateMe':{'type':'str','text':date_meeting,'fmt':{}},
                    'Date':{'type':'str','text':date_meeting,'fmt':{}},
                    'Subject':{'type':'str','text':subject,'fmt':{}},
                    'Service':{'type':'str','text':'Quality Department','fmt':{}},
                    'Place':{'type':'str','text':'Montreuil','fmt':{}},
                    'Ref':{'type':'str','text':reference,'fmt':{}},
                    'Issue':{'type':'str','text':issue,'fmt':{}},
                    'Tel':{'type':'str','text':'','fmt':{}},
                    'Fax':{'type':'str','text':'','fmt':{}},
                    'Email':{'type':'str','text':'olivier.appere@zodiacaerospace.com','fmt':{}},
                    'TGT_REL':{'type':'str','text':target_release,'fmt':{}},
                    'CSCI':{'type':'str','text':ci_identification,'fmt':{}},
                    'CONFLEVEL':{'type':'str','text':'1','fmt':{}},
                    'SW_LEVEL':{'type':'str','text':'B','fmt':{}},
                    'PART_NUMBER':{'type':'str','text':part_number,'fmt':{}},
                    'CHECKSUM':{'type':'str','text':checksum,'fmt':{}},
                    'TBL_CR':{'type':'tab','text':tableau_pr,'fmt':fmt_pr},
                    'ATTENDEES':{'type':'tab','text':tbl_attendees,'fmt':fmt_two},
                    'MISSING':{'type':'tab','text':tbl_missing,'fmt':fmt_two},
                    'COPIES':{'type':'tab','text':tbl_copies,'fmt':fmt_two},
                    'PREVIOUS_ACTIONS':{'type':'tab','text':tbl_previous_actions_whdr,'fmt':fmt_action},
                    'CURRENT_ACTIONS':{'type':'tab','text':tbl_current_actions_whdr,'fmt':fmt_action}
                    }

        baseline_doc = ""
        release_doc = ""
        project_doc = ""
        baseline_store = []
        release_store = []
        project_store = []
        link_id = 0
        tbl_upper_doc = []
        tbl_output_doc = []
        tbl_inspection_doc = []
        tbl_peer_review_doc = []
        tbl_transition_doc = []
        header = ["Ref","Name","Reference","Version","Description"]
        tbl_upper_doc.append(header)
        tbl_output_doc.append(header)
        tbl_inspection_doc.append(header)
        tbl_peer_review_doc.append(header)
        tbl_transition_doc.append(header)
        #
        # selection of reviews/audits
        #
        if review_number == 9: # SCR
            review_string = "SCR"
            # Documents and inspections
            # For SAS and SCI
            # Project set in GUI
            for release,baseline,project in self.project_list:
                output = self.getArticles(("pdf","doc","xls","ascii"),release,baseline,project,False)
                if baseline not in baseline_store:
                    baseline_store.append(baseline)

                if release not in release_store:
                    release_store.append(release)

                if project not in project_store:
                    project_store.append(project)

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
            self.synergy_log("Amount of SCI found: " + str(index_sci),False)
            self.synergy_log("Amount of SAS found: " + str(index_sas),False)
            self.synergy_log("Amount of SECI found: " + str(index_seci),False)
            self.synergy_log("Amount of plans found: " + str(index_plans),False)
            self.synergy_log("Amount of checksum log found: " + str(index_log),False)
            psac_doc_tbl = self._getIinspectionSheetList(psac_doc)

            list_tags = {
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

            # Project set in GUI
            for release,baseline,project in self.project_list:
                output = self.getArticles(("pdf","doc","xls","ascii"),release,baseline,project,False)
                if baseline not in baseline_store:
                    baseline_store.append(baseline)

                if release not in release_store:
                    release_store.append(release)

                if project not in project_store:
                    project_store.append(project)

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

            list_tags = {
                        'PSAC_DOC':{'type':'tab','text':psac_doc_tbl,'fmt':fmt_one},
                        'SDP_DOC':{'type':'str','text':sdp_doc,'fmt':{}},
                        'SVP_DOC':{'type':'str','text':svp_doc,'fmt':{}},
                        'SCMP_DOC':{'type':'str','text':scmp_doc,'fmt':{}},
                        'SQAP_DOC':{'type':'str','text':sqap_doc,'fmt':{}},
                        'SRTS_DOC':{'type':'str','text':srts_doc,'fmt':{}},
                        'SDTS_DOC':{'type':'str','text':sdts_doc,'fmt':{}},
                        'SCS_DOC':{'type':'str','text':scs_doc,'fmt':{}},
                        'PSAC_IS':{'type':'tab','text':psac_is_tbl,'fmt':fmt_one},
                        'SDP_IS':{'type':'tab','text':sdp_is_tbl,'fmt':fmt_one},
                        'SVP_IS':{'type':'tab','text':svp_is_tbl,'fmt':fmt_one},
                        'SCMP_IS':{'type':'tab','text':scmp_is_tbl,'fmt':fmt_one},
                        'SQAP_IS':{'type':'tab','text':sqap_is_tbl,'fmt':fmt_one},
                        }

        elif review_number == 2: # SRR:
            review_string = "SRR"
            # Project set in GUI
            for release,baseline,project in self.project_list:
                output = self.getArticles(("pdf","doc","xls","ascii"),release,baseline,project,False)

                if baseline not in baseline_store:
                    baseline_store.append(baseline)

                if release not in release_store:
                    release_store.append(release)

                if project not in project_store:
                    project_store.append(project)

                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    self.ihm.log("Found doc: " + line,False)
                    m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
                    if m:
                        # Look for documents
                        if self._getSpecificDoc(m,"SWRD",("doc")):
                            index_doc +=1
                            swrd_doc = self.getDocName(m)
                        elif self._getSpecificDoc(m,"SHLDR",("xls")):
                            index_doc +=1
                            shldr_doc = self.getDocName(m)
                        elif self._getSpecificDoc(m,"SRTS",("pdf")):
                            index_doc +=1
                            srts_doc = self.getDocName(m)
                        # Look for peer reviews or inspection sheets
                        elif self._getSpecificDoc(m,"IS_SWRD",("xls")) or self._getSpecificDoc(m,"IS_SwRD",("xls")):
                            index_is +=1
                            name =  self.getDocName(m)
                            swrd_is.append(name)
                        # Upper documents
                        elif self._getSpecificDoc(m,"SSCS",("doc","pdf")):
                            index_doc +=1
                            name  = self.getDocName(m)
                            sys_doc.append(name)
                        elif self._getSpecificDoc(m,"SPI",("doc","xls")):
                            index_doc +=1
                            name  = self.getDocName(m)
                            sys_doc.append(name)

            swrd_is_tbl = self._getIinspectionSheetList(swrd_is)
            sys_doc_tbl = self._getIinspectionSheetList(sys_doc)


            list_tags = {
                        'SRTS_DOC':{'type':'str','text':srts_doc,'fmt':{}},
                        'SWRD_DOC':{'type':'str','text':swrd_doc,'fmt':{}},
                        'SHLDR_DOC':{'type':'str','text':shldr_doc,'fmt':{}},
                        'SYS_DOC':{'type':'tab','text':sys_doc_tbl,'fmt':fmt_one},
                        'SWRD_IS':{'type':'tab','text':swrd_is_tbl,'fmt':fmt_one}
                        }
        elif review_number == 3: # SDR:
            review_string = "SDR"
            # Project set in GUI
            result = Review.getChecks(review_number,1)
            # Create table
            tbl_inputs_check = []
            header = ["Nb. Item","Category","Item","Compliance status","Non compliance description / Justification","Actions (if compliance status is NOK)"]
            tbl_inputs_check.append(header)
            nb_item = 1
            for rank,description,category in result:
                nb_item_str = "{:d}".format(nb_item)
                tbl_inputs_check.append([nb_item_str,category,description,"OK/NOK/NA","",""])
                nb_item += 1
            print "INPUT ITEM CHECK",tbl_inputs_check
            list_tags = {
                        'SDTS_DOC':{'type':'str','text':sdts_doc,'fmt':{}},
                        'SDP_DOC':{'type':'str','text':sdp_doc,'fmt':{}},
                        'SVP_DOC':{'type':'str','text':svp_doc,'fmt':{}},
                        'SCMP_DOC':{'type':'str','text':scmp_doc,'fmt':{}},
                        'SWRD_DOC':{'type':'str','text':swrd_doc,'fmt':{}},
                        'SWDD_DOC':{'type':'str','text':swdd_doc,'fmt':{}},
                        'SWDD_IS':{'type':'str','text':swdd_is,'fmt':fmt_one},
                        'INPUTS_CHECK':{'type':'tab','text':tbl_inputs_check,'fmt':fmt_inputs_check},
                        'TBL_IN':{'type':'tab','text':tbl_upper_doc,'fmt':fmt_baseline},
                        'TBL_OUT':{'type':'tab','text':tbl_output_doc,'fmt':fmt_baseline},
                        'TBL_TRANSITION':{'type':'tab','text':tbl_transition_doc,'fmt':fmt_baseline},
                        'TBL_INSPECTION':{'type':'tab','text':tbl_inspection_doc,'fmt':fmt_baseline}
                        }
        elif review_number == 20: # SwRD audit:
            review_string = "AUD_SWRD"
            swrd_doc = ""
            swrd_is = ""

            # Project set in GUI
            for release,baseline,project in self.project_list:
                output = self.getArticles(("pdf","doc","xls","ascii"),release,baseline,project,False)
                if baseline not in baseline_store:
                    baseline_store.append(baseline)
                if release not in release_store:
                    release_store.append(release)
                if project not in project_store:
                    project_store.append(project)
                for line in output:
                    line = re.sub(r"<void>",r"",line)
                    self.ihm.log("Found doc: " + line,False)
                    m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)',line)
                    if m:
                        # Look for peer reviews or inspection sheets
                        if self._getSpecificDoc(m,"IS_SWRD",("xls")) or self._getSpecificDoc(m,"IS_SwRD",("xls")):
                            index_is +=1
                            swrd_is =  self.getDocName(m)
                            link_id = self._createTblDocuments(m,tbl_inspection_doc,link_id)
                        elif self._getSpecificDoc(m,"PRR_",("xls")):
                            index_prr +=1
                            link_id = self._createTblDocuments(m,tbl_peer_review_doc,link_id)
                        # Look for output documents
                        elif self._getSpecificDoc(m,"SWRD",("doc")):
                            index_doc +=1
                            swrd_doc = self.getDocName(m)
                            link_id = self._createTblDocuments(m,tbl_output_doc,link_id)
                        elif self._getSpecificDoc(m,"SHLDR",("xls")):
                            index_doc +=1
                            shldr_doc = self.getDocName(m)
                            link_id = self._createTblDocuments(m,tbl_output_doc,link_id)
                        # Look for inputput documents
                        elif self._getSpecificDoc(m,"SRTS",("pdf")):
                            index_doc +=1
                            srts_doc = self.getDocName(m)
                            link_id = self._createTblDocuments(m,tbl_upper_doc,link_id)
                        elif self._getSpecificDoc(m,"SDP",("doc")):
                            index_doc +=1
                            sdp_doc = self.getDocName(m)
                            link_id = self._createTblDocuments(m,tbl_upper_doc,link_id)
                        elif self._getSpecificDoc(m,"SCMP",("doc")):
                            index_doc +=1
                            link_id = self._createTblDocuments(m,tbl_upper_doc,link_id)
                        elif self._getSpecificDoc(m,"SVP",("doc")):
                            index_doc +=1
                            link_id = self._createTblDocuments(m,tbl_upper_doc,link_id)
                        # Upper documents
                        elif self._getSpecificDoc(m,"SSCS",("doc","pdf")):
                            index_doc +=1
                            doc  = self.getDocName(m)
                            link_id = self._createTblDocuments(m,tbl_upper_doc,link_id)
                        elif self._getSpecificDoc(m,"SPI",("doc","xls")):
                            index_doc +=1
                            doc  = self.getDocName(m)
                            link_id = self._createTblDocuments(m,tbl_upper_doc,link_id)
                        # CCB minutes
                        elif self._getSpecificDoc(m,"CCB_Minutes",("doc")):
                            index_doc +=1
                            doc  = self.getDocName(m)
                            link_id = self._createTblDocuments(m,tbl_upper_doc,link_id)
                        # transition documents
                        elif self._getSpecificDoc(m,"HSID",("doc","pdf")):
                            index_doc +=1
                            link_id = self._createTblDocuments(m,tbl_transition_doc,link_id)

            if len(tbl_upper_doc) == 1:
                tbl_upper_doc.append(["--","--","--","--","--"])
            if len(tbl_output_doc) == 1:
                tbl_output_doc.append(["--","--","--","--","--"])
            if len(tbl_peer_review_doc) == 1:
                tbl_inspection_doc.append(["--","--","--","--","--"])
            if len(tbl_inspection_doc) == 1:
                tbl_inspection_doc.append(["--","--","--","--","--"])
            list_tags = {
                        'SRTS_DOC':{'type':'str','text':srts_doc,'fmt':{}},
                        'SDP_DOC':{'type':'str','text':sdp_doc,'fmt':{}},
                        'SVP_DOC':{'type':'str','text':svp_doc,'fmt':{}},
                        'SCMP_DOC':{'type':'str','text':scmp_doc,'fmt':{}},
                        'SWRD_DOC':{'type':'str','text':swrd_doc,'fmt':{}},
                        'SWRD_IS':{'type':'str','text':swrd_is,'fmt':fmt_one},
                        'TBL_IN':{'type':'tab','text':tbl_upper_doc,'fmt':fmt_baseline},
                        'TBL_OUT':{'type':'tab','text':tbl_output_doc,'fmt':fmt_baseline},
                        'TBL_TRANSITION':{'type':'tab','text':tbl_transition_doc,'fmt':fmt_baseline},
                        'TBL_INSPECTION':{'type':'tab','text':tbl_inspection_doc,'fmt':fmt_baseline}
                        }
            print "LIST_TAGS",list_tags

        else:
            self.synergy_log("Review report export not implemented yet")
        self.synergy_log("Amount of inspection sheets found: " + str(index_is),False)
        self.synergy_log("Amount of documents found: " + str(index_doc),False)
    ##            tkMessageBox.showinfo("Review report export not implemented yet")
        baseline_doc = ", ".join(map(str, baseline_store))
        release_doc = ", ".join(map(str, release_store))
        project_doc = ", ".join(map(str, project_store))
        list_tags_scope = {
                    'REL':{'type':'str','text':release_doc,'fmt':{}},
                    'BAS':{'type':'str','text':baseline_doc,'fmt':{}},
                    'PROJ':{'type':'str','text':project_doc,'fmt':{}}}
        list_tags.update(list_tags_basics)
        list_tags.update(list_tags_scope)
        template_type = review_string
        template_name = self._getTemplate(template_type)
        docx_filename = self.system + "_" + self.item + "_" + template_type + "_Report_" + self.reference + "_%f" % time.time() + ".docx"
        if review_number in (1,2,3,9,20): # Patch temporaire
            self.docx_filename,exception = self._createDico2Word(list_tags,template_name,docx_filename)
        else:
            self.docx_filename = False
            exception = "Review report export not implemented yet"
        return self.docx_filename,exception
    # Static methods
    getReviewList = staticmethod(getReviewList)
    getChecks = staticmethod(getChecks)

    def getDocName(self,m):
        document = m.group(2)
        version = m.group(3)
        doc_name = re.sub(r"(.*)\.(.*)",r"\1",document)
        name = doc_name + " issue " + version
        return name

    def _getSpecificDoc(self,m,key,filter_type_doc=('doc','pdf','xls','ascii')):
        '''
            - the name of the document match the name in dictionary
            - the type of the document is doc or pdf or xls or ascii
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
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",document)
            if key in doc_name:
                description,reference = self._getDescriptionDoc(document)
                self.dico_found[key,type_doc] = doc_name + " issue " + version
                print "DICO_FOUND",self.dico_found
                result = True
        return result

    def _createTblDocuments(self,m,tbl,link_id):
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
        description,reference = self._getDescriptionDoc(document)
##        # Discard peer reviews
##        if description not in ("Inspection Sheet","Peer Review Register"):
        # Check if document already exists
        find = False
        for lref,ldoc_name,lreference,lversion,ldescription in tbl:
            if ldoc_name == doc_name and lreference == reference and lversion == version:
                find = True
                break
        if not find:
            link_id += 1
            ref = "[R{:d}]".format(link_id)
            tbl.append([ref,doc_name,reference,version,description])
        return link_id

def main():
##    target_release = self.ihm.previous_release
##    release = self.ihm.release
##    baseline =  self.ihm.baseline
##    self.ccb_type = "SCR"#self.ihm.ccb_var_type.get()
##    self.detect_release = self.ihm.previous_release
##    self.impl_release = self.ihm.impl_release
##    self.cr_type = self.ihm.cr_type
    # self.list_cr_for_ccb = self._getListCRForCCB
    # tbl_cr = self.getPR_CCB("",True)
##    tableau_pr = []
##    tableau_pr.append(["","","","",""])
##    environmenet = {"System":system,"Item":item,"Component":component}
##    review_number = self.ihm.var_review_type.get()
##    part_number = self.ihm.part_number_entry.get()
##    checksum = self.ihm.checksum_entry.get()
    review_number = 3
    subject = Review.getReviewList(review_number)
    checksum = "0XCAFE"
    part_number = "ECE24A3310201"
    release = "SW_ENM/01"
    baseline = "SW_ENM_01_01"

    result = Review.getChecks(review_number)
    # Create table
    tbl_inputs_check = []
    header = ["Nb.	Item","Category","Item","Compliance status","Non compliance description / Justification","Actions"]
    tbl_inputs_check.append(header)
    nb_item = 1
    for rank,description,category in result:
        tbl_inputs_check.append([nb_item,category,description,"OK/NOK/NA","",""])
        nb_item += 1
    print "INPUT ITEM CHECK",tbl_inputs_check

    project_list = []
    project_list.append([release,baseline,""])
    review = Review(review_number,
                    detect_release="",
                    impl_release="",
                    tbl_cr_for_ccb=[["45","Allo Houston, we have a problem","Major","In Review","No comments."]],
                    session_started = False,
                    project_list=project_list,
                    system="Dassault F5X PDS",
                    item="ESSNESS",
                    component="ENM",
                    part_number="ECE24A3310201",checksum="0xCAFE",subject=subject,
                    reference="ET1234-S",
                    issue="1.0",
                    review_qams_id="350")
    review.createReviewReport()

if __name__ == '__main__':
    main()
