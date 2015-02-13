#!/usr/bin/env python 2.7.3
# # -*- coding: latin-1 -*-
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
# TODO: Suppress getPR_CCB and in BuidDoc class
#
#
import logging

from tool import Tool
from synergy import Synergy
from api_mysql import MySQL
import time
# For ToolPatchReview
import sys
sys.path.append("python-docx")
import docx
import copy
import re
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
from ccb import CCB
# patch docx
nsprefixes = {
    'mo': 'http://schemas.microsoft.com/office/mac/office/2008/main',
    'o': 'urn:schemas-microsoft-com:office:office',
    've': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    # Text Content
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    # Drawing
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'mv': 'urn:schemas-microsoft-com:mac:vml',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'v': 'urn:schemas-microsoft-com:vml',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    # Properties (core and extended)
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    # Content Types
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
    # Package Relationships
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
    # Dublin Core document properties
    'dcmitype': 'http://purl.org/dc/dcmitype/',
    'dcterms': 'http://purl.org/dc/terms/'}


def advReplace(document, search, replace, bs=3):
    """Replace all occurences of string with a different string, return updated document

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

    """
    # Enables debug output
    DEBUG = False

    newdocument = document

    # Compile the search regexp
    searchre = re.compile(search)

    # Will match against searchels. Searchels is a list that contains last
    # n text elements found in the document. 1 < n < bs
    searchels = []

    for element in newdocument.iter():
        if element.tag == '{%s}t' % nsprefixes['w']:  # t (text) elements
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
                for l in range(1, len(searchels) + 1):
                    if found:
                        break
                    #print "slen:", l
                    for s in range(len(searchels)):
                        if found:
                            break
                        if s + l <= len(searchels):
                            e = range(s, s + l)
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
                                    print "Matched text (splitted):", map(lambda i: i.text, searchels)
                                    print "Matched at position:", match.start()
                                    print "matched in elements:", e
                                    if isinstance(replace, etree._Element):
                                        print "Will replace with XML CODE"
                                    elif type(replace) == list or type(replace) == tuple:
                                        print "Will replace with LIST OF ELEMENTS"
                                    else:
                                        print "Will replace with:", re.sub(search, replace, txtsearch)

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
                                            searchels[i].text = re.sub(search, '', txtsearch)
                                            searchels[i].append(replace)
                                        elif type(replace) == list or type(replace) == tuple:
                                            # I'm replacing with a list of etree elements
                                            searchels[i].text = re.sub(search, '', txtsearch)
                                            for r in replace:
                                                searchels[i].append(r)
                                        else:
                                            # Replacing with pure text
                                            searchels[i].text = re.sub(search, replace, txtsearch)
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

    def replaceTag(self, doc, tag, replace, fmt=None):
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
        if not fmt: fmt = {}
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
            repl = self._table(replace[1], fmt)
        elif replace[0] == 'img':
            relationships = docx.relationshiplist()
            relationshiplist, repl = self.picture_add(relationships, replace[1], 'This is a test description')
            return advReplace(doc, '\{\{' + re.escape(tag) + '\}\}', repl), relationshiplist
        elif replace[0] == 'mix':
            num_begin = ord("a")
            num_end = ord("z")
            num = num_begin
            prefix = ""
            repl = []
            dico = replace[1]
            for key, value in dico.items():
                if key[0] == "checklist":
                    par = [(prefix + chr(num) + ") " + dico['domain'] + " " + key[1], 'rb')]
                    elt = self._par(par)
                    num += 1
                    if num > num_end:
                        prefix += "a"
                        num = num_begin
                    repl.append(elt)
                    elt = self._table(value, fmt)
                    repl.append(elt)
                    par = [("Conclusion of CR review:", '')]
                    elt = self._par(par)
                    repl.append(elt)
                    par = [("CR Transition to state:", '')]
                    elt = self._par(par)
                    repl.append(elt)
        else:
            raise NotImplementedError, "Unsupported " + replace[0] + " tag type!"
        # Replace tag with 'lxml.etree._Element' objects
        result = advReplace(doc, '\{\{' + re.escape(tag) + '\}\}', repl, 6)
        ##        result = docx.advReplace_new(doc, '\{\{'+re.escape(tag)+'\}\}', repl,6)
        return result


class Log():
    def __init__(self):
        pass

    @staticmethod
    def log(text="", display_gui=True):
        """
        Log messages
        """
        print text


class SynergyPatchReview(ToolPatchReview):
    def __init__(self, session_started):
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
    """
       Model of review
       Reviews are managed by 4 tables:
           review_types
               id
               name
               description
               objective
               transition
               conclusion

           review_checklists_dispatch
                id
                review_id: ->
                                review_types.id
                category_id: ->
                                category_checklist.id
                rank: how items are sorted
                sub_category: ex: Standards
                check_id: ->
                                review_checklists.id

           review_checklists
               id
               name: ex: SwDD document is developed and under configuration management control: {{SWDD_DOC}}
               level: 1,2 or 3

           category_checklist
                id
                name: ex: Input Items Check

           review_types id ----
    """
    sw_checklists_db_filename = ""
    pld_checklists_db_filename = ""
    board_checklists_db_filename = ""
    eqpt_checklists_db_filename = ""
    default_checklists_db_filename = ""
    def __init__(self,
                 review_number=1,
                 detect_release="",
                 impl_release="",
                 session_started=False,
                 **kwargs):

        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        self.tbl_inspection_sheets = []
        self.dico_doc = {}
        self.object_integrate = False
        self.object_released = False
        self.ccb_type = "SCR"  #self.ihm.ccb_var_type.get()
        self.docx_filename = False

        self.detect_release = detect_release
        self.impl_release = impl_release

        self.review_number = review_number
        if "ihm" in self.__dict__:
            Synergy.__init__(self, session_started,self.ihm)
        else:
            Synergy.__init__(self, session_started)

        if review_number in range(1,20):  # Software Reviews
            review_domain = "SW"
        elif review_number in range(30,39):  # PLD Reviews
            review_domain = "PLD"
        elif review_number in range(40,49):  # Board Reviews
            review_domain = "BOARD"
        elif review_number in range(50,59):  # Eqpt Reviews
            review_domain = "EQPT"
        else:
            review_domain = "GENERIC"
        self._loadSQLConfig(review_domain)

        self.subject = self.getReviewList(review_number,review_domain)

    def _loadSQLConfig(self,review_domain="SW"):
        def getChecklistDbFilename(filename_key="sw_checklists_db"):
            db_filename = self.getOptions("SQL",filename_key)
            if db_filename == "":
                db_filename = "default_checklists_db.db3"
            return db_filename
        self.gen_dir = "result"
        try:
            # get generation directory
            self.gen_dir = self.getOptions("Generation","dir")

            self.sw_checklists_db_filename = getChecklistDbFilename("sw_checklists_db")
            self.pld_checklists_db_filename = getChecklistDbFilename("pld_checklists_db")
            self.board_checklists_db_filename = getChecklistDbFilename("board_checklists_db")
            self.eqpt_checklists_db_filename = getChecklistDbFilename("eqpt_checklists_db")
            self.default_checklists_db_filename = getChecklistDbFilename("sw_checklists_db")

            print "Review module config reading succeeded"
            self.selectDatabase(review_domain)
            print "database",self.database
        except IOError as exception:
            print "Review module config reading failed:", exception

    def getChecks(self,
                  review_id=3,
                  category_id=0):
        """
        From SQLite tables review_checklists_dispatch and review_checklists and review_types

        :param review_id:
        :param category_id:
        :return: rank description category sub_category level
        """

        database=self.database
        print "database",database
        if category_id == 0:
            query = "SELECT review_checklists_dispatch.rank,review_checklists.name,category_checklist.name as category,review_checklists_dispatch.sub_category,review_checklists.level FROM review_checklists \
                        LEFT OUTER JOIN review_checklists_dispatch ON review_checklists_dispatch.check_id = review_checklists.id \
                        LEFT OUTER JOIN review_types ON review_checklists_dispatch.review_id = review_types.id \
                        LEFT OUTER JOIN category_checklist ON review_checklists_dispatch.category_id = category_checklist.id \
                        WHERE review_types.id LIKE '{:d}' ".format(review_id)
        else:
            query = "SELECT review_checklists_dispatch.rank,review_checklists.name,review_checklists_dispatch.sub_category,review_checklists.level FROM review_checklists \
                        LEFT OUTER JOIN review_checklists_dispatch ON review_checklists_dispatch.check_id = review_checklists.id \
                        LEFT OUTER JOIN review_types ON review_checklists_dispatch.review_id = review_types.id \
                        WHERE review_types.id LIKE '{:d}' AND review_checklists_dispatch.category_id LIKE '{:d}' ".format(
                review_id, category_id)
        result = Tool.sqlite_query(query,database)

        print "RESULT", result
        return result

    def getName(self,review_id=3):
        """
            from SQLite tables review_checklists and review_types
        """
        database=self.database
        print "DATABASE",self.database
        query = "SELECT name FROM review_types \
                    WHERE review_types.id LIKE '{:d}' ".format(review_id)
        result = Tool.sqlite_query_one(query,database)
        print result
        if result is None or result[0] is None:
            txt = "None"
        else:
            txt = result[0]
        return txt

    def getObjective(self,review_id=3):
        """
            from SQLite tables review_checklists_dispatch and review_checklists and review_types
        """
        database=self.database
        print "DATABASE",self.database
        query = "SELECT objective FROM review_types \
                    WHERE review_types.id LIKE '{:d}' ".format(review_id)
        result = Tool.sqlite_query_one(query,database)
        print result
        if result is None or result[0] is None:
            txt = "None"
        else:
            txt = result[0]
        return txt

    def getTransition(self,review_id=3):
        """
            from SQLite tables review_checklists_dispatch and review_checklists and review_types
        """
        database=self.database
        query = "SELECT transition FROM review_types \
                    WHERE review_types.id LIKE '{:d}' ".format(review_id)
        result = Tool.sqlite_query_one(query,database)
        if result is None or result[0] is None:
            txt = "None"
        else:
            txt = result[0]
        return txt

    def getConclusion(self,review_id=3):
        """
            from SQLite tables review_checklists_dispatch and review_checklists and review_types
        """
        database=self.database
        query = "SELECT conclusion FROM review_types \
                    WHERE review_types.id LIKE '{:d}' ".format(review_id)
        result = Tool.sqlite_query_one(query,database)
        if result is None or result[0] is None:
            txt = "None"
        else:
            txt = result[0]
        return txt

    def selectDatabase(self,review_domain):
        if review_domain == "SW":
            self.database=self.sw_checklists_db_filename
        elif review_domain == "PLD":
            self.database = self.pld_checklists_db_filename
        elif review_domain == "Board":
            self.database=self.board_checklists_db_filename
        elif review_domain == "EQPT":
            self.database=self.eqpt_checklists_db_filename
        else:
            self.database=self.default_checklists_db_filename

    def getReviewList(self,
                      review_type_id="",
                      review_domain="SW"):
        """
        Method to get list of reviews (PR,SRR,etc.)
        """
        self.selectDatabase(review_domain)
        database=self.database
        print "getReviewList database",review_domain,database

        if review_type_id == "":
            query = "SELECT id,description FROM review_types"
            result = Tool.sqlite_query(query,database)
            if result is None:
                reviews_list = "None"
            else:
                reviews_list = result
            return reviews_list
        else:
            query = "SELECT description FROM review_types WHERE id LIKE '{:d}'".format(review_type_id)
            result = Tool.sqlite_query_one(query,database)
            if result is None:
                description = "None"
            else:
                description = result[0]
            return description

    @staticmethod
    def _getIinspectionSheetList(is_doc):
        if not is_doc:
            is_doc.append(["", "None"])
            return is_doc
        else:
            is_doc_filtered = sorted(set(is_doc))
        is_doc_tbl = []
        for item in is_doc_filtered:
            is_doc_tbl.append(["", item])
        return is_doc_tbl

    def replaceDocTag(self,text,dico):
        """

        :param text:
        :param dico:
        :return:
        """
        for tag, doc in dico.iteritems():
            print "Tag",tag,doc
            text = re.sub('\{\{'+re.escape(tag)+'\}\}',doc,text)
        return text

    def createChecksTable(self,review_number,type_check_id,tbl_check,dico,nb_item=1,selected_level=2):
        """
        :return:
        """
        result = self.getChecks(review_number, type_check_id)

        for rank, description, category, level in result:
            nb_item_str = "{:d}".format(nb_item)
            # Replace tag by documents name found
            description = self.replaceDocTag(description,dico)
            if level is None or int(selected_level) >= level:
                justification = ""
                compliance_status = "OK/NOK/NA"
            else:
                justification = "Not applicable for conformity level {:s}".format(selected_level)
                compliance_status = "NA"
            tbl_check.append([nb_item_str, description, compliance_status,justification, ""])
            nb_item += 1
        if len(tbl_check) == 1:
            tbl_check.append(["--", "--", "--", "--", "--"])
        print "tbl_check",tbl_check
        return nb_item

    def createInputChecksTable(self,review_number,type_check_id,tbl_check,dico,nb_item=1):
        """
        :return:
        """
        result = self.getChecks(review_number, type_check_id)

        for rank, description, category,level in result:
            nb_item_str = "{:d}".format(nb_item)
            # Replace tag by documents name found
            description = self.replaceDocTag(description,dico)
            tbl_check.append([nb_item_str, category, description, "OK/NOK/NA", "", ""])
            nb_item += 1
        if len(tbl_check) == 1:
            tbl_check.append(["--", "--", "--", "--", "--", "--"])
        print "tbl_check",tbl_check
        return nb_item

    def getDataSheet(self,
                     keywords,
                     project,
                     baseline,
                     release):
        # datasheet_folder = self.getFolderName("*Data*sheet*")#getDataSheetFolderName()
        # list_data_sheets = self.getFromFolder(datasheet_folder,project)
        # converted_list_datasheets = []
        # for data_sheet in list_data_sheets:
        #     m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',data_sheet)
        #     if m:
        #         doc = "{:s} issue {:s}".format(m.group(1),m.group(2))
        # DATA SHEETS
        data_sheets_str = ""
        list_datasheets = []
        converted_list_datasheets = []
        for keyword in keywords:
            result = self.getItemsInFolder(keyword,
                                              project,
                                              baseline,
                                              release)
            if result != []:
                if converted_list_datasheets == []:
                    converted_list_datasheets = result
                else:
                    converted_list_datasheets.append(result)
        if converted_list_datasheets:
            print "getDataSheet L616"
            data_sheets_str = "\n ".join(map(str, converted_list_datasheets))
            return data_sheets_str
        else:
            print "getDataSheet L620"
            # is it a child of Input Data ?
            folder_info = self.getFolderName(keyword,
                                             project,
                                             baseline,
                                             release)
            # result should like this Input Data-1:dir:2
            if folder_info:
                print "folder_info",folder_info
                # getFromFolder method needs a project
                list_folders = self.getFromFolder(folder_info,project,False)
                print "LISTFOLDERS",list_folders
                for sub_folder_info in list_folders:
                    m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',sub_folder_info)
                    if m:
                        dirname = m.group(1)
                        #print "DIRNAME",dirname
                        m = re.match(r'Data ?sheet|Errata',dirname,re.IGNORECASE)
                        if m:
                            # getFromFolder method needs a project
                            sub_list_folders = self.getFromFolder(sub_folder_info,project)
                            for sub_folder in sub_list_folders:
                                m = re.match(r'^(.*)-(.*):(.*):([0-9]*)$',sub_folder)
                                if m:
                                    doc = "{:s} issue {:s}".format(m.group(1),m.group(2))
                                    list_datasheets.append(doc)
                            # we found Datasheet folder
                            break
                data_sheets_str = "\n ".join(map(str, list_datasheets))
            else:
                data_sheets_str = False
        return data_sheets_str

    def createReviewReport(self,
                           empty=False,
                           number=30,
                           detect_release="",
                           impl_release=""):
        """
        Create review report using docx module
        """
        def getCRDomain(review_number,ihm):
            if review_number in range(1,20):  # Software Reviews
                review_domain = "SW"
                cr_type = "SCR"
            elif review_number in range(30,39):  # PLD Reviews
                review_domain = "PLD"
                cr_type = "PLDCR"
            elif review_number in range(40,49):  # Board Reviews
                review_domain = "BOARD"
                cr_type = "SACR"
            elif review_number in range(50,59):  # Eqpt Reviews
                review_domain = "EQPT"
                cr_type = "ECR"
            else:
                review_domain = ""
                cr_type = ihm.getCR_Domain()
            ihm.forceCCBType(cr_type)
            return review_domain

        reference = self.reference
        issue = self.issue
        target_release = self.impl_release
        if target_release == "":
            target_release = "All releases"
        review_number = self.review_number
        conformity_level = "{:d}".format(self.conformity_level)

        sci_doc = "None"
        seci_doc = "None"
        sas_doc = "None"
        sci_is = "None"
        seci_is = "None"
        sas_is = "None"

        # tableau_pr = []
        # tableau_pr.append(["CR ID", "Synopsis", "Severity", "Status", "Comment/Impact/Risk"])
        # tableau_pr.append(self.tbl_cr)

        cr_domain = getCRDomain(number,self.ihm)
        #
        # Creation of CR table
        #
        ccb = CCB(self.ihm,
                  system=self.ihm.system,
                  item=self.ihm.item)
        ccb.setDetectRelease(detect_release)
        ccb.setImplRelease(impl_release)
        list_cr_for_ccb,status_list = self.ihm._getListCRForCCB()
        print "list_cr_for_ccb in synergy_thread",list_cr_for_ccb
        ccb.setListCR(list_cr_for_ccb,status_list)
        # Set CR domain
        ccb.setDomain(cr_domain)
        cr_with_parent = True
        if not empty:
            tableau_pr_unsorted,found_cr = ccb.getPR_CCB(cr_status="",
                                                    for_review=True,
                                                    cr_with_parent=cr_with_parent)
        else:
            tableau_pr_unsorted = ccb.fillPRTable(for_review=True,
                                             cr_with_parent=cr_with_parent)

        print "tableau_pr_unsorted",tableau_pr_unsorted
        # tableau_pr_sorted = sorted(tableau_pr_unsorted,key=ccb._getSeverity)
        tableau_pr= []
        tableau_pr.append(["CR ID", "Synopsis", "Severity", "Status", "Comment/Impact/Risk"])
        # if ccb_type == "SCR" and \
        #         not cr_with_parent:
        #     tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity"])
        # else:
        #    tableau_pr.append(["Domain","CR Type","ID","Status","Synopsis","Severity","Detected on","Implemented for","Parent CR"])
        tableau_pr.extend(tableau_pr_unsorted)

        if self.component != "":
            ci_identification = self.getComponentID(self.component)
        else:
            ci_identification = self.get_ci_sys_item_identification(self.system, self.item)

        date_report = time.strftime("%d %b %Y", time.localtime())

        colw_pr = [500,  # CR ID
                   2500,  # Synopsis
                   500,  # Severity
                   500,  # Status
                   1000]  # Comment

        colw_baseline = [500,  # Ref ID
                         1000,  # Name
                         500,  # Reference
                         500,  # Version
                         2500]  # Description

        colw_input_checks = [500,  # Ref ID
                             500,  # Name
                             2000,  # Reference
                             500,  # Version
                             1000,
                             500]  # Description
        colw_checks = [500,  # Ref ID
                         2000,  # Reference
                         1000,  # Version
                         1000,
                         500]  # Description

        colw_scope = [1000,  #
                     1000,  #
                     1000,  #
                     1000,  #
                     1000]  #

        colw_action = [250,  # ID
                       500,  # Origin
                       2000,  # Action
                       500,  # Impact
                       250,  # Severity
                       250,  # Assignee
                       500,  # Closure
                       250,  # Status
                       1000]  # 5000 = 100%
        fmt_pr = {
            'heading': True,
            'colw': colw_pr,  # 5000 = 100%
            'cwunit': 'pct', 'tblw': 5000, 'twunit': 'pct',
            'borders': {'all': {'color': 'auto', 'space': 0, 'sz': 6, 'val': 'single', }}
        }
        fmt_baseline = {
            'heading': True,
            'colw': colw_baseline,  # 5000 = 100%
            'cwunit': 'pct', 'tblw': 5000, 'twunit': 'pct',
            'borders': {'all': {'color': 'auto', 'space': 0, 'sz': 6, 'val': 'single', }}
        }
        fmt_ipnut_checks = {
            'heading': True,
            'colw': colw_input_checks,  # 5000 = 100%
            'cwunit': 'pct', 'tblw': 5000, 'twunit': 'pct',
            'borders': {'all': {'color': 'auto', 'space': 0, 'sz': 6, 'val': 'single', }}
        }
        fmt_checks = {
            'heading': True,
            'colw': colw_checks,  # 5000 = 100%
            'cwunit': 'pct', 'tblw': 5000, 'twunit': 'pct',
            'borders': {'all': {'color': 'auto', 'space': 0, 'sz': 6, 'val': 'single', }}
        }
        fmt_scope = {
            'heading': True,
            'colw': colw_scope,  # 5000 = 100%
            'cwunit': 'pct', 'tblw': 5000, 'twunit': 'pct',
            'borders': {'all': {'color': 'auto', 'space': 0, 'sz': 6, 'val': 'single', }}
        }
        fmt_action = {
            'heading': True,
            'colw': colw_action,  # 5000 = 100%
            'cwunit': 'pct', 'tblw': 5000, 'twunit': 'pct',
            'borders': {'all': {'color': 'auto', 'space': 0, 'sz': 6, 'val': 'single', }}
        }
        fmt_two = {
            'heading': False,
            'colw': [2000, 3000],  # 5000 = 100%
            'cwunit': 'pct', 'tblw': 5000, 'twunit': 'pct'
        }
        fmt_one = {
            'heading': False,
            'colw': [500, 4500],  # 5000 = 100%
            'cwunit': 'pct', 'tblw': 5000, 'twunit': 'pct'
        }
        self._clearDicofound()
        self.tbl_inspection_sheets = []
        part_number = self.part_number
        checksum = self.checksum
        subject = self.subject
        # Documents dictionary set
        dico_plan_doc = {"PSAC": "Plan for Software Aspect of Certification",
                         "SDP": "Software Development Plan",
                         "SVP": "Software Verification Plan",
                         "SCMP": "Software Configuration Management Plan",
                         "SQAP": "Software Quality Assurance Plan",
                         "SRTS": "Software Requirement Test Standard",
                         "SDTS": "Software Design Test Standard",
                         "SCS": "Software Coding Standard"}
        dico_sas = {"SAS": "Software Accomplishment Summary"}
        dico_sci = {"SCI": "Software Configuration Index"}
        dico_seci = {"SECI": "Software Environment Configuration Index"}
        dico_spec = {"SWRD": "Software Requirements Data"}
        dico_upper = {"SPI": "SPI Interface Document",
                      "ICD": "Interface Control Document",
                      "HSID": "Hardware Software Interface Document",
                      "SSCS": "Board Specification Document"}
        # Inspection sheets dictionary set
        dico_is = {"IS_PSAC": "PSAC Inspection Sheet",
                   "IS_SDP": "SDP Inspection Sheet",
                   "IS_SVP": "SVP Inspection Sheet",
                   "IS_SCMP": "SVP Inspection Sheet",
                   "IS_SQAP": "SQAP Inspection Sheet",
                   "IS_SCI": "SCI Inspection Sheet",
                   "IS_SAS": "SAS Inspection Sheet",
                   "IS_SECI": "SECI Inspection Sheet",
                   "IS_SWRD": "SwRD Inspection Sheet"}
        # Voir si on peu pas faire mieux
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

        # Delivery documents
        sci_doc = "No " + dico_sci["SCI"]
        seci_doc = "No " + dico_seci["SECI"]
        sas_doc = "No " + dico_sas["SAS"]

        # Checksum
        dico_log = {"checksum": "checksum"}
        make_log = "No " + dico_log["checksum"]


        # Counter reset
        index_sci = 0
        index_seci = 0
        index_sas = 0

        index_is = 0
        index_prr = 0
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
        sqar_doc = []
        mysql = MySQL()
        if self.review_qams_id != "":
            date_meeting = mysql.getReviewDate(self.review_qams_id)
        else:
            date_meeting = date_report
        # Liste d'actions vierge

        # Accès base MySQL QAMS pour les actions et les revues
        if self.review_qams_id != "":
            list_id,sqar_doc_tmp = mysql.getPreviousReviewsRecords(self.review_qams_id,impl_release)
            sqar_doc = list(sqar_doc_tmp)
        tbl_previous_actions_whdr = []
        tbl_current_actions_whdr = []
        header = ["Action item ID",
                  "Origin",
                  "Action",
                  "Impact",
                  "Severity",
                  "Assignee",
                  "Closure due date",
                  "Status",
                  "Closing proof"]
        tbl_previous_actions_whdr.append(header)
        tbl_current_actions_whdr.append(header)
        if not empty:
            tbl_previous_actions = mysql.exportPreviousActionsList(self.review_qams_id,recur=True,open=True)
            tbl_actions = mysql.exportActionsList(self.review_qams_id)
        else:
            tbl_previous_actions = False
            tbl_actions = False
        if not tbl_previous_actions:
            tbl_previous_actions_whdr.append(["--", "--", "--", "--", "--", "--", "--", "--", "--"])
        else:
            tbl_previous_actions_whdr.extend(tbl_previous_actions)
        if not tbl_actions:
            tbl_current_actions_whdr.append(["--", "--", "--", "--", "--", "--", "--", "--", "--"])
        else:
            tbl_current_actions_whdr.extend(tbl_actions)

        # Accès base MySQL QAMS pour les personnes qui assistent à la réunion
        if self.review_qams_id != "":
            tbl_attendees = mysql.exportAttendeesList(self.review_qams_id)
        else:
            tbl_attendees = [[self.author, "Function"]]
        # List of missing
        if self.review_qams_id != "":
            tbl_missing = mysql.exportAttendeesList(self.review_qams_id, True)
        else:
            tbl_missing = [["Name", "Function"]]
        # List of copies
        if self.review_qams_id != "":
            tbl_copies = [["Marc Maufret", "QA team leader"]]
        else:
            tbl_copies = [["Name", "Function"]]
        objective = self.getObjective(review_number)
        transition = self.getTransition(review_number)

        conclusion = self.getConclusion(review_number)
        conclusion = self.replaceDocTag(conclusion,{"CONFLEVEL":conformity_level,
                                                    "PART_NUMBER":part_number})
        user_info_sw={"name":self.author,
                   "mail":"olivier.appere@zodiacaerospace.com"}
        user_info_pld = user_info_sw
        # user_info_pld={"name":"H. Bollon",
        #            "mail":"henri.bollon@zodiacaerospace.com"}

        if review_number in range (30,39):
            user_info = user_info_pld
        else:
            user_info = user_info_sw
        print "fmt_pr",fmt_pr
        print "tableau_pr",tableau_pr
        if not empty:
            list_tags_basics = {
                'Name': {'type': 'str', 'text': user_info["name"], 'fmt': {}},
                'DateMe': {'type': 'str', 'text': date_meeting, 'fmt': {}},
                'Date': {'type': 'str', 'text': date_report, 'fmt': {}},
                'Subject': {'type': 'str', 'text': subject, 'fmt': {}},
                'SUBJECT': {'type': 'str', 'text': subject.upper(), 'fmt': {}},
                'Service': {'type': 'str', 'text': 'Quality Department', 'fmt': {}},
                'Place': {'type': 'str', 'text': 'Montreuil', 'fmt': {}},
                'Ref': {'type': 'str', 'text': reference, 'fmt': {}},
                'Issue': {'type': 'str', 'text': issue, 'fmt': {}},
                'Tel': {'type': 'str', 'text': '', 'fmt': {}},
                'Fax': {'type': 'str', 'text': '', 'fmt': {}},
                'Email': {'type': 'str', 'text': user_info["mail"], 'fmt': {}},
                'TGT_REL': {'type': 'str', 'text': target_release, 'fmt': {}},
                'CSCI': {'type': 'str', 'text': ci_identification, 'fmt': {}},
                'CONFLEVEL': {'type': 'str', 'text': conformity_level, 'fmt': {}},
                'SW_LEVEL': {'type': 'str', 'text': 'B', 'fmt': {}},
                'PART_NUMBER': {'type': 'str', 'text': part_number, 'fmt': {}},
                'CHECKSUM': {'type': 'str', 'text': checksum, 'fmt': {}},
                'TBL_CR': {'type': 'tab', 'text': tableau_pr, 'fmt': fmt_pr},
                'ATTENDEES': {'type': 'tab', 'text': tbl_attendees, 'fmt': fmt_two},
                'MISSING': {'type': 'tab', 'text': tbl_missing, 'fmt': fmt_two},
                'COPIES': {'type': 'tab', 'text': tbl_copies, 'fmt': fmt_two},
                'OBJECTIVE': {'type': 'str', 'text': objective, 'fmt': {}},
                'TRANSITION': {'type': 'str', 'text': transition, 'fmt': {}},
                'CONCLUSION': {'type': 'str', 'text': conclusion, 'fmt': {}},
                'PREVIOUS_ACTIONS': {'type': 'tab', 'text': tbl_previous_actions_whdr, 'fmt': fmt_action},
                'CURRENT_ACTIONS': {'type': 'tab', 'text': tbl_current_actions_whdr, 'fmt': fmt_action}
            }
        else:
            list_tags_basics = {
                'TBL_CR': {'type': 'tab', 'text': tableau_pr, 'fmt': fmt_pr},
                'ATTENDEES': {'type': 'tab', 'text': tbl_attendees, 'fmt': fmt_two},
                'MISSING': {'type': 'tab', 'text': tbl_missing, 'fmt': fmt_two},
                'COPIES': {'type': 'tab', 'text': tbl_copies, 'fmt': fmt_two},
                'OBJECTIVE': {'type': 'str', 'text': objective, 'fmt': {}},
                'TRANSITION': {'type': 'str', 'text': transition, 'fmt': {}},
                'CONCLUSION': {'type': 'str', 'text': conclusion, 'fmt': {}},
                'PREVIOUS_ACTIONS': {'type': 'tab', 'text': tbl_previous_actions_whdr, 'fmt': fmt_action},
                'CURRENT_ACTIONS': {'type': 'tab', 'text': tbl_current_actions_whdr, 'fmt': fmt_action}
            }
        baseline_doc = ""
        release_doc = ""
        project_doc = ""
        baseline_store = []
        release_store = []
        project_store = []
        link_id = 0

        header = ["Ref", "Name", "Reference", "Version", "Description"]
        tbl_plans_doc = [header]
        tbl_upper_doc = [header]
        tbl_output_doc = [header]
        tbl_inspection_doc = [header]
        tbl_peer_review_doc = [header]
        tbl_transition_doc = [header]

        dal_doc = ""
        # Standards
        srts_doc = ""
        sdts_doc = ""

        # Specifications
        swrd_doc = ""
        shldr_doc = ""
        # Design
        swdd_doc = ""
        slldr_doc = ""
        hsid_doc = ""

        # Interfaces
        icd_doc = ""

        # Inspections
        swdd_is = ""

        cur_doc = []
        tbl_prr = []
        tbl_plans = []
        ccb_doc = []
        list_datasheets = []

        for release, baseline, project in self.project_list:
            input_data_keyword = "Input*Data"
            datasheet_keyword = ["Data*[s|S]heet","Errata"]
            design_keyword = "S[w|W]DD"
            # No project selected ?
            if Tool.isAttributeValid(release) and \
                    Tool.isAttributeValid(baseline) and \
                    not Tool.isAttributeValid(project) :
                # We have a baseline but no project
                # input_data_keyword = "Input ?Data"
                # datasheet_keyword = "Data ?sheet"
                # design_keyword = "S[w|W]DD"
                # Test get projects
                list_projects = self._getProjectsList_wo_ihm(release,
                                                             baseline)
                print "TEST list_projects in reviews.py module",list_projects
            else:
                list_projects = [project]
            output = self.getArticles(("pdf", "doc", "xls", "ascii","dir"),
                                      release,
                                      baseline,
                                      project,
                                      False)
            #if baseline not in baseline_store:
            baseline_store.append(baseline)
            #if release not in release_store:
            release_store.append(release)
            #if project not in project_store:
            project_store.append(project)
            data_sheets_str = ""
            for found_project in list_projects:
                result = self.getDataSheet(datasheet_keyword,
                                            found_project,
                                            baseline,
                                            release)
                if result:
                    data_sheets_str = result
                    break

            print "datasheet:",data_sheets_str
            # INPUT DATA
            list_input_data_str = ""
            list_input_data = []
            for found_project in list_projects:
                list_input_data = self.getItemsInFolder(input_data_keyword,
                                                        found_project,
                                                        baseline,
                                                        release)
                if list_input_data != []:
                    break
            if list_input_data:
                list_input_data_str = "\n ".join(map(str, list_input_data))
            else:
                list_input_data_str = ""
            print "input data:",list_input_data_str
            # DESIGN
            list_design_document_str = ""
            list_design_document = []
            for found_project in list_projects:
                list_design_document = self.getItemsInFolder(design_keyword,
                                                             found_project,
                                                             baseline,
                                                             release,
                                                             exclude=["IS_"])
                if list_design_document != []:
                    break
            if list_design_document:
                list_design_document_str = "\n ".join(map(str, list_design_document))
            else:
                list_design_document_str = ""
            print "design:",list_design_document_str
            for line in output:
                line = re.sub(r"<void>", r"", line)
                self.ihm.log("Found doc: " + line, False)
                m = re.match(r'(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*)', line)
                if m:
                    #
                    # Look for IS first
                    #
                    if self._getSpecificDoc(m, "IS_SAS", ("xls")):
                        index_is += 1
                        sas_is = self.getDocName(m)
                    elif self._getSpecificDoc(m, "IS_SCI", ("xls")):
                        index_is += 1
                        sci_is = self.getDocName(m)
                    elif self._getSpecificDoc(m, "IS_SECI", ("xls")):
                        index_is += 1
                        seci_is = self.getDocName(m)
                    elif self._getSpecificDoc(m, "IP_SW", ("pdf")) or self._getSpecificDoc(m, "CRI_", ("pdf")):
                        index_doc += 1
                        name = self.getDocName(m)
                        cur_doc.append(name)
                    # Look for inspection sheet
                    elif self._getSpecificDoc(m, "IS_PSAC", ("xls")):
                        index_is += 1
                        name = self.getDocName(m)
                        psac_is.append(name)
                    elif self._getSpecificDoc(m, "IS_SDP", ("xls")):
                        index_is += 1
                        name = self.getDocName(m)
                        sdp_is.append(name)
                    elif self._getSpecificDoc(m, "IS_SVP", ("xls")):
                        index_is += 1
                        name = self.getDocName(m)
                        svp_is.append(name)
                    elif self._getSpecificDoc(m, "IS_SCMP", ("xls")):
                        index_is += 1
                        name = self.getDocName(m)
                        scmp_is.append(name)
                    elif self._getSpecificDoc(m, "IS_SQAP", ("xls")):
                        index_is += 1
                        name = self.getDocName(m)
                        sqap_is.append(name)
                    elif self._getSpecificDoc(m, "IS_SWRD", ("xls")) or self._getSpecificDoc(m, "IS_SwRD", ("xls")):
                        index_is += 1
                        name = self.getDocName(m)
                        swrd_is.append(name)
                        link_id = self._createTblDocuments(m, tbl_inspection_doc, link_id)
                    #
                    # Extract Peer Review Register
                    #
                    elif self._getSpecificDoc(m, "PRR_", ("xls")):
                        index_prr += 1
                        name = self.getDocName(m)
                        if name not in tbl_prr:
                            tbl_prr.append(name)
                        link_id = self._createTblDocuments(m, tbl_peer_review_doc, link_id)
                    # Look for Software Accomplishment Summary
                    elif self._getSpecificDoc(m, "SAS", ("doc")):
                        index_is += 1
                        sas_doc = self.getDocName(m)
                    elif self._getSpecificDoc(m, "SCI", ("doc")):
                        index_is += 1
                        sci_doc = self.getDocName(m)
                    elif self._getSpecificDoc(m, "SECI", ("doc")):
                        index_is += 1
                        seci_doc = self.getDocName(m)
                    # Look for compilation log
                    elif self._getSpecificDoc(m, "checksum", ("ascii")):
                        index_log += 1
                        make_log = self.getDocName(m)
                    # Look for plans
                    elif self._getSpecificDoc(m, "PSAC", ("doc")) or \
                        self._getSpecificDoc(m, "SDP", ("doc")) or \
                        self._getSpecificDoc(m, "SVP", ("doc")) or \
                        self._getSpecificDoc(m, "SCMP", ("doc")) or \
                        self._getSpecificDoc(m, "SQAP", ("doc")):
                        index_plans += 1
                        link_id = self._createTblDocuments(m, tbl_upper_doc, link_id)
                        name = self.getDocName(m)
                        if name not in tbl_plans:
                            tbl_plans.append(name)
                        if self._getSpecificDoc(m, "PSAC", ("doc")):
                            psac_doc.append(name)
                        elif self._getSpecificDoc(m, "SDP", ("doc")):
                            sdp_doc = self.getDocName(m)
                        elif self._getSpecificDoc(m, "SVP", ("doc")):
                            svp_doc = self.getDocName(m)
                        elif self._getSpecificDoc(m, "SCMP", ("doc")):
                            scmp_doc = self.getDocName(m)
                        elif self._getSpecificDoc(m, "SQAP", ("doc")):
                            sqap_doc = self.getDocName(m)
                    elif self._getSpecificDoc(m, "SRTS_SW", ("pdf")):
                        index_doc += 1
                        srts_doc = self.getDocName(m)
                        link_id = self._createTblDocuments(m, tbl_upper_doc, link_id)
                    elif self._getSpecificDoc(m, "SDTS_SW", ("pdf")):
                        index_doc += 1
                        sdts_doc = self.getDocName(m)
                    elif self._getSpecificDoc(m, "SCS_SW", ("pdf")):
                        index_doc += 1
                        scs_doc = self.getDocName(m)
                    elif self._getSpecificDoc(m, "DAL", ("doc","pdf")):
                        index_doc += 1
                        dal_doc = self.getDocName(m)
                    elif self._getSpecificDoc(m, "SWRD", ("doc")) or \
                            self._getSpecificDoc(m, "SwRD", ("doc")) or \
                            self._getSpecificDoc(m, "PLDRD", ("doc","pdf")):
                        index_doc += 1
                        swrd_doc = self.getDocName(m)
                        link_id = self._createTblDocuments(m, tbl_output_doc, link_id)
                    elif self._getSpecificDoc(m, "SHLDR", ("xls")):
                        index_doc += 1
                        shldr_doc = self.getDocName(m)
                        link_id = self._createTblDocuments(m, tbl_output_doc, link_id)
                    # Upper documents
                    elif self._getSpecificDoc(m, "SSCS", ("doc", "pdf","xls")) or \
                            self._getSpecificDoc(m, "SDTS", ("doc", "pdf","xls")) or \
                            self._getSpecificDoc(m, "SES", ("doc", "pdf","xls")) or \
                            self._getSpecificDoc(m, "CAN_ICD", ("doc", "pdf","xls")) or \
                            self._getSpecificDoc(m, "IRD", ("doc", "pdf","xls")) or \
                            self._getSpecificDoc(m, "SPI_ICD", ("doc", "pdf","xls")):
                        index_doc += 1
                        name = self.getDocName(m)
                        if self._getSpecificDoc(m, "ICD_", ("doc", "pdf","xls")):
                            icd_doc = name
                        if name not in sys_doc:
                            sys_doc.append(name)
                            link_id = self._createTblDocuments(m, tbl_upper_doc, link_id)
                    elif self._getSpecificDoc(m, "HSID", ("doc", "pdf")) or \
                            self._getSpecificDoc(m, "HPID", ("doc", "xls","pdf")):
                        index_doc += 1
                        hsid_doc = self.getDocName(m)
                        link_id = self._createTblDocuments(m, tbl_transition_doc, link_id)
                    elif self._getSpecificDoc(m, "SWDD", ("doc")) or \
                        self._getSpecificDoc(m, "PLDDD", ("doc")) or \
                            self._getSpecificDoc(m, "SwDD", ("doc")):
                        index_doc += 1
                        swdd_doc = self.getDocName(m)
                    elif self._getSpecificDoc(m, "IS_SWDD", ("xls")) or \
                            self._getSpecificDoc(m, "IS_SwDD", ("xls")):
                        index_is += 1
                        swdd_is = self.getDocName(m)
                    elif self._getSpecificDoc(m, "SLLDR", ("xls")):
                        index_doc += 1
                        slldr_doc = self.getDocName(m)

                    # CCB minutes
                    elif self._getSpecificDoc(m, "CCB_Minutes", ("doc")):
                        index_doc += 1
                        name = self.getDocName(m)
                        ccb_release = self.getDocRelease(m)
                        if target_release == "" or ccb_release == target_release:
                            if name not in ccb_doc:
                                ccb_doc.append(name)
                        #link_id = self._createTblDocuments(m, tbl_upper_doc, link_id)

        if len(tbl_upper_doc) == 1:
            tbl_upper_doc.append(["--", "--", "--", "--", "--"])
        if len(tbl_output_doc) == 1:
            tbl_output_doc.append(["--", "--", "--", "--", "--"])
        if len(tbl_peer_review_doc) == 1:
            tbl_peer_review_doc.append(["--", "--", "--", "--", "--"])
        if len(tbl_inspection_doc) == 1:
            tbl_inspection_doc.append(["--", "--", "--", "--", "--"])

        sqar_doc_str = "\n ".join(map(str, sqar_doc))
        ccb_doc_str = "\n ".join(map(str, ccb_doc))
        peer_review_str = "\n ".join(map(str, tbl_prr))
        plans_str = "\n ".join(map(str, tbl_plans))
        sys_doc_str = "\n ".join(map(str, sys_doc))
        cur_doc_str = "\n ".join(map(str, cur_doc))
        psac_doc_str = "\n ".join(map(str, psac_doc))
        psac_is_str = "\n ".join(map(str, psac_is))
        sdp_is_str = "\n ".join(map(str, sdp_is))
        svp_is_str = "\n ".join(map(str, svp_is))
        scmp_is_str = "\n ".join(map(str, scmp_is))
        sqap_is_str = "\n ".join(map(str, sqap_is))
        swrd_is_str = "\n ".join(map(str, swrd_is))
        dico_conformity = {}
        # Change
        dico_change = {'CCB_MINUTES':ccb_doc_str}
        # Quality Assurance
        dico_quality = {'SQAR':sqar_doc_str}
         # Inputs
        dico_inputs = {}
        # Development
        dico_produced = {}
        # Verification
        dico_verif = {}
        # Conformity check
        dico_conformity = {}
        # Transition
        dico_transition = {}
        #
        # selection of reviews/audits
        #
        if review_number == 9:  # SCR
            review_string = "SCR"
            filename_header = "REV_SCR_{:s}_SQA_{:s}".format(self.cr_type,self.reference)
            if not empty:
                # Inputs
                dico_inputs = {}
                # Development
                dico_produced = {"SCI_DOC":sci_doc,
                                 "SECI_DOC":seci_doc,
                                 "SAS_DOC":sas_doc
                                 }
                # Verification
                dico_verif = {"SCI_IS":sci_is,
                             "SECI_IS":seci_is,
                             "SAS_IS":sas_is
                                 }
                # Conformity check
                dico_conformity = {'CCB_MINUTES':ccb_doc_str}
                # Transition
                dico_transition = {}
            else:
                # Shallow review
                # Change
                dico_change = {}
                # Quality Assurance
                dico_quality = {}
                 # Inputs
                dico_inputs = {}
                # Development
                dico_produced = {}
                # Verification
                dico_verif = {}
                # Conformity check
                dico_conformity = {}
                # Transition
                dico_transition = {}

        elif review_number == 1:  # PR:
            review_string = ""
            filename_header = "REV_PR_{:s}_SQA_{:s}".format(self.cr_type,self.reference)
            if not empty:
                # Inputs
                dico_inputs = {"DAL_DOC":dal_doc,
                               "CUS_DOC":cur_doc_str,
                               "SRTS_DOC":srts_doc,
                               "SDTS_DOC":sdts_doc,
                               "SCS_DOC":scs_doc}
                # Development
                dico_produced = {"PSAC_DOC":psac_doc_str,
                               "SDP_DOC":sdp_doc,
                               "SVP_DOC":svp_doc,
                               "SCMP_DOC":scmp_doc,
                               "SQAP_DOC":sqap_doc}
                # Verification
                dico_verif = {"PSAC_IS":psac_is_str,
                               "SDP_IS":sdp_is_str,
                               "SVP_IS":svp_is_str,
                               "SCMP_IS":scmp_is_str,
                               "SQAP_IS":sqap_is_str}
                # Transition
                dico_transition = {"SYS_DOC":sys_doc_str}
            else:
                # Shallow review
                # Change
                dico_change = {}
                # Quality Assurance
                dico_quality = {}
                 # Inputs
                dico_inputs = {}
                # Development
                dico_produced = {}
                # Verification
                dico_verif = {}
                # Conformity check
                dico_conformity = {}
                # Transition
                dico_transition = {}
        elif review_number == 2:  # SRR:
            review_string = ""
            filename_header = "REV_SRR_{:s}_SQA_{:s}".format(self.cr_type,self.reference)
            if not empty:
                # Inputs
                dico_inputs = {"SRTS_DOC":srts_doc,
                               "SYS_DOC":sys_doc_str}
                # Development
                dico_produced = {"SWRD_DOC":swrd_doc,
                               "SHLDR_DOC":shldr_doc}
                # Verification
                dico_verif = {"SWRD_IS":swrd_is_str}
                # Transition
                dico_transition = {"HSID_DOC":hsid_doc,
                                   "DATASHEETS":data_sheets_str}
            else:
                # Shallow review
                # Change
                dico_change = {}
                # Quality Assurance
                dico_quality = {}
                 # Inputs
                dico_inputs = {}
                # Development
                dico_produced = {}
                # Verification
                dico_verif = {}
                # Conformity check
                dico_conformity = {}
                # Transition
                dico_transition = {}
        elif review_number == 3:  # SDR:
            review_string = ""
            filename_header = "REV_SDR_{:s}_SQA_{:s}".format(self.cr_type,self.reference)
            if not empty:
                # Inputs
                dico_inputs = {"SRTS_DOC":srts_doc,
                               "SDTS_DOC":sdts_doc,
                               "HSID_DOC":hsid_doc,
                               "DATASHEETS":data_sheets_str,
                               "SWRD_DOC":swrd_doc}
                # Development
                dico_produced = {"SWDD_DOC":list_design_document_str,
                               "SLLDR_DOC":slldr_doc}
                # Verification
                dico_verif = {"SWDD_IS":swdd_is}
                # Transition
                dico_transition = {}
            else:
                # Shallow review
                # Change
                dico_change = {}
                # Quality Assurance
                dico_quality = {}
                 # Inputs
                dico_inputs = {}
                # Development
                dico_produced = {}
                # Verification
                dico_verif = {}
                # Conformity check
                dico_conformity = {}
                # Transition
                dico_transition = {}
        elif review_number == 20:  # SwRD audit:
            review_string = "AUD_SWRD"
            filename_header = "AUD_SWRD_{:s}_SQA_{:s}".format(self.cr_type,self.reference)
            dico_change = {'CCB_MINUTES':ccb_doc_str}
            dico_inputs = {}
            # Development
            dico_produced = {}
            # Verification
            dico_verif = {}
            # Conformity check
            dico_conformity = {}
            # Transition
            dico_transition = {}
        elif review_number == 31:  # PLD Specification Review:
            review_string = "REV_PLDSR"
            filename_header = "REV_PLDSR_{:s}_HPA_{:s}".format(self.cr_type,self.reference)
            dico_inputs = {"UPPER_DOC":sys_doc_str,
                           "PLANS":plans_str,
                            "STDS":"",
                            "CUS":"",
                            "ERRATA":"",
                            "COMPLEXITY":""}
            # Development
            dico_produced = {"PLDRD_DOC":swrd_doc}
            # Verification
            dico_verif = {"PLDRD_PRR":peer_review_str,
                          "REQVAL":""}
            # Conformity check
            dico_conformity = {}
            # Transition
            dico_transition = {"HPID_DOC":hsid_doc,
                                "COMPLEXITY":""}
        elif review_number == 32:  # PLD Detailled Design Review::
            dico_inputs = {"PLANS":plans_str,
                            "HPID_DOC":hsid_doc,
                            "PLDRD_DOC":swrd_doc,
                           "ICD_DOC":icd_doc,
                           "PRR":peer_review_str,
                           "DATASHEET":data_sheets_str}
            # Development
            dico_produced = {"PLDRD_DOC":swrd_doc,
                             "PLDDD_DOC":swdd_doc}
            # Verification
            dico_verif = {"PRR":peer_review_str,
                          "REQVAL":""}
            # Conformity check
            dico_conformity = {}
            # Transition
            dico_transition = {"HPID_DOC":hsid_doc,
                                "COMPLEXITY":""}
            review_string = "REV_PLDDDR"
            filename_header = "REV_PLDDDR_{:s}_HPA_{:s}".format(self.cr_type,self.reference)
        else:
            if review_number in range(30,39):
                review_string = "REV_PLD"
                filename_header = "REV_PLD_{:s}_HPA_{:s}".format(self.cr_type,self.reference)
            elif review_number in range(40,49):
                review_string = "REV_BOARD"
                filename_header = "REV_BOARD_{:s}_HPA_{:s}".format(self.cr_type,self.reference)
            elif review_number in range(50,59):
                review_string = "REV_EQPT"
                filename_header = "REV_EQPT {:s}_HPA_{:s}".format(self.cr_type,self.reference)
            else:
                review_string = "GENERIC"
                filename_header = "GENERIC_{:s}_QA_{:s}".format(self.cr_type,self.reference)

            dico_inputs = {}
            # Development
            dico_produced = {}
            # Verification
            dico_verif = {}
            # Conformity check
            dico_conformity = {}
            # Transition
            dico_transition = {}
            self.synergy_log("Review report export not implemented yet")
        self.synergy_log("Amount of SCI found: {:d}".format(index_sci), False)
        self.synergy_log("Amount of SAS found: {:d}".format(index_sas), False)
        self.synergy_log("Amount of SECI found: {:d}".format(index_seci), False)
        self.synergy_log("Amount of plans found: {:d}".format(index_plans), False)
        self.synergy_log("Amount of checksum log found: {:d}".format(index_log), False)
        self.synergy_log("Amount of inspection sheets found: {:d}".format(index_is), False)
        self.synergy_log("Amount of documents found: {:d}".format(index_doc), False)
        ##            tkMessageBox.showinfo("Review report export not implemented yet")
        baseline_doc = ", ".join(map(str, baseline_store))
        release_doc = ", ".join(map(str, release_store))
        project_doc = ", ".join(map(str, project_store))
        hdr_scope = ["CSCI identification",
                     "Standard/Synergy Release",
                     "Baseline/Synergy Baseline",
                     "Conformity Level",
                     "Software Level"]
        tbl_scope = [hdr_scope]
        sw_level = "B"
        if not empty:
            tbl_scope.append([ci_identification, release_doc, baseline_doc, conformity_level, self.sw_level])
        else:
            tbl_scope.append(["{{CSCI ID}}","{{RELEASE}}","{{BASELINE}}","{{CONFORMITY LEVEL}}","{{SW LEVEL}}"])
        list_tags_scope = {
            'SCOPE': {'type': 'tab', 'text': tbl_scope, 'fmt': fmt_scope},
            'REL': {'type': 'str', 'text': release_doc, 'fmt': {}},
            'BAS': {'type': 'str', 'text': baseline_doc, 'fmt': {}},
            'PROJ': {'type': 'str', 'text': project_doc, 'fmt': {}}}
        header_input = ["Nb. Item",
                      "Category",
                      "Item",
                      "Compliance status",
                      "Non compliance description / Justification",
                      "Actions (if compliance status is NOK)"]
        header = ["Nb. Item",
                  "Item",
                  "Compliance status",
                  "Non compliance description / Justification",
                  "Actions (if compliance status is NOK)"]
        header_cr = ["Nb. Item",
                  "Change Requests",
                  "Compliance status",
                  "Non compliance description / Justification",
                  "Actions (if compliance status is NOK)"]
        header_sqa = ["Nb. Item",
                  "SQA activity records",
                  "Compliance status",
                  "Non compliance description / Justification",
                  "Actions (if compliance status is NOK)"]
        tbl_cr_check = [header_cr]
        tbl_sqa_check = [header_sqa]
        tbl_inputs_check = [header_input]
        tbl_dev_check = [header]
        tbl_verif_check = [header]
        tbl_conformity_check = [header]
        tbl_transition_check = [header]

        nb_item = 1
        # Change Request
        nb_item= self.createChecksTable(review_number,5,tbl_cr_check,dico_change,nb_item)
        # SQA Activity
        nb_item= self.createChecksTable(review_number,6,tbl_sqa_check,dico_quality,nb_item)
        # Inputs
        nb_item= self.createInputChecksTable(review_number,1,tbl_inputs_check,dico_inputs,nb_item)
        # Development
        nb_item = self.createChecksTable(review_number,2,tbl_dev_check,dico_produced,nb_item,conformity_level)
        # Verification
        nb_item = self.createChecksTable(review_number,3,tbl_verif_check,dico_verif,nb_item,conformity_level)
        # Conformity
        nb_item = self.createChecksTable(review_number,7,tbl_conformity_check,dico_conformity,nb_item,conformity_level)
        # Transition
        nb_item = self.createChecksTable(review_number,4,tbl_transition_check,dico_transition,nb_item,conformity_level)
        # CR checklist creation
        # TODO: redondant avec synergy_thread
        ccb = CCB(self.ihm,
                  system=self.ihm.system,
                  item=self.ihm.item)
        ccb.setDetectRelease(self.detect_release)
        ccb.setImplRelease(self.impl_release)
        list_cr_for_ccb,status_list = self.ihm._getListCRForCCB()
        print "list_cr_for_ccb in review",list_cr_for_ccb
        ccb.setListCR(list_cr_for_ccb,status_list)
        # Set CR domain
        ccb.setDomain(self.ccb_type)
        ccb.tableau_pr,found_cr = ccb.getPR_CCB(for_review=True)
        print "tableau_pr in review",tableau_pr
        if found_cr:
            dico_cr_checklist = ccb.createChecklist(self.ccb_type,
                                                    for_review=True)
        else:
            dico_cr_checklist ={'domain':'SCR'}
            # table_cr_checklist = []
            # table_cr_checklist.append(["Check","Status","Remark"])
            # table_cr_checklist.append(["--","--","--"])
            # dico_cr_checklist['checklist',"1","In_Analysis"] = table_cr_checklist
        print "dico_cr_checklist",dico_cr_checklist
        if not empty:
            list_tags = {
                'MAKE_LOG': {'type': 'str', 'text': make_log, 'fmt': {}},
                'SCI_DOC': {'type': 'str', 'text': sci_doc, 'fmt': {}},
                'SECI_DOC': {'type': 'str', 'text': seci_doc, 'fmt': {}},
                'SAS_DOC': {'type': 'str', 'text': sas_doc, 'fmt': {}},
                'SCI_IS': {'type': 'str', 'text': sci_is, 'fmt': {}},
                'SECI_IS': {'type': 'str', 'text': seci_is, 'fmt': {}},
                'SAS_IS': {'type': 'str', 'text': sas_is, 'fmt': {}},
                'PSAC_DOC': {'type': 'tab', 'text': psac_doc_str, 'fmt': fmt_one},
                'SDP_DOC': {'type': 'str', 'text': sdp_doc, 'fmt': {}},
                'SVP_DOC': {'type': 'str', 'text': svp_doc, 'fmt': {}},
                'SCMP_DOC': {'type': 'str', 'text': scmp_doc, 'fmt': {}},
                'SRTS_DOC': {'type': 'str', 'text': srts_doc, 'fmt': {}},
                'SDTS_DOC': {'type': 'str', 'text': sdts_doc, 'fmt': {}},
                'SCS_DOC': {'type': 'str', 'text': scs_doc, 'fmt': {}},
                'SWRD_DOC': {'type': 'str', 'text': swrd_doc, 'fmt': {}},
                'SWDD_DOC': {'type': 'str', 'text': swdd_doc, 'fmt': {}},
                'SWDD_IS': {'type': 'str', 'text': swdd_is, 'fmt': fmt_one},
                'CR_CHECK': {'type': 'tab', 'text': tbl_cr_check, 'fmt': fmt_checks},
                'TABLECHECKLIST':{'type':'mix','text':dico_cr_checklist,'fmt':ccb.fmt_chk},
                'SQA_CHECK': {'type': 'tab', 'text': tbl_sqa_check, 'fmt': fmt_checks},
                'INPUTS_CHECK': {'type': 'tab', 'text': tbl_inputs_check, 'fmt': fmt_ipnut_checks},
                'DEV_CHECK': {'type': 'tab', 'text': tbl_dev_check, 'fmt': fmt_checks},
                'VERIF_CHECK': {'type': 'tab', 'text': tbl_verif_check, 'fmt': fmt_checks},
                'TRANSITION_CHECK': {'type': 'tab', 'text': tbl_transition_check, 'fmt': fmt_checks},
                'CONFORMITY_CHECK': {'type': 'tab', 'text': tbl_conformity_check, 'fmt': fmt_checks},
                'TBL_IN': {'type': 'tab', 'text': tbl_upper_doc, 'fmt': fmt_baseline},
                'TBL_OUT': {'type': 'tab', 'text': tbl_output_doc, 'fmt': fmt_baseline},
                'TBL_TRANSITION': {'type': 'tab', 'text': tbl_transition_doc, 'fmt': fmt_baseline},
                'TBL_INSPECTION': {'type': 'tab', 'text': tbl_inspection_doc, 'fmt': fmt_baseline},
            }
        else:
             list_tags = {
                'CR_CHECK': {'type': 'tab', 'text': tbl_cr_check, 'fmt': fmt_checks},
                'SQA_CHECK': {'type': 'tab', 'text': tbl_sqa_check, 'fmt': fmt_checks},
                'INPUTS_CHECK': {'type': 'tab', 'text': tbl_inputs_check, 'fmt': fmt_ipnut_checks},
                'DEV_CHECK': {'type': 'tab', 'text': tbl_dev_check, 'fmt': fmt_checks},
                'VERIF_CHECK': {'type': 'tab', 'text': tbl_verif_check, 'fmt': fmt_checks},
                'TRANSITION_CHECK': {'type': 'tab', 'text': tbl_transition_check, 'fmt': fmt_checks},
                'CONFORMITY_CHECK': {'type': 'tab', 'text': tbl_conformity_check, 'fmt': fmt_checks},
                'TBL_IN': {'type': 'tab', 'text': tbl_upper_doc, 'fmt': fmt_baseline},
                'TBL_OUT': {'type': 'tab', 'text': tbl_output_doc, 'fmt': fmt_baseline},
                'TBL_TRANSITION': {'type': 'tab', 'text': tbl_transition_doc, 'fmt': fmt_baseline},
                'TBL_INSPECTION': {'type': 'tab', 'text': tbl_inspection_doc, 'fmt': fmt_baseline},
            }
        list_tags.update(list_tags_basics)
        list_tags.update(list_tags_scope)
        # Remove dash in filename for Synergy
        filename_header = re.sub(r"-",r"",filename_header)
        if review_number in range(1,20):  # Software Reviews
            template_type = review_string
            template_name = self._getTemplate(template_type,"review_template.docx")
            docx_filename = filename_header + "_%f" % time.time() + ".docx"
        elif review_number in range(30,39):  # PLD Reviews
            template_type = review_string
            template_name = self._getTemplate(template_type,"pld_review_template.docx")
            docx_filename = filename_header + "_%f" % time.time() + ".docx"
        elif review_number in range(40,49):  # Board Reviews
            template_type = review_string
            template_name = self._getTemplate(template_type,"board_review_template.docx")
            docx_filename = filename_header + "_%f" % time.time() + ".docx"
        elif review_number in range(50,59):  # Eqpt Reviews
            template_type = review_string
            template_name = self._getTemplate(template_type,"eqpt_review_template.docx")
            docx_filename = filename_header + "_%f" % time.time() + ".docx"
        else:
            template_type = review_string
            template_name = self._getTemplate(template_type,"default_review_template.docx")
            docx_filename = filename_header + "_%f" % time.time() + ".docx"

        self.ihm.docx_filename = docx_filename
        self.docx_filename, exception = self._createDico2Word(list_tags,
                                                              template_name,
                                                              docx_filename)
        exception = "Review report export not implemented yet"
        return self.docx_filename, exception

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

    checksum = "0XCAFE"
    part_number = "ECE24A3310201"
    release = "SW_ENM/01"
    baseline = "SW_ENM_01_01"



    project_list = [[release, baseline, ""]]
    review = Review()
    result = review.getChecks(review_number)
    exit()

    review = Review(review_number,
                detect_release="",
                impl_release="",
                tbl_cr_for_ccb=[["45", "Allo Houston, we have a problem", "Major", "In Review", "No comments."]],
                session_started=False,
                project_list=project_list,
                system="Dassault F5X PDS",
                item="ESSNESS",
                component="ENM",
                part_number="ECE24A3310201", checksum="0xCAFE", subject="TEST",
                reference="ET1234-S",
                issue="1.0",
                review_qams_id="350",
                conformity_level=2,
                cr_type="SW_ENM")
    print "DATABASE",review.database
    result = review.getName(31)
    print "RESULT",result
    exit()
    result = review.getChecks(review_number)
    # Create table
    tbl_inputs_check = []
    header = ["Nb.	Item", "Category", "Item", "Compliance status", "Non compliance description / Justification",
              "Actions"]
    tbl_inputs_check.append(header)
    nb_item = 1
    for rank, description, category,level in result:
        tbl_inputs_check.append([nb_item, category, description, "OK/NOK/NA", "", ""])
        nb_item += 1
    print "INPUT ITEM CHECK", tbl_inputs_check
    subject = review.getReviewList(review_number)
    test = review.getReviewList(review_domain="PLD")
    print "PLD",test
    review.createReviewReport()

if __name__ == '__main__':
    main()
