__author__ = 'olivier'
class ExportDocx():
    def __init__(self,ihm,**kwargs):
        """

        :param ihm:
        :param kwargs:
        :return:
        """

        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        self.ihm = ihm
        Tool.__init__(self)

    def create(self,
               list_tags,
               template_key):
        template_name = self._getTemplate(template_key,"empty.docx")
        docx_filename = "_%f" % time.time() + ".docx"
        else:
            docx_filename = self.system + "_" + ccb_type + "_" + template_type + "_Minutes_" + self.reference + "_%f" % time.time() + ".docx"
        self.ihm.docx_filename = docx_filename
        self.docx_filename,exception = self._createDico2Word(list_tags,
                                                             template_name,
                                                             docx_filename)
        return self.docx_filename,exception
