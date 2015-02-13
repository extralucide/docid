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
                 group,
                 sub_group,
                 artic,
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
    def __init__(self):
        self.filename = "getQA.html"
        # Django settings
        try:
            settings.configure(DEBUG=True,
                               TEMPLATE_DEBUG=True,
                               TEMPLATE_LOADERS=('django.template.loaders.filesystem.Loader',
                                                'django.template.loaders.app_directories.Loader'),
                               TEMPLATE_DIRS=('template',))
            setup()
        except NameError:
            print "Missing Django module."
        except RuntimeError:
            print "Settings already configured."
    def start(self):
        os.startfile(self.filename)

    def get(self,qams_user_id,action_id=False,url_root="localhost",name=""):
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

    def createListIG(self,item="FPGA",list_ig={},tbl_ig_items=[]):
        list = []
        self.sqlite_connect()
        if item=="Certification":
            for id in range(1,10):
                doc = self.sqlite_get_docs_certification((id,))
                link = "doc/{:s}".format(doc[0][4])
                type = doc[0][0]
                reference = doc[0][1]
                version = doc[0][2]
                title = doc[0][3]
                list.append((id,reference,type,title,link,version))
                #keys =["Type","Reference","Indice","Titre","Link"]
                #list_upper = self.sqlite_get_child(parent_id)
                # for child_id in list_upper:
                #     cert_doc = self.sqlite_get_docs_certification(child_id)
                #     for tbl in cert_doc:
                #         dico = dict(zip(keys, tbl))
                #         type = dico["Type"]
                #         reference = dico["Reference"]
                #         title = dico["Titre"]
                #         link = "doc/{:s}".format(dico["Link"])
                #         version = dico["Indice"]
                #         list.append(("",reference,type,title,link,version))
                #         print "CHILD",("",reference,type,title,link,version)
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
            settings.configure(DEBUG=True,
                               TEMPLATE_DEBUG=True,
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
                      ((1,2,3,6,8),"DO-178"),
                      ((4,7),"DO-254"))
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
    if 0==1:
        easy_ig = easyIG()
        easy_ig.get()
        easy_ig.start()
    getqa = getQA()
    getqa.get(qams_user_id=1,action_id=1555)
    getqa.start()