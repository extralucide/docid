**doCID** allows project manager to:

- Generate configuration index documents in openXML format like
    SCI,HCMR PLD, HCMR board and ECMR documents based on *IBM Rational Synergy* and *Change* database

- Generate CCB minutes report based on Change database in openXML format
	Change Requests (CR) to deal with are chosen among a list of CRs resulting from a query according to attributes like:
		* detected on (ex: SW_ENM/03)
		* implemented for (ex: SW_ENM/04)
		* CR type (ex: SW_ENM)
		
	Table is created to list CRs with the following columns:
	
        * Domain: EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR
        * CR Type: ex SW_ENM
        * ID
        * Status: In_analysis, In_review, etc.
        * Synopsis
        * Severity: Blocking, Major, Minor, etc.
        * Detected on: ex SW_ENM/03
        * Implemented for: ex SW_ENM/04
        * Parent CR: ID | Domain | Type | synopsis | status

	Tables are created according to key CR transition (Reviewed/Postpone/Close)

- Export CR list in Excel files with the following column:

    * CR ID
    * Type: ex: EXCR|SyCR|ECR|SACR|HCR|SCR|BCR|PLDCR
    * Synopsis
    * Level
    * Status: 
    * Detected on: ex SW_ENM/03
    * Implemented in: ex SW_ENM/04
    * Implementation in baseline: ex SW_ENM_04_02
    * Modified time,
    * Impact analysis
    * Parent CR ID
    * Parent CR status
    * Parent CR synopsis
	

- Generate Review report based on both **Synergy** and **Change** database in openXML format
	Software Planning Review,
	Specification Requirement Review,
	etc.
	Checklist is stored in a SQLite database

- List tasks, objects in a specific baseline
- Export history of objects and more specifically source files
- Make a difference between 2 baselines

doCID also includes a Synergy easy Command Line Interface

User Configuration file docid.ini is located in "conf" directory:

Example
-------

[User]
login=mon_nom
password=mon_mot_de_passe
author=O. Appere

[Default]
; option start is used to start automatically the doCID GUI without entering the login GUI.
; set "auto" to start automatically or anything else to enter login GUI
start=auto
system=Dassault F5X PDS
item=ESSNESS

; Filter to display data.
[Objects]
type_doc=doc,xls,pdf
sw_src=csrc,asmsrc,incl,macro_c,library
sw_prog=shsrc,makefile,executable,ascii
hw_src=ascii

; Information related to docx template to be used for document generation
[Template]
; CID templates
SCI=SCI_F5X_ENM_template.docx
HCMR_PLD=HCMR_PLD_template.docx
HCMR_BOARD=HCMR_BOARD_template.docx
ECMR=ECMR_template.docx
CID=ECMR_template.docx

; CCB templates
CCB=CCB_Minutes_SW_ENM_template.docx
CCB_PLD=CCB_Minutes_HW_PLD_template.docx

; Template for reviews report
SCR=REV_SCR_SW_template.docx
; Template for audit report
AUD_SWRD=AUD_SWRD_SW_template.docx

; Template for delivery sheets
SDS=SDS_template.docx

; Template for Inspection Sheets export and check report
IS_EXPORT=IS_SwRD-1.4_clean.xlsx
IS_CHECK=is_check_report.xlsx

[Generation]
dir=result
plans=PLAN
input_data=INTPUT_DATA,INPUT_DATA,Input_Data,Input Data
peer_reviews=REVIEWS,Reviews
; Filter project with VHDL in the name of the project
sources=VHDL,SRC
verification=VTPR,HWVPR,ATP
; Discard all files included in these following folders
exclude=ENMTools,Reqtify
; to add description for documents in CID
description_docs=descr_docs.csv
glossary=glossary.csv
func_chg_filename=func_chg.txt
oper_chg_filename=oper_chg.txt

; Compatibility index
protocol_interface=SMS_EPDS_SPI_ICD_ET3532_S
data_interface=SMS_EPDS_ESSNESS_SPI_Annex_ET3547_S


; File of list of A/C standards and project standards and part numbers
; If no file is defined then listbox are not displayed on the GUI.
;[Standards]
;file=standards.csv

[Check]
system_spec=SDTS_WDS_ET2710_S
board_spec=SSCS_ESSNESS_ET2788_S
icd_spi_prot=SMS_EPDS_SPI_ICD_ET3532_S
icd_spi_data=SMS_EPDS_ESSNESS_SPI_Annex_ET3547_S
icd_can_prot=SMS_EPDS_CAN_ICD_GS3338
icd_can_data=SMS_EPDS_CAN_ICD_GS3338_Annex_B2
swrd=SWRD_ENM_ET3135_S
swdd=SwDD_ENM_ET3136_S
hsid=SMS_ESNESS_FUNC_HSID_ET2717_E

[Sheets]
icd_can=ListOfModifications,Applicable documents,DataUnitsExchanges,DataCoding,Message Identifiers,Synchro (50ms)
icd_spi=Evolution,Frame
is=CONTEXT,REVIEW,DOC REVIEW,REQ REVIEW,REQ ANALYSIS,UPPER REQ ANALYSIS,REMARKS
