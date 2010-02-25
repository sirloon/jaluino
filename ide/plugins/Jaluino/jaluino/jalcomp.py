###############################################################################
# Name: jalcomp.py                                                            #
# Purpose: Jalv2 autocompleter                                                #
# Author: Sebastien Lelong                                                    #
# Copyright: (c) 2010 Sebastien Lelong <sebastien.lelong@gmail.com>           #
# License: wxWindows License                                                  #
###############################################################################

"""
Autocompletion for jalv2.
Uses an API file to get all available symbols.
"""

import os, re
import cPickle

import xml
import xml.dom
import xml.dom.minidom as minidom

import wx.stc

#--------------------------------------------------------------------------#
# Imports
import ed_glob
import ed_msg
import autocomp.completer as completer
import jallib

# Local Imports

# Globals
DEFAULT_JALUINO_API_FILE = "jaluino_api.pick"
INCLUDE_API_FILE = "jaluino_include.api"

#--------------------------------------------------------------------------#


def GetFullAPIFile():
    '''Return path to the file containing full API generated from
    all available JAL libraries
    '''
    pickfile = os.environ.get("JALUINO_API_FILE",DEFAULT_JALUINO_API_FILE)
    path = ed_glob.CONFIG['CACHE_DIR']
    filepath = os.path.join(path, unicode(pickfile))
    return filepath

def GetIncludeAPIFile():
    path = ed_glob.CONFIG['CACHE_DIR']
    apifile = os.path.join(path,INCLUDE_API_FILE)
    return apifile
        


class Completer(completer.BaseCompleter):
    """Code completer provider"""
    def __init__(self, stc_buffer):
        completer.BaseCompleter.__init__(self, stc_buffer)

        class AlwaysIn(list):
            def __init__(self,cmpl):
                self.cmpl = cmpl
            def __contains__(self,val):
                # except chars used for calltip'ing
                # and while calltip'ing
                return not self.cmpl.GetBuffer().CallTipActive() and \
                       not val in self.cmpl.GetCallTipKeys()

        # Setup
        self.SetAutoCompKeys(AlwaysIn(self))
        self.SetAutoCompStops('=,.\t\n')
        self.SetAutoCompFillups('')
        self.SetCallTipKeys([ord('('), ])
        self.SetCallTipCancel([ord(')'), wx.WXK_RETURN])

        # don't start to autocomplete until ... chars entered
        self.min_char_before_cmpl = 3
        # don't autowrite whole word
        self.SetChooseSingle(False)
        # jalv2 is case-insensitive
        self.SetCaseSensitive(False)

        # get all available libraries' path at startup
        self.libraries = jallib.get_library_list()

        # Contains every includes + symbols available in current buffer
        self._api_symbols = {}
        # Contains only API strings, for convenience (quick search, "it this symbol
        # already available ?")
        self._registered_symbol = {}    # what's in current API
        # Stores first level includes, that is, includes found in current buffer
        # Used to keep track on what's included, what's not include anymore, to adjust
        # current available API
        self._first_level_include = []  # include in current buffer only

        # auto-update API with a timer/worker (brut-force...)
        self._timer = wx.Timer(self.GetBuffer())
        self.GetBuffer().Bind(wx.EVT_TIMER, self.OnUpdateAPINeeded,self._timer)
        # wel will update API every xxx msecs
        self._timer.Start(1000)
        # we need to stop timer when buffer gets closed, or segfault will knock at your door :)
        ed_msg.Subscribe(self.OnTimeStopNeeded, ed_msg.EDMSG_UI_NB_CLOSING)

        # Generate current API
        self.GenerateAPI()

    def OnTimeStopNeeded(self,msg):
        if self._timer.IsRunning():
            self._timer.Stop()

    def OnUpdateAPINeeded(self, evt):
        self.GenerateCurrentAPI()

    def GetBufferContent(self):
        txt = self.GetBuffer().GetText().splitlines()
        return txt

    def GenerateCurrentAPI(self,libname=None,remove=False):
        '''Extract content from current buffer (if libname is None)
        or read corresponding JAL file and extract its API (if libname is
        specified), and merge (or unmerge if remove is True) its API.

        If libname includes other libraries, recursively merge/unmerge.
        '''
        if libname is None:
            content = self.GetBufferContent()
        else:
            jalfile = "%s.jal" % libname
            if self.libraries.get(jalfile):
                content = file(self.libraries[jalfile]).readlines()
            else:
                content = ""
                self._log("[jaluino][warn] Unable to get JAL file for library '%s'" % libname)
                
        apidesc = jallib.api_parse_content(content,strict=False)
        self.MergeAPI(libname,apidesc,remove)

        # never consider current buffer in add/remove API, it's done before
        scurrent = set([inc['name'] for inc in apidesc['include'] if not inc['name'] is None])
        sprev = set(self._first_level_include)
        toadds = scurrent.difference(sprev)
        # when about current buffer, analyze which lib should be added or deleted from API
        if libname is None:
            toremoves = sprev.difference(scurrent)
        else:
            toremoves = []

        for toadd in toadds:
            self.GenerateCurrentAPI(toadd)
        for toremove in toremoves:
            self.GenerateCurrentAPI(toremove,remove=True)

        # keep track of include in current buffer only (ie. not includes of include)
        if libname is None:
            self._first_level_include = list(scurrent)

    def MergeAPI(self,jalfile,api,remove=False):
        '''Merge an API description with existing. If remove is True,
        unmerge this API
          - jalfile: a JAL filename
          - api: a python dict representing API contained in jalfile
          - remove: trigger merge/unmerge
        '''

        def fill(libname,api,command,keyname,keyline,type):
            for elem in api:
                name = elem[keyname]
                # put all lowercased to do case-insensitive search
                lcname = name.lower()
                if not remove and self._registered_symbol.get(command) and self._registered_symbol[command].get(lcname):
                    continue
                # keep original case for symbol to be inserted
                symbol = completer.CreateSymbols([name],type)[0]
                libfile = self.libraries.get("%s.jal" % libname)
                line = elem[keyline]
                if remove:
                    idx = [symbol_info[0] for symbol_info in self._api_symbols["__all__"]].index(lcname)
                    self._api_symbols["__all__"].pop(idx)
                    del self._registered_symbol[command][lcname]
                else:
                    self._api_symbols.setdefault(command,[]).append((lcname,symbol,libfile,line,elem))
                    self._api_symbols.setdefault("__all__",[]).append((lcname,symbol,libfile,line,elem))
                    self._registered_symbol.setdefault(command,{})[lcname] = True

        libname = jalfile and jalfile.replace(".jal","")
        fill(libname,api['procedure'],"procedure","name","line",completer.TYPE_FUNCTION)
        fill(libname,api['function'],"function","name","line",completer.TYPE_FUNCTION)
        fill(libname,api['pseudovar'],"pseudovar","name","line",completer.TYPE_VARIABLE)
        fill(libname,api['var'],"var","name","line",completer.TYPE_VARIABLE)
        fill(libname,api['const'],"const","name","line",completer.TYPE_ATTRIBUTE)
        fill(libname,api['alias'],"alias","name","line",completer.TYPE_ELEMENT)
        # finally register lib containing API
        if remove:
            del self._registered_symbol["include"][libname.lower()]
        else:
            self._registered_symbol.setdefault("include",{})[libname and libname.lower()] = True

    def GenerateAPI(self):
        
        apifile = GetIncludeAPIFile()
        if os.path.exists(apifile):
            self._log("[jaluino][info] Loading API from file '%s'" % apifile)
            self._api_symbols['include'] = cPickle.load(file(apifile))
            self.GenerateCurrentAPI()
            return

        filepath = GetFullAPIFile()
        if os.path.exists(filepath):
            try:
                apis = cPickle.load(file(filepath))
            except Exception,e:
                self._log("[jaluino][err] Can't load complete API file '%s': %s" % (filepath,e))
                return

            # first deal with all includes
            for inc in apis.keys():
                libname = inc.replace(".jal","")
                symbol = completer.CreateSymbols([libname],completer.TYPE_CLASS)[0]
                # put all lowercased to do case-insensitive search, but keep original case
                self._api_symbols.setdefault('include',[]).append((libname.lower(),symbol,self.libraries.get(inc)))

        else:
            self._log("[jaluino][warn] No API file available, '%s' does not exist" % filepath)

        cPickle.dump(self._api_symbols['include'],file(apifile,"wb"))
        self.GenerateCurrentAPI()

    def GetSymbols(self,chars,command=None):
        '''return available symbols according to previously entered command
        remove spaces to keep only the command. But a space should exist
        after the command !
        '''
        chars = chars.lower()
        command = command and command.lower()
        if command and command == "include":
            res = sorted([symbol_info[1] for symbol_info in self._api_symbols[command] if symbol_info[0].startswith(chars)])
            return res
        elif len(chars) >= self.min_char_before_cmpl:
            # something has been entered, we try to complete
            # keep spaces, as in this case, space can be used to stop autocompl.
            return sorted([symbol_info[1] for symbol_info in self._api_symbols.get("__all__",[]) if symbol_info[0].startswith(chars)])
        else:
            return list()

    def GetAPIs(self,chars,command):
        apis = [symbol_info[-1] for symbol_info in self._api_symbols.get(command,[]) if symbol_info[0] == chars]
        return apis


    def GetAutoCompList(self, chars):
        if chars in [None, u'']:
            return list()

        ##print "orig chars: %s" % repr(chars)
        context_cmd = re.split("\s",chars)
        if len(context_cmd) > 1:
            chars = context_cmd.pop()
            prevcmd = context_cmd.pop()
        else:
            prevcmd = None

        ##print "prevcmd: %s, chars: %s" % (repr(prevcmd),repr(chars))
        return self.GetSymbols(chars,prevcmd)

    def GenerateToolTip(self,command,apis):
        '''Return tooltip string'''
        # there can be multiple definition (conditional compile)
        tp = []
        for api in apis:
            name = api['name']
            params = ["%(type)s %(context)s %(name)s" % param for param in api.get('params',[])]
            strparams = ", ".join(params)
            if command == "procedure" :
                tp.append("%s(%s)" % (name,strparams))
            if command == "function":
                rettype = api['return']
                tp.append("%s(%s) return %s" % (name,strparams,rettype))
        return u"\n\n".join(tp)


    def GetCallTip(self, chars):
        chars = chars.lower()
        # find which is the command type
        if self._registered_symbol.get("procedure") and self._registered_symbol['procedure'].get(chars):
            apis = self.GetAPIs(chars,"procedure")
            return self.GenerateToolTip("procedure",apis)
        elif self._registered_symbol.get("function") and self._registered_symbol['function'].get(chars):
            apis = self.GetAPIs(chars,"function")
            return self.GenerateToolTip("function",apis)

        # no tooltip...
        return u""


