#
# Makefile to generate docid.exe
#
# Attention: La commande $(shell [ -f <filename>]) ne fonctionne pas
#
# Author: Olivier Appere
# Date: 07th of July 2014
#
ifndef VERSION
VERSION=3_9_3
endif
	
DIST = dist
GUI_EXE = docid.exe
GUI_BACKUP_EXE = docid_backup.exe
CLI_EXE = docid_cli.exe
MARKDOWN = lib/markdown2.py
MAKE = make
CC=dcc
LD=dld
LFLAGS=-tPPCE200Z6NEN:simple -m30 -Xlink-time-lint -Xstop-on-warning
CFLAGS=-tPPCE200Z6NEN:simple -g -Xalign-functions=4 -Xforce-prototypes -Xlint -Xstop-on-warning -Xenum-is-best -Xsmall-data=0 -Xsmall-const=0 -Xno-common -Xdebug-local-cie -Xpass-source -Xkeep-assembly-file -Xnested-interrupts -Xpragma-section-last 
LIST_OBJ_TXT=list_obj.txt

#
# Configuration:
#
PYTHON = python
PYTHON_3 = C:\WinPython-64bit-3.4.4.2\python-3.4.4.amd64\python
PYTHON_34 = C:\Users\olivier.appere\Python34\python
PYTHON_35 = C:\Python35\python

PYINSTALLER = C:\WinPython-64bit-3.4.4.2\python-3.4.4.amd64\Scripts\pyinstaller
CX_FREEZE = C:\WinPython-64bit-3.4.4.2\python-3.4.4.amd64\Scripts\cxfreeze
CSCI_SRC = ../SRC
INCLUDE = $(CSCI_SRC)/INCLUDE
LINK_DIR = ../BUILD
#CSCI_DIR = $(sort $(dir $(wildcard $(CSCI_SRC)/*/ $(CSCI_SRC)/*/*/)))
#LIST_CSCI_SRC = $(sort $(dir $(wildcard $(CSCI_SRC)/*/*/*.c)))
#LIST_CSCI_SRC := $(shell find $(CSCI_SRC) -type d)
# Make does not offer a recursive wildcard function, so here's one:
rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))

# How to recursively find all files with the same name in a given folder
#ALL_INDEX_HTMLS := $(call rwildcard,foo/,index.html)

# How to recursively find all files that match a pattern
SRC := $(call rwildcard,$(CSCI_SRC)/,*.c)
OBJ= $(SRC:.c=.o)
OBJDIR = ../OBJ
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

stack_pyinstaller:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            stack windows mode executable generation ...             º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@$(PYINSTALLER) -onefile --windowed stack.py
	@rm -f -r -v $(DIST)/result/*.*
	@touch $(DIST)/result/empty.txt
	@cp conf/docid_empty.ini $(DIST)/conf/docid.ini
	
stack_cxfreeze:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            stack windows mode executable generation ...             º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@$(PYTHON_3) setup_cxfreeze.py build
	@rm -f -r -v $(DIST)/result/*.*
	@touch $(DIST)/result/empty.txt
	@cp conf/docid_empty.ini $(DIST)/conf/docid.ini
	
stack_py2exe:
	@echo ================================================
	@echo = stack windows mode executable generation ... =
	@echo ================================================
	@$(PYTHON_35) setup_dummy.py py2exe
	@rm -f -r -v $(DIST)/result/*.*
	@touch $(DIST)/result/empty.txt
	@cp conf/docid_empty.ini $(DIST)/conf/docid.ini

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

ig:
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º            showIG windows mode executable generation ...            º
	@echo ÈÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ¼
	@$(PYTHON) setup_easyig.py py2exe

ig_nsis: ig
	@echo ÉÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍ»
	@echo º             showIG installer generation ...                         º
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
tu:
	$(PYTHON) tutu.py > log.txt

stack:
	$(PYTHON) stack.py

list_obj:$(OBJ)
	@echo "Create list of objects"
	$(foreach obj,$^,$(file >>$(LIST_OBJ_TXT),$obj))
	
acenm: hello
 
hello: list_obj
	@echo "Link"
	$(LD) $(LFLAGS) -o $@.elf -@$(LIST_OBJ) $(LINK_DIR)\ACENM.ld -@O=hello.map
	
$(OBJDIR)%.o: %.c
	@echo "Compile"
	$(CC) $(CFLAGS) -I$(INCLUDE) -O -c $< -o $@ -DCHECKSUM_EXTERNAL_DEFINITION=0
	
clean_acenm:
	@echo "Clean objects"
	@$(foreach obj,$(OBJ),rm -rf $(obj);)
	
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
