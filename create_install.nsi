;--------------------------------
;Header Files

!include "MUI2.nsh"
!include "Sections.nsh"
!include "LogicLib.nsh"
!include "Memento.nsh"
!include "WordFunc.nsh"
;!include "Image.nsh"

;Interface Settings
!define MUI_ICON "ico_sys_desktop.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "essai2.bmp"
!define MUI_HEADERIMAGE_RIGHT

Name "doCID"
LoadLanguageFile "C:\Program Files (x86)\NSIS\Contrib\Language Files\French.nlf"
OutFile "docid_installer.exe"
InstallDir "C:\Program Files (x86)\docid"

PageEx directory
  DirVar $INSTDIR
PageExEnd
Page instfiles
Section "Install"
;!insertmacro DisplayImage 'Image.bmp'
SetOutPath $INSTDIR
SetShellVarContext current
; C:\Users\olivier.appere\AppData\Roaming\Microsoft\Windows\Start Menu\Programs
createDirectory $SMPROGRAMS\doCID
createShortCut $SMPROGRAMS\doCID\doCID.lnk $INSTDIR\docid.exe
;SetShellVarContext All
;CreateDirectory $SMPROGRAMS\doCID
;CreateShortcut "$SMPROGRAMS\doCID\All users doCID.lnk" $INSTDIR\docid.exe
		
IfFileExists $INSTDIR\conf\docid.ini DOCID_INI_EXISTS  DOCID_INI_NOT_EXISTS
DOCID_INI_EXISTS:
    MessageBox MB_OK "Previous version of docid.ini found. Keep it."
    File /r /x docid_empty.ini /x docid.ini /x *.pyc /x *.py dist\conf
	${If} ${Cmd} `MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Overwrite previous configuration files ?" IDYES`
		File /r dist\db
		File /r dist\template
		; database
		File dist\docid.db3
		File dist\ig.db3	
	${EndIf}	
	Goto NEXT
DOCID_INI_NOT_EXISTS:
    File /r /x docid_empty.ini /x *.pyc /x *.py dist\conf
	File /r dist\db
	File /r dist\template
	; database
	File dist\docid.db3
	File dist\ig.db3	
NEXT:
File /r dist\img
File /r dist\js
File /r dist\css

File /r dist\Microsoft.VC90.CRT
File /r dist\tcl
; TCL
;File /r dist\tcl\tcl8.5\http1.0
;createDirectory $INSTDIR\tcl
;createDirectory $INSTDIR\tcl\tcl8.5
;createDirectory $INSTDIR\tcl\tcl8.5\tzdata
;createDirectory $INSTDIR\tcl\tk8.5
;createDirectory $INSTDIR\tcl\tk8.5\msgs

;File /oname=tcl\tcl8.5\encoding\ascii.enc dist\tcl\tcl8.5\encoding\ascii.enc
;File /oname=tcl\tcl8.5\encoding\iso8859-1.enc dist\tcl\tcl8.5\encoding\iso8859-1.enc
;File /oname=tcl\tcl8.5\tclIndex dist\tcl\tcl8.5\tclIndex
; TK
;File /oname=tcl\tk8.5\ttk /r dist\tcl\tk8.5\ttk
;File /oname=tcl\tk8.5\tclIndex \dist\tcl\tk8.5\tclIndex
;File /oname=tcl\tk8.5\msgs\en.msg dist\tcl\tk8.5\msgs\en.msg
;File /oname=tcl\tk8.5\msgs\fr.msg dist\tcl\tk8.5\msgs\fr.msg

File /r dist\template
File /r /x *.docx /x *.xlsx /x *.csv dist\result
File /r /x *.db3 dist\actions

; dll
File dist\QtCore4.dll
File dist\QtGui4.dll
File dist\freetype6.dll
File dist\intl.dll
File dist\libcairo-2.dll
File dist\libexpat-1.dll
File dist\libfontconfig-1.dll
File dist\libglib-2.0-0.dll
;File dist\libgobject-2.0-0.dll
File dist\libgthread-2.0-0.dll
File dist\libpng14-14.dll
File dist\python27.dll
File dist\pythoncom27.dll
File dist\pywintypes27.dll
File dist\sqlite3.dll
File dist\tcl85.dll
File dist\tk85.dll
File dist\wxbase294u_net_vc90.dll
File dist\wxbase294u_vc90.dll
File dist\wxmsw294u_adv_vc90.dll
File dist\wxmsw294u_core_vc90.dll
File dist\wxmsw294u_html_vc90.dll
File dist\zlib1.dll
; exe
; Main executable
File dist\docid.exe
; This program is used by Python's os.popen function to work around a limitation in Windows 95/98
;File dist\w9xpopen.exe

File dist\ico_sys_desktop.ico
; pyd
File dist\PIL._imagingft.pyd
File dist\PIL._imaging.pyd
File dist\PyQt4.QtGui.pyd
File dist\_ctypes.pyd
File dist\_elementtree.pyd
File dist\_hashlib.pyd
File dist\_imaging.pyd
File dist\_socket.pyd
File dist\_sqlite3.pyd
File dist\_ssl.pyd
File dist\_tkinter.pyd
File dist\bz2.pyd
File dist\cairo._cairo.pyd
File dist\glib._glib.pyd
File dist\gobject._gobject.pyd
File dist\lxml.etree.pyd
File dist\lxml.objectify.pyd
File dist\matplotlib._cntr.pyd
File dist\matplotlib._delaunay.pyd
File dist\matplotlib._image.pyd
File dist\matplotlib._path.pyd
File dist\matplotlib._png.pyd
File dist\matplotlib._tri.pyd
File dist\matplotlib.backends._backend_agg.pyd
File dist\matplotlib.ft2font.pyd
File dist\matplotlib.nxutils.pyd
File dist\matplotlib.ttconv.pyd
File /r dist\mpl-data
File dist\numpy.core._sort.pyd
File dist\numpy.core.multiarray.pyd
File dist\numpy.core.scalarmath.pyd
File dist\numpy.core.umath.pyd
File dist\numpy.fft.fftpack_lite.pyd
File dist\numpy.lib._compiled_base.pyd
File dist\numpy.linalg.lapack_lite.pyd
File dist\numpy.random.mtrand.pyd
File dist\pyexpat.pyd
File dist\select.pyd
File dist\unicodedata.pyd
File dist\win32api.pyd
;File dist\win32evtlog.pyd
File dist\win32pdh.pyd
File dist\win32pipe.pyd
File dist\win32wnet.pyd
File dist\wx._controls_.pyd
File dist\wx._core_.pyd
File dist\wx._gdi_.pyd
File dist\wx._misc_.pyd
File dist\wx._windows_.pyd
; Documentation
File /r doc\_build\html
File /r /x _build /x source /x make.bat /x Makefile dist\doc
;File /nonfatal /oname=doc\air6110.pdf dist\doc\air6110.pdf 
;File /nonfatal /oname=doc\arp4754a.pdf dist\doc\arp4754a.pdf 
;File /nonfatal /oname=doc\cert_memo_ceh_1.pdf dist\doc\cert_memo_ceh_1.pdf 
;File /nonfatal /oname=doc\cert_memo_sw_1.pdf dist\doc\cert_memo_sw_1.pdf 
;File /nonfatal /oname=doc\do178b.pdf dist\doc\do178b.pdf 
;File /nonfatal /oname=doc\do178c.pdf dist\doc\do178c.pdf 
;File /nonfatal /oname=doc\do248.pdf dist\doc\do248.pdf 
;File /nonfatal /oname=doc\do254.pdf dist\doc\do254.pdf 
;File /nonfatal /oname=doc\do330.pdf dist\doc\do330.pdf 
;File /nonfatal /oname=doc\PSAC_SW_PLAN_PDS_SDS_ET3131.pdf dist\doc\PSAC_SW_PLAN_PDS_SDS_ET3131.pdf 
;File /nonfatal /oname=doc\SCMP_SW_PLAN_ET3134-2.0.pdf dist\doc\SCMP_SW_PLAN_ET3134-2.0.pdf 
;File /nonfatal /oname=doc\SCS_SW_STANDARD_ET3159-1.12.pdf dist\doc\SCS_SW_STANDARD_ET3159-1.12.pdf 
;File /nonfatal /oname=doc\SDP_SW_PLAN_ET3132-1.9.pdf dist\doc\SDP_SW_PLAN_ET3132-1.9.pdf 
;File /nonfatal /oname=doc\SDTS_SW_STANDARD_ET3158-1.8.pdf dist\doc\SDTS_SW_STANDARD_ET3158-1.8.pdf 
;File /nonfatal /oname=doc\SQAP_SW_PLAN_PQ_0.1.0.155-2.0.pdf dist\doc\SQAP_SW_PLAN_PQ_0.1.0.155-2.0.pdf 
;File /nonfatal /oname=doc\SRTS_SW_STANDARD_ET3157-1.5.pdf dist\doc\SRTS_SW_STANDARD_ET3157-1.5.pdf 
;File /nonfatal /oname=doc\SVP_SW_PLAN_ET3133-2.0.pdf dist\doc\SVP_SW_PLAN_ET3133-2.0.pdf 
; ??
File dist\explain.txt
SectionEnd