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

 This file gte IG from intranet and post process data.

"""
__author__ = "O. Appere <olivier.appere@gmail.com>"
__date__ = "17th of November 2014"
__version__ = "0.3.0"
import xml.etree.ElementTree as ET
import sys
import os
import urllib2
from HTMLParser import HTMLParser
import sqlite3 as lite
import re
from datetime import datetime

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
                cur.execute("SELECT type,reference,indice,title,link FROM docs_certification WHERE id LIKE '{:d}'".format(id[0]))
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
class easyIG():
    """
    Use the E-factory from lxml.builder which provides a simple and compact syntax for generating XML and HTML
    """
    def start(self):
        os.startfile("easyIG.html")

    def __init__(self):
        # Change url = http://spar-syner1.in.com:8600/change
        # Read procedures page
        url_intranet_root = "http://intranet-ece.in.com/dq/documentation/"
        # IG
        url_intranet = "http://intranet-ece.in.com/dq/documentation/procedures_zodiac_aero_electric"
        try:
            response = urllib2.urlopen(url_intranet)
            html = response.read()
        except IOError,e:
            html = ""
            print e
        header = ["Type","Reference","Indice","Titre","Application","MQ","Link","New"]
        parser = MyHTMLParser(header)
        parser.feed(html)
        parser.header.append("Link")
        parser.header.append("New")
        # SAQ
        try:
            response_templates = urllib2.urlopen(url_intranet_root + "formulaires")
            html = response_templates.read()
        except IOError,e:
            html = ""
            print e
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
        prev_type = ""

        # Prepare HTML document
        racine = ET.Element("html")
        head = ET.SubElement(racine, "head")
        title = ET.SubElement(head, "title")
        title.text = "IG - procedures"
        # CSS
        link = parser.createLinkCss(head,"css/easy_ig.css")
        link = parser.createLinkCss(head,"css/jquery-ui.css")
        link = parser.createLinkCss(head,"css/style.css")
        #link = ET.SubElement(head, "link")
        #link.set("rel", "stylesheet")
        #link.set("type", "text/css")
        #link.set("href", "easy_ig.css")
        # Javascript
        js = parser.createLinkJS(head,"js/easy_ig.js")
        js = parser.createLinkJS(head,"js/jquery-ui.js")
        js = parser.createLinkJS(head,"js/jquery-1.10.2.js")
        #script = ET.SubElement(head, "script")
        #script.set("type", "text/javascript")
        #script.set("src", "js/easy_ig.js")
        #script.text = "dummy"
        body = ET.SubElement(racine, "body")
        div_header = ET.SubElement(body, "div",attrib={"id":"bandeau"})
        div_title = ET.SubElement(div_header, "div",attrib={"id":"bandeau2"})
        header1 = ET.SubElement(div_title, "h2")
        header1.text = "Procedures Zodiac Aero Electric"
        div1 = ET.SubElement(body, "div",attrib={"id":"main"})
        div_top = ET.SubElement(div1, "div",attrib={"id":"page_tabs"})
        div_general = ET.SubElement(div_top, "div",attrib={"id":"general"})
        div_general.text = "General"
        div_software = ET.SubElement(div_top, "div",attrib={"id":"software"})
        div_software.text = "Software"
        div_fpga = ET.SubElement(div_top, "div",attrib={"id":"fpga"})
        div_fpga.text = "FPGA"
        div_hardware = ET.SubElement(div_top, "div",attrib={"id":"hardware"})
        div_hardware.text = "Hardware"
        div_bench = ET.SubElement(div_top, "div",attrib={"id":"bench"})
        div_bench.text = "Bench"
        div_agile = ET.SubElement(div_top, "div",attrib={"id":"agile"})
        div_agile.text = "Agile"
        div_new = ET.SubElement(div_top, "div",attrib={"id":"new"})
        div_new.text = "New"
        div_change = ET.SubElement(div_top, "div",attrib={"id":"change"})
        div_change.text = "Change"
        div_certification = ET.SubElement(div_top, "div",attrib={"id":"certification"})
        div_certification.text = "Certification"
        div_apropos = ET.SubElement(div_top, "div",attrib={"id":"apropos"})
        div_apropos.text = "A propos"
        div_clearb = ET.SubElement(div1, "div",attrib={"class":"clearer"})
        div_square = ET.SubElement(div1, "div",attrib={"class":"nice_square"})
        # General
        div_general_c = ET.SubElement(div_square, "div",attrib={"id":"general_c"})

          # <div id="menu">
          #   <ul class="top_group level-one">
          #     <a class="short selected">Zodiac Aero Electric</a>
          #     <li class="group">
          #       <a class="short" href="#subgroup_1" name="subgroup_1" onClick="show_ig('subgroup_1')">Generalit&#233;s</a>
          #       <ul class="hidden" id="subgroup_1">
          #         <li class="sub_group">
          #           <a class="short" href="#artic_1" name="artic_1" onClick="show_ig('artic_1')">Activit&#233;s industrielles</a>
          #           <ul class="hidden" id="artic_1">
          #             <li class="articulation">
          #               <a class="short" href="#article_1" name="article_1">Commercial - Supply Chain</a>
          #               <ul>
          #                 <li class="dark">
          #                   <a href="#0_2_0_001" name="0_2_0_001" onClick="show_ig('0_2_0_001')" style="float:right">
          #                     <span class="down_arrow" onClick="return display_action_comment('0_2_0_001',this)" style="float:right">
          #                     </span></a>
          #                   <a class="wide" href="http://intranet-ece.in.com:8080/dq_docece_data/1.pdf">IG 0.2.0.001 version D: Revue de Passage en production s&#233;rie "Production Readiness Review" (PRR) </a>
          #                   <ul class="hidden" id="0_2_0_001">
          #                     <li class="list_saq">
          #                       <a href="http://intranet-ece.in.com:8080/dq_form_data\44.dot" style="">SAQ062 version /: Bordereau de diffusion des plans</a></li>
          #                     <li class="list_saq">
          #                       <a href="http://intranet-ece.in.com:8080/dq_form_data\134.xls" style="">SAQ174 version B: Revue de passage en production s&#233;rie (PRR)</a></li>
          #                   </ul></li>

        # Start accordion
        div_accordion = ET.SubElement(div_general_c, "div",attrib={"id":"accordion"})
        color_flag = 0
        # <ul class="group">
        ul_group = ET.SubElement(div_accordion, "ul",attrib={"class":"top_group level-one"})
        hyperlink = ET.SubElement(ul_group, "a",attrib={"class":"short selected"})
        hyperlink.text = "Zodiac Aero Electric"
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
                id = m.group(4)
                #print "GROUP",groupe
                groupe_id,groupe_description = parser.sqlite_get_groupe(groupe)
                if groupe != prev_gr:
                    # on change de groupe
                    prev_gr = groupe
                    # <li class="group">
                    li0 = ET.SubElement(ul_group, "li",attrib={"class":"group"})
                    hyperlink0 = ET.SubElement(li0, "a",attrib={"class":"short"})
                    hyperlink0.text = groupe_description
                    tag = "subgroup_{:d}".format(groupe_id)
                    hyperlink0.set("href","#"+tag)
                    hyperlink0.set("name",tag)
                    hyperlink0.set("onClick","show_ig('{:s}')".format(tag))
                    ul1 = ET.SubElement(li0, "ul",attrib={"class":"hidden","id":tag})
                    #print groupe_description
                sous_groupe_id,sous_groupe_description = parser.sqlite_get_sous_groupe(groupe,sous_groupe)
                if gr_sgr != prev_gr_sgr and sous_groupe_id is not None:
                    # On change de sous groupe
                    prev_gr_sgr = gr_sgr
                    prev_sous_groupe_description = sous_groupe_description
                    # <li class="sub_group">
                    li1 = ET.SubElement(ul1, "li",attrib={"class":"sub_group"})
                    hyperlink1 = ET.SubElement(li1, "a",attrib={"class":"short"})
                    hyperlink1.text = sous_groupe_description
                    tag = "artic_{:d}".format(sous_groupe_id)
                    hyperlink1.set("href","#"+tag)
                    hyperlink1.set("name",tag)
                    hyperlink1.set("onClick","show_ig('{:s}')".format(tag))
                    ul3 = ET.SubElement(li1, "ul",attrib={"class":"hidden","id":tag})
                    #print "   ",sous_groupe_description
                articulation_id,articulation_description = parser.sqlite_get_articulation(groupe,sous_groupe,articulation)
                if gr_sgr_art != prev_gr_sgr_art and articulation_id is not None:
                    # On change d articulation
                    prev_gr_sgr_art = gr_sgr_art
                    li2 = ET.SubElement(ul3, "li",attrib={"class":"articulation"})
                    hyperlink2 = ET.SubElement(li2, "a",attrib={"class":"short"})
                    tag = "article_{:d}".format(articulation_id)
                    hyperlink2.set("href","#"+tag)
                    hyperlink2.set("name",tag)
                    ul4 = ET.SubElement(li2, "ul")
                    hyperlink2.text = articulation_description
                    #print "         ",articulation_description
                # <li class="dark"><a href="http://intranet-ece.in.com:8080/dq_docece_data/615.pdf">IG 0.2.1.032: Guide utilisateur du devis NRC</a></li>
                li3 = ET.SubElement(ul4, "li",attrib={"class":"articulation"})
                # Button Show SAQ
                if reference in dico_ig_tbl_saq:
                    tag_saq = re.sub(r'\.',r'_',reference)
                    hyperlink_right = ET.SubElement(li3, "a",attrib={"href":"#"+tag_saq,"name":tag_saq,"style":"float:right"})
                    hyperlink_right.text = ""
                    hyperlink_right.set("onClick","show_ig('{:s}')".format(tag_saq))
                    span = ET.SubElement(hyperlink_right, "span",attrib={"class":"down_arrow","style":"float:right","onClick":"return display_action_comment('{:s}',this)".format(tag_saq)})
                    #span.text = "TEST"
                    #img = ET.SubElement(hyperlink_right, "img",attrib={"style":"float:right","src":"img/down_arrow_2.png"})
                #img.text = "y"
                # Hyperlink IG
                hyperlink = ET.SubElement(li3, "a",attrib={"class":"wide"})
                hyperlink.text ="{:s} {:s} version {:s}: {:s}".format(type,reference,version,title)
                hyperlink.set("href", link)
                if color_flag % 2:
                    li3.set("class","dark")
                else:
                    li3.set("class","light")
                header,obsolete = parser.sqlite_get_char(reference)
                if header and obsolete:
                    hyperlink.set("class","wide obsolete_and_header")
                elif header:
                    hyperlink.set("class","wide top_ig")
                elif obsolete:
                    hyperlink.set("class","wide obsolete")
                else:
                    pass
                # List SAQ
                if reference in dico_ig_tbl_saq:
                    p_saq = ET.SubElement(li3, "ul",attrib={"class":"hidden","id":"{:s}".format(tag_saq)})
                    for saq in dico_ig_tbl_saq[reference]:
                        p = ET.SubElement(p_saq, "li",attrib={"class":"list_saq"})
                        version = dico_saq[saq]["Indice"]
                        description = dico_saq[saq]["Titre"]
                        link = dico_saq[saq]["Link"]
                        hyperlink = ET.SubElement(p, "a",attrib={"style":""})
                        hyperlink.text = "{:s} version {:s}: {:s}".format(saq,version,description)
                        hyperlink.set("href", link)

            elif re.match(r'X.X.X.XXX',reference):
                pass
                #print "Gestion des RT dans AGILE"
            elif re.match(r'ZA',type):
                if type != prev_type:
                    prev_type = type
                    li0 = ET.SubElement(ul_group, "li",attrib={"class":"group"})
                    hyperlink0 = ET.SubElement(li0, "a",attrib={"class":"short selected"})
                    hyperlink0.text = "Zodiac Aerospace"
                    tag = "subgroup_99"
                    hyperlink0.set("name",tag)
                    #hyperlink0.set("href","Notes:///C1257A3800343D8A/ZodFrame2?OpenFrameset")
                    hyperlink0.set("onClick","show_ig('{:s}')".format(tag))
                    ul1 = ET.SubElement(li0, "ul",attrib={"class":"hidden","id":tag})
                    #ul2 = ET.SubElement(li0, "ul")
                    li1 = ET.SubElement(ul1, "li",attrib={"class":"sub_group"})
                    tag = "artic_99"
                    hyperlink1 = ET.SubElement(li1, "a",attrib={"class":"short"})
                    hyperlink1.text = "Procedures"
                    hyperlink1.set("href","#"+tag)
                    hyperlink1.set("name",tag)
                    hyperlink1.set("onClick","show_ig('{:s}')".format(tag))
                    ul3 = ET.SubElement(li1, "ul",attrib={"class":"hidden","id":tag})
                    li2 = ET.SubElement(ul3, "li",attrib={"class":"articulation"})
                    hyperlink2 = ET.SubElement(li2, "a",attrib={"class":"short"})
                    ul4 = ET.SubElement(li2, "ul")
                    hyperlink2.text = "Procedures"
                li3 = ET.SubElement(ul4, "li")
                hyperlink = ET.SubElement(li3, "a",attrib={"class":"wide"})
                hyperlink.text ="{:s} {:s} version {:s}: {:s}".format(type,reference,version,title)
                hyperlink.set("href", link)
                if color_flag % 2:
                    li3.set("class","dark")
                else:
                    li3.set("class","light")
                #print reference
            elif re.match(r'ZS',type):
                if type != prev_type:
                    prev_type = type
                    li0 = ET.SubElement(ul_group, "li",attrib={"class":"group"})
                    hyperlink0 = ET.SubElement(li0, "a",attrib={"class":"short selected"})
                    hyperlink0.text = "Zodiac Service"
                    tag = "subgroup_100"
                    hyperlink0.set("name",tag)
                    hyperlink0.set("href","#"+tag)
                    hyperlink0.set("onClick","show_ig('{:s}')".format(tag))
                    ul1 = ET.SubElement(li0, "ul",attrib={"class":"hidden","id":tag})
                    #ul2 = ET.SubElement(li0, "ul")
                    li1 = ET.SubElement(ul1, "li",attrib={"class":"sub_group"})
                    tag = "artic_100"
                    hyperlink1 = ET.SubElement(li1, "a",attrib={"class":"short"})
                    hyperlink1.text = "Procedures"
                    hyperlink1.set("href","#"+tag)
                    hyperlink1.set("name",tag)
                    hyperlink1.set("onClick","show_ig('{:s}')".format(tag))
                    ul3 = ET.SubElement(li1, "ul",attrib={"class":"hidden","id":tag})
                    li2 = ET.SubElement(ul3, "li",attrib={"class":"articulation"})
                    hyperlink2 = ET.SubElement(li2, "a",attrib={"class":"short"})
                    ul4 = ET.SubElement(li2, "ul")
                    hyperlink2.text = "Procedures"
                li3 = ET.SubElement(ul4, "li")
                hyperlink = ET.SubElement(li3, "a",attrib={"class":"wide"})
                hyperlink.text ="{:s} {:s} version {:s}: {:s}".format(type,reference,version,title)
                hyperlink.set("href", link)
                if color_flag % 2:
                    li3.set("class","dark")
                else:
                    li3.set("class","light")
                #print reference
            else:
                p = ET.SubElement(div_accordion, "p")
                hyperlink = ET.SubElement(p, "a")
                hyperlink.text ="{:s} {:s}: {:s}".format(type,reference,title)
                hyperlink.set("href", link)
        # Software
        div_software_c = ET.SubElement(div_square, "div",attrib={"id":"software_c"})
        #img = ET.SubElement(div_software_c, "img",attrib={"style":"float:right;margin:25px","src":"img/SW.png"})
        parser.createListIG(div_software_c,"Software")
        txt = 'Les procédures logiciels ne sont plus applicables pour les nouveaux projets.\nElles restent applicables pour les programmes A350, Legacy 450/550 etc.\n' \
              'Les standards à appliquer pour les nouveaux programmes (F5X, G7000, MC21 etc.) sont\n- SCS_SW_STANDARD_ET3159\n- SDTS_SW_STANDARD_ET3158\n- SRTS_SW_STANDARD_ET3157.' \
              '\nIl sont accessibles dans la base de donnée Synergy db_tools:\nhttp://spar-syner1.in.com:8602'
        div_warning = parser.createWarning(div_software_c,txt)
        h = ET.SubElement(div_warning, "h2")
        h.text = "Les standards:"
        div = parser.createParagraph(div_warning,"",attrib={"style":"margin:5px 0px 0px 10px"})
        a = ET.SubElement(div, "a",attrib={"href":"doc/SRTS_SW_STANDARD_ET3157-1.5.pdf"})
        a.text = "SRTS software standard issue 1.5"
        a = ET.SubElement(div, "a",attrib={"href":"doc/SDTS_SW_STANDARD_ET3158-1.8.pdf"})
        a.text = "SDTS software standard issue 1.8"
        a = ET.SubElement(div, "a",attrib={"href":"doc/SCS_SW_STANDARD_ET3159-1.12.pdf"})
        a.text = "SCS software standard issue 1.12"
        h = ET.SubElement(div_warning, "h2")
        h.text = "Les plans F5X:"
        div = parser.createParagraph(div_warning,"",attrib={"style":"margin:5px 0px 0px 10px"})
        a = ET.SubElement(div, "a",attrib={"href":"doc/SDP_SW_PLAN_ET3132-1.9.pdf"})
        a.text = "SDP software development plan issue 1.9"
        a = ET.SubElement(div, "a",attrib={"href":"doc/SVP_SW_PLAN_ET3133-2.0.pdf"})
        a.text = "SVP software verification plan issue 2.0"
        a = ET.SubElement(div, "a",attrib={"href":"doc/SCMP_SW_PLAN_ET3134-2.0.pdf"})
        a.text = "SCMP software configuration management plan issue 2.0"
        a = ET.SubElement(div, "a",attrib={"href":"doc/SQAP_SW_PLAN_PQ 0.1.0.155-2.0.pdf"})
        a.text = "SQAP software quality asurance plan issue 2.0"
        # FPGA
        div_fpga_c = ET.SubElement(div_square, "div",attrib={"id":"fpga_c"})
        #img = ET.SubElement(div_fpga_c, "img",attrib={"style":"float:right;margin:25px","src":"img/fpga.png"})
        parser.createListIG(div_fpga_c,"FPGA")

        # Hardware
        div_hardware_c = ET.SubElement(div_square, "div",attrib={"id":"hardware_c"})
        #img = ET.SubElement(div_hardware_c, "img",attrib={"style":"float:right;margin:25px","src":"img/HW.png"})
        parser.createListIG(div_hardware_c,"Hardware")

        # Bench
        div_bench_c = ET.SubElement(div_square, "div",attrib={"id":"bench_c"})
        parser.createListIG(div_bench_c,"Bench")

        # Agile
        div_agile_c = ET.SubElement(div_square, "div",attrib={"id":"agile_c"})
        parser.createListIG(div_agile_c,"Agile")

        # Change
        div_change_c = ET.SubElement(div_square, "div",attrib={"id":"change_c"})
        #img_cr_workflow = ET.SubElement(div_change_c, "img",attrib={"style":"float:right","src":"img/cr_workflow.gif"})
        parser.createListIG(div_change_c,"Configuration")
        div_clearer = ET.SubElement(div_change_c, "div",attrib={"class":"clearer"})
        txt = "IBM Rational Change est accessible à l'adresse suivante:\nhttp://spar-syner1.in.com:8600/change"
        parser.createWarning(div_change_c,txt)

        # Certification
        div_cert_c = ET.SubElement(div_square, "div",attrib={"id":"certification_c"})
        parser.createListCert(div_cert_c,"Certification")
        txt = "Des errata sur la DO-330 ont été publié ici:\nhttp://acg-solutions.fr/acg/do330ed-215-errors/"
        parser.createWarning(div_cert_c,txt)
        # New
        div_new_c = ET.SubElement(div_square, "div",attrib={"id":"new_c"})
        parser.createListIG(div_new_c,"New")

        # A propos
        url_za = "Notes:///C1257A3800343D8A/ZodFrame2?OpenFrameset"
        url_intranet = "http://intranet-ece.in.com/dq/documentation/procedures_zodiac_aero_electric"
        div_apropos_c = ET.SubElement(div_square, "div",attrib={"id":"apropos_c","style":"padding:10px"})
        #img= ET.SubElement(div_apropos_c, "img",attrib={"style":"float:left;margin:10px","src":"img/training_small.gif"})
        parser.createParagraph(div_apropos_c,"Ce logiciel récupère les données concernant les procédures dans la page intranet:")
        a = ET.SubElement(div_apropos_c, "a",attrib={"href":url_intranet})
        a.text = url_intranet
        parser.createParagraph(div_apropos_c,"et classifie les procédures conformément à la procédure IG 0.4.0.001")
        parser.createParagraph(div_apropos_c,"De plus une base de donnée additionnelle SQLite permet de classifier suivant les thèmes:")
        parser.createParagraph(div_apropos_c,"Logiciel, FPGA, Hardware Agile, Bancs de test, etc.")
        parser.createParagraph(div_apropos_c,"L'onglet New affiche les procédures nouvellement publiées et sont triées par date par ordre décroissant.")
        parser.createParagraph(div_apropos_c,"Les procédures Zodiac Aerospace sont dorénavant accessibles ici:")
        a = ET.SubElement(div_apropos_c, "a",attrib={"href":url_za})
        a.text = url_za
        parser.createParagraph(div_apropos_c,"Fonctionne complètement avec Firefox et Chrome et partiellement avec Internet Explorer")
        parser.createParagraph(div_apropos_c,"Le couleurs des lignes ont la signification suivante:")
        ul = ET.SubElement(div_apropos_c, "ul")
        li = ET.SubElement(ul, "li",attrib={"class":"obsolete","style":"width:500px"})
        li.text = parser.encode_for_xml("Gris foncé: Procédures obsolètes pour les nouveaux projets")
        li = ET.SubElement(ul, "li",attrib={"class":"top_ig","style":"width:500px"})
        li.text = parser.encode_for_xml("Bleu: Procédure chapeau")
        li = ET.SubElement(ul, "li",attrib={"class":"obsolete_and_header","style":"width:500px"})
        li.text = parser.encode_for_xml("Orange: Procédure chapeau mais obsolète")
        # Generation
        date = datetime.now().strftime('%d/%m/%Y')
        heure = datetime.now().strftime('%H:%M:%S')
        div_info_gen = ET.SubElement(body, "div",attrib={"style":"margin-left: 20px"})
        div_info_gen.text = parser.encode_for_xml("Page generée par easyIG version {:s} le {:s} à {:s}".format(__version__,date,heure))
        div_footer = ET.SubElement(body, "div",attrib={"id":"piedpage"})
        span = ET.SubElement(div_footer, "span",attrib={"class":"copyright"})
        span.text = "Copyright &copy; 2014 All Rights Reserved"
        script_page_tab = ET.SubElement(body, "script",attrib={"type":"text/javascript"})
        script_page_tab.text = "cms_page_tab_style();"

        tree = ET.ElementTree(racine)
        filename ="easyIG.html"
        with open(filename, 'w') as html_handler:
            # HTML 4.1
            html_handler.write("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd\">\n")
            # HTML 5
            # <!doctype html>
        tree.write(filename,method="html")

if __name__ == '__main__':
    easyig = easyIG()
    easyig.start()
