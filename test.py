__author__ = 'Olive'

from unittest import TestLoader, TextTestRunner, TestSuite, TestCase
import coverage
import os
from os.path import join
from stack import Stack

class TestDoCID(TestCase):

    def test_FunctionCallTree(self):
        current_dir = os.getcwd()
        test = Stack() #ThreadQuery()
        test.compiler="cc"
        test.root_user_dir = join(current_dir,"qualification/SET_G7000_ACENM")
        test.src_user_dir  = "Software/SW_ACENM_CODE/SRC"
        test.build_user_dir  = "Software/SW_ACENM_CODE/BUILD"
        dico_function_vs_stack_size = test._getStackFromAsm()
        print ("dico_function_vs_stack_size",dico_function_vs_stack_size)
        print (len(dico_function_vs_stack_size))
        one_leaf = ['CtlBoot_P_Init', 'CtlStartup_G_Manager', 'DplCanRx_G_Init', '', '', '', '', '', '', '', '', '']
        compute_stack = test._computeStackSize(one_leaf,
                                               dico_function_vs_stack_size)
        assert(compute_stack==208)
        result = test._stackAnalysis()
        test._computeLeaves()
        for x in test.leaves:
            print ("X:",x)
        if len(test.leaves) > 2:
            assert(test.leaves[1]==['CtlSchd_G_Manager', 'CtlSchd_P_Init', 'CtlSchd_P_InitManagePowerCut', 'CmpWdg_G_Refresh', '', '', '', '', '', '', '', ''])
        else:
            print("Test failed")

    def setUp(self,case=0):
        #print("Setting up Test cases")
        dirname = ""
        current_dir = os.getcwd()
        if case == 1:
            self.dirname_upper = ""
            self.dirname_req = "C:/Users/olivier.appere/Documents/ENM/SW_ENM/SwDD"
            self.filename_is = "C:/Users/olivier.appere/Documents/ENM/SW_ENM/SwDD/IS_SwDD_ENM_ET3136_S.xlsm"
        elif case == 2:
            dirname = join(current_dir,"qualification/SET_F5X_ENM/SHLVCP")
        else:
            self.dirname_upper = join(current_dir,"qualification/SET_F5X_ENM/UPPER")
            self.dirname_req = join(current_dir,"qualification/SET_F5X_ENM/SWRD")
            self.filename_is = join(current_dir,"qualification/SET_F5X_ENM/IS/IS_SwRD_ENM_ET3135_S-5.1.1.xlsm")
            self.hsid_dirname = "/Users/olivier/github/local/HSID"
        self.ig = join(current_dir,"qualification/IG/procedures_zodiac_aero_electric.htm")
        self.saq = join(current_dir,"qualification/IG/formulaires_saq.htm")
        self.cov = coverage.coverage(branch=True,source=("stack.py",))
        self.cov.start()
        return dirname

    def tearDown(self):
        self.cov.stop()
        self.cov.save()
        try:
            self.cov.html_report(directory='covhtml')
        except coverage.CoverageException as e:
            print (e)

if __name__ == "__main__":

    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(TestDoCID)
        ))

    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)
