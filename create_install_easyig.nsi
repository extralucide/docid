;--------------------------------
;Header Files

!include "MUI2.nsh"
!include "Sections.nsh"
!include "LogicLib.nsh"
!include "Memento.nsh"
!include "WordFunc.nsh"

;Interface Settings
!define MUI_ABORTWARNING

!define MUI_HEADERIMAGE
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\nsis.bmp"

!define MUI_COMPONENTSPAGE_SMALLDESC

Name "easyIG"
LoadLanguageFile "C:\Program Files\NSIS\Contrib\Language Files\French.nlf"
OutFile "easyig_installer.exe"
InstallDir "c:\program Files\easyig"

Section "Install"
SetOutPath $INSTDIR
File /r dist\img
File /r dist\css
File /r dist\js
File /r dist\doc
File /r dist\template
File /r dist\Microsoft.VC90.CRT

; database
File dist\ig.db3
; dll
File dist\python27.dll
File dist\pywintypes27.dll
File dist\sqlite3.dll
; exe
File dist\get_ig_jquery.exe

File dist\ico_sys_internet.ico
; pyd
File dist\_ctypes.pyd
File dist\_hashlib.pyd
File dist\_socket.pyd
File dist\_sqlite3.pyd
File dist\_ssl.pyd
File dist\bz2.pyd
File dist\lxml.etree.pyd
File dist\lxml.objectify.pyd
File dist\PIL._imaging.pyd
File dist\pyexpat.pyd
File dist\select.pyd
File dist\unicodedata.pyd
File dist\win32api.pyd
File dist\win32evtlog.pyd
File dist\win32pipe.pyd
File dist\win32wnet.pyd

SectionEnd