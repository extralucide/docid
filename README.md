docid
-----

generate document from IBM Rational Synergy Configuration Management tool

CID/HCMR/SCI generator
---------------------

Cet outil permet de générer un CID à partir de l'outil de gestion de configuration Synergy.
La génération s'appuie sur un modèle de document.

Installation
-------------

Outre les fichiers
- docid.py
- docid.ini

le programme nécessite la base de donnée SQLite: 
- synergy.db
Le répertoire img qui contient les images
- doc.gif
- earhart12_240x116.gif
Le module python-docx
Le répertoire template avec les fichiers au format open xml

Développement
-------------

Il est écrit en Python et est compatible avec la version 2.7.3.2.
Il utilise également:
 - l'interface TCL/Tk,
 - SQLite
 - PMW version 1.3.3a (à installer dans les librairies de Python),
 - Python-docx version 0.2 (copier le répertoire python-docx à la racine du projet dans le répertoire)

Pour généer l'exécutable il faut lancer la commande: python setup.py py2exe
Il faut de plus créer le répertoire Microsoft.VC90.CRT avec mles fichiers suivant:
 - Microsoft.VC90.CRT.manifest
 - msvcm90.dll
 - msvcp90.dll
 - msvcr90.dll

Fichier de configuration
------------------------
Le fichier de configuration docid.ini Contient les paramètres suivant:
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
name=HCMR_template.docx
type=HCMR/SCI/CID

sqap=SQAP_template.docx

Ce sont des informations utilisateurs.

Base de données SQLite
----------------------

Le fichier synergy.db contient les tables suivantes:
  	- systems: liste les systèmes
	- items: liste les items
	- link_systems_items: fait le lien entre items et systèmes
	- last_query: contient les 10 dernières requêtes
Ce sont des informations projets.

Filtrage des données dans Synergy
---------------------------------
Définition extraite du guide "Rational Synergy Build Managers Guide, Release 7.1"
Release:
"A release enables you to mark projects, tasks, and folders for particular releases. It also helps you to
keep track of which object versions were developed for each release."
"When you create a new release, you can create it based on an existing release, and
the new release inherits properties of that release automatically."

Baseline:
"A baseline is an object (of type baseline) in the Synergy database which is related to various objects including
tasks, project hierarchies etc which together represent a milestone in your development cycle."
"A baseline is a set of projects and tasks used to represent your data at a specific
point in time. A baseline has many uses. When you perform an update, Rational
Synergy uses a baseline as a starting point to look for new changes."

A ne pas confondre avec

"A baseline-project is a specific project object-version (of type project) which is in a static state.
A working state project object may use a baseline-project as a start point for an update/reconfigure operation."

Project:
"The database contains projects. A project is a user-defined group of related files, directories, and other projects.
A project normally represents a logical grouping of software, such as a library or an executable, and
it contains the directory structure of the files. Projects have version, like any other object."

Modèle de document
------------------

Le modèle de document doit être au format docx peut contenir les tags suivant:

{{SUBJECT}}		Titre dans l'entête du document

{{CI_ID}}Numéro d'identification (A295, etc.)

{{REFERENCE}}Référence du document

{{ISSUE}}		Version du document

{{TITLE}}		Titre de la première page

{{ITEM}}		Abbréviation de l'équipement (LRU)

{{ITEM_DESCRIPTION}}	Description de l'équipement

{{PROJECT}}		Nom du projet

{{RELEASE}}		Release Synergy

{{BASELINE}}		Baseline Synergy

{{WRITER}}		Auteur du document

{{DATE}}		Date de génération du document

{{TABLEITEMS}}		Liste des documents excel et word

{{TABLESOURCE}}		Liste des sources (type c,asm,h,vhd etc.)

{{TABLEPRS}}		Liste des PRs implémentés dans la release


TODO
----
- remplacer l'interface TK par pyGTK qui offre plus de possibilités
- intégrer un générateur de checklist, de compte rendu de CCB (utiliser des onglets)
- modificer le pointeur de la souris lorsqu'il passe sur un hyperlien
- implémenter la table des fichier de sortie de génération du logiciel avec les types ascii et binary
- récupérer le nom de la database associée à la session
- Ajouter Group (PMW)
- Remplacer les combobox

