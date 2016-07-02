#!/usr/bin/env python 2.7.3
# -*- coding: latin-1 -*-
"""
 easyIG
 Copyright (c) 2013-2014 Olivier Appere
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
 This file get IG from intranet and post process data.
"""
__author__ = "O. Appere <olivier.appere@gmail.com>"
__date__ = "08th of Janury 2015"
__version__ = "1.0.0"
import xml.etree.ElementTree as ET
import sys
import os
import urllib2
from HTMLParser import HTMLParser
import sqlite3 as lite
import re
from datetime import datetime
try:
    from django import setup
    from django.conf import settings
    from django.template.loader import render_to_string
except ImportError:
    print "Django module not found."
from os.path import join
from tool import Tool
from conf import VERSION
from check_llr import CheckLLR
# create a subclass and override the handler methods
class ApiSQLite():
    def sqlite_connect(self):
        try:
            self.con = lite.connect('ig.db3', isolation_level=None)
            #cur = self.con.cursor()
            #cur.execute("DROP TABLE IF EXISTS hlr_vs_chapter")
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
    def sqlite_get(self,req_id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id,req_id,chapter FROM ig_vs_category WHERE req_id LIKE '" + req_id + "' LIMIT 1")
            data = cur.fetchone()
            if data is not None:
                #print "DATA:",data
                id = data[0]
                req_id = data[1]
                chapter = data[2]
        return chapter
    def sqlite_get_child(self,parent_id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT child_id FROM docs_depend WHERE parent_id LIKE '{:d}'".format(parent_id))
            data = cur.fetchall()
            if data is not None:
                return data
            else:
                return False
    def sqlite_get_docs_certification(self,id=0):
        with self.con:
            cur = self.con.cursor()
            if id == 0:
                cur.execute("SELECT type,reference,indice,title,link FROM docs_certification")
            else:
                if id[0] != "":
                    cur.execute("SELECT type,reference,indice,title,link FROM docs_certification WHERE id LIKE '{:d}'".format(int(id[0])))
            data = cur.fetchall()
        return data
    def sqlite_get_groupe(self,groupe_id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id,description FROM groupes WHERE groupe LIKE '{:s}' LIMIT 1".format(groupe_id))
            data = cur.fetchone()
            if data is not None:
                id = data[0]
                description = data[1]
            else:
                id = None
                description = None
        return id,description
    def sqlite_get_sous_groupe(self,groupe_id,sous_groupe_id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id,description FROM sous_groupes WHERE groupe LIKE '{:s}' AND sous_groupe LIKE '{:s}' LIMIT 1".format(groupe_id,sous_groupe_id))
            #print "SQL_SOUS_GROUP","SELECT id,description FROM sous_groupes WHERE groupe LIKE '{:s}' AND sous_groupe LIKE '{:s}' LIMIT 1".format(groupe_id,sous_groupe_id)
            data = cur.fetchone()
            if data is not None:
                id = data[0]
                description = data[1]
            else:
                id = None
                description = None
            #print id,description
        return id,description
    def sqlite_get_articulation(self,groupe_id,sous_groupe_id,articulation_id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id,description FROM articulations WHERE groupe LIKE '{:s}' AND sous_group LIKE '{:s}' AND articulation LIKE '{:s}' LIMIT 1".format(groupe_id,sous_groupe_id,articulation_id))
            data = cur.fetchone()
            if data is not None:
                id = data[0]
                description = data[1]
            else:
                id = None
                description = None
        return id,description
    def sqlite_read_categories(self):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id,name FROM categories")
            data = cur.fetchall()
        return data
    def sqlite_delete(self):
        try:
            #self.con = lite.connect('swrd_enm.db3', isolation_level=None)
            cur = self.con.cursor()
            cur.execute("DROP TABLE IF EXISTS ig_vs_category")
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
    def sqlite_insert_many(self,tbl_ig):
        with self.con:
            cur = self.con.cursor()
            cur.executemany("INSERT INTO ig_vs_category(id,reference,category_id) VALUES(?,?,?)", tbl_ig)
            self.con.commit()
    def sqlite_create(self):
        try:
            #con = lite.connect('swrd_enm.db3')
            cur = self.con.cursor()
            cur.executescript("""
                                BEGIN TRANSACTION;
                                CREATE TABLE ig_vs_category (id INTEGER PRIMARY KEY, reference TEXT, category_id NUMERIC);
                                COMMIT;
                """)
            self.con.commit()
            print 'New SQLite table created.'
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
    def sqlite_get_category(self,reference,category = "FPGA"):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT categories.name FROM ig_vs_category LEFT OUTER JOIN categories ON category_id = categories.id WHERE reference LIKE '" + reference + "' AND categories.name LIKE '" + category + "' LIMIT 1")
            data = cur.fetchone()
            if data is not None:
                category = data[0]
            else:
                category = False
        return category
    def sqlite_get_char(self,reference):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT header,obsolete FROM ig_vs_category WHERE reference LIKE '" + reference + "' LIMIT 1")
            data = cur.fetchone()
            header = False
            obsolete = False
            if data is not None:
                if data[0] not in (None,u''):
                    if data[0] == 0:
                        header = False
                    else:
                        header = True
                else:
                    header = False
                if data[1] not in (None,u''):
                    if data[1] == 0:
                        obsolete = False
                    else:
                        obsolete = True
                else:
                    obsolete = False
        return header,obsolete
class MyHTMLParser(HTMLParser,ApiSQLite):
    def __init__(self,header,saq_requested=False):
        HTMLParser.__init__(self)
        self.header = header
        self.found_table =False
        self.found_start_header_cell = False
        self.found_start_cell = False
        self.found_end_cell = False
        self.start_table_line = False
        #self.header = []
        self.row = {}
        self.list_ig = []
        self.link = ""
        self.new = False
        self.header_index = 0
        self.text = ""
        self.saq_requested = saq_requested
        self.color_flag = 0
    def getListSAQ(self,dico_ig_tbl_saq,dico_saq):
        tbl_ig_vs_saq = []
        list_ig = []
        for dico in self.list_ig:
            ig = dico["Procedure"]
            saq = dico["Reference"]
            version = dico["Indice"]
            description = dico["Titre"]
            link = dico["Link"]
            #print "LIST SAQ:",saq,link
            dico_saq[saq] = {"Indice":version,"Titre":description,"Link":link}
            #print "DICO:",dico["Reference"],dico["Procedure"]
            tbl_ig_vs_saq.append((ig,saq))
            if ig not in list_ig:
                list_ig.append(ig)
        for ig in list_ig:
            tbl = []
            for ig2,saq in tbl_ig_vs_saq:
                if ig2 == ig:
                    tbl.append(saq)
            dico_ig_tbl_saq[ig] = tbl
        #print "IG_VS_SAQ:",tbl_ig_vs_saq
        #print "IG:",list_ig
        #print "DICO:",dico_ig_tbl_saq
    def encode_for_xml(self,unicode_data, encoding='ascii'):
        """
        Encode unicode_data for use as XML or HTML, with characters outside
        of the encoding converted to XML numeric character references.
        """
        def _xmlcharref_encode(unicode_data, encoding):
            """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
            chars = []
            # Step through the unicode_data string one character at a time in
            # order to catch unencodable characters:
            for char in unicode_data:
                try:
                    chars.append(char.encode(encoding, 'strict'))
                except UnicodeError:
                    chars.append('&#%i;' % ord(char))
            str = ''.join(chars)
            return str
        try:
            return unicode_data.encode(encoding, 'xmlcharrefreplace')
        except ValueError:
            # ValueError is raised if there are unencodable chars in the
            # data and the 'xmlcharrefreplace' error handler is not found.
            # Pre-2.3 Python doesn't support the 'xmlcharrefreplace' error
            # handler, so we'll emulate it.
            return _xmlcharref_encode(unicode_data, encoding)
    def handle_starttag(self, tag, attrs):
        if ('class','Documentation') in attrs:
            self.found_table = True
            #print "Encountered a start table tag:", tag
        if self.found_table:
            if self.start_table_line:
                if self.found_start_cell:
                    if tag == "a":
                        # Take first hyperlink for SAQ
                        href = attrs[0][1]
                        m = re.search(r'dq_form_data',href)
                        if m:
                            # SAQ
                            if self.saq_requested:
                                self.link = attrs[0][1]
                        else:
                            # IG
                            if not self.saq_requested:
                                self.link = attrs[0][1]
                    elif tag == "font":
                        #print "COLOR:",attrs
                        self.new = True
                        #print new
                else:
                    if tag == "th":
                        #print "Encountered a start header cell tag:", tag
                        self.found_start_header_cell = True
                        self.row = {}
                    elif tag == "td":
                        #print "Encountered a start cell tag:", tag
                        #print "Debut TD"
                        self.found_start_cell = True
                        self.found_end_cell = False
            if tag == "tr":
                #print "Encountered a start line tag:", tag
                self.start_table_line = True
                self.link = ""
                self.new = False
    def handle_endtag(self, tag):
        if self.found_table:
            #print "Encountered an end tag :", tag
            if self.start_table_line:
                if tag == "td":
                    self.found_start_cell = False
                    #print "Fin TD"
                    self.found_end_cell = True
                elif tag == "th":
                    self.found_start_header_cell = False
                elif tag == "tr":
                    self.start_line = False
                    #print "End line"
                    self.found_end_cell = False
                    if self.row != {}:
                        self.row[self.header[self.header_index]] = self.link
                        self.header_index += 1
                        self.row[self.header[self.header_index]] = self.new
                        self.list_ig.append(self.row)
                        #print self.row
                        self.row = {}
                    self.header_index = 0
    def handle_data(self, data):
        if self.found_table:
            if self.found_start_header_cell:
                pass
                #self.header.append(data)
                #print "Encountered some data  :", data
            elif self.found_start_cell:
                #print "DATA",data
                data_converted = self.encode_for_xml(data,'ascii')
                #data_converted = self.unescape(data)
                self.text += data_converted
                #print "Encountered some data  :", data
            elif self.found_end_cell:
                #print self.header_index
                #print self.header[self.header_index]
                #print self.text
                self.row[self.header[self.header_index]] = self.text
                self.header_index += 1
                self.text = ""
    def createWarning(self,beacon,txt):
        txt_tbl = txt.split("\n")
        div = ET.SubElement(beacon, "div",attrib={"class":"warning","style":"list-style-type: none;margin-top:0px;margin-right:10px"})
        for row in txt_tbl:
            p = ET.SubElement(div, "p")
            m = re.match(r'^http://.*',row)
            if m:
                url = ET.SubElement(p,"a",attrib={"href":row})
                url.text = row
            else:
                txt_html = self.encode_for_xml(row)
                p.text = txt_html
        return div
    def createLinkCss(self,beacon,file,attrib={"class":""}):
        link = ET.SubElement(beacon, "link")
        link.set("rel", "stylesheet")
        link.set("type", "text/css")
        link.set("href", file)
        return link
    def createLinkJS(self,beacon,file,attrib={"class":""}):
        link = ET.SubElement(beacon, "script")
        link.set("type", "text/javascript")
        link.set("src", file)
        link.text = "dummy"
        return link
    def createParagraph(self,beacon,txt,attrib={"class":""}):
        div = ET.SubElement(beacon, "p",attrib)
        div.text = self.encode_for_xml(txt)
        return div
    def alternColor(self,ul_beacon,type,reference,title,version,link):
        self.color_flag += 1
        li = ET.SubElement(ul_beacon, "li",attrib={"style":"width:800px"})
        hyperlink = ET.SubElement(li, "a",attrib={"class":"wide"})
        if version not in ("",None):
            hyperlink.text ="{:s} {:s} version {:s}: {:s} ".format(type,reference,version,title)
        else:
            hyperlink.text ="{:s} {:s} {:s} ".format(type,reference,title)
        hyperlink.set("href", link)
        if self.color_flag % 2:
            li.set("class","dark")
        else:
            li.set("class","light")
        header,obsolete = self.sqlite_get_char(reference)
        if header and obsolete:
            hyperlink.set("class","wide obsolete_and_header")
        elif header:
            hyperlink.set("class","wide top_ig")
        elif obsolete:
            hyperlink.set("class","wide obsolete")
        else:
            pass
    def getChild(self,ul_group,parent_id):
        keys =["Type","Reference","Indice","Titre","Link"]
        list = self.sqlite_get_child(parent_id)
        for child_id in list:
            cert_doc = self.sqlite_get_docs_certification(child_id)
            #print "DATA",data
            #li = ET.SubElement(ul_group, "li",attrib={"class":"group"})
            #hyperlink = ET.SubElement(li, "a",attrib={"class":"short"})
            #hyperlink.text = "DO-178"
            for tbl in cert_doc:
                dico = dict(zip(keys, tbl))
                type = dico["Type"]
                reference = dico["Reference"]
                title = dico["Titre"]
                link = "doc/{:s}".format(dico["Link"])
                version = dico["Indice"]
                self.alternColor(ul_group,
                                 type,
                                 reference,
                                 title,
                                 version,
                                 link)
    def createListCert(self,parent_beacon,category=""):
        div = ET.SubElement(parent_beacon, "div",attrib={"id":"menu"})
        ul_group = ET.SubElement(div, "ul",attrib={"class":"top_group level-one"})
        hyperlink = ET.SubElement(ul_group, "a",attrib={"class":"short selected"})
        hyperlink.text = "ARP-4754"
        doc = self.sqlite_get_docs_certification((5,))
        hyperlink.set("href","doc/{:s}".format(doc[0][4]))
        self.getChild(ul_group,5)
        ul_group = ET.SubElement(div, "ul",attrib={"class":"top_group level-one"})
        hyperlink = ET.SubElement(ul_group, "a",attrib={"class":"short selected"})
        hyperlink.text = "DO-178"
        doc = self.sqlite_get_docs_certification((2,))
        hyperlink.set("href","doc/{:s}".format(doc[0][4]))
        self.getChild(ul_group,2)
        ul_group = ET.SubElement(div, "ul",attrib={"class":"top_group level-one"})
        hyperlink = ET.SubElement(ul_group, "a",attrib={"class":"short selected"})
        hyperlink.text = "DO-254"
        doc = self.sqlite_get_docs_certification((4,))
        hyperlink.set("href","doc/{:s}".format(doc[0][4]))
        self.getChild(ul_group,4)
        if 0 == 1:
            cert_doc = self.sqlite_get_docs_certification()
            for tbl in cert_doc:
                dico = dict(zip(keys, tbl))
                type = dico["Type"]
                reference = dico["Reference"]
                title = dico["Titre"]
                link = "doc/{:s}".format(dico["Link"])
                version = dico["Indice"]
                self.alternColor(ul_group,
                                 type,
                                 reference,
                                 title,
                                 version,
                                 link)
    def createListIG(self,beacon,item="FPGA"):
        color_flag = 0
        ul_fpga_group = ET.SubElement(beacon, "ul",attrib={"class":"group"})
        if item == "New":
            list = []
            for dico in self.list_ig:
                date = dico["Application"]
                m = re.match(r'^([0-9]{2})\/([0-9]{2})\/([0-9]{2})$',date)
                if m:
                    day = m.group(1)
                    month = m.group(2)
                    year = m.group(3)
                    if int(year) > 50:
                        century = 19
                    else:
                        century = 20
                    new_date = "{:d}{:s}-{:s}-{:s}".format(century,year,month,day)
                    if dico["New"]:
                        list.append((new_date,dico["Reference"],dico["Type"],dico["Titre"],dico["Link"],dico["Indice"]))
            sorted_list = sorted(list,reverse=True)
            for row in sorted_list:
                date = row[0]
                reference = row[1]
                type = row[2]
                title = row[3]
                link = row[4]
                version = row[5]
                color_flag += 1
                li3 = ET.SubElement(ul_fpga_group, "li")
                hyperlink = ET.SubElement(li3, "a")
                hyperlink.text ="{:s} {:s}: {:s} version {:s} published date: {:s}".format(type,reference,title,version,date)
                hyperlink.set("href", link)
                if color_flag % 2:
                    li3.set("class","dark")
                else:
                    li3.set("class","light")
                header,obsolete = self.sqlite_get_char(reference)
                if header and obsolete:
                    hyperlink.set("class","obsolete_and_header")
                elif header:
                    hyperlink.set("class","top_ig")
                elif obsolete:
                    hyperlink.set("class","obsolete")
                else:
                    pass
        else:
            for dico in self.list_ig:
                type = dico["Type"]
                reference = dico["Reference"]
                title = dico["Titre"]
                link = dico["Link"]
                version = dico["Indice"]
                date = dico["Application"]
                #tbl.append((index,reference,0))
                #index += 1
                category = self.sqlite_get_category(reference,item)
                if category == item:
                    self.alternColor(ul_fpga_group,
                                     type,
                                     reference,
                                     title,
                                     version,
                                     link)
                    if 0==1:
                        color_flag += 1
                        li3 = ET.SubElement(ul_fpga_group, "li")
                        hyperlink = ET.SubElement(li3, "a")
                        hyperlink.text ="{:s} {:s}: {:s} version {:s}".format(type,reference,title,version)
                        hyperlink.set("href", link)
                        if color_flag % 2:
                            li3.set("class","dark")
                        else:
                            li3.set("class","light")
                        header,obsolete = parser.sqlite_get_char(reference)
                        if header and obsolete:
                            hyperlink.set("class","obsolete_and_header")
                        elif header:
                            hyperlink.set("class","top_ig")
                        elif obsolete:
                            hyperlink.set("class","obsolete")
                        else:
                            pass
class IG():
    def __init__(self,
                 group="",
                 sub_group="",
                 artic="",
                 title="",
                 date="",
                 link="",
                 list_saq=[],
                 obsolete=""):
        self.date = date
        self.title = title
        self.link = link
        self.artic = artic
        self.group = group
        self.sub_group = sub_group
        self.list_saq = list_saq
        if obsolete:
            self.obsolete = "obsolete"
        else:
            self.obsolete = ""
        if len(list_saq) > 0:
            self.saq_exist = True
        else:
            self.saq_exist = False
class getQA(ApiSQLite):
    """
    Use the E-factory from lxml.builder which provides a simple and compact syntax for generating XML and HTML
    """
    def __init__(self,filename=""):
        if filename == "":
            self.filename = "getQA.html"
        else:
            self.filename = filename
        # Django settings
        try:
            settings.configure(DEBUG=False,
                               TEMPLATE_DEBUG=False,
                               TEMPLATE_LOADERS=('django.template.loaders.filesystem.Loader',
                                                'django.template.loaders.app_directories.Loader'),
                               TEMPLATE_DIRS=('template',))
            setup()
        except NameError:
            print "Missing Django module."
        except RuntimeError:
            print "Settings already configured."
    def start(self):
        try:
            print "start filename:",self.filename
            os.startfile(self.filename)
        except AttributeError,e:
            print e
        except WindowsError,e:
            print e

    def get(self,
            qams_user_id,
            action_id=False,
            url_root="localhost",
            name=""):
        url = "http://{:s}/qams/atomik/index.php?action=export/export_docid_actions_list&user_id={:d}".format(url_root,qams_user_id)
        if action_id:
            url += "&action_id={:d}".format(action_id)
        print "URL:",url
        try:
            response = urllib2.urlopen(url)
            tbl_actions_html = response.read()
        except IOError,e:
            tbl_actions_html = e
            print e
        date = datetime.now().strftime('%A %d %b %Y')
        heure = datetime.now().strftime('%H:%M:%S')
        generated = "List of open action items for {:s}. ".format(name)
        generated += "Page created by doCID version {:s} on {:s} at {:s}".format(VERSION,date,heure)
        try:
            rendered = render_to_string('get_qa_template.html', {'tbl_actions':tbl_actions_html,'GENERATED_DATE':generated})
        except NameError,e:
            rendered = "<p>Django module not found.</p>"
            print e
        rendered_filtered = Tool.replaceNonASCII(rendered)
        with open(self.filename, 'w') as html_handler:
            try:
                html_handler.write(rendered_filtered)
            except UnicodeEncodeError,e:
                print e
        return self.filename

class exportCR_HTML(ApiSQLite,getQA):
    def __init__(self):
        getQA.__init__(self,filename="export_cr_mapping.html")
    def get(self):
        pass
    def exportHTML(self,
                   list_cr=[],
                   list_cr_children=[],
                   list_cr_bottom_up=[],
                   list_cr_parent=[],
                   list_cr_errors=[],
                   dico_log_errors={},
                   database=""):
        nb_crs = len(list_cr)
        nb_crs_bottom_up = len(list_cr_bottom_up)
        date = datetime.now().strftime('%A %d %b %Y')
        heure = datetime.now().strftime('%H:%M:%S')
        generated = "Page created by doCID version {:s} on {:s} at {:s}".format(VERSION,date,heure)
        try:
            print "list_cr_bottom_up",list_cr_bottom_up
            print "list_cr_errors",list_cr_errors
            print "dico_log_errors",dico_log_errors
            rendered = render_to_string('cr_report.html', {'list_cr':list_cr,
                                                           'list_cr_children':list_cr_children,
                                                           'list_cr_bottom_up':list_cr_bottom_up,
                                                           'list_cr_parent':list_cr_parent,
                                                           'list_cr_errors':list_cr_errors,
                                                           'dico_log_errors':dico_log_errors,
                                                            'nb_crs':nb_crs,
                                                            'nb_crs_bottom_up':nb_crs_bottom_up,
                                                            'GENERATED_DATE':generated,
                                                            'database':database})
        except NameError,e:
            rendered = "<p>Django rendering failed.</p>"
            print e
        with open(self.filename, 'w') as html_handler:
            html_handler.write(rendered)
        return self.filename

class exportSCOD_HTML(ApiSQLite,getQA):
    def __init__(self):
        getQA.__init__(self,filename="export_is_synthesis.html")

    def get(self):
        pass

    def exportHTML(self,
                   list_reqs_spec={},
                   list_llr_per_hlr={},
                   list_hlr_per_llr={},
                   list_code_per_llr={},
                   list_llr_per_code={},
                   user_dir=("","","","")):
        date = datetime.now().strftime('%A %d %b %Y')
        heure = datetime.now().strftime('%H:%M:%S')
        generated = "Page created by doCID version {:s} on {:s} at {:s}".format(VERSION,date,heure)
        tbl_group = []
        tbl_sub_group = []
        tbl_articulation = []
        tbl_ig = []
        nb_reqs = 0
        index_group = 1
        # First tab top -> bottom
        for req_id in list_reqs_spec:
            tbl_group.append((index_group,req_id,"TEST"))
            if req_id in list_llr_per_hlr:
                index_sub_group = 1
                for low_level_req_id in list_llr_per_hlr[req_id]:
                    #tbl_sub_group.append((index_group,index_sub_group,low_level_req_id))
                    csu_id = re.sub(r"\w*(CSC[0-9]{3}_CSU[0-9]{3})_[0-9]{3}",r"\1",low_level_req_id)

                    if csu_id in list_code_per_llr:
                        #print "list_code_per_llr[csu_id][0]",list_code_per_llr[csu_id][0]
                        func_name = list_code_per_llr[csu_id][1]
                        source_code = list_code_per_llr[csu_id][0]
                        source_code_name = list_code_per_llr[csu_id][2]
                        #current_dir = user_dir[0] # os.getcwd()
                        link_code = join(user_dir[0],user_dir[1])
                        link_code = join(link_code,source_code)
                        link_llr = join(user_dir[0],user_dir[2])
                        link_llr = join(link_llr,func_name)
                        llr_obj = IG(title=low_level_req_id,
                                          link="file:///{:s}".format(link_llr))
                        src_code_obj = IG(title=source_code_name,
                                          link="file:///{:s}".format(link_code))
                        tbl_sub_group.append((index_group,src_code_obj,llr_obj))
                        #tbl_articulation.append((index_group,index_sub_group,0,list_code_per_llr[csu_id][0]))
                    else:
                        src_code_obj = IG(title="",
                                          link="#")
                        tbl_sub_group.append((index_group,src_code_obj,low_level_req_id))
                    index_sub_group += 1
            index_group += 1
        # Second tab: Bottom -> up
        index_src_files = 1
        tbl_src_files = []
        tbl_hlrs = []
        for source_file,values in list_llr_per_code.iteritems():
            llr_name = values[0] #CSC001_CSU002
            func_name = values[1]
            csu_func_name = values[2]
            source_code_name = values[3]
            tbl_src_files.append((index_src_files,source_file,"TEST"))
            if llr_name in list_hlr_per_llr:
                index_sub_group = 1
                current_dir = user_dir[0] #os.getcwd()
                link_llr = join(user_dir[0],user_dir[2])
                link_llr = join(link_llr,func_name)
                llr_obj = IG(title=llr_name,
                             group=csu_func_name,
                             link="file:///{:s}".format(link_llr))
                for high_level_req_id in list_hlr_per_llr[llr_name]:
                    tbl_hlrs.append((index_src_files,"{:s}".format(high_level_req_id),llr_obj))
            index_src_files += 1
        # Reverse list_code_per_llr
        try:
            #print "tbl_doc_items_rules",tbl_doc_items_rules
            #print "tbl_group",tbl_group
            #print "tbl_sub_group",tbl_sub_group
            print "tbl_hlrs",tbl_hlrs
            rendered = render_to_string('scod_template.html', {'tbl_group':tbl_group,
                                                            'tbl_sub_group':tbl_sub_group,
                                                            'tbl_src_files': tbl_src_files,
                                                            'tbl_hlrs': tbl_hlrs,
                                                            'tbl_ig':tbl_ig,
                                                            'NB_REQS':nb_reqs,
                                                            'GENERATED_DATE':generated})
        except NameError,e:
            rendered = "<p>Django rendering failed.</p>"
            print e
        except MemoryError,e:
            rendered = "<p>Django rendering failed due to memory error.</p>"
            print e
        with open(self.filename, 'w') as html_handler:
            html_handler.write(rendered)
        return self.filename

class exportIS_HTML(ApiSQLite,getQA):
    def __init__(self):
        getQA.__init__(self,filename="export_is_synthesis.html")
    def get(self):
        pass
    def exportHTML(self,
               doc_upper="",
               doc_inspected="",
               filename_is="",
               spec_available=True,
               list_reqs_is={},
               dico_errors={},
               list_reqs_spec={},
               list_cr=[],
               list_cr_not_found=[], # List of CRs not found in CONTEXT folder of IS
               target_release="",
               dico_list_applicable_docs=[]):
        # Prepare HTML document
        #print "exportHTML:list_reqs",list_reqs
        #print "exportHTML:dico_errors",dico_errors
        #print "exportHTML:list_reqs_spec",list_reqs_spec
        def remove_zero(rule):
            rule.lstrip('0')
            return rule
        color_flag = 0
        ul_root = ET.Element('ul')
        tbl_group = []
        tbl_sub_group = []
        tbl_articulation = []
        tbl_ig = []
        index_group = 1
        # Requirements folder
        for req in list_reqs_is["REQ_ANALYSIS"]:
            found_error = False
            found_req_analysis_error = False
            found_req_review_error = False
            found_upper_req_analysis_error = False
            found_status_error = False
            req_id = req[0]
            if req_id in list_reqs_spec:
                value = list_reqs_spec[str(req_id)]
                refer = CheckLLR.getAtribute(value,"refer")
                status = CheckLLR.getAtribute(value,"status")
                rationale = CheckLLR.getAtribute(value,"rationale")
                if status in ("TBD","TBC"):
                    found_error = True
                    found_status_error = True
                    txt = rationale
                    tbl_articulation.append((index_group,3,0,txt))
                    #print "REQUIREMENT NOT MATURE",req_id
            else:
                value = ""
                refer = ""
                status = ""
                rationale = ""
            # List errors
            #for status,is_rule,folder,req_id_error,srts_rule,comment in dico_errors.iteritems():
            # IS Check report with errors
            index_sub_group = 0
            for list,error in dico_errors.iteritems():
                type = "ERROR"
                status,rule_tag,localisation,req_id_error,rule = list
                if req_id == req_id_error:
                    found_error = True
                    if rule == "":
                        rule = rule_tag
                    #tbl_sub_group.append((index_group,0,txt))
                    print "RULE:",rule
                    print "ERROR:",error[0]
                    txt = "{:s}: {:s}".format(str(rule),error[0])
                    #build_list_req_failed.append
                    if localisation == "REQ REVIEW":
                        found_req_review_error = True
                        tbl_articulation.append((index_group,0,0,txt))
                        #list_req_review.append(req_id_error)
                    elif localisation == "REQ ANALYSIS":
                        found_req_analysis_error = True
                        tbl_articulation.append((index_group,1,0,txt))
                        #list_req_analysis.append(req_id_error)
                else:
                    # Refered to upper requirement problem
                    if localisation == "UPPER REQ ANALYSIS":
                        # Check if upper requirement is linked to this requirement
                        if req_id in list_reqs_spec:
                            if req_id_error not in ("",None) and req_id_error in refer:
                                found_error = True
                                found_upper_req_analysis_error = True
                                #print "REQUIREMENT UPPER PB",req_id,req_id_error
                                txt = "{:s}: {:s}".format(req_id_error,error[0])
                                tbl_articulation.append((index_group,2,0,txt))
            if found_error:
                tbl_group.append((index_group,req_id,status))
                if found_req_review_error:
                    tbl_sub_group.append((index_group,0,"REQ REVIEW"))
                if found_req_analysis_error:
                    tbl_sub_group.append((index_group,1,"REQ ANALYSIS"))
                if found_upper_req_analysis_error:
                    tbl_sub_group.append((index_group,2,"UPPER REQ ANALYSIS"))
                if found_status_error:
                    tbl_sub_group.append((index_group,3,"MATURITY"))
                index_group += 1
            #if not found_error:
            #        tbl_sub_group.append((index_group,0,"No errors."))
        nb_reqs = index_group
        # Upper requirements folder
        index_upper_req_id = 0
        tbl_upper_req_id = []
        tbl_upper_req_defects = []
        for upper_req in list_reqs_is["UPPER_REQ_ANALYSIS"]:
            upper_req_id = upper_req[0]
            index_upper_req = 0
            found_error = False
            for list,error in dico_errors.iteritems():
                status,rule_tag,localisation,upper_req_id_error,rule = list
                if upper_req_id == upper_req_id_error:
                    found_error = True
                    if localisation == "UPPER REQ ANALYSIS":
                        txt = "{:s}: {:s} {:s}".format(upper_req_id_error,rule_tag,error[0])
                        tbl_upper_req_defects.append((index_upper_req_id,
                                                      index_upper_req,
                                                      txt))
                        index_upper_req += 1
            if found_error:
                tbl_upper_req_id.append((index_upper_req_id,
                                         upper_req_id)) # Ex: SDTS_WDS_035
                index_upper_req_id += 1
        nb_upper_reqs = index_upper_req_id
        # Document global items folder
        found_doc_item_error = False
        index_doc_item = 0
        tbl_doc_items_rules = []
        for list,error in dico_errors.iteritems():
            status,rule_tag,localisation,req_id_error,rule = list
            if localisation == "DOC REVIEW" or localisation == "REVIEW":
                found_doc_item_error = True
                header = "{:s}: {:s}".format(req_id_error,error[0]) #,rule)
                # get rule description
                id = re.sub(r"(.*)_([0-9]{2})",r"\2",req_id_error)
                #id.lstrip('0')
                result = Tool.getSRTS_Rule(id)
                print "rule_text",result
                if result:
                    rule_text = "Rule {:s}: {:s}<br/>".format(req_id_error,Tool.replaceNonASCII(result,html=True))
                else:
                    rule_text = "Rule undefined."
                list_remarks = []
                if rule:
                    #print "RULE:",rule
                    # rule.lstrip('0')321415
                    tbl_remarks = rule.split(",")
                    tbl_remarks = map(remove_zero,tbl_remarks)
                    #print "tbl_remarks", tbl_remarks
                    for id,remarks,loc,author,item,origin,analysis,status,cr,verif,review in list_reqs_is["REMARKS"]:
                        #print "ID:",id
                        if id is not None and unicode(id) in tbl_remarks:
                            #print "remarks in doc_review",remarks
                            remark = "Remark {:s} from {:s}: {:s}<br/>".format(rule,
                                                                               Tool.replaceNonASCII(author),
                                                                               Tool.replaceNonASCII(remarks,html=True))
                            answer = "Answer: {:s}".format(Tool.replaceNonASCII(analysis,html=True))
                            list_remarks.append((remark,answer))
                tbl_doc_items_rules.append((index_doc_item,
                                            header,
                                            rule_text,
                                            status,
                                            list_remarks
                ))
                index_doc_item += 1
        nb_rules = index_doc_item
        # Baseline
        tbl_list_input_documents = []
        print "tbl_list_applicable_docs",dico_list_applicable_docs
        for name,reference in dico_list_applicable_docs.iteritems():
            tbl_list_input_documents.append("{:s} {:s}".format(name,reference))
        nb_input_docs = len(tbl_list_input_documents)
        # Input CRs
        # ID, synopsis, type, status, detected_on, implemented_for, in_is
        tbl_list_input_crs = []
        for input_cr in list_reqs_is["CONTEXT"]:
            if input_cr[0] in list_cr_not_found:
                input_cr[1] += "<p>CR not implemented for release {:s} (not in CONTEXT folder)</p>".format(target_release)
                input_cr.append(False)
            else:
                input_cr.append(True)
            tbl_list_input_crs.append(input_cr)
        nb_input_crs = len(tbl_list_input_crs)
        #print "tbl_list_input_crs",tbl_list_input_crs
        #for not_found_cr in list_cr_not_found:
        #    tbl_list_input_crs.append([not_found_cr,"CR not implemented for release {:s}".format(target_release),"","","",""])
        # Output CRs
        # Remarks open and CR related
        tbl_list_crs = list_cr
        tbl_list_crs.sort()
        print "tbl_list_crs",tbl_list_crs
        nb_crs = len(list_cr)
        date = datetime.now().strftime('%A %d %b %Y')
        heure = datetime.now().strftime('%H:%M:%S')
        generated = "Page created by doCID version {:s} on {:s} at {:s}".format(VERSION,date,heure)
        try:
            #print "tbl_doc_items_rules",tbl_doc_items_rules
            rendered = render_to_string('is_report.html', {'tbl_group':tbl_group,
                                                            'tbl_sub_group':tbl_sub_group,
                                                            'tbl_articulation': tbl_articulation,
                                                            'tbl_ig':tbl_ig,
                                                            'NB_REQS':nb_reqs,
                                                            'tbl_upper_req_id':tbl_upper_req_id,
                                                            'tbl_upper_req_defects':tbl_upper_req_defects,
                                                            'NB_UPPER_REQS':nb_upper_reqs,
                                                            'tbl_doc_items_rules':tbl_doc_items_rules,
                                                            'NB_RULES':nb_rules,
                                                            'tbl_list_input_documents':tbl_list_input_documents,
                                                            'NB_INPUT_DOCS':nb_input_docs,
                                                            'tbl_list_input_crs':tbl_list_input_crs,
                                                            #'tbl_list_cr_not_found':tbl_list_cr_not_found,
                                                            'NB_INPUT_CRS':nb_input_crs,
                                                            'tbl_list_crs':tbl_list_crs,
                                                            'NB_CRS':nb_crs,
                                                            'status_impl':("Fixed","Closed"),
                                                            'GENERATED_DATE':generated})
        except NameError,e:
            rendered = "<p>Django rendering failed.</p>"
            print e
        except MemoryError,e:
            rendered = "<p>Django rendering failed due to memory error.</p>"
            print e
        with open(self.filename, 'w') as html_handler:
            html_handler.write(rendered)
        return self.filename

class easyIG(ApiSQLite):
    """
    Use the E-factory from lxml.builder which provides a simple and compact syntax for generating XML and HTML
    """
    def start(self):
        os.startfile(self.filename)
    def createListNewIG(self,item="FPGA",list_ig={},tbl_ig_items=[]):
        list = []
        #self.sqlite_connect()
        for dico in list_ig:
            #category = self.sqlite_get_category(dico["Reference"],item)
            #if category == item:
            date = dico["Application"]
            m = re.match(r'^([0-9]{2})\/([0-9]{2})\/([0-9]{2})$',date)
            if m:
                day = m.group(1)
                month = m.group(2)
                year = m.group(3)
                if int(year) > 50:
                    century = 19
                else:
                    century = 20
                new_date = "{:d}{:s}-{:s}-{:s}".format(century,year,month,day)
                if dico["New"]:
                    list.append((new_date,dico["Reference"],dico["Type"],dico["Titre"],dico["Link"],dico["Indice"]))
        sorted_list = sorted(list,reverse=True)
        for row in sorted_list:
            date = self.PrettyDate(row[0])
            reference = row[1]
            type = row[2]
            title = row[3]
            link = row[4]
            version = row[5]
            if version is not None:
                title ="{:s} {:s} version {:s}: {:s}".format(type,reference,version,title)
            else:
                title ="{:s} {:s}: {:s}".format(type,reference,title)
            ig = IG(group="",
                    sub_group = "",
                    artic="",
                    title=title,
                    date=date,
                    link=link,
                    list_saq=[])
            tbl_ig_items.append(ig)
    def PrettyDate(self,date):
        try:
            d = datetime.strptime(date, '%Y-%m-%d')
            date = d.strftime('%A %d %b %Y')
        except ValueError:
            pass
        return date
    def createListIG(self,
                     item="FPGA",
                     list_ig={},
                     tbl_ig_items=[]):
        list = []
        self.sqlite_connect()
        if item == "Certification":
            for id in range(1,14):
                doc = self.sqlite_get_docs_certification((id,))
                link = "doc/{:s}".format(doc[0][4])
                type = doc[0][0]
                reference = doc[0][1]
                version = doc[0][2]
                title = doc[0][3]
                list.append((id,reference,type,title,link,version))
            print "LIST CERT:",list

        else:
            for dico in list_ig:
                category = self.sqlite_get_category(dico["Reference"],item)
                if category == item:
                    date = dico["Application"]
                    m = re.match(r'^([0-9]{2})\/([0-9]{2})\/([0-9]{2})$',date)
                    if m:
                        day = m.group(1)
                        month = m.group(2)
                        year = m.group(3)
                        if int(year) > 50:
                            century = 19
                        else:
                            century = 20
                        new_date = "{:d}{:s}-{:s}-{:s}".format(century,year,month,day)
                        #if dico["New"]:
                        list.append((new_date,dico["Reference"],dico["Type"],dico["Titre"],dico["Link"],dico["Indice"]))
        sorted_list = sorted(list,key=lambda student: student[1])
        for row in sorted_list:
            try:
                id = ""
                date = self.PrettyDate(row[0])
            except:
                date = ""
                id = row[0] # for certification documents only
            reference = row[1]
            type = row[2]
            title = row[3]
            link = row[4]
            version = row[5]
            if version is not None:
                title ="{:s} {:s} version {:s}: {:s} ".format(type,reference,version,title)
            else:
                title ="{:s} {:s}: {:s} ".format(type,reference,title)
            title =  title.ljust(120, ' ');
            #if date != "":
            #    title += " published date: {:s}".format(date)
            #print "TITLE",title
            header,obsolete = self.sqlite_get_char(reference)
            ig = IG(group="",
                    sub_group = "",
                    artic=id,
                    title=title,
                    date=date,
                    link=link,
                    list_saq=[],
                    obsolete=obsolete)
            tbl_ig_items.append(ig)
    def __init__(self):
        self.filename = "easyIG.html"
        # Django settings
        try:
            settings.configure(DEBUG=False,
                               TEMPLATE_DEBUG=False,
                               TEMPLATE_LOADERS=('django.template.loaders.filesystem.Loader',
                                                'django.template.loaders.app_directories.Loader'),
                               TEMPLATE_DIRS=('template',))
            setup()
        except NameError:
            print "Missing Django module."
        except RuntimeError:
            print "Settings already configured."
    def get(self,
            from_file_ig=False,
            from_file_saq=False):
        # Change url = http://spar-syner1.in.com:8600/change
        # Read procedures page
        url_intranet_root = "http://intranet-ece.in.com/dq/documentation/"
        # IG
        if not from_file_ig:
            url_intranet = "http://intranet-ece.in.com/dq/documentation/procedures_zodiac_aero_electric"
            try:
                response = urllib2.urlopen(url_intranet)
                html = response.read()
            except IOError,e:
                html = ""
                print e
        else:
            file_handler = open(from_file_ig,"r")
            html = file_handler.read()
        #print "HTML",unicode(html,'iso-8859-1')
        #exit()
        header = ["Type","Reference","Indice","Titre","Application","MQ","Link","New"]
        parser = MyHTMLParser(header)
        parser.feed(html)
        parser.header.append("Link")
        parser.header.append("New")
        # SAQ
        if not from_file_saq:
            try:
                response_templates = urllib2.urlopen(url_intranet_root + "formulaires")
                html = response_templates.read()
            except IOError,e:
                html = ""
                print e
        else:
            file_handler = open(from_file_saq,"r")
            html = file_handler.read()
        header = ["Reference","Indice","Titre","Procedure","Application","Link","New"]
        parser_saq = MyHTMLParser(header,True)
        parser_saq.feed(html)
        parser_saq.header.append("Link")
        parser_saq.header.append("New")
        dico_ig_tbl_saq = {}
        dico_saq = {}
        parser_saq.getListSAQ(dico_ig_tbl_saq,dico_saq)
        #print "DICO:",dico_ig_tbl_saq
        parser.sqlite_connect()
        tbl = []
        index = 1
        prev_gr =""
        prev_gr_sgr = ""
        prev_gr_sgr_art = ""
        # Prepare HTML document
        color_flag = 0
        ul_root = ET.Element('ul')
        tbl_group = []
        tbl_sub_group = []
        tbl_articulation = []
        tbl_ig = []
        for dico in parser.list_ig:
            color_flag += 1
            type = dico["Type"]
            reference = dico["Reference"]
            version = dico["Indice"]
            title = dico["Titre"]
            title = title.replace("<br/>", " ")
            link = dico["Link"]
            tbl.append((index,reference,0))
            index += 1
            # Match X.X .X .X X X
            m = re.match(r'([0-9]).([0-9]).([0-9]).([0-9]{3})',reference)
            if m:
                groupe = m.group(1)
                sous_groupe = m.group(2)
                gr_sgr = "{:s}{:s}".format(groupe,sous_groupe)
                articulation = m.group(3)
                gr_sgr_art = "{:s}{:s}{:s}".format(groupe,sous_groupe,articulation)
                groupe_id,groupe_description = parser.sqlite_get_groupe(groupe)
                if groupe != prev_gr:
                    # on change de groupe
                    prev_gr = groupe
                    tbl_group.append((groupe,groupe_description))
                sous_groupe_sql_id,sous_groupe_description = parser.sqlite_get_sous_groupe(groupe,sous_groupe)
                if gr_sgr != prev_gr_sgr and sous_groupe_sql_id is not None:
                    # On change de sous groupe
                    prev_gr_sgr = gr_sgr
                    tbl_sub_group.append((groupe,sous_groupe,sous_groupe_description))
                articulation_sql_id,articulation_description = parser.sqlite_get_articulation(groupe,sous_groupe,articulation)
                if gr_sgr_art != prev_gr_sgr_art and articulation_sql_id is not None:
                    # On change d articulation
                    tbl_articulation.append((groupe,sous_groupe,articulation,articulation_description))
                    prev_gr_sgr_art = gr_sgr_art
                # Hyperlink IG
                title = "{:s} {:s} version {:s}: {:s}".format(type,reference,version,title)
                # List SAQ
                list_saq = []
                if reference in dico_ig_tbl_saq:
                    for saq in dico_ig_tbl_saq[reference]:
                        version = dico_saq[saq]["Indice"]
                        description = dico_saq[saq]["Titre"]
                        link_saq = dico_saq[saq]["Link"]
                        list_saq.append((saq,description,version,link_saq))
                ig = IG(group=groupe,
                        sub_group = sous_groupe,
                        artic=articulation,
                        title=title,
                        link=link,
                        list_saq=list_saq)
                tbl_ig.append(ig)
                header,obsolete = parser.sqlite_get_char(reference)
                if header and obsolete:
                    pass
                    #hyperlink.set("class","wide obsolete_and_header")
                elif header:
                    pass
                    #hyperlink.set("class","wide top_ig")
                elif obsolete:
                    pass
                    #hyperlink.set("class","wide obsolete")
                else:
                    pass
            elif re.match(r'X.X.X.XXX',reference):
                pass
                #print "Gestion des RT dans AGILE"
            elif re.match(r'ZA',type):
                title = "{:s} {:s} version {:s}: {:s}".format(type,reference,version,title)
                ig = IG(group=5,
                        sub_group = 0,
                        artic=0,
                        title=title,
                        link=link,
                        list_saq=[])
                tbl_ig.append(ig)
            elif re.match(r'ZS',type):
                title = "{:s} {:s} version {:s}: {:s}".format(type,reference,version,title)
                ig = IG(group=6,
                        sub_group = 0,
                        artic=0,
                        title=title,
                        link=link,
                        list_saq=[])
                tbl_ig.append(ig)
            else:
                ig = IG(group=groupe,
                        sub_group = sous_groupe,
                        artic=articulation,
                        title=title,
                        link=link,
                        list_saq=[])
                tbl_ig.append(ig)
        tbl_group.append((5,"Zodiac Aerospace"))
        tbl_sub_group.append((5,0,"G&eacute;n&eacute;ralit&eacute;s"))
        tbl_articulation.append((5,0,0,"G&eacute;n&eacute;ralit&eacute;s"))
        tbl_group.append((6,"Zodiac Service"))
        tbl_sub_group.append((6,0,"G&eacute;n&eacute;ralit&eacute;s"))
        tbl_articulation.append((6,0,0,"G&eacute;n&eacute;ralit&eacute;s"))
        from xml.etree.ElementTree import XML, fromstring, tostring
        list_ig_txt = tostring(ul_root)
        date = datetime.now().strftime('%A %d %b %Y')
        heure = datetime.now().strftime('%H:%M:%S')
        generated = "Page created by doCID version {:s} on {:s} at {:s}".format(VERSION,date,heure)
        tbl_ig_software = []
        self.createListIG("Software",parser.list_ig,tbl_ig_software)
        tbl_ig_fpga = []
        self.createListIG("FPGA",parser.list_ig,tbl_ig_fpga)
        tbl_ig_hardware = []
        self.createListIG("Hardware",parser.list_ig,tbl_ig_hardware)
        tbl_ig_bench = []
        self.createListIG("Bench",parser.list_ig,tbl_ig_bench)
        tbl_ig_agile = []
        self.createListIG("Agile",parser.list_ig,tbl_ig_agile)
        tbl_ig_change = []
        self.createListIG("Configuration",parser.list_ig,tbl_ig_change)
        tbl_ig_certif = []
        self.createListIG("Certification",parser.list_ig,tbl_ig_certif)
        tbl_ig_new = []
        self.createListNewIG("Agile",parser.list_ig,tbl_ig_new)
        tbl_certif = (((5,9),"ARP-4754"),
                      ((1,10,2,3,6,8,11,12),"DO-178"),
                      ((4,7,13),"DO-254"))
        try:
            rendered = render_to_string('easy_ig_header.html', {'tbl_group':tbl_group,
                                                                'tbl_sub_group':tbl_sub_group,
                                                                'tbl_articulation': tbl_articulation,
                                                                'tbl_ig':tbl_ig,
                                                                'tbl_ig_sw':tbl_ig_software,
                                                                'tbl_ig_fpga':tbl_ig_fpga,
                                                                'tbl_ig_hardware':tbl_ig_hardware,
                                                                'tbl_ig_bench':tbl_ig_bench,
                                                                'tbl_ig_agile':tbl_ig_agile,
                                                                'tbl_ig_change':tbl_ig_change,
                                                                'tbl_ig_certif':tbl_ig_certif,
                                                                'tbl_certif':tbl_certif,
                                                                'tbl_ig_new':tbl_ig_new,
                                                                'GENERATED_DATE':generated})
        except NameError,e:
            rendered = "<p>Django module not found.</p>"
            print e
        with open(self.filename, 'w') as html_handler:
            html_handler.write(rendered)
        return self.filename
if __name__ == '__main__':
    low_level_req_id = "SWDD_G7000_PPDS_ACENM_CSC060_CSU004_001"
    csu_id = re.sub(r"\w*(CSC[0-9]{3}_CSU[0-9]{3})_[0-9]{3}",r"\1",low_level_req_id)
    print "csu_id",csu_id
    exit()
    select = 3
    if select == 1:
        easy_ig = easyIG()
        easy_ig.get()
        easy_ig.start()
    elif select == 2:
        getqa = getQA()
        getqa.get(qams_user_id=1,action_id=1555)
        getqa.start()
    elif select == 3:
        from check_llr import CheckLLR
        dir_swrd = "C:\Users\olivier.appere\Desktop\Projets\g7000\SW_ACENM_01_34\SW_ACENM\SwRD"
        dir_swdd = "C:\Users\olivier.appere\Desktop\Projets\g7000\SW_ACENM_01_34\SW_ACENM\SWDD\LLR\Service Layer\Service Memory"
        dir_swdd = "C:\Users\olivier.appere\Desktop\Projets\g7000\SW_ACENM_01_34\SW_ACENM\SWDD\LLR"
        print "ONE"
        extract_req = CheckLLR(basename=dir_swrd,
                           hlr_selected = True)
        print "TWO"
        extract_req.openLog("RD")
        export_scod_html = exportSCOD_HTML()
        if 0==1:
            extract_req.extract(dirname=dir_swrd,
                             type=("SWRD",))
        else:
            extract_req.tbl_list_llr = {u'SWRD_GLOBAL-ACENM_0008': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.2', 'refer': u'[CAN-IRD-346]'}, u'SWRD_GLOBAL-ACENM_0551': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0009': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[CAN-IRD-350]'}, u'SWRD_GLOBAL-ACENM_0361': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Initial value is provided at start-up.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0360': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-857]'}, u'SWRD_GLOBAL-ACENM_0523': {'body': '', 'status': u'MATURE', 'additional': u'The preliminary tests results of the second execution override the preliminary tests results of the first execution.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1415]'}, u'SWRD_GLOBAL-ACENM_0522': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default values are specified for data which are extracted from CAN bus when data are not available or not valid on CAN bus.', 'issue': u'1.7', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0027': {'body': '', 'status': u'MATURE', 'additional': u'One packet contains 6 bytes of data.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[CAN-IRD-636]'}, u'SWRD_GLOBAL-ACENM_0366': {'body': '', 'status': u'MATURE', 'additional': u'Each ACMP is commanded only by one CAN bus, commands of an ACMP cannot be split between two CAN busses. If closed command of an ACMP is invalid, all the commands of this ACMP are switched to the other CAN bus. ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_722],[SSCS_ACLog_725],[SSCS_ACLog_731],[SSCS_ACLog_693],[SSCS_ACLog_692]'}, u'SWRD_GLOBAL-ACENM_0497': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0496': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0495': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0494': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0493': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0492': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0491': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-727]'}, u'SWRD_GLOBAL-ACENM_0490': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-727]'}, u'SWRD_GLOBAL-ACENM_0499': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0498': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0189': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1058]'}, u'SWRD_GLOBAL-ACENM_0445': {'body': '', 'status': u'MATURE', 'additional': u'DSI AC EP overvoltage is defined in HSID.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1506]'}, u'SWRD_GLOBAL-ACENM_0127': {'body': '', 'status': u'MATURE', 'additional': u'The maximum opening time of the contactor (20ms) is included in the tolerance.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_846],[SSCS_ACLog_459],[SSCS_ACLog_1097],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0126': {'body': '', 'status': u'MATURE', 'additional': u'At start-up these data are initialized first with values from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1584],[SSCS_ACLog_1142],[SSCS_ACLog_1119],[SSCS_ACLog_1280]'}, u'SWRD_GLOBAL-ACENM_0125': {'body': '', 'status': u'MATURE', 'additional': u'At start-up these data are initialized first with values from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1584],[SSCS_ACLog_1142],[SSCS_ACLog_1119],[SSCS_ACLog_1280]'}, u'SWRD_GLOBAL-ACENM_0124': {'body': '', 'status': u'MATURE ', 'additional': u'Need to have a global protection status to compute RCCB states.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_459],[SSCS_ACLog_867],[SSCS_ACLog_1114]'}, u'SWRD_GLOBAL-ACENM_0123': {'body': '', 'status': u'MATURE', 'additional': u'Need to have a global protection status to compute RCCB states. ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_459],[SSCS_ACLog_867],[SSCS_ACLog_1114]'}, u'SWRD_GLOBAL-ACENM_0089': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1149],[SSCS_ACLog_922],[SSCS_ACLog_1181],[SSCS_ACLog_883]'}, u'SWRD_GLOBAL-ACENM_0121': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1326],[SSCS_ACLog_1337],[SSCS_ACLog_1336],[SSCS_ACLog_1345],[CAN-IRD-426],[CAN-IRD-427],[CAN-IRD-534]'}, u'SWRD_GLOBAL-ACENM_0120': {'body': '', 'status': u'MATURE', 'additional': u'The maximum opening time of the contactor (20ms) is included in the tolerance.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_445],[SSCS_ACLog_437],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0084': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_883],[SSCS_ACLog_875],[SSCS_ACLog_1541]'}, u'SWRD_GLOBAL-ACENM_0085': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0086': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0087': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_883],[SSCS_ACLog_874]'}, u'SWRD_GLOBAL-ACENM_0080': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1519],[SSCS_ACLog_610]'}, u'SWRD_GLOBAL-ACENM_0081': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_610],[SSCS_ACLog_1407]'}, u'SWRD_GLOBAL-ACENM_0129': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'GFI protection has been removed from SSCS', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0083': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_883],[SSCS_ACLog_874]'}, u'SWRD_GLOBAL-ACENM_0066': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_614],[SSCS_ACLog_609]'}, u'SWRD_GLOBAL-ACENM_0067': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_610],[SSCS_ACLog_1407]'}, u'SWRD_GLOBAL-ACENM_0064': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_614],[SSCS_ACLog_609]'}, u'SWRD_GLOBAL-ACENM_0065': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_609],[SSCS_ACLog_1407]'}, u'SWRD_GLOBAL-ACENM_0062': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_596],,[SSCS_ACLog_595]'}, u'SWRD_GLOBAL-ACENM_0063': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1149],[SSCS_ACLog_922],[SSCS_ACLog_1181],[SSCS_ACLog_596]'}, u'SWRD_GLOBAL-ACENM_0060': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0308': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default value NOT_FAILED is specified during SW initialization phase.', 'issue': u'1.0', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0307': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure computation is defined at HSID level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0306': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure computation is defined at HSID level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0305': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure computation is defined at HSID level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0304': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure computation is defined at HSID level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0303': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure computation is defined at HSID level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0302': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure computation is defined at HSID level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0068': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1519],[SSCS_ACLog_610]'}, u'SWRD_GLOBAL-ACENM_0069': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_610],[SSCS_ACLog_1407]'}, u'SWRD_GLOBAL-ACENM_0398': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default value NOT_FAILED is specified during SW initialization phase.', 'issue': u'1.7', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0399': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Converter failure computation is defined at HSID level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0468': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0546': {'body': '', 'status': u'MATURE', 'additional': u'At start-up, the ACMPx tripped states are restored from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_721],[SSCS_ACLog_1119],[SSCS_ACLog_1280],[SSCS_ACLog_1581],[SSCS_ACLog_1583]'}, u'SWRD_GLOBAL-ACENM_0017': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_667],[SSCS_ACLog_897]'}, u'SWRD_GLOBAL-ACENM_0016': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Not defined in SSCS', 'issue': u'1.0', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0015': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'The figure included in this requirement has been moved outside of a requirement.', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0014': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[CAN-IRD-352]'}, u'SWRD_GLOBAL-ACENM_0462': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0463': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0460': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-845]'}, u'SWRD_GLOBAL-ACENM_0461': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0466': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0467': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0464': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0465': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0264': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_920],[SSCS_ACLog_1196],[SSCS_ACLog_1612],[SSCS_ACLog_1613]'}, u'SWRD_GLOBAL-ACENM_0265': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Upper requirement SSCS_ACLog_1313 has been deleted.', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0266': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'The figure included in this requirement has been moved outside of a requirement (refer to Figure 10).', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0267': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_701]'}, u'SWRD_GLOBAL-ACENM_0260': {'body': '', 'status': u'MATURE', 'additional': u'At start-up this data is initialized first with value from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_920],[SSCS_ACLog_1196],[SSCS_ACLog_1610]'}, u'SWRD_GLOBAL-ACENM_0261': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Merged in with the ATCX failed open management requirement', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0262': {'body': '', 'status': u'MATURE', 'additional': u'At start-up this data is initialized first with value from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_920],[SSCS_ACLog_1196],[SSCS_ACLog_1606]'}, u'SWRD_GLOBAL-ACENM_0263': {'body': '', 'status': u'MATURE', 'additional': u'This failure is not latched in context NVM and is reset at each software start-up.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_919],[SSCS_ACLog_1196],[SSCS_ACLog_1612],[SSCS_ACLog_1613]'}, u'SWRD_GLOBAL-ACENM_0268': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A ', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_667]'}, u'SWRD_GLOBAL-ACENM_0269': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.2', 'refer': u'[SSCS_ACLog_667]'}, u'SWRD_GLOBAL-ACENM_0391': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_663]'}, u'SWRD_GLOBAL-ACENM_0392': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1140]'}, u'SWRD_GLOBAL-ACENM_0393': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'FO/FC monitoring of the opposite contactor has been removed in SSCS', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0150': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_683],[SSCS_ACLog_1040],[SSCS_ACLog_1038]'}, u'SWRD_GLOBAL-ACENM_0169': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1068],[SSCS_ACLog_1121],[SSCS_ACLog_721],[SSCS_ACLog_661],[SSCS_ACLog_464],[SSCS_ACLog_869],[SSCS_ACLog_1122],[SSCS_ACLog_1320],[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0151': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_683],[SSCS_ACLog_1040],[SSCS_ACLog_1038]'}, u'SWRD_GLOBAL-ACENM_0394': {'body': '', 'status': u'MATURE', 'additional': u'Each fault has a unique fault code. The power supplies presence failures are not stored in NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1188],[SSCS_ACLog_1380],[SSCS_ACLog_1400],[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0163': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_557],[SSCS_ACLog_627],[SSCS_ACLog_828],[SSCS_ACLog_1214],[SSCS_ACLog_1315],[SSCS_ACLog_1462],[SSCS_ACLog_1463],[SSCS_ACLog_1483],[SSCS_ACLog_1515],[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0162': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_557],[SSCS_ACLog_1228],[SSCS_ACLog_639],[SSCS_ACLog_827],[SSCS_ACLog_566],[SSCS_ACLog_1222],[SSCS_ACLog_1315],[SSCS_ACLog_1462],[SSCS_ACLog_1463],[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0161': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_557],[SSCS_ACLog_1228],[SSCS_ACLog_638],[SSCS_ACLog_828],[SSCS_ACLog_566],[SSCS_ACLog_1222],[SSCS_ACLog_1315],[SSCS_ACLog_1462],[SSCS_ACLog_1463],[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0160': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_557],[SSCS_ACLog_1228],[SSCS_ACLog_637],[SSCS_ACLog_566],[SSCS_ACLog_1222],[SSCS_ACLog_1315],[SSCS_ACLog_1462],[SSCS_ACLog_1463],[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0167': {'body': '', 'status': u'MATURE', 'additional': u'Closed state corresponds to a GCU "acknowledged" and Open state corresponds to a GCU "not acknowledged"', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_557],[SSCS_ACLog_627],[SSCS_ACLog_1217],[SSCS_ACLog_1462],[SSCS_ACLog_1611]'}, u'SWRD_GLOBAL-ACENM_0166': {'body': '', 'status': u'MATURE', 'additional': u'Closed state corresponds to a GCU "acknowledged" and Open state corresponds to a GCU "not acknowledged"', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_557],[SSCS_ACLog_624],[SSCS_ACLog_1216],[SSCS_ACLog_1462],[SSCS_ACLog_1611]'}, u'SWRD_GLOBAL-ACENM_0165': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1055],[SSCS_ACLog_1228],[SSCS_ACLog_566],[SSCS_ACLog_1462],[SSCS_ACLog_1463]'}, u'SWRD_GLOBAL-ACENM_0164': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'The DSI Emerlog AEC open is no more used.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0185': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_663]'}, u'SWRD_GLOBAL-ACENM_0184': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_663]'}, u'SWRD_GLOBAL-ACENM_0028': {'body': '', 'status': u'MATURE', 'additional': u'Each time slot contains 20 messages including 6 bytes of NVM data.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1077],[CAN-IRD-633],[CAN-IRD-643],[CAN-IRD-641],[CAN-IRD-644],[CAN-IRD-642],[CAN-IRD-868],[CAN-IRD-1034]'}, u'SWRD_GLOBAL-ACENM_0395': {'body': '', 'status': u'MATURE', 'additional': u'The procedure to test the AC TIE current transformer is described in HSID.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1141],[SSCS_ACLog_1419]'}, u'SWRD_GLOBAL-ACENM_0181': {'body': '', 'status': u'MATURE', 'additional': u'For ATC1, ATC2 and AEC contactors, the validity of XFR is checked in the STEP5.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_558],[SSCS_ACLog_563],[SSCS_ACLog_561]'}, u'SWRD_GLOBAL-ACENM_0180': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Failed open/failed closed failures have no impact on network re-configuration', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0183': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_563]'}, u'SWRD_GLOBAL-ACENM_0182': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_561]'}, u'SWRD_GLOBAL-ACENM_0022': {'body': '', 'status': u'MATURE', 'additional': u'The cold start phase includes preliminary tests and PBIT tests.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_669]'}, u'SWRD_GLOBAL-ACENM_0023': {'body': '', 'status': u'MATURE', 'additional': u'The warm start phase includes preliminary tests.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_672]'}, u'SWRD_GLOBAL-ACENM_0020': {'body': '', 'status': u'MATURE', 'additional': u'DSI_5S_POWER_CUT is ACTIVE when a power interrupt greater than 5s has occurred.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_664]'}, u'SWRD_GLOBAL-ACENM_0021': {'body': '', 'status': u'MATURE', 'additional': u'PBIT is not performed if there is a IBIT request.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_668],[SSCS_ACLog_896]'}, u'SWRD_GLOBAL-ACENM_0026': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Provide the initialization value of NVM data to transmit to EDMU.', 'issue': u'1.12', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0158': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_575],[SSCS_ACLog_927]'}, u'SWRD_GLOBAL-ACENM_0024': {'body': '', 'status': u'MATURE', 'additional': u'ACTIVE corresponds to Ground in SSCS, INACTIVE corresponds to Open in SSCS. BOARD_ERROR state is used at software level to catch all wrong pin programming combination.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_886]'}, u'SWRD_GLOBAL-ACENM_0025': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1084],[SSCS_ACLog_1174]'}, u'SWRD_GLOBAL-ACENM_0509': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0508': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0159': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO\t', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_936],[SSCS_ACLog_927]'}, u'SWRD_GLOBAL-ACENM_0118': {'body': '', 'status': u'MATURE', 'additional': u'The maximum opening time of the contactor (20ms) is included in the tolerance.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_443],[SSCS_ACLog_437],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0119': {'body': '', 'status': u'MATURE', 'additional': u'The maximum opening time of the contactor (20ms) is included in the tolerance.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_444],[SSCS_ACLog_437],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0116': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Unbalanced protection has been removed from SSCS.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0117': {'body': '', 'status': u'MATURE', 'additional': u'The frequency range is defined in HSID', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.10', 'refer': u'[SSCS_ACLog_1089]'}, u'SWRD_GLOBAL-ACENM_0114': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_437],[SSCS_ACLog_440]'}, u'SWRD_GLOBAL-ACENM_0115': {'body': '', 'status': u'MATURE', 'additional': u'The maximum opening time of the contactor (20ms) is included in the tolerance.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_441],[SSCS_ACLog_888],[SSCS_ACLog_437],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0112': {'body': '', 'status': u'MATURE', 'additional': u'The maximum opening time of the contactor (20ms) is included in the tolerance.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_437],[SSCS_ACLog_438],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0113': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_437],[SSCS_ACLog_439]'}, u'SWRD_GLOBAL-ACENM_0110': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_437]'}, u'SWRD_GLOBAL-ACENM_0111': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'The AC EP protection are no more latched', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0396': {'body': '', 'status': u'MATURE', 'additional': u'Computed SW checksum is the same as in ROM integrity test', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.8', 'refer': u'[CAN-IRD-211]'}, u'SWRD_GLOBAL-ACENM_0326': {'body': '', 'status': u'MATURE', 'additional': u'The complement value will be used for data integrity check in static area.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1261]'}, u'SWRD_GLOBAL-ACENM_0019': {'body': '', 'status': u'MATURE', 'additional': u'A critical software error occurs in case of an unexpected interruption, an exception (address error, trap error,...), a CPU overload, ....  ', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Prevent SW from an unexpected behavior in case of a critical SW error', 'issue': u'1.4', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0336': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1224],[SSCS_ACLog_1373],[SSCS_ACLog_1372]'}, u'SWRD_GLOBAL-ACENM_0337': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1224],[SSCS_ACLog_1373]'}, u'SWRD_GLOBAL-ACENM_0334': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1230]'}, u'SWRD_GLOBAL-ACENM_0335': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1230]'}, u'SWRD_GLOBAL-ACENM_0332': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1601],[SSCS_ACLog_1602],[SSCS_ACLog_1605],[SSCS_ACLog_1609]'}, u'SWRD_GLOBAL-ACENM_0333': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1443],[SSCS_ACLog_1288]'}, u'SWRD_GLOBAL-ACENM_0330': {'body': '', 'status': u'MATURE', 'additional': u'Even if the NVM compatibility is declared as failed, the HW data are restored from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1119],[SSCS_ACLog_1550],[SSCS_ACLog_1581],[SSCS_ACLog_1583],[SSCS_ACLog_1585],[SSCS_ACLog_1587]'}, u'SWRD_GLOBAL-ACENM_0331': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'IBIT command is saved in static area in order to take into account the request for the next SW start-up.', 'issue': u'1.4', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0237': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Merged in SWRD_GLOBAL-ACENM_0539', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0236': {'body': '', 'status': u'MATURE', 'additional': u'SW is protected against SEU/MBU to avoid unexpected behavior.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1300],[SSCS_ACLog_1301],[SSCS_ACLog_1302]'}, u'SWRD_GLOBAL-ACENM_0235': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1138],[SSCS_ACLog_1345],[CAN-IRD-426],[CAN-IRD-534]'}, u'SWRD_GLOBAL-ACENM_0234': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1137],[SSCS_ACLog_1336],[CAN-IRD-426],[CAN-IRD-427]'}, u'SWRD_GLOBAL-ACENM_0233': {'body': '', 'status': u'MATURE', 'additional': u'Other combinations (data are invalid) are managed in CAN bus management. If a data is invalid on one CAN bus, the data used is taken on the other bus. If a data is invalid on the two CAN busses, a default value is used. At start-up, the ACMPx open locked states are restored from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_721],[SSCS_ACLog_1585],[SSCS_ACLog_1586],[SSCS_ACLog_1587],[SSCS_ACLog_1588]'}, u'SWRD_GLOBAL-ACENM_0232': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1121],[SSCS_ACLog_721],[SSCS_ACLog_1582],[SSCS_ACLog_1586]'}, u'SWRD_GLOBAL-ACENM_0338': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1224],[SSCS_ACLog_1079],[SSCS_ACLog_1379]'}, u'SWRD_GLOBAL-ACENM_0339': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1394]'}, u'SWRD_GLOBAL-ACENM_0435': {'body': '', 'status': u'MATURE', 'additional': u'The IBIT tests results of the second execution override the IBIT results of the first execution.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_955],[SSCS_ACLog_1178]'}, u'SWRD_GLOBAL-ACENM_0434': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Not defined in SSCS', 'issue': u'1.4', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0341': {'body': '', 'status': u'MATURE', 'additional': u'Write NVM current LEG even If no failure is detected on this current LEG.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1378]'}, u'SWRD_GLOBAL-ACENM_0436': {'body': '', 'status': u'MATURE', 'additional': u'Command DSO for RCCB/contactor will be override if a IBIT is requested. ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_898],[SSCS_ACLog_663],[SSCS_ACLog_1084],[SSCS_ACLog_1174]'}, u'SWRD_GLOBAL-ACENM_0347': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Merged in requirement SWRD_GLOBAL-ACENM_0237', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0430': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'The AC EP protection are no more latched', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0433': {'body': '', 'status': u'MATURE', 'additional': u'NO', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Copy of the anti-paralleling calculated protection status in the associated anti-paralleling global protections status.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0432': {'body': '', 'status': u'MATURE', 'additional': u'NO', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Copy of the differential calculated protection status in the associated differential global protections status.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0246': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1127]'}, u'SWRD_GLOBAL-ACENM_0349': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_692]'}, u'SWRD_GLOBAL-ACENM_0348': {'body': '', 'status': u'MATURE', 'additional': u'CAN Data with validities are only extracted from one and only one CAN bus.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_722],[SSCS_ACLog_725],[SSCS_ACLog_728],[SSCS_ACLog_729],[SSCS_ACLog_730],[SSCS_ACLog_731],[SSCS_ACLog_693],[SSCS_ACLog_694],[CAN-IRD-857]'}, u'SWRD_GLOBAL-ACENM_0439': {'body': '', 'status': u'MATURE', 'additional': u'Roll-over of fault index will be managed at design level (maximum 191 faults can be stored in NVM).', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Manage the restoration of the faults and the flight leg at power-up.', 'issue': u'1.4', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0438': {'body': '', 'status': u'MATURE', 'additional': u'When the maximum number of different faults for one flight leg is reached, the new faults are not registered. When the maximum occurrence of a given fault for one flight leg is reached, this fault is updated when it occurs again (but the number of occurrence remains to 255). A fault is updated only when its state switch from NOT_FAILED to FAILED.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1382],[SSCS_ACLog_1395]'}, u'SWRD_GLOBAL-ACENM_0247': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1128]'}, u'SWRD_GLOBAL-ACENM_0168': {'body': '', 'status': u'MATURE', 'additional': u'Closed state corresponds to a GCU "acknowledged" and Open state corresponds to a GCU "not acknowledged"', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_557],[SSCS_ACLog_624],[SSCS_ACLog_629],[SSCS_ACLog_1220],[SSCS_ACLog_1221],[SSCS_ACLog_1462]'}, u'SWRD_GLOBAL-ACENM_0378': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-636]'}, u'SWRD_GLOBAL-ACENM_0379': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Unlatch failure request is no more used', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0350': {'body': '', 'status': u'MATURE', 'additional': u'A communication failure can be a loss of the bus, a loss of one or several messages in reception, an issue to send message(s) on CAN bus or a protocol error.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1404],[SSCS_ACLog_1405],[SSCS_ACLog_693],[SSCS_ACLog_694],[SSCS_ACLog_1496],[CAN-IRD-857],[CAN-IRD-1017]'}, u'SWRD_GLOBAL-ACENM_0351': {'body': '', 'status': u'MATURE', 'additional': u'CAN Data without validities are extracted from the first CAN bus which provides the data.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1404],[SSCS_ACLog_1405],[SSCS_ACLog_693],[SSCS_ACLog_694],[CAN-IRD-857]'}, u'SWRD_GLOBAL-ACENM_0376': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-215]'}, u'SWRD_GLOBAL-ACENM_0377': {'body': '', 'status': u'MATURE', 'additional': u'If NVM download request, NVM erase or IBIT request are sent at the same time, only the first command received will be taken into account. A download request is ignored if the requested NVM block size is not consistent (greater than the maximum size of NVM). ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A ', 'issue': u'1.12', 'refer': u'[CAN-IRD-643],[CAN-IRD-641],[SSCS_ACLog_1531]'}, u'SWRD_GLOBAL-ACENM_0188': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1056],[SSCS_ACLog_1058],[SSCS_ACLog_1098]'}, u'SWRD_GLOBAL-ACENM_0187': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1056],[SSCS_ACLog_1058],[SSCS_ACLog_1206]'}, u'SWRD_GLOBAL-ACENM_0152': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Step 2 of test 2 has been removed.', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0153': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1040],[SSCS_ACLog_1038]'}, u'SWRD_GLOBAL-ACENM_0099': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_717],[SSCS_ACLog_718]'}, u'SWRD_GLOBAL-ACENM_0098': {'body': '', 'status': u'MATURE', 'additional': u'This failure is not latched in context NVM and is reset at each software start-up.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_717],[SSCS_ACLog_1072],[SSCS_ACLog_939],[SSCS_ACLog_1370],[SSCS_ACLog_1576],[SSCS_ACLog_1612],[SSCS_ACLog_1613],[SSCS_ACLog_1614]'}, u'SWRD_GLOBAL-ACENM_0156': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_575],[SSCS_ACLog_927]'}, u'SWRD_GLOBAL-ACENM_0157': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_575],[SSCS_ACLog_927]'}, u'SWRD_GLOBAL-ACENM_0154': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'PBIT execution time has been removed in SSCS.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0155': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_903],[SSCS_ACLog_840]'}, u'SWRD_GLOBAL-ACENM_0093': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'ACMP data about opposite side are no more used', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0092': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'ACMP data about opposite side are no more used', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0091': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'ACMP data about opposite side are no more used', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0090': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_717],[SSCS_ACLog_713]'}, u'SWRD_GLOBAL-ACENM_0097': {'body': '', 'status': u'MATURE', 'additional': u'This failure is not latched in context NVM and is reset at each software start-up. A failed open failure (due to chattering) clears a failed closed failure.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_717],[SSCS_ACLog_1071],[SSCS_ACLog_939],[SSCS_ACLog_1370],[SSCS_ACLog_1612],[SSCS_ACLog_1613],[SSCS_ACLog_1614]'}, u'SWRD_GLOBAL-ACENM_0096': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_717],[SSCS_ACLog_1070],[SSCS_ACLog_940],[SSCS_ACLog_1371]'}, u'SWRD_GLOBAL-ACENM_0095': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_717],[SSCS_ACLog_714]'}, u'SWRD_GLOBAL-ACENM_0094': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_717],[SSCS_ACLog_714]'}, u'SWRD_GLOBAL-ACENM_0075': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0074': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0077': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_609],[SSCS_ACLog_1407]'}, u'SWRD_GLOBAL-ACENM_0076': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_614],[SSCS_ACLog_609]'}, u'SWRD_GLOBAL-ACENM_0071': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0070': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0073': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0072': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0372': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Merged in requirement SWRD_GLOBAL-ACENM_0373', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0373': {'body': '', 'status': u'MATURE', 'additional': u'If several protections are active, the trip cause is set with the first protection which occurred. Each EDMU_ACMPX_TRIPPED_CMD is associated with one ACMP. An ACMP can receive a TRIP reset independently from other ACMPs.  At start-up, the ACMPx trip causes are restored from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_721],[SSCS_ACLog_1119],[SSCS_ACLog_1280],[SSCS_ACLog_1581],[SSCS_ACLog_1582],[SSCS_ACLog_1583],[SSCS_ACLog_1584]'}, u'SWRD_GLOBAL-ACENM_0370': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default values are specified for data which are extracted from CAN bus when data are not available or not valid on CAN bus.', 'issue': u'1.4', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0371': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1405]'}, u'SWRD_GLOBAL-ACENM_0079': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_610],[SSCS_ACLog_1407]'}, u'SWRD_GLOBAL-ACENM_0078': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_614],[SSCS_ACLog_609]'}, u'SWRD_GLOBAL-ACENM_0374': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'If the protocol version is different for EDMU and ACLOG, the ACLOG continues to answer to all message from EDMU.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0375': {'body': '', 'status': u'MATURE', 'additional': u'If NVM download request and IBIT request are sent at the same time, only the first command received will be taken into account. While the IBIT has not been fully performed the IBIT request are ignored. IBIT request are ignored if a network reconfiguration is in progress.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1259],[SSCS_ACLog_1260]'}, u'SWRD_GLOBAL-ACENM_0479': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0478': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0471': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0470': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0473': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0472': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0475': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0474': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0477': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0476': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0387': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_663]'}, u'SWRD_GLOBAL-ACENM_0386': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_932],[SSCS_ACLog_1194],[SSCS_ACLog_944],[SSCS_ACLog_1191],[SSCS_ACLog_1457],[SSCS_ACLog_1546]'}, u'SWRD_GLOBAL-ACENM_0385': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1080]'}, u'SWRD_GLOBAL-ACENM_0384': {'body': '', 'status': u'MATURE', 'additional': u'GREEN and RED are described in HSID. ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.2', 'refer': u'[SSCS_ACLog_701]'}, u'SWRD_GLOBAL-ACENM_0383': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Removed in SSCS', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0382': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Trip reset request is no more used', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0381': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Trip reset request is no more used', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0380': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Unlatch failure request is no more used', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0389': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1247],[SSCS_ACLog_437],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0388': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1224],[SSCS_ACLog_1374]'}, u'SWRD_GLOBAL-ACENM_0206': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_753]'}, u'SWRD_GLOBAL-ACENM_0207': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_754]'}, u'SWRD_GLOBAL-ACENM_0204': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_536]'}, u'SWRD_GLOBAL-ACENM_0205': {'body': '', 'status': u'MATURE', 'additional': u'The ground service mode cannot be active if the ground servicing request is open.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_552],[SSCS_ACLog_554],[SSCS_ACLog_1504],[SSCS_ACLog_1058]'}, u'SWRD_GLOBAL-ACENM_0202': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_537],[SSCS_ACLog_1471]'}, u'SWRD_GLOBAL-ACENM_0203': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1593]'}, u'SWRD_GLOBAL-ACENM_0200': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_526]'}, u'SWRD_GLOBAL-ACENM_0201': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_537],[SSCS_ACLog_1471]'}, u'SWRD_GLOBAL-ACENM_0208': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_755]'}, u'SWRD_GLOBAL-ACENM_0209': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_735]'}, u'SWRD_GLOBAL-ACENM_0273': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'CPU test is not required during preliminary tests', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0272': {'body': '', 'status': u'MATURE', 'additional': u'Hardware/software compatibility index is defined in HSID', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1535],[SSCS_ACLog_1550]'}, u'SWRD_GLOBAL-ACENM_0271': {'body': '', 'status': u'MATURE', 'additional': u'A 32bits checksum is computed by an additional tool. In ROM, a 32bits constant (initially equal to 0x00000000) is replaced by the complemented value of the computed checksum. It is why ACENM software will get 0x00000000 as result of ROM checksum.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_667]'}, u'SWRD_GLOBAL-ACENM_0270': {'body': '', 'status': u'MATURE', 'additional': u'RAM integrity test algorithm is defined at design level.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_667]'}, u'SWRD_GLOBAL-ACENM_0277': {'body': '', 'status': u'MATURE', 'additional': u'CT tests are not included because these tests are linked to an external failure. ', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Used to have a global result of the PBIT.', 'issue': u'1.7', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0276': {'body': '', 'status': u'MATURE', 'additional': u'The PBIT tests results of the second execution override the PBIT results of the first execution.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1178]'}, u'SWRD_GLOBAL-ACENM_0275': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_899],[SSCS_ACLog_900],[SSCS_ACLog_904],[SSCS_ACLog_1141],[SSCS_ACLog_1176],[SSCS_ACLog_897],[SSCS_ACLog_1419],[SSCS_ACLog_1535]'}, u'SWRD_GLOBAL-ACENM_0274': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_897]'}, u'SWRD_GLOBAL-ACENM_0319': {'body': '', 'status': u'MATURE', 'additional': u'Improve lifetime of NVM device by not writing the same value several times.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1582],[SSCS_ACLog_1584]'}, u'SWRD_GLOBAL-ACENM_0279': {'body': '', 'status': u'MATURE', 'additional': u'The procedure to test the hardware overvoltage protection function is described in HSID.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_904]'}, u'SWRD_GLOBAL-ACENM_0278': {'body': '', 'status': u'MATURE', 'additional': u'MAX and MIN value are defined in HSID', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_900],[SSCS_ACLog_832],[SSCS_ACLog_833],[SSCS_ACLog_1084]'}, u'SWRD_GLOBAL-ACENM_0501': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-870]'}, u'SWRD_GLOBAL-ACENM_0500': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0503': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0502': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-871]'}, u'SWRD_GLOBAL-ACENM_0505': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0504': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-879]'}, u'SWRD_GLOBAL-ACENM_0507': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0506': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0437': {'body': '', 'status': u'MATURE', 'additional': u'Write NVM last LEG with fault.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1377]'}, u'SWRD_GLOBAL-ACENM_0039': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_507],[SSCS_ACLog_1208],[SSCS_ACLog_1481],[SSCS_ACLog_1482]'}, u'SWRD_GLOBAL-ACENM_0038': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_534],[SSCS_ACLog_1474],[SSCS_ACLog_1475]'}, u'SWRD_GLOBAL-ACENM_0031': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Filter on WOW DSI has been removed in SSCS (req SSCS_ACLog_662 removed).', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0030': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Filter on WOW DSI has been removed in SSCS.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0033': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_548],[SSCS_ACLog_953]'}, u'SWRD_GLOBAL-ACENM_0032': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_548],[SSCS_ACLOG_1507]'}, u'SWRD_GLOBAL-ACENM_0035': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_578]'}, u'SWRD_GLOBAL-ACENM_0034': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1469],[SSCS_ACLog_1470]'}, u'SWRD_GLOBAL-ACENM_0037': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Functionalities deleted in SSCS.', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0036': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_578],[SSCS_ACLog_925]'}, u'SWRD_GLOBAL-ACENM_0109': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[CAN-IRD-180]'}, u'SWRD_GLOBAL-ACENM_0108': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-215]'}, u'SWRD_GLOBAL-ACENM_0105': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'No external fuse to monitor.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0104': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1227]'}, u'SWRD_GLOBAL-ACENM_0107': {'body': '', 'status': u'MATURE', 'additional': u'This failure is not latched in context NVM and is reset at each software start-up.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_919],[SSCS_ACLog_1196],[SSCS_ACLog_1612]'}, u'SWRD_GLOBAL-ACENM_0106': {'body': '', 'status': u'MATURE', 'additional': u'Only EDMU trip cause on phase A is used (the ACMP protections are not computed for each phase).', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_721]'}, u'SWRD_GLOBAL-ACENM_0101': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_636],[SSCS_ACLog_632],[SSCS_ACLog_1450],[SSCS_ACLog_1451]'}, u'SWRD_GLOBAL-ACENM_0100': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_717],[SSCS_ACLog_719]'}, u'SWRD_GLOBAL-ACENM_0103': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_636],[SSCS_ACLog_634],[SSCS_ACLog_1450],[SSCS_ACLog_1451]'}, u'SWRD_GLOBAL-ACENM_0102': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_636],[SSCS_ACLog_632],[SSCS_ACLog_1450],[SSCS_ACLog_1451]'}, u'SWRD_GLOBAL-ACENM_0534': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-219]'}, u'SWRD_GLOBAL-ACENM_0535': {'body': '', 'status': u'MATURE', 'additional': u'Write accesses to BITE NVM are not authorized during BITE NVM reset but write accesses to CONTEXT NVM are still authorized. If an erase command occurs during a NVM writing in progress, the writing operation is finished before taking into account the erase command.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1364]'}, u'SWRD_GLOBAL-ACENM_0536': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-499],[CAN-IRD-501],[CAN-IRD-505],[CAN-IRD-506],[CAN-IRD-331]'}, u'SWRD_GLOBAL-ACENM_0537': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_559]'}, u'SWRD_GLOBAL-ACENM_0530': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_629]'}, u'SWRD_GLOBAL-ACENM_0531': {'body': '', 'status': u'MATURE', 'additional': u'A timer is allocated for each phase for each step. If a fault condition comes back, the associated step timer start from its last saved value.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1487]'}, u'SWRD_GLOBAL-ACENM_0532': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1533]'}, u'SWRD_GLOBAL-ACENM_0533': {'body': '', 'status': u'MATURE', 'additional': u'The procedure to test DSI multiplexer is described in HSID.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1107]'}, u'SWRD_GLOBAL-ACENM_0088': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_883],[SSCS_ACLog_875],[SSCS_ACLog_1541]'}, u'SWRD_GLOBAL-ACENM_0538': {'body': '', 'status': u'MATURE', 'additional': u'The AC_EP_PINF_STATE is initialized at ACTIVE state at start-up ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_839],[SSCS_ACLog_526],[SSCS_ACLog_1396],[SSCS_ACLog_1577]'}, u'SWRD_GLOBAL-ACENM_0539': {'body': '', 'status': u'MATURE', 'additional': u'During the 5s, the active AC EP protection BITE failure(s) are stored in NVM and the active AC EP protection BITE failure(s) are sent on CAN busses.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_447],[SSCS_ACLog_1359]'}, u'SWRD_GLOBAL-ACENM_0122': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1327],[SSCS_ACLog_1338],[SSCS_ACLog_1336],[SSCS_ACLog_1345],[CAN-IRD-426],[CAN-IRD-427],[CAN-IRD-534]'}, u'SWRD_GLOBAL-ACENM_0325': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1230]'}, u'SWRD_GLOBAL-ACENM_0324': {'body': '', 'status': u'MATURE', 'additional': u'N/A  ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_676],[SSCS_ACLog_1117],[SSCS_ACLog_1115],[SSCS_ACLog_1262],[SSCS_ACLog_1119],[SSCS_ACLog_1142]'}, u'SWRD_GLOBAL-ACENM_0327': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1230],[SSCS_ACLog_1119]'}, u'SWRD_GLOBAL-ACENM_0249': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Upper requirement has been deleted.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0321': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1601],[SSCS_ACLog_1602],[SSCS_ACLog_1605],[SSCS_ACLog_1609]'}, u'SWRD_GLOBAL-ACENM_0320': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'IBIT command is saved in static area in order to take into account the request for the next SW start-up.', 'issue': u'1.4', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0323': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_830],[SSCS_ACLog_1063],[SSCS_ACLog_1262],[SSCS_ACLog_1142],[SSCS_ACLog_1119]'}, u'SWRD_GLOBAL-ACENM_0322': {'body': '', 'status': u'MATURE', 'additional': u'The complement value will be used for data integrity check in NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1261]'}, u'SWRD_GLOBAL-ACENM_0242': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_504],[SSCS_ACLog_1485]'}, u'SWRD_GLOBAL-ACENM_0243': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_504],[SSCS_ACLog_1485]'}, u'SWRD_GLOBAL-ACENM_0240': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Only one software is used for the two ACLog. One unique part number is used.', 'issue': u'1.0', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0241': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'YES', 'safety': u'YES', 'rationale': u'Defined in PSAC.', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1085],[SSCS_ACLog_491]'}, u'SWRD_GLOBAL-ACENM_0329': {'body': '', 'status': u'MATURE', 'additional': u'All these data are initialized first with values from NVM at start-up. Then, others treatments at start-up can modify the value of these data.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1443]'}, u'SWRD_GLOBAL-ACENM_0328': {'body': '', 'status': u'MATURE', 'additional': u'NVM compatibility algorithm is defined at SwDD level', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'NVM data compatibility is needed to avoid restoration of wrong data', 'issue': u'1.7', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0244': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_935]'}, u'SWRD_GLOBAL-ACENM_0245': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_935]'}, u'SWRD_GLOBAL-ACENM_0400': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[CAN-IRD-211]'}, u'SWRD_GLOBAL-ACENM_0401': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Not defined in SSCS/IRD CAN', 'issue': u'1.3', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0402': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Used in order to ignore a IBIT command when the network reconfiguration is in progress.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0403': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Used in order to ignore a IBIT command when the network reconfiguration is in progress.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0404': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'This alias is no more useful (it is not relevant to merge all the CTC anti-paralleling protection).', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0405': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_845],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0406': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1479]'}, u'SWRD_GLOBAL-ACENM_0407': {'body': '', 'status': u'MATURE', 'additional': u'SW Part number is built according to PSAC', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'A software PN is defined for each software build.', 'issue': u'1.11', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0408': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-784]'}, u'SWRD_GLOBAL-ACENM_0409': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[CAN-IRD-315]'}, u'SWRD_GLOBAL-ACENM_0082': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1149],[SSCS_ACLog_922],[SSCS_ACLog_1181],[SSCS_ACLog_614]'}, u'SWRD_GLOBAL-ACENM_0128': {'body': '', 'status': u'MATURE', 'additional': u'The maximum opening time of the contactor (20ms) is included in the tolerance.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_850],[SSCS_ACLog_459],[SSCS_ACLog_1097],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0248': {'body': '', 'status': u'MATURE', 'additional': u'The preliminary tests are already taken into account in the failed mode management.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1107]'}, u'SWRD_GLOBAL-ACENM_0239': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1087]'}, u'SWRD_GLOBAL-ACENM_0238': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1087]'}, u'SWRD_GLOBAL-ACENM_0231': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1334],[SSCS_ACLog_1343],[CAN-IRD-180]'}, u'SWRD_GLOBAL-ACENM_0230': {'body': '', 'status': u'MATURE', 'additional': u'CT AC EP failure is computed only on ACLog2 board.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_574],[SSCS_ACLog_845],[SSCS_ACLog_576],[SSCS_ACLog_937],[SSCS_ACLog_1041],[SSCS_ACLog_957],[SSCS_ACLog_901],[SSCS_ACLog_1187],[SSCS_ACLog_913],[SSCS_ACLog_921],[SSCS_ACLog_926],[SSCS_ACLog_929],[SSCS_ACLog_928],[SSCS_ACLog_941],[SSCS_ACLog_1070],[SSCS_ACLog_1071],[SSCS_ACLog_1072],[SSCS_ACLog_1397],[SSCS_ACLog_1453],[SSCS_ACLog_1545],[SSCS_ACLog_1598],[SSCS_ACLog_1599],[SSCS_ACLog_1576],[CAN-IRD-180],[CAN-IRD-216],[CAN-IRD-870],[CAN-IRD-871],[CAN-IRD-1001]'}, u'SWRD_GLOBAL-ACENM_0343': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1368],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0342': {'body': '', 'status': u'MATURE', 'additional': u'Roll-over of fault index will be managed at design level (maximum 191 faults can be stored in NVM).', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Define LEG transition according to EDMU flight leg status.', 'issue': u'1.4', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0545': {'body': '', 'status': u'MATURE', 'additional': u'At start-up, the ACMPx open locked states are restored from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_721],[SSCS_ACLog_1585],[SSCS_ACLog_1587]'}, u'SWRD_GLOBAL-ACENM_0340': {'body': '', 'status': u'MATURE', 'additional': u'When the maximum number of fault stored in NVM is reached, there is a roll-over of the fault buffer. Roll-over of fault index will be managed at design level (maximum 191 faults can be stored in NVM).', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1376],[SSCS_ACLog_1381]'}, u'SWRD_GLOBAL-ACENM_0431': {'body': '', 'status': u'MATURE', 'additional': u'NO', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Copy of the ACMP calculated protection statuses in the associated ACMP global protections statuses.', 'issue': u'1.7', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0346': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1369],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0345': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1367],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0344': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1366],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0368': {'body': '', 'status': u'MATURE', 'additional': u'{CAN_X_DATAX_VALIDITY} of ACMPX_CMD are managed in another requirement.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_693]'}, u'SWRD_GLOBAL-ACENM_0309': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Synthesis of all the contactor DSO failures used to compute global contactor DSO failure.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0547': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-636]'}, u'SWRD_GLOBAL-ACENM_0061': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_598],[SSCS_ACLog_596],[SSCS_ACLog_1517]'}, u'SWRD_GLOBAL-ACENM_0141': {'body': '', 'status': u'MATURE', 'additional': u'At start-up these data are initialized first with values from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1142],[SSCS_ACLog_1262],[SSCS_ACLog_1119],[SSCS_ACLog_1503],[SSCS_ACLog_1443]'}, u'SWRD_GLOBAL-ACENM_0140': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_826]'}, u'SWRD_GLOBAL-ACENM_0143': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1329],[SSCS_ACLog_1331],[SSCS_ACLog_1333],[SSCS_ACLog_1340],[SSCS_ACLog_1342],[SSCS_ACLog_1336],[SSCS_ACLog_1345],[CAN-IRD-426],[CAN-IRD-427],[CAN-IRD-534]'}, u'SWRD_GLOBAL-ACENM_0142': {'body': '', 'status': u'MATURE', 'additional': u'The DSI linked to anti-paralleling are defined in HSID.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1063],[SSCS_ACLog_832],[SSCS_ACLog_833],[SSCS_ACLog_837]'}, u'SWRD_GLOBAL-ACENM_0145': {'body': '', 'status': u'MATURE', 'additional': u"The computation is done on the same frequencies sent on CAN busses [EXT_AC_FREQUENCY]. That's why there is no tolerance. ", 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1350],[SSCS_ACLog_1353],[CAN-IRD-792],[CAN-IRD-879]'}, u'SWRD_GLOBAL-ACENM_0301': {'body': '', 'status': u'MATURE', 'additional': u'Fuse failure computation is defined at HSID level.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1181],[SSCS_ACLog_1455]'}, u'SWRD_GLOBAL-ACENM_0147': {'body': '', 'status': u'MATURE', 'additional': u'10ms timing is defined in HSID', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_683],[SSCS_ACLog_1040],[SSCS_ACLog_1038]'}, u'SWRD_GLOBAL-ACENM_0146': {'body': '', 'status': u'MATURE', 'additional': u"The computation is done on the same power sent on CAN busses [EXT_AC_LOAD]. That's why there is no tolerance.", 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1351],[SSCS_ACLog_1353],[CAN-IRD-792],[CAN-IRD-879]'}, u'SWRD_GLOBAL-ACENM_0149': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_683]'}, u'SWRD_GLOBAL-ACENM_0148': {'body': '', 'status': u'MATURE', 'additional': u'TCB status is sent every 250ms to EDMU through CAN bus.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_682]'}, u'SWRD_GLOBAL-ACENM_0300': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure computation is defined at HSID level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0013': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[CAN-IRD-365],[CAN-IRD-525],[CAN-IRD-466],[CAN-IRD-366],[CAN-IRD-526],[CAN-IRD-367],[CAN-IRD-671],[CAN-IRD-501],[CAN-IRD-506]'}, u'SWRD_GLOBAL-ACENM_0541': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0012': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[CAN-IRD-365],[CAN-IRD-525],[CAN-IRD-466],[CAN-IRD-366],[CAN-IRD-526],[CAN-IRD-367],[CAN-IRD-671],[CAN-IRD-499],[CAN-IRD-505]'}, u'SWRD_GLOBAL-ACENM_0011': {'body': '', 'status': u'MATURE', 'additional': u'ACLog 1 is identified either by XLOG1 or ACLOG1. ACLog 2 is identified either by XLOG2 or ACLOG2.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[CAN-IRD-347]'}, u'SWRD_GLOBAL-ACENM_0369': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'This requirement is redundant with requirement SWRD_GLOBAL-ACENM_0383', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0041': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Source availability is no more impacted by failed open/closed states.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0042': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_571]'}, u'SWRD_GLOBAL-ACENM_0469': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0044': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_571]'}, u'SWRD_GLOBAL-ACENM_0045': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Source availability is no more impacted by failed open/closed states.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0046': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_571],[SSCS_ACLog_924]'}, u'SWRD_GLOBAL-ACENM_0047': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_571],[SSCS_ACLog_924]'}, u'SWRD_GLOBAL-ACENM_0048': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_571],[SSCS_ACLog_924]'}, u'SWRD_GLOBAL-ACENM_0049': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_557],[SSCS_ACLog_1225],[CAN-IRD-182]'}, u'SWRD_GLOBAL-ACENM_0363': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Initial value is provided at start-up.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0362': {'body': '', 'status': u'MATURE', 'additional': u'All messages are sent by EDMU every 1s.No valid CAN message means bad CRC on CAN message or bad CAN identifier or no message received or CAN HW error.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_693]'}, u'SWRD_GLOBAL-ACENM_0365': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_692]'}, u'SWRD_GLOBAL-ACENM_0364': {'body': '', 'status': u'MATURE', 'additional': u'A message is considered as failed if this message is not received on the CAN bus during 3 times its period.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_693]'}, u'SWRD_GLOBAL-ACENM_0367': {'body': '', 'status': u'MATURE', 'additional': u'Each ACMP is commanded only by one CAN bus, commands of an ACMP cannot be split between two CAN busses. If closed command of an ACMP is invalid, all the commands of this ACMP are switches to the other CAN bus.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_728],[SSCS_ACLog_730],[SSCS_ACLog_731],[SSCS_ACLog_693]'}, u'SWRD_GLOBAL-ACENM_0540': {'body': '', 'status': u'MATURE', 'additional': u'At start-up these data are initialized first with value from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1576],[SSCS_ACLog_1119],[SSCS_ACLog_1142],[SSCS_ACLog_1262],[SSCS_ACLog_1443]'}, u'SWRD_GLOBAL-ACENM_0543': {'body': '', 'status': u'MATURE', 'additional': u'There is one engineering data (containing 128 bytes) for each active failure', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1391]'}, u'SWRD_GLOBAL-ACENM_0197': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1058],[SSCS_ACLog_1098]'}, u'SWRD_GLOBAL-ACENM_0542': {'body': '', 'status': u'MATURE', 'additional': u'CAN Data without validities are extracted from the first CAN bus which provides the data.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1404],[SSCS_ACLog_1405],[SSCS_ACLog_693],[SSCS_ACLog_694],[CAN-IRD-857]'}, u'SWRD_GLOBAL-ACENM_0444': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1516]'}, u'SWRD_GLOBAL-ACENM_0390': {'body': '', 'status': u'MATURE', 'additional': u'The frequency range is defined in HSID. ', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Validity bit is computed for CAN bus.', 'issue': u'1.7', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0446': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0447': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0440': {'body': '', 'status': u'MATURE', 'additional': u'Write NVM first fault index.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1375]'}, u'SWRD_GLOBAL-ACENM_0441': {'body': '', 'status': u'MATURE', 'additional': u'The command of the AEC contactor is not sequenced. The command is directly applied independently from the other contactors.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1055]'}, u'SWRD_GLOBAL-ACENM_0442': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'FO/FC monitoring of the opposite contactor has been removed in SSCS', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0443': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'FO/FC monitoring of the opposite contactor has been removed in SSCS', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0448': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0449': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0193': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1056]'}, u'SWRD_GLOBAL-ACENM_0018': {'body': '', 'status': u'MATURE', 'additional': u'AEC is a normally closed contactor.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_892],[SSCS_ACLog_1308],[SSCS_ACLog_1412],[SSCS_ACLog_1363]'}, u'SWRD_GLOBAL-ACENM_0190': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1058]'}, u'SWRD_GLOBAL-ACENM_0549': {'body': '', 'status': u'MATURE', 'additional': u'At start-up this data is initialized first with value from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_920],[SSCS_ACLog_1196],[SSCS_ACLog_1607]'}, u'SWRD_GLOBAL-ACENM_0191': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Failed open/failed closed failures have no impact on network re-configuration', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0548': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1149],[SSCS_ACLog_922],[SSCS_ACLog_1181],[SSCS_ACLog_583],[SSCS_ACLog_1518]'}, u'SWRD_GLOBAL-ACENM_0215': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_744]'}, u'SWRD_GLOBAL-ACENM_0214': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_743]'}, u'SWRD_GLOBAL-ACENM_0217': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1335],[SSCS_ACLog_1344]'}, u'SWRD_GLOBAL-ACENM_0216': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_745]'}, u'SWRD_GLOBAL-ACENM_0211': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_737]'}, u'SWRD_GLOBAL-ACENM_0210': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_736]'}, u'SWRD_GLOBAL-ACENM_0213': {'body': '', 'status': u'MATURE', 'additional': u'For this contactor the hardware logic is inverted.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_739]'}, u'SWRD_GLOBAL-ACENM_0212': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_738]'}, u'SWRD_GLOBAL-ACENM_0397': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-215]'}, u'SWRD_GLOBAL-ACENM_0219': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_701]'}, u'SWRD_GLOBAL-ACENM_0218': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_701]'}, u'SWRD_GLOBAL-ACENM_0054': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_583]'}, u'SWRD_GLOBAL-ACENM_0288': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Global synthesis of all the CBIT failures is not used. ', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0289': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_909],[SSCS_ACLog_1083],[SSCS_ACLog_912],[SSCS_ACLog_919],[SSCS_ACLog_920],[SSCS_ACLog_1149],[SSCS_ACLog_924],[SSCS_ACLog_927],[SSCS_ACLog_932],[SSCS_ACLog_1194],[SSCS_ACLog_939],[SSCS_ACLog_940],[SSCS_ACLog_944],[SSCS_ACLog_1038],[SSCS_ACLog_840],[SSCS_ACLog_953],[SSCS_ACLog_902],[SSCS_ACLog_905]'}, u'SWRD_GLOBAL-ACENM_0286': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_955],[SSCS_ACLog_1141]'}, u'SWRD_GLOBAL-ACENM_0287': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'This requirement is not allocated to software.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0284': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1230]'}, u'SWRD_GLOBAL-ACENM_0285': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_955],[SSCS_ACLog_1141],[SSCS_ACLog_1615]'}, u'SWRD_GLOBAL-ACENM_0282': {'body': '', 'status': u'MATURE', 'additional': u'NO', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_899],[SSCS_ACLog_1084]'}, u'SWRD_GLOBAL-ACENM_0283': {'body': '', 'status': u'MATURE', 'additional': u'Write accesses to NVM are not authorized during NVM download to avoid inconsistency in NVM (checksum issue).', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1364]'}, u'SWRD_GLOBAL-ACENM_0280': {'body': '', 'status': u'MATURE', 'additional': u'The procedure to test the AC EP current transformer is described in HSID. This test is only performed on ACLog2 board.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1141],[SSCS_ACLog_1419]'}, u'SWRD_GLOBAL-ACENM_0281': {'body': '', 'status': u'MATURE', 'additional': u'The procedure to test the 5s power cut function is described in HSID.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_902]'}, u'SWRD_GLOBAL-ACENM_0051': {'body': '', 'status': u'MATURE', 'additional': u'N/A ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_583]'}, u'SWRD_GLOBAL-ACENM_0199': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_839],[SSCS_ACLog_526]'}, u'SWRD_GLOBAL-ACENM_0427': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_722],[SSCS_ACLog_725],[SSCS_ACLog_728],[SSCS_ACLog_729],[SSCS_ACLog_730],[SSCS_ACLog_731],[SSCS_ACLog_693],[SSCS_ACLog_694],[SSCS_ACLog_1496],[CAN-IRD-857],[CAN-IRD-1017]'}, u'SWRD_GLOBAL-ACENM_0138': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1328],[SSCS_ACLog_1330],[SSCS_ACLog_1332],[SSCS_ACLog_1339],[SSCS_ACLog_1341],[SSCS_ACLog_1336],[SSCS_ACLog_1345],[CAN-IRD-426],[CAN-IRD-427],[CAN-IRD-534]'}, u'SWRD_GLOBAL-ACENM_0139': {'body': '', 'status': u'MATURE', 'additional': u'At start-up these data are initialized first with values from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_831],[SSCS_ACLog_1142],[SSCS_ACLog_1262],[SSCS_ACLog_1119],[SSCS_ACLog_1443]'}, u'SWRD_GLOBAL-ACENM_0130': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'GFI protection has been removed from SSCS', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0131': {'body': '', 'status': u'MATURE', 'additional': u'The maximum opening time of the contactor (20ms) is included in the tolerance.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_865],[SSCS_ACLog_866],[SSCS_ACLog_867],[SSCS_ACLog_1499],[SSCS_ACLog_1457],[SSCS_ACLog_1546]'}, u'SWRD_GLOBAL-ACENM_0132': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_865],[SSCS_ACLog_866],[SSCS_ACLog_1594]'}, u'SWRD_GLOBAL-ACENM_0133': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_865],[SSCS_ACLog_866],[SSCS_ACLog_1594]'}, u'SWRD_GLOBAL-ACENM_0134': {'body': '', 'status': u'MATURE', 'additional': u'Converter failure computation is defined at HSID level.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1181],[SSCS_ACLog_1455]'}, u'SWRD_GLOBAL-ACENM_0135': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_912],[SSCS_ACLog_1181],[SSCS_ACLog_1195],[SSCS_ACLog_1084]'}, u'SWRD_GLOBAL-ACENM_0136': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_846],[SSCS_ACLog_1114],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0137': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_850],[SSCS_ACLog_1114],[SSCS_ACLog_1499]'}, u'SWRD_GLOBAL-ACENM_0488': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-727]'}, u'SWRD_GLOBAL-ACENM_0489': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0521': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1282]'}, u'SWRD_GLOBAL-ACENM_0520': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_501],[SSCS_ACLog_527]'}, u'SWRD_GLOBAL-ACENM_0527': {'body': '', 'status': u'MATURE', 'additional': u'The power cut test result of the second execution override the result of the first execution.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_902]'}, u'SWRD_GLOBAL-ACENM_0526': {'body': '', 'status': u'MATURE', 'additional': u'If NVM download request or NVM reset request or IBIT request are sent at the same time, only the first command received will be taken into account', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1528]'}, u'SWRD_GLOBAL-ACENM_0525': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1257]'}, u'SWRD_GLOBAL-ACENM_0524': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1507],[SSCS_ACLog_548]'}, u'SWRD_GLOBAL-ACENM_0480': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0481': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0482': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-772]'}, u'SWRD_GLOBAL-ACENM_0483': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0484': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0485': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0486': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-727]'}, u'SWRD_GLOBAL-ACENM_0487': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-727]'}, u'SWRD_GLOBAL-ACENM_0310': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default value NOT_FAILED is specified during SW initialization phase.', 'issue': u'1.0', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0311': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Synthesis of all the other DSO failures used to compute global other DSO failure.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0312': {'body': '', 'status': u'MATURE', 'additional': u'HW keeps transparency during 5ms and SW read DSI every 1ms. SW uses transparency information to avoid NVM corruption at start up.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1261]'}, u'SWRD_GLOBAL-ACENM_0313': {'body': '', 'status': u'MATURE', 'additional': u'A mapping of NVM is defined in order to specify block of memory allocated by functionalities.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1491]'}, u'SWRD_GLOBAL-ACENM_0314': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'NVM storage is managed at design level.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0315': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Upper requirement has been removed. HW and SW PN are stored in NVM during ATP.', 'issue': u'1.5', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0316': {'body': '', 'status': u'MATURE', 'additional': u'Improve lifetime of NVM device by not writing the same value several times.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_1119]'}, u'SWRD_GLOBAL-ACENM_0317': {'body': '', 'status': u'MATURE', 'additional': u'Improve lifetime of NVM device by not writing the same value several times.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1582],[SSCS_ACLog_1584]'}, u'SWRD_GLOBAL-ACENM_0251': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'YES', 'safety': u'NO', 'rationale': u'Hardware component used is compliant with the ARINC-825 standard.', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1044],[CAN-IRD-312]'}, u'SWRD_GLOBAL-ACENM_0250': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[CAN-IRD-324],[SSCS_ACLog_706]'}, u'SWRD_GLOBAL-ACENM_0253': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1530]'}, u'SWRD_GLOBAL-ACENM_0252': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1363]'}, u'SWRD_GLOBAL-ACENM_0255': {'body': '', 'status': u'MATURE', 'additional': u'At start-up this data is initialized first with value from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1216],[SSCS_ACLog_1217],[SSCS_ACLog_919],[SSCS_ACLog_1196],[SSCS_ACLog_1603],[SSCS_ACLog_1604]'}, u'SWRD_GLOBAL-ACENM_0254': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1363],[SSCS_ACLog_892]'}, u'SWRD_GLOBAL-ACENM_0257': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Management of all the failed open failures for GLC1, GLC2 and ALC are merged in one requirement', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0256': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Failed closed failure is no more used', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0004': {'body': '', 'status': u'MATURE', 'additional': u'To be compliant with the protection timing constraint', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_695]'}, u'SWRD_GLOBAL-ACENM_0005': {'body': '', 'status': u'MATURE', 'additional': u'Maximum processing time are dedicated to HW. The "Tbit" data is computed from CAN refresh rate (1/500).', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_657],[CAN-IRD-314]'}, u'SWRD_GLOBAL-ACENM_0006': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[CAN-IRD-345],[CAN-IRD-313]'}, u'SWRD_GLOBAL-ACENM_0007': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[CAN-IRD-344],[CAN-IRD-313],[CAN-IRD-331],[CAN-IRD-332]'}, u'SWRD_GLOBAL-ACENM_0552': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0001': {'body': '', 'status': u'MATURE', 'additional': u'Acquisition frequency should be twice higher than maximum ASI frequency to measure (650Hz x 2)  ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A  ', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_695]'}, u'SWRD_GLOBAL-ACENM_0002': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'To be compliant with the protection measurement accuracy constraint', 'issue': u'1.6', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0003': {'body': '', 'status': u'MATURE', 'additional': u'To be compliant with the protection timing constraint', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_695]'}, u'SWRD_GLOBAL-ACENM_0417': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-338],[CAN-IRD-869]'}, u'SWRD_GLOBAL-ACENM_0416': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[CAN-IRD-336]'}, u'SWRD_GLOBAL-ACENM_0415': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[CAN-IRD-335],[CAN-IRD-364]'}, u'SWRD_GLOBAL-ACENM_0414': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[CAN-IRD-334]'}, u'SWRD_GLOBAL-ACENM_0413': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[CAN-IRD-333],[CAN-IRD-107],[CAN-IRD-108],[CAN-IRD-109],[CAN-IRD-110]'}, u'SWRD_GLOBAL-ACENM_0412': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'BNR format constraint is now traced on each HLR using BNR data ', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0411': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[CAN-IRD-317]'}, u'SWRD_GLOBAL-ACENM_0410': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[CAN-IRD-316]'}, u'SWRD_GLOBAL-ACENM_0544': {'body': '', 'status': u'MATURE', 'additional': u'There is one engineering data (containing 128 bytes) for each active failure', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1391]'}, u'SWRD_GLOBAL-ACENM_0529': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1455]'}, u'SWRD_GLOBAL-ACENM_0528': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1041],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0029': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Managed in the NVM acceptance.', 'issue': u'1.7', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0010': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[CAN-IRD-351]'}, u'SWRD_GLOBAL-ACENM_0144': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Redundant with requirement SWRD_GLOBAL-ACENM_0143', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0426': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'CPU margin is defined in order to keep resource for future evolutions.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0355': {'body': '', 'status': u'MATURE', 'additional': u'This alias is used to check if there is no communication on the two CAN busses.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_701]'}, u'SWRD_GLOBAL-ACENM_0356': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_663]'}, u'SWRD_GLOBAL-ACENM_0425': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_1087]'}, u'SWRD_GLOBAL-ACENM_0422': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Each contactor failure management is specific and has been split.', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0423': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'ACMPX failed open and failed closed failures are no more latched in context NVM', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0259': {'body': '', 'status': u'MATURE', 'additional': u'This failure is not latched in context NVM and is reset at each software start-up.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_919],[SSCS_ACLog_1196],[SSCS_ACLog_1612]'}, u'SWRD_GLOBAL-ACENM_0352': {'body': '', 'status': u'MATURE', 'additional': u'Checksum computation will be defined at design level.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1079],[SSCS_ACLog_1384],[SSCS_ACLog_1385],[SSCS_ACLog_1388],[SSCS_ACLog_1389],[SSCS_ACLog_1390],[SSCS_ACLog_1391]'}, u'SWRD_GLOBAL-ACENM_0258': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Failed closed failure is no more used', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0353': {'body': '', 'status': u'MATURE', 'additional': u'Checksum computation will be defined at design level. If the number of occurrence maximum is reached, the fault occurrence remains to 255.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1079],[SSCS_ACLog_1383],[SSCS_ACLog_1386],[SSCS_ACLog_1387],[SSCS_ACLog_1389],[SSCS_ACLog_1390],[SSCS_ACLog_1391]'}, u'SWRD_GLOBAL-ACENM_0419': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Merged in SWRD_GLOBAL-ACENM_0013', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0178': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_559]'}, u'SWRD_GLOBAL-ACENM_0179': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_561],[SSCS_ACLog_585],[SSCS_ACLog_589],[SSCS_ACLog_591],[SSCS_ACLog_1219]'}, u'SWRD_GLOBAL-ACENM_0174': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_559],[SSCS_ACLog_585],[SSCS_ACLog_565],[SSCS_ACLog_1462]'}, u'SWRD_GLOBAL-ACENM_0175': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_559],[SSCS_ACLog_585],[SSCS_ACLog_565],[SSCS_ACLog_1462]'}, u'SWRD_GLOBAL-ACENM_0176': {'body': '', 'status': u'MATURE', 'additional': u"The computation is done on the same voltage sent on CAN busses [EXT_AC_PHX_VOLTAGE]. That's why there is no tolerance.", 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1352],[SSCS_ACLog_1353],[CAN-IRD-792],[CAN-IRD-879]'}, u'SWRD_GLOBAL-ACENM_0177': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_559],[SSCS_ACLog_585],[SSCS_ACLog_561]'}, u'SWRD_GLOBAL-ACENM_0170': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1068],[SSCS_ACLog_1121],[SSCS_ACLog_721],[SSCS_ACLog_661],[SSCS_ACLog_466],[SSCS_ACLog_869],[SSCS_ACLog_1122],[SSCS_ACLog_1320],[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0171': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.12', 'refer': u'[SSCS_ACLog_1068],[SSCS_ACLog_1121],[SSCS_ACLog_721],[SSCS_ACLog_661],[SSCS_ACLog_463],[SSCS_ACLog_868],[SSCS_ACLog_1122],[SSCS_ACLog_1320],[SSCS_ACLog_1576]'}, u'SWRD_GLOBAL-ACENM_0172': {'body': '', 'status': u'MATURE', 'additional': u'During IBIT contactor commands to apply are restored from static memory', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_663]'}, u'SWRD_GLOBAL-ACENM_0173': {'body': '', 'status': u'MATURE', 'additional': u'During IBIT contactor commands to apply are restored from static memory', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_663]'}, u'SWRD_GLOBAL-ACENM_0358': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Used in order to ignore a IBIT command when the network reconfiguration is in progress.', 'issue': u'1.0', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0418': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[CAN-IRD-365],[CAN-IRD-525],[CAN-IRD-466],[CAN-IRD-366],[CAN-IRD-526],[CAN-IRD-367],[CAN-IRD-671],[CAN-IRD-331],[CAN-IRD-858],[CAN-IRD-712]'}, u'SWRD_GLOBAL-ACENM_0186': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.2', 'refer': u'[SSCS_ACLog_1056],[SSCS_ACLog_1058],[SSCS_ACLog_1206]'}, u'SWRD_GLOBAL-ACENM_0359': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Initial value is provided at start-up.', 'issue': u'1.1', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0196': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1058],[SSCS_ACLog_1098]'}, u'SWRD_GLOBAL-ACENM_0318': {'body': '', 'status': u'MATURE', 'additional': u'Improve lifetime of NVM device by not writing the same value several times.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1586],[SSCS_ACLog_1588]'}, u'SWRD_GLOBAL-ACENM_0194': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1056],[SSCS_ACLog_1098]'}, u'SWRD_GLOBAL-ACENM_0195': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1056],[SSCS_ACLog_1098]'}, u'SWRD_GLOBAL-ACENM_0192': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Failed open/failed closed failures have no impact on network re-configuration', 'issue': u'1.11', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0428': {'body': '', 'status': u'MATURE', 'additional': u'NO', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1176]'}, u'SWRD_GLOBAL-ACENM_0059': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Contactor status validity deleted from SSCS', 'issue': u'1.9', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0058': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_596],[SSCS_ACLog_595]'}, u'SWRD_GLOBAL-ACENM_0057': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_598],[SSCS_ACLog_596],[SSCS_ACLog_1517]'}, u'SWRD_GLOBAL-ACENM_0056': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_583]'}, u'SWRD_GLOBAL-ACENM_0055': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1518]'}, u'SWRD_GLOBAL-ACENM_0292': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure has no impact on power supply monitoring.', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0053': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_583]'}, u'SWRD_GLOBAL-ACENM_0052': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1518]'}, u'SWRD_GLOBAL-ACENM_0198': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.1', 'refer': u'[SSCS_ACLog_912],[SSCS_ACLog_1181],[SSCS_ACLog_1195]'}, u'SWRD_GLOBAL-ACENM_0050': {'body': '', 'status': u'MATURE', 'additional': u'NO', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A ', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1111],[SSCS_ACLog_1126],[SSCS_ACLog_1466]'}, u'SWRD_GLOBAL-ACENM_0518': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1449],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0519': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1452],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0512': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-180]'}, u'SWRD_GLOBAL-ACENM_0513': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_829],[SSCS_ACLog_1062],[SSCS_ACLog_933],[SSCS_ACLog_1192],[SSCS_ACLog_1193],[SSCS_ACLog_449],[SSCS_ACLog_943],[SSCS_ACLog_1118],[SSCS_ACLog_1116],[SSCS_ACLog_1256],[SSCS_ACLog_1458],[SSCS_ACLog_1545],[CAN-IRD-216]'}, u'SWRD_GLOBAL-ACENM_0510': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0511': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-180]'}, u'SWRD_GLOBAL-ACENM_0516': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1261]'}, u'SWRD_GLOBAL-ACENM_0517': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1477],[SSCS_ACLog_1478]'}, u'SWRD_GLOBAL-ACENM_0514': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'A flight leg fault counter is defined to manage the storage management of the failure.', 'issue': u'1.4', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0515': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[SSCS_ACLog_1261]'}, u'SWRD_GLOBAL-ACENM_0453': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'YES', 'safety': u'NO', 'rationale': u'This requirement only depends on the CAN protocol defined in CAN IRD. ', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1494],[CAN-IRD-848]'}, u'SWRD_GLOBAL-ACENM_0452': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0451': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1506]'}, u'SWRD_GLOBAL-ACENM_0450': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0457': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0456': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0455': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0454': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0459': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.4', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394]'}, u'SWRD_GLOBAL-ACENM_0458': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[CAN-IRD-315],[CAN-IRD-392],[CAN-IRD-394],[CAN-IRD-845]'}, u'SWRD_GLOBAL-ACENM_0429': {'body': '', 'status': u'MATURE', 'additional': u'Timeout is defined in HSID. Watchdog needs to be periodically refreshed in order to avoid a CPU reset. ', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_1103]'}, u'SWRD_GLOBAL-ACENM_0220': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_701]'}, u'SWRD_GLOBAL-ACENM_0221': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[CAN-IRD-194],[CAN-IRD-767],[CAN-IRD-195],[CAN-IRD-422],[CAN-IRD-423],[CAN-IRD-198]'}, u'SWRD_GLOBAL-ACENM_0222': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_597],[SSCS_ACLog_615],[SSCS_ACLog_879],[SSCS_ACLog_1226],[CAN-IRD-185],[CAN-IRD-186],[CAN-IRD-1001]'}, u'SWRD_GLOBAL-ACENM_0223': {'body': '', 'status': u'MATURE', 'additional': u'Trip cause is the same for each phase (protections are not computed by phase).', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_677],[SSCS_ACLog_718],[SSCS_ACLog_719],[SSCS_ACLog_1582],[SSCS_ACLog_1584],[SSCS_ACLog_1586],[SSCS_ACLog_1588],[CAN-IRD-194],[CAN-IRD-767],[CAN-IRD-195]'}, u'SWRD_GLOBAL-ACENM_0224': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[CAN-IRD-731],[CAN-IRD-1001],[SSCS_ACLog_1460],[SSCS_ACLog_1542]'}, u'SWRD_GLOBAL-ACENM_0225': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_506],[CAN-IRD-731],[CAN-IRD-1001],[SSCS_ACLog_1460]'}, u'SWRD_GLOBAL-ACENM_0226': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1073],[SSCS_ACLog_1074],[CAN-IRD-464],[CAN-IRD-688],[CAN-IRD-689],[CAN-IRD-205],[CAN-IRD-207],[SSCS_ACLog_1360],[SSCS_ACLog_1362],[SSCS_ACLog_1393],[CAN-IRD-1001]'}, u'SWRD_GLOBAL-ACENM_0227': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_550],[CAN-IRD-215],[CAN-IRD-1001]'}, u'SWRD_GLOBAL-ACENM_0228': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_686],[CAN-IRD-201],[CAN-IRD-1001]'}, u'SWRD_GLOBAL-ACENM_0229': {'body': '', 'status': u'MATURE', 'additional': u'Network is always considered as valid.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.9', 'refer': u'[SSCS_ACLog_1127],[SSCS_ACLog_1128],[SSCS_ACLog_1226],[SSCS_ACLog_1227],[SSCS_ACLog_1228],[CAN-IRD-180],[CAN-IRD-181],[CAN-IRD-1001]'}, u'SWRD_GLOBAL-ACENM_0354': {'body': '', 'status': u'MATURE', 'additional': u'Default values are specified for data which are extracted from CAN bus when data are not available or not valid on the two CAN busses or when software is in INIT mode.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_1068]'}, u'SWRD_GLOBAL-ACENM_0040': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_571]'}, u'SWRD_GLOBAL-ACENM_0424': {'body': '', 'status': u'MATURE', 'additional': u'Each EDMU_ACMPX_TRIPPED_CMD is associated with one ACMP. An ACMP can receive a TRIP reset independently from other ACMPs. At start-up, the ACMPx tripped states are restored from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.7', 'refer': u'[SSCS_ACLog_721],[SSCS_ACLog_1119],[SSCS_ACLog_1280],[SSCS_ACLog_1581],[SSCS_ACLog_1582],[SSCS_ACLog_1583],[SSCS_ACLog_1584]'}, u'SWRD_GLOBAL-ACENM_0357': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'YES', 'rationale': u'N/A', 'issue': u'1.0', 'refer': u'[SSCS_ACLog_663]'}, u'SWRD_GLOBAL-ACENM_0299': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default value NOT_FAILED is specified during SW initialization phase.', 'issue': u'1.7', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0298': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure has no impact on power supply monitoring.', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0420': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Merged in SWRD_GLOBAL-ACENM_0012', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0421': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.6', 'refer': u'[SSCS_ACLog_1486],[CAN-IRD-182]'}, u'SWRD_GLOBAL-ACENM_0295': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Fuse failure has no impact on power supply monitoring.', 'issue': u'1.4', 'refer': 'EMPTY'}, u'SWRD_GLOBAL-ACENM_0294': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1183],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0297': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1183],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0296': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default value NOT_FAILED is specified during SW initialization phase.', 'issue': u'1.0', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0291': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.5', 'refer': u'[SSCS_ACLog_1183],[SSCS_ACLog_1181]'}, u'SWRD_GLOBAL-ACENM_0290': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default value NOT_FAILED is specified during SW initialization phase.', 'issue': u'1.0', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0293': {'body': '', 'status': u'MATURE', 'additional': u'N/A', 'derived': u'YES', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'Default value NOT_FAILED is specified during SW initialization phase.', 'issue': u'1.0', 'refer': u'N/A'}, u'SWRD_GLOBAL-ACENM_0550': {'body': '', 'status': u'MATURE', 'additional': u'At start-up this data is initialized first with value from NVM.', 'derived': u'NO', 'terminal': u'NO', 'safety': u'NO', 'rationale': u'N/A', 'issue': u'1.11', 'refer': u'[SSCS_ACLog_920],[SSCS_ACLog_1196],[SSCS_ACLog_1608]'}, u'SWRD_GLOBAL-ACENM_0043': {'body': '', 'status': u'DELETED', 'additional': 'EMPTY', 'derived': 'EMPTY', 'terminal': 'EMPTY', 'safety': 'EMPTY', 'rationale': u'Source availability is no more impacted by failed open/closed states.', 'issue': u'1.5', 'refer': 'EMPTY'}}
        tbl_list_req=[]
        for name,value in extract_req.tbl_list_llr.iteritems():
            status = CheckLLR.getAtribute(value,"status")
            if status != "DELETED":
                tbl_list_req.append(name)
        tbl_list_req.sort()
        extract_req.basename = dir_swdd
        extract_req.hlr_selected = False
        print "THREE"
        extract_req.tbl_list_llr.clear()
        extract_req.extract(dirname=dir_swdd,
                         type=("SWDD",))
        hlr_vs_llr = {}
        for req,value in extract_req.tbl_list_llr.iteritems():
            print "Req:",req,value
            list_refer,list_constraints = extract_req.getLLR_Trace(value)
            print "list_refer:",list_refer
            for refer in list_refer:
                if refer not in hlr_vs_llr:
                    hlr_vs_llr[refer]=[req]
                else:
                    hlr_vs_llr[refer].append(req)
        print "hlr_vs_llr:",hlr_vs_llr
        #for x in extract_req.tbl_list_llr:
        #    print "check_is.tbl_list_llr",x

        report_filename = export_scod_html.exportHTML(list_reqs_spec = tbl_list_req,
                                                      list_llr_per_hlr = hlr_vs_llr)
        export_scod_html.start()
