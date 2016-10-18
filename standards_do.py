__author__ = 'Olivier.Appere'
#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
import platform
import re
from tool import Tool
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
    print ("DoCID requires the Python MegaWidgets for Python. " \
    "See http://sourceforge.net/projects/pmw/")
import tkMessageBox
import tkSimpleDialog
import Queue
from tkintertable.Custom import MyTable
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel

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
        return

class smallWindows(Frame,
                   Toplevel,
                   Text):
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

    def write(self, txt):
        self.help_text.delete(0.0, END)
        self.help_text.insert(END, txt)

    def exit(self):
        self.destroy()

    @staticmethod
    def start(window):
        window.mainloop()

    def create(self,
               icon="ico_sys_desktop.ico",
               title="",
               bg="#80c0c0",
               width=120,
               height=16,
               labels=("", ""),
               callback=None,
               master=None):
        help_window = Toplevel(master=master)
        self.setWindowPos(help_window)

        help_window.iconbitmap(icon)
        help_window.title(title)
        help_window.resizable(False, False)
        help_window.grab_set()
        help_window.focus_set()
        help_frame_label = Label(help_window,
                                 text=labels[0])
        help_frame_label.pack(anchor=W)

        help_frame = Frame(help_window, bg=bg)
        help_frame.pack()
        scrolltxt_first_area = scrollTxtArea(help_frame,
                                             wrap=WORD,
                                             width=width,
                                             height=height)
        self.help_text = scrolltxt_first_area.text
        if 0==1:
            second_frame_label = Label(help_window,
                                       text=labels[1])
            second_frame_label.pack(anchor=W)

            second_frame = Frame(help_window, bg=bg)
            second_frame.pack(anchor=W)
            #if 0==1:
            scrolltxt_second_area = scrollTxtArea(second_frame,
                                                  wrap=WORD,
                                                  width=width,
                                                  height=height)
            self.second_text = scrolltxt_second_area.text
            #scrolltxt_second_area.text['yscrollcommand'] = scrolltxt_second_area.scroll.set
        ok_button = Button(help_window, text='Update', command=callback)
        ok_button.pack(side=LEFT, anchor=E)
        cancel_button = Button(help_window, text='Quit', command=help_window.destroy)
        cancel_button.pack(anchor=E)
        return help_window

class Std(TableCanvas):
    """
    To manage projets set
    """


    def __init__(self,
                 parent=None,
                 model=None,
                 width=None,
                 height=None,
                 rows=10,
                 cols=5,
                 editable=False,
                 database=None,
                 **kwargs):
        TableCanvas.__init__(self, parent,
                        bg='white',
                        width=width,
                        height=height,
                        relief=GROOVE,
                        scrollregion=(0, 0, 150, 100))
        if database is not None:
            self.database = database
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
        self.tablewidth = (self.cellwidth) * self.cols
        #self.do_bindings()
        #initial sort order
        self.model.setSortOrder()

        #column specific actions, define for every column type in the model
        #when you add a column type you should edit this dict
        self.columnactions = {'text': {"Edit": 'drawCellEntry'},
                              'number': {"Edit": 'drawCellEntry'}}
        self.setFontSize()

    def std_double_click(self, event):  #Click event callback function.
        def callback():
            update_text=self.small_windows.help_text.get(1.0, END)
            Tool.updateRule(rule_id,update_text,self.database)
            print "updateRule",update_text

        #Probably needs better exception handling, but w/e.
        #try:
        rclicked = self.get_row_clicked(event)
        cclicked = self.get_col_clicked(event)
        clicks = (rclicked, cclicked)
        print 'clicks:', clicks
        #except:
        #    print 'Error'
        if clicks:
            #Now we try to get the value of the row+col that was clicked.
            try:
                if clicks[1] == 0:
                    rule = self.model.getValueAt(clicks[0], clicks[1])
                    m = re.match(r'.*_([0-9]{1,3})',rule)
                    if m:
                        rule_id = m.group(1)
                        txt = Tool.getSDTS_Rule(rule_id,self.database)
                        self.small_windows = smallWindows()
                        self.small_windows.create(title=rule,
                                                  callback=callback)
                        self.small_windows.write(txt)
            except:
                print 'No record at:', clicks

            #This is how you can get the entire contents of a row.
            try: print 'entire record:', self.model.getRecordAtRow(clicks[0])
            except: print 'No record at:', clicks

    def do_bindings(self):
        print "Std custom do_bindings"
        self.bind("<Button-1>",self.handle_left_click)
        self.bind("<Double-Button-1>",self.std_double_click)
        if self.ostyp=='mac':
            #For mac we bind Shift, left-click to right click
            self.bind("<Button-2>", self.handle_right_click)
            self.bind('<Shift-Button-1>',self.handle_right_click)
        else:
            self.bind("<Button-3>", self.handle_right_click)

    def setList(self,
                by_req=True,
                page=None):

        result = Tool.getAll_SDTS_Rule_by_req(by_req=by_req,
                                              version=self.version,
                                              database=self.database)
        if result:
            if by_req:
                rule_type = "REQ_"
            else:
                rule_type = ""
            sorted_result = sorted(result,key=lambda x: x[0])#,reverse=True)
            self._refreshTableProject(page,
                                      sorted_result,
                                      std_type=self.sds_type,
                                      rule_type=rule_type)

    def _refreshTableProject(self,
                             page,
                             project_list,
                             std_type="",
                             rule_type=""):
        index = 1
        data = {}
        for id,status,version,description,auto,comments in project_list:
            data[index] = {}
            data[index]["1) Rule ID"] = "{:s}_{:s}{:s}".format(std_type,rule_type,id)
            data[index]["2) Version"] = version
            data[index]["3) Status"] = status
            index += 1
        index_max = page.model.getRowCount()
        print "index_max", index_max
        while index <= index_max:
            data[index] = {}
            data[index]["1) Rule ID"] = ""
            data[index]["2) Version"] = ""
            data[index]["3) Status"] = ""
            index += 1
        model = TableModel()
        model.importDict(data)
        print "DATA _refreshTableProject", data
        page.model.importDict(data)
        # self.table_project.setModel(model)
        page.updateModel(model)
        page.redrawTable()

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
                   Text,
                   Std):
    def online_documentation(self,event=None):
        """Open the online documentation"""
        import webbrowser
        link='file:///C:/Users/olivier.appere/DesignEditor/srts_rules.html#'
        webbrowser.open(link,autoraise=1)

    def export_xml(self):
        import xml.etree.ElementTree as ET
        type = "SDTS"
        if type == "SRTS":
            database = "db/srts_rules.db3"
            xml_filename = "result\\srts_rules_list.xml"
        elif type == "SDTS":
            database = "db/sdts_rules.db3"
            xml_filename = "result\\sdts_rules_list.xml"
        else:
            database = "db/scs_rules.db3"
            xml_filename = "result\\scs_rules_list.xml"
        root = ET.Element("STD")
        result = Tool.getAll_SDTS_Rule_by_req(by_req=True,database=database)
        # TODO: add link to DO-178
        for id,status,version,description,auto,comments in sorted(result):
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
            if auto == 2:
                auto_attrib = "PARTIALLY"
            if auto == 3:
                auto_attrib = "MAYBE"
            else:
                auto_attrib = "NO"
            print "AUTO:",auto
            rule_node = ET.SubElement(root, "RULE",attrib={"id":id,
                                                            "status":status,
                                                            "version":version,
                                                            "auto":auto_attrib,
                                                            "by_req":"TRUE"})
            desc_node = ET.SubElement(rule_node, "DESC")
            from markdown2 import Markdown
            markdowner = Markdown()
            rule_in_html = markdowner.convert(description)
            desc_node.text = rule_in_html
            print "HTML:",rule_in_html
            #desc_node.text = Tool.replaceNonASCII(description,html=True)
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

    def add_Sheet(self,
                  sheetname=None,
                  sheetdata=None):
        """Add a new sheet - handles all the table creation stuff"""
        def checksheet_name(name):
            if name == '':
                tkMessageBox.showwarning("Whoops", "Name should not be blank.")
                return 0
            if self.sheets.has_key(name):
                tkMessageBox.showwarning("Name exists", "Sheet name already exists!")
                return 0
        noshts = len(self.notebook.pagenames())
        if sheetname == None:
            sheetname = tkSimpleDialog.askstring("New sheet name?", "Enter sheet name:",
                                                initialvalue='sheet'+str(noshts+1))
        checksheet_name(sheetname)
        page = self.notebook.add(sheetname)
        #Create the table and model if data present
        if sheetdata != None:
            model = TableModel()
            model.importDict(sheetdata)
            self.currenttable = Std(page,
                                    model=model,
                                    reverseorder=1,
                                    database=self.database)
        else:
            self.currenttable = Std(page,database=self.database)

        #Load preferences into table
        self.currenttable.loadPrefs()
        #This handles all the canvas and header in the frame passed to constructor
        self.currenttable.createTableFrame()
        #add the table to the sheet dict
        self.sheets[sheetname] = self.currenttable
        self.saved = 0
        return sheetname

    def __init__(self,
                 fenetre,
                 database,
                 version,
                 std_type):
        self.sheets = {}
        self.database=database
        self.version=version
        self.sds_type=std_type
        Frame.__init__(self,fenetre)
        self.small_windows = smallWindows(master=fenetre)
        page = fenetre #self.small_windows.create(title="EOC information")
        self.overall_frame = LabelFrame(page, bd=0, text='')
        self.overall_frame.pack(anchor=W)
        self.notebook = Pmw.NoteBook(self.overall_frame, raisecommand=self.setcurrenttable)
        self.notebook.pack(fill='both', expand=1, padx=4, pady=4)
        matrix_frame = Frame(self.overall_frame, padx=10)
        matrix_frame.pack(side=LEFT)
        data = {"colnames": {"1) Rule ID": "", "2) Version": "", "3) Status": ""}}
        model = TableModel()
        #import after model created
        model.importDict(data)
        #return
        if 0==1:
            self.table_project = Std(matrix_frame,
                                         model=model,
                                         cellwidth=150,
                                         width=450,
                                         #height=120,
                                         cellbackgr='#E3F6CE',
                                         thefont=('Arial', 8),
                                         rowheight=16,
                                         editable=False,
                                         rowheaderwidth=0,
                                         rowselectedcolor='white',
                                         reverseorder=1)

        self.add_Sheet(sheetname='General',sheetdata=data)
        self.setList(by_req=False,
                     page=self.sheets['General'])
        self.add_Sheet(sheetname='By Req',sheetdata=data)
        self.setList(by_req=True,
                     page=self.sheets['By Req'])
        self.sheets['General'].do_bindings()
        self.sheets['By Req'].do_bindings()
        #self.table_project = self.currenttable
        self.notebook.setnaturalsize()

        #self.table_project.createTableFrame()
        #self.table_project.bind("<Double-Button-1>",self.std_double_click)
def test():
    pass
if __name__ == '__main__':
    # TODO:
    # - Create a separate table for comments
    # - Manage version of rules
    # - Manage link to DO-178 objectives
    #
    queue = Queue.Queue()
    fenetre = Tk()
    icone = "ico_sys_desktop.ico"
    fenetre.iconbitmap(icone)
    fenetre.resizable(False, False)
    fenetre.title('Standards Management')

    std_win = ManageStdGui(fenetre,
                           database="db/sdts_rules.db3",
                           version="1.8",
                           std_type="SDS")
    mainmenu = Menu(fenetre)
    menubar = Menu(mainmenu)
    menubar.add_command(label="Export XML", command=std_win.export_xml)
    menubar.add_separator()
    menubar.add_command(label="View HTML", command=std_win.online_documentation)
    mainmenu.add_cascade(label="File", menu=menubar)
    fenetre.configure(menu=mainmenu)
    # Populate table with Standards from SQLite database
    ok_button = Button(fenetre, text='OK', command=fenetre.destroy)
    ok_button.pack(side=LEFT, anchor=E)
    cancel_button = Button(fenetre, text='Quit', command=fenetre.destroy)
    cancel_button.pack(anchor=E)
    fenetre.mainloop()