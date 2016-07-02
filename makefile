#
# Makefile to generate docid.exe
#
# Attention: La commande $(shell [ -f <filename>]) ne fonctionne pas
#
# Author: Olivier Appere
# Date: 07th of July 2014
#
ifndef VERSION
VERSION=3_9_2
endif
	
DIST = dist
GUI_EXE = docid.exe
GUI_BACKUP_EXE = docid_backup.exe
CLI_EXE = docid_cli.exe
MARKDOWN = lib/markdown2.py
MAKE = make
#
# Configuration:
#
PYTHON = python
MAKENSIS = makensis.exe
ZIP2EXE = Contrib\zip2exe
OUTPUT = 
WEBSERVER = C:\xampplite\htdocs\qams\docid
#WORKAREA = C:\Documents\ and\ Settings\appereo1\Mes%20documents\Synergy\ccm_wa\db_sms_pds\TOOLS_QA-dev_appere\TOOLS_QA\doCID
#WORKAREA = C:\DOCUME~1\appereo1\Mes*\Synergy\ccm_wa\db_sms_pds\TOOLS_QA-dev_appere\TOOLS_QA\doCID
WORKAREA = C:\synergy_workarea\db_sms_pds\TOOLS_QA-dev_appere\TOOLS_QA\doCID
#QUALITY = M:\02%20-%20Qualit%E9%20d%E9veloppement\Appere\doCID
#QUALITY = M:\"02 - Qualit? d?veloppement"\Appere\doCID
#QUALITY = M:\02-QUA~1\Appere\doCID
QUALITY = M:\doCID.lnk
DOCID_DIR = C:\Python\Project\docid
# Sphynx
BUILDDIR=_build
SPHINXOPTS =
ALLSPHINXOPTS=-d $(BUILDDIR)/doctrees

#
# The project to be built
#
quick: nsis
	@$(PATHNSIS)$(MAKENSIS) create_install.nsi
	@mv docid_installer.exe doCID_v$(VERSION)_install.exe
	@cp doCID_v$(VERSION)_install.exe $(WEBSERVER)\download
	@cp doCID_v$(VERSION)_install.exe $(WORKAREA)
	
default: nsis copy_docs copy copy_wrk_area

install: copy_docs copy copy_wrk_area

gui:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            doCID windows mode executable generation ...             º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@$(PYTHON) setup.py py2exe
	@rm -f -r -v $(DIST)/result/*.*
	@touch $(DIST)/result/empty.txt
	@rm -f -r -v $(DIST)/actions/*.*
	@touch $(DIST)/actions/actions.txt	
	@cp conf/docid_empty.ini $(DIST)/conf/docid.ini
	
cli:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            doCID console mode executable generation ...             º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@mv $(DIST)/$(GUI_EXE) $(DIST)/$(GUI_BACKUP_EXE)
	@$(PYTHON) setup_dos.py py2exe
	@mv $(DIST)/$(GUI_EXE) $(DIST)/$(CLI_EXE)
	@mv $(DIST)/$(GUI_BACKUP_EXE) $(DIST)/$(GUI_EXE)
	
docs:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            doCID documentation generation ...                       º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	cd doc && $(PYTHON) -m sphinx.__init__ source -c source -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html

copy_html:
	xcopy doc\_build\html $(WEBSERVER)
	xcopy doc\_build\html\_images $(WEBSERVER)\_images
	
copy_docs: docs
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º           doCID documentation copy on web server ...                º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	xcopy doc\_build\html $(WEBSERVER)
	xcopy doc\_build\html\_images $(WEBSERVER)\_images
	
# $(MAKE) -f Makefile html -C doc
	
nsis: gui
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            doCID installer generation ...                           º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@$(PATHNSIS)$(MAKENSIS) create_install.nsi
	
copy:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º           Copy doCID binary on webserver ...                        º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@mv docid_installer.exe doCID_v$(VERSION)_install.exe
	@cp doCID_v$(VERSION)_install.exe $(WEBSERVER)\download
	
copy_quality_area:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º           Copy doCID binary on Quality area ...                     º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	cp $(DOCID_DIR)\doCID_v$(VERSION)_install.exe $(QUALITY)
	
copy_wrk_area:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            Copy doCID binary on Synergy workarea ...                º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@cp doCID_v$(VERSION)_install.exe $(WORKAREA)
	
all: gui cli doc

easyig:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            easyIG windows mode executable generation ...            º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@$(PYTHON) setup_easyig.py py2exe
	
easyig_nsis: easyig
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º             easyIG installer generation ...                         º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@$(PATHNSIS)$(MAKENSIS) create_install_easyig.nsi

#
# This part convert markdown document readme.md into html document readme.html
#

# Implicit rules
.SUFFIXES: .html .md
.md.html:
	$(PYTHON) $(MARKDOWN) $< > $@

readme: readme.html
target: $(MD).html
#
# Launch tests
#
test:
	@echo ---------------------
	@echo |  Test _getItems   | 
	@echo ---------------------
	$(DIST)\$(CLI_EXE) --cli -system Dassault_F5X_PDS -item "ESSNESS" -release SW_ENM/02 -baseline SW_ENM_DELIV_02_01 -cr_type SW_ENM
	@echo ---------------------
	@echo |  Test _getCR      | 
	@echo ---------------------
	$(DIST)\$(CLI_EXE) --cli -system Dassault_F5X_PDS -item "ESSNESS" -release SW_ENM/02 -cr_type SW_ENM
clean:
	@rm doCID_v$(VERSION)_install.exe
	@rm -fr *.pyc *.log
	@rm -f -r -v $(DIST)/result/*.*
	@rm -f -v $(DIST)/*.exe
	@rm -f -v $(DIST)/*.py
	@rm -f -v $(DIST)/*.pyd
	@rm -f -v $(DIST)/*.html
	@rm -f -v $(DIST)/*.db3
	@rm -f -v $(DIST)/*.ico
	@rm -f -v $(DIST)/*.txt
	@rm -f -v $(DIST)/*.log
	@touch $(DIST)/result/empty.txt
