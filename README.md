doCID
-----
![Alt text][id]
[id]: img/SMS.jpg  "F5X aircraft"

Description
-----------
Generates Configuration Index Document and more from IBM Rational Synergy Version Management System tool

CID/HCMR/SCI generator
----------------------

Cet outil permet de g&eacute;n&eacute;rer un CID &agrave; partir de l'outil de gestion de version *IBM Rational Synergy*.
La g&eacute;n&eacute;ration s'appuie sur un mod&eagrave;le de document.

Installation
------------

Outre les fichiers:
> docid.py  
> docid.ini  

- le programme n&eacute;cessite la base de donn?e SQLite docid.db3 (Si elle n'existe pas le programme en cr&eacute;&eacute; une vierge.)  
- Le r&eacute;pertoire img qui contient les images:  
> doc.gif  
> earhart12_240x116.gif  

- le fichier icone qams.ico  
- Le module python-docx  
- Le r&eacute;pertoire template avec les fichiers au format open xml  

D&eacute;veloppement
-------------

Il est &eacute;crit en Python et est compatible avec la version 2.7.3.2.
Il utilise &eacute;galement:

- l'interface TCL/Tk,
- SQLite v3.x
- PMW version 1.3.3a (&agrave; installer dans les librairies de Python),
- Python-docx version 0.2 (copier le r&eacute;pertoire python-docx &agrave; la racine du projet dans le r&eacute;pertoire)

Pour g&eacuten&eacuterer l'ex?cutable il faut lancer la commande: python setup.py py2exe
Il faut de plus cr?er le r&eacutepertoire *Microsoft.VC90.CRT* avec les fichiers suivant:

- Microsoft.VC90.CRT.manifest
- msvcm90.dll
- msvcp90.dll
- msvcr90.dll

Fichier de configuration
------------------------
Le fichier de configuration docid.ini Contient les param&ecirc;tres suivant:
<pre>
[User]
login
password
author

[Synergy]
synergy_dir=C:\Program Files\IBM\Rational\Synergy\bin\
synergy_server=http://spar-syner1:8602

[Objects]
type_doc=doc,xls
type_src=csrc,asmsrc

[Template]
SCI=SCI_template.docx
HCI=HCI_template.docx
CID=CID_template.docx
SQAP=SQAP_template.docx
</pre>
Ce sont des informations utilisateurs.

Base de donn&eacute;es SQLite
----------------------

Le fichier synergy.db contient les tables suivantes:

* systems: liste les syst&egrave;mes
* items: liste les items
* link_systems_items: fait le lien entre items et syst?mes
* last_query: contient les 10 derni?res requ&ecirc;tes
Ce sont des informations projets.

Filtrage des donn&eacute;es dans Synergy
---------------------------------
D&eacute;finition extraite du guide "Rational Synergy Build Manager's Guide, Release 7.1"
_Release:_
>"A release enables you to mark projects, tasks, and folders for particular releases. It also helps you to
>keep track of which object versions were developed for each release."
>"When you create a new release, you can create it based on an existing release, and
>the new release inherits properties of that release automatically."

_Baseline:_
>"A baseline is an object (of type baseline) in the Synergy database which is related to various objects including
>tasks, project hierarchies etc which together represent a milestone in your development cycle."
>"A baseline is a set of projects and tasks used to represent your data at a specific
>point in time. A baseline has many uses. When you perform an update, Rational
>Synergy uses a baseline as a starting point to look for new changes."

A ne pas confondre avec

>"A baseline-project is a specific project object-version (of type project) which is in a static state.
>A working state project object may use a baseline-project as a start point for an update/reconfigure operation."

_Project:_
>"The database contains projects. A project is a user-defined group of related files, directories, and other projects.
>A project normally represents a logical grouping of software, such as a library or an executable, and
>it contains the directory structure of the files. Projects have version, like any other object."

Checklist model
---------------
*review\_checklists\_dispatch*

- sub_category: Standards / Project documents / Preliminary Safety Assessment etc.
- check_id: id de la table **review_checklists**
- category_id: id de la table **category_checklist**
- id: auto-increment
- rank: ordre d'apparatition dans le document produit
- review_id: id de la table **review_types**

*review\_checklists*

- level: niveau de conformit&eacute; du logiciel
- id: auto-increment
- name: check

*category\_checklist*

- id: auto-increment
- name:
<table>
    <tr><th>ID</th><th>Checks</th></tr>
    <tr><td>1</td><td>Input Items</td></tr>
    <tr><td>2</td><td>Development Activities</td></tr>
    <tr><td>3</td><td>Verification Activities</td></tr>
    <tr><td>4</td><td>Transition Criteria</td></tr>
    <tr><td>5</td><td>Change Control Activity</td></tr>
    <tr><td>6</td><td>Software Quality Assurance Activity</td></tr>	
</table>
	
*review\_types*

- id: auto-increment
- name: PR / SRR / SDR / SCOR etc.
- description: Software Plan Review / Software Requirement Review etc.
- objective:
- transition:
- conlusion:

Mod&egrave;le de document
------------------

Le mod&egrave;le de document doit &ecirc;tre au format docx peut contenir les tags suivant:
<pre>
{{SUBJECT}}             Titre dans l'ent&ecirc;te du document
{{TABLELISTMODIFS}}     Log des modifications gard? dans la base SQLite
{{CI_ID}                }Num?ro d'identification (A295, etc.)
{{REFERENCE}}           R&eacute;f&eacute;rence du document
{{ISSUE}}               Version du document
{{TITLE}}               Titre de la premi&egrave;re page
{{COMPONENT}}           Abbr&eacute;viation du composant (Logiciel, FPGA etc.)
{{ITEM}}                Abbr&eacute;viation de l'&eacute;quipement (LRU)
{{ITEM_DESCRIPTION}}    Description de l'&eacute;quipement
{{PROJECT}}             Nom du projet
{{RELEASE}}             Release Synergy
{{BASELINE}}            Baseline Synergy
{{WRITER}}              Auteur du document
{{DATE}}                Date de g?n?ration du document
{{TABLEITEMS}}          Liste des documents excel et word
{{TABLESOURCE}}         Liste des sources (type c,asm,h,vhd etc.)
{{TABLEPRS}}            Liste des PRs impl?ment?s dans la release
</pre>

HCMR carte
----------
{{DATABASE}}			Nomm de la base synergy (ex: db_sms_pds)
{{REFERENCE}}           R&eacute;f&eacute;rence du document
{{ISSUE}}               Version du document
{{TITLE}}               Contient le nom du syst&egrave;me (ex: Dassalt F5X PDS) suivi de l'abbr&eacute;viation de la carte (ex: ESSNESS) suivi de HCMR
{{ITEM}}                Abbr&eacute;viation de la carte
{{ITEM\_DESCRIPTION}}   Description de l'abbr&eacute;viation de la carte
{{TABLEPLAN}}			Liste des plans contenant les mots clef HMP\_ ou PHAC\_ au format Word ou PDF
{{TABLESAS}}			Liste des documents contenant les mots clef HAS\_ au format Word ou PDF
{{TABLECID}}			Liste des documents contenant les mots clef SCI\_ ou HCMR\_au format Word ou PDF
{{TABLEOPR}}			List des CRs ouverts
{{TABLECLOSEPRS}}		Liste des CR impl&eacute;ment&eacute;s ("Fixed","Closed")
{{BOARD_PART_NUNMBER}}	P/N de la carte
{{PREVIOUS_BASELINE}}	P/N de la version de carte pr&eacute;c&eacute;dente
{{MAIN\_BOARD\_PART_NUMBER}}	Pas impl&eacute;ment&eacute;
{{MEZA\_BOARD\_PART_NUMBER}}	Pas impl&eacute;ment&eacute;
{{TABLEPEERREVIEWS}}	Liste des fichiers de relectures contenant les mots clef PRR, IS FDL_ au format Word ou Excel
{{TABLEVERIF}}			Liste des documents dans le répertoire ATP
{{TABLECCB}}			Liste des compte-rendus de CCB contenant le mot-clef dans le nom dont la release asscoi&eacute; correspond au champs "CR_implemented_for"
{{TABLEINPUTDATA}}		Liste des documents contenu dans les répertoires INTPUT_DATA,INPUT_DATA,Input_Data ou Input Data
{{TABLEINPUTDATA}}		Liste des documents contenu dans les répertoires INTPUT_DATA,INPUT_DATA,Input_Data ou Input Data
{{TABLEITEMS}}			Liste de tous les autres documents pr&eacute;sents dans la baseline

See my [About](/about/) page for details.   

TODO
----

 get 10 times more traffic from [Google] [1] than from
[Yahoo] [2] or [MSN] [3].

  [1]: http://google.com/        "Google"
  [2]: http://search.yahoo.com/  "Yahoo Search"
  [3]: http://search.msn.com/    "MSN Search"
