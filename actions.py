#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
import sqlite3 as lite
from tool import Tool
import datetime
import sys

class Action(Tool):
    def __init__(self):
        Tool.__init__(self)
        self._loadSQLConfig()
        # Verify if the database SQLite exists
        try:
            with open(self.actions_db_filename):
                pass
        except IOError:
            print 'SQLite database does not exists.'
            self.sqlite_create_actions_db()

    def getAssigneeId(self,name):
        database=self.actions_db_filename
        id = 0
        if name != "":
            query = "SELECT id FROM assignees WHERE assignees.name LIKE '{:s}'".format(name)
            print "QUERY",query
            result = self.sqlite_query_one(query,database)
            if result in (None,[]):
                id = 0
            else:
                id = result[0]
        return id
    def getStatusId(self,name):
        database=self.actions_db_filename
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
        self.gen_dir = "result"
        try:
            # get generation directory
            self.gen_dir = self.getOptions("Generation","dir")
            self.actions_db_filename = self.getOptions("SQL","actions_db")
        except IOError as exception:
            print "Config reading failed:", exception

    def deleteActionItem(self,action_id):
        database=self.actions_db_filename
        try:
            con = lite.connect(database, isolation_level=None)
            cur = con.cursor()
            cur.execute("DELETE FROM actions WHERE id LIKE '{:d}'".format(action_id))
        except lite.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if con:
                con.close()

    def getActionItem(self,id="",status=""):
        database=self.actions_db_filename
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
                                actions.date_closure, \
                                status.name as status FROM actions \
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
                                status.name as status FROM actions \
                                LEFT OUTER JOIN assignees ON actions.assignee = assignees.id \
                                LEFT OUTER JOIN status ON actions.status = status.id "
            result = self.sqlite_query(query,database)
            if result in (None,[]):
                action = None
            else:
                action = result
        return action

    def getAssignees(self,id=""):
        database=self.actions_db_filename
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
        database=self.actions_db_filename
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
            database=self.actions_db_filename
            con = lite.connect(database, isolation_level=None)
            cur = con.cursor()
            cur.execute("INSERT INTO actions(description,context,assignee,date_open,date_closure,status) VALUES(?,?,?,?,?,?)",(action_item['description'],action_item['context'],action_item['assignee'],action_item['date_open'],action_item['date_closure'],action_item['status']))
        except lite.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if con:
                con.close()

    def updateActionItem(self,action_item):
        '''
        '''
        try:
            database=self.actions_db_filename
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
            if data != None:
                id = data[0]
                print "Update row in SQLite database"
                cur.execute("UPDATE actions SET context=?,description=?,assignee=?,date_closure=?,status=? WHERE id= ?",(action_item['context'],action_item['description'],action_item['assignee'],date_closure,action_item['status'],id))
            else:
                pass
        except lite.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if con:
                con.close()

    def sqlite_create_actions_db(self):
        try:
            con = lite.connect(self.actions_db_filename)
            cur = con.cursor()
            cur.executescript("""
                                BEGIN TRANSACTION;
                                CREATE TABLE actions (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, context TEXT, assignee NUMERIC, date_open TEXT, date_closure TEXT, status INTEGER);
                                INSERT INTO actions VALUES(1,'set to closed with QA manager','SyCR 237',1,'2014-03-11',NULL,1);
                                INSERT INTO actions VALUES(2,'Add an evidence for BITE µC','SyCR 254',1,'2014-03-11',NULL,1);
                                CREATE TABLE assignees (id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO assignees VALUES(1,'David Bailleul');
                                INSERT INTO assignees VALUES(2,'Henri Bollon');
                                INSERT INTO assignees VALUES(3,'Antoine Bottolier');
                                INSERT INTO assignees VALUES(4,'Louis Farge');
                                INSERT INTO assignees VALUES(5,'Stephane Oisnard');
                                INSERT INTO assignees VALUES(6,'Thomas Bouhafs');
                                INSERT INTO assignees VALUES(7,'Gilles Lecoq');
                                CREATE TABLE status (id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO status VALUES(1,'Open');
                                INSERT INTO status VALUES(2,'Closed');
                                COMMIT;
                """)
            con.commit()
            print 'New SQLite database created.'
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if con:
                con.close()
if __name__ == "__main__":
    action = Action()
    id = action.getAssigneeId("Henri Bollon")
    print "Id",id