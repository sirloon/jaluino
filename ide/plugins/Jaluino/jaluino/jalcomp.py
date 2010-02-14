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

import os
import xml.dom.minidom as minidom

#--------------------------------------------------------------------------#
# Imports
import ed_glob
import autocomp.completer as completer

# Local Imports


#--------------------------------------------------------------------------#

class Completer(completer.BaseCompleter):
    """Code completer provider"""
    def __init__(self, stc_buffer):
        completer.BaseCompleter.__init__(self, stc_buffer)

        class AlwaysIn(list):
            def __contains__(self,val):
                return True

        # Setup
        self.SetAutoCompKeys(AlwaysIn())
        self.SetAutoCompStops(' ()')
        self.SetAutoCompFillups('')

        self.min_char_before_cmpl = 3

        # Read existing API file
        self._api_symbols = {}
        path = ed_glob.CONFIG['CACHE_DIR']
        apifile = os.environ.get("JALUINO_API_FILE","jaluino_api.xml")
        path = os.path.join(path, unicode(apifile))
        if os.path.exists(path):
            try:
                xmldoc = minidom.parse(path)
                comgroups = xmldoc.getElementsByTagName("commandgroup")
                for grpelem in comgroups:
                    grp = grpelem.getAttribute("value")
                    type = grpelem.getAttribute("type")
                    cmdelems = grpelem.getElementsByTagName("command")
                    cmds = [e.firstChild.nodeValue for e in cmdelems]

                    # register command_group => commands
                    # eg. include => all available includes
                    try:
                        self._api_symbols[grp] = completer.CreateSymbols(cmds,getattr(completer,type))
                    except AttributeError,e:
                        self._log("[jaluino][warn] '%s' is not a recognized completer type: %s" % (type,e))
                        self._api_symbols[grp] = completer.CreateSymbols(cmds,completer.TYPE_ELEMENT)

            except Exception,e:
                self._log("[jaluino][err] Unable to parse API file '%s' because %s" % (path,e))
        else:
            self._log("[jaluino][warn] No API file available, '%s' does not exist" % path)

        # mix all symbols into one category, for context independent autocompletion
        # (whatever the command before)
        for symbols in self._api_symbols.values():
            self._api_symbols.setdefault("__all__",[]).extend(symbols)

        self._log("[jaluino][info] completion map %s" % self._api_symbols)


    def GetAutoCompList(self, command):
        """Returns the list of possible completions for a
        command string. If namespace is not specified the lookup
        is based on the locals namespace
        @param command: commadn lookup is done on
        @keyword namespace: namespace to do lookup in

        """

        if command in [None, u'']:
            return list()

        # return available symbols according to previously entered command
        # remove spaces to keep only the command
        if self._api_symbols.has_key(command.strip()):
            return self._api_symbols[command.strip()]
        elif len(command) >= self.min_char_before_cmpl:
            # something has been entered, we try to complete
            # keep spaces, as in this case, space can be used to stop autocompl.
            return [symbol for symbol in self._api_symbols["__all__"] if symbol.Name.startswith(command)]
        else:
            return list()

