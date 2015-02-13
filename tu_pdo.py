#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Olivier.Appere
#
# Created:     13/06/2014
# Copyright:   (c) Olivier.Appere 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#import MySQLdb
import sys
sys.path.append("PDO")
import pdo
from tool import Tool
from api_mysql import MySQL

def main():
    tool = MySQL()
##    tool._loadConfigMySQL()
    sql_opt = "-X -udocid finister -e \" SELECT * FROM actions LIMIT 0,1\" "
    output = tool.mysql_query(sql_opt,"MySQL test")
    print "MySQL test",output
##    sql_opt = " -u root root"
##    output = tool.mysql_query(sql_opt,"MySQL test")
##    print "MySQL test",output
##    sql_opt = "help"
##    output = tool.mysql_query(sql_opt,"MySQL help")
##    print "MySQL help",output
    #sql_opt = "-u docid finister"
    #output = tool.mysql_query(sql_opt,"MySQL test")
    #print "MySQL test",output
##    sql_opt = "-udocid"
##    output = tool.mysql_query(sql_opt,"MySQL init")
##    print "MySQL init",output
##    sql_opt = "use finister;"
##    output = tool.mysql_query(sql_opt,"Select database")
##    print "Select database",output
##    sql_query = "SELECT * FROM actions LIMIT 1,30;"
##    output = tool.mysql_query(sql_query,"Get QA actions")
##    print "Actions",output
    if 0==1:
        db=pdo.connect("Module=MySQLdb;User=root;Passwd=root;DB=finister")
        if db.active:
            strSelect="SELECT * FROM actions"
            rs=db.openRS(strSelect)
            while rs.next():
                print rs.fields['Description'].value

if __name__ == '__main__':
    main()
