"""
Provide CodeBrowser interface for Jalv2
"""

import codebrowser.gentag.taglib as taglib
import jallib


# type: registered icon class, used to match an existing icon
class Include(taglib.Scope):
    def __init__(self, name, line, scope=None):
        taglib.Scope.__init__(self, name, line, "class", scope)

class Procedure(taglib.Scope):
    def __init__(self, name, line, scope=None):
        taglib.Scope.__init__(self, name, line, "procedure", scope)

class Function(taglib.Scope):
    def __init__(self, name, line, scope=None):
        taglib.Scope.__init__(self, name, line, "function", scope)

class PseudoVar(taglib.Scope):
    def __init__(self, name, line, scope=None):
        taglib.Scope.__init__(self, name, line, "pseudovar", scope)

class Constant(taglib.Scope):
    def __init__(self, name, line, scope=None):
        taglib.Scope.__init__(self, name, line, "const", scope)

class Variable(taglib.Scope):
    def __init__(self, name, line, scope=None):
        taglib.Scope.__init__(self, name, line, "var", scope)

class Alias(taglib.Scope):
    def __init__(self, name, line, scope=None):
        taglib.Scope.__init__(self, name, line, "tag_blue", scope)

class JalBrowser(object):

    def __init__(self,buff):
        self.rtags = taglib.DocStruct()
        self.rtags.SetElementDescription('class', "Includes")
        self.rtags.SetElementDescription('procedure', "Procedures")
        self.rtags.SetElementDescription('function', "Functions")
        self.rtags.SetElementDescription('const', "Constants")
        self.rtags.SetElementDescription('variable', "Variables")
        self.rtags.SetElementDescription('tag_blue', "Aliases")
        self.rtags.SetElementPriority("class",50)
        self.rtags.SetElementPriority("procedure",40)
        self.rtags.SetElementPriority("function",30)
        self.rtags.SetElementPriority("const",10)
        self.rtags.SetElementPriority("variable",1)
        self.rtags.SetElementPriority("tag_blue",0)

        apidesc = jallib.api_parse_content(buff.readlines())
        self.fill(apidesc)

    def fill(self,apidesc):
        self.fillElements(apidesc['include'],Include,'class',50)
        self.fillElements(apidesc['procedure'],Procedure,'function',40)
        self.fillElements(apidesc['function'],Function,'function',30)
        self.fillElements(apidesc['pseudovar'],PseudoVar,'variable',20)
        self.fillElements(apidesc['const'],Constant,'const',10)
        self.fillElements(apidesc['var'],Variable,'variable',1)
        self.fillElements(apidesc['alias'],Alias,'tag_blue',-1)

    def fillElements(self,elems,klass,name,prio):
        for elem in elems:
            mobj = klass(elem['name'], elem['line'])
            self.rtags.AddElement(name,mobj)

    def getTags(self):
        return self.rtags


def GenerateTags(buff):
    """GenTag interface method
    @return: taglib.DocStruct

    """
    browser = JalBrowser(buff)
    return browser.getTags()

