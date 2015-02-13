#This file was originally generated by PyScripter's unitest wizard

import unittest
import docid
from ConfigParser import ConfigParser
from Tkinter import *
import threading
import time
import pickle
import re
import Queue


class Interface (docid.Interface):
    def __init__(self, queue, window, **kwargs):
        # Create top frame, with scrollbar and listbox
        Frame.__init__(self, window, width=768, height=576,relief =GROOVE,**kwargs)
        self.project_description = Label(self)
        self.project_description_entry_pg2 = Entry(self)
        self.project_description_entry_pg_ccb = Entry(self)
        self.button_select = Button(self, text='Build', state=DISABLED)
        self.button_find_baselines = Button(self, text='Build', state=DISABLED)
        self.button_find_releases = Button(self, text='Build', state=DISABLED)
        self.button_find_projects = Button(self, text='Build', state=DISABLED)
        self.can = Canvas(self, width =240, height =116)
        self.releaselistbox = Listbox(self,height=6,exportselection=0)
        self.crlistbox = Listbox(self,height=5,width=16,exportselection=0,state=DISABLED,bg="gray",selectmode=EXTENDED)
        self.general_output_txt = Text(self,wrap=WORD, width = 10, height = 10)
        self.button_list_items = Button(self, text='List items', state=DISABLED,width=30)
        self.button_list_tasks = Button(self, text='List tasks', state=DISABLED,width=30)
        self.button_list_history = Button(self, text='List items', state=DISABLED,width=30)
        self.button_set_baselines = Button(self, text='List history', state=DISABLED,width=30)
        self.baselinelistbox = Listbox(self,height=6,width=10,exportselection=0)
        self.check_button_status_in_analysis = Checkbutton(self, text="In analysis")
        self.check_button_status_in_review = Checkbutton(self, text="In review")
        self.check_button_status_under_modif = Checkbutton(self, text="Under modification")
        self.check_button_status_under_verif = Checkbutton(self, text="Under verification")
        self.check_button_status_fixed = Checkbutton(self, text="Fixed")
        self.check_button_status_closed = Checkbutton(self, text="Closed")
        self.check_button_status_postponed = Checkbutton(self, text="Postponed")
        self.check_button_status_compl_analysis = Checkbutton(self, text="Complementary analysis")
        self.check_button_status_canceled = Checkbutton(self, text="Canceled")
        self.check_button_status_rejected = Checkbutton(self, text="Rejected")
        self.check_button_status_all = Checkbutton(self, text="All")

        self.ccb_var_type = StringVar()
        self.ccb_var_type.set("SCR")
        self.cr_type = "SW_ENM"
        self.project_list = []
        # For PR
        self.checkbutton_all = True
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
        self.log_on_var = IntVar()
        self.partnumber = ""
        self.standard = ""
        self.active_release_var = IntVar()
        self.queue = queue
        self._readConfig()

    def cr_activate_all_button(self):
        pass

    def log(self,text,gui=False):
        print time.strftime("%H:%M:%S", time.localtime()) + " " + text

    def defill(self):
        pass
    def log(self,text):
        pass
    def getTypeWorkflow(self):
        return(False)

class ThreadQuery(docid.ThreadQuery):
    def __init__(self,name_id="",master="",queue=""):
        docid.session_started = True
        self.verrou = threading.RLock()
        self.queue = queue
        self.master_ihm = master
        # BuildDoc instance
        self.log = BuildDoc_tu(master)

    def ccm_query(self,query,cmd_name):
        stdout = ""
        stderr = ""
        print "TEST"
        if "Get releases" in cmd_name:
            print cmd_name
            stub_ccm_file = open('tu_get_releases.txt','rb')
        elif cmd_name == "Get source files from baseline: SW_ENM_01_06":
            stub_ccm_file = open('tu_list_history.txt','rb')
        else:
            stub_ccm_file = None
        if stub_ccm_file != None:
            stdout = stub_ccm_file.read()
        else:
            print "No stub file for ccm_query"
        return stdout,stderr

class BuildDoc_tu(docid.BuildDoc):
    def __init__(self,ihm):
        docid.BuildDoc.__init__(self,ihm)
        self.ihm=ihm
        self.release = "SW_ENM/01"
        self.baseline = "SW_ENM_01_03"
        self.project = "All"

    def ccm_query(self,query,cmd_name):
        stdout = ""
        stderr = ""
        print "TEST"
        print cmd_name
        if cmd_name == "Get documents from baseline: SW_ENM_01_03":
            stub_ccm_file = open('tu_get_baseline_swrd.txt','rb')
        elif cmd_name == "Get source files from baseline: SW_ENM_01_06":
            stub_ccm_file = open('tu_list_history.txt','rb')
        elif cmd_name == "Get source files from baseline: PLD_TIE_02_06":
            stub_ccm_file = open('tu_list_history_2.txt','rb')
        elif "Finduse query" in cmd_name:
            stub_ccm_file = open('tu_getarticles_swrd.txt','rb')
        else:
            stub_ccm_file = None
        if stub_ccm_file != None:
            stdout = stub_ccm_file.read()
        else:
            print "No stub file for ccm_query"
        return stdout,stderr

class TestBuildDoc(unittest.TestCase):
    def setUp(self):
        global doc
        global interface

        if 0==1:
            docid.interface.general_output_txt = Text(fenetre,wrap=WORD, width = 100, height = 10)
            docid.verrou = threading.Lock()
            docid.startSession("","db_sms_pds","appereo1","jeudi2009","SMS")
            docid.list_projects = []
            docid.getProjectsList("SW_PLAN/01","",False)
        docid.session_started = True
        docid.list_projects = ["CODE_SW_ENM_PROTO-2.10"]

        doc = BuildDoc_tu(docid.interface)

    def tearDown(self):
        pass

    def testcreateItemType(self):
        pass

    def testgetArticles(self):
##        import csv
##        # read config file
##        config_parser = ConfigParser()
##        config_parser.read('docid.ini')
##        type_doc = config_parser.get("Objects","type_doc")
##        for list_type_doc in csv.reader([type_doc]):
##            pass
##        build_doc = docid.BuildDoc()
##        result =build_doc.getArticles(1,1,list_type_doc)
##        print result
        pass

    def testGetDescription(self):
        description = doc._getDescriptionDoc("PRR_PLDRD_TIE_ET2740_S_Issue1D1.xls")
        print description

    def testFilterDoc(self):
        global doc
        print "\n\n\nTEST:getSpecificData\n"
        items_filter = [["Input_Data","INPUT_DATA"],"Test","REVIEW"]
##        items_filter = ['SRC']
        release = "SW_ENM/01"
        baseline = "SW_ENM_01_03"
        project = "SW_ENM-1.3"
        l_table = doc.getSpecificData(release,baseline,project,items_filter)
        print l_table
        for line in l_table:
            if line != []:
##                pass
                print line

    def testLoadConfig(self):
        print "\n\n\nTEST:_loadConfig\n"
        doc = docid.BuildDoc()
        print doc.dico_descr_docs

    def testHistory(self):
        global thread

        docid.interface.click_list_history()
##        cmd = self.thread.queue.get(0)
##        query = self.thread.queue.get(1)
##        regexp = self.thread.queue.get(2)
##        print cmd,query,regexp
        session_started = True
        thread.processIncoming()

##    def testHistory(self):
##        print "\n\n\nTEST:_getAllSourcesHistory\n"
##        filename = "test.csv"
##        release = "SW_ENM/01"
##        baseline = "SW_ENM_01_06"
##        project = ""
##        cid = BuildDoc_tu("","","","","","",release,baseline,project,"SCI","","","","")
##        cid.display_attr = ' -f "%name;%version;%task;%task_synopsis;%change_request;%change_request_synopsis;%type" '
##        header = ["Document","Issue","Tasks","Synopsis","CR","Synopsis"]
##        cid.tableau_items = []
##        cid.tableau_items.append(header)
##        cid.list_type_src = cid.getSrcType()
##        cid.object_released = False
##        cid.object_integrate = False
##        output = cid._getAllSourcesHistory(release,baseline,project)
##        print cid.tableau_items
##        with open(cid.gen_dir + filename, 'w') as of:
####            output = cid.tableau_items
##            header = "File;Version;Task;Synopsis;CR;Synopsis\n"
##            of.write(header)
##            for line in output:
##                line = re.sub(r"<void>",r"",line)
##                print line
##                # Remove Baseline info at the beginning
##                if not re.search("(^Baseline)",line):
##                    of.write(line)
##                    of.write("\n")

    def testGetAllDocuments(self):
        print "\n\n\nTEST:_getAllDocuments\n"
        release = "SW_ENM/01"
        baseline = "SW_ENM_01_03"
        project = ""
        cid = BuildDoc_tu("","","","","","",release,baseline,project,"SCI","","","","")
##        cid.display_attr = ' -f "%name;%version;%task;%task_synopsis;%change_request;%change_request_synopsis;%type" '
        header = ["Title","Reference","Synergy Name","Version","Type","Synopsis","Instance","Release"]
        cid.tableau_items = []
        cid.tableau_items.append(header)
        cid.list_type_src = cid.getSrcType()
        cid.object_released = False
        cid.object_integrate = False
        cid._initTables()
        cid._getAllDocuments(release,baseline,project)
        print cid.tableau_items

    def testCreateCID(self):
        global doc

        doc.createCID()

    def testFindRelease(self):
        global session_started
        global thread

        print "\n\n\nTEST:_getReleasesList\n"
        docid.interface.find_releases()
##        cmd = self.thread.queue.get(0)
##        query = self.thread.queue.get(1)
##        regexp = self.thread.queue.get(2)
##        print cmd,query,regexp
        session_started = True
        thread.processIncoming()
##        self.thread._getReleasesList("ccm release -l",docid.interface.release_regexp)
##        cmd = self.thread.queue.get(0)
##        stdout = self.thread.queue.get(1)
##        print stdout
    def testgetParentCR(self):
        global thread
        thread._getParentCR("419")
    def testInterface(self):
        fenetre = Tk()
        Pmw.initialise(fenetre)
        fenetre.iconbitmap("qams.ico")
        fenetre.title("Create Configuration Index Document")
        # enable height window resize
        fenetre.resizable(False,False)
         # instance threads
        queue = Queue.Queue()
        gui = docid.Gui(fenetre,queue,"UN","DEUX")
        docid.interface.mainloop()

    def testConditionStatus(self):
        global interface

        build_doc = docid.BuildDoc(docid.interface)
        print "TEST 1"
        build_doc.previous_release = "SW_ENM/00,SW_PLAN/01"
        condition,detect_attribut = build_doc._createConditionStatus("SW_ENM/01,SW_PLAN/02")
        print "condition",condition
        print "detect_attribut",detect_attribut
        print "TEST 2"
        build_doc.previous_release = "SW_ENM/00,SW_PLAN/01"
        condition,detect_attribut = build_doc._createConditionStatus("")
        print "condition",condition
        print "detect_attribut",detect_attribut

    def testgetReference(self):
        build_doc = docid.BuildDoc()
        reference = build_doc._getReference("SECI_ENM_ET3123_S")
        print "reference",reference

    def testgetCRStatus(self):
        build_doc = docid.BuildDoc()
        build_doc.tableau_pr = [['Domain', 'CR Type', 'ID', 'Status', 'Synopsis'], ['SCR', 'SW_ENM', '417', 'Closed', 'Update tolerance on PWM reception'], ['SCR', 'SW_PLAN', '365', 'In_Analysis', 'SQA: Dassault SQAP review sheet remarks rework'], ['SCR', 'SW_PLAN', '351', 'In_Review', 'SQA: Adapt SCR review according to software conformity level ']]
        cr_status = build_doc._getCRStatus("365")
        print "STATUS",cr_status

    def get_severity(self,cr):
        scores = {'Showstopper': 1, 'Severe': 2, 'Medium': 3, 'Minor': 4}
        if cr[5] in scores:
            return scores[cr[5]]
        else:
            return 5

    def test_populate_components_listbox(self):
        from tool import Tool
        fenetre = Tk()
        queue = Queue.Queue()
        docid.interface = Interface(queue,fenetre)
        componentslistbox = Listbox(docid.interface)
        tool = Tool()
        result = tool.populate_components_listbox(componentslistbox,1,"ESSNESS","Dassault F5X PDS")
        print "populate_components_listbox",result
        result = tool.populate_components_listbox(componentslistbox,1,"SDSIO","Dassault F5X SDS")
        print "populate_components_listbox",result
        result = tool.populate_components_listbox(componentslistbox,1,"WHCC","Dassault F5X WDS")
        print "populate_components_listbox",result
        result = tool.populate_components_listbox_wo_select(componentslistbox,"ESSNESS","Dassault F5X PDS")
        print "populate_components_listbox_wo_select",result
        result = tool.populate_components_listbox_wo_select(componentslistbox,"","Dassault F5X PDS")
        print "populate_components_listbox_wo_select",result
        result = tool.populate_components_listbox_wo_select(componentslistbox,"","")
        print "populate_components_listbox_wo_select",result
    def testTri(self):
        tableau_pr = [['SCR', 'SW_ENM', '417', 'Closed', 'Update tolerance on PWM reception','Minor'], ['SCR', 'SW_PLAN', '365', 'In_Analysis', 'SQA: Dassault SQAP review sheet remarks rework','Blocking'], ['SCR', 'SW_PLAN', '351', 'In_Review', 'SQA: Adapt SCR review according to software conformity level ','Showstopper']]

        result = sorted(tableau_pr,key=self.get_severity)
        print result

    def testHTML(self):
        from HTMLParser import HTMLParser
        # create a subclass and override the handler methods
        class MyHTMLParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                print "Encountered a start tag:", tag
            def handle_endtag(self, tag):
                print "Encountered an end tag :", tag
            def handle_data(self, data):
                print "Encountered some data  :", data

        # instantiate the parser and fed it some HTML
        parser = MyHTMLParser()
        parser.feed('<html><head><title>Test</title></head>'
                    '<body><h1>Parse me!</h1></body></html>')
    def testCreateReviewReport(self):
        global doc

        doc.createReviewReport()

    def testCreateCCB(self):
        global doc
        doc.tableau_pr = []
        doc.tableau_pr.append(["","","375","In_Review"])
##        print "tableau_pr",doc.tableau_pr[0][2]
##        result = doc._getCRStatus("375")
##        print "STATUS",result
        doc.list_cr_for_ccb =('375',)
        dico_cr_checklist = doc.createChecklist("PLDCR")
##        print "DICO_TEST_CR",dico_cr_checklist
##        for check in dico_cr_checklist['checklist','375']:
##            print "DICO_TEST_CR",check
##        list_tags_corrompu = {
##            'TABLEPRS': {'text': [['Domain', 'CR Type', 'ID', 'Status', 'Synopsis', 'Severity', 'Dectected on', 'Implemented for'], ['PLDCR', 'PLD_SDSIO', '375', 'Fixed', 'SEU/MEU protection mechanisms for a neutrons flow of 4230 n/cm.h', 'N/A', 'PLD_SDSIO/03', 'PLD_SDSIO/04']], 'fmt': {'colw': [500, 500, 500, 500, 1500, 500, 500, 500], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'tab'},
##            'TABLECHECKLIST': {'text': {'domain': 'PLDCR', ('checklist', u'375'): [['Check', 'Status', 'Remark'], [u'check CR field coherency with configuration management process, -"Under_modification" reviewed and approved, -"Under_verification" reviewed and approved', '', ''], [u'confirm that performed activities (development and verification) are complete and consistent', '', '']]}, 'fmt': {'colw': [3000, 500, 1000], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'mix'},
##            'TABLEANNEX': {'text': [(u'a) Extract PLDCR-375', 'rb'), ('', 'r')], 'fmt': {}, 'type': 'par'},
##            'TABLELOGS': {'text': [['id', 'Log'], ['--', '--']], 'fmt': {'colw': [500, 4500], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'tab'}
##        }
##        list_tags_new = {
##            'TABLEPRS': {'text': [['Domain', 'CR Type', 'ID', 'Status', 'Synopsis', 'Severity', 'Dectected on', 'Implemented for'], ['PLDCR', 'PLD_SDSIO', '375', 'Fixed', 'SEU/MEU protection mechanisms for a neutrons flow of 4230 n/cm.h', 'N/A', 'PLD_SDSIO/03', 'PLD_SDSIO/04']], 'fmt': {'colw': [500, 500, 500, 500, 1500, 500, 500, 500], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'tab'},
##            'TABLECHECKLIST': {'text': {'domain': 'PLDCR', ('checklist', u'375'): [['Check', 'Status', 'Remark'], ['check CR field coherency with configuration management process, -"Under_modification" reviewed and approved, -"Under_verification" reviewed and approved', '', ''], ['confirm that performed activities (development and verification) are complete and consistent', '', '']]}, 'fmt': {'colw': [3000, 500, 1000], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'mix'},
##            'TABLEANNEX': {'text': [(u'a) Extract PLDCR-375', 'rb'), ('', 'r')], 'fmt': {}, 'type': 'par'},
##            'TABLELOGS': {'text': [['id', 'Log'], ['--', '--']], 'fmt': {'colw': [500, 4500], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'tab'}
##        }

        list_tags = {
            'TABLEPRS': {'text': [['Domain', 'CR Type', 'ID', 'Status', 'Synopsis', 'Severity', 'Dectected on', 'Implemented for'], ['PLDCR', 'PLD_SDSIO', '375', 'Fixed', 'SEU/MEU protection mechanisms for a neutrons flow of 4230 n/cm.h', 'N/A', 'PLD_SDSIO/03', 'PLD_SDSIO/04']], 'fmt': {'colw': [500, 500, 500, 500, 1500, 500, 500, 500], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'tab'},
            'TABLECHECKLIST': {'text': dico_cr_checklist, 'fmt': {'colw': [3000, 500, 1000], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'mix'},
            'TABLEANNEX': {'text': [(u'a) Extract PLDCR-375', 'rb'), ('', 'r')], 'fmt': {}, 'type': 'par'},
            'TABLELOGS': {'text': [['id', 'Log'], ['--', '--']], 'fmt': {'colw': [500, 4500], 'twunit': 'pct', 'tblw': 5000, 'cwunit': 'pct', 'borders': {'all': {'color': 'auto', 'sz': 6, 'val': 'single', 'space': 0}}, 'heading': True}, 'type': 'tab'}
        }
##        list_tags = {
##            'TABLECHECKLIST':{'type':'mix','text':dico_cr_checklist,'fmt':fmt_chk},
##            'TABLEPRS':{'type':'tab','text':self.tableau_pr,'fmt':fmt_pr},
##            'TABLELOGS':{'type':'tab','text':tableau_log,'fmt':fmt_log},
##            'TABLEANNEX':{'type':'par','text':list_cr_annex,'fmt':{}}
##                }
        template_name = doc._getTemplate("CCB")
##        docx_filename = "test_ccb_corrrompu.docx"
##        docx_filename,exception = doc._createDico2Word(list_tags_corrompu,template_name,docx_filename)
        docx_filename = "test_ccb.docx"
        docx_filename,exception = doc._createDico2Word(list_tags,template_name,docx_filename)

    def testclick_add_action_item(self):
        global docid
##        fenetre = Tk()
##        queue = Queue.Queue()
##        docid.interface = Interface(queue,fenetre)
        docid.click_add_action_item()
    def testReplaceTag(self):
        import zipfile
        from lxml import etree
        global doc

        login_window = Tk()
        interface_login = docid.Login(login_window)
        if interface_login.auto_start:
            interface_login.click_bypass()
            login_window.destroy()
        print "TEST",docid.item
        author,item,database,aircraft,item_description,ci_identification,program = doc._getInfo()

        try:
            import docx
        except ImportError:
            print "DoCID requires the python-docx library for Python. " \
                    "See https://github.com/mikemaccana/python-docx/"
                        #    raise ImportError, "DoCID requires the python-docx library for Python. " \
                        #         "See https://github.com/mikemaccana/python-docx/"

        outdoc = {}
        # Load the original template
        try:
            template = zipfile.ZipFile(doc.template_name,mode='r')
        except IOError as exception:
            print "Execution failed:", exception
            interface.log("Something is wrong with template file. Check .ini file Default template is used.")
            try:
                template = zipfile.ZipFile(doc.template_default_name,mode='r')
            except IOError as exception:
                pass
        if 'template' in locals():
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
            print doc.func_chg
            doc.func_chg =\
        [ ('some bold text', 'b')
        , ('some normal text', '')
        , ('some italic underlined text', 'iu')
        ]
            print doc.oper_chg
            colw = [1000,2300,200,500,500,500,500,500] # 5000 = 100%
            fmt =  {
                    'heading': True,
                    'colw': colw, # 5000 = 100%
                    'cwunit': 'pct',
                    'tblw': 5000,
                    'twunit': 'pct',
                    'borders': {'all': {'color': 'auto','space': 0,'sz': 6,'val': 'single',}}
                    }
            tbl_items_filtered = []
            tbl_items_filtered.append(["Title","Reference","Synergy Name","Version","Type","Instance","Release","CR"])
            tbl_items_filtered.append(["--","--","--","--","--","--","--","--"])
            list_tags = {
                'ITEM':{'type':'str','text':item,'fmt':{}},
                'ITEM_DESCRIPTION':{'type':'str','text':item_description,'fmt':{}},
                'TABLEITEMS':{'type':'tab','text':tbl_items_filtered,'fmt':fmt},
                'PROGRAM':{'type':'str','text':program,'fmt':{}},
                'FUNCCHG':{'type':'par','text':doc.func_chg,'fmt':{}},
                'OPCHG':{'type':'par','text':doc.oper_chg,'fmt':{}}}
            for curact in actlist:
                xmlcontent = template.read(curact[0])
                outdoc[curact[0]] = etree.fromstring(xmlcontent)
                # Will work on body
                docbody = outdoc[curact[0]].xpath(curact[1], namespaces=docx.nsprefixes)[0]


                for key, value in list_tags.items():
                    print "TEST:" + key,value
                    if value['text'] != None:
                        text = value['text']
                    else:
                        text = "None"
                    docbody = doc.replaceTag(docbody, key, (value['type'], value['text']),value['fmt'] )
        # ------------------------------
        # Save output
        # ------------------------------
        try:
            outfile = zipfile.ZipFile(doc.gen_dir + "test.docx",mode='w',compression=zipfile.ZIP_DEFLATED)
##            # Copy relationships
##            actlist.append(('word/_rels/document.xml.rels', '/w:document/w:wordrelationships'))
##            # Serialize our trees into out zip file
##            treesandfiles = {wordrelationships: 'word/_rels/document.xml.rels'}
##            for tree in treesandfiles:
##                treestring = etree.tostring(tree, pretty_print=True)
##                outfile.writestr(treesandfiles[tree], treestring)

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

if __name__ == '__main__':
##    docid.session_started = True
    docid.item_id= 1
    docid.project_item= 1
    try:
        import Pmw
    except ImportError:
        print "DoCID requires the Python MegaWidgets for Python. " \
            "See http://sourceforge.net/projects/pmw/"
    score = {
        "joueur 1":    5,
        "joueur 2":   35,
        "joueur 3":   20,
        "joueur 4":    2,
    }
    with open('donnees', 'wb') as fichier:
        mon_pickler = pickle.Pickler(fichier)
        mon_pickler.dump(score)
    print "TEST DICO"
    print fichier
    fenetre = Tk()
    queue = Queue.Queue()
    docid.interface = Interface(queue,fenetre)
    thread = ThreadQuery("",docid.interface,queue)


    suite = unittest.TestSuite()
##    suite.addTest(TestBuildDoc('testReplaceTag'))
    suite.addTest(TestBuildDoc('testConditionStatus'))
##    suite.addTest(TestBuildDoc('testInterface'))
##    suite.addTest(TestBuildDoc('testCreateCID'))
    unittest.TextTestRunner(verbosity=2).run(suite)


##    suite = unittest.TestLoader().loadTestsFromTestCase(TestBuildDoc)
##    suite = unittest.TestLoader().loadTestsFromModule(testInterface)
##    unittest.TextTestRunner(verbosity=2).run(suite)
##    unittest.main(defaultTest ='testInterface')
##    if "PLDRRT" in "PRR_PLDRD_TIE_ET2740_S_Issue1D1.xls":
##            print "OK"
##    print "PRR_PLDRD_TIE_ET2740_S_Issue1D1.xls".lstrip('PR_')
