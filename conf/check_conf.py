#!/usr/bin/env python 2.7.3
# # -*- coding: latin-1 -*-
# -*- coding: utf-8 -*-
class Conf():
    active_dbg = True
    # TODO: Rendre parametrable dans docid.ini
    list_req_id = ("REQ_Id","Req Id")
    dico_types = {"SWRD":("body","issue","refer","status","derived","rationale","terminal","safety","additional","end"),
                  "SWDD":("body","issue","refer","status","derived","rationale","terminal","safety","additional","end","constraint"),
                "SHLVCP":("body","issue","verify","status","forward","rationale","additional","end"),
                  "IRD":(),
                  "HSID":("body","issue","refer","status","derived","rationale","terminal","additional","end")
                }
    dico_styles = {"REQ_Body":"body",
                        "REQ_Issue":"issue",
                        "REQ_Refers to":"refer",  # Attention sur F5X REQ_Refers to
                        "REQ_Constrained by":"constraint",
                        "REQ_Status":"status",
                        "REQ_Derived":"derived",
                        "REQ_Rationale":"rationale",
                        "REQ_Terminal":"terminal",
                        "REQ_Safety":"safety",
                        "REQ_Verifies":"verify",
                        "REQ_Forwarded":"forward",
                        "REQ_Additional_information":"additional",
                        "REQ_End":"end"}
    dico_attributes = {"body":"",
                "issue":"Issue:",
                 "status":"Status:",
                 "refer":"Refers to:",
                 # Constraint by, Constrained by
                 "constraint":"Constrain\w* by:",
                 "derived":"Derived:",
                 "terminal":("Terminal:","Stop Req:"),
                 "rationale":"Rationale:",
                 "safety":"Safety:",
                 "additional":"Additional [i|I]nfo\w*:",
                "req_id":("SWRD_","SWDD_","SHLVCP_","HSID_","PLD[R|D]D_"),
                 "end":("\[End [R|r]equirement\]","\[End Test Case\]"),
                 # Attributes not used in software specification document
                 "allocation":"Allocation:",
                 "conformity":"Conformity:",
                 "verification":"Verification Means?:",
                 "compliance":"Mean Of Compliance:",
                 "justification":"Justification Type:",
                 "assumption":"Assumption:",
                 "problem":"Problem Report:",
                 # For PLD
                 "refined":"Refined:",
                 "source_code":"File name:",
                 # For SHLVCP
                 "verify":"Verifies:",
                 "forward":"Forwarded:"
                 }

    tbl_list_of_modif = [("issue","(([0-9])\.([0-9]{1,2}))"),
                          ("date","(([0-9]{2})\/([0-9]{4}))"),
                          ("author","([A-Za-z \.]*)"),
                          ("modif","(.*)")]
    dico_specifications = {"PLDRD":{"modifications":"LIST OF MODIFICATIONS",
                                   "toc":"TABLE OF CONTENTS",
                                   "requirement":"ARCHITECTURAL FUNCTIONS",
                                   "derived":"YES"},
                           "SWDD":{"modifications":"Purpose of Modification",
                                   "toc":"Table of content",
                                   "requirement":"LOW LEVEL REQUIREMENTS",
                                   "derived":"YES"},
                           "SHLVCP":{"forward":"YES"},
                           "SWRD":{"modifications":("Purpose of Modification","LIST OF MODIFICATIONS"),
                                   "toc":"TABLE OF CONTENT",
                                   "requirement":"[R|r]equirements",
                                   "derived":"YES",
                                   "top_bottom_matrix":"Software Requirements -> System Requirements allocated to Software",
                                   "bottom_up_matrix":"System Requirements allocated to Software -> Software Requirements",
                                   "derived_matrix":"Derived Requirements",
                                   "tbd_matrix":"TBD (software )*High Level Requirements",
                                   "tbc_matrix":"TBC (software )*High Level Requirements",
                                   "deletion_matrix":"Deletion matrix"},
                           "SSCS":{"modifications":"LIST OF MODIFICATIONS",
                                   "toc":("TABLE OF CONTENTS","CONTENTS"),
                                   "requirement":("Functional requirements","FUNCTIONAL REQUIREMENTS"),
                                   "derived":("TRUE","YES")},
                           "ICD_SPI":{"modifications":"LIST OF MODIFICATIONS",
                                   "toc":"CONTENTS",
                                   "requirement":"[R|r]equirements",
                                   "derived":"TRUE"},
                           "ICD_CAN":{"modifications":"LIST OF MODIFICATIONS",
                                   "toc":"CONTENTS",
                                   "requirement":"[R|r]equirements",
                                   "derived":"TRUE"},
                           "SDTS":{"modifications":"LIST OF MODIFICATIONS",
                                   "toc":"CONTENTS",
                                   "requirement":"general constitution of WDS",
                                   "derived":"TRUE"},
                           "HSID":{"modifications":"LIST OF MODIFICATIONS",
                                   "toc":("TABLE OF CONTENTS","CONTENTS"),
                                   "requirement":("GENERAL ARCHITECTURE","MPC5566"),
                                   "derived":("TRUE","Yes")},
                           "HPID":{"modifications":"LIST OF MODIFICATIONS",
                                   "toc":"CONTENTS",
                                   "requirement":"GENERAL ARCHITECTURE",
                                   "derived":"TRUE"},
                           "IRD":{"tag_req":"CAN-IRD-",
                                  "modifications":"AMENDMENT RECORD CHART",
                                  "toc":"TABLE OF CONTENT",
                                  "requirement":"CAN NETWORK ARCHITECTURE",
                                  "derived":"TRUE"},
                           }
    dico_srts_rule_vs_check_rules = {"SRS_31":"S_10", # DO-178B/C chapter 6.3.1-a
                                     "SRS_32":"S_11", # DO-178B/C chapter 6.3.1-f
                                     "SRS_33":"",
                                     "SRS_34":"",
                                     "SRS_35":"",
                                     "SRS_36":"",
                                     "SRS_REQ_37":"S_5",
                                     "SRS_REQ_38":"S_4", # Check by REQtify, see StandardRules.br
                                     "SRS_REQ_39":"Not verifiable", # Check by REQtify for DELETED part only
                                     "SRS_REQ_40":"S_8", # Check by REQtify
                                     "SRS_REQ_41":"",
                                     "SRS_REQ_42":"", # Check by REQtify
                                     "SRS_REQ_43":"", # Check by REQtify
                                     "SRS_REQ_44":"", # Check by REQtify
                                     "SRS_REQ_45":"", # Check by REQtify
                                     "SRS_REQ_46":"", # Check by REQtify
                                     "SRS_REQ_47":"", # Check by REQtify
                                     "SRS_REQ_48":"", # Check by REQtify for DELETED part only
                                     "SRS_REQ_49":"",
                                     "SRS_REQ_50":"",
                                     "SRS_REQ_51":"",
                                     "SRS_REQ_53":"", # DO-178B/C chapter 6.3.1-b
                                     "SRS_REQ_54":"", # DO-178B/C chapter 6.3.1-d
                                     "SRS_REQ_56":"", # DO-178B/C chapter 6.3.1-d
                                     "SRS_REQ_57":"", # DO-178B/C chapter 6.3.1-d
                                     "SRS_REQ_61":"", # DO-178B/C chapter 6.3.1-g
                                     "SRS_REQ_62":"",
                                     "SRS_REQ_63":"", # DO-178B/C chapter 6.3.1-d
                                    }