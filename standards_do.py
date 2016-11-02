__author__ = 'Olivier.Appere'
#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
import platform
import re
import getpass
from os.path import join
from tool import Tool
import threading
from synergy_thread import ThreadQuery
try:
    from Tkinter import *
    ##    import Tkinter              # Python 2
    import ttk
except ImportError:
    from tkinter import *
    ##    import tkinter as Tkinter   # Python 3
    import tkinter.ttk as ttk
try:
    import Pmw
except ImportError:
    print ("DoCID requires the Python MegaWidgets for Python. "
           "See http://sourceforge.net/projects/pmw/")
import tkMessageBox
import tkSimpleDialog
import Queue
import webbrowser
from datetime import datetime
from markdown2 import Markdown
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel
from tkintertable.TableFormula import Formula
from check_llr import CheckLLR
from check_is import CheckIS
from tool import SQLite

class scrollTxtArea:
    def __init__(self,
                 root,
                 wrap=WORD,
                 width=60,
                 height=16):
        frame = Frame(root)
        frame.pack()
        self.textPad(frame,
                     height=height,
                     width=width,
                     wrap=wrap)
        return

    def textPad(self,
                frame,
                wrap=WORD,
                width=60,
                height=16):
        #add a frame and put a text area into it
        textPad = Frame(frame)
        self.text = Text(textPad,
                         height=height,
                         width=width,
                         wrap=wrap)

        # add a vertical scroll bar to the text area
        scroll = Scrollbar(textPad)
        self.text.configure(yscrollcommand=scroll.set)
        scroll.config(command=self.text.yview)
        #pack everything
        self.text.pack(side=LEFT)
        scroll.pack(side=RIGHT, fill=Y)
        textPad.pack(side=TOP)

class ExportIS(CheckIS):
    dico_sheets = {"is":("CONTEXT","REVIEW","DOC REVIEW","REQ REVIEW","REQ ANALYSIS","UPPER REQ ANALYSIS","REMARKS")}

    def __init__(self, hlr_selected=False, **kwargs):
        CheckIS.__init__(self, **kwargs)
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
        self.index_row = 0
        self.index_column = 0
        self.nb_cell_read = 0
        self.context_issue = ""
        self.log_filename = None
        self.log_handler = None
        self.tbl_cr = []
        self.tbl_is_cr_id = []
        self.applicable_docs = {}
        self.is_release = ""
        self.is_baseline = ""
        self.resetKeywords()
        self.dico_remarks = {}
        self.resetSheetsList()
        self.component = ""
        self.list_cr = []
        self.list_cr_not_found = []
        self.list_rules_unknown = []
        self.tbl_list_llr = {}
        self.tbl_file_llr_wo_del = {}
        swrd = ExtractReq()
        result = swrd.restoreFromSQLite()
        for id, tag, body, issue, refer, status, derived, terminal, rationale, safety, additional in project_list:
            self.tbl_list_llr[tag] = {"issue": issue,
                                      "status": status,
                                      "refer": refer,
                                      "derived": derived,
                                      "body": body
            }
            if status is not "DELETED":
                self.tbl_file_llr_wo_del[tag] = {"issue": issue,
                                                 "status": status,
                                                 "refer": refer,
                                                 "derived": derived,
                                                 "body": body
                }

class ThreadReq(ThreadQuery):
    def __init__(self,
                 name_id="",
                 master=None,
                 queue=None,
                 login="",
                 password="",
                 **kwargs):
        """
        :param name_id:
        :param master:
        :param queue:
        :param kwargs:
        :return:
        """

        for key in kwargs:
            self.__dict__[key] = kwargs[key]
        if "no_start_session" not in self.__dict__:
            self.no_start_session = False

        threading.Thread.__init__(self)
        # Create the queue
        self.queue = queue
        self.master_ihm = master
        self.running = True
        self.verrou = threading.RLock()

    @staticmethod
    def _importSWRD():
        print "ImportSWRD"
        swrd = ExtractReq()
        swrd.extract()

    def _exportIS(self):

        export_is = ExportIS(hlr_selected = True)

        print "tbl_file_llr_wo_del",export_is.tbl_file_llr_wo_del
        print "tbl_list_llr",export_is.tbl_list_llr

        filename_is = export_is.exportIS()
        print "filename_is",filename_is

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
        while self.queue.qsize():
            try:
                self.lock()
                print threading.enumerate()
                # Check contents of message
                action = self.queue.get(0)
                print "ACTION:",action
                #print time.strftime("%H:%M:%S", time.localtime()) + " Commmand: " + action
                if action == "IMPORT_SWRD":
                    self.import_req_thread = threading.Thread(None,self._importSWRD,None)
                    self.import_req_thread.start()
                elif action == "EXPORT_IS_HLR":
                    self.send_cmd_thread = threading.Thread(None,self._exportIS,None)
                    self.send_cmd_thread.start()
                self.unlock()
            except Queue.Empty:
                pass

class ExtractReq():

    def __init__(self):

        filename = self.setUp(case=11)
        self.spec = CheckLLR(filename,
                            hlr_selected=True)
        # print spec.dico_types
        # exit()
        self.spec.openLog("SWRD")
        self.spec.use_full_win32com = True

    @staticmethod
    def getSplitRefer(str_refer,type_doc="SWRD_[\w-]*"):
        list_hlr = re.findall(r'\[({:s})\]'.format(type_doc), str_refer)
        return list_hlr

    def extract(self):
        self.spec.listDir(tbl_type=("SWRD",),
                    table_enabled=False) # True
        print "Extraction fini"
        self.saveInSQLite()
        self.spec.closeLog()

    @staticmethod
    def restoreFromSQLite(database="db/swrd.db3"):
        sql_req = SQLite(database)
        sql_req.connect()
        reqs = sql_req.get_all()
        #for req in reqs:
        #    print "REQS",req
        sql_req.close()
        return reqs

    def saveInSQLite(self,database="db/swrd.db3"):
        sql_req = SQLite(database)
        sql_req.connect()
        sql_req.create()
        nb = sql_req.insert_many(self.spec.tbl_list_llr)
        print "nb entries:",nb
        sql_req.close()
        for req,value in self.spec.tbl_list_llr.iteritems():
            dico_attrib = {"id": req, "body": self.spec.getAtribute(value, "body"),
                           "derived": self.spec.getAtribute(value, "derived"),
                           "issue": self.spec.getAtribute(value, "issue"),
                           "status": self.spec.getAtribute(value, "status"),
                           "safety": self.spec.getAtribute(value, "safety"),
                           "terminal": self.spec.getAtribute(value, "terminal")}
            #print "REQ:",req
            #print "BODY:",dico_attrib["body"]

    @staticmethod
    def setUp(case=0):
        import os
        #print("Setting up Test cases")
        dirname = ""
        current_dir = os.getcwd()
        if case == 11:
            #dirs = ("SET_G7000_ACENM","SWDD","LLR","Application Layer","Application Actuation")
            dirs = ("SWRD","TEST")
            dirname = join(current_dir,"qualification")
            for directory in dirs:
                dirname = join(dirname,directory)
        return dirname

    def test_extract_tables_in_swrd(self):
        from check_llr import CheckLLR
        from swrd import Swrd

        filename = self.setUp(case=11)
        spec = CheckLLR(filename,
                        hlr_selected=True)
        # print spec.dico_types
        # exit()
        spec.openLog("SWRD")
        spec.use_full_win32com = True
        spec.listDir(tbl_type=("SWRD",),
                    table_enabled=True) # True
        print "Extract result"
        print "Found {:d} tables at the beginning".format(spec.nb_tables)
        swrd = Swrd(spec.list_tbl_tables_begin)
        nb_ext_signals = swrd.populateDicoExtSignal()
        print("{:d} external signals found.".format(nb_ext_signals))
        nb_int_signals = swrd.populateDicoIntSignal()
        print("{:d} internal signals found.".format(nb_int_signals))
        nb_alias = swrd.populateDicoAlias()
        print("{:d} alias found.".format(nb_alias))

        for table_id,table in spec.list_tbl_tables_begin.iteritems():
            if table_id == 4: # External interface dataflow
                for index,row in enumerate(table):
                    if index == 0: # header
                        print "HEADER"
                        for col in row:
                            print col
                        print "----------"
                    else:
                        print row
            elif table_id == 5: # Internal interface dataflow
                for row in table:
                    print row
            elif table_id == 6: # Alias
                for row in table:
                    print row
        #req.extract(filename,type=["SWRD"])
        spec.closeLog()
        # Output requirements tags in xml format
        root = ET.Element("SWRD")
        signals = ET.SubElement(root, "SIGNALS")
        for req,value in spec.tbl_list_llr.iteritems():
            dico_attrib = {"id": req, "derived": spec.getAtribute(value, "derived"),
                           "issue": spec.getAtribute(value, "issue"), "status": spec.getAtribute(value, "status"),
                           "safety": spec.getAtribute(value, "safety"), "terminal": spec.getAtribute(value, "terminal")}
            requirements = ET.SubElement(root, "REQ",attrib=dico_attrib)
            # Refer
            str_refer = spec.getAtribute(value,"refer")
            list_refer = spec.getSplitRefer(str_refer,type="[A-Z]*[_-][\w-]*")
            #if req == "SWRD_GLOBAL-ACENM_0006":
            #    print "str_refer",str_refer
            #    print "list_refer",list_refer
            # Constraints
            if "constraint" in value:
                str_constraints = self.getAtribute(value,"constraint")
                str_constraints_cleaned = Tool.removeNonAscii(str_constraints)
                str_constraints_cleaned_wo_dot = re.sub(r"\.", r"_",str_constraints_cleaned)
                list_constraints = self.getSplitRefer(str_constraints_cleaned_wo_dot,type="[^\[^\].]*")
            rationale_tag = ET.SubElement(requirements, "RATIONALE")
            rationale_tag.text = spec.getAtribute(value,"rationale")
            additional_tag = ET.SubElement(requirements, "ADDITIONAL")
            additional_tag.text = spec.getAtribute(value,"additional")
            for refer in list_refer:
                refer_tag = ET.SubElement(requirements, "REFER")
                refer_tag.text = refer
        tree = ET.ElementTree(root)
        xml_filename = "result\\spec_tags.xml"
        html_filename = "result\\spec_tags.html"
        #treestring = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "\n"
        #treestring += ET.tostring(tree)
        #print treestring
        tree.write(xml_filename)
        if 0==1:
            current_dir = os.getcwd()
            xsl = join(current_dir,"template\\spec_tags.xsl")
            htmlC = HtmlConverter(xml_filename,xsl)
            html_final = htmlC.toHtml(html_filename)
            os.startfile(html_filename)

class GuiTool():
    def __init__(self):
        pass

    @staticmethod
    def createEntry(frame,
                    tag,
                    content,
                    bg="white",
                    entry_size=30,
                    width=20,
                    side=""):
        """

            :param frame:
            :param tag:
            :param content:
            :param bg:
            :param entry_size:
            :param width:
            :param side:
            :return: Entry object
            """
        box = Frame(frame)
        label_txt = Label(box, text=tag,width=width, anchor=W, padx=2)
        label_txt.pack(side=LEFT)
        entry = Entry(box,
                    state=NORMAL,
                    width=entry_size,
                    bg=bg)
        entry.insert(END, content)
        entry.pack()
        if side != "":
            box.pack(side=side)
        else:
            box.pack()
        return entry

class smallWindows(Frame,
                   Toplevel,
                   Text,
                   GuiTool):
    def __init__(self,
                 master=None,
                 database=None,
                 review_type=None):
        self.database=database
        self.review_type = review_type
        print "master parameter not implemented"
    #             fenetre=None,
    #             rule_id=None):
        Frame.__init__(self,master)
    #    self.rule_id=rule_id
    def crlistbox_scrollEvent(self, event):
        if event.delta > 0:
            self.status_listbox.yview_scroll(-2, 'units')
        else:
            self.status_listbox.yview_scroll(2, 'units')

    def up_event(self, event,listbox):
        index = listbox.index("active")
        if listbox.selection_includes(index):
            index -= 1
        else:
            index = listbox.size() - 1
        if index < 0:
            listbox.bell()
        else:
            self.select(index,listbox)
            self.on_select(index)
        return "break"

    def down_event(self, event,listbox):
        index = listbox.index("active")
        if listbox.selection_includes(index):
            index = index + 1
        else:
            index = 0
        if index >= listbox.size():
            listbox.bell()
        else:
            self.select(index,listbox)
            self.on_select(index)
        return "break"

    @staticmethod
    def setWindowPos(window):
        global fenetre
        x = fenetre.winfo_rootx()
        y = fenetre.winfo_rooty()
        geom = "+%d+%d" % (x + 20, y + 20)
        print
        geom
        window.geometry(geom)

    def scrollEvent(self, event):
        if event.delta > 0:
            # scroll up
            self.help_text.yview_scroll(-2, 'units')
        else:
            # scroll down
            self.help_text.yview_scroll(2, 'units')

    def read(self):
        update_text=self.help_text.get(1.0, END)
        return update_text

    def get_version(self):
        version=self.entry_version.get()
        return version

    def get_status(self):
        status=self.status_listbox.get(FIRST)
        return status

    def remove_comment(self,event,comment_id,rule_id,rule_tag,user_login):
        # TODO: Add a menu
        user_logged = getpass.getuser()
        role = Tool.getUserRole(user_login)
        print "Login of the user logged:",user_logged
        print "Login of the user who write the comment:",user_login
        print "Role of the user logged:",role
        if tkMessageBox.askyesno("Remove comment {:d} from rule {:s}".format(comment_id,rule_tag), "Are you sure?"):
            print "To be implemented"
            self.refreshComments(rule_id,rule_tag)
            self.exit()

    def add_comment(self,rule_id,rule_tag,callback_refresh):
        txt=self.read()
        now = datetime.now()
        date = now.strftime("%A, %d. %B %Y %I:%M%p")
        user_login = getpass.getuser()
        if tkMessageBox.askyesno("Add Comment to rule {:s}".format(rule_tag), "Are you sure?"):
            Tool.addCommentRule(rule_id,
                                user_login=user_login,
                                date=date,
                                txt=txt)
            callback_refresh(rule_id,rule_tag)
            self.exit()

    def add_link_rule_to_objective(self,rule_id,callback):
        m = re.match(r'([0-9]{1,3})\).*',self.selection)
        if m:
            objective_id = m.group(1)
            Tool.addLinkRule2Objective(rule_id,objective_id,database=self.database)
            # Refresh parent objectives list
            callback(rule_id)

    def onLink(self, event):
        event.widget.configure(cursor="arrow")

    def outsideLink(self, event):
        event.widget.configure(cursor="xterm")

    def write(self,
              txt,
              frame=None,
              color=None,
              handle=None,
              hlink=None,
              callback=None,
              callback_delete=None,
              run=False):
        if frame is None:
            frame = self.help_text
        if not run:
            frame.delete(0.0, END)
        if color is not None:
            frame.tag_configure(handle, background=color)
        if hlink is not None:
            frame.tag_bind(handle,
                            "<Double-Button-1>",
                            callback)
            if callback_delete is not None:
                frame.tag_bind(handle,
                                "<Button-3>",
                                callback_delete)
            frame.tag_bind(handle, "<Enter>", self.onLink)
            frame.tag_bind(handle, "<Leave>", self.outsideLink)
        frame.insert(END, txt,handle)

    def edit_comment(self,comment_id):
        txt=self.read()
        now = datetime.now()
        date = now.strftime("%A, %d. %B %Y %I:%M%p")
        print "NOW:",date
        user_login = getpass.getuser()
        status = self.get_status()
        if tkMessageBox.askyesno("Update Comment", "Are you sure?"):
            Tool.UpdateComment(comment_id,
                                user_login=user_login,
                                date=date,
                                txt=txt,
                                status=status)
        self.exit()

    def edit_response(self,response_id):
        txt=self.read()
        now = datetime.now()
        date = now.strftime("%A, %d. %B %Y %I:%M%p")
        print "NOW:",date
        user_login = getpass.getuser()
        if tkMessageBox.askyesno("Update Response", "Are you sure?"):
            Tool.UpdateResponse(response_id,
                                user_login=user_login,
                                date=date,
                                txt=txt)
        self.exit()

    def add_response(self,comment_id):
        txt=self.read()
        now = datetime.now()
        date = now.strftime("%A, %d. %B %Y %I:%M%p")
        user_login = getpass.getuser()
        if tkMessageBox.askyesno("Add a response", "Are you sure?"):
            Tool.ResponseToComment(comment_id,
                                user_login=user_login,
                                date=date,
                                txt=txt)
            self.exit()

    def editResponseWindow(self, event, response_id):
        # Edit comment
        InspectionWorkflow = ("TO BE DISCUSSED","ACCEPTED","CORRECTED","REJECTED")
        sql_response_id,user_login,date,response,status = Tool.readResponse(response_id)
        comment_windows = smallWindows(master=self.display_rule)
        comment_windows.create(title="Response")
        left_frame = Frame(comment_windows.display_rule)
        comment_windows.create_text(title="Response {:d} written by {:s} on {:s}".format(sql_response_id,user_login,date),
                                    frame=left_frame,
                                    height=8,
                                    side=TOP)
        comment_windows.write(txt='{:s}'.format(response))
        left_frame.pack(side=LEFT)
        comment_windows.add_button(text="Update",
                                   help="Update response",
                                   side=TOP,
                                   callback=lambda arg1=response_id: comment_windows.edit_response(response_id))
        comment_windows.add_button(text="Quit",help="Back to the rule",side=TOP,callback=comment_windows.exit)

    def editCommentWindow(self, event, comment_id,rule_tag):
        # Edit comment
        InspectionWorkflow = ("TO BE DISCUSSED","ACCEPTED","CORRECTED","REJECTED")
        sql_comment_id,user_login,date,comment,status = Tool.readCommentByID(comment_id)
        comment_windows = smallWindows(master=self.display_rule)
        comment_windows.create(title="Comment")
        left_frame = Frame(comment_windows.display_rule)
        comment_windows.create_text(title="Update comment {:d} written by {:s} on {:s} for rule {:s}".format(sql_comment_id,user_login,date,rule_tag),
                                    frame=left_frame,
                                    height=8,
                                    side=TOP)
        formatted_comment = Tool.replaceNonASCII(comment)
        comment_windows.write(txt='{:s}'.format(formatted_comment))
        # Display comments
        responses_frame = comment_windows.create_text(title="Responses for comments {:d}".format(sql_comment_id),
                                                      frame=left_frame,
                                                      height=8)
        responses = Tool.readResponses(comment_id)
        if responses:
            print "COMMENTS",responses
            inter = 0
            for response_id,user_login,date,response in responses:
                if inter % 2 == 0:
                    color = 'gray88'
                else:
                    color = 'lightgrey'
                handle = "handle_{:d}".format(inter)
                #self.comment_windows.write(txt='{:d}) {:s} {:s}: {:s}\n'.format(id,user_login,date,comment),
                comment_windows.write(txt='{:d}) {:s} [{:s} - {:s}]\n'.format(response_id,response,user_login,date),
                                      frame=responses_frame.text,
                                       color=color,
                                       handle=handle,
                                       hlink = response_id,
                                       callback=lambda event, arg1=response_id: self.editResponseWindow(event,response_id),
                                       run=True)
                inter += 1
        left_frame.pack(side=LEFT)
        # Rule status
        comment_windows.create_combobox(comment_windows.display_rule,
                                        width=40,
                                        text="Status",
                                        list=InspectionWorkflow,
                                        callback=self.status_listbox_onselect)
        comment_windows.status_focus(status,
                                     list_items=InspectionWorkflow)
        comment_windows.add_button(text="Update",
                                   help="Update comment",
                                   side=TOP,
                                   callback=lambda arg1=comment_id: comment_windows.edit_comment(comment_id))
        comment_windows.add_button(text="Respond",
                                   help="Add a response",
                                   side=TOP,
                                   callback=lambda arg1=comment_id: comment_windows.display_input_new_response_windows(comment_id))
        comment_windows.add_button(text="Quit",help="Back to the rule",side=TOP,callback=comment_windows.exit)

    def write_version(self,version):
        self.entry_version.delete(0, END)
        print "VERSION",version
        self.entry_version.insert(END, version)

    def status_focus(self,status,list_items=("APPROVED","MODIFIED","TO BE MODIFIED","DELETED")):
        if status in list_items:
            num = list_items.index(status)
            print "Status Num:",num
            self.status_listbox.selectitem(num,setentry=1)

    def add_button(self,text,func_help,side=LEFT,callback=None,rule_id=None):
        if rule_id is None:
            self.button_add_comment = Button(self.display_rule,
                                               text=text,
                                               command=callback)
        else:
            self.button_add_comment = Button(self.display_rule,
                                               text=text,
                                               command=lambda arg=rule_id: callback(arg))
        balloon_help = Pmw.Balloon(self.display_rule)
        balloon_help.bind(self.button_add_comment, func_help)

        self.button_add_comment.pack(padx=5,anchor=E,fill=X,side=side)

    def exit(self):
        print "Close Rule Window"
        self.destroy()
        self.display_rule.destroy()

    @staticmethod
    def start(window):
        window.mainloop()

    def display_input_new_comment_windows(self,rule_id,rule_tag,callback_refresh=None):
        comment_windows = smallWindows(master=self.display_rule)
        #comment_windows.set_id(self.rule_id)
        comment_windows.create(title="Add a new comment")
        comment_windows.create_text(title="Comment for rule {:s}".format(rule_tag))
        comment_windows.add_button(text="Add",
                                   help="Add a comment",
                                   side=TOP,
                                   callback=lambda arg1=rule_id,arg2=rule_tag,arg3=callback_refresh: comment_windows.add_comment(arg1,arg2,arg3))
        comment_windows.add_button(text="Quit",help="Back to the rule",side=TOP,callback=comment_windows.exit)

    def display_input_new_response_windows(self,comment_id):
        comment_windows = smallWindows(master=self.display_rule)
        comment_windows.create(title="Response")
        comment_windows.create_text(title="Response to comment {:d}".format(comment_id))
        comment_windows.add_button(text="OK",
                                   help="Add a response",
                                   side=TOP,
                                   callback=lambda arg=comment_id:comment_windows.add_response(arg))
        comment_windows.add_button(text="Quit",
                                   help="Back",
                                   side=TOP,
                                   callback=comment_windows.exit)
    def refreshComments(self,rule_id,rule_tag):
        # Enable writing
        self.comment_windows.help_text.config(state=NORMAL)
        comments = Tool.readComments(rule_id)
        if comments:
            print "COMMENTS",comments
            inter = 0
            for comment_id,user_login,date,comment in comments:
                if inter % 2 == 0:
                    color = 'gray88'
                else:
                    color = 'lightgrey'
                handle = "handle_{:d}".format(inter)
                #self.comment_windows.write(txt='{:d}) {:s} {:s}: {:s}\n'.format(id,user_login,date,comment),
                formatted_comment = Tool.replaceNonASCII(comment)
                self.comment_windows.write(txt='{:d}) {:s}\n'.format(comment_id,formatted_comment),
                                           color=color,
                                           handle=handle,
                                           hlink = comment_id,
                                           callback=lambda event, arg1=comment_id,arg2=rule_tag: self.editCommentWindow(event,arg1,arg2),
                                           callback_delete=lambda event, arg1=comment_id,arg2=rule_id,arg3=rule_tag,arg4=user_login: self.remove_comment(event,arg1,arg2,arg3,arg4),
                                           run=True)
                inter += 1
        # Disable writing
        self.comment_windows.help_text.config(state=DISABLED)

    def display_comment_windows(self,rule_tag=""):
        self.comment_windows = smallWindows(master=self.display_rule)
        # TODO: Replace self.rule_id by rule_id
        self.comment_windows.set_id(self.rule_id)
        self.comment_windows.create(title="List of comments for rule {:s}".format(rule_tag))
        self.comment_windows.create_text(title="Comments")
        self.comment_windows.add_button(text="Add",
                                        help="Add a comment",
                                        side=TOP,
                                        callback=lambda arg1=self.rule_id,arg2=rule_tag,arg3=self.refreshComments: self.comment_windows.display_input_new_comment_windows(arg1,arg2,arg3))
        self.refreshComments(self.rule_id,rule_tag)
        self.comment_windows.add_button(text="Quit",
                                        help="Back to the rule",
                                        side=TOP,
                                        callback=self.comment_windows.exit)

    def display_objectives_windows(self,
                                   parent,
                                   rule_id,
                                   callback):
        self.comment_windows = smallWindows(master=parent,
                                            database=self.database,
                                            review_type=self.review_type)
        self.comment_windows.set_id(self.rule_id)
        self.comment_windows.create(title="DO-178 {:s} Objectives".format(self.review_type))
        result = Tool.getDesignReviewDoObjectives()
        list_objectives = []
        for objective_id,chapter,objective,description in result:
            list_objectives.append("{:d}) {:s} {:s}".format(objective_id,chapter,objective))
        left_frame = Frame(self.comment_windows.display_rule)
        self.comment_windows.create_listbox(frame=left_frame,
                                            height=6,
                                            width=80,
                                            list=list_objectives)
        self.comment_windows.create_text(frame=left_frame,
                                         width=60,
                                         title="Objective description in markdown language",
                                         height=8)
        left_frame.pack(side=LEFT)
        self.comment_windows.add_button(text="Add",
                                        help="Add a link between a rule and an objective",
                                        side=TOP,
                                        callback=lambda arg1=rule_id,arg2=callback: self.comment_windows.add_link_rule_to_objective(arg1,arg2))
        self.comment_windows.add_button(text="Quit",
                                        help="Back to the rule",
                                        side=TOP,
                                        callback=self.comment_windows.exit)

    def viewer_html(self,args=None):
        import os
        description=self.read()
        markdowner = Markdown()
        html = markdowner.convert(description)
        print "HTML:",html
        html_converted = Tool.replaceNonASCII(html)
        filename = join("result","preview.html")
        with open(filename, 'w') as of:
            of.write(html_converted)
        #os.startfile("result/{:s}".format(html_converted))
        webbrowser.open(filename,autoraise=1)

    def set_listbox_selection(self,event):
        index = self.status_listbox.curselection()[0]
        if index != ():
            item = self.status_listbox.get(index)
        else:
            item = None
        self.selection = item
        print "ITEM SELECTED",item

    def status_listbox_onselect(self,event):
        index = self.status_listbox.curselection()[0]
        if index != ():
            status = self.status_listbox.get(index)
        else:
            status = None
        print "STATUS",status
        Tool.updateRuleStatus(self.rule_id,status)

    def popupMenu(self,event):
        def popupFocusOut(event):
            popupmenu.unpost()
        defaultactions = {"Insert Image":lambda:self.edit_rule_menu(event),
                          "Create HTML table":lambda:self.create_html_table_menu(event)}
        popupmenu = Menu(self, tearoff = 0)
        for action,command in defaultactions.iteritems():
            popupmenu.add_command(label=action, command=command)
        popupmenu.bind("<FocusOut>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)

    def create_html_table_menu(self,event):
        table_string = '<thead><tr><th>Col1</th><th>Col2</th><th>Col3</th></tr></thead>'
        table_string += '<tbody><tr><td></td><td></td><td></td></tr></tbody>'
        self.help_text.insert(CURRENT,'<p><table>{:s}</table></p>'.format(table_string))

    def edit_rule_menu(self,event):
        import tkFileDialog
        import base64

        filename = tkFileDialog.askopenfilename(defaultextension='.png',
                                                filetypes=[('Image', '.png')],
                                                title="Get image")
        print "FILENAME",filename
        with open(filename,'rb') as f:
            data = f.read()
        string = base64.b64encode(data)
        print "STRING",string
        print "call edit_rule_menu"
        print "@%d,%d" % (event.x,event.y)
        print "Test menu"
        self.help_text.insert(CURRENT,'<p><image alt="inserted image" src="data:image/png;base64,{:s}" /></p>'.format(string))

    def create_text(self,
                    frame=None,
                    width=80,
                    height=6,
                    side=LEFT,
                    title="Description",
                    callback=None):
        if frame is None:
            frame = self.display_rule
        description_frame = Frame(frame)
        help_frame_label = Label(description_frame,
                                 text=title)
        help_frame_label.pack(anchor=W)
        help_frame = Frame(description_frame, bg="green")
        scrolltxt_first_area = scrollTxtArea(help_frame,
                                             wrap=WORD,
                                             width=width,
                                             height=height)
        #scrolltxt_first_area.text.bind("<Button-3>",self.popupMenu)
        help_frame.pack()
        description_frame.pack(anchor=N,side=side)
        self.help_text = scrolltxt_first_area.text
        if callback is not None:
            ok_button = Button(frame, text='Update', command=callback)
            ok_button.pack(side=TOP, anchor=E,fill=X)
        cancel_button = Button(frame, text='Quit', command=self.exit)
        cancel_button.pack(side=TOP, anchor=E,fill=X)
        return scrolltxt_first_area

    def create_combobox(self,
                       frame,
                       text=None,
                       height=2,
                       width=80,
                       list_items=("APPROVED","MODIFIED","TO BE MODIFIED","DELETED"),
                       callback=None):

        self.status_listbox = Pmw.ComboBox(frame,
                label_text = text,
                labelpos = 'nw',
                sticky = 'w',
                selectioncommand = self.set_listbox_selection,
                scrolledlist_items = list_items,
                dropdown = 0,
        )

        #self.status_listbox.pack(fill=BOTH, expand=1,anchor=W)
        self.status_listbox.pack(anchor=W)

    def overListbox(self,event,listbox):
        index = listbox.nearest(event.y)
        selection = listbox.get(index)
        m = re.match(r'([0-9]{1,3})\).*',selection)
        if m:
            objective_id = int(m.group(1))
        print "INDEX",index
        chapter,objective,description = Tool.getDoObjective(objective_id)
        print  "DESCRIPTION",description
        #balloon_help = Pmw.Balloon(listbox)
        #balloon_help.bind(listbox, description)
        # Display objective
        self.write(description)

    def create_listbox(self,
                       frame,
                       text=None,
                       height=2,
                       width=80,
                       list_items=("APPROVED","MODIFIED","TO BE MODIFIED","DELETED"),
                       callback=None):

        if text is None:
            self.status_frame = Frame(frame,
                                      #bg="white",
                                      bd=0)
        else:
            self.status_frame = LabelFrame(frame,
                                           #bg="white",
                                           text=text,
                                           bd=0)
        self.status_frame.pack()
        self.status_listbox = Listbox(self.status_frame,height=height,width=width)
        self.vbar_crlisbox = vbar_crlisbox = Scrollbar(self.status_frame, name="vbar_crlisbox")
        self.vbar_crlisbox.pack(side=RIGHT, fill=Y)
        vbar_crlisbox["command"] = self.status_listbox.yview
        self.status_listbox["yscrollcommand"] = vbar_crlisbox.set
        self.status_listbox.bind("<Double-Button-1>", callback)
        self.status_listbox.bind("<Button-3>", lambda event, arg=self.status_listbox: self.overListbox(event, arg))
        self.status_listbox.bind("<MouseWheel>", self.crlistbox_scrollEvent)
        self.status_listbox.bind("<Key-Up>", lambda event, arg=self.status_listbox: self.up_event(event, arg))
        self.status_listbox.bind("<Key-Down>", lambda event, arg=self.status_listbox: self.down_event(event, arg))
        self.status_listbox.bind("<ButtonRelease-1>", self.set_listbox_selection)
        inter = 0
        for status in list_items:
            self.status_listbox.insert(END, status)
            if inter % 2 == 0:
                self.status_listbox.itemconfig(inter, {'bg': 'gray88', 'fg': 'black'})
            else:
                self.status_listbox.itemconfig(inter, {'bg': 'lightgrey', 'fg': 'black'})
            inter += 1
        self.status_listbox.pack(fill=BOTH, expand=1,anchor=W)
        #self.status_listbox.pack(anchor=W)

    def create_rule(self,
                    text="Description",
                    rule_tag="",
                   width=80,
                   height=20,
                   callback=None,
                   callback2=None,
                   callback3=None):
        self.create_text(width=width,
                        height=height,
                        title=text)
        self.help_text.bind("<Button-3>",self.popupMenu)
        right_frame = Frame(self.display_rule,width=50)
        # DO-178 Objectives
        self.objectives_frame = LabelFrame(right_frame,
                                           #bg="white",
                                           text="Objectives",
                                           bd=0)
        self.display_objectives = Text(self.objectives_frame,
                                               width=40,
                                               height=4,
                                               #bg="gray"
                                               )
        self.display_objectives.pack(expand=1)
        self.button_add_objective = Button(self.objectives_frame,
                                           text='Add',
                                           command=lambda arg1=self.display_rule,arg2=self.rule_id,arg3=callback2: self.display_objectives_windows(arg1,arg2,arg3))
        self.button_add_objective.pack(padx=5,anchor=E)
        balloon_help = Pmw.Balloon(self.objectives_frame)
        balloon_help.bind(self.button_add_objective, 'Add a link to DO-178\n'
                                                     'Software Design Review\n'
                                                     'Objectives')

        self.objectives_frame.pack()
        # Rule status
        self.create_combobox(right_frame,
                            width=40,
                            text="Status",
                            callback=self.status_listbox_onselect)

        self.entry_version = self.createEntry(frame=right_frame,
                                              tag='Version',
                                              content="",
                                              entry_size=8,
                                              width=40)
        self.entry_version.pack(anchor=W)
        right_frame.pack()
        bottom_frame = Frame(self.display_rule, bg="red",width=400)
        show_comments_button = Button(bottom_frame,
                                      text='Show Comments',
                                      command=lambda arg1=rule_tag: self.display_comment_windows(rule_tag))
        show_comments_button.pack(side=LEFT,anchor=E)
        ok_button = Button(bottom_frame, text='Update', command=lambda arg=callback3: callback(callback3))
        ok_button.pack(side=LEFT, anchor=E)
        view_html = Button(bottom_frame, text='Preview', command=self.viewer_html)
        view_html.pack(side=LEFT, anchor=E)
        #cancel_button = Button(bottom_frame, text='Quit', command=self.display_rule.destroy)
        cancel_button = Button(bottom_frame, text='Quit', command=self.exit)
        cancel_button.pack(side=LEFT,anchor=E)
        bottom_frame.pack(anchor=E)

    def create_req_deprecated(self,
                    text="Description",
                    rule_tag="",
                   width=80,
                   height=20,
                   callback=None,
                   callback2=None,
                   callback3=None):
        self.create_text(width=width,
                        height=height,
                        title=text)
        self.help_text.bind("<Button-3>",self.popupMenu)
        right_frame = Frame(self.display_rule,width=50)
        # DO-178 Objectives
        self.objectives_frame = LabelFrame(right_frame,
                                           #bg="white",
                                           text="Refers to",
                                           bd=0)
        self.display_objectives = Text(self.objectives_frame,
                                               width=40,
                                               height=4,
                                               #bg="gray"
                                               )
        self.display_objectives.pack(expand=1)
        if 0==1:
            self.button_add_objective = Button(self.objectives_frame,
                                               text='Add',
                                               command=lambda arg1=self.display_rule,arg2=self.rule_id,arg3=callback2: self.display_objectives_windows(arg1,arg2,arg3))
            self.button_add_objective.pack(padx=5,anchor=E)
            balloon_help = Pmw.Balloon(self.objectives_frame)
            balloon_help.bind(self.button_add_objective, 'Add a link to DO-178\n'
                                                         'Software Design Review\n'
                                                         'Objectives')

        self.objectives_frame.pack()
        # Rule status
        self.create_combobox(right_frame,
                            width=40,
                            text="Status",
                            list=("MATURE","TBD","TBC"),
                            callback=self.status_listbox_onselect)

        self.entry_version = self.createEntry(frame=right_frame,
                                              tag='Version',
                                              content="",
                                              entry_size=8,
                                              width=40)
        self.entry_version.pack(anchor=W)
        right_frame.pack()
        bottom_frame = Frame(self.display_rule, bg="red",width=400)
        show_comments_button = Button(bottom_frame,
                                      text='Show Comments',
                                      command=lambda arg1=rule_tag: self.display_comment_windows(rule_tag))
        show_comments_button.pack(side=LEFT,anchor=E)
        ok_button = Button(bottom_frame, text='Update', command=lambda arg=callback3: callback(callback3))
        ok_button.pack(side=LEFT, anchor=E)
        view_html = Button(bottom_frame, text='Preview', command=self.viewer_html)
        view_html.pack(side=LEFT, anchor=E)
        #cancel_button = Button(bottom_frame, text='Quit', command=self.display_rule.destroy)
        cancel_button = Button(bottom_frame, text='Quit', command=self.exit)
        cancel_button.pack(side=LEFT,anchor=E)
        bottom_frame.pack(anchor=E)

    def create(self,
               icon="ico_sys_desktop.ico",
               title="",
               bg="#80c0c0",
               width=80,
               height=8,
               labels=("", ""),
               callback=None,
               master=None):
        self.display_rule = Toplevel(master=master)
        self.setWindowPos(self.display_rule)
        self.display_rule.iconbitmap(icon)
        self.display_rule.title(title)
        self.display_rule.resizable(False, False)
        self.display_rule.grab_set()
        self.display_rule.focus_set()

    def write_objectives(self, list_objectives):
        for type_objective,chapter,objective in list_objectives:
            print "list_objectives",list_objectives
            self.display_objectives.insert(END, chapter + " " + type_objective + ": " + objective + "\n")
        self.objectives_frame.pack(anchor=W)

    def write_refers_to_deprecated(self, list_refers_to):
        for refer in list_refers_to:
            self.display_objectives.insert(END, refer + "\n")
        self.objectives_frame.pack(anchor=W)

    def set_id(self, rule_id):
        self.rule_id = rule_id

class smallWindowsReq(smallWindows):
    def create_rule(self,
                text="Description",
                rule_tag="",
               width=80,
               height=20,
               callback=None,
               callback2=None,
               callback3=None):
        self.create_text(width=width,
                        height=height,
                        title=text)
        self.help_text.bind("<Button-3>",self.popupMenu)
        right_frame = Frame(self.display_rule,width=50)
        # DO-178 Objectives
        self.objectives_frame = LabelFrame(right_frame,
                                           #bg="white",
                                           text="Refers to",
                                           bd=0)
        self.display_objectives = Text(self.objectives_frame,
                                               width=40,
                                               height=4,
                                               #bg="gray"
                                               )
        self.display_objectives.pack(expand=1)
        if 0==1:
            self.button_add_objective = Button(self.objectives_frame,
                                               text='Add',
                                               command=lambda arg1=self.display_rule,arg2=self.rule_id,arg3=callback2: self.display_objectives_windows(arg1,arg2,arg3))
            self.button_add_objective.pack(padx=5,anchor=E)
            balloon_help = Pmw.Balloon(self.objectives_frame)
            balloon_help.bind(self.button_add_objective, 'Add a link to DO-178\n'
                                                         'Software Design Review\n'
                                                         'Objectives')

        self.objectives_frame.pack()
        # Rule status
        self.create_combobox(right_frame,
                            width=40,
                            text="Status",
                            list=("MATURE","TBD","TBC"),
                            callback=self.status_listbox_onselect)

        self.entry_version = self.createEntry(frame=right_frame,
                                              tag='Version',
                                              content="",
                                              entry_size=8,
                                              width=40)
        self.entry_version.pack(anchor=W)
        right_frame.pack()
        bottom_frame = Frame(self.display_rule, bg="red",width=400)
        show_comments_button = Button(bottom_frame,
                                      text='Show Comments',
                                      command=lambda arg1=rule_tag: self.display_comment_windows(rule_tag))
        show_comments_button.pack(side=LEFT,anchor=E)
        ok_button = Button(bottom_frame, text='Update', command=lambda arg=callback3: callback(callback3))
        ok_button.pack(side=LEFT, anchor=E)
        view_html = Button(bottom_frame, text='Preview', command=self.viewer_html)
        view_html.pack(side=LEFT, anchor=E)
        #cancel_button = Button(bottom_frame, text='Quit', command=self.display_rule.destroy)
        cancel_button = Button(bottom_frame, text='Quit', command=self.exit)
        cancel_button.pack(side=LEFT,anchor=E)
        bottom_frame.pack(anchor=E)

    def write_objectives(self, list_refers_to):
        for refer in list_refers_to:
            self.display_objectives.insert(END, refer + "\n")
        self.objectives_frame.pack(anchor=W)

class Std(TableCanvas):
    """
    To manage projets set
    """

    dico_objectives={"SRS":"Software Requirements Review",
                     "SDS":"Software Design Review",
                     "SCS":"Software Coding Review"}
    def __init__(self,
                 parent=None,
                 model=None,
                 width=None,
                 height=None,
                 rows=10,
                 cols=5,
                 editable=False,
                 database=None,
                 sds_type=None,
                 **kwargs):
        TableCanvas.__init__(self, parent,
                        bg='white',
                        width=width,
                        height=height,
                        relief=GROOVE,
                        scrollregion=(0, 0, 150, 100))
        if database is not None:
            print "DATABASE:",database
            self.database = database
        self.sds_type=sds_type
        self.cellbackgr = '#FFFAF0'
        self.entrybackgr = 'white'

        self.selectedcolor = 'yellow'
        self.rowselectedcolor = '#B0E0E6'
        self.multipleselectioncolor = '#ECD672'
        self.parentframe = parent
        #get platform into a variable
        self.ostyp = self.checkOSType()
        if "log" in self.__dict__:
            self.log("ostyp" + self.ostyp, False)  # From Interface class
        self.platform = platform.system()
        if "log" in self.__dict__:
            self.log("platform" + self.platform, False)  # From Interface class
        self.width = width
        self.height = height
        self.set_defaults()

        self.currentpage = None
        self.navFrame = None
        self.currentrow = 0
        self.currentcol = 0
        self.reverseorder = 0
        self.startrow = self.endrow = None
        self.startcol = self.endcol = None
        self.allrows = False  #for selected all rows without setting multiplerowlist
        self.multiplerowlist = []
        self.multiplecollist = []
        self.col_positions = []  #record current column grid positions
        self.mode = 'normal'
        self.editable = editable
        self.filtered = False

        self.loadPrefs()
        #set any options passed in kwargs to overwrite defaults and prefs
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        if model is None:
            self.model = TableModel(rows=rows, columns=cols)
        else:
            self.model = model

        self.rows = self.model.getRowCount()
        self.cols = self.model.getColumnCount()
        self.tablewidth = self.cellwidth * self.cols
        #self.do_bindings()
        #initial sort order
        self.model.setSortOrder()

        #column specific actions, define for every column type in the model
        #when you add a column type you should edit this dict
        self.columnactions = {'text': {"Edit": 'drawCellEntry'},
                              'number': {"Edit": 'drawCellEntry'}}
        self.setFontSize()

    def user_handle_left_click(self,event):
        """Does cell selection when mouse is clicked on canvas"""

        self.delete('rect')
        self.delete('entry')
        self.delete('multicellrect')
        rclicked = self.get_row_clicked(event)
        colclicked = self.get_col_clicked(event)
        if colclicked is None:
            return
        column_name = self.model.getColumnLabel(colclicked)
        print "column_name",column_name
        if column_name is "Rule ID":
            return
        #set all rows selected
        self.allrows = True
        self.setSelectedCol(colclicked)

        #if self.atdivider == 1:
        #    return
        self.drawRect(rclicked,colclicked)
        #also draw a copy of the rect to be dragged
        self.draggedcol = None
        self.drawRect(rclicked,colclicked,
                      tag='dragrect',
                      color='red')
        if hasattr(self, 'rightmenu'):
            self.rightmenu.destroy()
        #finally, draw the selected col on the table
        self.drawSelectedCol()

    def refreshObjectives(self,rule_id):
        # Objectives
        list_objectives = Tool.getRuleObjectives(rule_id,self.database)
        self.small_windows.write_objectives(list_objectives)

    def user_handle_double_click(self, event,callback_refresh_all):  #Click event callback function.
        def callback(callback_refresh_all=None):
            update_text=self.small_windows.read()
            version = self.small_windows.get_version()
            status = self.small_windows.get_status()
            Tool.updateRule(tag=rule_id,
                            txt=update_text,
                            status=status,
                            version=version,
                            database=self.database)
            print "updateRule",update_text
            #print "Current page:",self.currenttable
            # Refresh parent window
            callback_refresh_all()

        def callback_do():
            update_text=self.small_windows.help_text.get(1.0, END)
            Tool.updateDo(objective_id,update_text,self.database)
            print "update do-178 objective",update_text

        #Probably needs better exception handling, but w/e.
        #try:
        rclicked = self.get_row_clicked(event)
        cclicked = self.get_col_clicked(event)
        clicks = (rclicked, cclicked)
        print 'clicks:', clicks
        column_name = self.model.getColumnLabel(cclicked)
        rule_id_column = re.search(r'Rule ID',column_name)
        do_objectives_column = re.search(r'Objective ID',column_name)
        if not rule_id_column and not do_objectives_column:
            #absrow = self.get_AbsoluteRow(row)
            model=self.getModel()
            cellvalue = model.getCellRecord(rclicked, cclicked)
            if Formula.isFormula(cellvalue):
                self.formula_Dialog(rclicked, cclicked, cellvalue)
        else:
            print "column_name = ",column_name
            #except:
            #    print 'Error'
            if clicks:
                if rule_id_column:
                    #Now we try to get the value of the row+col that was clicked.
                    #try:
                    if 1==1:
                        #if clicks[1] == 0:
                        rule = self.model.getValueAt(clicks[0], clicks[1])
                        m = re.match(r'.*_0?([0-9]{1,3})',rule)
                        if m:
                            rule_id = m.group(1).lstrip("0")
                            # Create windows for rule attributes
                            txt,status,version = Tool.getSDTS_Rule(tag=rule_id,database=self.database)
                            self.small_windows = smallWindows(database=self.database,
                                                              review_type=self.dico_objectives[self.sds_type])
                            self.small_windows.set_id(rule_id)
                            self.small_windows.create(title=rule)
                            # Description
                            self.small_windows.create_rule(text="Description of the rule in markdown language",
                                                           rule_tag=rule,
                                                           callback=callback,
                                                           callback2=self.refreshObjectives,
                                                           callback3=callback_refresh_all)
                            self.small_windows.write(txt)
                            # Status
                            self.small_windows.status_focus(status)
                            # Objectives
                            self.refreshObjectives(rule_id)
                            # Version
                            self.small_windows.write_version(version)
                    #except:
                    #    print 'No record at:', clicks
                elif do_objectives_column:
                    objective_id = self.model.getValueAt(clicks[0], clicks[1])
                    chapter,objective,txt = Tool.getDoObjective(objective_id,database=self.database)
                    self.small_windows = smallWindows(database=self.database)
                    self.small_windows.create(title="DO-178 chapter {:s} {:s}".format(chapter,objective))
                    self.small_windows.create_text(width=80,
                                                    height=8,
                                                    title="Objective Description",
                                                    callback=callback_do)
                    self.small_windows.write(txt)

                #This is how you can get the entire contents of a row.
                try: print 'entire record:', self.model.getRecordAtRow(clicks[0])
                except: print 'No record at:', clicks

    def do_bindings(self,callback=None):
        if callback is None:
            print "Missing callback for do_bindings line 1360"
        #print "Std custom do_bindings"
        #self.bind("<Button-1>",self.user_handle_left_click)
        self.bind("<Double-Button-1>",lambda event,arg=callback: self.user_handle_double_click(event,arg))
        if self.ostyp=='mac':
            #For mac we bind Shift, left-click to right click
            self.bind("<Button-2>", self.handle_right_click)
            self.bind('<Shift-Button-1>',self.handle_right_click)
        else:
            self.bind("<Button-3>", self.handle_right_click)

    def setListDoObjectives(self,page):
        result = Tool.getDesignReviewDoObjectives(database=self.database)
        index = 1
        data = {}
        for objective_id,chapter,objective,description in result:
            data[index] = {}
            data[index]["Objective ID"] = objective_id
            data[index]["Chapter"] = chapter
            data[index]["Objective"] = objective
            data[index]["Description"] = description
            index += 1
        index_max = page.model.getRowCount()
        print "index_max", index_max
        while index <= index_max:
            data[index] = {}
            data[index]["Objective ID"] = ""
            data[index]["Chapter"] = ""
            data[index]["Objective"] = ""
            data[index]["Description"] = ""
            index += 1
        model = TableModel()
        model.importDict(data)
        print "DATA _refreshTableProject", data
        page.model.importDict(data)
        # self.table_project.setModel(model)
        page.updateModel(model)
        page.redrawTable()

    def setList(self,
                by_req=True,
                page=None):
        print "setList for class Std"
        result = Tool.getAll_SDTS_Rule_by_req(by_req=by_req,
                                              version=self.version,
                                              database=self.database)
        if result:
            if by_req:
                rule_type = "REQ_"
            else:
                rule_type = ""
            sorted_result = sorted(result,key=lambda x: x[1])#,reverse=True)
            self._refreshTableProject(page,
                                      sorted_result,
                                      std_type=self.sds_type,
                                      rule_type=rule_type)

    def _refreshTableProject(self,
                             page,
                             project_list,
                             std_type="",
                             rule_type=""):
        print "_refreshTableProject from class Std"
        index = 1
        data = {}
        for comment_id,tag,status,version,description,auto,comments in project_list:
            data[index] = {}
            str_id = "{:d}".format(tag)
            data[index]["Rule ID"] = "{:s}_{:s}{:s}".format(std_type,rule_type,str_id.zfill(3))
            data[index]["Version"] = version
            data[index]["Status"] = status
            index += 1
        index_max = page.model.getRowCount()
        print "index_max", index_max
        while index <= index_max:
            data[index] = {}
            data[index]["Rule ID"] = ""
            data[index]["Version"] = ""
            data[index]["Status"] = ""
            index += 1
        model = TableModel()
        model.importDict(data)
        print "DATA _refreshTableProject", data
        page.model.importDict(data)
        # self.table_project.setModel(model)
        page.updateModel(model)
        page.redrawTable()

class Std_Req(Std):
    def __init__(self,
             parent=None,
             model=None,
             width=None,
             height=None,
             rows=10,
             cols=5,
             editable=False,
             database=None,
             sds_type=None,
             **kwargs):
        Std.__init__(self,parent,model,width,height,rows,cols,editable,database,sds_type,**kwargs)

    def setList(self,
                by_req=False,
                page=None):
        print "setList for class Std_Req"
        swrd = ExtractReq()
        result = swrd.restoreFromSQLite()

        #result = Tool.getAll_SWRD_req(database=self.database)
        if result:
            sorted_result = sorted(result,key=lambda x: x[0])
            self._refreshTableProject(page,
                                  sorted_result,
                                  std_type=self.sds_type)

    def _refreshTableProject(self,
                             page,
                             project_list,
                             std_type="",
                             rule_type=""):
        """

        :param page:
        :param project_list:
        :param std_type:
        :param rule_type:
        """
        index = 1
        data = {}
        page.reqs_tag_vs_id = {}
        # TODO: Ajouter un lien entre id et tag
        for req_id,tag,body,issue,refer,status,derived,terminal,rationale,safety,additional in project_list:
            page.reqs_tag_vs_id[tag]=req_id
            data[index] = {}
            data[index]["Req ID"] = tag
            #data[index]["Version"] = issue
            #data[index]["Status"] = status
            index += 1
        index_max = page.model.getRowCount()
        print "index_max", index_max
        while index <= index_max:
            data[index] = {}
            data[index]["Req ID"] = ""
            #data[index]["Version"] = ""
            #data[index]["Status"] = ""
            index += 1
        model = TableModel()
        model.importDict(data)
        #print "DATA _refreshTableProject", data
        page.model.importDict(data)
        # self.table_project.setModel(model)
        page.updateModel(model)
        page.redrawTable()

    def refreshObjectives(self,str_refer):
        # Refers To
        list_refer = ExtractReq.getSplitRefer(str_refer,type="[A-Z]*_[\w-]*") #"SWRD_[\w-]*"
        self.small_windows.write_objectives(list_refer)

    def user_handle_double_click(self, event,callback_refresh_all):  #Click event callback function.
        def callback(callback_refresh_all=None):
            print "req callback"

        #Probably needs better exception handling, but w/e.
        #try:
        rclicked = self.get_row_clicked(event)
        cclicked = self.get_col_clicked(event)
        clicks = (rclicked, cclicked)
        print 'clicks:', clicks
        column_name = self.model.getColumnLabel(cclicked)
        rule_id_column = re.search(r'Req ID',column_name)
        if not rule_id_column:
            #absrow = self.get_AbsoluteRow(row)
            model=self.getModel()
            cellvalue = model.getCellRecord(rclicked, cclicked)
            if Formula.isFormula(cellvalue):
                self.formula_Dialog(rclicked, cclicked, cellvalue)
        else:
            print "column_name = ",column_name
            #except:
            #    print 'Error'
            if clicks:
                if rule_id_column:
                    #Now we try to get the value of the row+col that was clicked.
                    #try:
                    #if clicks[1] == 0:
                    tag = self.model.getValueAt(clicks[0], clicks[1])
                    print "TAG clicked:",tag
                    if tag in self.reqs_tag_vs_id:
                        req_id = self.reqs_tag_vs_id[tag]
                        # Create windows for rule attributes
                        sql_req = SQLite(database=self.database)
                        sql_req.connect()
                        sql_req_id,tag,body,issue,refer,status,derived,terminal,rationale,safety,additional = sql_req.get(id=req_id)
                        sql_req.close()
                        self.small_windows = smallWindowsReq(database=self.database)
                        # TODO: passer en argument
                        self.small_windows.set_id(req_id)
                        self.small_windows.create(title=tag)
                        # Description
                        self.small_windows.create_rule(text="Description of the requirement in markdown language",
                                                       rule_tag=tag,
                                                       callback=callback,
                                                       callback2=self.refreshObjectives,
                                                       callback3=callback_refresh_all)
                        self.small_windows.write(body)
                        # Status
                        self.small_windows.status_focus(status,
                                                        list_items=("MATURE","TBD","TBC"))
                        # Refers to
                        print "REFER:",refer
                        if refer:
                            self.refreshObjectives(refer)
                        # Version
                        self.small_windows.write_version(issue)
                    #except:
                    #    print 'No record at:', clicks

                #This is how you can get the entire contents of a row.
                try: print 'entire record:', self.model.getRecordAtRow(clicks[0])
                except: print 'No record at:', clicks

    def do_bindings(self,callback=None):
        if callback is None:
            print "Missing callback for do_bindings of class Std_Req"
        #print "Std custom do_bindings"
        #self.bind("<Button-1>",self.user_handle_left_click)
        self.bind("<Double-Button-1>",lambda event,arg=callback: self.user_handle_double_click(event,arg))
        if self.ostyp=='mac':
            #For mac we bind Shift, left-click to right click
            self.bind("<Button-2>", self.handle_right_click)
            self.bind('<Shift-Button-1>',self.handle_right_click)
        else:
            self.bind("<Button-3>", self.handle_right_click)

class ThreadSafeListbox(Listbox):
    """
    This class create a widget Listbox thread safe
    """

    def __init__(self, master, **options):
        Listbox.__init__(self, master, **options)
        self.queue = Queue.Queue()
        self.update_me()

    def write(self, line):
        #print "call write method"
        self.queue.put("write")
        self.queue.put(line)

    def clear(self):
        #print "call clear method"
        self.queue.put("delete")

    def white(self):
        #print "call white method"
        self.queue.put("white")

    def begin(self):
        #print "call begin method"
        self.queue.put("begin")

    def enable(self):
        #print "call enable method"
        self.queue.put("enable")

    def disable(self):
        #print "call enable method"
        self.queue.put("disable")

    def update_me(self):
        try:
            while 1:
                cmd = self.queue.get_nowait()
                if cmd == "delete":
                    #print "ThreadSafeListbox delete method"
                    self.delete(0, END)
                elif cmd == "white":
                    #print "ThreadSafeListbox white method"
                    self.configure(bg="white")
                elif cmd == "enable":
                    #print "ThreadSafeListbox enable method"
                    self.configure(state=NORMAL)
                elif cmd == "disable":
                    #print "ThreadSafeListbox enable method"
                    self.configure(state=DISABLED)
                elif cmd == "begin":
                    #print "ThreadSafeListbox begin method"
                    self.selection_set(first=0)
                elif cmd == "write":
                    #print "ThreadSafeListbox write method"
                    line = self.queue.get_nowait()
                    self.insert(END, str(line))
                else:
                    print "ThreadSafeListbox unknown method"
                    print "method:", cmd
                #self.see(END)
                self.update_idletasks()
        except Queue.Empty:
            pass
        self.after(100, self.update_me)

class ManageStdGui(Frame,
                   Toplevel,
                   Text):
    dico_sheetnames={"general":"General","by_req":"By Requirement","do":"DO-178 Design Review Objectives"}
    def online_documentation(self,event=None):
        """Open the online documentation"""
        import webbrowser
        link='file:///C:/Users/olivier.appere/DesignEditor/srts_rules.html#'
        webbrowser.open(link,autoraise=1)

    @staticmethod
    def export_xml():
        import xml.etree.ElementTree as ET
        type_standard = "SDTS"
        if type_standard == "SRTS":
            database = "db/srts_rules.db3"
            xml_filename = "result\\srts_rules_list.xml"
        elif type_standard == "SDTS":
            database = "db/sdts_rules.db3"
            xml_filename = "result\\sdts_rules_list.xml"
        else:
            database = "db/scs_rules.db3"
            xml_filename = "result\\scs_rules_list.xml"
        root = ET.Element("STD")
        result = Tool.getAll_SDTS_Rule_by_req(by_req=True,database=database)
        # TODO: add link to DO-178
        for comment_id,status,version,description,auto,comments in sorted(result):
            if status is None:
                status = ""
            if version is None:
                version = ""
            if auto is None:
                auto = ""
            if comments is None:
                comments = ""
            if auto == 1:
                auto_attrib = "YES"
            elif auto == 2:
                auto_attrib = "PARTIALLY"
            elif auto == 3:
                auto_attrib = "MAYBE"
            else:
                auto_attrib = "NO"
            str_id = "{:d}".format(comment_id)
            list_objectives = Tool.getRuleObjectives(str_id,database = database)
            rule_node = ET.SubElement(root, "RULE",attrib={"id":str_id,
                                                            "status":status,
                                                            "version":version,
                                                            "auto":auto_attrib,
                                                            "by_req":"TRUE"})
            desc_node = ET.SubElement(rule_node, "DESC")
            markdowner = Markdown()
            rule_in_html = markdowner.convert(description)
            desc_node.text = rule_in_html
            print "HTML:",rule_in_html
            #desc_node.text = Tool.replaceNonASCII(description,html=True)
            if list_objectives is not None:
                for chapter,objective in list_objectives:
                    do_node = ET.SubElement(rule_node, "DO")
                    do_node.text = "{:s} {:s}".format(chapter,objective)
            comment_node = ET.SubElement(rule_node, "COMMENTS")
            comment_node.text = Tool.replaceNonASCII(comments,html=True)
            #print "DESC:",clean_description
            #if id == "37":
            #    break
        tree = ET.ElementTree(root)
        tree.write(xml_filename)

    def setcurrenttable(self, event):
        """Set the currenttable so that menu items work with visible sheet"""
        try:
            s = self.notebook.getcurselection()
            self.currenttable = self.sheets[s]
        except:
            pass
        return

    def add_Sheet_Req(self,
                  sheetname=None,
                  sheetdata=None,
                  import_dict=False):
        """Add a new sheet - handles all the table creation stuff"""
        def checksheet_name(name):
            if name == '':
                tkMessageBox.showwarning("Whoops", "Name should not be blank.")
                return 0
            if self.sheets.has_key(name):
                tkMessageBox.showwarning("Name exists", "Sheet name already exists!")
                return 0
        noshts = len(self.notebook.pagenames())
        if sheetname is None:
            sheetname = tkSimpleDialog.askstring("New sheet name?", "Enter sheet name:",
                                                initialvalue='sheet'+str(noshts+1))
        checksheet_name(sheetname)
        page = self.notebook.add(sheetname)
        #Create the table and model if data present
        if sheetdata is not None:
            if import_dict:
                model = TableModel()
                model.importDict(sheetdata)
            else:
                model = TableModel(newdict=sheetdata)
                #model.importDict(sheetdata)
            print "Std_Req"
            self.currenttable = Std_Req(page,
                                    model=model,
                                    reverseorder=1,
                                    editable=True,
                                    rowheaderwidth=100,
                                    showkeynamesinheader=True,
                                    database=self.database,
                                    sds_type=self.sds_type,
                                    )
        else:
            self.currenttable = Std_Req(page,
                                    database=self.database,
                                    sds_type=self.sds_type)

        #Load preferences into table
        self.currenttable.loadPrefs()
        #This handles all the canvas and header in the frame passed to constructor
        self.currenttable.createTableFrame()
        #add the table to the sheet dict
        self.sheets[sheetname] = self.currenttable
        self.saved = 0
        return sheetname

    def add_Sheet(self,
                  sheetname=None,
                  sheetdata=None,
                  import_dict=False):
        """Add a new sheet - handles all the table creation stuff"""
        def checksheet_name(name):
            if name == '':
                tkMessageBox.showwarning("Whoops", "Name should not be blank.")
                return 0
            if self.sheets.has_key(name):
                tkMessageBox.showwarning("Name exists", "Sheet name already exists!")
                return 0
        noshts = len(self.notebook.pagenames())
        if sheetname is None:
            sheetname = tkSimpleDialog.askstring("New sheet name?", "Enter sheet name:",
                                                initialvalue='sheet'+str(noshts+1))
        checksheet_name(sheetname)
        page = self.notebook.add(sheetname)
        #Create the table and model if data present
        if sheetdata is not None:
            if import_dict:
                model = TableModel()
                model.importDict(sheetdata)
            else:
                model = TableModel(newdict=sheetdata)
                #model.importDict(sheetdata)
            print "Std"
            self.currenttable = Std(page,
                                    model=model,
                                    reverseorder=1,
                                    editable=True,
                                    rowheaderwidth=100,
                                    showkeynamesinheader=True,
                                    database=self.database,
                                    sds_type=self.sds_type,
                                    )
        else:
            self.currenttable = Std(page,
                                    database=self.database,
                                    sds_type=self.sds_type)

        #Load preferences into table
        self.currenttable.loadPrefs()
        #This handles all the canvas and header in the frame passed to constructor
        self.currenttable.createTableFrame()
        #add the table to the sheet dict
        self.sheets[sheetname] = self.currenttable
        self.saved = 0
        return sheetname

    def refreshAll(self):
        # Page General
        self.setList(by_req=False,page=self.sheets[self.dico_sheetnames['general']])
        # Page By Requirement
        self.setList(by_req=True,page=self.sheets[self.dico_sheetnames['by_req']])
        # Page DO-178 Objectives
        self.setListDoObjectives(page=self.sheets[self.dico_sheetnames['do']])

    def refreshReq(self):
        self.setList(by_req=True,page=self.sheets[self.dico_sheetnames['by_req']])

    @staticmethod
    def setWindowPos(window):
        global fenetre
        x = fenetre.winfo_rootx()
        y = fenetre.winfo_rooty()
        geom = "+%d+%d" % (x + 20, y + 20)
        print
        geom
        window.geometry(geom)

    def __init__(self,
                 fenetre,
                 database,
                 version=None,
                 std_type="SDS",
                 queue=None):
        self.queue = queue
        self.fenetre = fenetre
        self.database=database
        self.version=version
        self.sds_type=std_type
        self.overall_frame = None

    def displaySCS(self):
        self.database="db/scs_rules.db3"
        self.version=None
        self.sds_type="SCS"
        self.createMainWin()

    def displaySDTS(self):
        self.database="db/sdts_rules.db3"
        self.version=None
        self.sds_type="SDS"
        self.createMainWin()

    def displaySRTS(self):
        self.database="db/srts_rules.db3"
        self.version=None
        self.sds_type="SRS"
        self.createMainWin()

    def displaySWRD(self):
        self.database="db/swrd.db3"
        self.version=None
        self.sds_type="SWRD"
        self.createMainWinReq()

    def importSWRD(self):
        self.queue.put("IMPORT_SWRD")

    def smallWindowForIS(self,query="EXPORT_IS_HLR"):
        def callback():
            print "Click OK"
            self.queue.put("EXPORT_IS_HLR")  # order to check HLR
            return True
        self.window_for_export_is = Toplevel()
        self.setWindowPos(self.window_for_export_is)
        self.window_for_export_is.iconbitmap("ico_sys_desktop.ico")
        self.window_for_export_is.title("IS Information")
        self.window_for_export_is.resizable(False, False)
        self.window_for_export_is.grab_set()
        self.window_for_export_is.focus_set()
        check_reqs = Frame(self.window_for_export_is)
        check_reqs.pack()
        # Image
        last_pane = Frame(check_reqs, padx=20, pady=30)
        last_pane.pack(side=LEFT)
        #Drawing
        self.check_reqs_img_can = Canvas(last_pane, width=128, height=128, highlightthickness=0)
        try:
            bitmap = PhotoImage(file="img/kghostview.gif")
            self.check_reqs_img = self.check_reqs_img_can.create_image(64, 64, image=bitmap)
            self.check_reqs_img_can.bitmap = bitmap
        except TclError as exception:
            print
            "TCL error:", exception
        self.check_reqs_img_can.pack(fill=Y)
        box_param = Frame(check_reqs, padx=10)
        box_param.pack(anchor=W)
        ok_button = Button(check_reqs,
                           text='OK',
                           command=callback)
        ok_button.pack(side=TOP, anchor=E,fill=X)
        cancel_button = Button(check_reqs,
                               text='Cancel',
                               command=self.window_for_export_is.destroy)
        cancel_button.pack(side=TOP,anchor=E,fill=X)

    def genInspectSheetHLR(self):
        if 0==1:
            self.getGUICRStatus()
            self.selectCR_Domain()
            self.getGUICRType(self.system,
                              self.item)
        self.smallWindowForIS(query="EXPORT_IS_HLR")

    def createMainWinReq(self):
        if self.overall_frame is not None:
            self.overall_frame.destroy()
        Frame.__init__(self,self.fenetre)
        page = fenetre
        self.overall_frame = LabelFrame(page, bd=0, text='')
        self.overall_frame.pack(anchor=W)
        self.notebook = Pmw.NoteBook(self.overall_frame, raisecommand=self.setcurrenttable)
        self.notebook.pack(fill='both', expand=1, padx=4, pady=4)
        data = {"colnames": {"Rule ID": "", "Version": "", "Status": "", "Objective": ""},
                "columnorder":{1:"Rule ID",2:"Version",3:"Status",4:"Objective"},
                "columnlabels":{},
                "columntypes":{"Rule ID":"text","Version":"text","Status":"text","Objective":"text"}}
        self.sheets = {}
        self.add_Sheet_Req(sheetname=self.dico_sheetnames['by_req'],sheetdata=data)
        self.currenttable.setList(page=self.sheets[self.dico_sheetnames['by_req']])
        self.currenttable.do_bindings(self.refreshReq)
        ok_button = Button(self.overall_frame, text='OK', command=self.fenetre.destroy)
        ok_button.pack(side=LEFT, anchor=E)
        refresh_button = Button(self.overall_frame, text='Refresh', command=self.refreshReq)
        refresh_button.pack(side=LEFT, anchor=E)
        cancel_button = Button(self.overall_frame, text='Quit', command=self.fenetre.destroy)
        cancel_button.pack(anchor=E)


    def createMainWin(self):
        if self.overall_frame is not None:
            self.overall_frame.destroy()
        Frame.__init__(self,self.fenetre)
        page = fenetre
        self.overall_frame = LabelFrame(page, bd=0, text='')
        self.overall_frame.pack(anchor=W)
        self.notebook = Pmw.NoteBook(self.overall_frame, raisecommand=self.setcurrenttable)
        self.notebook.pack(fill='both', expand=1, padx=4, pady=4)

        data = {"colnames": {"Rule ID": "", "Version": "", "Status": "", "Objective": ""},
                "columnorder":{1:"Rule ID",2:"Version",3:"Status",4:"Objective"},
                "columnlabels":{},
                "columntypes":{"Rule ID":"text","Version":"text","Status":"text","Objective":"text"}}
        self.sheets = {}
        self.add_Sheet(sheetname=self.dico_sheetnames['general'],sheetdata=data)
        self.add_Sheet(sheetname=self.dico_sheetnames['by_req'],sheetdata=data)
        self.add_Sheet(sheetname=self.dico_sheetnames['do'],
                       sheetdata={"colnames":{"Objective ID":"","Chapter":"","Objectives":"","Description":""}},
                       import_dict=True)

        # Page General, By Requirement and DO-178 Objectives
        self.refreshAll()
        # Binding
        self.sheets[self.dico_sheetnames['general']].do_bindings(self.refreshAll)
        self.sheets[self.dico_sheetnames['by_req']].do_bindings(self.refreshAll)
        self.sheets[self.dico_sheetnames['do']].do_bindings(self.refreshAll)
        #self.table_project = self.currenttable
        self.notebook.setnaturalsize()
        ok_button = Button(self.overall_frame, text='OK', command=self.fenetre.destroy)
        ok_button.pack(side=LEFT, anchor=E)
        refresh_button = Button(self.overall_frame, text='Refresh', command=self.refreshAll)
        refresh_button.pack(side=LEFT, anchor=E)
        cancel_button = Button(self.overall_frame, text='Quit', command=self.fenetre.destroy)
        cancel_button.pack(anchor=E)

def test():
    pass
if __name__ == '__main__':

    #exit()
    # TODO:
    # - Create a separate table for comments
    # - Manage version of rules
    # - Manage link to DO-178 objectives
    #

    fenetre = Tk()
    icone = "ico_sys_desktop.ico"
    fenetre.iconbitmap(icone)
    fenetre.resizable(False, False)
    fenetre.title('Standards Management')
    queue_gui_thread = Queue.Queue()
    queue_thread_gui = Queue.Queue()

    std_win = ManageStdGui(fenetre,
                           database="db/sdts_rules.db3",
                           #version="1.8",
                           std_type="SDS",
                           queue=queue_gui_thread)

                           #queue_thread_gui=queue_thread_gui,
                           #queue_gui_thread=queue_gui_thread)
    thread_req = ThreadReq(master=fenetre,
                            queue=queue_gui_thread,
                            queue_thread_gui=queue_thread_gui)
    mainmenu = Menu(fenetre)
    menubar = Menu(mainmenu)
    menubar.add_command(label="Import SWRD", command=std_win.importSWRD)
    menubar.add_command(label="Import SWDD", command=None)
    menubar.add_separator()
    menubar.add_command(label="Import Inspection Sheet", command=None)
    menubar.add_separator()
    menubar.add_command(label="View HTML", command=std_win.online_documentation)
    mainmenu.add_cascade(label="File", menu=menubar)
    exportbar = Menu(mainmenu)
    exportbar.add_command(label="Export XML", command=std_win.export_xml)
    exportbar.add_command(label="Export to ReqIF format", command=std_win.export_xml)
    mainmenu.add_cascade(label="Tools", menu=exportbar)
    reportbar = Menu(mainmenu)
    reportbar.add_command(label="Export Inspection Sheet", command=std_win.genInspectSheetHLR)
    mainmenu.add_cascade(label="Reports", menu=reportbar)
    managebar = Menu(mainmenu)
    managebar.add_command(label="SWRD", command=std_win.displaySWRD)
    managebar.add_separator()
    managebar.add_command(label="SRTS", command=std_win.displaySRTS)
    managebar.add_command(label="SDTS", command=std_win.displaySDTS)
    managebar.add_command(label="SCS", command=std_win.displaySCS)
    mainmenu.add_cascade(label="Display", menu=managebar)
    fenetre.configure(menu=mainmenu)
    thread_req.start()
    fenetre.mainloop()