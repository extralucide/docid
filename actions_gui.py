#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Olivier.Appere
#
# Created:     10/06/2014
# Copyright:   (c) Olivier.Appere 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#from tool import Table_docid

try:
    from Tkinter import *
    import ttk
except ImportError:
    from tkinter import *
    import tkinter.ttk as ttk
from Tkinter import Canvas,Toplevel
from tkintertable.TableModels import TableModel
from tkintertable.Tables import TableCanvas
import re
from actions import Action
from tool import Tool
import tkMessageBox
import tkFileDialog
try:
    import Pmw
except ImportError:
    print "DoCID requires the Python MegaWidgets for Python. " \
          "See http://sourceforge.net/projects/pmw/"
from datetime import datetime

class Table_docid(TableCanvas):
    def __init__(self, parent=None, model=None, width=None, height=None,
                     rows=10, cols=5, **kwargs):
        Canvas.__init__(self, parent, bg='white',
                         width=width, height=height,
                         relief=GROOVE,
                         scrollregion=(0,0,300,200))
        self.parentframe = parent
        #get platform into a variable
        self.ostyp = self.checkOSType()
        #self.platform = platform.system()
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
        self.allrows = False       #for selected all rows without setting multiplerowlist
        self.multiplerowlist=[]
        self.multiplecollist=[]
        self.col_positions=[]       #record current column grid positions
        self.mode = 'normal'
        self.editable = True
        self.filtered = False

        self.loadPrefs()
        #set any options passed in kwargs to overwrite defaults and prefs
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        if model == None:
            self.model = TableModel(rows=rows,columns=cols)
        else:
            self.model = model

        self.rows = self.model.getRowCount()
        self.cols = self.model.getColumnCount()
        self.tablewidth = (self.cellwidth)*self.cols
        self.do_bindings()
        #initial sort order
        self.model.setSortOrder()

        #column specific actions, define for every column type in the model
        #when you add a column type you should edit this dict
        self.columnactions = {'text' : {"Edit":  'drawCellEntry' },
                              'number' : {"Edit": 'drawCellEntry' }}
        self.setFontSize()
        return

    def drawTooltip(self, row, col):
        pass

    def do_bindings(self):
        print "Call do_binding for action items table"
        """Bind keys and mouse clicks"""
        self.bind("<Button-1>",self.handle_left_click)
        self.bind("<Double-Button-1>",self.handle_double_click)

    def handle_double_click(self, event):
        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event)
        model=self.getModel()
        row_max = model.getRowCount()
        col_max = model.getColumnCount()
        if row != None and col != None and row < row_max and col < col_max:
            print "row",row_max,row
            print "col",col_max,col
            record = model.getRecordAtRow(row)
            print "RECORD:",record
            action_id = "{:d}".format(record['ID'])
            print "action_id",action_id
            self.callback(action_id)

class ActionGui (Frame,Action):
    def __init__(self,**kwargs):
        Action.__init__(self)
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
        if "system" in self.__dict__:
            self.system = self.__dict__["system"]
        else:
            self.system = ""
        if "callback" in self.__dict__:
            self.updatedBinGui = self.__dict__["callback"]
        else:
            self.updatedBinGui = False

    def click_update_action_item(self, action_id=0):
        db_exist = self.isFilenameDbExist()
        if db_exist:
            if "list_action" in self.__dict__:
                try:
                    self.list_action.destroy()
                except TclError, e:
                    print "Error %s:" % e.args[0]
            if action_id != 0:
                action_data = self.getActionItem(action_id)
                if action_data is not None:
                    print "Action",action_data
                    self.action_id = action_data[0]
                    title = "Update action item {:s}".format(action_id)
                    button_txt = "Update"
                    cmd = self.update_action
                else:
                    # abnormal
                    title = "Add action item"
                    button_txt = "Post"
                    cmd = self.submit_action
            else:
                title = "Add action item"
                button_txt = "Post"
                cmd = self.submit_action
            self.input_action = Toplevel()
            self.input_action.iconbitmap("ico_sys_desktop.ico")
            self.input_action.title(title)
            self.input_action.resizable(False,False)
            row_index = 1
            action_frame = Frame(self.input_action, width = 50)
            #action_frame.pack()
            action_frame.grid(row = row_index)
            # self.input_action.bind('<MouseWheel>', self.actionScrollEvent)
            action_context_label = Label(action_frame, text='Action context:',justify=LEFT)
            #action_context_label.pack()
            self.action_context = Entry(action_frame, width = 80)
            row_index += 1
            action_context_label.grid(row = row_index,sticky='E')
            self.action_context.grid(row = row_index, column =1,sticky='W')
            #self.action_context.pack(fill=X,expand=1)

            row_index +=1
            action_description_label = Label(action_frame, text='Action description:',justify=LEFT)
            self.action_description = Text(action_frame,wrap=WORD, width = 60, height = 5)
            action_description_label.grid(row = row_index,sticky='E')
            self.action_description.grid(row = row_index, column =1,sticky='E')

            row_index +=1
            action_assignee_label = Label(action_frame, text='Responsible person:',justify=LEFT)
            #action_assignee_label.pack(side=LEFT)
            assigneelistbox_frame = Frame(action_frame)
            if 0==1:
                #assigneelistbox_frame.pack()
                self.vbar_assignees = vbar_assignees = Scrollbar(assigneelistbox_frame , name="vbar_assignees")
                self.vbar_assignees.pack(side=RIGHT, fill=Y)
                self.assigneelistbox = Listbox(assigneelistbox_frame ,height=3,width=40,exportselection=0,yscrollcommand=vbar_assignees.set)
                self.assigneelistbox.pack()
                vbar_assignees["command"] = self.assigneelistbox.yview
                self.assigneelistbox.bind("<ButtonRelease-1>", self.select_assignee)
                self.assigneelistbox.bind("<Key-Up>", lambda event, arg=self.assigneelistbox: self.up_event(event, arg))
                self.assigneelistbox.bind("<Key-Down>", lambda event, arg=self.assigneelistbox: self.down_event(event, arg))
            print "ASSIGNEES SYSTEM:",self.system
            list_sqlite_assignees = self.get_writers_vs_systems(self.system)
            values = []
            if list_sqlite_assignees:
                for assignee in list_sqlite_assignees:
                    values.append(assignee[0])
                    #self.assigneelistbox.insert(END,"{:s}".format(Tool.replaceNonASCII(assignee[0])))
            else:
                list_assignees = self.getAssignees()
                if list_assignees is not None:
                    for assignee in list_assignees:
                        values.append(assignee[0])
                        #self.assigneelistbox.insert(END,"{:s}".format(Tool.replaceNonASCII(assignee[0])))
            print "ASSIGNEES:",values
            # Spinbox or Openmenu
            self.assigneelistbox = Spinbox(action_frame,values=values,width=40)
            #w.grid(row = row_index,sticky='E')
            #row_index +=1
            action_assignee_label.grid(row = row_index,sticky='E')
            #assigneelistbox_frame.grid(row = row_index,column =1,sticky='W')
            row_index +=1
            self.assigneelistbox.grid(row = row_index,column =1,sticky='W')
            self.assigneelistbox.bind("<ButtonRelease-1>", self.select_assignee)
            row_index +=1
            action_status_label = Label(action_frame, text='Status:',justify=LEFT)
            statuslistbox_frame = Frame(action_frame)
            self.statuslistbox = Listbox(statuslistbox_frame ,height=2,width=20,exportselection=0)
            self.statuslistbox.pack()
            self.statuslistbox.bind("<ButtonRelease-1>", self.select_status)
            self.statuslistbox.bind("<Key-Up>", lambda event, arg=self.statuslistbox: self.up_event(event, arg))
            self.statuslistbox.bind("<Key-Down>", lambda event, arg=self.statuslistbox: self.down_event(event, arg))
            list_status = self.getStatus()
            for status in list_status:
                self.statuslistbox.insert(END,"{:s}".format(status[0]))
            if action_id != 0:
                action_status_label.grid(row = row_index,sticky='E')
                statuslistbox_frame.grid(row = row_index,column =1,sticky='W')
            row_index +=1

            action_planned_for_label = Label(action_frame, text='Planned for:',justify=LEFT)
            self.action_planned_for = Entry(action_frame, width = 80)
            row_index += 1
            action_planned_for_label.grid(row = row_index,sticky='E')
            self.action_planned_for.grid(row = row_index, column =1,sticky='W')

            action_comment_label = Label(action_frame, text='Comment:',justify=LEFT)
            self.action_comment = Text(action_frame,wrap=WORD, width = 60, height = 5)
            row_index += 1
            action_comment_label.grid(row = row_index,sticky='E')
            self.action_comment.grid(row = row_index, column =1,sticky='E')

            submit_button = Button(self.input_action, text=button_txt, command = cmd)
            delete_button = Button(self.input_action, text='Delete', command = self.delete_action)
            cancel_button = Button(self.input_action, text='Cancel', command = self.input_action.destroy)

            if action_id != 0 and action_data is not None:
                delete_button.grid(row = row_index, padx=0,sticky='W')
                submit_button.grid(row = row_index, padx=50,sticky='E')
                cancel_button.grid(row = row_index, sticky='E')
                self.action_context.insert(END, action_data[2])
                self.action_description.insert(END, action_data[1])
                self.action_planned_for.insert(END, action_data[7])
                self.action_comment.insert(END, action_data[8])
                assignee_id = action_data[3]
                index = assignee_id-1
                #self.assigneelistbox.selection_set(first=index)
                self.assigneelistbox.icursor(index)
                status_id = action_data[6]
                print"status_id",status_id
                index = status_id-1
                self.statuslistbox.selection_set(first=index)
            else:
                submit_button.grid(row = row_index, column =1,padx=50)
                cancel_button.grid(row = row_index, column =1,sticky='E')
                self.action_context.insert(END, "Enter here the action item context")
                self.action_description.insert(END, "Enter here the action item description")
                self.action_planned_for.insert(END, "When does the action achievement is planned for")
                self.assigneelistbox.icursor(0)
                #self.assigneelistbox.selection_set(first=0)
            self.input_action.mainloop()
        else:
            print 'click_update_action_item: SQLite database does not exists.'
            if tkMessageBox.askokcancel("Create Action Items SQLite database", "SQLite database does not exists.\nDo you want to create new database ?"):
                #self.sqlite_create_actions_db()
                print "EDEBUG:UN"
                db_name = self.createActionItemsDb(get_user_filename=True)
                print "EDEBUG:DEUC"
                self.setActionIemsDb(db_name)
                if self.updatedBinGui:
                    self.updatedBinGui(db_name)

    def select_assignee(self,event):
        pass

    def select_status(self,event):
        pass

    def actionitemlistbox_onselect(self,event):
        # Note here that Tkinter passes an event object to onselect()
        w = event.widget
        #print "WIDGET:",w
        index = self.actionitemslistbox.curselection()[0]
        if index != ():
            action = self.actionitemslistbox.get(index)
            print action
            m = re.match(r'^([0-9]{1,4})\) (.*)',action)
            # Attention au CR/LF !! marche pas faut les enlever
            if m:
                action_id = m.group(1)
                self.click_update_action_item(action_id)
            else:
                action_id = "None"

    def update_list_actions(self):
        list_action_items = self.getActionItem()
        data = {}
        if list_action_items is not None:
            #colnames=["ID","Context","Description","Assignee","Date open","Date closure","Status"]
            index = 1
            for action_item in list_action_items:
                data[index]={}
                data[index]["ID"] = action_item[0]
                context = action_item[2]
                data[index]["Context"] = context
                description = re.sub(r"\n",r" ",action_item[1])
                data[index]["Description"] = self.removeNonAscii(description)
                if action_item[3] is not None:
                    assignee = action_item[3]
                else:
                    assignee = "Nobody"
                data[index]["Assignee"] = assignee
                if action_item[4] is not None:
                    date_open = action_item[4]
                else:
                    date_open = ""
                data[index]["Date open"] = date_open
                if action_item[5] is not None:
                    date_closure = action_item[5]
                else:
                    date_closure = ""
                data[index]["Date closure"] = date_closure
                if action_item[6] is not None:
                    status = action_item[6]
                else:
                    status = "Open"
                data[index]["Status"] = status
                index += 1
        else:
            pass
            #data[1] = {"ID":0,"Context":"","Description":"","Assignee":"","Date open":"","Date closure":"","Status":""}

        return data

    def click_list_action_item(self):
        db_exist = self.isFilenameDbExist()
        if db_exist:
            data = self.update_list_actions()
            print "Create list action items window"
            self.list_action = Toplevel()
            self.list_action.iconbitmap("ico_sys_desktop.ico")
            self.list_action.title("List action item")
            self.list_action.resizable(False,False)
            action_frame = Frame(self.list_action,
                                 width = 768,
                                 height = 512)
            action_frame.pack()

            if data not in ({},None):
            #    #import after model created
            #    model.importDict(data)
            #else:
            #    tkMessageBox.showinfo("Warning","No action items so far.")
            #    print "No action items so far."
                model = TableModel()
                model.importDict(data)
                table = Table_docid(action_frame,
                                    model,
                                    width=960,
                                    height=480,
                                    cellwidth=60,
                                    cellbackgr='#e3f698',
                                    thefont=('Arial',12),
                                    rowheight=18,
                                    rowheaderwidth=0,
                                    rowselectedcolor='yellow',
                                    editable=False,
                                    callback=self.click_update_action_item)

                table.createTableFrame()
            export_button = Button(self.list_action, text='Export', command = self.export_action,state="disabled")
            export_button.pack(side=RIGHT)
            balloon_export_button = Pmw.Balloon(self.list_action)
            balloon_export_button.bind(export_button, "No yet implemented")
            cancel_button = Button(self.list_action, text='Close', command = self.list_action.destroy)
            cancel_button.pack(side=RIGHT)
            add_action_button = Button(self.list_action, text='Add', command = self.click_update_action_item)
            add_action_button.pack(side=RIGHT)
            self.list_action.mainloop()
        else:
            print 'click_list_action_item: SQLite database does not exists.'
            if tkMessageBox.askokcancel("Create Action Items SQLite database",
                                        "SQLite database does not exists.\nDo you want to create new database ?"):
                #self.sqlite_create_actions_db()
                print "DEBUG:UN"
                db_name = self.createActionItemsDb(get_user_filename=True)
                print "DEBUG:DEUC"
                self.setActionIemsDb(db_name)
                if self.updatedBinGui:
                    self.updatedBinGui(db_name)

    def export_action(self,event):
        pass
    def select_action_item(self,event):
        pass

    def delete_action(self):
        if tkMessageBox.askokcancel("Delete Action item", "Do you want to delete action item {:d} ?".format(self.action_id)):
            self.deleteActionItem(self.action_id)
            self.update_list_actions()
            self.input_action.destroy()

    def update_action(self):
        print"Update action"
        action_item={}
        # description
        action_item['id'] = self.action_id
        action_item['description']=self.action_description.get(1.0,END)
        action_item['context']=self.action_context.get()
        action_item['planned_for']=self.action_planned_for.get()
        action_item['comment']=self.action_comment.get(1.0,END)
        #assignee_id = self.assigneelistbox.curselection()
        #if assignee_id != ():
        self.replaceNonASCII(self.assigneelistbox.get())
        assignee_sqlite_id = self.getAssigneeId(assignee_name)
        if assignee_sqlite_id == 0:
            tkMessageBox.showinfo("Error","{:s} not found in SQLite database.\n Action not updated.".format(assignee_name))
        else:
            action_item['assignee'] = assignee_sqlite_id
            status_id = self.statuslistbox.curselection()
            if status_id != ():
                status_name = self.statuslistbox.get(status_id)
                status_sqlite_id = self.getStatusId(status_name)
                action_item['status'] = status_sqlite_id
            else:
                action_item['status'] = 1 # Open
            self.updateActionItem(action_item)
            self.update_list_actions()
        self.input_action.destroy()

    def submit_action(self):
        print"Submit action"
        action_item={}
        # description
        action_item['description']=self.action_description.get(1.0,END)
        action_item['context']=self.action_context.get()
        action_item['planned_for']=self.action_planned_for.get()
        action_item['comment']=self.action_comment.get(1.0,END)
        #assignee_id = self.assigneelistbox.get() #curselection()
        #if assignee_id != ():
        assignee_name = self.replaceNonASCII(self.assigneelistbox.get())
        print "assignee_name",assignee_name
        assignee_sqlite_id = self.getAssigneeId(assignee_name)
        if assignee_sqlite_id == 0:
            tkMessageBox.showinfo("Error","{:s} not found in SQLite database\n Action not updated.".format(assignee_name))
        else:
            action_item['assignee'] = assignee_sqlite_id
            maintenant = datetime.now()
            # maintenant.strftime("%A, %d. %B %Y %I:%M%p")
            # 'Tuesday, 21. November 2006 04:30PM'
            date_open = maintenant.strftime("%Y-%m-%d")
            action_item['date_open']= date_open
            action_item['date_closure']= ""
            action_item['status']= 1 # Open
            print"ACTION SUBMITTED", action_item
            self.addActionItem(action_item)
        self.input_action.destroy()

    def createActionItemsDb(self,get_user_filename=False):
        # Verify if the database SQLite exists
        if not get_user_filename:
            print "not get_user_filename"
            db_name = self.actions_db_filename
            try:
                with open(db_name):
                    pass
            except IOError:
                print 'createActionItemsDb: SQLite database does not exists.'
                if tkMessageBox.askokcancel("Create Action Items SQLite database", "Do you want to create new database ?"):
                    self.sqlite_create_actions_db()
        else:
            print "get_user_filename"
            db_name = tkFileDialog.asksaveasfilename(defaultextension = '.db3',
                                                filetypes=[('SQLite v3 database','.db3'),('SQLite database','.db')],
                                                title="Create Action Items database.")

            print "DBNAME",db_name
            if db_name:
                self.sqlite_create_actions_db(db_name)
                self.setActionIemsDb(db_name)
                if self.updatedBinGui:
                    self.updatedBinGui(db_name)
        return db_name

if __name__ == '__main__':
    action = ActionGui()
    action.click_list_action_item()
