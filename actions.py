#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
import sqlite3 as lite
from tool import Tool
import datetime
import sys
import tkMessageBox
from os.path import join

class Action(Tool):
    def __init__(self):
        self.actions_db_filename = ""
        self.actions_list_assignees = []
        Tool.__init__(self)
        self._loadSQLConfig()

        if 0==1:
            try:
                with open(self.actions_db_filename):
                    pass
            except IOError:
                print 'SQLite database does not exists.'
                if tkMessageBox.askokcancel("Create Action Items SQLite database", "Do you want to create new database ?"):
                    self.sqlite_create_actions_db()

    def getActionsDbLocation(self):
        database=self.actions_db_filename
        database = join("actions",database)
        return database

    def isFilenameDbExist(self):
        database = self.getActionsDbLocation()
        try:
            with open(database):
                pass
                exist = True
        except IOError:
            print 'isFilenameDbExist: SQLite database does not exists.'
            exist = False
        return exist

            #if tkMessageBox.askokcancel("Create Action Items SQLite database", "Do you want to create new database ?"):
            #    self.sqlite_create_actions_db()

    def setActionIemsDb(self,db_name):
        self.actions_db_filename = db_name

    def getAssigneeId(self,name):
        database = self.getActionsDbLocation()
        id = 0
        if name != "":
            query = "SELECT id FROM assignees WHERE assignees.name LIKE '{:s}'".format(self.replaceNonASCII(name))
            print "QUERY",query
            result = self.sqlite_query_one(query,database)
            if result in (None,[]):
                id = 0
            else:
                id = result[0]
        return id

    def getStatusId(self,name):
        database = self.getActionsDbLocation()
        id = 0
        if name != "":
            query = "SELECT id FROM status WHERE status.name LIKE '{:s}'".format(name)
            print "QUERY",query
            result = self.sqlite_query_one(query,database)
            if result in (None,[]):
                id = 0
            else:
                id = result[0]
        return id

    def _loadSQLConfig(self):
        if 0==1:
            self.gen_dir = "result"
            try:
                # get generation directory
                self.gen_dir = self.getOptions("Generation","dir")
                self.actions_db_filename = self.getOptions("SQL","actions_db")
                list_assignees_str = self.getOptions("SQL","list_assignees")
                self.actions_list_assignees = list_assignees_str.split(",")
                print "Action module config reading succeeded"
            except IOError as exception:
                print "Action module config reading failed:", exception
                self.gen_dir = "result"
                self.actions_db_filename = "default_checklist.db3"
                self.actions_list_assignees = ('David Bailleul',
                                               'Henri Bollon',
                                               'Antoine Bottolier',
                                               'Louis Farge',
                                               'Stephane Oisnard',
                                               'Thomas Bouhafs',
                                               'Gilles Lecoq')
        else:
            del self.actions_list_assignees[0:]
            list_writers = self.getUsersList()
            print "list_writers",list_writers
            for writer in list_writers:
                self.actions_list_assignees.append(writer[0])

    def deleteActionItem(self,action_id):
        database = self.getActionsDbLocation()
        try:
            # autocommit mode
            con = lite.connect(database, isolation_level=None)
            cur = con.cursor()
            cur.execute("DELETE FROM actions WHERE id LIKE '{:d}'".format(action_id))
        except lite.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if con:
                con.close()

    def getActionItem(self,
                      id="",
                      status=""):
        database = self.getActionsDbLocation()
        if id != "":
            query = "SELECT * FROM actions WHERE actions.id LIKE '" + id + "'"
            result = self.sqlite_query_one(query,database)
            if result in (None,[]):
                action = None
            else:
                action = result
        else:
            if status != "":
                query = "SELECT actions.id, \
                                actions.description, \
                                actions.context, \
                                assignees.name as assignee, \
                                actions.date_open, \
                                actions.date_closure,  \
                                status.name as status, \
                                actions.planned_for, \
                                actions.comment \
                                FROM actions \
                                LEFT OUTER JOIN assignees ON actions.assignee = assignees.id \
                                LEFT OUTER JOIN status ON actions.status = status.id  \
                                WHERE actions.status  LIKE '{:d}'".format(status)
            else:
                query = "SELECT actions.id, \
                                actions.description, \
                                actions.context, \
                                assignees.name as assignee, \
                                actions.date_open, \
                                actions.date_closure, \
                                status.name as status, \
                                actions.planned_for, \
                                actions.comment \
                                FROM actions \
                                LEFT OUTER JOIN assignees ON actions.assignee = assignees.id \
                                LEFT OUTER JOIN status ON actions.status = status.id "
            result = self.sqlite_query(query,database)
            if result in (None,[]):
                action = None
            else:
                action = result
        return action

    def getAssignees(self,id=""):
        database = self.getActionsDbLocation()
        if id != "":
            pass
        else:
            query = "SELECT assignees.name FROM assignees "
            result = self.sqlite_query(query,database)
            if result in (None,[]):
                list_assignees = None
            else:
                list_assignees = result
        return list_assignees

    def getStatus(self,id=""):
        database = self.getActionsDbLocation()
        if id != "":
            pass
        else:
            query = "SELECT status.name FROM status "
            result = self.sqlite_query(query,database)
            if result in (None,[]):
                list_status = None
            else:
                list_status = result
        return list_status

    def addActionItem(self,action_item):
        '''
        '''
        try:
            database = self.getActionsDbLocation()
            con = lite.connect(database, isolation_level=None)
            cur = con.cursor()
            cur.execute("INSERT INTO actions(description,context,assignee,date_open,date_closure,status,planned_for,comment) VALUES(?,?,?,?,?,?,?,?)",(action_item['description'],
                                                                                                                                                       action_item['context'],
                                                                                                                                                       action_item['assignee'],
                                                                                                                                                       action_item['date_open'],
                                                                                                                                                       action_item['date_closure'],
                                                                                                                                                       action_item['status'],
                                                                                                                                                       action_item['planned_for'],
                                                                                                                                                       action_item['comment']))
        except lite.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if con:
                con.close()

    def updateActionItem(self,action_item):
        '''
        '''
        try:
            database = self.getActionsDbLocation()
            if action_item['status'] == 2:# Closed
                maintenant = datetime.datetime.now()
                date_closure = maintenant.strftime("%Y-%m-%d")
            else:
                date_closure = ""
            con = lite.connect(database, isolation_level=None)
            cur = con.cursor()
            id = action_item['id']
            cur.execute("SELECT id FROM actions WHERE id LIKE '{:d}' LIMIT 1".format(id))
            data = cur.fetchone()
            if data is not None:
                id = data[0]
                print "Update row in SQLite database"
                cur.execute("UPDATE actions SET context=?,description=?,assignee=?,date_closure=?,status=?,planned_for=?,comment=? WHERE id= ?",(action_item['context'],
                                                                                                                         action_item['description'],
                                                                                                                         action_item['assignee'],
                                                                                                                         date_closure,
                                                                                                                         action_item['status'],
                                                                                                                         action_item['planned_for'],
                                                                                                                         action_item['comment'],
                                                                                                                         id))
            else:
                pass
        except lite.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if con:
                con.close()

    def sqlite_create_actions_db(self,
                                 actions_db_filename=""):
        """
        Example:
        INSERT INTO actions VALUES(1,'set to closed with QA manager','SyCR 237',1,'2014-03-11',NULL,1);
        INSERT INTO actions VALUES(2,'Add an evidence for BITE µC','SyCR 254',1,'2014-03-11',NULL,1);
        :return:
        """
        if actions_db_filename == "":
            database = self.getActionsDbLocation()
        else:
            database = actions_db_filename
        try:
            con = lite.connect(database)
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS actions")
            cur.execute("DROP TABLE IF EXISTS assignees")
            cur.execute("DROP TABLE IF EXISTS status")
            script = "BEGIN TRANSACTION;\
                                CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, context TEXT, assignee NUMERIC, date_open TEXT, date_closure TEXT, status INTEGER, planned_for TEXT, comment TEXT);\
                                CREATE TABLE IF NOT EXISTS assignees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT); \
                                CREATE TABLE IF NOT EXISTS status (id INTEGER PRIMARY KEY, name TEXT);\
                                INSERT INTO status VALUES(1,'Open');\
                                INSERT INTO status VALUES(2,'Closed');"
            print "self.actions_list_assignees",self.actions_list_assignees
            for user in self.actions_list_assignees:
                script += "INSERT INTO assignees (name) VALUES('{:s}');".format(self.replaceNonASCII(user))
            script += "COMMIT;"
            print "SCRIPT",script
            cur.executescript(script)
            con.commit()
            print 'New SQLite database created.'
        except lite.Error, e:
            con = False
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
if __name__ == "__main__":
    action = Action()
    id = action.getAssigneeId("Henri Bollon")
    print "Id",id