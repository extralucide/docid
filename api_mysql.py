#!/usr/bin/env python 2.7.3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Olivier.Appere
#
# Created:     17/06/2014
# Copyright:   (c) Olivier.Appere 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import subprocess
import time
from ConfigParser import ConfigParser
from tool import Tool
import sys
import os
import re
import copy
# TODO enlever ConfigParser et utiliser Tool
# MySQL
from HTMLParser import HTMLParser
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.foundCell = False
        self.foundRow = False
        self.row_number = 0
        self.text = ""
        self.dico = {}
    def _createBeacon(self,tag,attrs):
        text = "<" + tag
        for key,value in attrs:
            if key != None and value != None:
                attr_inline = ' ' + key + ' =  "'+value+'" '
                text += attr_inline
        text += ">"
        return (text)
    def _createEndBeacon(self,tag):
        text = "</{:s}>".format(tag)
        return (text)
    def handle_starttag(self, tag, attrs):
##        print "Encountered a start tag:", tag
        if tag == "row":
            self.foundRow = True
            self.row_number += 1
        if tag == "field":
            self.foundCell = True
            for attr in attrs:
                self.attr = attr[1]
        elif self.foundCell:
            try:
                self.text += self._createBeacon(tag,attrs)
            except UnicodeDecodeError,exception:
                pass
            #self.text += "<" + tag + ">"
    def handle_endtag(self, tag):
##            print "Encountered an end tag :", tag
        if tag == "row":
            self.foundRow = False
        elif tag == "field":
            self.foundCell = False
##            self.tbl.append(self.text)
            if self.attr != None:
                self.dico[self.row_number,self.attr] = self.text
            self.text= ""
        else:
            self.text += self._createEndBeacon(tag)

    def handle_data(self, data):
##            print "Encountered some data  :", data
        if self.foundCell:
            self.text += data
class MySQL():
    def __init__(self):
        '''
            get in file .ini information to access MySQL server
            '''
       # tool = Tool()
        self.count = 0
       # self.config_parser = ConfigParser()
       # self.config_parser.read('docid.ini')
       # self.gen_dir = self.getOptions("Generation","dir")
        self._loadConfigMySQL()

    #def getOptions(self,key,tag):
    #    if self.config_parser.has_option(key,tag):
    #        value = self.config_parser.get(key,tag)
    #    else:
    #        value = ""
    #    return value

    def _loadConfigMySQL(self):
        tool = Tool()
        #self.gen_dir = "result"
        try:
            # get generation directory
            #self.gen_dir = self.getOptions("Generation","dir")
            conf_synergy_dir = tool.getOptions("Apache","mysql_dir")
            self.mysql_exe = os.path.join(conf_synergy_dir, 'mysql.exe')
        except IOError as exception:
            print "Config reading failed:", exception
        try:
            print self.mysql_exe
            with open(self.mysql_exe): pass
        except IOError:
            print "mysql_exe not found."
            self.mysql_exe = False

    def mysql_query(self,query,cmd_name):
        '''
        Invoke mysql command
        '''
        stdout = ""
        stderr = ""
        if self.mysql_exe:
            # hide commmand DOS windows
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            except AttributeError:
                print "mysql_query works on Windows only so far."
                return "",""
            try:
    ##            print self.mysql_exe + " " + query
                proc = subprocess.Popen(self.mysql_exe + " " + query, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
                stdout, stderr = proc.communicate()
                if stderr:
                    print "Error while executing " + cmd_name + " command: " + stderr
                time.sleep(1)
                return_code = proc.wait()
            except UnicodeEncodeError as exception:
                print "Character not supported:", exception
        return stdout,stderr

    def getReviewDate(self,review_id):
        stdout = ""
        stderr = ""
        if review_id != "":
            sql_query = "SELECT reviews.date \
    					 FROM reviews \
    					 WHERE reviews.id = {:s}".format(review_id)

            sql_opt = "-X -udocid finister -e \" {:s}\" ".format(sql_query)
            stdout,stderr = self.mysql_query(sql_opt,"MySQL getReviewDate")
            parser = MyHTMLParser()
            stdout = MySQL.convertBeacon(stdout)
            parser.feed(stdout)
            for key,value in parser.dico.items():
                print key,value
                if key[1] == "date":
                    date = value
        return date

    def getPreviousReviewsRecords(self,
                                  review_id,
                                  target_release_requested=""):
        """

        :param review_id:
        :return: list of reviews ID, list of references of SQAR
        """
        def invert_dict(d):
            return dict([(v, k) for k, v in d.iteritems()])

        recur = True
        stdout = ""
        stderr = ""
        tbl_reviews = []
        tbl_ref = []
        final_tbl_reviews = []
        if review_id != "":
            sql_query = "SELECT review_join_review.link_review_id, \
    							review_type.description as type, \
    							review_type.type as type, \
    							scope.abrvt as scope,  \
                                reviews.target_release, \
                                bug_applications.application \
    							FROM review_join_review \
    							LEFT OUTER JOIN reviews ON reviews.id = review_join_review.link_review_id \
                                LEFT OUTER JOIN data_join_review ON reviews.id = data_join_review.review_id \
                                LEFT OUTER JOIN bug_applications ON bug_applications.id = data_id \
    							LEFT OUTER JOIN review_type ON reviews.type = review_type.id \
    							LEFT OUTER JOIN scope ON review_type.scope_id = scope.id \
    							WHERE review_join_review.review_id = {:s}".format(review_id)
            sql_opt = "-X -udocid finister -e \" {:s}\" ".format(sql_query)
            stdout,stderr = self.mysql_query(sql_opt,"MySQL getPreviousReviews")
            parser = MyHTMLParser()
            print "SQAR:",stdout
            stdout = MySQL.convertBeacon(stdout)

            parser.feed(stdout)
            print "DICO_SQAR:",parser.dico
            #for key,value in parser.dico.items():
            #    print key,value
            #    if key[1] == "link_review_id":
            #        tbl_reviews.append(value)
            #    # if key[1] == "type":
            #    if key[1] == "application":
            #        tbl_ref.append(value)
            #    if key[1] == "target_release":
            #        target_release = value

            tbl_dico_ref = {}
            tbl_dico_type = {}
            tbl_dico_target = {}
            tbl_dico_link_review_id = {}
            stack = []
            for (key1,key2),value in parser.dico.items():
                stack.append(key1)
                if key2 == "link_review_id":
                    tbl_reviews.append(value)
                    tbl_dico_link_review_id[value] = key1
                if key2 == "application":
                    #stack.append(value)
                    tbl_ref.append(value)
                    tbl_dico_ref[value] = key1
                if key2 == "type":
                    #stack.append(value)
                    tbl_dico_type[value] = key1
                if key2 == "target_release":
                    #stack.append(value)
                    tbl_dico_target[value] = key1
           # print stack
            stack = set(stack)
            tbl_dico_ref = invert_dict(tbl_dico_ref)
            tbl_dico_type = invert_dict(tbl_dico_type)
            tbl_dico_target = invert_dict(tbl_dico_target)
            tbl_dico_link_review_id = invert_dict(tbl_dico_link_review_id)
            print "STACK",stack
            print "tbl_dico_ref",tbl_dico_ref
            print "tbl_dico_type",tbl_dico_type
            print "tbl_dico_target",tbl_dico_target
            print "tbl_dico_link_review_id",tbl_dico_link_review_id
            # Second pass
            if target_release_requested != "":
                tbl_reviews = []
                tbl_ref = []
                for key,target_release in tbl_dico_target.items():
                    if target_release_requested == target_release:
                        tbl_reviews.append(tbl_dico_link_review_id[key])
                        tbl_ref.append(tbl_dico_ref[key] + " " + tbl_dico_type[key])
            final_tbl_reviews = copy.copy(tbl_reviews)
            final_tbl_ref = copy.copy(tbl_ref)
            if recur:
                if tbl_reviews != []:
                    for top_review_id in tbl_reviews:
                        top_tbl_reviews,top_tbl_ref = self.getPreviousReviewsRecords(top_review_id,target_release_requested)
                        if top_tbl_reviews != []:
                            final_tbl_reviews.extend(top_tbl_reviews)
                            final_tbl_ref.extend(top_tbl_ref)
        return set(final_tbl_reviews),set(final_tbl_ref)

    def getPreviousReviews(self,review_id,recur=False):
        stdout = ""
        stderr = ""
        tbl_reviews = []
        final_tbl_reviews = []
        if review_id != "":
            sql_query = "SELECT review_join_review.link_review_id, \
    							review_join_review.id, \
    							reviews.date, \
    							reviews.type, \
    							review_type.description as type, \
    							review_type.id as type_id, \
    							scope.abrvt as scope \
    							FROM review_join_review \
    							LEFT OUTER JOIN reviews ON reviews.id = review_join_review.link_review_id \
    							LEFT OUTER JOIN review_type ON reviews.type = review_type.id \
    							LEFT OUTER JOIN scope ON review_type.scope_id = scope.id \
    							WHERE review_join_review.review_id = {:s}".format(review_id)
            sql_opt = "-X -udocid finister -e \" {:s}\" ".format(sql_query)
            stdout,stderr = self.mysql_query(sql_opt,"MySQL getPreviousReviews")
            parser = MyHTMLParser()
            stdout = MySQL.convertBeacon(stdout)
            parser.feed(stdout)
            for key,value in parser.dico.items():
                if key[1] == "link_review_id":
                    tbl_reviews.append(value)
            final_tbl_reviews = copy.copy(tbl_reviews)
            if recur:
                if tbl_reviews != []:
                    for top_review_id in tbl_reviews:
                        top_tbl_reviews = self.getPreviousReviews(top_review_id,True)
                        if top_tbl_reviews != []:
                            # tbl_reviews.extend(top_tbl_reviews)
                            final_tbl_reviews.extend(top_tbl_reviews)
        return set(final_tbl_reviews)

    def getActions(self,review_id,open=False):
        stdout = ""
        stderr = ""
        if review_id != "":
            if open:
                only_open_actions = " AND actions.status = 8 "
            else:
                only_open_actions = ""
            sql_query = "SELECT actions.comment,\
    					actions.id, \
    					actions.review as review_id, \
    					actions.status as status_id, \
    					actions.posted_by, \
    					actions.criticality as criticality_id, \
    					actions.context, \
    					actions.Description, \
    				    projects.project, \
    				   projects.id as project_id, \
    				   lrus.lru, \
    				   lrus.id as sub_project_id, \
    				   fname, \
    				   lname, \
    				   bug_criticality.name as criticality, \
    				   bug_status.name as status, \
    				   date_open, \
    				   date_expected, \
    				   date_closure,  \
                       scope.abrvt as scope, \
                       review_type.type \
    				   FROM actions \
    				   LEFT OUTER JOIN reviews ON actions.review = reviews.id \
                       LEFT OUTER JOIN review_type ON reviews.type = review_type.id \
                       LEFT OUTER JOIN scope ON review_type.scope_id = scope.id \
    				   LEFT OUTER JOIN baseline_join_review ON baseline_join_review.review_id = reviews.id \
    				   LEFT OUTER JOIN baselines ON baseline_join_review.baseline_id = baselines.id \
    				   LEFT OUTER JOIN bug_users ON bug_users.id = actions.posted_by \
    				   LEFT OUTER JOIN lrus ON lrus.id = actions.lru \
    				   LEFT OUTER JOIN projects ON projects.id = actions.project \
    				   LEFT OUTER JOIN bug_status ON bug_status.id = actions.status \
    				   LEFT OUTER JOIN bug_criticality ON bug_criticality.level = actions.criticality \
    				   WHERE review = {:s} {:s}\
                        GROUP BY actions.id ORDER BY id ASC".format(review_id,only_open_actions)

            sql_opt = "-X -udocid finister -e \" {:s}\" ".format(sql_query)
            stdout,stderr = self.mysql_query(sql_opt,"MySQL getActions")
        return stdout,stderr

    def getAttendeesList(self,review_id,copy=False):
        stdout = ""
        stderr = ""
        if review_id != "":
            if copy:
                copy_nb = 1
            else:
                copy_nb = 0
            sql_query = "SELECT user_join_review.user_id as id , \
    					 user_join_review.id as link_id, \
    					 copy, \
    					 fname, \
    					 lname, \
    					 email, \
    					 telephone as phone, \
    					 function , \
    					 enterprises.name as company \
    					 FROM bug_users \
    					 LEFT OUTER JOIN enterprises ON enterprises.id = enterprise_id \
    					 LEFT OUTER JOIN user_join_review ON bug_users.id = user_join_review.user_id \
    					 LEFT OUTER JOIN reviews ON reviews.id = user_join_review.review_id \
    					 WHERE user_join_review.copy = {:d} AND reviews.id = {:s} ORDER BY company ASC, lname ASC".format(copy_nb,review_id)

            sql_opt = "-X -udocid finister -e \" {:s}\" ".format(sql_query)
            stdout,stderr = self.mysql_query(sql_opt,"MySQL getAttendees")
        return stdout,stderr

    def getReviewsList(self):
        sql_query = "SELECT DISTINCT reviews.id, \
						reviews.title, \
						reviews.status, \
						reviews.mom_id, \
						reviews.comment, \
						reviews.description as description, \
						reviews.date, \
						reviews.date_end, \
						reviews.managed_by, \
						reviews.previous_id, \
						reviews.objective, \
						reviews.target_release, \
						reviews.type as type_id, \
						review_type.type as type_abbreviation, \
						review_type.description as type_description, \
						review_type.objectives, \
						review_type.activities, \
						review_type.type, \
						review_type.scope_id, \
						scope.scope, \
						data_join_review.data_id as link, \
						data_location.id as uploaded_id, \
						data_location.name as extension, \
						bug_applications.application as reference, \
						projects.project, \
						lrus.lru, \
						lrus.project as project_lru_id, \
						bug_status.name as status_name, \
						enterprises.name as company \
						FROM reviews \
						 LEFT OUTER JOIN bug_status ON reviews.status = bug_status.id \
						 LEFT OUTER JOIN aircrafts ON reviews.aircraft = aircrafts.id \
						 LEFT OUTER JOIN projects ON projects.aircraft_id = aircrafts.id \
						 LEFT OUTER JOIN review_type ON review_type.id = reviews.type \
						 LEFT OUTER JOIN enterprises ON review_type.company_id = enterprises.id \
						 LEFT OUTER JOIN scope ON review_type.scope_id = scope.id \
						 LEFT OUTER JOIN baseline_join_review ON baseline_join_review.review_id = reviews.id \
						 LEFT OUTER JOIN baselines ON baselines.id = baseline_join_review.baseline_id \
						 LEFT OUTER JOIN data_join_review ON reviews.id = data_join_review.review_id \
						 LEFT OUTER JOIN data_location ON data_location.data_id = data_join_review.data_id \
						 LEFT OUTER JOIN bug_applications ON bug_applications.id = data_join_review.data_id \
						 LEFT OUTER JOIN review_join_item ON review_join_item.review_id = reviews.id \
						 LEFT OUTER JOIN lrus ON (lrus.id = review_join_item.item_id) \
						 LEFT OUTER JOIN item_join_system ON item_join_system.item_id = lrus.id \
                         WHERE review_type.scope_id = 2 \
                         GROUP BY reviews.id ORDER BY reviews.id DESC"

						 # Attention si la review n'est pas associé à un lru alors on obtient lru = NULL
        sql_opt = "-X -udocid finister -e \" {:s}\" ".format(sql_query)
        stdout,stderr = self.mysql_query(sql_opt,"MySQL getReviewsList")
        return stdout,stderr

    def convertMySQLDate(self,date):
        return date

    def getData(self,raw,key):
        import html2text

        id = raw[key,"id"]
        context = raw[key,"scope"] + " " + raw[key,"type"] + " " + raw[key,"review_id"]
        description = raw[key,"Description"]
        description_plain_txt = html2text.html2text(Tool.removeNonAscii(description))
        impact = raw[key,"context"]
        criticality = raw[key,"criticality"]
        assignee = raw[key,"lname"]
        expected = raw[key,"date_expected"][0:10]
        status = raw[key,"status"]
        response = raw[key,"comment"]
        response_plain_txt = html2text.html2text(Tool.removeNonAscii(response))
        tbl = [id,context,description_plain_txt,impact,criticality,assignee,expected,status,response_plain_txt]
        return tbl

    def exportActionsList(self,review_id):
        tbl_action_items = []
        parser = MyHTMLParser()
        stdout,stderr = self.getActions(review_id)

        stdout = self.convertBeacon(stdout)
        parser.feed(stdout)

        for key,value  in parser.dico:
            if value == "id":
                tbl = self.getData(parser.dico,key)
                tbl_action_items.append(tbl)
        return tbl_action_items

    def exportPreviousActionsList(self,review_id,recur=False,open=False):

        tbl_reviews = []
        tbl_action_items = []
        tbl_reviews = self.getPreviousReviews(review_id,recur)
        parser = MyHTMLParser()
        #
        # stdout = self.convertBeacon(stdout)
        # parser.feed(stdout)
        #
        # for key,value in parser.dico.items():
        #
        #     if key[1] == "link_review_id":
        #         tbl_reviews.append(value)
        # parser = MyHTMLParser()
        print "Previous reviews:",tbl_reviews
        for review_id in tbl_reviews:
            stdout,stderr = self.getActions(review_id,open)

            stdout = self.convertBeacon(stdout)
            parser.feed(stdout)

        for key,value  in parser.dico:
            if value == "id":
                tbl = self.getData(parser.dico,key)
                tbl_action_items.append(tbl)
        return tbl_action_items

    def exportReviewsList(self,component_selected="",release_selected=""):
        stdout,stderr = self.getReviewsList()
        print "TEST: ", stderr
        m = re.match(r'ERROR 2003',stderr)
        print "TEST3",m
        if m:
            return "Cannot connect to MySQL server",False
        parser = MyHTMLParser()
        stdout = self.convertBeacon(stdout)
        parser.feed(stdout)
        # print parser.dico
        tbl_reviews_list = []
        for key,value  in parser.dico:
            if value == "id":
                id = parser.dico[key,"id"]
                type = parser.dico[key,"type_abbreviation"]
                reference = parser.dico[key,"reference"]
                item = parser.dico[key,"project"]
                target_release = parser.dico[key,"target_release"]
                # if "lru" in  parser.dico:
                #      print "NO lru key"
                # else:
                #      print "lru key"
                try:
                    component = parser.dico[key,"lru"]
                except KeyError:
                    # lru is a key which is not part of the dictionary
                    component = ""
                tbl = "{:s}) {:s} {:s} {:s} {:s} {:s}".format(id,component,item,type,reference,target_release)  #[id,item,type,reference]
                if (component_selected == "" or component_selected == component) and (release_selected == "" or release_selected == target_release):
                    tbl_reviews_list.append(tbl)
                else:
                    pass
                    #print "component_selected component",component_selected,component
        tbl_reviews_list.sort(reverse=True)
        return tbl_reviews_list,True

    def exportAttendeesList(self,review_id,copy=False):
        stdout,stderr = self.getAttendeesList(review_id,copy)
        parser = MyHTMLParser()
        stdout = self.convertBeacon(stdout)
        parser.feed(stdout)
        tbl_attendees_list = []
        for key,value  in parser.dico:
##            print key,value
            if value == "id":
                id = parser.dico[key,"id"]
                fname = parser.dico[key,"fname"]
                lname = parser.dico[key,"lname"]
                function = parser.dico[key,"function"]
                tbl = [fname + " " + lname,function]
                tbl_attendees_list.append(tbl)
                tbl_attendees_list.sort(reverse=True)
        if tbl_attendees_list == []:
            tbl_attendees_list = [["",""]]
        return tbl_attendees_list
    @staticmethod
    def convertBeacon(data):
        # Converti esperluette et é
        char = {r'&lt;':'<',
                '&gt;':'>',
                '&amp;nbsp;':' ',
                '&amp;ldquo;':'"',
                '&amp;rdquo;':'"',
                '&amp;quot;':'"',
                '&amp;sect;':'paragraph ',
                '\xc3\xa9':'e'}
        for before_char, after_char in char.iteritems():
            data = re.sub(before_char,after_char,data)
        return data
def main():
    tool = MySQL()
    result = tool.exportReviewsList()
    print result
    exit()
    stdout = tool.getReviewDate("354")
    print stdout
    id,ref = tool.getPreviousReviewsRecords("354")
    new_ref = list(ref)
    new_new_ref= new_ref.sort()
    print new_new_ref
    exit()
    stdout,stderr = tool.getActions("353",True)
    print stdout
    print stderr
    exit()
    result = tool.exportPreviousActionsList("353",True)
    exit()
##    stdout,stderr = tool.getAttendeesList("351")
##
##    print "stdout",stdout
    list_attendees = tool.exportAttendeesList("351")
    print list_attendees
    list_copies = tool.exportAttendeesList("351",True)
    print list_copies

    stdout,stderr = tool.getReviewsList()
    parser = MyHTMLParser()
    stdout = MySQL.convertBeacon(stdout)
    parser.feed(stdout)
    print parser.dico
    tbl_reviews_list = []
    for key,value  in parser.dico:
        if value == "id":
            id = parser.dico[key,"id"]
            type = parser.dico[key,"type_abbreviation"]
            reference = parser.dico[key,"reference"]
            item = parser.dico[key,"project"]
            tbl = [id,item,type,reference]
            tbl_reviews_list.append(tbl)
    print "TBL",tbl_reviews_list

##    tool._loadConfigMySQL()
##    sql_opt = "-X -udocid finister -e \" {:s}\" ".format(tool.getActions("350"))
##    stdout,stderr = tool.mysql_query(sql_opt,"MySQL test")
    tbl_reviews = []
    tbl_reviews = tool.getPreviousReviews("352")
    print "REVIEWS LIST",tbl_reviews
    tbl_reviews = []
    tbl_reviews = tool.getPreviousReviews("340",True)
    print "REVIEWS LIST",tbl_reviews
    print "REVIEWS LIST SET",set(tbl_reviews)

    for review_id in tbl_reviews:
        stdout,stderr = tool.getActions(review_id)

##        parser.tbl = []
        stdout = tool.convertBeacon(stdout)
        print "stdout",stdout
        parser.feed(stdout)
    print "MySQL test getActions",parser.dico
    for key,value  in parser.dico:
##        print "KEY/VALUE",key,value
        if value == "id":
            print "ACTION_ID",parser.dico[key,"id"]
if __name__ == '__main__':
    #main()
    def invert_dict(d):
        return dict([(v, k) for k, v in d.iteritems()])
    dico = {(2, 'type_id'): '58', (2, 'scope'): 'Sw', (1, 'scope'): 'Sw', (2, 'link_review_id'): '348', (1, 'application'): 'CR14-8514', (1, 'target_release'): 'SW_ENM/03', (1, 'type'): '<p>\r\r\n\tSpecification evaluation</p>\r\r\n', (1, 'type_id'): '65', (2, 'target_release'): 'SW_ENM/02', (1, 'link_review_id'): '351', (2, 'application'): 'CR14-8479', (2, 'type'): '<p>\r\r\n\tConformity Review</p>\r\r\n'}
    tbl_dico_ref = {}
    tbl_dico_type = {}
    tbl_dico_target = {}
    stack = []
    for (key1,key2),value in dico.items():
        if key2 == "application":
            #stack.append(value)
            tbl_dico_ref[value] = key1
        if key2 == "type_id":
            #stack.append(value)
            tbl_dico_type[value] = key1
        if key2 == "target_release":
            #stack.append(value)
            tbl_dico_target[value] = key1
   # print stack
    tbl_dico_ref = invert_dict(tbl_dico_ref)
    tbl_dico_type = invert_dict(tbl_dico_type)
    tbl_dico_target = invert_dict(tbl_dico_target)
    for (key1,key2),value in dico.items():
        if key2 == "target_release":
            stack.append(value)
        #tbl_dico[key1] = [key2,value]