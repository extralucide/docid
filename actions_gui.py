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
try:
    from Tkinter import *
    import ttk
except ImportError:
    from tkinter import *
    import tkinter.ttk as ttk
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel
import re
from actions import Action
import platform
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
        self.platform = platform.system()
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
##            cellvalue = model.getCellRecord(row, col)
##            print cellvalue
##            label = model.getColumnLabel(col)
##            if label == "ID":
##                action_id = "{:d}".format(cellvalue)
##                self.callback(action_id)

class ActionGui (Frame,Action,Table_docid):
    def __init__(self,**kwargs):
        Action.__init__(self)

    def click_update_action_item(self,action_id=0):
            if action_id != 0:
                action_data = self.getActionItem(action_id)
                print "Action",action_data
                self.action_id = action_data[0]
                title = "Update action item {:s}".format(action_id)
                button_txt = "Update"
                cmd = self.update_action
            else:
                title = "Add action item"
                button_txt = "Add"
                cmd = self.submit_action
            self.input_action = Tk()
            self.input_action.iconbitmap("qams.ico")
            self.input_action.title(title)
            self.input_action.resizable(False,False)
            row_index = 1
            action_frame = Frame(self.input_action, width = 50)
            #action_frame.pack()
            action_frame.grid(row = row_index)
    ##        scrollbar = Scrollbar(help_frame)
            self.input_action.bind('<MouseWheel>', self.scrollEvent)
    ##        scrollbar.pack(side=RIGHT, fill=Y)
            action_context_label = Label(action_frame, text='Action context:',justify=LEFT)
            #action_context_label.pack()
            self.action_context = Entry(action_frame, width = 60)
            row_index += 1
            action_context_label.grid(row = row_index)
            self.action_context.grid(row = row_index, column =1,sticky='W')
            #self.action_context.pack(fill=X,expand=1)

            row_index +=1
            action_description_label = Label(action_frame, text='Action description:',justify=LEFT)
            #action_description_label.pack()
            self.action_description = Text(action_frame,wrap=WORD, width = 60, height = 5)
            #self.action_description.pack(fill=X,expand=1)
            action_description_label.grid(row = row_index)
            self.action_description.grid(row = row_index, column =1,sticky='E')
    ##        self.action_description.pack()

            row_index +=1
            action_assignee_label = Label(action_frame, text='Accountable person:',justify=LEFT,width=20)
            #action_assignee_label.pack(side=LEFT)
            assigneelistbox_frame = Frame(action_frame)
            #assigneelistbox_frame.pack()
            self.vbar_assignees = vbar_assignees = Scrollbar(assigneelistbox_frame , name="vbar_assignees")
            self.vbar_assignees.pack(side=RIGHT, fill=Y)
            self.assigneelistbox = Listbox(assigneelistbox_frame ,height=3,width=40,exportselection=0,yscrollcommand=vbar_assignees.set)
            self.assigneelistbox.pack()
            vbar_assignees["command"] = self.assigneelistbox.yview
            self.assigneelistbox.bind("<ButtonRelease-1>", self.select_assignee)
            self.assigneelistbox.bind("<Key-Up>", lambda event, arg=self.assigneelistbox: self.up_event(event, arg))
            self.assigneelistbox.bind("<Key-Down>", lambda event, arg=self.assigneelistbox: self.down_event(event, arg))
            list_assignees = self.getAssignees()
            for assignee in list_assignees:
                self.assigneelistbox.insert(END,"{:s}".format(self.removeNonAscii(assignee[0])))
            action_assignee_label.grid(row = row_index)
            assigneelistbox_frame.grid(row = row_index, column =1,sticky='W')

            row_index +=1

            action_status_label = Label(action_frame, text='Status:',justify=LEFT,width=20)
            #action_status_label.pack(side=LEFT)
            statuslistbox_frame = Frame(action_frame)
            #statuslistbox_frame.pack()
    ##        self.vbar_statuss = vbar_statuss = Scrollbar(statuslistbox_frame , name="vbar_statuss")
    ##        self.vbar_statuss.pack(side=RIGHT, fill=Y)
            self.statuslistbox = Listbox(statuslistbox_frame ,height=2,width=20,exportselection=0)
            self.statuslistbox.pack()
    ##        vbar_statuss["command"] = self.statuslistbox.yview
            self.statuslistbox.bind("<ButtonRelease-1>", self.select_status)
            self.statuslistbox.bind("<Key-Up>", lambda event, arg=self.statuslistbox: self.up_event(event, arg))
            self.statuslistbox.bind("<Key-Down>", lambda event, arg=self.statuslistbox: self.down_event(event, arg))
            list_statuss = self.getStatus()
            for status in list_statuss:
                self.statuslistbox.insert(END,"{:s}".format(status[0]))
            if action_id != 0:
                action_status_label.grid(row = row_index)
                statuslistbox_frame.grid(row = row_index, column =1,sticky='W')
    ##        action_target_date_label = Label(action_frame, text='Expected date for action resolution:',justify=LEFT)
    ##        action_target_date_label.pack()
    ##        self.action_target_date = Text(action_frame,wrap=WORD, width = 100, height = 1)
    ##        self.action_target_date.insert(END, "Enter here the expected date for action closing")
    ##        self.action_target_date.pack()
            row_index +=1
            submit_button = Button(self.input_action, text=button_txt, command = cmd)
            delete_button = Button(self.input_action, text='Delete', command = self.delete_action)
            cancel_button = Button(self.input_action, text='Cancel', command = self.input_action.destroy)

            if action_id != 0:
                submit_button.grid(row = row_index, padx=0,sticky='W')
                delete_button.grid(row = row_index, padx=50,sticky='W')
                cancel_button.grid(row = row_index, sticky='E')
                self.action_context.insert(END, action_data[2])
                self.action_description.insert(END, action_data[1])
                assignee_id = action_data[3]
                index = assignee_id-1
                self.assigneelistbox.selection_set(first=index)
                status_id = action_data[6]
                print"status_id",status_id
                index = status_id-1
                self.statuslistbox.selection_set(first=index)
            else:
                submit_button.grid(row = row_index, column =1,padx=50)
                cancel_button.grid(row = row_index, column =1,sticky='E')
                self.action_context.insert(END, "Enter here the action item context")
                self.action_description.insert(END, "Enter here the action item description")
                self.assigneelistbox.selection_set(first=0)
            self.input_action.mainloop()

    def select_assignee(self,event):
        pass

    def select_status(self,event):
        pass

    def actionitemlistbox_onselect(self,event):
        # Note here that Tkinter passes an event object to onselect()
        w = event.widget
        print "WIDGET:",w
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
##        self.log('You selected action item %s' % (action_id))
##        print 'You selected action item %s' % (action_id)
    def update_list_actions_old(self):
        self.actionitemslistbox.delete(0,END)
        list_action_items = self.getActionItem()
        print "list_action_items",list_action_items
        inter = 0
        for action_item in list_action_items:
            context = action_item[2]
            description = re.sub(r"\n",r" ",action_item[1])
            if action_item[3] != None:
                assignee = action_item[3]
            else:
                assignee = "Nobody"
            if action_item[4] != None:
                date_open = action_item[4]
            else:
                date_open = ""
            if action_item[5] != None:
                date_closure = action_item[5]
            else:
                date_closure = ""
            if action_item[6] != None:
                status = action_item[6]
            else:
                status = "Open"
            self.actionitemslistbox.insert(END,  "{:d}) ".format(action_item[0]) + " " + context + " " + description + " " + assignee + " " + date_open + " " + date_closure + " " + status)
            if inter % 2 == 0:
                self.actionitemslistbox.itemconfig(inter,{'bg':'darkgrey','fg':'white'})
            else:
                self.actionitemslistbox.itemconfig(inter,{'bg':'lightgrey','fg':'black'})
            inter += 1
    def update_list_actions(self):
##        self.actionitemslistbox.delete(0,END)
        list_action_items = self.getActionItem()
        print "list_action_items",list_action_items
        data = {}
        colnames=["ID","Context","Description","Assignee","Date open","Date closure","Status"]

        index = 1
        for action_item in list_action_items:
            data[index]={}
            data[index]["ID"] = action_item[0]
            context = action_item[2]
            data[index]["Context"] = context
            description = re.sub(r"\n",r" ",action_item[1])
            data[index]["Description"] = self.removeNonAscii(description)
            if action_item[3] != None:
                assignee = action_item[3]
            else:
                assignee = "Nobody"
            data[index]["Assignee"] = assignee
            if action_item[4] != None:
                date_open = action_item[4]
            else:
                date_open = ""
            data[index]["Date open"] = date_open
            if action_item[5] != None:
                date_closure = action_item[5]
            else:
                date_closure = ""
            data[index]["Date closure"] = date_closure
            if action_item[6] != None:
                status = action_item[6]
            else:
                status = "Open"
            data[index]["Status"] = status
##            self.actionitemslistbox.insert(END,  "{:d}) ".format(action_item[0]) + " " + context + " " + description + " " + assignee + " " + date_open + " " + date_closure + " " + status)
##            if inter % 2 == 0:
##                self.actionitemslistbox.itemconfig(inter,{'bg':'darkgrey','fg':'white'})
##            else:
##                self.actionitemslistbox.itemconfig(inter,{'bg':'lightgrey','fg':'black'})
            index += 1
        return data
    def click_list_action_item_old(self):
        list_action = Tk()
        list_action.iconbitmap("qams.ico")
        list_action.title("List action item")
        list_action.resizable(False,False)
        action_frame = Frame(list_action, width = 50)
        action_frame.pack()

        actionitemslistbox_frame = Frame(action_frame)
        actionitemslistbox_frame.pack()
        self.vbar_action_items = vbar_action_items = Scrollbar(actionitemslistbox_frame , name="vbar_action_items")
        self.vbar_action_items.pack(side=RIGHT, fill=Y)
        self.actionitemslistbox = Listbox(actionitemslistbox_frame ,height=20,width=120,exportselection=0,yscrollcommand=vbar_action_items.set)
        self.actionitemslistbox.bind("<Double-Button-1>", self.actionitemlistbox_onselect)
        self.actionitemslistbox.pack()

        vbar_action_items["command"] = self.actionitemslistbox.yview
        self.actionitemslistbox.bind("<ButtonRelease-1>", self.select_action_item)
        self.actionitemslistbox.bind("<Key-Up>", lambda event, arg=self.actionitemslistbox: self.up_event(event, arg))
        self.actionitemslistbox.bind("<Key-Down>", lambda event, arg=self.actionitemslistbox: self.down_event(event, arg))

        self.update_list_actions_old()
        cancel_button = Button(list_action, text='Cancel', command = list_action.destroy)
        cancel_button.pack(side=RIGHT)
        list_action.mainloop()

    def click_list_action_item(self):
        list_action = Tk()
        list_action.iconbitmap("qams.ico")
        list_action.title("List action item")
        list_action.resizable(False,False)
        action_frame = Frame(list_action, width = 768)
        action_frame.pack()
        model = TableModel()
        #import after model created

        data = self.update_list_actions()
        print data
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
        if 0==1:
            actionitemslistbox_frame = Frame(action_frame)
            actionitemslistbox_frame.pack()
            self.vbar_action_items = vbar_action_items = Scrollbar(actionitemslistbox_frame , name="vbar_action_items")
            self.vbar_action_items.pack(side=RIGHT, fill=Y)
            self.actionitemslistbox = Listbox(actionitemslistbox_frame ,height=20,width=120,exportselection=0,yscrollcommand=vbar_action_items.set)
            self.actionitemslistbox.bind("<Double-Button-1>", self.actionitemlistbox_onselect)
            self.actionitemslistbox.pack()

            vbar_action_items["command"] = self.actionitemslistbox.yview
            self.actionitemslistbox.bind("<ButtonRelease-1>", self.select_action_item)
            self.actionitemslistbox.bind("<Key-Up>", lambda event, arg=self.actionitemslistbox: self.up_event(event, arg))
            self.actionitemslistbox.bind("<Key-Down>", lambda event, arg=self.actionitemslistbox: self.down_event(event, arg))

        cancel_button = Button(list_action, text='Cancel', command = list_action.destroy)
        cancel_button.pack(side=RIGHT)
        list_action.mainloop()

    def select_action_item(self,event):
        pass

    def delete_action(self):
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

        assignee_id = self.assigneelistbox.curselection()
        if assignee_id != ():
            assignee_name = self.assigneelistbox.get(assignee_id)
            assignee_sqlite_id = self.getAssigneeId(assignee_name)
            action_item['assignee'] = assignee_sqlite_id
        else:
            action_item['assignee'] = 0

        status_id = self.statuslistbox.curselection()
        if status_id != ():
            status_name = self.statuslistbox.get(status_id)
            status_sqlite_id = self.getStatusId(status_name)
            action_item['status'] = status_sqlite_id
        else:
            action_item['status'] = 1 # Open
##        date_open =
##        from datetime import datetime, date, time
##        maintenant = datetime.now()
        # maintenant.strftime("%A, %d. %B %Y %I:%M%p")
        # 'Tuesday, 21. November 2006 04:30PM'
##        date_open = maintenant.strftime("%Y-%m-%d")
##        action_item['date_open']= date_open
##        action_item['date_closure']= ""
##        action_item['status']= 1 # Open
        print"ACTION Updated", action_item
        self.updateActionItem(action_item)
        self.update_list_actions()
        self.input_action.destroy()

    def submit_action(self):
        print"Submit action"
        action_item={}
        # description
        action_item['description']=self.action_description.get(1.0,END)
        action_item['context']=self.action_context.get()
        assignee_id = self.assigneelistbox.curselection()
        if assignee_id != ():
            assignee_name = self.assigneelistbox.get(assignee_id)
            assignee_sqlite_id = self.getAssigneeId(assignee_name)
            action_item['assignee'] = assignee_sqlite_id
        else:
            action_item['assignee'] = 0
##        date_open =
        from datetime import datetime, date, time
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

    def click_edit_action_item_test(self):
        root = Tk()
        Pmw.initialise(root)
        title = 'Pmw.ComboBox demonstration'
        root.title(title)

        exitButton = Button(root, text = 'Exit', command = root.destroy)
        exitButton.pack(side = 'bottom')
        widget = Demo(root)
        root.mainloop()

if __name__ == '__main__':
    action = ActionGui()
    action.click_list_action_item()
