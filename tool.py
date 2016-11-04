#!/usr/bin/env python 2.7.3
## -*- coding: latin-1 -*-
# -*- coding: utf-8 -*-
import warnings
try:
    from Tkinter import END
except ImportError as exception:
    from tkinter import END
#from Tkinter import Canvas
#import platform
import time
#import datetime
import csv
import sqlite3 as lite
import subprocess
try:
    from ConfigParser import ConfigParser
except ImportError as exception:
    from configparser import ConfigParser
import sys
import os
import re # For regular expressions
#from tkintertable.TableModels import TableModel
#from tkintertable.Tables import TableCanvas
from datetime import datetime

sys.path.append("python-docx")
sys.path.append("python_docx_html")
sys.path.append("intelhex")
sys.path.append("html_build")
sys.path.append("pycparser")

try:
    import docx
except ImportError:
    print ("DoCID requires the python-docx library for Python. See https://github.com/mikemaccana/python-docx/")
                #    raise ImportError, "DoCID requires the python-docx library
from os.path import join
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
import urllib

try:
    import urllib2
except ImportError as exception:
    warnings.warn(str(exception))
import sys
try:
    from intelhex import IntelHex,IntelHex16bit
except ImportError as e:
    print (e)
from math import floor
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser
try:
    from html import add_html
except ImportError as e:
    print (e)
try:
    from html_build import HTML
except ImportError as e:
    print (e)

# Abstract Syntax Tree
#try:
#    from pycparser import c_parser, c_ast,parse_file
#except ImportError as e:
#    warnings.warn(e)
class SQLite():
    # TODO: Move sqlite query from Tool class here
    def __init__(self,database):
        self.database = database

    def connect(self):
        try:
            self.con = lite.connect(self.database, isolation_level=None)
            #cur = self.con.cursor()
            #cur.execute("DROP TABLE IF EXISTS hlr_vs_chapter")
            return True
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            return False

    def create(self):
        try:
            #con = lite.connect('swrd_enm.db3')
            cur = self.con.cursor()
            cur.executescript("""
                                BEGIN TRANSACTION;
                                DROP TABLE IF EXISTS requirements;
                                CREATE TABLE requirements (id INTEGER PRIMARY KEY, tag TEXT, body TEXT, issue TEXT, refer TEXT, status TEXT, derived TEXT, terminal TEXT,rationale TEXT, safety TEXT, additional TEXT);
                                COMMIT;
                """)
            self.con.commit()
            print 'New SQLite database created.'
            return True
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            return False
        #finally:
        #    if con:
        #        con.close()

    def insert_many(self,dico_attr):
        with self.con:
            counter = 0
            cur = self.con.cursor()
            #self.con.set_progress_handler(self.progress_handler, 1)
            #print "tbl_req_vs_chapter",tbl_req_vs_chapter
            #cur.execute("INSERT INTO last_query(database,reference,revision,project,item,release,baseline,input_date) VALUES(?,?,?,?,?,?,?,?)",(self.database,self.reference,self.revision,project,item,release,baseline,now))
            for req,value in dico_attr.iteritems():
                dico_attrib = {}
                dico_attrib["id"] = req
                dico_attrib["body"] = Tool.getAtribute(value,"body")
                dico_attrib["derived"] = Tool.getAtribute(value,"derived")
                dico_attrib["issue"] = Tool.getAtribute(value,"issue")
                dico_attrib["refer"] = Tool.getAtribute(value,"refer")
                dico_attrib["status"] = Tool.getAtribute(value,"status")
                dico_attrib["safety"] = Tool.getAtribute(value,"safety")
                dico_attrib["terminal"] = Tool.getAtribute(value,"terminal")
                dico_attrib["additional"] = Tool.getAtribute(value,"additional")
                dico_attrib["rationale"] = Tool.getAtribute(value,"rationale")
                counter += 1
                cur.execute("INSERT INTO requirements(tag,body,issue,refer,status,derived,terminal,rationale,safety,additional) "
                            "VALUES(?,?,?,?,?,?,?,?,?,?)",(dico_attrib["id"],dico_attrib["body"],dico_attrib["issue"],
                                                           dico_attrib["refer"],dico_attrib["status"],dico_attrib["derived"],
                                                           dico_attrib["terminal"],dico_attrib["rationale"],dico_attrib["safety"],
                                                           dico_attrib["additional"]))
            #cur.executemany("INSERT INTO hlr_vs_chapter(chapter,req_id) VALUES(?,?)", tbl_req_vs_chapter)
            #print cur.rowcount
            self.con.commit()
        return counter

    def get_all(self):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id, tag , body , issue , refer , status , derived, terminal ,rationale, safety, additional FROM requirements")
            data = cur.fetchall()
        return data

    def get(self,id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id, tag , body , issue , refer , status , derived, terminal ,rationale, safety, additional FROM requirements WHERE id = {:d}".format(id))
            data = cur.fetchone()
        return data

    def close(self):
        if self.con:
            self.con.close()

class StdMngt(SQLite):
    @staticmethod
    def getUserRole(login,
                     database="db/sdts_rules.db3"):
        table = "access_control_list"
        query = "SELECT role FROM {:s} WHERE login LIKE '{:s}'".format(table,login)
        print "QUERY",query
        result = Tool.sqlite_query_one(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def getSDTS_Rule(tag,
                     version=None,
                     database="db/sdts_rules.db3"):
        table = "rules"
        print ("rule id:",tag)
        if version is not None:
            query = "SELECT description,status,version FROM {:s} WHERE tag = {:s} AND version = {:s}".format(table,str(tag),version)
        else:
            query = "SELECT description,status,version FROM {:s} WHERE tag = {:s} ".format(table,str(tag))
        print "getSDTS_Rule:",query
        result = Tool.sqlite_query_one(query,database=database)
        print "RESULT",result
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def getSDTS_Rule_by_ID(rule_id,
                           database="db/sdts_rules.db3"):
        table = "rules"
        print ("rule id:",rule_id)
        query = "SELECT description,status,version FROM {:s} WHERE id = {:s} ".format(table,str(rule_id))
        print "getSDTS_Rule:",query
        result = Tool.sqlite_query_one(query,database=database)
        print "RESULT",result
        if result is None:
            data = False
        else:
            data = result
        return data

    @classmethod
    def getSRTS_Rule(cls,id):
        # TODO: Erreur a corriger self ... static method
        """

        :type cls: object
        """
        data = cls.getSDTS_Rule(id,database="db/srts_rules.db3")
        return data
        table = "rules"
        #print ("rule id:",id)
        query = "SELECT description FROM {:s} WHERE id LIKE '{:s}'".format(table,id)
        result = Tool.sqlite_query_one(query,database="db/srts_rules.db3")
        if result is None:
            data = False
        else:
            data = result[0]
        return data

    @staticmethod
    def getRuleObjectives(tag,
                          database="db/sdts_rules.db3"):
        table = "rules_vs_objectives"
        print ("rule id:",tag)
        query = "SELECT type,chapter,objective FROM {:s} LEFT JOIN do_178_objectives ON do_178_objectives.id = rules_vs_objectives.objective_id WHERE rule_id LIKE '{:s}'".format(table,str(tag))
        print "getRuleObjectives:",query
        result = Tool.sqlite_query(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def getDoObjective(objective_id,
                     database="db/sdts_rules.db3"):
        table = "do_178_objectives"
        print ("objective id:",objective_id)
        query = "SELECT chapter,objective,description,type FROM {:s} WHERE id LIKE '{:d}'".format(table,objective_id)
        print "QUERY",query
        result = Tool.sqlite_query_one(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def getDesignReviewDoObjectives(database="db/sdts_rules.db3"):
        table = "do_178_objectives"
        query = "SELECT id,chapter,objective,description,type FROM {:s} ".format(table)
        result = Tool.sqlite_query(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    # sdts_rules.db3
    @staticmethod
    def getAll_SDTS_Rule_by_req(by_req=True,
                                version=None,
                                database="db/sdts_rules.db3"):
        table = "rules"
        #print ("rule id:",id)
        if by_req:
            by_req_str = "1"
        else:
            by_req_str = "0"
        if version is not None:
            if by_req_str == "1":
                query = "SELECT id,tag,status,version,description,auto,comments FROM {:s} WHERE by_req LIKE '1' AND version LIKE '{:s}'".format(table,version)
            else:
                query = "SELECT id,tag,status,version,description,auto,comments FROM {:s} WHERE (by_req != '1' OR by_req IS NULL) AND version LIKE '{:s}'".format(table,version)
        else:
            if by_req_str == "1":
                query = "SELECT id,tag,status,version,description,auto,comments FROM {:s} WHERE by_req LIKE '1' AND (status != 'OBSOLETE' OR status IS NULL)".format(table)
            else:
                query = "SELECT id,tag,status,version,description,auto,comments FROM {:s} WHERE (by_req != '1' OR by_req IS NULL) AND (status != 'OBSOLETE' OR status IS NULL)".format(table)
        print "getAll_SDTS_Rule_by_req:",query
        result = Tool.sqlite_query(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def updateDo(id,txt,database="db/sdts_rules.db3"):
        #now = datetime.datetime.now()
        con = lite.connect(database, isolation_level=None)
        cur = con.cursor()
        cur.execute("SELECT id FROM do_178_objectives WHERE id LIKE '{:d}'  LIMIT 1".format(id))
        data = cur.fetchone()
        if data is not None:
            id = data[0]
            cur.execute("UPDATE do_178_objectives SET description=? WHERE id= ?",(txt,id))

    @staticmethod
    def updateRuleStatus(tag,
                         status,
                         database="db/sdts_rules.db3"):
        #now = datetime.datetime.now()
        con = lite.connect(database, isolation_level=None)
        cur = con.cursor()
        cur.execute("SELECT id,tag FROM rules WHERE tag LIKE '{:s}' LIMIT 1".format(tag))
        data = cur.fetchone()
        print "DATA",data
        if data is not None:
            id_found = data[0]
            query = "UPDATE rules SET status=? WHERE id= ?",(status,id_found)
            print "QUERY",query
            cur.execute("UPDATE rules SET status=? WHERE id= ?",(status,id_found))
        #else:
        #    cur.execute("INSERT INTO history(document_id,issue,writer_id,date,modifications) VALUES(?,?,?,?,?)",(3,self.revision,1,now,interface.modif_log.get(1.0,END)))

    @staticmethod
    def updateRule(tag,
                   txt,
                   status,
                   version=None,
                   database="db/sdts_rules.db3"):
        #now = datetime.datetime.now()
        con = lite.connect(database, isolation_level=None)
        cur = con.cursor()
        if version is not None:
            query = "SELECT id,tag FROM rules WHERE tag = {:s} AND version LIKE '{:s}' LIMIT 1".format(tag,version)
            print "QUERY",query
            cur.execute(query)
            data = cur.fetchone()
            if data is None:
                print "May be version is to be created in database {:s}".format(database)
                cur.execute("INSERT INTO rules(description,status,version,tag) VALUES(?,?,?,?)",(txt,status,version,tag))
        else:
            cur.execute("SELECT id,tag FROM rules WHERE tag LIKE '{:s}' LIMIT 1".format(tag))
            data = cur.fetchone()
        print "DATA",data
        if data is not None:
            id_found = data[0]
            cur.execute("UPDATE rules SET description=?,status=?,version=? WHERE id= ?",(txt,status,version,id_found))
        #else:
        #    cur.execute("INSERT INTO history(document_id,issue,writer_id,date,modifications) VALUES(?,?,?,?,?)",(3,self.revision,1,now,interface.modif_log.get(1.0,END)))

    @staticmethod
    def addLinkRule2Objective(rule_id,objective_id,database="db/sdts_rules.db3"):
        #TODO: write addLinkRule2Objective function
        print "write addLinkRule2Objective function",rule_id,objective_id
        con = lite.connect(database, isolation_level=None)
        cur = con.cursor()
        #cur.execute("SELECT rules.id FROM rules_vs_comments WHERE rule_id LIKE '" + id + "'  LIMIT 1")
        #data = cur.fetchone()
        #if data is not None:
        #   id = data[0]
        #   cur.execute("UPDATE rules SET description=? WHERE id= ?",(txt,id))
        #else:
        cur.execute("INSERT INTO rules_vs_objectives(rule_id,objective_id) VALUES(?,?)",(rule_id,objective_id))

    @staticmethod
    def readComments(id,database="db/sdts_rules.db3",table = "rules_vs_comments"):
        # TODO: rendre generique pour les reqs
        print ("rule id:",id)
        query = "SELECT id,user_login,date,comment FROM {:s} WHERE rule_id LIKE '{:s}' ".format(table,str(id))
        result = Tool.sqlite_query(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def readResponses(comment_id,database="db/sdts_rules.db3"):
        table = "responses_to_comments"
        query = "SELECT id,user_login,date,response FROM {:s} WHERE comment_id LIKE '{:d}' ".format(table,comment_id)
        result = Tool.sqlite_query(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def readCommentByID(comment_id,database="db/sdts_rules.db3"):
        table = "rules_vs_comments"
        print ("rule id:",comment_id)
        query = "SELECT id,user_login,date,comment,status,rule_id FROM {:s} WHERE id LIKE '{:d}' ".format(table,comment_id)
        result = Tool.sqlite_query_one(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def readResponse(id,database="db/sdts_rules.db3"):
        table = "responses_to_comments"
        print ("rule id:",id)
        query = "SELECT id,user_login,date,response,status,comment_id FROM {:s} WHERE id LIKE '{:d}' ".format(table,id)
        result = Tool.sqlite_query_one(query,database=database)
        if result is None:
            data = False
        else:
            data = result
        return data

    @staticmethod
    def ResponseToComment(id,user_login="Nobody",date="",txt="",database="db/sdts_rules.db3"):
        con = lite.connect(database, isolation_level=None)
        cur = con.cursor()
        cur.execute("INSERT INTO responses_to_comments(comment_id,user_login,date,response) VALUES(?,?,?,?)",(id,user_login,date,txt))

    @staticmethod
    def addCommentRule(id,user_login="Nobody",date="",txt="",database="db/sdts_rules.db3"):
        con = lite.connect(database, isolation_level=None)
        cur = con.cursor()
        cur.execute("INSERT INTO rules_vs_comments(rule_id,user_login,date,comment) VALUES(?,?,?,?)",(id,user_login,date,txt))

    @staticmethod
    def UpdateComment(id,user_login="Nobody",date="",txt="",status="",database="db/sdts_rules.db3"):
        con = lite.connect(database, isolation_level=None)
        cur = con.cursor()
        cur.execute("SELECT id FROM rules_vs_comments WHERE id LIKE '{:d}'  LIMIT 1".format(id))
        data = cur.fetchone()
        if data is not None:
           id = data[0]
           cur.execute("UPDATE rules_vs_comments SET user_login=?,date=?,comment=?,status=? WHERE id= ?",(user_login,date,txt,status,id))

    @staticmethod
    def UpdateResponse(id,user_login="Nobody",date="",txt="",database="db/sdts_rules.db3"):
        con = lite.connect(database, isolation_level=None)
        cur = con.cursor()
        cur.execute("SELECT id FROM responses_to_comments WHERE id LIKE '{:d}'  LIMIT 1".format(id))
        data = cur.fetchone()
        if data is not None:
           id = data[0]
           cur.execute("UPDATE responses_to_comments SET user_login=?,date=?,response=? WHERE id= ?",(user_login,date,txt,id))

#
# Class Tool
#
class Tool(StdMngt,SQLite):
    """
        Class toolbox
    """
    dico_status_vs_transition = {"In Review":"To Under Modification",
                                 "Complementary Analysis":"To Under Modification",
                                 "Postponed":"From Postponed",
                                 "Fixed":"From Fixed"
                                }
    dico_status_flow = {"In Review":("Under_Modification",),
                        "Complementary Analysis":("Under_Modification",),
                        "Postponed":("In_Analysis",),
                        "Fixed":("Under_Verification","Cancelled","Closed")
                        }
    dico_transition_flow = {"In Review":("Reviewed",),
                        "Complementary Analysis":("Reviewed",),
                        "Postponed":("Incomplete analysis",),
                        "Fixed":("Incomplete verification","Cancel","Close")
                        }
    dico_get_transition_flow = {"Closed":"Close",
                                "Cancelled":"Cancel",
                                "Rejected":"Reject",
                                "Under Modification":"Reviewed",
                                "Under Verification":"Modified",
                                "Postponed":"Postpone",
                                "Fixed":"Verified"}

    def getStatementBlock(self,line,keyword="Statement blocks"):
        m = re.match(r'^\s*'+keyword+'\s*\.*\s*([0-9]{1,3}\.[0-9])%\s\(([0-9]{1,3}\/[0-9]{1,3})\)',line)
        if m:
            percentage = m.group(1)
            range = m.group(2)
            return percentage,range
        else:
            return False,False

    def listDir(self,
                dirname=""):
        """
        Recursive function to find files in directories.
        Treatment for Excel and Word file is different
        :param dirname:
        :param type:
        :return:
        """
        color = "white"
        if "general_output_txt" in self.__dict__:
            self.general_output_txt.tag_configure("color", foreground=color)
        #print "depth",self.depth
        new_concat_dirname = self.basename
        for dir in self.stack:
            new_concat_dirname = join(new_concat_dirname,dir)
            if sys.platform.startswith('win32'):
                new_concat_dirname = "{:s}\\".format(new_concat_dirname)
            else:
                new_concat_dirname = "{:s}/".format(new_concat_dirname)

        try:
            try:
                list_dir = os.listdir(new_concat_dirname)
            except WindowsError as e:
                self.log("{:s}".format(e))
                list_dir = []
            except OSError as e:
                self.log("{:s}".format(e))
                list_dir = []
        except NameError as exception:
                self.log("{:s}".format(exception))
                list_dir = []

        for found_dir in list_dir:
            path_dir = os.path.join(new_concat_dirname, found_dir)
            isdir = os.path.isdir(path_dir)
            if isdir:
                self.stack.append(found_dir)
                self.listDir(found_dir)
                self.stack.pop()
            else:
                void = re.sub(r"(~\$)(.*)\.(.*)",r"\1",found_dir)
                name = re.sub(r"(.*)\.(.*)",r"\1",found_dir)
                extension = re.sub(r"(.*)\.(.*)",r"\2",found_dir)
                new_concat_dirname = re.sub(r'\/',r'\\',new_concat_dirname)
                filename = join(new_concat_dirname,found_dir)
                print ("1) DOC NAME:",filename)
                fin = open(filename)
                input = fin.read()
                output = input.splitlines()
                found = False
                tbl_stats = {}
                for line in output:
                    for keyword in ("Statement blocks",
                                    "Decisions",
                                    "Basic conditions",
                                    "Modified conditions"):
                        percentage,range = self.getStatementBlock(line,keyword)
                        if percentage:
                            found =True
                            tbl_stats[keyword] = percentage
                if found:
                    self.list_coverage[found_dir] = tbl_stats

    def CommentStripper (self,iterator):
        '''
            Remove # comment
            '''
        for line in iterator:
            if line [:1] == '#':
                continue
            if not line.strip ():
                continue
            yield line

    @staticmethod
    def getAtribute(dico,attr):
        if attr in dico:
            value = Tool.removeNonAscii(dico[attr])
            # Remove tabulation
            value = re.sub(r"\t",r"",value)
        else:
            value = "None"
        return value

    def getOptions(self,key,tag):
        if self.config_parser.has_option(key,tag):
            value = self.config_parser.get(key,tag)
        else:
            value = ""
        return value

    def getOptionsTuple(self,key,tag):
        if self.config_parser.has_option(key,tag):
            value = [e.strip() for e in self.config_parser.get(key, tag).split(',')]
        else:
            value = ["",""]
        return value


    def updateCheck(self):
        """
        Checks for updates
        if web server is not reachable then we consider that no new version is available.
        :return: new_version
        """
        #Get downloaded version
        versionSource = open('version.txt', 'r')
        versionContents = versionSource.read()

        #gets newest version
        url = self.getOptions("Default","update_server")
        url_proxy = self.getOptions("Default","proxy")
        try:
            print ("Try update version reading without proxy")
            updateSource = urllib.urlopen("{:s}/version.txt".format(url))
            updateContents = updateSource.read()
        except IOError as e:
            print ("Try update version reading with proxy")
            proxy_support = urllib2.ProxyHandler({"http":url_proxy})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
            #try:
            updateContents = urllib2.urlopen("{:s}/version.txt".format(url)).read()
            #except URLError,e: # NameError: global name 'URLError' is not defined
            #    updateContents = ""
            #    print e
        found_last_version = re.sub(r"([0-9]*\.[0-9]*\.[0-9]*)", r"\1",updateContents)
        found_last_version = updateContents.replace("\r","")
        found_last_version = found_last_version.replace("\n","")
        if found_last_version == versionContents:
            new_version = False
        else:
            new_version = found_last_version
        return new_version
    #
    # Static methods
    #
    @staticmethod
    def getDateNow():
        default_time = datetime.now()
        default_time_converted = "{:d}/{:d}/{:d} {:d}:{:d}:{:d}".format(default_time.year,
                                           default_time.month,
                                           default_time.day,
                                           default_time.hour,
                                           default_time.minute,
                                           default_time.second)
        return default_time_converted

    @staticmethod
    def extractName(filename_is):
        filename_is_short = re.sub(r"^(.*)(\/|\\)([0-9A-Za-z ]*_.*)\.(.*)$",r"\3",filename_is)
        return filename_is_short

    @staticmethod
    def getDocRelease(m):
        release = m.group(1)
        return release

    @staticmethod
    def getDocName(m):
        document = m.group(2)
        version = m.group(3)
        doc_name = re.sub(r"(.*)\.(.*)", r"\1", document)
        name = doc_name + " issue " + version
        return name

    @staticmethod
    def getFileExt(filename):
        extension = re.sub(r"(.*)\.(.*)",r"\2",filename)
        return extension

    @staticmethod
    def getFileNameAlone(filename):
        extension = re.sub(r"(.*)\.(.*)",r"\1",filename)
        return extension

    @staticmethod
    def getCoord(txt):
        coord = re.sub(r"^[\w\\_\.:]*:([0-9]*)$",r"\1",str(txt))
        return coord

    @staticmethod
    def getFileName(filename):
        #doc_name = re.sub(r"^(.*)(\/|\\)([A-Za-z ]*)\.(.*)$",r"\3",filename)
        doc_name = re.sub(r"^.*(\/|\\)(.*)\.([a-zA-Z]){1,6}$", r"\2", filename)
        return doc_name

    @staticmethod
    def getType(filename,
                tbl_type = ("SWRD","SWDD","HSID","IRD","ICD","SHLVCP","SLLVCP","SSCS","SES","SSS"),
                default_type="\w*"):
        """
        Define type of the document according to keyword in filename
        :return:
        """
        type_found = default_type
        ext = Tool.getFileExt(filename)
        if ext == "bproc":
            type_found = "BPROC"
        elif ext in ("c","asm","vhd"):
            type_found = "SRC"
        else:
            filename = filename.upper()
            for type in tbl_type:
                if type in filename:
                    type_found = type.upper()
                    break
                else:
                    keywords = type.split("_")
                    nb_keywords = len(keywords)
                    counter_keywords = 0
                    for keyword in keywords:
                        #print "KEYWORD",keyword
                        if keyword in filename:
                            counter_keywords += 1
                            print "counter_keywords",counter_keywords
                    if counter_keywords == nb_keywords:
                        type_found = type.upper()
        return type_found

    @staticmethod
    def isAttributeValid(attr):
        if attr not in ("","*", "All", "None",None):
            result = True
        else:
            result = False
        return result

    @staticmethod
    def removeStatusPrefix(status):
        result = re.sub(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)', r'\2', status)
        return result

    @staticmethod
    def getStatusPrefix(status):
        result = re.sub(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)', r'\1', status)
        return result

    @staticmethod
    def getPN(txt):
        def getAscii(hex):
            code_hex = hex
            code_ascii = code_hex.decode("hex")
            return code_ascii
        #dirname = "C:\\Documents and Settings\\appereo1\\Bureau\\sqa\\"
        #filename = join(dirname,"F5X_BITE-2.0.hex")

        pn = ["E","C","E"]
        # ENM, WHCC
        # ex:
        # :10040000010000004543000045330000462d000078
        # :1004100041330000333800002d300000343000003c
        # :0404200031000000a7
        found_pn = False
        for data in txt:
            #print "DATA:",data
            # ECEX
            m = re.match(r'^:10040000010000004543000045([\w]{2})0000([\w]{2})2d0000[\w]{2}$', data)
            if m:
                code_crc_1 = getAscii(m.group(1))
                code_crc_2 = getAscii(m.group(2))
                pn.append(code_crc_1)
                pn.append(code_crc_2)
                pn.append("-")
            # X-AX
            m = re.match(r'^:1004100041([\w]{2})0000([\w]{2})([\w]{2})00002d([\w]{2})0000([\w]{2})([\w]{2})0000[\w]{2}$', data)
            if m:
                pn.append("A")
                code_pn_1 = getAscii(m.group(1))
                code_pn_2 = getAscii(m.group(2))
                code_pn_3 = getAscii(m.group(3))
                code_vi_1 = getAscii(m.group(4))
                code_vi_2 = getAscii(m.group(5))
                code_ri_1 = getAscii(m.group(6))
                pn.append(code_pn_1)
                pn.append(code_pn_2)
                pn.append(code_pn_3)
                pn.append("-")
                pn.append(code_vi_1)
                pn.append(code_vi_2)
                pn.append(code_ri_1)
            # XXX
            m = re.match(r'^:04042000([\w]{2})000000[\w]{2}$', data)
            if m:
                code_ri_2 = getAscii(m.group(1))
                pn.append(code_ri_2)
                found_pn = True
                break;
        # BITE
        if not found_pn:
            for data in txt:
                #print "DATA:",data
                # ECEX
                m = re.match(r'^:10040000450000004300000045000000([\w]{2})000000[\w]{2}$', data)
                if m:
                    code_crc_1 = getAscii(m.group(1))
                    pn.append(code_crc_1)
                # X-AX
                m = re.match(r'^:10041000([\w]{2})0000002d00000041000000([\w]{2})000000[\w]{2}$', data)
                if m:
                    code_crc_2 = getAscii(m.group(1))
                    pn.append(code_crc_2)
                    pn.append("-")
                    pn.append("A")
                    code_pn_1 = getAscii(m.group(2))
                    pn.append(code_pn_1)
                # XX-X
                m = re.match(r'^:10042000([\w]{2})000000([\w]{2})0000002d000000([\w]{2})000000[\w]{2}$', data)
                if m:
                    code_pn_2 = getAscii(m.group(1))
                    pn.append(code_pn_2)
                    code_pn_3 = getAscii(m.group(2))
                    pn.append(code_pn_3)
                    pn.append("-")
                    code_vi_1 = getAscii(m.group(3))
                    pn.append(code_vi_1)
                # XXX
                m = re.match(r'^:0c043000([\w]{2})000000([\w]{2})000000([\w]{2})000000[\w]{2}$', data)
                if m:
                    code_vi_2 = getAscii(m.group(1))
                    pn.append(code_vi_2)
                    code_ri_1 = getAscii(m.group(2))
                    pn.append(code_ri_1)
                    code_ri_2 = getAscii(m.group(3))
                    pn.append(code_ri_2)
                    break;
        print ("PN:",pn)
        str_pn = "".join(pn)
        return str_pn

    def __init__(self,config_filename="docid.ini"):
        '''
            get in file .ini information to access synergy server
            '''
        # Get config
        self.stack = []
        self.list_coverage = {}
        self.found_config = False
        self.config_parser = ConfigParser()
        config_file = join("conf",config_filename)
        result = self.config_parser.read(config_file)
        if result != []:
            self.found_config = True
        self.gen_dir = self.getOptions("Generation","dir")
        #self._loadConfigSynergy()
        # En doublon avec la classe BuildDoc
        self.dico_descr_docs = {}
        self.dico_descr_docs_default = {}
        # read dictionary of generic description for doc
        # 2 columns separated by comma
        if self.config_parser.has_option("Generation","glossary"):
            file_descr_docs = self.config_parser.get("Generation","glossary")
            file_descr_docs = join("conf",file_descr_docs)
            if sys.version_info[0] > 2:
                # Python 3
                with open(file_descr_docs, 'rt', encoding='utf-8') as file_csv_handler:
                    reader = csv.reader(self.CommentStripper (file_csv_handler))
                    for tag,description in reader:
                        self.dico_descr_docs_default[tag] = description
            else:
                 # Python 2
                with open(file_descr_docs, 'rb') as file_csv_handler:
                    reader = csv.reader(self.CommentStripper (file_csv_handler))
                    for tag,description in reader:
                        self.dico_descr_docs_default[tag] = description

    def ccb_minutes(self):
        pass
    def plan_review_minutes(self):
        pass
    def spec_review_minutes(self):
        pass

    def scrollEvent(self,event):
        print (event.delta)
        if event.delta >0:
            print ('move up')
            self.help_text.yview_scroll(-2,'units')
        else:
            print ('move down')
            self.help_text.yview_scroll(2,'units')

    def populate_listbox(self,
                         query,
                         listbox,
                         first,
                         two=False,
                         init=False):
        # populate systems listbox
        listbox.delete(0, END)
        listbox.insert(END, first)
        if two:
            result_query = self.sqlite_query(query)
            if result_query in (None,[]):
                result = None
            else:
                 # Remove doublons; attention set supprime le tri
                result = result_query
                for item in sorted(set(result)):
                    txt = item[0] + " (" + item[1] + ")"
                    listbox.insert(END, txt)
        else:
            result = self.sqlite_query(query)
             # Remove doublons; attention set supprime le tri
            if init:
                list_items_id = []
                for item in sorted(set(result)):
                    list_items_id.append(item[1])
                    listbox.insert(END, item[0])
            else:
                for item in sorted(set(result)):
                    listbox.insert(END, item[0])
                list_items_id = result
        # return list of entries found in SQLite database
        return list_items_id

    def populate_specific_listbox(self,listbox,item_id,system):
        query = 'SELECT items.name FROM items LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id \
                                                LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                WHERE systems.name LIKE \'{:s}\' ORDER BY items.name ASC'.format(system)
        self.populate_listbox(query,listbox,"None")
        if item_id != ():
            listbox.selection_set(first=item_id)
            listbox.see(item_id)
            item = listbox.get(item_id)
        else:
            listbox.selection_set(first=0)
            item = ""
        return item

    def populate_components_listbox(self,listbox,item_id,item,system=""):
        if item != "" and system != "":
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            LEFT OUTER JOIN items ON items.id = link_items_components.item_id \
                                                            WHERE systems.name LIKE \'' + system + '\' AND items.name LIKE \'' + item + '\'  ORDER BY components.name ASC'
        elif system != "":
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            WHERE systems.name LIKE \'' + system + '\' ORDER BY components.name ASC'
        else:
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            ORDER BY components.name ASC'
        result_query = self.populate_listbox(query,listbox,"None")
        if item_id != ():
            listbox.selection_set(first=item_id)
            listbox.see(item_id)
            item = listbox.get(item_id)
        else:
            listbox.selection_set(first=0)
            item = ""
        if result_query in (None,[]):
            result = None
        else:
            result = result_query
        return result

    def getListComponents(self,
                          item="",
                          system=""):
        if item != "" and system != "":
            query = 'SELECT components.name,components.cr_type FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            LEFT OUTER JOIN items ON items.id = link_items_components.item_id \
                                                            WHERE systems.name LIKE \'' + system + '\' AND items.name LIKE \'' + item + '\'  ORDER BY components.name ASC'
        elif system != "":
            query = 'SELECT components.name,components.cr_type FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            WHERE systems.name LIKE \'' + system + '\'  ORDER BY components.name ASC'
        else:
             query = 'SELECT components.name,components.cr_type FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                             ORDER BY components.name ASC'
        result_query = self.sqlite_query(query)
        if result_query in (None,[]):
            result = None
        else:
             # Remove doublons; attention set supprime le tri
            result = result_query
        return result

    def populate_components_listbox_wo_select(self,
                                              listbox,
                                              item="",
                                              system=""):
        if item != "" and system != "":
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            LEFT OUTER JOIN items ON items.id = link_items_components.item_id \
                                                            WHERE systems.name LIKE \'' + system + '\' AND items.name LIKE \'' + item + '\'  ORDER BY components.name ASC'
        elif system != "":
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                            LEFT OUTER JOIN link_systems_items ON link_items_components.item_id = link_systems_items.item_id \
                                                            LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                                                            WHERE systems.name LIKE \'' + system + '\'  ORDER BY components.name ASC'
        else:
            print ("TROIS")
            query = 'SELECT components.name FROM components LEFT OUTER JOIN link_items_components ON components.id = link_items_components.component_id \
                                                             ORDER BY components.name ASC'
        result_query = self.populate_listbox(query,listbox,"None")
        return result_query

    def _getCRChecklist(self,status="",sw=True):
        '''
        Get checklist according to CR status
        Return None if no CCB decision is needed
        '''

        result = []
        if status in self.dico_status_vs_transition:
            transition = self.dico_status_vs_transition[status]
            if sw:
                query = "SELECT check_item FROM cr_checklist WHERE transition LIKE '{:s}'".format(transition)
            else:
                query = "SELECT check_item FROM cr_pld_checklist WHERE transition LIKE '{:s}'".format(transition)
            result = self.sqlite_query(query)
        if result != []:
            return result
        else:
            return None

    def _getComponentCRType(self,component=""):
        '''
        Get CR type according to component
        Return None if no CR type found
        '''
        query = "SELECT cr_type,type FROM components \
                WHERE components.name LIKE '" + component + "'"
        result = self.sqlite_query(query)
        if result in (None,[]):
            cr_type = None
            domain = None
        else:
            cr_type = result[0][0]
            cr_domain = result[0][1]
        print ("CR_TYPE",cr_type)
        return cr_type,cr_domain

    def _getItemCRType(self,item="",system=""):
        '''
        Get CR type according to component
        Return None if no CR type found
        '''
        query = 'SELECT items.cr_type FROM items \
                LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id \
                LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id \
                WHERE systems.name LIKE \'' + system + '\' AND items.name LIKE \'' + item + '\'  ORDER BY items.name ASC'
        print ("_getItemCRType:",query)
        result = self.sqlite_query(query)
        if result in (None,[]):
            cr_type = None
        else:
            cr_type = result[0][0]
        return cr_type

    def _getCRType(self,item=""):
        '''
        Get CR type according to item
        Return None if no CR type found
        '''
        query = "SELECT cr_type FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + item + "' and systems.name LIKE '" + system + "'"
        result = self.sqlite_query(query)
        if result == None or result == []:
            cr_type = None
        else:
            cr_type = result[0][0]
        return cr_type
    #
    # SQLite
    #
    def get_image(self,item):
        '''
            Get image in SQLite database
            '''
        query = "SELECT img FROM systems WHERE aircraft LIKE '{:s}' LIMIT 1".format(item)
        result = self.sqlite_query_one(query)
        if result is None:
            image_name = "earhart12_240x116.gif"
        else:
            image_name = result[0]
        return image_name

    def get_database(self,name):
        query = "SELECT items.database,aircraft FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + name + "'"
        result = self.sqlite_query(query)
        if result != []:
            return result[0][0],result[0][1]
        else:
            return None,None

    def get_sys_item_database(self,system,item):
        query = "SELECT items.database,aircraft FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + item + "' and systems.name LIKE '" + system + "'"
##        print "TEST get_sys_item_database",query
        result = self.sqlite_query(query)
        if result != []:
            return result[0][0],result[0][1]
        else:
            return None,None

    def get_sys_database(self):
        if self.system != "":
            query = "SELECT systems.database,aircraft FROM systems WHERE systems.name LIKE '" + self.system + "'"
##            print "TEST get_sys_database",query
            result = self.sqlite_query(query)
            if result != []:
                return result[0][0],result[0][1]
            else:
                return None,None
        else:
            return None,None

    def get_user_infos(self,login):
        """
        Get name, mail and telephone according to login of the person logged
        :param login:
        :return: (name,mail,tel,service,qams_user_id)
        """
        default = ("Olivier Appere","olivier.appere@zodiacaerospace.com","0155825104","DQ",1)
        if login != "":
            query = "SELECT name,mail,tel,service,qams_user_id FROM writers WHERE login LIKE '{:s}'".format(login)
            result = self.sqlite_query(query)
            if result in (None,[]):
                infos = default
                print ("No match in SQLite database, default author's name used.")
            else:
                infos = result[0]
        else:
            infos = default
            print ("Login empty, default author's name used.")
        return infos

    def get_writers_vs_systems(self,system):
        query = "SELECT writers.name FROM writers " \
                "LEFT OUTER JOIN link_writers_systems ON link_writers_systems.writer_id = writers.id " \
                "LEFT OUTER JOIN systems ON link_writers_systems.system_id = systems.id " \
                "WHERE systems.name LIKE '{:s}'".format(system)
        #print "get_writers_vs_systems",query
        result = self.sqlite_query(query)
        if result in (None,[]):
            infos = False
        else:
            infos = result
        return infos

    @staticmethod
    def get_source_code_version(src_code_name):
        source_code_version = False
        try:
            with open(src_code_name, 'r') as source_code_file:
                for line in source_code_file:
                    #print line
                    m = re.search(r'%version: ?([0-9\.]*) ?%',line)
                    if m:
                        source_code_version = m.group(1)
                        #print ("found version",source_code_version)
                        break
        except IOError as e:
            source_code_version = "No such file"
            print (e)
        return source_code_version

    def get_ci_identification(self,item):
        if item != "":
            query = "SELECT ci_identification FROM items WHERE items.name LIKE '" + item + "'"
            result = self.sqlite_query(query)
            if result == None or result == []:
                ci_id = "None"
            else:
                ci_id = result[0][0]
        else:
            ci_id = "None"
        return ci_id

    def get_ci_sys_item_identification(self,system,item):
        query = "SELECT ci_identification FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + item + "' and systems.name LIKE '" + system + "'"
        result = self.sqlite_query(query)
        if result == None or result == []:
            ci_id = "None"
        else:
            ci_id = result[0][0]
        return ci_id

    def get_sys_item_old_workflow(self,system,item):
        query = "SELECT old_workflow FROM items \
        LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id  \
        LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id WHERE items.name LIKE '" + item + "' and systems.name LIKE '" + system + "'"
        result = self.sqlite_query(query)
        if result in (None,[]):
            old_workflow = False
        else:
            if result[0][0] == 1:
                old_workflow = True
            else:
                old_workflow = False
        return old_workflow
    def get_ear(self,item):
        if item not in  ("","None"):
            query = "SELECT ear FROM items LEFT OUTER JOIN link_systems_items ON item_id = items.id LEFT OUTER JOIN systems ON systems.id = system_id WHERE items.name LIKE '" + item + "'"
            result = self.sqlite_query(query)
            if result == None:
                ear = ""
            else:
                ear = result[0][0]
        else:
            ear = ""
        return ear
    def get_lastquery(self):
        query = 'SELECT database,item,project,release FROM last_query WHERE id = 1'
        item = self.sqlite_query(query)
        item = cur.fetchall()
        return item

    def sqlite_save_projects(self,projects_set,config_id=1):
        print ("sqlite_save_projects",projects_set)
        try:
            con = lite.connect('docid.db3')
            cur = con.cursor()
            #cur.execute("DROP TABLE IF EXISTS gen_save")
            cur.execute("DELETE FROM gen_save WHERE conf_id LIKE '%{:d}%'".format(config_id))
            cur.execute("CREATE TABLE IF NOT EXISTS gen_save(conf_id NUMERIC, release TEXT, baseline TEXT, project TEXT)")
            cur.executemany("INSERT INTO gen_save VALUES(?, ?, ?, ?)", projects_set)
            con.commit()
##            print time.strftime("%H:%M:%S", time.localtime()) + " Generation set saved."
        except lite.Error as e:
            print ("Error %s:" % e.args[0])
            sys.exit(1)
        finally:
            if con:
                con.close()

    def sqlite_restore_projects(self,config_id=1):
        """
        Restore release,baseline and project list
        :param config_id:
        :return:
        """
        query = "SELECT release,baseline,project FROM gen_save WHERE conf_id LIKE '{:d}'".format(config_id)
        print ("QUERY",query)
        result = self.sqlite_query(query)
        print ("RESULT",result)
        return result

    def sqlite_save_parameters(self,data,dico,config_id=1):
        print ("DATA",data)
        try:
            con = lite.connect('docid.db3')
            cur = con.cursor()
            #cur.execute("DROP TABLE IF EXISTS parameters")
            cur.execute("CREATE TABLE IF NOT EXISTS parameters(author TEXT, reference TEXT, issue TEXT, pn TEXT, board_pn TEXT, checksum TEXT, dal TEXT, previous_bas TEXT, release TEXT, baseline TEXT, project TEXT, detect TEXT, implemented TEXT, item TEXT, component TEXT, system TEXT, cr_type TEXT, cr_domain TEXT,conf_id NUMERIC)")
            cur.execute("SELECT * FROM parameters WHERE conf_id LIKE '{:d}' LIMIT 1".format(config_id))
            row_exist = cur.fetchone()
            if row_exist is not None:
                update_data = data
                update_data.append(config_id)
                param = tuple(update_data)
                print ("PARAM",param)
                # parameterized queries
                #This format is more robust but require a dictionary !
                parameterized_query = "UPDATE parameters SET author=:author, reference=:reference, issue=:issue, pn=:pn, board_pn=:board_pn, " \
                                       "checksum=:checksum, dal=:dal,  previous_bas=:previous_bas, release=:release, baseline=:baseline," \
                                       "project=:project, detect=:detect, implemented=:implemented, item=:item, component=:component, system=:system, cr_type=:cr_type , cr_domain=:cr_domain WHERE conf_id=:conf_id"
                print ("DICO",dico)
                dico["conf_id"]=config_id
                print ("UPDATE QUERY",parameterized_query)
                # cur.execute(parameterized_query, dico)

                # Marche pas avec le tuple
                parameterized_query = "UPDATE parameters SET author=?, reference=?, issue=?, pn=?, board_pn=?, " \
                                      "checksum=?, dal=?,  previous_bas=?, release=?, baseline=?," \
                                      "project=?, detect=?, implemented=?, item=?, component=?, system=?, cr_type=?, cr_domain=? WHERE conf_id=?"

                print ("UPDATE QUERY",parameterized_query)
                cur.execute(parameterized_query, param)
                #cur.execute("UPDATE parameters SET database=?,reference=?,revision=?,project=?,release=?,baseline=?,input_date=? WHERE id= ?",(self.database,self.reference,self.revision,project,release,baseline,now,id))
            else:
##                print "Insert new row in SQLite database"
                #cur.execute("INSERT INTO last_query(database,reference,revision,project,item,release,baseline,input_date) VALUES(?,?,?,?,?,?,?,?)",(self.database,self.reference,self.revision,project,item,release,baseline,now))
                insert_data = [config_id]
                insert_data.extend(data)
                cur.executemany("INSERT INTO parameters VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [insert_data])
            con.commit()
##            print time.strftime("%H:%M:%S", time.localtime()) + " Generation set saved."
        except lite.Error as e:
            print ("Error %s:" % e.args[0])
            sys.exit(1)
        finally:
            if con:
                con.close()

    def sqlite_restore_parameters(self,config_id=1):
        def convert_values(x):
            y="{:s}".format(x)
            return y
        query = "SELECT author, reference, issue, pn, board_pn, checksum, dal,  previous_bas, release, baseline, project, detect, implemented, item, component, system, cr_type, cr_domain FROM parameters WHERE conf_id = '{:d}'".format(config_id)
        print ("QUERY",query)
        result = self.sqlite_query(query)
        print ("RESULT",result)
        if result not in (None,[]):
            print ("RESULT sqlite_restore_parameters",result)
            values = result[0]
            print ("BEFORE",values)
            #values = map(convert_values,values)
        else:
            values = False
        return values

    def sqlite_create(self):
        try:
            con = lite.connect('docid.db3')
            cur = con.cursor()
            cur.executescript("""
                                BEGIN TRANSACTION;
                                CREATE TABLE components (id INTEGER PRIMARY KEY, description TEXT, ci_id TEXT, cr_type TEXT, name TEXT);
                                INSERT INTO components VALUES(1,'Electric Network Management','A338','SW_ENM','ENM');
                                INSERT INTO components VALUES(2,'Monitoring and communication','A326','SW_BITE','BITE');
                                INSERT INTO components VALUES(3,'Whindshield Deicing Control and Contactor','A331','SW_WHCC','WHCC');
                                INSERT INTO components VALUES(4,'PLD SDS IO','A325','PLD_SDSIO','SDSIO');
                                INSERT INTO components VALUES(5,'PLD TIE','A415','PLD_TIE','TIE');
                                INSERT INTO components VALUES(6,'Ethernet communication','A330','SW_COM','COM');
                                INSERT INTO components VALUES(7,'Plans',NULL,'SW_PLAN','PLAN');
                                CREATE TABLE cr_checklist (check_item TEXT, transition TEXT);
                                INSERT INTO cr_checklist VALUES('decide if postponed CR shall be corrected on planned release','From Postponed');
                                INSERT INTO cr_checklist VALUES('check that defect/evolution is understandable (description, problem condition, ...)
                                ','To Under Modification');
                                INSERT INTO cr_checklist VALUES('check CR field coherency with SCMP process','To Under Modification');
                                INSERT INTO cr_checklist VALUES('discuss and validate classification in case of Defect','To Under Modification');
                                INSERT INTO cr_checklist VALUES('approve corrective action and impact analysis','To Under Modification');
                                INSERT INTO cr_checklist VALUES('schedule correction release','To Under Modification');
                                INSERT INTO cr_checklist VALUES('check CR field coherency with SCMP process','From Fixed');
                                INSERT INTO cr_checklist VALUES('confirm that performed activities (development and verification) are complete and consistent','From Fixed');
                                CREATE TABLE cr_pld_checklist (field1, field2);
                                INSERT INTO cr_pld_checklist VALUES('check_item','transition');
                                INSERT INTO cr_pld_checklist VALUES('decide if postponed CR shall be corrected on planned release','From Postponed');
                                INSERT INTO cr_pld_checklist VALUES('check that defect/evolution is understandable (description, problem condition, ...)
                                ','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('check CR field coherency with configuration management process','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('discuss and validate classification','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('approve corrective action and impact analysis','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('schedule ?CR implemented for? correction','To Under Modification');
                                INSERT INTO cr_pld_checklist VALUES('check CR field coherency with configuration management process
                                -?Under_modification? reviewed and approved
                                -?Under_verification? reviewed and approved','From Fixed');
                                INSERT INTO cr_pld_checklist VALUES('confirm that performed activities (development and verification) are complete and consistent','From Fixed');
                                CREATE TABLE document_types (description TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO document_types VALUES('Hardware Confguration Management Record',1,'HCMR');
                                INSERT INTO document_types VALUES('Software Configuration Index',2,'SCI');
                                INSERT INTO document_types VALUES('Configuration Index Document',3,'CID');
                                INSERT INTO document_types VALUES('Software Quality Assurance Plan',4,'SQAP');
                                INSERT INTO document_types VALUES('Plan for Software Aspects of Certification',5,'PSAC');
                                INSERT INTO document_types VALUES('Software Development Plan',6,'SDP');
                                INSERT INTO document_types VALUES('Software Verification Plan',7,'SVP');
                                INSERT INTO document_types VALUES('Software Configuration Management Plan',8,'SCMP');
                                CREATE TABLE documents (status_id NUMERIC, reference TEXT, last_revision TEXT, id INTEGER PRIMARY KEY, item_id NUMERIC, type NUMERIC);
                                INSERT INTO documents VALUES(41,'PQ 0.1.0.160',NULL,1,'',4);
                                INSERT INTO documents VALUES(41,'PQ 0.1.0.155',NULL,2,5,4);
                                INSERT INTO documents VALUES(45,'PQ 0.1.0.163',1.2,3,1,4);
                                INSERT INTO documents VALUES(41,'PQ 0.1.0.169',NULL,4,15,4);
                                INSERT INTO documents VALUES(45,'ET3335-E',NULL,5,1,6);
                                INSERT INTO documents VALUES(45,'ET3337-E',NULL,6,1,8);
                                INSERT INTO documents VALUES(45,'ET3334-E',NULL,7,1,5);
                                INSERT INTO documents VALUES(45,'ET3336-E',NULL,8,1,7);
                                CREATE TABLE gen_save(release TEXT, baseline TEXT, project TEXT);
                                INSERT INTO gen_save VALUES('SW_PLAN/01','SW_PLAN_01_07','SW_PLAN-1.7');
                                INSERT INTO gen_save VALUES('SW_PLAN_PDS_SDS/01','SW_PLAN_PDS_SDS_01_03','SW_PLAN_PDS_SDS-1.3');
                                INSERT INTO gen_save VALUES('SW_ENM/01','SW_ENM_01_06','SW_ENM-1.6');
                                INSERT INTO gen_save VALUES('SW_ENM/01','SW_ENM_01_06','CODE_SW_ENM-1.6');
                                INSERT INTO gen_save VALUES('SW_ENM_DELIV/01','SW_ENM_DELIV_01_02','SW_ENM_DELIV-1.2');
                                CREATE TABLE history (writer_id NUMERIC, date TEXT, issue TEXT, document_id NUMERIC, id INTEGER PRIMARY KEY, modifications TEXT);
                                CREATE TABLE items (cr_type TEXT, old_workflow NUMERIC, ci_identification TEXT, database TEXT, description TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO items VALUES(NULL,NULL,'A333','db_g7000_ppds','AC logic board',1,'ACLOG');
                                INSERT INTO items VALUES(NULL,NULL,'A334','db_g7000_ppds','DC logic board',2,'DCLOG');
                                INSERT INTO items VALUES(NULL,NULL,NULL,'db_g7000_ppds','Electrical Distribution Management Unit',3,'EDMU');
                                INSERT INTO items VALUES(NULL,NULL,'A335','db_g7000_ppds','EMERgency LOGic board',4,'EMERLOG');
                                INSERT INTO items VALUES('ESSNESS',NULL,'A338','db_sms_pds','ESSential Non ESSential board',5,'ESSNESS');
                                INSERT INTO items VALUES('TIE',NULL,NULL,'db_sms_pds','TIE board',6,'TIE');
                                INSERT INTO items VALUES('SDSIO',NULL,'A330','db_sms_pds','Secondary Distribution System Input Output',7,'SDSIO');
                                INSERT INTO items VALUES(NULL,1,'A267','db_787','Electrical Load Control Unit - Protection',8,'ELCU_P');
                                INSERT INTO items VALUES(NULL,NULL,NULL,NULL,'Electrical Load Control Unit - Command',9,'ELCU_C');
                                INSERT INTO items VALUES(NULL,1,'A295','db_a350_enmu','Electrical Network Management Unit',10,'ENMU');
                                INSERT INTO items VALUES(NULL,1,'A297','db_a350_rccb','Remote Control Circuit Breaker',11,'RCCB');
                                INSERT INTO items VALUES(NULL,1,'A304','db_egp','Windshield Wiper Electronic Unit',12,'WECU');
                                INSERT INTO items VALUES(NULL,NULL,NULL,'db_sms_ocp','Overhead Cockpit Panel',13,'ARINC');
                                INSERT INTO items VALUES('WHCC',NULL,'A331','db_sms_pds','Windshield Heater Control Command',15,'WHCC');
                                INSERT INTO items VALUES(NULL,1,'A320','db_cseries_cpdd','Circuit Protection Device Detector',16,'CPDD');
                                INSERT INTO items VALUES(NULL,NULL,'A417','db_mc21_ppds','Electrical Network Management Unit',17,'ENMU');
                                CREATE TABLE last_query (id INTEGER PRIMARY KEY, reference TEXT, revision TEXT ,database TEXT, project TEXT, item TEXT, release TEXT, baseline TEXT, input_date timestamp);
                                INSERT INTO last_query VALUES(51,'','','db_sms_pds','','ESSNESS','SW_ENM/02','','2014-05-21 10:30:13.425000');
                                INSERT INTO last_query VALUES(53,'ET3142-E','1D2','db_sms_pds','All','','SW_ENM/02','SW_ENM_02_04','2014-05-13 15:44:49.471000');
                                INSERT INTO last_query VALUES(55,'','','db_sms_pds','','SDSIO','SW_ENM/02','','2014-05-19 15:22:05.019000');
                                INSERT INTO last_query VALUES(56,'','','db_sms_pds','','WHCC','SW_ENM/02','','2014-05-19 15:36:35.260000');
                                CREATE TABLE link_items_components (component_id NUMERIC, id INTEGER PRIMARY KEY, item_id NUMERIC);
                                INSERT INTO link_items_components VALUES(1,1,5);
                                INSERT INTO link_items_components VALUES(2,2,5);
                                INSERT INTO link_items_components VALUES(3,3,15);
                                INSERT INTO link_items_components VALUES(4,4,7);
                                INSERT INTO link_items_components VALUES(5,5,6);
                                INSERT INTO link_items_components VALUES(6,6,7);
                                INSERT INTO link_items_components VALUES(2,7,7);
                                INSERT INTO link_items_components VALUES(7,8,5);
                                INSERT INTO link_items_components VALUES(7,9,6);
                                INSERT INTO link_items_components VALUES(7,10,7);
                                INSERT INTO link_items_components VALUES(7,11,15);
                                CREATE TABLE link_std_pn (id NUMERIC, pn_id NUMERIC, std_id NUMERIC);
                                CREATE TABLE link_systems_items (id INTEGER PRIMARY KEY, item_id NUMERIC, system_id NUMERIC);
                                INSERT INTO link_systems_items VALUES(1,1,3);
                                INSERT INTO link_systems_items VALUES(2,2,3);
                                INSERT INTO link_systems_items VALUES(3,3,3);
                                INSERT INTO link_systems_items VALUES(4,4,3);
                                INSERT INTO link_systems_items VALUES(5,5,2);
                                INSERT INTO link_systems_items VALUES(6,6,2);
                                INSERT INTO link_systems_items VALUES(7,7,11);
                                INSERT INTO link_systems_items VALUES(8,8,1);
                                INSERT INTO link_systems_items VALUES(9,9,1);
                                INSERT INTO link_systems_items VALUES(10,10,4);
                                INSERT INTO link_systems_items VALUES(11,11,4);
                                INSERT INTO link_systems_items VALUES(12,12,5);
                                INSERT INTO link_systems_items VALUES(13,13,6);
                                INSERT INTO link_systems_items VALUES(14,15,8);
                                INSERT INTO link_systems_items VALUES(15,16,9);
                                INSERT INTO link_systems_items VALUES(16,17,12);
                                CREATE TABLE part_number (id NUMERIC, name TEXT);
                                CREATE TABLE review_types (description TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO review_types VALUES('Software Plan Review',1,'PR');
                                INSERT INTO review_types VALUES('Software Requirement Review',2,'SRR');
                                INSERT INTO review_types VALUES('Software Design Review',3,'SDR');
                                INSERT INTO review_types VALUES('Software COde Review',4,'SCOR');
                                INSERT INTO review_types VALUES('High Level Test Readiness Review',5,'HL-TRR');
                                INSERT INTO review_types VALUES('Low Level Test Readiness Review',6,'LL-TRR');
                                INSERT INTO review_types VALUES('High Level Test Review',7,'HL-TR');
                                INSERT INTO review_types VALUES('Low Level Test Review',8,'LL-TR');
                                INSERT INTO review_types VALUES('Software Conformity Review',9,'SCR');
                                CREATE TABLE standards (id NUMERIC, name TEXT);
                                CREATE TABLE status (description TEXT, id INTEGER PRIMARY KEY, name TEXT, transition TEXT, type TEXT);
                                INSERT INTO status VALUES('peer data review has been performed and has been taken into account.',10,'Reviewed',0,'data');
                                INSERT INTO status VALUES('No peer data review has been performed yet.',11,'New',0,'data');
                                INSERT INTO status VALUES('review successfully passed',17,'Accepted',0,'review');
                                INSERT INTO status VALUES('Document has been signed AQ',45,'Approved',0,'data');
                                CREATE TABLE status_id (description TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO status_id VALUES('Not created.',1,'None');
                                CREATE TABLE systems (database TEXT, ear TEXT, img TEXT, aircraft TEXT, id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO systems VALUES('db_787',NULL,'B787.gif','B787',1,'Boeing B787 PPDS');
                                INSERT INTO systems VALUES('db_sms_pds',NULL,'SMS.gif','F5X',2,'Dassault F5X PDS');
                                INSERT INTO systems VALUES('db_g7000_ppds','EAR
                                Information contained herein is subject to the export administration regulations (EAR) of the united states of America and export classified under those regulations as (ECCN: 9E991). No portion of this document can be re-exported from the recipient country or re-transferred or disclosed to any other entity or person not authorized to receive it without the prior authorization of ECE.
                                ','G7000.gif','G7000',3,'Bombardier G7000 PPDS');
                                INSERT INTO systems VALUES('db_a350_xwb',NULL,'A350.gif','A350',4,'Airbus A350 EPDS');
                                INSERT INTO systems VALUES('db_egp',NULL,'A350.gif','A350',5,'Airbus A350 WWS');
                                INSERT INTO systems VALUES(NULL,NULL,'SMS.gif','F5X',6,'Dassault F5X OCP');
                                INSERT INTO systems VALUES('db_sms_pds',NULL,'SMS.gif','F5X',8,'Dassault F5X WDS');
                                INSERT INTO systems VALUES('db_cseries_cpdd',NULL,'CSERIES.gif','Cseries',9,'Bombardier CSeries EPC');
                                INSERT INTO systems VALUES('db_tools',NULL,'TOOL.gif','All',10,'Tools');
                                INSERT INTO systems VALUES('db_sms_pds',NULL,'SMS.gif','F5X',11,'Dassault F5X SDS');
                                INSERT INTO systems VALUES('db_mc21_ppds',NULL,'MC21.gif','MC21',12,'Irkut MC21 PPDS');
                                CREATE TABLE writers (id INTEGER PRIMARY KEY, name TEXT);
                                INSERT INTO writers VALUES(1,'O. APPERE');
                                INSERT INTO writers VALUES(2,'F. CLOCHET');
                                COMMIT;
                """)
            con.commit()
            print ('New SQLite database created.')
        except lite.Error as e:
            print ("Error %s:" % e.args[0])
            sys.exit(1)
        finally:
            if con:
                con.close()

    def storeSelection(self,project,item,release,baseline):
        '''
        Store selection in SQLite database
         -project
         -release
         -baseline
        '''
        con = False
        try:
            now = datetime.now()
            con = lite.connect('docid.db3', isolation_level=None)
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS last_query (id INTEGER PRIMARY KEY, reference TEXT, revision TEXT ,database TEXT, project TEXT, item TEXT, release TEXT, baseline TEXT, input_date timestamp)")
            cur.execute("SELECT id FROM last_query WHERE item LIKE '" + item + "' LIMIT 1")
##            print "SELECT id FROM last_query WHERE item LIKE '" + item + "' LIMIT 1"
            data = cur.fetchone()
            if data is not None:
                id = data[0]
##                print "Update row in SQLite database"
                cur.execute("UPDATE last_query SET database=?,reference=?,revision=?,project=?,release=?,baseline=?,input_date=? WHERE id= ?",(self.database,self.reference,self.revision,project,release,baseline,now,id))
            else:
##                print "Insert new row in SQLite database"
                cur.execute("INSERT INTO last_query(database,reference,revision,project,item,release,baseline,input_date) VALUES(?,?,?,?,?,?,?,?)",(self.database,self.reference,self.revision,project,item,release,baseline,now))
            # Keep only the 4 last input
            cur.execute("DELETE FROM last_query WHERE id NOT IN ( SELECT id FROM ( SELECT id FROM last_query ORDER BY input_date DESC LIMIT 4) x )")
            lid = cur.lastrowid
        except lite.Error as e:
            print ("Error %s:" % e.args[0])
        finally:
            if con:
                con.close()

    @staticmethod
    def getConfigList(database = 'docid.db3',id=""):
        if id == "":
            query = "SELECT id,name FROM config"
            result = Tool.sqlite_query(query,database)
        else:
            query = "SELECT name FROM config WHERE id LIKE '{:d}'".format(id)
            result = Tool.sqlite_query_one(query,database)
        if result is None:
            config_list = "None"
        else:
            config_list = result
        return config_list

    @staticmethod
    def setConfig(database = 'docid.db3',id="",txt=""):
        result = False
        if id != "":
            try:
                con = lite.connect(database, isolation_level=None)
                cur = con.cursor()
                cur.execute("UPDATE config SET name=? WHERE id= ?",(txt,str(id)))
            except lite.Error as e:
                print ("Error %s:" % e.args[0])
                sys.exit(1)
            finally:
                if con:
                    con.close()
        return result

    def sqlite_query(query,database='docid.db3'):
        try:
            con = lite.connect(database)
            cur = con.cursor()
            cur.execute(query)
            result = cur.fetchall()
            if con:
                con.close()
        except lite.Error as e:
            print ("Error %s:" % e.args[0])
            result = None
            con = False
        finally:
            if con:
                con.close()
        return result

    def sqlite_query_one(query,database='docid.db3'):
        try:
            con = lite.connect(database)
            cur = con.cursor()
            cur.execute(query)
##            print time.strftime("%H:%M:%S", time.localtime()) + " " + query
            result = cur.fetchone()
            if con:
                con.close()
        except lite.Error as e:
            print ("Error %s:" % e.args[0])
            result = None
        #finally:
        #    if con:
        #        con.close()
        return result

    # Apache
    def apache_start(self,config="httpd_home.conf"):
        # read config file
        #config_parser = ConfigParser()
        #config_parser.read('docid.ini')
        httpd_dir = self.config_parser.get("Apache","httpd_dir")
        conf_dir = self.config_parser.get("Apache","conf_dir")
        mysql_dir = self.config_parser.get("Apache","mysql_dir")
        config = conf_dir + config
        # hide commmand DOS windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        # default config
        print (time.strftime("%H:%M:%S", time.localtime()) + " httpd.exe -f " + config)
        proc_httpd = subprocess.Popen(httpd_dir + "httpd.exe -f " + config, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
        print (time.strftime("%H:%M:%S", time.localtime()) + " mysqld --defaults-file=mysql\\bin\\my.ini --standalone --console")
        proc_mysql = subprocess.Popen(mysql_dir + "mysqld --defaults-file=mysql\\bin\\my.ini --standalone --console", stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
        stdout_httpd, stderr_httpd = proc_httpd.communicate()
        stdout_mysql, stderr_mysql = proc_mysql.communicate()
        ##    print time.strftime("%H:%M:%S", time.localtime()) + " " + stdout
        if stderr_httpd:
            print ("Error while executing httpd command: " + stderr_httpd)
        elif stderr_mysql:
            print ("Error while executing mysql command: " + stderr_mysql)
        time.sleep(1)
        return_code_httpd = proc_httpd.wait()
        return_code_mysql = proc_mysql.wait()
        print (stdout_httpd)
        print (stdout_mysql())

    #Srecord
    def srec_to_intelhex(self,filename,output):
        '''
        Invoke srec_cat command
        '''
        stdout = ""
        stderr = ""
        # hide commmand DOS windows
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        except AttributeError:
            warnings.warn("ccm_query works on Windows only.")
            return "",""
        try:
            #name = Tool.getFileName(filename)
            print ("bin\\srec_cat {:s} -o result\\{:s}.hex -intel".format(filename,output))
            proc = subprocess.Popen("bin\\srec_cat {:s} -o result\\{:s}.hex -intel".format(filename,output),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    startupinfo=startupinfo)
            stdout, stderr = proc.communicate()
            if stderr:
                print ("Error while executing srec_cat command: " + stderr)
            time.sleep(1)
            return_code = proc.wait()
        except UnicodeEncodeError as exception:
            print ("Character not supported:", exception)
            stderr = "Character not supported: {:s}".format(exception)
        except WindowsError as exception:
            print ("Wrong path for srec_cat:", exception)
            stderr = "Wrong path for srec_cat"
        return stdout,stderr

    # Synergy
    def ccm_query(self,query,cmd_name):
        '''
        Invoke ccm command
        '''
        stdout = ""
        stderr = ""
        # hide commmand DOS windows
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        except AttributeError:
            warnings.warn("ccm_query works on Windows only.")
            return "",""
        try:
            proc = subprocess.Popen(self.ccm_exe + " " + query, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
            stdout, stderr = proc.communicate()
            if stderr:
                print ("Error while executing " + cmd_name + " command: " + stderr)
            time.sleep(1)
            return_code = proc.wait()
        except UnicodeEncodeError as exception:
            print ("Character not supported:", exception)
            stderr = "Character not supported: {:s}".format(exception)
        except WindowsError as exception:
            print ("Wrong path for ccm.exe:", exception)
            stderr = "Wrong path for ccm.exe"
        return stdout,stderr

    # MySQL
##    def mysql_query(self,query,cmd_name):
##        '''
##        Invoke mysql command
##        '''
##        stdout = ""
##        stderr = ""
##        # hide commmand DOS windows
##        try:
##            startupinfo = subprocess.STARTUPINFO()
##            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
####            startupinfo.wShowWindow = subprocess.SW_HIDE
##        except AttributeError:
##            print "mysql_query works on Windows only so far."
##            return "",""
##        try:
##            print self.mysql_exe + " " + query
##            proc = subprocess.Popen(self.mysql_exe + " " + query, stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=startupinfo)
##            stdout, stderr = proc.communicate()
##            print "STDOUT",stdout
##            if stderr:
##                print "Error while executing " + cmd_name + " command: " + stderr
##            time.sleep(1)
##            return_code = proc.wait()
##        except UnicodeEncodeError as exception:
##            print "Character not supported:", exception
##        return stdout,stderr
    # srts_rules.db3

    # docid.db3
    def retrieveLastSelection(self,item):
        data = []
        try:
            data = self.sqlite_query("SELECT * FROM last_query WHERE item LIKE '" + item + "' LIMIT 1")
            if data == []:
                data = self.sqlite_query("SELECT * FROM last_query ORDER BY input_date DESC LIMIT 1")
        except:
            pass
        return data

    def getSystemName(self,item=""):
        if item != "":
            query = "SELECT systems.name FROM systems \
                        LEFT OUTER JOIN linkze_systems_items ON link_systems_items.system_id = systems.id \
                        LEFT OUTER JOIN items ON items.id = link_systems_items.item_id \
                        WHERE items.name LIKE '{:s}'".format(item)
            result = self.sqlite_query_one(query)
            if result is None:
                description = "None"
            else:
                description = result[0]
        else:
            query = "SELECT systems.name FROM systems"
            result = Tool.sqlite_query(query)
            if result is not None:
                description = result
            else:
                description = False
        return description

    def getListItems(self,system=""):
        if system != "":
            query = 'SELECT items.name,items.id FROM items ' \
                    'LEFT OUTER JOIN link_systems_items ON items.id = link_systems_items.item_id ' \
                    'LEFT OUTER JOIN systems ON systems.id = link_systems_items.system_id ' \
                    'WHERE systems.name LIKE \'' + system + '\' ORDER BY items.name ASC'
        else:
            query = 'SELECT items.name,items.id FROM items '
        result = Tool.sqlite_query(query)
        if result is not None:
            description = result
        else:
            description = False
        return query

    def getItemID(self,table="systems",name=""):
        query = "SELECT id FROM {:s} WHERE name LIKE '{:s}'".format(table,name)
        result = self.sqlite_query_one(query)
        if result is None:
            id = None
        else:
            id = result[0]
        return id

    def getItemDescription(self,item):
        query = "SELECT description FROM items WHERE name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result is None:
            description = item
        else:
            if result[0] is None:
                description = ""
            else:
                description = result[0]
        return description

    def getItemPartNumber(self,item):
        query = "SELECT ci_identification FROM items WHERE name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result is None:
            description = item
        else:
            if result[0] is None:
                description = ""
            else:
                description = result[0]
        return description

    def getComponentDescription(self,item):
        query = "SELECT description FROM components WHERE name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result == None:
            description = item
        else:
            if result[0] == None:
                description = ""
            else:
                description = result[0]
        return description

    def getComponentPartNumber(self,component):
        query = "SELECT ci_id FROM components WHERE name LIKE '{:s}'".format(component)
        result = self.sqlite_query_one(query)
        if result is None:
            description = component
        else:
            if result[0] is None:
                description = ""
            else:
                description = result[0]
        return description

    def getComponentBoardPartNumber(self,component):
        query = "SELECT items.ci_identification FROM items " \
                "LEFT OUTER JOIN link_items_components ON items.id = link_items_components.item_id " \
                "LEFT OUTER JOIN components ON components.id = link_items_components.component_id " \
                "WHERE components.name LIKE '{:s}'".format(component)
        #print "QUERY:",query
        result = self.sqlite_query_one(query)
        if result is None:
            description = "UNKNOWN"
        else:
            if result[0] is None:
                description = ""
            else:
                description = result[0]
        return description

    @staticmethod
    def getComponentAllocation(item):
        # Remove blank space before and after keyword
        item_wo_blank = re.sub(r"^\s*(.*[A-Z])\s*$", r"\1",item)
        query = "SELECT cr_type FROM components WHERE allocation_name LIKE '%{:s}%'".format(item_wo_blank)
        result = Tool.sqlite_query_one(query)
        if result is None:
            cr_type = item
        else:
            if result[0] == None:
                cr_type = ""
            else:
                cr_type = result[0]
        return cr_type

    @staticmethod
    def removeBlankSpace(txt):
        # Remove blank space before and after keyword
        if txt is not None:
            if type(txt) in (str,unicode):
                #print ":{:s}:".format(txt)
                txt_wo_blank = str(re.sub(r"^\s*([\w\._]*)\s*$", r"\1",txt))
                #print ":{:s}:".format(txt_wo_blank)
            else:
                #if type(txt) is float:
                #print type(txt)
                txt_wo_blank = str(txt)
        else:
            #print "problem removeBlankSpace",txt
            txt_wo_blank = "None"
        return txt_wo_blank

    @staticmethod
    def getAllocationComponent(item=""):
        if item != "":
            # Remove blank space before and after keyword
            item_wo_blank = re.sub(r"^\s*(.*[A-Z])\s*$", r"\1",item)
            query = "SELECT allocation_name FROM components WHERE cr_type LIKE '%{:s}%'".format(item_wo_blank)
        else:
            query = "SELECT allocation_name FROM components"
        result = Tool.sqlite_query(query)
        if result is not None:
            return result
        else:
            return False

    def getComponentID(self,item):
        if not self._is_array(item):
            query = "SELECT ci_id FROM components WHERE name LIKE '%{:s}%'".format(item)
            print ("getComponentID",query)
            result = self.sqlite_query_one(query)
        else:
            result = None
        if result == None:
            ci_id = "None"
        else:
            if result[0] == None:
                ci_id = "None"
            else:
                ci_id = result[0]
        return ci_id

    def getListModifs(self,item):
        query = "SELECT issue,date,modifications,writers.name FROM history LEFT OUTER JOIN documents ON documents.id = document_id LEFT OUTER JOIN items ON items.id = documents.item_id LEFT OUTER JOIN writers ON writers.id = history.writer_id WHERE items.name LIKE '{:s}'".format(item)
        result = self.sqlite_query(query)
        if result == None:
            history = "None"
        else:
            history = result
        return history

    def getLastModificationLog(self,item):
        if item != "" and item != "None":
            query = "SELECT modifications FROM history LEFT OUTER JOIN documents ON documents.id = history.document_id WHERE documents.reference LIKE '{:s}' ORDER BY date DESC LIMIT 1".format(item)
            result = self.sqlite_query(query)
            if result == None:
                modif = "None"
            else:
                modif = result[0]
        else:
            modif = "None"
        return modif

    def updateLastModificationLog(self):
        now = datetime.datetime.now()
        con = lite.connect('docid.db3', isolation_level=None)
        cur = con.cursor()
        cur.execute("SELECT history.id FROM history LEFT OUTER JOIN documents ON documents.id = history.document_id WHERE reference LIKE '" + self.reference + "' AND issue LIKE '" + self.revision + "' LIMIT 1")
        data = cur.fetchone()
        if data != None:
            id = data[0]
            cur.execute("UPDATE history SET date=?,writer_id=?,modifications=? WHERE id= ?",(now,1,interface.modif_log.get(1.0,END),id))
        else:
            cur.execute("INSERT INTO history(document_id,issue,writer_id,date,modifications) VALUES(?,?,?,?,?)",(3,self.revision,1,now,interface.modif_log.get(1.0,END)))

    def getTypeDocDescription(self,item):
        query = "SELECT description FROM document_types WHERE name LIKE '{:s}'".format(item)
        #print "QUERY",query
        result = self.sqlite_query_one(query)
        if result == None:
            description = "None"
        else:
            description = result[0]
        return description

    def getDocRef(self,item,type):
        query = "SELECT reference,document_types.description FROM documents LEFT OUTER JOIN items ON items.id = documents.item_id LEFT OUTER JOIN document_types ON document_types.id = documents.type WHERE document_types.name LIKE '"+ type +"' AND items.name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result != None:
            description = result[0] + " " + result[1]
        else:
            description = ""
        return description

    def getDocInfo(self,item):
        '''
            Get information on the document
            - reference allocated to the document according to the project
            - revision: last revision known
            '''
        query = "SELECT reference,last_revision,status.name FROM documents LEFT OUTER JOIN items ON items.id = documents.item_id LEFT OUTER JOIN status ON status.id = documents.status_id WHERE items.name LIKE '{:s}'".format(item)
        result = self.sqlite_query_one(query)
        if result == None:
            reference = "None"
            revision = "1.0"
            status = "None"
        else:
            if result[0] != None:
                reference = result[0]
            else:
                reference = "None"
            if result[1] != None:
                try:
                    revision = int(result[1])
                except ValueError:
                    revision = float(result[1]) + 0.1
            else:
                revision = 1.0
            if result[2] != None:
                status = result[2]
            else:
                status = "None"
        return reference,revision,status

    def getUsersList(self,id=""):
        if id == "":
            query = "SELECT name FROM writers"
        else:
            query = "SELECT name FROM writers WHERE id = '{:d}'".format(id)
        result = self.sqlite_query(query)
        if result is None:
            list = "None"
        else:
            list = result
        return list

    def updateRevision(self,reference,revision):
        '''
            '''
        pass

    @staticmethod
    def getProjectInfo(project):
        """
        From Synergy project object get name and version
        :param project:
        :return:
        """
        m = re.match(r'(.*)-(.*)',project)
        if m:
            name = m.group(1)
            version = m.group(2)
        else:
            name = project
            version = "*"
        return name,version

    def up_event(self, event,listbox):
        index = listbox.index("active")
        if listbox.selection_includes(index):
            index = index - 1
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
    def on_select(self, event):
        pass
    def select(self,index,listbox):
        listbox.focus_set()
        listbox.activate(index)
        listbox.selection_clear(0, "end")
        listbox.selection_set(index)
        listbox.see(index)

    @staticmethod
    def discardCRPrefix(text):
        '''
        Remove Change Request prefix
        '''
        result = re.sub(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)', r'\2', text)
        # Replace underscore by space, prettier
        result = re.sub(r'_',r' ',result)
        return result

    @staticmethod
    def getCRPrefix(text):
        '''
        Get Change Request prefix
        '''
        result = re.sub(r'(EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR)_(.*)', r'\1', text)
        return result

    def createCrStatus(self,cr_status="",find_status=False):
        '''
            Create Change Request status query
        '''
        condition = ""
        if cr_status != "" and cr_status is not None:
            if find_status:
                condition = ' or (crstatus=\'{:s}\') '.format(cr_status)
            else:
                find_status = True
                condition =  ' and ((crstatus=\'{:s}\') '.format(cr_status)
        return(condition,find_status)

    @staticmethod
    def createItemType(item_type="",find_status=False):
        '''
            Create Synergy type query
        '''
        condition = ""
        if item_type not in ("",None):
            if find_status == True:
                condition = ' or '
            else:
                condition = '"('
                find_status = True
            condition = condition + ' (cvtype=\''+ item_type +'\') '
        return(condition,find_status)

    def _splitComma(self,input):
        '''
        Creates a string like "((CR_implemented_for='SW_ENM/01') or(CR_implemented_for='SW_PLAN/02'))"
        if keyword = CR_implemented_for and release = SW_ENM/01,SW_PLAN/02
        '''
        # Remove not ascii character
        input = self.removeNonAscii(input)
        for list_rel in csv.reader([input]):
            pass
        text = ""
        if self._is_array(list_rel):
            for rel in list_rel:
                text +=  rel +' and '
            # Remove last comma
            text = text[0:-5]
        else:
            text= input
        return text

    def createCrImplemented(self,cr_std="",find=False,filter_cr="CR_detected_on"):
        '''
            Create Change Request status query with attribute
        '''
        condition = ""
        if cr_std not in ("",None):
            if find == True:
                condition = ' or ('+filter_cr+'=\''+ cr_std +'\') '
            else:
                find = True
                condition =  ' and (('+filter_cr+'=\''+ cr_std +'\') '
        return(condition,find)

    def makeobjectsFilter(self,object_released,object_integrate):
        '''
            Create Synergy item status query
        '''
        query = ""
        if object_integrate == 1 and object_released == 1:
            query = ' and (status=\'released\' or status=\'integrate\')'
        elif object_integrate == 0 and object_released == 1:
            query = '  and status=\'released\' '
        elif object_integrate == 1 and object_released == 0:
            query = ' and status=\'integrate\' '
        else:
            pass
        return query

    @staticmethod
    def _is_array(var):
        '''
            Define if a variable is an array (a list or a tuple)
        '''
        return isinstance(var, (list, tuple))

    def _getOptionArray(self,label,option):
        ##        self.sources_filter = self.getOptions(label,option)
        table = ()
        if self.config_parser.has_option(label,option):
            sources_filter = self.config_parser.get(label,option)
            if sources_filter:
                m = re.search(r',',sources_filter)
                if m:
                    ##                    print type(sources_filter)
                    for table in csv.reader([sources_filter]):
                        pass
                else:
                    table = sources_filter
            else:
                table = ()
        return(table)
    #
    # Regular expressions
    #
    def _prepareRegexp(self,filters):
        #global project_name
        index = 0
        list_items_skipped = []
        regexp=[]
        for filter_array in filters:
            ##            print type(filter_array)
            if self._is_array(filter_array):
                sub_regexp=[]
                ##                regexp[index] = '^(.*)'+ project_name + '\\\\([A-Z]*\\\\)?' + re.escape(filter) + '\\\\(.*)-(.*)@(.*)-(.*)$'
                for filter in filter_array:
                    sub_regexp.append('^(.*)'+ re.escape(filter) + '(.*)\\\\(.*)-(.*)@(.*)-(.*)$')
                    list_items_skipped.append([])
                    index += 1
                regexp.append(sub_regexp)
            else:
                regexp.append('^(.*)'+ re.escape(filter_array) + '(.*)\\\\(.*)-(.*)@(.*)-(.*)$')
                list_items_skipped.append([])
                index += 1
        return regexp,list_items_skipped

    def _filterRegexp(self,
                      regexp,
                      line):
        list_items_skipped = ""
        if self._is_array(regexp):
            for sub_regexp in regexp:
                match_result = re.match(sub_regexp,line)
                if match_result:
                    ##                            print m_input_data.group(3)
                    list_items_skipped = match_result.group(3)
        else:
            match_result = re.match(regexp,line)
            if match_result:
                ##                            print m_input_data.group(3)
                list_items_skipped = match_result.group(3)
            else:
                pass
        return list_items_skipped

    def _par(self,txt,style=""):
        repl = ''
        # Will make a table
        unicode_paragraph = []
##            repl = ""
        for element in txt:
            try:
                # Unicodize
                unicode_paragraph.append(element)
##                    repl = unicode(replace[1], errors='ignore')
##                    unicode_paragraph = unicode(element, errors='ignore')
##                    unicode_paragraph.append( map(lambda i: unicode(i, errors='ignore'), element) )
            except TypeError as exception:
                print ("Execution failed:", exception)
                unicode_paragraph.append(element)
##                    print element
            except UnicodeDecodeError as exception:
                print ("Execution failed:", exception)
                unicode_paragraph.append(element)
            if not len(unicode_paragraph):
                # Empty paragraph
                repl = ''
            else:
##                    print "unicode_paragraph:",unicode_paragraph
                # create 'lxml.etree._Element' objects
##                print "TEST_PAR",unicode_paragraph
                try:
                    repl = docx.paragraph(unicode_paragraph,style=style)
                except ValueError as exception:
                    print ("unicode_paragraph",unicode_paragraph)
                    print ("TXT",txt)
        return repl

    def _table(self,array,fmt):
        # Will make a table
        unicode_table = []
        for element in array:
            try:
                # Unicodize
                unicode_table.append( map(lambda i: unicode(i, errors='ignore'), element) )
            except TypeError as exception:
                print ("Execution failed:", exception)
                unicode_table.append(element)
##                    print element
            except UnicodeDecodeError as exception:
                print ("Execution failed:", exception)
                unicode_table.append(element)
        if not len(unicode_table):
            # Empty table
            repl = ''
        else:
            repl = docx.table(
                unicode_table,
                heading = fmt['heading'] if 'heading' in fmt.keys() else False,
                colw = fmt['colw'] if 'colw' in fmt.keys() else None,
                cwunit = fmt['cwunit'] if 'cwunit' in fmt.keys() else 'dxa',
                tblw = fmt['tblw'] if 'tblw' in fmt.keys() else 0,
                twunit = fmt['twunit'] if 'twunit' in fmt.keys() else 'auto',
                borders = fmt['borders'] if 'borders' in fmt.keys() else {},
                celstyle = fmt['celstyle'] if 'celstyle' in fmt.keys() else None,
##                headstyle = fmt['headstyle'] if 'headstyle' in fmt.keys() else {},
            )
        return repl

    def heading(self,txt):
        headinglevel = "3"
        repl = docx.heading(txt,headinglevel,lang='fr')
        return repl

    def replaceTag(self,
                   doc,
                   tag,
                   replace,
                   fmt = {}):
        """ Searches for {{tag}} and replaces it with replace.
    Replace is a list with two indexes: 0=type, 1=The replacement
    Supported values for type:
    'str': <string> Renders a simple text string
    'par': <paragraph> Renders a paragraph with carriage return
    'tab': <table> Renders a table, use fmt to tune look
    'list': <list> Renders a list of tables
    'mix': <mixed> Renders a list of tables and paragraph
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
                print ("Execution failed:", exception)
                repl = replace[1]
##                print repl
            except UnicodeDecodeError as exception:
                print ("Execution failed:", exception)
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
            return docx.advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl),relationshiplist
        elif replace[0] == 'html':
            paragraph = self._par("")
            h = HTML('html', 'text')
            t = h.table(border='1')
            for line in replace[1]:
                r = t.tr
                for cell in line:
                    r.td(cell)
            #print "HTML",h
            #add_html(paragraph, str(h))
            #repl.append(paragraph)
        elif replace[0] == 'list':
            repl = []
            for dir,tbl in replace[1]:
                #print "DIR",dir
                #print "TBL",tbl
                elt = self.heading(dir)
                #elt = self._par([(dir,'rb')])
                repl.append(elt)
                elt = self._table(tbl,fmt)
                repl.append(elt)
                elt = self._par([("",'rb')])
                repl.append(elt)
        elif replace[0] == 'mix':
            num_begin = ord("a")
            num_end = ord("z")
            num = num_begin
            prefix = ""
            repl = []
            dico = replace[1]
            tbl_checklist = []
            index_sort = 0
            #TODO to put in ccb.py
            for key,value in dico.items():
                if key == "sort":
                    if value == "id":
                        index_sort = 0
                    elif value == "status":
                        index_sort = 1
                    elif value == "severity":
                        index_sort = 2
                    else:
                        index_sort = 0
                elif key == "domain":
                    pass
                elif key == "timeline":
                    pass
                else:
                    # Checklist
                    cr_id = key[1].zfill(4)
                    cr_status = key[2]
                    tbl_checklist.append((cr_id,cr_status,value))
            tbl_checklist_sorted = sorted(tbl_checklist,key=lambda x: x[index_sort])
            # Example: value for a PLDCR in "Fixed" state
            # [['Check', 'Status', 'Remark'],
            # [u'check that defect/evolution is understandable (description, problem condition, ...)\n', '', ''],
            # [u'check CR field coherency with configuration management process', '', ''],
            # [u'discuss and validate classification', '', ''],
            # [u'approve corrective action and impact analysis', '', ''],
            # [u'schedule CR implemented for correction', '', '']]
            #

            for cr_id,cr_status,value in tbl_checklist_sorted:
                #header = [("{:s}{:s}) {:s} {:s}".format(prefix,chr(num),dico['domain'],cr_id),'rb')]
                header = "{:s}_{:s}".format(dico['domain'],cr_id)
                # Next state and transition
                if 0==1:
                    if cr_status in self.dico_status_flow:
                        if cr_id in dico["timeline"]:
                            print ("CR_STATUS",cr_status)
                            print ("TEST TIMELINE",dico["timeline"][cr_id])
                            final_cr_status = dico["timeline"][cr_id]["current"]
                            #cr_next_state = [("CR Transition to state: \"{:s}\"".format(final_cr_status),'')]
                            if final_cr_status in self.dico_get_transition_flow:
                                list_target_states = "/".join(map(str, self.dico_status_flow[final_cr_status]))
                                list_target_transitions = "/".join(map(str, self.dico_transition_flow[final_cr_status]))
                                cr_next_state = [("CR Transition to state: \"{:s}\"".format(list_target_states),'')]
                                cr_transition = [("Conclusion of CR review: Transition \"{:s}\" authorized/not authorized.".format(list_target_transitions),'')]
                            else:
                                cr_next_state = [("CR Transition to state:",'b')]
                                cr_transition = [("Conclusion of CR review:",'b')]
                        else:
                            list_target_states = "/".join(map(str, self.dico_status_flow[cr_status]))
                            list_target_transitions = "/".join(map(str, self.dico_transition_flow[cr_status]))
                            cr_next_state = [("CR Transition to state: \"{:s}\"".format(list_target_states),'')]
                            cr_transition = [("Conclusion of CR review: Transition \"{:s}\" authorized/not authorized.".format(list_target_transitions),'')]
                    else:
                        cr_next_state = [("CR Transition to state:",'b')]
                        cr_transition = [("Conclusion of CR review:",'b')]
                else:
                    if cr_status in self.dico_status_flow:
                        if cr_id in dico["timeline"]:
                            print ("TEST TIMELINE",dico["timeline"][cr_id])
                            current_cr_status = dico["timeline"][cr_id]["current"]
                            former_cr_status = dico["timeline"][cr_id]["former"]
                            if former_cr_status in self.dico_status_flow:
                                list_target_states = "/".join(map(str, self.dico_status_flow[former_cr_status]))
                            else:
                                list_target_states = "Error, unexpected CR status"
                            cr_next_state = [("CR Transition to state: \"{:s}\"".format(list_target_states),'')]
                            if former_cr_status in self.dico_transition_flow:
                                transition = "/".join(map(str, self.dico_transition_flow[former_cr_status]))
                                #transition = self.dico_get_transition_flow[current_cr_status]
                            else:
                                transition = "Error unexpected transition"
                            cr_transition = [("Conclusion of CR review: Transition \"{:s}\" authorized.".format(transition),'')]
                        else:
                            list_target_states = "/".join(map(str, self.dico_status_flow[cr_status]))
                            list_target_transitions = "/".join(map(str, self.dico_transition_flow[cr_status]))
                            cr_next_state = [("CR Transition to state: \"{:s}\"".format(list_target_states),'')]
                            cr_transition = [("Conclusion of CR review: Transition \"{:s}\" authorized/not authorized.".format(list_target_transitions),'')]
                    else:
                        cr_next_state = [("CR Transition to state:",'b')]
                        cr_transition = [("Conclusion of CR review:",'b')]
                num += 1
                if num > num_end:
                    prefix += "a"
                    num = num_begin
                print ("HEADER:",header)
                elt = self._par(header,style="Titre2")
                repl.append(elt)
                print ("VALUE:",value)
                elt = self._table(value,fmt)
                repl.append(elt)
                print ("TRANSITION:",cr_transition)
                elt = self._par(cr_transition)
                repl.append(elt)
                print ("STATE:",cr_next_state)
                elt = self._par(cr_next_state)
                repl.append(elt)
        else:
            raise NotImplementedError("Unsupported " + replace[0] + " tag type!")
        # Replace tag with 'lxml.etree._Element' objects
        result = docx.advReplace(doc, '\{\{'+re.escape(tag)+'\}\}', repl,6)
##        result = docx.advReplace_new(doc, '\{\{'+re.escape(tag)+'\}\}', repl,6)
        return result

    def picture_add(self,
                    relationshiplist,
                    picname,
                    picdescription,
                    pixelwidth=None,
                    pixelheight=None,
                    nochangeaspect=True,
                    nochangearrowheads=True):
        '''Take a relationshiplist, picture file name, and return a paragraph containing the image
        and an updated relationshiplist'''
        # http://openxmldeveloper.org/articles/462.aspx
        # Create an image. Size may be specified, otherwise it will based on the
        # pixel size of image. Return a paragraph containing the picture'''
        # Copy the file into the media dir
    ##    media_dir = join(template_dir, 'word', 'media')
    ##    if not os.path.isdir(media_dir):
    ##        os.mkdir(media_dir)
    ##    shutil.copyfile(picname, join(media_dir, picname))
        # Check if the user has specified a size
        if not pixelwidth or not pixelheight:
            # If not, get info from the picture itself
            pixelwidth, pixelheight = Image.open(picname).size[0:2]
        # OpenXML measures on-screen objects in English Metric Units
        # 1cm = 36000 EMUs
        emuperpixel = 12667
        width = str(pixelwidth * emuperpixel)
        height = str(pixelheight * emuperpixel)
        # Set relationship ID to the first available
        picid = '2'
        picrelid = 'rId'+str(len(relationshiplist)+1)
        relationshiplist.append([
            'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
            'media/'+picname])
        # There are 3 main elements inside a picture
        # 1. The Blipfill - specifies how the image fills the picture area (stretch, tile, etc.)
        blipfill = docx.makeelement('blipFill', nsprefix='pic')
        blipfill.append(docx.makeelement('blip', nsprefix='a', attrnsprefix='r',
                        attributes={'embed': picrelid}))
        stretch = docx.makeelement('stretch', nsprefix='a')
        stretch.append(docx.makeelement('fillRect', nsprefix='a'))
        blipfill.append(docx.makeelement('srcRect', nsprefix='a'))
        blipfill.append(stretch)
        # 2. The non visual picture properties
        nvpicpr = docx.makeelement('nvPicPr', nsprefix='pic')
        cnvpr = docx.makeelement('cNvPr', nsprefix='pic',
                            attributes={'id': '0', 'name': 'Picture 1', 'descr': picname})
        nvpicpr.append(cnvpr)
        cnvpicpr = docx.makeelement('cNvPicPr', nsprefix='pic')
        cnvpicpr.append(docx.makeelement('picLocks', nsprefix='a',
                        attributes={'noChangeAspect': str(int(nochangeaspect)),
                                    'noChangeArrowheads': str(int(nochangearrowheads))}))
        nvpicpr.append(cnvpicpr)
        # 3. The Shape properties
        sppr = docx.makeelement('spPr', nsprefix='pic', attributes={'bwMode': 'auto'})
        xfrm = docx.makeelement('xfrm', nsprefix='a')
        xfrm.append(docx.makeelement('off', nsprefix='a', attributes={'x': '0', 'y': '0'}))
        xfrm.append(docx.makeelement('ext', nsprefix='a', attributes={'cx': width, 'cy': height}))
        prstgeom = docx.makeelement('prstGeom', nsprefix='a', attributes={'prst': 'rect'})
        prstgeom.append(docx.makeelement('avLst', nsprefix='a'))
        sppr.append(xfrm)
        sppr.append(prstgeom)
        # Add our 3 parts to the picture element
        pic = docx.makeelement('pic', nsprefix='pic')
        pic.append(nvpicpr)
        pic.append(blipfill)
        pic.append(sppr)
        # Now make the supporting elements
        # The following sequence is just: make element, then add its children
        graphicdata = docx.makeelement('graphicData', nsprefix='a',
                                    attributes={'uri': 'http://schemas.openxmlforma'
                                                     'ts.org/drawingml/2006/picture'})
        graphicdata.append(pic)
        graphic = docx.makeelement('graphic', nsprefix='a')
        graphic.append(graphicdata)
        framelocks = docx.makeelement('graphicFrameLocks', nsprefix='a',
                                 attributes={'noChangeAspect': '1'})
        framepr = docx.makeelement('cNvGraphicFramePr', nsprefix='wp')
        framepr.append(framelocks)
        docpr = docx.makeelement('docPr', nsprefix='wp',
                            attributes={'id': picid, 'name': 'Picture 1',
                                        'descr': picdescription})
        effectextent = docx.makeelement('effectExtent', nsprefix='wp',
                                     attributes={'l': '25400', 't': '0', 'r': '0',
                                                 'b': '0'})
        extent = docx.makeelement('extent', nsprefix='wp',
                             attributes={'cx': width, 'cy': height})
        inline = docx.makeelement('inline', attributes={'distT': "0", 'distB': "0",
                                                     'distL': "0", 'distR': "0"},
                             nsprefix='wp')
        inline.append(extent)
        inline.append(effectextent)
        inline.append(docpr)
        inline.append(framepr)
        inline.append(graphic)
        drawing = docx.makeelement('drawing')
        drawing.append(inline)
        run = docx.makeelement('r')
        run.append(drawing)
        paragraph = docx.makeelement('p')
        paragraph.append(run)
        return relationshiplist, paragraph

    @staticmethod
    def getReleaseName(release):
        regexp = '^(.*)/([0-9]*)$'
        match_result = re.match(regexp,release)
        if match_result:
            release_name = match_result.group(1)
        else:
            release_name = ""
        return release_name

    def _compareReleaseName(self,releases=[]):
        sub_regexp = '^(.*)/([0-9]*)$'
        name = []
        if len(releases) > 2:
            raise Exception("This function accept array of 2 elements only!")
            return False
        for release in releases:
            match_result = re.match(sub_regexp,release)
            if match_result:
                name.append(match_result.group(1))
        if name[0] == name[1]:
            return True
        else:
            return False
    @staticmethod
    def _removeDoublons(tbl_in):
        '''
        '''
        tbl_out = []
        if tbl_in is not None:
            for elt in tbl_in:
                if elt not in tbl_out:
                    tbl_out.append(elt)
        return tbl_out

    @staticmethod
    def removeNonAscii(s):
        txt = ""
        try:
            txt = "".join(filter(lambda x: ord(x)<128, s))
        except TypeError as e:
            #print "TypeError",e
            #print "TXT:",s
            s = str(s)
            txt = "".join(filter(lambda x: ord(x)<128, s))
        return txt

    @staticmethod
    def _invert_dol(in_dico):
        #return dict((v, k) for k in d for v in d[k])
        invert_dico = {}
        for k in in_dico:
            for v in in_dico[k]:
               # print("test:",k,v)
                v = Tool.removeNonAscii(v)
                invert_dico.setdefault(str(v), []).append(k)
        #print "invert_dico",invert_dico
        #print "in_dico",in_dico
        return invert_dico

    @staticmethod
    def replaceNonASCII(text,html=False):
        if html:
            char = {r'\x02':r'<',
                    r'\x03':r'>',
                    r'\xa7':r'chapter ',
                    r'\x0d':r'',                # CR
                    r'\x0a':r'<br/>',           # LF
                    r'\x09':r'    ',           # Tab
                    r'\x95':r'...',     # dot
            }
        else:
            char = {r'\x02':r'<',
                    r'\x03':r'>',
                    r'\x07':r'',    # BEL
                    r'\x0c':r'',    # Form Feed
                    r'\xa7':r'chapter ',
                    r'\xf1':r'+/-',
                    r'\xf2':r'>=',
                    r'\xf3':r'<=',
                    r'&':r'and'
                    }
        try:
            for before, after in char.iteritems():
                text = re.sub(before,after,text)
        except TypeError as e:
            print (e)
        try:
            from unidecode import unidecode
            text = unidecode(text)
        except ImportError:
            pass
        return text

    @staticmethod
    def replaceBeacon(text):
        char = {r'\x02':r'<',r'\x03':r'>'}
        for before, after in char.iteritems():
            text = re.sub(before,after,text)
        return text

    @staticmethod
    def adjustCR(stdout):
        char = {r"<br ?\/>":r", ",
                        r"\r\n":r"\n",
                        r"\x1E":"----------\n",
                        r"\x1C":r"\n",
                        r"<void>":r"",
                        r"&":r"and",
                        r"<font size= \"[0-9]{1,2}\">":r""} #,
                        #r"<(?!cell|/cell|void|span|div|/p|p\>|a|a\>|/b|b/>|h3|h3\>|td|tr|ul|li|font|style|/)":r" strictly lesser than"}
        for before,after in char.iteritems():
            stdout = re.sub(before,after,stdout)
        return stdout

    # Change part
    def new_createConditionStatus(self,
                               detect_release="",
                               impl_release="",
                               cr_type="",              # to be deleted
                               old_cr_workflow=False,   # to be deleted
                               cr_status="",
                               attribute="CR_implemented_for",
                               list_cr_type=[],
                               list_cr_status=[],
                               list_cr_doamin=[],
                               list_cr_selected_by_user=[]
                               ):
        '''
            Create CR status filter for Change query
        '''

        # Get filter attributes
        #
        # Default = CR_implemented_for
        # Detected on
        # Implemented for
        # Applicable Since

        if attribute is "None":
            filter_cr = ""
        else:
            filter_cr = attribute
        # Determine wether an old or new Change Request workflow is used
        # Query format is modified accordingly
        if old_cr_workflow:
            detection_word = "detected_on"
            filter_cr = "implemented_in"
        else:
            detection_word = "CR_detected_on"
            filter_cr = "CR_implemented_for"
        detect_attribut = "%{:s};%{:s}".format(detection_word,filter_cr)
        condition = '"(cvtype=\'problem\') '
        if  Tool.isAttributeValid(impl_release):
            # implemented
            condition_impl = self._createImpl(filter_cr, impl_release,with_and=False)
        else:
            condition_impl = False
        if Tool.isAttributeValid(detect_release):
            # detected
            condition_detect = self._createImpl(detection_word, detect_release,with_and=False)
        else:
            condition_detect = False
        if condition_impl and condition_detect:
            condition += "and ({:s} or {:s})".format(condition_impl,condition_detect)
        elif condition_impl:
            condition += "and {:s}".format(condition_impl)
        elif condition_detect:
            condition += "and {:s}".format(condition_detect)
        # CR types
        condition += self._createImpl("CR_type", list_cr_type)
        # CR status
        condition += self._createImpl("crstatus", list_cr_status)
        # CR domains
        condition += self._createImpl("CR_domain", list_cr_doamin)
        # CRs selected by the user
        condition += self._createImpl("problem_number", list_cr_selected_by_user)
        condition += '" '
        return condition, detect_attribut

    @classmethod
    def _createImpl(cls,keyword,release,with_and=True):
        '''
        Creates a string like "((CR_implemented_for='SW_ENM/01') or (CR_implemented_for='SW_PLAN/02'))"
        if keyword = CR_implemented_for and release = SW_ENM/01,SW_PLAN/02
        '''
        def dico(keyword,rel):
            txt = "({:s}='{:s}')".format(keyword,rel)
            return txt
        print ("_createImpl",keyword,release)
        if release != [] and release != ['']:
            if not cls._is_array(release):
                # Split string with comma as separator
                list_rel = release.split(",")
            else:
                # Keep list
                list_rel = release
            keywords_tbl = map((lambda x: keyword),list_rel)
            text = " or ".join(map(dico,keywords_tbl, list_rel))
            if with_and:
                text_final = " and ( " + text + " ) "
            else:
                text_final = " ( " + text + " ) "
        else:
            text_final = ""
        return text_final

    def _parseMultiCRParent(self,text_html):
        # instantiate the parser and fed it some HTML
        parser = MyHTMLParserTable()
        #parser.tbl = []
        parser.feed(text_html)
        return parser.tbl

    def _parseCRParent(self,text_html):
        # instantiate the parser and fed it some HTML
        parser = MyHTMLParserPlain()
        #parser.tbl = []
        parser.feed(text_html)
        return parser.tbl

    def _filterASCII(self,transi_log):
        print ("transi_log",transi_log)
        # Remove ASCII control characters
        # Replace FS and RS characters
##        char = {r'\x1e':'',r'\x1c':'',r'\x0d':'<br/>'}
        char = {r'\x1e(.*)\x0d':r'<span style="color:\'red\'">\1</span><br/>',
                r'\x1c(.*)\x0d':r'<span style="color:\'green\'">\1</span><br/>'}
        for before, after in char.iteritems():
            transi_log = re.sub(before,after,transi_log)
        if transi_log is not None:
            transi_log_filtered = self.removeNonAscii(transi_log)
            #transi_log_filter.decode('latin1') #filter(string.printable[:-5].__contains__,transi_log_filter)
        else:
            transi_log_filtered = transi_log
        return transi_log_filtered

    @staticmethod
    def _parseCRCell(text_html):
        # instantiate the parser and fed it some HTML
        parser = MyHTMLParser()
        parser.text = ""
        parser.tbl = []
        parser.dico = {}
        parser.foundCell = False
        parser.feed(text_html)
        return parser.tbl
    
    def createCR(self,dico_replace={'problem_number':'999',
                                    'crstatus':'SACR_In_Analysis',
                                    'problem_synopsis':'The computation of the OCP command IS NOT in accordance with WHCC functional mode.',
                                    'CR_detected_on':'S.2',
                                    'CR_applicable_since':'S1.0',
                                    'CR_implemented_for':'S1.6',
                                    'submitter':'bouhaft1',
                                    'create_time':'',
                                    'CR_ECE_classification':'Major',
                                    'CR_customer_classification':'',
                                    'CR_request_type':'Defect',
                                    'CR_expected':'',
                                    'CR_observed':'',
                                    'CR_functional_impact':'',
                                    'CR_origin':'',
                                    'CR_origin_desc':'',
                                    'CR_analysis':'',
                                    'CR_correction_description':'The states ACTIVE and INACTIVE of the SDTS have been replaced by the states OCP_AUTO, OCP_OFF and OCP_STANDBY in order to take the WHCC mode into account.',
                                    'CR_product_impact':'yes',
                                    'CR_doc_impact':'yes',
                                    'CR_verif_impact':'',
                                    'impact_analysis':'',
                                    'functional_limitation_desc':'',
                                    'implemented_modification':'',
                                    'CR_implementation_baseline':'',
                                    'CR_verification_activities':'',
                                    'functional_limitation':'',
                                    'parent_cr':"<td><IMG SRC=\"../img/changeRequestIcon.gif\">---</td><td>---</td><td>---</td><td>---</td><td>---</td>",
                                    'SCR_Closed_id':'',
                                    'SCR_Closed_time':'',
                                    'transition_log':'',
                                    'modify_time':'',
                                    'CR_domain':'SACR',
                                    'CR_type':'WDS'
                                    },
                                    output_filename="test.html"):
        # dictionary to replace in Word
        replacements = {r'\${CR_ID}':dico_replace['problem_number'],
                        r'\${CR_STATUS}':dico_replace['crstatus'],
                        r'\${CR_SYNOPSIS}':dico_replace['problem_synopsis'],
                        r'\${CR_APPLICABLE_SINCE}':dico_replace['CR_applicable_since'],
                        r'\${CR_IMPLEMENTED_FOR}':dico_replace['CR_implemented_for'],
                        r'\${SCR_IN_ANALYSIS_ID}':dico_replace['submitter'],
                        r'\${CREATE_TIME}':dico_replace['create_time'],
                        r'\${CR_ECE_CLASSIFICATION}':dico_replace['CR_ECE_classification'],
                        r'\${CR_CUSTOMER_CLASSIFICATION}':dico_replace['CR_customer_classification'],
                        r'\${CR_REQUEST_TYPE}':dico_replace['CR_request_type'],
                        r'\${CR_DETECTED_ON}':dico_replace['CR_detected_on'],
                        r'\${CR_EXPECTED}':dico_replace['CR_expected'],
                        r'\${CR_OBSERVED}':dico_replace['CR_observed'],
                        r'\${CR_FUNCTIONAL_IMPACT}':dico_replace['CR_functional_impact'],
                        r'\${CR_ORIGIN}':dico_replace['CR_origin'],
                        r'\${CR_ORIGIN_DESC}':dico_replace['CR_origin_desc'],
                        r'\${CR_ANALYSIS}':dico_replace['CR_analysis'],
                        r'\${CR_CORRECTION_DESCRIPTION}':dico_replace['CR_correction_description'],
                        r'\${CR_PRODUCT_IMPACT}':dico_replace['CR_product_impact'],
                        r'\${CR_DOC_IMPACT}':dico_replace['CR_doc_impact'],
                        r'\${CR_VERIF_IMPACT}':dico_replace['CR_verif_impact'],
                        r'\${IMPACT_ANALYSIS}':dico_replace['impact_analysis'],
                        r'\${FUNCTIONAL_LIMITATION_DESC}':dico_replace['functional_limitation_desc'],
                        r'\${IMPLEMENTED_MODIFICATION}':dico_replace['implemented_modification'],
                        r'\${CR_IMPLEMENTATION_BASELINE}':dico_replace['CR_implementation_baseline'],
                        r'\${CR_VERIFICATION_ACTIVITIES}':dico_replace['CR_verification_activities'],
                        r'\${FUNCTIONAL_LIMITATION}':dico_replace['functional_limitation'],
                        r'\${CR_PARENT}':dico_replace['parent_cr'],
                        r'\${SCR_CLOSED_ID}':dico_replace['SCR_Closed_id'],
                        r'\${SCR_CLOSED_TIME}':dico_replace['SCR_Closed_time'],
                        r'\${TRANSITION_LOG}':dico_replace['transition_log'],
                        r'\${MODIFY_TIME}':dico_replace['modify_time'],
                        r'\${VISUAL_STATUS}':dico_replace['crstatus'],
                        r'\${CR_DOMAIN}':dico_replace['CR_domain'],
                        r'\${CR_TYPE}':dico_replace['CR_type']}
        fin = open('template/cr_template.html')
        input = fin.read()
        out = open(output_filename, 'w')
        for before, after in replacements.iteritems():
            filtered_after = self.replaceNonASCII(after)
            try:
                filtered_after = filtered_after.encode("utf-8")
                input = re.sub(before,filtered_after,input)
            except UnicodeDecodeError as exception:
                # Vieux patch
                print (exception," ",before," ",filtered_after)
                # Remove span
                char = {r'<span style =  ?".*" >':'','<br>':''}
                for before_char, after_char in char.iteritems():
                    filtered_after = re.sub(before_char,after_char,filtered_after)
                print ("PATCH",filtered_after)
                filtered_after = filtered_after.encode("utf-8")
                input = re.sub(before,filtered_after,input)

        out.write(input)
        out.close

    def _parseCR(self,
                 text_html,
                 transition_log,
                 parent_cr=[],
                 information_cr=[],
                 child_cr=[],
                 output_filename=""):
        """
        This function populate Change CR template with CR inputs
        :param text_html:
        :param transition_log:
        :param parent_cr:
        :param information_cr:
        :param child_cr:
        :param output_filename:
        :return:
        """
        # instantiate the parser and fed it some HTML
        parser = MyHTMLParser()
        parser.text = ""
        parser.tbl = []
        parser.dico = {}
        parser.foundCell = False
        parser.feed(text_html)
        # dictionary to replace in Word
        replacements = {r'\${CR_ID}':parser.dico['problem_number'],
                        r'\${CR_STATUS}':parser.dico['crstatus'],
                        r'\${CR_SYNOPSIS}':parser.dico['problem_synopsis'],
                        r'\${CR_APPLICABLE_SINCE}':parser.dico['CR_applicable_since'],
                        r'\${CR_IMPLEMENTED_FOR}':parser.dico['CR_implemented_for'],
                        r'\${SCR_IN_ANALYSIS_ID}':parser.dico['SCR_In_Analysis_id'],
                        r'\${CREATE_TIME}':parser.dico['create_time'],
                        r'\${CR_ECE_CLASSIFICATION}':parser.dico['CR_ECE_classification'],
                        r'\${CR_CUSTOMER_CLASSIFICATION}':parser.dico['CR_customer_classification'],
                        r'\${CR_REQUEST_TYPE}':parser.dico['CR_request_type'],
                        r'\${CR_DETECTED_ON}':parser.dico['CR_detected_on'],
                        r'\${CR_EXPECTED}':parser.dico['CR_expected'],
                        r'\${CR_OBSERVED}':parser.dico['CR_observed'],
                        r'\${CR_FUNCTIONAL_IMPACT}':parser.dico['CR_functional_impact'],
                        r'\${CR_ORIGIN}':parser.dico['CR_origin'],
                        r'\${CR_ORIGIN_DESC}':parser.dico['CR_origin_desc'],
                        r'\${CR_ANALYSIS}':parser.dico['CR_analysis'],
                        r'\${CR_CORRECTION_DESCRIPTION}':parser.dico['CR_correction_description'],
                        r'\${CR_PRODUCT_IMPACT}':parser.dico['CR_product_impact'],
                        r'\${CR_DOC_IMPACT}':parser.dico['CR_doc_impact'],
                        r'\${CR_VERIF_IMPACT}':parser.dico['CR_verif_impact'],
                        r'\${IMPACT_ANALYSIS}':parser.dico['impact_analysis'],
                        r'\${FUNCTIONAL_LIMITATION_DESC}':parser.dico['functional_limitation_desc'],
                        r'\${IMPLEMENTED_MODIFICATION}':parser.dico['implemented_modification'],
                        r'\${CR_IMPLEMENTATION_BASELINE}':parser.dico['CR_implementation_baseline'],
                        r'\${CR_VERIFICATION_ACTIVITIES}':parser.dico['CR_verification_activities'],
                        r'\${FUNCTIONAL_LIMITATION}':parser.dico['functional_limitation'],
                        r'\${CR_PARENT}':parent_cr,
                        r'\${CR_INFORMATION}':information_cr,
                        r'\${CR_CHILD}':child_cr,
                        r'\${SCR_CLOSED_ID}':parser.dico['SCR_Closed_id'],
                        r'\${SCR_CLOSED_TIME}':parser.dico['SCR_Closed_time'],
                        r'\${TRANSITION_LOG}':transition_log,
                        r'\${MODIFY_TIME}':parser.dico['modify_time'],
                        r'\${VISUAL_STATUS}':parser.dico['crstatus'],
                        r'\${CR_DOMAIN}':parser.dico['CR_domain'],
                        r'\${CR_TYPE}':parser.dico['CR_type']}
        fin = open('template/cr_template.html')
        input = fin.read()
        out = open(output_filename, 'w')
        for before, after in replacements.iteritems():
            filtered_after = self.replaceNonASCII(after)
            try:
                filtered_after = filtered_after.encode("utf-8")
                input = re.sub(before,filtered_after,input)
            except UnicodeDecodeError as exception:
                # Vieux patch
                print (exception," ",before," ",filtered_after)
                # Remove span
                char = {r'<span style =  ?".*" >':'','<br>':''}
                for before_char, after_char in char.iteritems():
                    filtered_after = re.sub(before_char,after_char,filtered_after)
                print ("PATCH",filtered_after)
                filtered_after = filtered_after.encode("utf-8")
                input = re.sub(before,filtered_after,input)

        out.write(input)
        out.close

    def _getTemplate(self,template_type,template_default_name="default.docx"):
        # Get config
        try:
            # get template name
            template_dir = join(os.path.dirname("."), 'template')
            template_name = self.getOptions("Template",template_type)
            if template_name:
                template = join(template_dir, template_name)
                print ("{:s} template applied.".format(template_name))
            else:
                print ("Default {:s} template applied.".format(template_default_name))
                template = join(template_dir, template_default_name)
        except IOError as exception:
            print ("Execution failed:", exception)
            print ("Default {:s} template applied.".format(template_default_name))
            template = join(template_dir, template_default_name)
        #except NoOptionError as exception:
        #    print "Execution failed:", exception
        return template

    def _createDico2Word(self,
                         list_tags,
                         template_name,
                         filename,
                         image_name=None):
        """

        :param list_tags:
        :param template_name:
        :param filename:
        :param image_name:
        :return:
        """
        # Load the original template
        template_found = False
        try:
            template = zipfile.ZipFile(template_name,mode='r')
            template_found = True
        except IOError as exception:
            print ("Execution failed:", exception)
            docx_filename = False
            try:
                template_dir = join(os.path.dirname("."), 'template')
                template_default_name = join(template_dir, "review_template.docx")
                template = zipfile.ZipFile(template_default_name,mode='r')
                template_found = True
                print ("TAKE DEFAULT TEMPLATE")
            except IOError as exception:
                print ("Execution failed:", exception)
                docx_filename = False
        if template.testzip() or not template_found:
            raise Exception('File is corrupted!')
            docx_filename = False
        else:
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
            # Will store modified sections here
            outdoc = {}
            try:
                for curact in actlist:
                    xmlcontent = template.read(curact[0])
                    outdoc[curact[0]] = etree.fromstring(xmlcontent)
                    # Will work on body
                    docbody = outdoc[curact[0]].xpath(curact[1], namespaces=docx.nsprefixes)[0]
                    # Loop to replace tags
                    for key, value in list_tags.items():
                        if curact[0] == "word/document.xml":
                            print ("TEST:" + key,value)
                        if value['text'] != None:
                            text = value['text']
                        else:
                            text = "None"
                        docbody = self.replaceTag(docbody, key, (value['type'], text), value['fmt'])
                    # Cleaning
                    docbody = docx.clean(docbody)
            except KeyError as exception:
                print >>sys.stderr, "Execution failed:", exception
            # ------------------------------
            # Save output
            # ------------------------------
            # Prepare output file
            docx_filename = filename
            try:
                print ("GEN_DIR",self.gen_dir)
                target = join(self.gen_dir,docx_filename)
                outfile = zipfile.ZipFile(target,mode='w',compression=zipfile.ZIP_DEFLATED)
                # Replace image if image exists in SQLite database
                if image_name is not None:
                    actlist.append(('word/media/image1.png', ''))
                    img = open('img/' + image_name,'rb')
                    data = img.read()
                    outfile.writestr('word/media/image1.png',data)
                    img.close()
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
                docx_filename = False
        return docx_filename,exception
    #
    # Gestion des docs
    #

    def _clearDicofound(self):
        self.dico_found = {}

    def _getDicoFound(self,key,type_doc):
        if (key,type_doc) in self.dico_found:
            doc = self.dico_found[(key,type_doc)]
        else:
            doc = False
        return(doc)

    @staticmethod
    def _getReference(filename):
        """
        Get reference like
        ET1234-S
        PQ 0.1.0.155
        GS3058
        ATP100203
        SAQ319
        in the document name
        """
        def replaceUnderscore(txt):
            reference = re.sub(r"(.*)_(.*)",r"\1-\2",txt)
            return reference
        # Documents ET
        m = re.match(r"(.*)(ET[0-9]{4}_[ESV])",filename)
        if m:
            reference = replaceUnderscore(m.group(2))
        else:
            m = re.match(r"(.*)([ETDGSet]{2}[0-9]{4})",filename)
            if m:
                reference = m.group(2).upper()
            else:
                # Documents PQ
                m = re.match(r'(.*)(PQ_[0-9]_[0-9]_[0-9]_[0-9]{3})',filename)
                if m:
                    reference = m.group(2)
                else:
                    # Documents PQ
                    m = re.match(r'(.*)(PQ ?[0-9]\.[0-9]\.[0-9]\.[0-9]{3})',filename)
                    if m:
                        reference = m.group(2)
                    else:
                        # Document 7N
                        m = re.match(r"(.*)(7N_?[0-9]{5})",filename)
                        if m:
                            reference = replaceUnderscore(m.group(2))
                        else:
                            # Document AGILE
                            m = re.match(r"(.*)([A-Z]{3}[0-9]{6})",filename)
                            if m:
                                reference = m.group(2)
                            else:
                                m = re.match(r"^(EQ[0-9]{4}_[0-9]{3})",filename)
                                if m:
                                    reference = m.group(1)
                                else:
                                    # Document SAQ
                                    m = re.match(r"^(SAQ[0-9]{3})",filename)
                                    if m:
                                        reference = m.group(1)
                                    else:
                                        # Document CR
                                        m = re.match(r"^(.*)(CR_[0-9]*)",filename)
                                        if m:
                                            reference = m.group(2)
                                        else:
                                            reference = ""
        return reference
    #
    # Static methods
    #
    @staticmethod
    def getObjectName(m):
        document = m.group(2)
        version = m.group(3)
        instance = m.group(8)
        object_name = "{:s)-{:s}:dir:{:s}".format(document,version,instance)
        return object_name

    @staticmethod
    def removeCRs(res_tbl,cr_included):
        #Remove unexpected CRs
        if cr_included != [] or cr_included != ():
            for cr in res_tbl[:]:
                if str(cr) not in cr_included:
                    res_tbl.remove(cr)

    def _clearDicofound(self):
        self.dico_found = {}

    def _getDicoFound(self,key,type_doc):
        """
        :param key:
        :param type_doc:
        :return:
        """
        if (key,type_doc) in self.dico_found:
            doc = self.dico_found[(key,type_doc)]
        else:
            doc = False
        return(doc)

    def _getSpecificDoc(self,m, key, filter_type_doc=('doc', 'pdf', 'xls', 'ascii')):
        """
            - the name of the document match the name in dictionary
            - the type of the document is doc or pdf or xls or ascii
        """
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
            doc_name = re.sub(r"(.*)\.(.*)", r"\1", document)
            if key in doc_name:
                description, reference = self._getDescriptionDoc(document)
                self.dico_found[key, type_doc] = doc_name + " issue " + version
                result = True
        return result

    def _createTblDocuments(self,
                            m,
                            tbl,
                            link_id,
                            for_sci=False):
        """
        Populate tbl
        :param m:
        :param tbl:
        :param link_id:
        :param for_sci:
        :return:
        """
        release = m.group(1)
        document = m.group(2)
        version = m.group(3)
        task = m.group(4)
        cr = m.group(5)
        type_doc = m.group(6)
        project = m.group(7)
        instance = m.group(8)
        # discard SCI
        doc_name = re.sub(r"(.*)\.(.*)", r"\1", document)
        description, reference = self._getDescriptionDoc(document)
        ##        # Discard peer reviews
        ##        if description not in ("Inspection Sheet","Peer Review Register"):
        # Check if document already exists
        if for_sci:
            # Exclude SCI document
            result = False
            if "SCI_" not in doc_name:
                if type_doc in self.list_type_doc:
                    description,reference = self._getDescriptionDoc(document)
                    if self.getCIDType() not in ("SCI"):
                        tbl.append([release + ":" + project,document,version,description,task])
                    else:
                        tbl.append([description,reference,document,version,type_doc,instance,release,cr])
                    result = True
            return result
        else:
            find = False
            for lref, ldoc_name, lreference, lversion, ldescription in tbl:
                if ldoc_name == doc_name and lreference == reference and lversion == version:
                    find = True
                    break
            if not find and type_doc not in ("project","dir"):
                link_id += 1
                ref = "[R{:d}]".format(link_id)
                tbl.append([ref, document, reference, version, description])
            return link_id

    def _getDescriptionDoc(self,filename):
        '''
        return description of a document if name or keyword is found in database
        '''
        # remove suffix, extension
        description = ""
        reference = ""
        doc_name = re.sub(r"(.*)\.(.*)",r"\1",filename)
        # Look into the user list first
        # Example: SAQ313_PLDRD.doc
        if doc_name in self.dico_descr_docs:
            description = self.dico_descr_docs[doc_name]
            reference = self.dico_descr_docs_ref[doc_name]
        else:
            # Look into the default list then
            find = False
            # Peer review type ?
            if re.match("^PRR_(.*)",doc_name):
                description = self.dico_descr_docs_default["PRR"]
                find = True
            else:
                for key in self.dico_descr_docs_default:
                    if key in doc_name:
                        #TODO: Case where 2 keywords are found
                        description = self.dico_descr_docs_default[key]
                        # find keyword in doc name
                        find = True
            if not find:
                pass
            reference = self._getReference(doc_name)
        return description,reference

    def _getDoc(self,m,dico,filter_type_doc=('doc','pdf','xls','ascii')):
        '''
            Add a document in dictionary if
            - the name of the document match the name in document dictionary
            - the type of the document is doc or pdf
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
            doc_name = re.sub(r"(.*)\.(.*)",r"\1",m.group(2))
            for key in dico:
                if key in doc_name:
                    description,reference = self._getDescriptionDoc(document)
                    description = dico[key]
                    self.dico_found[key,type_doc] = doc_name + " issue " + version
                    print ("DICO_FOUND",self.dico_found)
                    result = True
                    break
        return result

    def _readEOC(self,
                 filename,
                 dico_addr={"hw_sw_compat":("0x400","0x402"),
                            "pn":("0x400","0x424"),
                            "checksum":("0x4DE8","0x4DEA")},
                 dspic=False):
        def string_range(dico_range,
                         dspic=False):
            pn = ""
            if dspic:
                begin = (int(dico_range[0],16) << 1)
                end = (int(dico_range[1],16) << 1)
            else:
                begin = (int(dico_range[0],16))
                end = (int(dico_range[1],16))
            for x in range(begin,end):
                y = ih[x]
                if y >= 0x20 and y < 0x80:
                    #print "{:d}:{:s}".format(x,chr(y))
                    pn += chr(y)
                else:
                    pass
                    #print "TEST:",x,y
            return pn

        def int_range(dico_range,
                      dspic=False):
            pn      = 0
            if dspic:
                decal   = 0
                begin   = (int(dico_range[0],16) << 1)
                end     = (int(dico_range[1],16) << 1)
                for x in range(begin,end):
                    y = ih[x]
                    # integer
                    pn += y << decal
                    decal += 8
                    if decal > 8:
                        break
            else:
                decal   = 24
                begin   = (int(dico_range[0],16))
                end     = (int(dico_range[1],16))
                for x in range(begin,end):
                    y = ih[x]
                    # integer
                    pn += y << decal
                    decal -= 8
                    if decal < 0:
                        break
            pn = "0x{:02x}".format(pn)
            return pn
        name = Tool.getFileName(filename)
        ext = Tool.getFileExt(filename)
        if ext == "srec":
            srec = True
        elif ext == "hex":
            srec = False
        elif not ext:
            srec = False
        else:
            srec = False
            print ("Format not taken into account.")

        if srec:
            #srec
            output = name + "_%d" % floor(time.time())
            stdout,stderr = self.srec_to_intelhex(filename,output)
            filename = "result\\{:s}.hex".format(output)

        ih = IntelHex()
        try:
            ih.fromfile(filename,format='hex')
            #for x in ih:
            #    print "IH",x
            hw_sw_compatibility = int_range(dico_addr["hw_sw_compat"],dspic)
            pn = string_range(dico_addr["pn"],dspic)
            checksum = int_range(dico_addr["checksum"],dspic)
            failed = False
        except IOError as e:
            print ("Read EOC",e)
            pn=""
            checksum=""
            hw_sw_compatibility=""
            failed = stderr + "\n" + str(e)
        return hw_sw_compatibility,pn,checksum,failed

    def getEOCAddress(self):
        if self.config_parser.has_section("EOC"):
            addr_hw_sw_compatibility = self.getOptions("EOC","addr_hw_sw_compatibility")
            addr_pn = self.getOptions("EOC","addr_pn")
            addr_checksum = self.getOptions("EOC","addr_checksum")
            addr_hw_sw_compatibility_range = addr_hw_sw_compatibility.split(",")
            addr_pn_range = addr_pn.split(",")
            addr_checksum_range = addr_checksum.split(",")
            dico_addr={"hw_sw_compat":addr_hw_sw_compatibility_range,
                       "pn":addr_pn_range,
                       "checksum":addr_checksum_range}
        else:
            dico_addr={"hw_sw_compat":("0x400","0x402"),
                       "pn":("0x400","0x424"),
                       "checksum":("0x4DE8","0x4DEA")}
        return dico_addr

    sqlite_query = staticmethod(sqlite_query)
    sqlite_query_one = staticmethod(sqlite_query_one)

# create a subclass and override the handler methods
class MyHTMLParserPlain(HTMLParser):
    def __init__(self,target_tag="cell"):
        HTMLParser.__init__(self)
        self.data = ""
        self.tbl = []
    def handle_starttag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if self.data == "":
            self.tbl.append("")
        self.data = ""
    #def handle_startendtag(self, tag):
    #    print "empty field"
    def handle_data(self, data):
        self.data = data
        self.tbl.append(data)

class MyHTMLParserTable(HTMLParser):
    def __init__(self,target_tag="td"):
        HTMLParser.__init__(self)
        self.data = ""
        self.row = []
        self.tbl = []
    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
            #del(self.row[:])
    def handle_endtag(self, tag):
        if tag == "tr":
            #print "self.row",self.row
            self.tbl.append(self.row)
            #print "self.tbl",self.tbl
        else:
            if self.data == "":
                self.row.append("")
                #self.tbl.append("")
            self.data = ""
    #def handle_startendtag(self, tag):
    #    print "empty field"
    def handle_data(self, data):
        self.data = data
        self.row.append(data)


class MyHTMLParser(HTMLParser):
    def __init__(self,target_tag="cell"):
        HTMLParser.__init__(self)
        self.target_tag = target_tag

    def _createBeacon(self,tag,attrs):
        text = "<" + tag
        for key,value in attrs:
            if key is not None and value is not None:
                attr_inline = ' ' + key + ' =  "'+value+'" '
                text += attr_inline
        text += ">"
        return (text)
    def handle_starttag(self, tag, attrs):
##            print "Encountered a start tag:", tag
        if tag == self.target_tag:
            self.foundCell = True
            for attr in attrs:
                self.attr = attr[1]
        elif self.foundCell:
            try:
                self.text += self._createBeacon(tag,attrs)
            except UnicodeDecodeError as exception:
                pass
            #self.text += "<" + tag + ">"
    def handle_endtag(self, tag):
##            print "Encountered an end tag :", tag
        if tag == self.target_tag:
            self.foundCell = False
            self.tbl.append(self.text)
            if "attr" in self.__dict__:
                self.dico[self.attr] = self.text
            self.text= ""
    def handle_data(self, data):
##            print "Encountered some data  :", data
        if self.foundCell:
            self.text += Tool.replaceNonASCII(data)

class BProc_HTMLParser(HTMLParser):
    def __init__(self,target_tag="cell"):
        HTMLParser.__init__(self)
        self.target_tag = target_tag

    def HighlightPattern(self,text):

        char = {r'"([^"]*)"':r'"<span class="color_signal">\1</span>"',
                r'\'([^\x92]*)\'':r"'<span class='color_value'>\1</span>'"}
        count = 0
        for before, after in char.iteritems():
            count += 1
            #print "{:d}: {:s}".format(count,text)
            text = re.sub(before,after,text)
        text_filtered = text
        return text_filtered

    def _createBeacon(self,tag,attrs):
        text = "<" + tag
        for key,value in attrs:
            if key is not None and value is not None:
                #print "KEY",key
                #print "VALUE",value
                attr_inline = ' {:s}="{:s}"'.format(key,value)
                text += attr_inline
        text += ">"
        return (text)

    def handle_starttag(self, tag, attrs):
##            print "Encountered a start tag:", tag
        if tag == self.target_tag:
            self.foundCell = True
        for attr in attrs:
            self.attr = attr[1]
        try:
            self.text += self._createBeacon(tag,attrs)
        except MemoryError as exception:
            print (exception)
        except UnicodeDecodeError as exception:
            print (exception)

    def handle_endtag(self, tag):
##            print "Encountered an end tag :", tag
        if tag == self.target_tag:
            self.foundCell = False
        try:
            self.text += "</" + tag +  ">"
        except MemoryError as exception:
            print (exception)
        # MemoryError with self.text
        self.tbl.append(self.text)
        if "attr" in self.__dict__:
            self.dico[self.attr] = self.text

    def handle_data(self, data):
##            print "Encountered some data  :", data
        if self.foundCell:
            data = Tool.replaceNonASCII(data)
            data = self.HighlightPattern(data)
        try:
            self.text += data
        except MemoryError as exception:
            print (exception)



if __name__ == "__main__":
    tool = Tool()
    tool.basename = "./qualification/summary"
    tool.listDir("qualification/summary")
    with open(join("result","tu_coverage.txt"), 'w') as of:
        of.write("{:s};{:s};{:s};{:s};{:s}\n".format("File","Statements","Decisions","Basic conditions","Modified conditions"))
        for name,percentage in tool.list_coverage.iteritems():
            of.write("{:s};{:s};{:s};{:s};{:s}\n".format(name,
                                                    percentage["Statement blocks"],
                                                    percentage["Decisions"],
                                                    percentage["Basic conditions"],
                                                    percentage["Modified conditions"],
                                                    ))