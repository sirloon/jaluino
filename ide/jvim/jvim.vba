" Vimball Archiver by Charles E. Campbell, Jr., Ph.D.
UseVimball
finish
README	[[[1
36
JVIM, VIM for Jalv2, Jallib and Jaluino

Sort of mix of different vim plugin and several helper/wrapper
more specific to jalv2, jallib and jaluino projects.

Installation
------------

Standard way:

 - open vimball, "vim jvim.vba"
 - source it, ":so %"
 - uninstall it using ":RmVimball jvim"

If using pathogen plugin, you can install it as a bundle
 - create target location, "mkdir ~/.vim/bundle/jvim"
 - open vimball, "vim jvim.vba"
 - install vimball, ":UseVimball ~/.vim/bundle/jvim"
 - uninstall it simply deleting  ~/.vim/bundle/jvim directory


Description
-----------

Included in this plugin are:

 - an updated syntax file for jalv2
 - code snippets
 - shortcut based in "jaluino" (or "jallib") wrapper, used to 
   simplify compile/upload cycles
 - online documentation
 - ctags definition and generation
 - autocompletion
 - NERDTree, a file explorer which rocks, really


nerdtree_plugin/exec_menuitem.vim	[[[1
41
" ============================================================================
" File:        exec_menuitem.vim
" Description: plugin for NERD Tree that provides an execute file menu item
" Maintainer:  Martin Grenfell <martin.grenfell at gmail dot com>
" Last Change: 22 July, 2009
" License:     This program is free software. It comes without any warranty,
"              to the extent permitted by applicable law. You can redistribute
"              it and/or modify it under the terms of the Do What The Fuck You
"              Want To Public License, Version 2, as published by Sam Hocevar.
"              See http://sam.zoy.org/wtfpl/COPYING for more details.
"
" ============================================================================
if exists("g:loaded_nerdtree_exec_menuitem")
    finish
endif
let g:loaded_nerdtree_exec_menuitem = 1

call NERDTreeAddMenuItem({
            \ 'text': '(!)Execute file',
            \ 'shortcut': '!',
            \ 'callback': 'NERDTreeExecFile',
            \ 'isActiveCallback': 'NERDTreeExecFileActive' })

function! NERDTreeExecFileActive()
    let node = g:NERDTreeFileNode.GetSelected()
    return !node.path.isDirectory && node.path.isExecutable
endfunction

function! NERDTreeExecFile()
    let treenode = g:NERDTreeFileNode.GetSelected()
    echo "==========================================================\n"
    echo "Complete the command to execute (add arguments etc):\n"
    let cmd = treenode.path.str({'escape': 1})
    let cmd = input(':!', cmd . ' ')

    if cmd != ''
        exec ':!' . cmd
    else
        echo "Aborted"
    endif
endfunction
nerdtree_plugin/fs_menu.vim	[[[1
194
" ============================================================================
" File:        fs_menu.vim
" Description: plugin for the NERD Tree that provides a file system menu
" Maintainer:  Martin Grenfell <martin.grenfell at gmail dot com>
" Last Change: 17 July, 2009
" License:     This program is free software. It comes without any warranty,
"              to the extent permitted by applicable law. You can redistribute
"              it and/or modify it under the terms of the Do What The Fuck You
"              Want To Public License, Version 2, as published by Sam Hocevar.
"              See http://sam.zoy.org/wtfpl/COPYING for more details.
"
" ============================================================================
if exists("g:loaded_nerdtree_fs_menu")
    finish
endif
let g:loaded_nerdtree_fs_menu = 1

call NERDTreeAddMenuItem({'text': '(a)dd a childnode', 'shortcut': 'a', 'callback': 'NERDTreeAddNode'})
call NERDTreeAddMenuItem({'text': '(m)ove the curent node', 'shortcut': 'm', 'callback': 'NERDTreeMoveNode'})
call NERDTreeAddMenuItem({'text': '(d)elete the curent node', 'shortcut': 'd', 'callback': 'NERDTreeDeleteNode'})
if g:NERDTreePath.CopyingSupported()
    call NERDTreeAddMenuItem({'text': '(c)copy the current node', 'shortcut': 'c', 'callback': 'NERDTreeCopyNode'})
endif

"FUNCTION: s:echo(msg){{{1
function! s:echo(msg)
    redraw
    echomsg "NERDTree: " . a:msg
endfunction

"FUNCTION: s:echoWarning(msg){{{1
function! s:echoWarning(msg)
    echohl warningmsg
    call s:echo(a:msg)
    echohl normal
endfunction

"FUNCTION: s:promptToDelBuffer(bufnum, msg){{{1
"prints out the given msg and, if the user responds by pushing 'y' then the
"buffer with the given bufnum is deleted
"
"Args:
"bufnum: the buffer that may be deleted
"msg: a message that will be echoed to the user asking them if they wish to
"     del the buffer
function! s:promptToDelBuffer(bufnum, msg)
    echo a:msg
    if nr2char(getchar()) ==# 'y'
        exec "silent bdelete! " . a:bufnum
    endif
endfunction

"FUNCTION: NERDTreeAddNode(){{{1
function! NERDTreeAddNode()
    let curDirNode = g:NERDTreeDirNode.GetSelected()

    let newNodeName = input("Add a childnode\n".
                          \ "==========================================================\n".
                          \ "Enter the dir/file name to be created. Dirs end with a '/'\n" .
                          \ "", curDirNode.path.str({'format': 'Glob'}) . g:NERDTreePath.Slash())

    if newNodeName ==# ''
        call s:echo("Node Creation Aborted.")
        return
    endif

    try
        let newPath = g:NERDTreePath.Create(newNodeName)
        let parentNode = b:NERDTreeRoot.findNode(newPath.getParent())

        let newTreeNode = g:NERDTreeFileNode.New(newPath)
        if parentNode.isOpen || !empty(parentNode.children)
            call parentNode.addChild(newTreeNode, 1)
            call NERDTreeRender()
            call newTreeNode.putCursorHere(1, 0)
        endif
    catch /^NERDTree/
        call s:echoWarning("Node Not Created.")
    endtry
endfunction

"FUNCTION: NERDTreeMoveNode(){{{1
function! NERDTreeMoveNode()
    let curNode = g:NERDTreeFileNode.GetSelected()
    let newNodePath = input("Rename the current node\n" .
                          \ "==========================================================\n" .
                          \ "Enter the new path for the node:                          \n" .
                          \ "", curNode.path.str())

    if newNodePath ==# ''
        call s:echo("Node Renaming Aborted.")
        return
    endif

    try
        let bufnum = bufnr(curNode.path.str())

        call curNode.rename(newNodePath)
        call NERDTreeRender()

        "if the node is open in a buffer, ask the user if they want to
        "close that buffer
        if bufnum != -1
            let prompt = "\nNode renamed.\n\nThe old file is open in buffer ". bufnum . (bufwinnr(bufnum) ==# -1 ? " (hidden)" : "") .". Delete this buffer? (yN)"
            call s:promptToDelBuffer(bufnum, prompt)
        endif

        call curNode.putCursorHere(1, 0)

        redraw
    catch /^NERDTree/
        call s:echoWarning("Node Not Renamed.")
    endtry
endfunction

" FUNCTION: NERDTreeDeleteNode() {{{1
function! NERDTreeDeleteNode()
    let currentNode = g:NERDTreeFileNode.GetSelected()
    let confirmed = 0

    if currentNode.path.isDirectory
        let choice =input("Delete the current node\n" .
                         \ "==========================================================\n" .
                         \ "STOP! To delete this entire directory, type 'yes'\n" .
                         \ "" . currentNode.path.str() . ": ")
        let confirmed = choice ==# 'yes'
    else
        echo "Delete the current node\n" .
           \ "==========================================================\n".
           \ "Are you sure you wish to delete the node:\n" .
           \ "" . currentNode.path.str() . " (yN):"
        let choice = nr2char(getchar())
        let confirmed = choice ==# 'y'
    endif


    if confirmed
        try
            call currentNode.delete()
            call NERDTreeRender()

            "if the node is open in a buffer, ask the user if they want to
            "close that buffer
            let bufnum = bufnr(currentNode.path.str())
            if buflisted(bufnum)
                let prompt = "\nNode deleted.\n\nThe file is open in buffer ". bufnum . (bufwinnr(bufnum) ==# -1 ? " (hidden)" : "") .". Delete this buffer? (yN)"
                call s:promptToDelBuffer(bufnum, prompt)
            endif

            redraw
        catch /^NERDTree/
            call s:echoWarning("Could not remove node")
        endtry
    else
        call s:echo("delete aborted")
    endif

endfunction

" FUNCTION: NERDTreeCopyNode() {{{1
function! NERDTreeCopyNode()
    let currentNode = g:NERDTreeFileNode.GetSelected()
    let newNodePath = input("Copy the current node\n" .
                          \ "==========================================================\n" .
                          \ "Enter the new path to copy the node to:                   \n" .
                          \ "", currentNode.path.str())

    if newNodePath != ""
        "strip trailing slash
        let newNodePath = substitute(newNodePath, '\/$', '', '')

        let confirmed = 1
        if currentNode.path.copyingWillOverwrite(newNodePath)
            call s:echo("Warning: copying may overwrite files! Continue? (yN)")
            let choice = nr2char(getchar())
            let confirmed = choice ==# 'y'
        endif

        if confirmed
            try
                let newNode = currentNode.copy(newNodePath)
                call NERDTreeRender()
                call newNode.putCursorHere(0, 0)
            catch /^NERDTree/
                call s:echoWarning("Could not copy node")
            endtry
        endif
    else
        call s:echo("Copy aborted.")
    endif
    redraw
endfunction

" vim: set sw=4 sts=4 et fdm=marker:
doc/NERD_tree.txt	[[[1
1222
*NERD_tree.txt*   A tree explorer plugin that owns your momma!



    omg its ... ~

    ________  ________   _   ____________  ____     __________  ____________~
   /_  __/ / / / ____/  / | / / ____/ __ \/ __ \   /_  __/ __ \/ ____/ ____/~
    / / / /_/ / __/    /  |/ / __/ / /_/ / / / /    / / / /_/ / __/ / __/   ~
   / / / __  / /___   / /|  / /___/ _, _/ /_/ /    / / / _, _/ /___/ /___   ~
  /_/ /_/ /_/_____/  /_/ |_/_____/_/ |_/_____/    /_/ /_/ |_/_____/_____/   ~


                              Reference Manual~




==============================================================================
CONTENTS                                                   *NERDTree-contents*

    1.Intro...................................|NERDTree|
    2.Functionality provided..................|NERDTreeFunctionality|
        2.1.Global commands...................|NERDTreeGlobalCommands|
        2.2.Bookmarks.........................|NERDTreeBookmarks|
            2.2.1.The bookmark table..........|NERDTreeBookmarkTable|
            2.2.2.Bookmark commands...........|NERDTreeBookmarkCommands|
            2.2.3.Invalid bookmarks...........|NERDTreeInvalidBookmarks|
        2.3.NERD tree mappings................|NERDTreeMappings|
        2.4.The NERD tree menu................|NERDTreeMenu|
    3.Options.................................|NERDTreeOptions|
        3.1.Option summary....................|NERDTreeOptionSummary|
        3.2.Option details....................|NERDTreeOptionDetails|
    4.The NERD tree API.......................|NERDTreeAPI|
        4.1.Key map API.......................|NERDTreeKeymapAPI|
        4.2.Menu API..........................|NERDTreeMenuAPI|
    5.About...................................|NERDTreeAbout|
    6.Changelog...............................|NERDTreeChangelog|
    7.Credits.................................|NERDTreeCredits|
    8.License.................................|NERDTreeLicense|

==============================================================================
1. Intro                                                            *NERDTree*

What is this "NERD tree"??

The NERD tree allows you to explore your filesystem and to open files and
directories. It presents the filesystem to you in the form of a tree which you
manipulate with the keyboard and/or mouse. It also allows you to perform
simple filesystem operations.

The following features and functionality are provided by the NERD tree:
    * Files and directories are displayed in a hierarchical tree structure
    * Different highlighting is provided for the following types of nodes:
        * files
        * directories
        * sym-links
        * windows .lnk files
        * read-only files
        * executable files
    * Many (customisable) mappings are provided to manipulate the tree:
        * Mappings to open/close/explore directory nodes
        * Mappings to open files in new/existing windows/tabs
        * Mappings to change the current root of the tree
        * Mappings to navigate around the tree
        * ...
    * Directories and files can be bookmarked.
    * Most NERD tree navigation can also be done with the mouse
    * Filtering of tree content (can be toggled at runtime)
        * custom file filters to prevent e.g. vim backup files being displayed
        * optional displaying of hidden files (. files)
        * files can be "turned off" so that only directories are displayed
    * The position and size of the NERD tree window can be customised
    * The order in which the nodes in the tree are listed can be customised.
    * A model of your filesystem is created/maintained as you explore it. This
      has several advantages:
        * All filesystem information is cached and is only re-read on demand
        * If you revisit a part of the tree that you left earlier in your
          session, the directory nodes will be opened/closed as you left them
    * The script remembers the cursor position and window position in the NERD
      tree so you can toggle it off (or just close the tree window) and then
      reopen it (with NERDTreeToggle) the NERD tree window will appear exactly
      as you left it
    * You can have a separate NERD tree for each tab, share trees across tabs,
      or a mix of both.
    * By default the script overrides the default file browser (netw), so if
      you :edit a directory a (slighly modified) NERD tree will appear in the
      current window
    * A programmable menu system is provided (simulates right clicking on a
      node)
        * one default menu plugin is provided to perform basic filesytem
          operations (create/delete/move/copy files/directories)
    * There's an API for adding your own keymappings


==============================================================================
2. Functionality provided                              *NERDTreeFunctionality*

------------------------------------------------------------------------------
2.1. Global Commands                                  *NERDTreeGlobalCommands*

:NERDTree [<start-directory> | <bookmark>]                         *:NERDTree*
    Opens a fresh NERD tree. The root of the tree depends on the argument
    given. There are 3 cases: If no argument is given, the current directory
    will be used.  If a directory is given, that will be used. If a bookmark
    name is given, the corresponding directory will be used.  For example: >
        :NERDTree /home/marty/vim7/src
        :NERDTree foo   (foo is the name of a bookmark)
<
:NERDTreeFromBookmark <bookmark>                       *:NERDTreeFromBookmark*
    Opens a fresh NERD tree with the root initialized to the dir for
    <bookmark>.  This only reason to use this command over :NERDTree is for
    the completion (which is for bookmarks rather than directories).

:NERDTreeToggle [<start-directory> | <bookmark>]             *:NERDTreeToggle*
    If a NERD tree already exists for this tab, it is reopened and rendered
    again.  If no NERD tree exists for this tab then this command acts the
    same as the |:NERDTree| command.

:NERDTreeMirror                                              *:NERDTreeMirror*
    Shares an existing NERD tree, from another tab, in the current tab.
    Changes made to one tree are reflected in both as they are actually the
    same buffer.

    If only one other NERD tree exists, that tree is automatically mirrored. If
    more than one exists, the script will ask which tree to mirror.

:NERDTreeClose                                                *:NERDTreeClose*
    Close the NERD tree in this tab.

:NERDTreeFind                                                  *:NERDTreeFind*
    Find the current file in the tree. If no tree exists for the current tab,
    or the file is not under the current root, then initialize a new tree where
    the root is the directory of the current file.

------------------------------------------------------------------------------
2.2. Bookmarks                                             *NERDTreeBookmarks*

Bookmarks in the NERD tree are a way to tag files or directories of interest.
For example, you could use bookmarks to tag all of your project directories.

------------------------------------------------------------------------------
2.2.1. The Bookmark Table                              *NERDTreeBookmarkTable*

If the bookmark table is active (see |NERDTree-B| and
|'NERDTreeShowBookmarks'|), it will be rendered above the tree. You can double
click bookmarks or use the |NERDTree-o| mapping to activate them. See also,
|NERDTree-t| and |NERDTree-T|

------------------------------------------------------------------------------
2.2.2. Bookmark commands                            *NERDTreeBookmarkCommands*

Note that the following commands are only available in the NERD tree buffer.

:Bookmark <name>
    Bookmark the current node as <name>. If there is already a <name>
    bookmark, it is overwritten. <name> must not contain spaces.

:BookmarkToRoot <bookmark>
    Make the directory corresponding to <bookmark> the new root. If a treenode
    corresponding to <bookmark> is already cached somewhere in the tree then
    the current tree will be used, otherwise a fresh tree will be opened.
    Note that if <bookmark> points to a file then its parent will be used
    instead.

:RevealBookmark <bookmark>
    If the node is cached under the current root then it will be revealed
    (i.e. directory nodes above it will be opened) and the cursor will be
    placed on it.

:OpenBookmark <bookmark>
    <bookmark> must point to a file. The file is opened as though |NERDTree-o|
    was applied. If the node is cached under the current root then it will be
    revealed and the cursor will be placed on it.

:ClearBookmarks [<bookmarks>]
    Remove all the given bookmarks. If no bookmarks are given then remove all
    bookmarks on the current node.

:ClearAllBookmarks
    Remove all bookmarks.

:ReadBookmarks
    Re-read the bookmarks in the |'NERDTreeBookmarksFile'|.

See also |:NERDTree| and |:NERDTreeFromBookmark|.

------------------------------------------------------------------------------
2.2.3. Invalid Bookmarks                            *NERDTreeInvalidBookmarks*

If invalid bookmarks are detected, the script will issue an error message and
the invalid bookmarks will become unavailable for use.

These bookmarks will still be stored in the bookmarks file (see
|'NERDTreeBookmarksFile'|), down the bottom. There will always be a blank line
after the valid bookmarks but before the invalid ones.

Each line in the bookmarks file represents one bookmark. The proper format is:
<bookmark name><space><full path to the bookmark location>

After you have corrected any invalid bookmarks, either restart vim, or go
:ReadBookmarks from the NERD tree window.

------------------------------------------------------------------------------
2.3. NERD tree Mappings                                     *NERDTreeMappings*

Default  Description~                                             help-tag~
Key~

o.......Open files, directories and bookmarks....................|NERDTree-o|
go......Open selected file, but leave cursor in the NERDTree.....|NERDTree-go|
t.......Open selected node/bookmark in a new tab.................|NERDTree-t|
T.......Same as 't' but keep the focus on the current tab........|NERDTree-T|
i.......Open selected file in a split window.....................|NERDTree-i|
gi......Same as i, but leave the cursor on the NERDTree..........|NERDTree-gi|
s.......Open selected file in a new vsplit.......................|NERDTree-s|
gs......Same as s, but leave the cursor on the NERDTree..........|NERDTree-gs|
O.......Recursively open the selected directory..................|NERDTree-O|
x.......Close the current nodes parent...........................|NERDTree-x|
X.......Recursively close all children of the current node.......|NERDTree-X|
e.......Edit the current dif.....................................|NERDTree-e|

<CR>...............same as |NERDTree-o|.
double-click.......same as the |NERDTree-o| map.
middle-click.......same as |NERDTree-i| for files, same as
                   |NERDTree-e| for dirs.

D.......Delete the current bookmark .............................|NERDTree-D|

P.......Jump to the root node....................................|NERDTree-P|
p.......Jump to current nodes parent.............................|NERDTree-p|
K.......Jump up inside directories at the current tree depth.....|NERDTree-K|
J.......Jump down inside directories at the current tree depth...|NERDTree-J|
<C-J>...Jump down to the next sibling of the current directory...|NERDTree-C-J|
<C-K>...Jump up to the previous sibling of the current directory.|NERDTree-C-K|

C.......Change the tree root to the selected dir.................|NERDTree-C|
u.......Move the tree root up one directory......................|NERDTree-u|
U.......Same as 'u' except the old root node is left open........|NERDTree-U|
r.......Recursively refresh the current directory................|NERDTree-r|
R.......Recursively refresh the current root.....................|NERDTree-R|
m.......Display the NERD tree menu...............................|NERDTree-m|
cd......Change the CWD to the dir of the selected node...........|NERDTree-cd|

I.......Toggle whether hidden files displayed....................|NERDTree-I|
f.......Toggle whether the file filters are used.................|NERDTree-f|
F.......Toggle whether files are displayed.......................|NERDTree-F|
B.......Toggle whether the bookmark table is displayed...........|NERDTree-B|

q.......Close the NERDTree window................................|NERDTree-q|
A.......Zoom (maximize/minimize) the NERDTree window.............|NERDTree-A|
?.......Toggle the display of the quick help.....................|NERDTree-?|

------------------------------------------------------------------------------
                                                                  *NERDTree-o*
Default key: o
Map option: NERDTreeMapActivateNode
Applies to: files and directories.

If a file node is selected, it is opened in the previous window.

If a directory is selected it is opened or closed depending on its current
state.

If a bookmark that links to a directory is selected then that directory
becomes the new root.

If a bookmark that links to a file is selected then that file is opened in the
previous window.

------------------------------------------------------------------------------
                                                                 *NERDTree-go*
Default key: go
Map option: None
Applies to: files.

If a file node is selected, it is opened in the previous window, but the
cursor does not move.

The key combo for this mapping is always "g" + NERDTreeMapActivateNode (see
|NERDTree-o|).

------------------------------------------------------------------------------
                                                                  *NERDTree-t*
Default key: t
Map option: NERDTreeMapOpenInTab
Applies to: files and directories.

Opens the selected file in a new tab. If a directory is selected, a fresh
NERD Tree for that directory is opened in a new tab.

If a bookmark which points to a directory is selected, open a NERD tree for
that directory in a new tab. If the bookmark points to a file, open that file
in a new tab.

------------------------------------------------------------------------------
                                                                  *NERDTree-T*
Default key: T
Map option: NERDTreeMapOpenInTabSilent
Applies to: files and directories.

The same as |NERDTree-t| except that the focus is kept in the current tab.

------------------------------------------------------------------------------
                                                                  *NERDTree-i*
Default key: i
Map option: NERDTreeMapOpenSplit
Applies to: files.

Opens the selected file in a new split window and puts the cursor in the new
window.

------------------------------------------------------------------------------
                                                                 *NERDTree-gi*
Default key: gi
Map option: None
Applies to: files.

The same as |NERDTree-i| except that the cursor is not moved.

The key combo for this mapping is always "g" + NERDTreeMapOpenSplit (see
|NERDTree-i|).

------------------------------------------------------------------------------
                                                                  *NERDTree-s*
Default key: s
Map option: NERDTreeMapOpenVSplit
Applies to: files.

Opens the selected file in a new vertically split window and puts the cursor in
the new window.

------------------------------------------------------------------------------
                                                                 *NERDTree-gs*
Default key: gs
Map option: None
Applies to: files.

The same as |NERDTree-s| except that the cursor is not moved.

The key combo for this mapping is always "g" + NERDTreeMapOpenVSplit (see
|NERDTree-s|).

------------------------------------------------------------------------------
                                                                  *NERDTree-O*
Default key: O
Map option: NERDTreeMapOpenRecursively
Applies to: directories.

Recursively opens the selelected directory.

All files and directories are cached, but if a directory would not be
displayed due to file filters (see |'NERDTreeIgnore'| |NERDTree-f|) or the
hidden file filter (see |'NERDTreeShowHidden'|) then its contents are not
cached. This is handy, especially if you have .svn directories.

------------------------------------------------------------------------------
                                                                  *NERDTree-x*
Default key: x
Map option: NERDTreeMapCloseDir
Applies to: files and directories.

Closes the parent of the selected node.

------------------------------------------------------------------------------
                                                                  *NERDTree-X*
Default key: X
Map option: NERDTreeMapCloseChildren
Applies to: directories.

Recursively closes all children of the selected directory.

Tip: To quickly "reset" the tree, use |NERDTree-P| with this mapping.

------------------------------------------------------------------------------
                                                                  *NERDTree-e*
Default key: e
Map option: NERDTreeMapOpenExpl
Applies to: files and directories.

|:edit|s the selected directory, or the selected file's directory. This could
result in a NERD tree or a netrw being opened, depending on
|'NERDTreeHijackNetrw'|.

------------------------------------------------------------------------------
                                                                  *NERDTree-D*
Default key: D
Map option: NERDTreeMapDeleteBookmark
Applies to: lines in the bookmarks table

Deletes the currently selected bookmark.

------------------------------------------------------------------------------
                                                                  *NERDTree-P*
Default key: P
Map option: NERDTreeMapJumpRoot
Applies to: no restrictions.

Jump to the tree root.

------------------------------------------------------------------------------
                                                                  *NERDTree-p*
Default key: p
Map option: NERDTreeMapJumpParent
Applies to: files and directories.

Jump to the parent node of the selected node.

------------------------------------------------------------------------------
                                                                  *NERDTree-K*
Default key: K
Map option: NERDTreeMapJumpFirstChild
Applies to: files and directories.

Jump to the first child of the current nodes parent.

If the cursor is already on the first node then do the following:
    * loop back thru the siblings of the current nodes parent until we find an
      open dir with children
    * go to the first child of that node

------------------------------------------------------------------------------
                                                                  *NERDTree-J*
Default key: J
Map option: NERDTreeMapJumpLastChild
Applies to: files and directories.

Jump to the last child of the current nodes parent.

If the cursor is already on the last node then do the following:
    * loop forward thru the siblings of the current nodes parent until we find
      an open dir with children
    * go to the last child of that node

------------------------------------------------------------------------------
                                                                *NERDTree-C-J*
Default key: <C-J>
Map option: NERDTreeMapJumpNextSibling
Applies to: files and directories.

Jump to the next sibling of the selected node.

------------------------------------------------------------------------------
                                                                *NERDTree-C-K*
Default key: <C-K>
Map option: NERDTreeMapJumpPrevSibling
Applies to: files and directories.

Jump to the previous sibling of the selected node.

------------------------------------------------------------------------------
                                                                  *NERDTree-C*
Default key: C
Map option: NERDTreeMapChdir
Applies to: directories.

Make the selected directory node the new tree root. If a file is selected, its
parent is used.

------------------------------------------------------------------------------
                                                                  *NERDTree-u*
Default key: u
Map option: NERDTreeMapUpdir
Applies to: no restrictions.

Move the tree root up a dir (like doing a "cd ..").

------------------------------------------------------------------------------
                                                                  *NERDTree-U*
Default key: U
Map option: NERDTreeMapUpdirKeepOpen
Applies to: no restrictions.

Like |NERDTree-u| except that the old tree root is kept open.

------------------------------------------------------------------------------
                                                                  *NERDTree-r*
Default key: r
Map option: NERDTreeMapRefresh
Applies to: files and directories.

If a dir is selected, recursively refresh that dir, i.e. scan the filesystem
for changes and represent them in the tree.

If a file node is selected then the above is done on it's parent.

------------------------------------------------------------------------------
                                                                  *NERDTree-R*
Default key: R
Map option: NERDTreeMapRefreshRoot
Applies to: no restrictions.

Recursively refresh the tree root.

------------------------------------------------------------------------------
                                                                  *NERDTree-m*
Default key: m
Map option: NERDTreeMapMenu
Applies to: files and directories.

Display the NERD tree menu. See |NERDTreeMenu| for details.

------------------------------------------------------------------------------
                                                                 *NERDTree-cd*
Default key: cd
Map option: NERDTreeMapChdir
Applies to: files and directories.

Change vims current working directory to that of the selected node.

------------------------------------------------------------------------------
                                                                  *NERDTree-I*
Default key: I
Map option: NERDTreeMapToggleHidden
Applies to: no restrictions.

Toggles whether hidden files (i.e. "dot files") are displayed.

------------------------------------------------------------------------------
                                                                  *NERDTree-f*
Default key: f
Map option: NERDTreeMapToggleFilters
Applies to: no restrictions.

Toggles whether file filters are used. See |'NERDTreeIgnore'| for details.

------------------------------------------------------------------------------
                                                                  *NERDTree-F*
Default key: F
Map option: NERDTreeMapToggleFiles
Applies to: no restrictions.

Toggles whether file nodes are displayed.

------------------------------------------------------------------------------
                                                                  *NERDTree-B*
Default key: B
Map option: NERDTreeMapToggleBookmarks
Applies to: no restrictions.

Toggles whether the bookmarks table is displayed.

------------------------------------------------------------------------------
                                                                  *NERDTree-q*
Default key: q
Map option: NERDTreeMapQuit
Applies to: no restrictions.

Closes the NERDtree window.

------------------------------------------------------------------------------
                                                                  *NERDTree-A*
Default key: A
Map option: NERDTreeMapToggleZoom
Applies to: no restrictions.

Maximize (zoom) and minimize the NERDtree window.

------------------------------------------------------------------------------
                                                                  *NERDTree-?*
Default key: ?
Map option: NERDTreeMapHelp
Applies to: no restrictions.

Toggles whether the quickhelp is displayed.

------------------------------------------------------------------------------
2.3. The NERD tree menu                                         *NERDTreeMenu*

The NERD tree has a menu that can be programmed via the an API (see
|NERDTreeMenuAPI|). The idea is to simulate the "right click" menus that most
file explorers have.

The script comes with two default menu plugins: exec_menuitem.vim and
fs_menu.vim. fs_menu.vim adds some basic filesystem operations to the menu for
creating/deleting/moving/copying files and dirs. exec_menuitem.vim provides a
menu item to execute executable files.

Related tags: |NERDTree-m| |NERDTreeApi|

==============================================================================
3. Customisation                                             *NERDTreeOptions*


------------------------------------------------------------------------------
3.1. Customisation summary                             *NERDTreeOptionSummary*

The script provides the following options that can customise the behaviour the
NERD tree. These options should be set in your vimrc.

|'loaded_nerd_tree'|            Turns off the script.

|'NERDChristmasTree'|           Tells the NERD tree to make itself colourful
                                and pretty.

|'NERDTreeAutoCenter'|          Controls whether the NERD tree window centers
                                when the cursor moves within a specified
                                distance to the top/bottom of the window.
|'NERDTreeAutoCenterThreshold'| Controls the sensitivity of autocentering.

|'NERDTreeCaseSensitiveSort'|   Tells the NERD tree whether to be case
                                sensitive or not when sorting nodes.

|'NERDTreeChDirMode'|           Tells the NERD tree if/when it should change
                                vim's current working directory.

|'NERDTreeHighlightCursorline'| Tell the NERD tree whether to highlight the
                                current cursor line.

|'NERDTreeHijackNetrw'|         Tell the NERD tree whether to replace the netrw
                                autocommands for exploring local directories.

|'NERDTreeIgnore'|              Tells the NERD tree which files to ignore.

|'NERDTreeBookmarksFile'|       Where the bookmarks are stored.

|'NERDTreeMouseMode'|           Tells the NERD tree how to handle mouse
                                clicks.

|'NERDTreeQuitOnOpen'|          Closes the tree window after opening a file.

|'NERDTreeShowBookmarks'|       Tells the NERD tree whether to display the
                                bookmarks table on startup.

|'NERDTreeShowFiles'|           Tells the NERD tree whether to display files
                                in the tree on startup.

|'NERDTreeShowHidden'|          Tells the NERD tree whether to display hidden
                                files on startup.

|'NERDTreeShowLineNumbers'|     Tells the NERD tree whether to display line
                                numbers in the tree window.

|'NERDTreeSortOrder'|           Tell the NERD tree how to sort the nodes in
                                the tree.

|'NERDTreeStatusline'|          Set a statusline for NERD tree windows.

|'NERDTreeWinPos'|              Tells the script where to put the NERD tree
                                window.

|'NERDTreeWinSize'|             Sets the window size when the NERD tree is
                                opened.

------------------------------------------------------------------------------
3.2. Customisation details                             *NERDTreeOptionDetails*

To enable any of the below options you should put the given line in your
~/.vimrc

                                                          *'loaded_nerd_tree'*
If this plugin is making you feel homicidal, it may be a good idea to turn it
off with this line in your vimrc: >
    let loaded_nerd_tree=1
<
------------------------------------------------------------------------------
                                                         *'NERDChristmasTree'*
Values: 0 or 1.
Default: 1.

If this option is set to 1 then some extra syntax highlighting elements are
added to the nerd tree to make it more colourful.

Set it to 0 for a more vanilla looking tree.

------------------------------------------------------------------------------
                                                        *'NERDTreeAutoCenter'*
Values: 0 or 1.
Default: 1

If set to 1, the NERD tree window will center around the cursor if it moves to
within |'NERDTreeAutoCenterThreshold'| lines of the top/bottom of the window.

This is ONLY done in response to tree navigation mappings,
i.e. |NERDTree-J| |NERDTree-K| |NERDTree-C-J| |NERDTree-C-K| |NERDTree-p|
|NERDTree-P|

The centering is done with a |zz| operation.

------------------------------------------------------------------------------
                                               *'NERDTreeAutoCenterThreshold'*
Values: Any natural number.
Default: 3

This option controls the "sensitivity" of the NERD tree auto centering. See
|'NERDTreeAutoCenter'| for details.

------------------------------------------------------------------------------
                                                 *'NERDTreeCaseSensitiveSort'*
Values: 0 or 1.
Default: 0.

By default the NERD tree does not sort nodes case sensitively, i.e. nodes
could appear like this: >
    bar.c
    Baz.c
    blarg.c
    boner.c
    Foo.c
<
But, if you set this option to 1 then the case of the nodes will be taken into
account. The above nodes would then be sorted like this: >
    Baz.c
    Foo.c
    bar.c
    blarg.c
    boner.c
<
------------------------------------------------------------------------------
                                                         *'NERDTreeChDirMode'*

Values: 0, 1 or 2.
Default: 0.

Use this option to tell the script when (if at all) to change the current
working directory (CWD) for vim.

If it is set to 0 then the CWD is never changed by the NERD tree.

If set to 1 then the CWD is changed when the NERD tree is first loaded to the
directory it is initialized in. For example, if you start the NERD tree with >
    :NERDTree /home/marty/foobar
<
then the CWD will be changed to /home/marty/foobar and will not be changed
again unless you init another NERD tree with a similar command.

If the option is set to 2 then it behaves the same as if set to 1 except that
the CWD is changed whenever the tree root is changed. For example, if the CWD
is /home/marty/foobar and you make the node for /home/marty/foobar/baz the new
root then the CWD will become /home/marty/foobar/baz.

------------------------------------------------------------------------------
                                               *'NERDTreeHighlightCursorline'*
Values: 0 or 1.
Default: 1.

If set to 1, the current cursor line in the NERD tree buffer will be
highlighted. This is done using the |'cursorline'| option.

------------------------------------------------------------------------------
                                                       *'NERDTreeHijackNetrw'*
Values: 0 or 1.
Default: 1.

If set to 1, doing a >
    :edit <some directory>
<
will open up a "secondary" NERD tree instead of a netrw in the target window.

Secondary NERD trees behaves slighly different from a regular trees in the
following respects:
    1. 'o' will open the selected file in the same window as the tree,
       replacing it.
    2. you can have as many secondary tree as you want in the same tab.

------------------------------------------------------------------------------
                                                            *'NERDTreeIgnore'*
Values: a list of regular expressions.
Default: ['\~$'].

This option is used to specify which files the NERD tree should ignore.  It
must be a list of regular expressions. When the NERD tree is rendered, any
files/dirs that match any of the regex's in 'NERDTreeIgnore' wont be
displayed.

For example if you put the following line in your vimrc: >
    let NERDTreeIgnore=['\.vim$', '\~$']
<
then all files ending in .vim or ~ will be ignored.

Note: to tell the NERD tree not to ignore any files you must use the following
line: >
    let NERDTreeIgnore=[]
<

The file filters can be turned on and off dynamically with the |NERDTree-f|
mapping.

------------------------------------------------------------------------------
                                                     *'NERDTreeBookmarksFile'*
Values: a path
Default: $HOME/.NERDTreeBookmarks

This is where bookmarks are saved. See |NERDTreeBookmarkCommands|.

------------------------------------------------------------------------------
                                                       *'NERDTreeMouseMode'*
Values: 1, 2 or 3.
Default: 1.

If set to 1 then a double click on a node is required to open it.
If set to 2 then a single click will open directory nodes, while a double
click will still be required for file nodes.
If set to 3 then a single click will open any node.

Note: a double click anywhere on a line that a tree node is on will
activate it, but all single-click activations must be done on name of the node
itself. For example, if you have the following node: >
    | | |-application.rb
<
then (to single click activate it) you must click somewhere in
'application.rb'.

------------------------------------------------------------------------------
                                                        *'NERDTreeQuitOnOpen'*

Values: 0 or 1.
Default: 0

If set to 1, the NERD tree window will close after opening a file with the
|NERDTree-o|, |NERDTree-i|, |NERDTree-t| and |NERDTree-T| mappings.

------------------------------------------------------------------------------
                                                     *'NERDTreeShowBookmarks'*
Values: 0 or 1.
Default: 0.

If this option is set to 1 then the bookmarks table will be displayed.

This option can be toggled dynamically, per tree, with the |NERDTree-B|
mapping.

------------------------------------------------------------------------------
                                                         *'NERDTreeShowFiles'*
Values: 0 or 1.
Default: 1.

If this option is set to 1 then files are displayed in the NERD tree. If it is
set to 0 then only directories are displayed.

This option can be toggled dynamically, per tree, with the |NERDTree-F|
mapping and is useful for drastically shrinking the tree when you are
navigating to a different part of the tree.

------------------------------------------------------------------------------
                                                        *'NERDTreeShowHidden'*
Values: 0 or 1.
Default: 0.

This option tells vim whether to display hidden files by default. This option
can be dynamically toggled, per tree, with the |NERDTree-I| mapping.  Use one
of the follow lines to set this option: >
    let NERDTreeShowHidden=0
    let NERDTreeShowHidden=1
<

------------------------------------------------------------------------------
                                                   *'NERDTreeShowLineNumbers'*
Values: 0 or 1.
Default: 0.

This option tells vim whether to display line numbers for the NERD tree
window.  Use one of the follow lines to set this option: >
    let NERDTreeShowLineNumbers=0
    let NERDTreeShowLineNumbers=1
<

------------------------------------------------------------------------------
                                                         *'NERDTreeSortOrder'*
Values: a list of regular expressions.
Default: ['\/$', '*', '\.swp$',  '\.bak$', '\~$']

This option is set to a list of regular expressions which are used to
specify the order of nodes under their parent.

For example, if the option is set to: >
    ['\.vim$', '\.c$', '\.h$', '*', 'foobar']
<
then all .vim files will be placed at the top, followed by all .c files then
all .h files. All files containing the string 'foobar' will be placed at the
end.  The star is a special flag: it tells the script that every node that
doesnt match any of the other regexps should be placed here.

If no star is present in 'NERDTreeSortOrder' then one is automatically
appended to the array.

The regex '\/$' should be used to match directory nodes.

After this sorting is done, the files in each group are sorted alphabetically.

Other examples: >
    (1) ['*', '\/$']
    (2) []
    (3) ['\/$', '\.rb$', '\.php$', '*', '\.swp$',  '\.bak$', '\~$']
<
1. Directories will appear last, everything else will appear above.
2. Everything will simply appear in alphabetical order.
3. Dirs will appear first, then ruby and php. Swap files, bak files and vim
   backup files will appear last with everything else preceding them.

------------------------------------------------------------------------------
                                                        *'NERDTreeStatusline'*
Values: Any valid statusline setting.
Default: %{b:NERDTreeRoot.path.strForOS(0)}

Tells the script what to use as the |'statusline'| setting for NERD tree
windows.

Note that the statusline is set using |:let-&| not |:set| so escaping spaces
isn't necessary.

Setting this option to -1 will will deactivate it so that your global
statusline setting is used instead.

------------------------------------------------------------------------------
                                                            *'NERDTreeWinPos'*
Values: "left" or "right"
Default: "left".

This option is used to determine where NERD tree window is placed on the
screen.

This option makes it possible to use two different explorer plugins
simultaneously. For example, you could have the taglist plugin on the left of
the window and the NERD tree on the right.

------------------------------------------------------------------------------
                                                           *'NERDTreeWinSize'*
Values: a positive integer.
Default: 31.

This option is used to change the size of the NERD tree when it is loaded.

==============================================================================
4. The NERD tree API                                             *NERDTreeAPI*

The NERD tree script allows you to add custom key mappings and menu items via
a set of API calls. Any scripts that use this API should be placed in
~/.vim/nerdtree_plugin/ (*nix) or ~/vimfiles/nerdtree_plugin (windows).

The script exposes some prototype objects that can be used to manipulate the
tree and/or get information from it: >
    g:NERDTreePath
    g:NERDTreeDirNode
    g:NERDTreeFileNode
    g:NERDTreeBookmark
<
See the code/comments in NERD_tree.vim to find how to use these objects. The
following code conventions are used:
    * class members start with a capital letter
    * instance members start with a lower case letter
    * private members start with an underscore

See this blog post for more details:
 http://got-ravings.blogspot.com/2008/09/vim-pr0n-prototype-based-objects.html

------------------------------------------------------------------------------
4.1. Key map API                                           *NERDTreeKeymapAPI*

NERDTreeAddKeyMap({options})                             *NERDTreeAddKeyMap()*
    Adds a new keymapping for all NERD tree buffers.
    {options} must be a dictionary, and must contain the following keys:
    "key" - the trigger key for the new mapping
    "callback" - the function the new mapping will be bound to
    "quickhelpText" - the text that will appear in the quickhelp (see
    |NERDTree-?|)

    Example: >
        call NERDTreeAddKeyMap({
               \ 'key': 'b',
               \ 'callback': 'NERDTreeEchoCurrentNode',
               \ 'quickhelpText': 'echo full path of current node' })

        function! NERDTreeEchoCurrentNode()
            let n = g:NERDTreeFileNode.GetSelected()
            if n != {}
                echomsg 'Current node: ' . n.path.str()
            endif
        endfunction
<
    This code should sit in a file like ~/.vim/nerdtree_plugin/mymapping.vim.
    It adds a (rather useless) mapping on 'b' which echos the full path to the
    current node.

------------------------------------------------------------------------------
4.2. Menu API                                                *NERDTreeMenuAPI*

NERDTreeAddSubmenu({options})                           *NERDTreeAddSubmenu()*
    Creates and returns a new submenu.

    {options} must be a dictionary and must contain the following keys:
    "text" - the text of the submenu that the user will see
    "shortcut" - a shortcut key for the submenu (need not be unique)

    The following keys are optional:
    "isActiveCallback" - a function that will be called to determine whether
    this submenu item will be displayed or not. The callback function must return
    0 or 1.
    "parent" - the parent submenu of the new submenu (returned from a previous
    invocation of NERDTreeAddSubmenu()). If this key is left out then the new
    submenu will sit under the top level menu.

    See below for an example.

NERDTreeAddMenuItem({options})                         *NERDTreeAddMenuItem()*
    Adds a new menu item to the NERD tree menu (see |NERDTreeMenu|).

    {options} must be a dictionary and must contain the
    following keys:
    "text" - the text of the menu item which the user will see
    "shortcut" - a shortcut key for the menu item (need not be unique)
    "callback" - the function that will be called when the user activates the
    menu item.

    The following keys are optional:
    "isActiveCallback" - a function that will be called to determine whether
    this menu item will be displayed or not. The callback function must return
    0 or 1.
    "parent" - if the menu item belongs under a submenu then this key must be
    specified. This value for this key will be the object that
    was returned when the submenu was created with |NERDTreeAddSubmenu()|.

    See below for an example.

NERDTreeAddMenuSeparator([{options}])             *NERDTreeAddMenuSeparator()*
    Adds a menu separator (a row of dashes).

    {options} is an optional dictionary that may contain the following keys:
    "isActiveCallback" - see description in |NERDTreeAddMenuItem()|.

Below is an example of the menu API in action. >
    call NERDTreeAddMenuSeparator()

    call NERDTreeAddMenuItem({
                \ 'text': 'a (t)op level menu item',
                \ 'shortcut': 't',
                \ 'callback': 'SomeFunction' })

    let submenu = NERDTreeAddSubmenu({
                \ 'text': 'a (s)ub menu',
                \ 'shortcut': 's' })

    call NERDTreeAddMenuItem({
                \ 'text': '(n)ested item 1',
                \ 'shortcut': 'n',
                \ 'callback': 'SomeFunction',
                \ 'parent': submenu })

    call NERDTreeAddMenuItem({
                \ 'text': '(n)ested item 2',
                \ 'shortcut': 'n',
                \ 'callback': 'SomeFunction',
                \ 'parent': submenu })
<
This will create the following menu: >
  --------------------
  a (t)op level menu item
  a (s)ub menu
<
Where selecting "a (s)ub menu" will lead to a second menu: >
  (n)ested item 1
  (n)ested item 2
<
When any of the 3 concrete menu items are selected the function "SomeFunction"
will be called.

------------------------------------------------------------------------------
NERDTreeRender()                                            *NERDTreeRender()*
    Re-renders the NERD tree buffer. Useful if you change the state of the
    tree and you want to it to be reflected in the UI.

==============================================================================
5. About                                                       *NERDTreeAbout*

The author of the NERD tree is a terrible terrible monster called Martyzilla
who gobbles up small children with milk and sugar for breakfast.

He can be reached at martin.grenfell at gmail dot com. He would love to hear
from you, so feel free to send him suggestions and/or comments about this
plugin.  Don't be shy --- the worst he can do is slaughter you and stuff you in
the fridge for later ;)

The latest stable versions can be found at
    http://www.vim.org/scripts/script.php?script_id=1658

The latest dev versions are on github
    http://github.com/scrooloose/nerdtree


==============================================================================
6. Changelog                                               *NERDTreeChangelog*

4.1.0
    features:
    - NERDTreeFind to reveal the node for the current buffer in the tree,
      see |NERDTreeFind|. This effectively merges the FindInNERDTree plugin (by
      Doug McInnes) into the script.
    - make NERDTreeQuitOnOpen apply to the t/T keymaps too. Thanks to Stefan
      Ritter and Rémi Prévost.
    - truncate the root node if wider than the tree window. Thanks to Victor
      Gonzalez.

    bugfixes:
    - really fix window state restoring
    - fix some win32 path escaping issues. Thanks to Stephan Baumeister, Ricky,
      jfilip1024, and Chris Chambers

4.0.0
    - add a new programmable menu system (see :help NERDTreeMenu).
    - add new APIs to add menus/menu-items to the menu system as well as
      custom key mappings to the NERD tree buffer (see :help NERDTreeAPI).
    - removed the old API functions
    - added a mapping to maximize/restore the size of nerd tree window, thanks
      to Guillaume Duranceau for the patch. See :help NERDTree-A for details.

    - fix a bug where secondary nerd trees (netrw hijacked trees) and
      NERDTreeQuitOnOpen didnt play nicely, thanks to Curtis Harvey.
    - fix a bug where the script ignored directories whose name ended in a dot,
      thanks to Aggelos Orfanakos for the patch.
    - fix a bug when using the x mapping on the tree root, thanks to Bryan
      Venteicher for the patch.
    - fix a bug where the cursor position/window size of the nerd tree buffer
      wasnt being stored on closing the window, thanks to Richard Hart.
    - fix a bug where NERDTreeMirror would mirror the wrong tree

3.1.1
    - fix a bug where a non-listed no-name buffer was getting created every
      time the tree windows was created, thanks to Derek Wyatt and owen1
    - make <CR> behave the same as the 'o' mapping
    - some helptag fixes in the doc, thanks strull
    - fix a bug when using :set nohidden and opening a file where the previous
      buf was modified. Thanks iElectric
    - other minor fixes

3.1.0
    New features:
    - add mappings to open files in a vsplit, see :help NERDTree-s and :help
      NERDTree-gs
    - make the statusline for the nerd tree window default to something
      hopefully more useful. See :help 'NERDTreeStatusline'
    Bugfixes:
    - make the hijack netrw functionality work when vim is started with "vim
      <some dir>" (thanks to Alf Mikula for the patch).
    - fix a bug where the CWD wasnt being changed for some operations even when
      NERDTreeChDirMode==2 (thanks to Lucas S. Buchala)
    - add -bar to all the nerd tree :commands so they can chain with other
      :commands (thanks to tpope)
    - fix bugs when ignorecase was set (thanks to nach)
    - fix a bug with the relative path code (thanks to nach)
    - fix a bug where doing a :cd would cause :NERDTreeToggle to fail (thanks nach)


3.0.1
    Bugfixes:
    - fix bugs with :NERDTreeToggle and :NERDTreeMirror when 'hidden
      was not set
    - fix a bug where :NERDTree <path> would fail if <path> was relative and
      didnt start with a ./ or ../  Thanks to James Kanze.
    - make the q mapping work with secondary (:e <dir>  style) trees,
      thanks to jamessan
    - fix a bunch of small bugs with secondary trees

    More insane refactoring.

3.0.0
    - hijack netrw so that doing an :edit <directory>  will put a NERD tree in
      the window rather than a netrw browser. See :help 'NERDTreeHijackNetrw'
    - allow sharing of trees across tabs, see :help :NERDTreeMirror
    - remove "top" and "bottom" as valid settings for NERDTreeWinPos
    - change the '<tab>' mapping to 'i'
    - change the 'H' mapping to 'I'
    - lots of refactoring

==============================================================================
7. Credits                                                   *NERDTreeCredits*

Thanks to the following people for testing, bug reports, ideas etc. Without
you I probably would have got bored of the hacking the NERD tree and
just downloaded pr0n instead.

    Tim Carey-Smith (halorgium)
    Vigil
    Nick Brettell
    Thomas Scott Urban
    Terrance Cohen
    Yegappan Lakshmanan
    Jason Mills
    Michael Geddes (frogonwheels)
    Yu Jun
    Michael Madsen
    AOYAMA Shotaro
    Zhang Weiwu
    Niels Aan de Brugh
    Olivier Yiptong
    Zhang Shuhan
    Cory Echols
    Piotr Czachur
    Yuan Jiang
    Matan Nassau
    Maxim Kim
    Charlton Wang
    Matt Wozniski (godlygeek)
    knekk
    Sean Chou
    Ryan Penn
    Simon Peter Nicholls
    Michael Foobar
    Tomasz Chomiuk
    Denis Pokataev
    Tim Pope (tpope)
    James Kanze
    James Vega (jamessan)
    Frederic Chanal (nach)
    Alf Mikula
    Lucas S. Buchala
    Curtis Harvey
    Guillaume Duranceau
    Richard Hart (hates)
    Doug McInnes
    Stefan Ritter
    Rémi Prévost
    Victor Gonzalez
    Stephan Baumeister
    Ricky
    jfilip1024
    Chris Chambers

==============================================================================
8. License                                                   *NERDTreeLicense*

The NERD tree is released under the wtfpl.
See http://sam.zoy.org/wtfpl/COPYING.
plugin/jvim.vim	[[[1
204

" only trigger plugin if launched from wrapper
if $JVIM_ROOT == ""
    "finish
endif

" Compilation of many vim tips glued together to bring some
" sort of IDE with compilation output windows...


"""""""""""""""""
" From http://vim.wikia.com/wiki/Automatically_fitting_a_quickfix_window_height
"""""""""""""""""
au FileType qf call AdjustWindowHeight(10,15)
function! AdjustWindowHeight(minheight, maxheight)
  exe max([min([line("$"), a:maxheight]), a:minheight]) . "wincmd _"
endfunction

""""""""""""""""
" http://vim.wikia.com/wiki/Always_keep_quickfix_window_at_specified_height
""""""""""""""""

" Maximize the window after entering it, be sure to keep the quickfix window
" at the specified height.
"au WinEnter * call MaximizeAndResizeQuickfix(8)

" Maximize current window and set the quickfix window to the specified height.
function MaximizeAndResizeQuickfix(quickfixHeight)
  " Redraw after executing the function.
  set lazyredraw
  " Ignore WinEnter events for now.
  set ei=WinEnter
  " Maximize current window.
  wincmd _
  " If the current window is the quickfix window
  if (getbufvar(winbufnr(winnr()), "&buftype") == "quickfix")
    " Maximize previous window, and resize the quickfix window to the
    " specified height.
    wincmd p
    resize
    wincmd p
    exe "resize " . a:quickfixHeight
  else
    " Current window isn't the quickfix window, loop over all windows to
    " find it (if it exists...)
    let i = 1
    let currBufNr = winbufnr(i)
    while (currBufNr != -1)
      " If the buffer in window i is the quickfix buffer.
      if (getbufvar(currBufNr, "&buftype") == "quickfix")
        " Go to the quickfix window, set height to quickfixHeight, and jump to the previous
        " window.
        exe i . "wincmd w"
        exe "resize " . a:quickfixHeight
        wincmd p
        break
      endif
      let i = i + 1
      let currBufNr = winbufnr(i)
    endwhile
  endif
  set ei-=WinEnter
  set nolazyredraw
endfunction

" Remap ,m to make and open error window if there are any errors. If there
" weren't any errors, the current window is maximized.
map <silent> ,m :mak<CR><CR>:cw<CR>:call MaximizeIfNotQuickfix()<CR>

" Maximizes the current window if it is not the quickfix window.
function MaximizeIfNotQuickfix()
  if (getbufvar(winbufnr(winnr()), "&buftype") != "quickfix")
    wincmd _
  endif
endfunction


" Automatically quit Vim if quickfix window is the last
" http://vim.wikia.com/wiki/VimTip536
au BufEnter * call MyLastWindow()
function! MyLastWindow()
    " if the window is quickfix go on
    if &buftype=="quickfix"
        " if this window is last on screen quit without warning
        if winbufnr(2) == -1
            quit!
        endif
    endif
endfunction

function MoveUpAndMaximize()
    wincmd k
    wincmd _
    call MaximizeAndResizeQuickfix(10)
endfunction

function MoveDownAndMaximize()
    wincmd j
    wincmd _
    call MaximizeAndResizeQuickfix(10)
endfunction

function DoCompile()
    "" Quickfix
    set makeprg=jaluino\ compile\ %
    set efm=%f:%l:%m
    make
    set makeprg=make " defaulting back
endfunction

function DoUpload()
    "" Quickfix
    set makeprg=jaluino\ upload\ %
    "set efm=%f:%l:%m
    make
    set makeprg=make " defaulting back
endfunction

function DoValidate()
    "" Quickfix
    set makeprg=jaluino\ validate\ %
    set efm=%EFile:\ %f,%Z%s:\ %f:%l:\ %m
    make
    set makeprg=make " defaulting back
endfunction

function DoReindent()
    "" Quickfix
    set makeprg=jaluino\ reindent\ %
    make
    set makeprg=make " defaulting back
endfunction

" generate jalapi doc for given jal file
function DoJalapi()
endfunction

" update all jalapi doc, browsing every jal files
" found in JALLIB_REPOS directories
function UpdateJalapi()
endfunction



" enrich with nice plugins...
"source plugin/NERD_tree.vim
runtime! NERD_tree.vim
"source plugin/taglist.vim
" TODO omni completion
" TODO conque
" TODO txtfmt
"source plugin/jaluinoide.vim

" jal language (taglist)
let tlist_jalv2_settings = 'jalv2;c:constant;p:procedure;f:function;v:variable'

"" File browser
" shorcut for explorer
map <C-P> :NERDTreeToggle<CR>
" shorcut for new window
nmap <silent> <C-N> <C-W>n<C-W>_<CR>
" allow fast switching between window
map <silent> <C-J> :call MoveDownAndMaximize()<CR>
map <silent> <C-K> :call MoveUpAndMaximize()<CR>
map <C-H> <C-W>h
map <C-L> <C-W>l

"" shortcuts
" rebuild ctags
"map <C-F12> :!ctags -R -h jal -f tags/jallib $JALUINO_ROOT/3rdparty/jallib_svn<CR>

map <C-F12> :!oIFS=$IFS && IFS=: && for d in "$JALLIB_REPOS" ;do  echo Extracting tags from $d; find $d -name \*.jal -type f \| xargs ctags -a -f tags/jallib.tmp; done && IFS="$oIFS" && mv tags/jallib.tmp tags/jallib<CR>|set tags+=tags/jallib

map <silent> <F5> :call DoCompile()<CR><CR>
map <silent> <F6> :call DoValidate()<CR>
map <F7> :!jaluino reindent %<CR>
map <silent> <F8> :call DoUpload()<CR>

" taglist
" ctags definition
set tags+=tags/jallib
" shorcut
"map <C-B> :TlistOpen<CR>
"
"set verbose=9
filetype on

autocmd! Syntax jalv2 runtime! jalv2.vim
autocmd! FileType jalv2 set softtabstop=3|set tabstop=3|set expandtab|set keywordprg=|set cinwords=if,for,while,forever,case|set smartindent
autocmd! BufNewFile,BufRead,BufEnter *.jal setfiletype jalv2


filetype plugin on
filetype plugin indent on

" misc
set cursorline

"" open quickfix window
""copen
""wincmd k

set mouse=a

plugin/NERD_tree.vim	[[[1
4059
" ============================================================================
" File:        NERD_tree.vim
" Description: vim global plugin that provides a nice tree explorer
" Maintainer:  Martin Grenfell <martin.grenfell at gmail dot com>
" Last Change: 1 December, 2009
" License:     This program is free software. It comes without any warranty,
"              to the extent permitted by applicable law. You can redistribute
"              it and/or modify it under the terms of the Do What The Fuck You
"              Want To Public License, Version 2, as published by Sam Hocevar.
"              See http://sam.zoy.org/wtfpl/COPYING for more details.
"
" ============================================================================
let s:NERD_tree_version = '4.1.0'

" SECTION: Script init stuff {{{1
"============================================================
if exists("loaded_nerd_tree")
    finish
endif
if v:version < 700
    echoerr "NERDTree: this plugin requires vim >= 7. DOWNLOAD IT! You'll thank me later!"
    finish
endif
let loaded_nerd_tree = 1

"for line continuation - i.e dont want C in &cpo
let s:old_cpo = &cpo
set cpo&vim

"Function: s:initVariable() function {{{2
"This function is used to initialise a given variable to a given value. The
"variable is only initialised if it does not exist prior
"
"Args:
"var: the name of the var to be initialised
"value: the value to initialise var to
"
"Returns:
"1 if the var is set, 0 otherwise
function! s:initVariable(var, value)
    if !exists(a:var)
        exec 'let ' . a:var . ' = ' . "'" . a:value . "'"
        return 1
    endif
    return 0
endfunction

"SECTION: Init variable calls and other random constants {{{2
call s:initVariable("g:NERDChristmasTree", 1)
call s:initVariable("g:NERDTreeAutoCenter", 1)
call s:initVariable("g:NERDTreeAutoCenterThreshold", 3)
call s:initVariable("g:NERDTreeCaseSensitiveSort", 0)
call s:initVariable("g:NERDTreeChDirMode", 0)
if !exists("g:NERDTreeIgnore")
    let g:NERDTreeIgnore = ['\~$']
endif
call s:initVariable("g:NERDTreeBookmarksFile", expand('$HOME') . '/.NERDTreeBookmarks')
call s:initVariable("g:NERDTreeHighlightCursorline", 1)
call s:initVariable("g:NERDTreeHijackNetrw", 1)
call s:initVariable("g:NERDTreeMouseMode", 1)
call s:initVariable("g:NERDTreeNotificationThreshold", 100)
call s:initVariable("g:NERDTreeQuitOnOpen", 0)
call s:initVariable("g:NERDTreeShowBookmarks", 0)
call s:initVariable("g:NERDTreeShowFiles", 1)
call s:initVariable("g:NERDTreeShowHidden", 0)
call s:initVariable("g:NERDTreeShowLineNumbers", 0)
call s:initVariable("g:NERDTreeSortDirs", 1)

if !exists("g:NERDTreeSortOrder")
    let g:NERDTreeSortOrder = ['\/$', '*', '\.swp$',  '\.bak$', '\~$']
else
    "if there isnt a * in the sort sequence then add one
    if count(g:NERDTreeSortOrder, '*') < 1
        call add(g:NERDTreeSortOrder, '*')
    endif
endif

"we need to use this number many times for sorting... so we calculate it only
"once here
let s:NERDTreeSortStarIndex = index(g:NERDTreeSortOrder, '*')

if !exists('g:NERDTreeStatusline')

    "the exists() crap here is a hack to stop vim spazzing out when
    "loading a session that was created with an open nerd tree. It spazzes
    "because it doesnt store b:NERDTreeRoot (its a b: var, and its a hash)
    let g:NERDTreeStatusline = "%{exists('b:NERDTreeRoot')?b:NERDTreeRoot.path.str():''}"

endif
call s:initVariable("g:NERDTreeWinPos", "left")
call s:initVariable("g:NERDTreeWinSize", 31)

let s:running_windows = has("win16") || has("win32") || has("win64")

"init the shell commands that will be used to copy nodes, and remove dir trees
"
"Note: the space after the command is important
if s:running_windows
    call s:initVariable("g:NERDTreeRemoveDirCmd", 'rmdir /s /q ')
else
    call s:initVariable("g:NERDTreeRemoveDirCmd", 'rm -rf ')
    call s:initVariable("g:NERDTreeCopyCmd", 'cp -r ')
endif


"SECTION: Init variable calls for key mappings {{{2
call s:initVariable("g:NERDTreeMapActivateNode", "o")
call s:initVariable("g:NERDTreeMapChangeRoot", "C")
call s:initVariable("g:NERDTreeMapChdir", "cd")
call s:initVariable("g:NERDTreeMapCloseChildren", "X")
call s:initVariable("g:NERDTreeMapCloseDir", "x")
call s:initVariable("g:NERDTreeMapDeleteBookmark", "D")
call s:initVariable("g:NERDTreeMapMenu", "m")
call s:initVariable("g:NERDTreeMapHelp", "?")
call s:initVariable("g:NERDTreeMapJumpFirstChild", "K")
call s:initVariable("g:NERDTreeMapJumpLastChild", "J")
call s:initVariable("g:NERDTreeMapJumpNextSibling", "<C-j>")
call s:initVariable("g:NERDTreeMapJumpParent", "p")
call s:initVariable("g:NERDTreeMapJumpPrevSibling", "<C-k>")
call s:initVariable("g:NERDTreeMapJumpRoot", "P")
call s:initVariable("g:NERDTreeMapOpenExpl", "e")
call s:initVariable("g:NERDTreeMapOpenInTab", "t")
call s:initVariable("g:NERDTreeMapOpenInTabSilent", "T")
call s:initVariable("g:NERDTreeMapOpenRecursively", "O")
call s:initVariable("g:NERDTreeMapOpenSplit", "i")
call s:initVariable("g:NERDTreeMapOpenVSplit", "s")
call s:initVariable("g:NERDTreeMapPreview", "g" . NERDTreeMapActivateNode)
call s:initVariable("g:NERDTreeMapPreviewSplit", "g" . NERDTreeMapOpenSplit)
call s:initVariable("g:NERDTreeMapPreviewVSplit", "g" . NERDTreeMapOpenVSplit)
call s:initVariable("g:NERDTreeMapQuit", "q")
call s:initVariable("g:NERDTreeMapRefresh", "r")
call s:initVariable("g:NERDTreeMapRefreshRoot", "R")
call s:initVariable("g:NERDTreeMapToggleBookmarks", "B")
call s:initVariable("g:NERDTreeMapToggleFiles", "F")
call s:initVariable("g:NERDTreeMapToggleFilters", "f")
call s:initVariable("g:NERDTreeMapToggleHidden", "I")
call s:initVariable("g:NERDTreeMapToggleZoom", "A")
call s:initVariable("g:NERDTreeMapUpdir", "u")
call s:initVariable("g:NERDTreeMapUpdirKeepOpen", "U")

"SECTION: Script level variable declaration{{{2
if s:running_windows
    let s:escape_chars =  " `\|\"#%&,?()\*^<>"
else
    let s:escape_chars =  " \\`\|\"#%&,?()\*^<>"
endif
let s:NERDTreeBufName = 'NERD_tree_'

let s:tree_wid = 2
let s:tree_markup_reg = '^[ `|]*[\-+~]'
let s:tree_up_dir_line = '.. (up a dir)'

"the number to add to the nerd tree buffer name to make the buf name unique
let s:next_buffer_number = 1

" SECTION: Commands {{{1
"============================================================
"init the command that users start the nerd tree with
command! -n=? -complete=dir -bar NERDTree :call s:initNerdTree('<args>')
command! -n=? -complete=dir -bar NERDTreeToggle :call s:toggle('<args>')
command! -n=0 -bar NERDTreeClose :call s:closeTreeIfOpen()
command! -n=1 -complete=customlist,s:completeBookmarks -bar NERDTreeFromBookmark call s:initNerdTree('<args>')
command! -n=0 -bar NERDTreeMirror call s:initNerdTreeMirror()
command! -n=0 -bar NERDTreeFind call s:findAndRevealPath()
" SECTION: Auto commands {{{1
"============================================================
augroup NERDTree
    "Save the cursor position whenever we close the nerd tree
    exec "autocmd BufWinLeave ". s:NERDTreeBufName ."* call <SID>saveScreenState()"
    "cache bookmarks when vim loads
    autocmd VimEnter * call s:Bookmark.CacheBookmarks(0)

    "load all nerdtree plugins after vim starts
    autocmd VimEnter * runtime! nerdtree_plugin/**/*.vim
augroup END

if g:NERDTreeHijackNetrw
    augroup NERDTreeHijackNetrw
        autocmd VimEnter * silent! autocmd! FileExplorer
        au BufEnter,VimEnter * call s:checkForBrowse(expand("<amatch>"))
    augroup END
endif

"SECTION: Classes {{{1
"============================================================
"CLASS: Bookmark {{{2
"============================================================
let s:Bookmark = {}
" FUNCTION: Bookmark.activate() {{{3
function! s:Bookmark.activate()
    if self.path.isDirectory
        call self.toRoot()
    else
        if self.validate()
            let n = s:TreeFileNode.New(self.path)
            call n.open()
        endif
    endif
endfunction
" FUNCTION: Bookmark.AddBookmark(name, path) {{{3
" Class method to add a new bookmark to the list, if a previous bookmark exists
" with the same name, just update the path for that bookmark
function! s:Bookmark.AddBookmark(name, path)
    for i in s:Bookmark.Bookmarks()
        if i.name ==# a:name
            let i.path = a:path
            return
        endif
    endfor
    call add(s:Bookmark.Bookmarks(), s:Bookmark.New(a:name, a:path))
    call s:Bookmark.Sort()
endfunction
" Function: Bookmark.Bookmarks()   {{{3
" Class method to get all bookmarks. Lazily initializes the bookmarks global
" variable
function! s:Bookmark.Bookmarks()
    if !exists("g:NERDTreeBookmarks")
        let g:NERDTreeBookmarks = []
    endif
    return g:NERDTreeBookmarks
endfunction
" Function: Bookmark.BookmarkExistsFor(name)   {{{3
" class method that returns 1 if a bookmark with the given name is found, 0
" otherwise
function! s:Bookmark.BookmarkExistsFor(name)
    try
        call s:Bookmark.BookmarkFor(a:name)
        return 1
    catch /^NERDTree.BookmarkNotFoundError/
        return 0
    endtry
endfunction
" Function: Bookmark.BookmarkFor(name)   {{{3
" Class method to get the bookmark that has the given name. {} is return if no
" bookmark is found
function! s:Bookmark.BookmarkFor(name)
    for i in s:Bookmark.Bookmarks()
        if i.name ==# a:name
            return i
        endif
    endfor
    throw "NERDTree.BookmarkNotFoundError: no bookmark found for name: \"". a:name  .'"'
endfunction
" Function: Bookmark.BookmarkNames()   {{{3
" Class method to return an array of all bookmark names
function! s:Bookmark.BookmarkNames()
    let names = []
    for i in s:Bookmark.Bookmarks()
        call add(names, i.name)
    endfor
    return names
endfunction
" FUNCTION: Bookmark.CacheBookmarks(silent) {{{3
" Class method to read all bookmarks from the bookmarks file intialize
" bookmark objects for each one.
"
" Args:
" silent - dont echo an error msg if invalid bookmarks are found
function! s:Bookmark.CacheBookmarks(silent)
    if filereadable(g:NERDTreeBookmarksFile)
        let g:NERDTreeBookmarks = []
        let g:NERDTreeInvalidBookmarks = []
        let bookmarkStrings = readfile(g:NERDTreeBookmarksFile)
        let invalidBookmarksFound = 0
        for i in bookmarkStrings

            "ignore blank lines
            if i != ''

                let name = substitute(i, '^\(.\{-}\) .*$', '\1', '')
                let path = substitute(i, '^.\{-} \(.*\)$', '\1', '')

                try
                    let bookmark = s:Bookmark.New(name, s:Path.New(path))
                    call add(g:NERDTreeBookmarks, bookmark)
                catch /^NERDTree.InvalidArgumentsError/
                    call add(g:NERDTreeInvalidBookmarks, i)
                    let invalidBookmarksFound += 1
                endtry
            endif
        endfor
        if invalidBookmarksFound
            call s:Bookmark.Write()
            if !a:silent
                call s:echo(invalidBookmarksFound . " invalid bookmarks were read. See :help NERDTreeInvalidBookmarks for info.")
            endif
        endif
        call s:Bookmark.Sort()
    endif
endfunction
" FUNCTION: Bookmark.compareTo(otherbookmark) {{{3
" Compare these two bookmarks for sorting purposes
function! s:Bookmark.compareTo(otherbookmark)
    return a:otherbookmark.name < self.name
endfunction
" FUNCTION: Bookmark.ClearAll() {{{3
" Class method to delete all bookmarks.
function! s:Bookmark.ClearAll()
    for i in s:Bookmark.Bookmarks()
        call i.delete()
    endfor
    call s:Bookmark.Write()
endfunction
" FUNCTION: Bookmark.delete() {{{3
" Delete this bookmark. If the node for this bookmark is under the current
" root, then recache bookmarks for its Path object
function! s:Bookmark.delete()
    let node = {}
    try
        let node = self.getNode(1)
    catch /^NERDTree.BookmarkedNodeNotFoundError/
    endtry
    call remove(s:Bookmark.Bookmarks(), index(s:Bookmark.Bookmarks(), self))
    if !empty(node)
        call node.path.cacheDisplayString()
    endif
    call s:Bookmark.Write()
endfunction
" FUNCTION: Bookmark.getNode(searchFromAbsoluteRoot) {{{3
" Gets the treenode for this bookmark
"
" Args:
" searchFromAbsoluteRoot: specifies whether we should search from the current
" tree root, or the highest cached node
function! s:Bookmark.getNode(searchFromAbsoluteRoot)
    let searchRoot = a:searchFromAbsoluteRoot ? s:TreeDirNode.AbsoluteTreeRoot() : b:NERDTreeRoot
    let targetNode = searchRoot.findNode(self.path)
    if empty(targetNode)
        throw "NERDTree.BookmarkedNodeNotFoundError: no node was found for bookmark: " . self.name
    endif
    return targetNode
endfunction
" FUNCTION: Bookmark.GetNodeForName(name, searchFromAbsoluteRoot) {{{3
" Class method that finds the bookmark with the given name and returns the
" treenode for it.
function! s:Bookmark.GetNodeForName(name, searchFromAbsoluteRoot)
    let bookmark = s:Bookmark.BookmarkFor(a:name)
    return bookmark.getNode(a:searchFromAbsoluteRoot)
endfunction
" FUNCTION: Bookmark.GetSelected() {{{3
" returns the Bookmark the cursor is over, or {}
function! s:Bookmark.GetSelected()
    let line = getline(".")
    let name = substitute(line, '^>\(.\{-}\) .\+$', '\1', '')
    if name != line
        try
            return s:Bookmark.BookmarkFor(name)
        catch /^NERDTree.BookmarkNotFoundError/
            return {}
        endtry
    endif
    return {}
endfunction

" Function: Bookmark.InvalidBookmarks()   {{{3
" Class method to get all invalid bookmark strings read from the bookmarks
" file
function! s:Bookmark.InvalidBookmarks()
    if !exists("g:NERDTreeInvalidBookmarks")
        let g:NERDTreeInvalidBookmarks = []
    endif
    return g:NERDTreeInvalidBookmarks
endfunction
" FUNCTION: Bookmark.mustExist() {{{3
function! s:Bookmark.mustExist()
    if !self.path.exists()
        call s:Bookmark.CacheBookmarks(1)
        throw "NERDTree.BookmarkPointsToInvalidLocationError: the bookmark \"".
            \ self.name ."\" points to a non existing location: \"". self.path.str()
    endif
endfunction
" FUNCTION: Bookmark.New(name, path) {{{3
" Create a new bookmark object with the given name and path object
function! s:Bookmark.New(name, path)
    if a:name =~ ' '
        throw "NERDTree.IllegalBookmarkNameError: illegal name:" . a:name
    endif

    let newBookmark = copy(self)
    let newBookmark.name = a:name
    let newBookmark.path = a:path
    return newBookmark
endfunction
" FUNCTION: Bookmark.openInNewTab(options) {{{3
" Create a new bookmark object with the given name and path object
function! s:Bookmark.openInNewTab(options)
    let currentTab = tabpagenr()
    if self.path.isDirectory
        tabnew
        call s:initNerdTree(self.name)
    else
        exec "tabedit " . bookmark.path.str({'format': 'Edit'})
    endif

    if has_key(a:options, 'stayInCurrentTab')
        exec "tabnext " . currentTab
    endif
endfunction
" Function: Bookmark.setPath(path)   {{{3
" makes this bookmark point to the given path
function! s:Bookmark.setPath(path)
    let self.path = a:path
endfunction
" Function: Bookmark.Sort()   {{{3
" Class method that sorts all bookmarks
function! s:Bookmark.Sort()
    let CompareFunc = function("s:compareBookmarks")
    call sort(s:Bookmark.Bookmarks(), CompareFunc)
endfunction
" Function: Bookmark.str()   {{{3
" Get the string that should be rendered in the view for this bookmark
function! s:Bookmark.str()
    let pathStrMaxLen = winwidth(s:getTreeWinNum()) - 4 - len(self.name)
    if &nu
        let pathStrMaxLen = pathStrMaxLen - &numberwidth
    endif

    let pathStr = self.path.str({'format': 'UI'})
    if len(pathStr) > pathStrMaxLen
        let pathStr = '<' . strpart(pathStr, len(pathStr) - pathStrMaxLen)
    endif
    return '>' . self.name . ' ' . pathStr
endfunction
" FUNCTION: Bookmark.toRoot() {{{3
" Make the node for this bookmark the new tree root
function! s:Bookmark.toRoot()
    if self.validate()
        try
            let targetNode = self.getNode(1)
        catch /^NERDTree.BookmarkedNodeNotFoundError/
            let targetNode = s:TreeFileNode.New(s:Bookmark.BookmarkFor(self.name).path)
        endtry
        call targetNode.makeRoot()
        call s:renderView()
        call targetNode.putCursorHere(0, 0)
    endif
endfunction
" FUNCTION: Bookmark.ToRoot(name) {{{3
" Make the node for this bookmark the new tree root
function! s:Bookmark.ToRoot(name)
    let bookmark = s:Bookmark.BookmarkFor(a:name)
    call bookmark.toRoot()
endfunction


"FUNCTION: Bookmark.validate() {{{3
function! s:Bookmark.validate()
    if self.path.exists()
        return 1
    else
        call s:Bookmark.CacheBookmarks(1)
        call s:renderView()
        call s:echo(self.name . "now points to an invalid location. See :help NERDTreeInvalidBookmarks for info.")
        return 0
    endif
endfunction

" Function: Bookmark.Write()   {{{3
" Class method to write all bookmarks to the bookmarks file
function! s:Bookmark.Write()
    let bookmarkStrings = []
    for i in s:Bookmark.Bookmarks()
        call add(bookmarkStrings, i.name . ' ' . i.path.str())
    endfor

    "add a blank line before the invalid ones
    call add(bookmarkStrings, "")

    for j in s:Bookmark.InvalidBookmarks()
        call add(bookmarkStrings, j)
    endfor
    call writefile(bookmarkStrings, g:NERDTreeBookmarksFile)
endfunction
"CLASS: KeyMap {{{2
"============================================================
let s:KeyMap = {}
"FUNCTION: KeyMap.All() {{{3
function! s:KeyMap.All()
    if !exists("s:keyMaps")
        let s:keyMaps = []
    endif
    return s:keyMaps
endfunction

"FUNCTION: KeyMap.BindAll() {{{3
function! s:KeyMap.BindAll()
    for i in s:KeyMap.All()
        call i.bind()
    endfor
endfunction

"FUNCTION: KeyMap.bind() {{{3
function! s:KeyMap.bind()
    exec "nnoremap <silent> <buffer> ". self.key ." :call ". self.callback ."()<cr>"
endfunction

"FUNCTION: KeyMap.Create(options) {{{3
function! s:KeyMap.Create(options)
    let newKeyMap = copy(self)
    let newKeyMap.key = a:options['key']
    let newKeyMap.quickhelpText = a:options['quickhelpText']
    let newKeyMap.callback = a:options['callback']
    call add(s:KeyMap.All(), newKeyMap)
endfunction
"CLASS: MenuController {{{2
"============================================================
let s:MenuController = {}
"FUNCTION: MenuController.New(menuItems) {{{3
"create a new menu controller that operates on the given menu items
function! s:MenuController.New(menuItems)
    let newMenuController =  copy(self)
    if a:menuItems[0].isSeparator()
        let newMenuController.menuItems = a:menuItems[1:-1]
    else
        let newMenuController.menuItems = a:menuItems
    endif
    return newMenuController
endfunction

"FUNCTION: MenuController.showMenu() {{{3
"start the main loop of the menu and get the user to choose/execute a menu
"item
function! s:MenuController.showMenu()
    call self._saveOptions()

    try
        let self.selection = 0

        let done = 0
        while !done
            redraw!
            call self._echoPrompt()
            let key = nr2char(getchar())
            let done = self._handleKeypress(key)
        endwhile
    finally
        call self._restoreOptions()
    endtry

    if self.selection != -1
        let m = self._current()
        call m.execute()
    endif
endfunction

"FUNCTION: MenuController._echoPrompt() {{{3
function! s:MenuController._echoPrompt()
    echo "NERDTree Menu. Use j/k/enter and the shortcuts indicated"
    echo "=========================================================="

    for i in range(0, len(self.menuItems)-1)
        if self.selection == i
            echo "> " . self.menuItems[i].text
        else
            echo "  " . self.menuItems[i].text
        endif
    endfor
endfunction

"FUNCTION: MenuController._current(key) {{{3
"get the MenuItem that is curently selected
function! s:MenuController._current()
    return self.menuItems[self.selection]
endfunction

"FUNCTION: MenuController._handleKeypress(key) {{{3
"change the selection (if appropriate) and return 1 if the user has made
"their choice, 0 otherwise
function! s:MenuController._handleKeypress(key)
    if a:key == 'j'
        call self._cursorDown()
    elseif a:key == 'k'
        call self._cursorUp()
    elseif a:key == nr2char(27) "escape
        let self.selection = -1
        return 1
    elseif a:key == "\r" || a:key == "\n" "enter and ctrl-j
        return 1
    else
        let index = self._nextIndexFor(a:key)
        if index != -1
            let self.selection = index
            if len(self._allIndexesFor(a:key)) == 1
                return 1
            endif
        endif
    endif

    return 0
endfunction

"FUNCTION: MenuController._allIndexesFor(shortcut) {{{3
"get indexes to all menu items with the given shortcut
function! s:MenuController._allIndexesFor(shortcut)
    let toReturn = []

    for i in range(0, len(self.menuItems)-1)
        if self.menuItems[i].shortcut == a:shortcut
            call add(toReturn, i)
        endif
    endfor

    return toReturn
endfunction

"FUNCTION: MenuController._nextIndexFor(shortcut) {{{3
"get the index to the next menu item with the given shortcut, starts from the
"current cursor location and wraps around to the top again if need be
function! s:MenuController._nextIndexFor(shortcut)
    for i in range(self.selection+1, len(self.menuItems)-1)
        if self.menuItems[i].shortcut == a:shortcut
            return i
        endif
    endfor

    for i in range(0, self.selection)
        if self.menuItems[i].shortcut == a:shortcut
            return i
        endif
    endfor

    return -1
endfunction

"FUNCTION: MenuController._setCmdheight() {{{3
"sets &cmdheight to whatever is needed to display the menu
function! s:MenuController._setCmdheight()
    let &cmdheight = len(self.menuItems) + 3
endfunction

"FUNCTION: MenuController._saveOptions() {{{3
"set any vim options that are required to make the menu work (saving their old
"values)
function! s:MenuController._saveOptions()
    let self._oldLazyredraw = &lazyredraw
    let self._oldCmdheight = &cmdheight
    set nolazyredraw
    call self._setCmdheight()
endfunction

"FUNCTION: MenuController._restoreOptions() {{{3
"restore the options we saved in _saveOptions()
function! s:MenuController._restoreOptions()
    let &cmdheight = self._oldCmdheight
    let &lazyredraw = self._oldLazyredraw
endfunction

"FUNCTION: MenuController._cursorDown() {{{3
"move the cursor to the next menu item, skipping separators
function! s:MenuController._cursorDown()
    let done = 0
    while !done
        if self.selection < len(self.menuItems)-1
            let self.selection += 1
        else
            let self.selection = 0
        endif

        if !self._current().isSeparator()
            let done = 1
        endif
    endwhile
endfunction

"FUNCTION: MenuController._cursorUp() {{{3
"move the cursor to the previous menu item, skipping separators
function! s:MenuController._cursorUp()
    let done = 0
    while !done
        if self.selection > 0
            let self.selection -= 1
        else
            let self.selection = len(self.menuItems)-1
        endif

        if !self._current().isSeparator()
            let done = 1
        endif
    endwhile
endfunction

"CLASS: MenuItem {{{2
"============================================================
let s:MenuItem = {}
"FUNCTION: MenuItem.All() {{{3
"get all top level menu items
function! s:MenuItem.All()
    if !exists("s:menuItems")
        let s:menuItems = []
    endif
    return s:menuItems
endfunction

"FUNCTION: MenuItem.AllEnabled() {{{3
"get all top level menu items that are currently enabled
function! s:MenuItem.AllEnabled()
    let toReturn = []
    for i in s:MenuItem.All()
        if i.enabled()
            call add(toReturn, i)
        endif
    endfor
    return toReturn
endfunction

"FUNCTION: MenuItem.Create(options) {{{3
"make a new menu item and add it to the global list
function! s:MenuItem.Create(options)
    let newMenuItem = copy(self)

    let newMenuItem.text = a:options['text']
    let newMenuItem.shortcut = a:options['shortcut']
    let newMenuItem.children = []

    let newMenuItem.isActiveCallback = -1
    if has_key(a:options, 'isActiveCallback')
        let newMenuItem.isActiveCallback = a:options['isActiveCallback']
    endif

    let newMenuItem.callback = -1
    if has_key(a:options, 'callback')
        let newMenuItem.callback = a:options['callback']
    endif

    if has_key(a:options, 'parent')
        call add(a:options['parent'].children, newMenuItem)
    else
        call add(s:MenuItem.All(), newMenuItem)
    endif

    return newMenuItem
endfunction

"FUNCTION: MenuItem.CreateSeparator(options) {{{3
"make a new separator menu item and add it to the global list
function! s:MenuItem.CreateSeparator(options)
    let standard_options = { 'text': '--------------------',
                \ 'shortcut': -1,
                \ 'callback': -1 }
    let options = extend(a:options, standard_options, "force")

    return s:MenuItem.Create(options)
endfunction

"FUNCTION: MenuItem.CreateSubmenu(options) {{{3
"make a new submenu and add it to global list
function! s:MenuItem.CreateSubmenu(options)
    let standard_options = { 'callback': -1 }
    let options = extend(a:options, standard_options, "force")

    return s:MenuItem.Create(options)
endfunction

"FUNCTION: MenuItem.enabled() {{{3
"return 1 if this menu item should be displayed
"
"delegates off to the isActiveCallback, and defaults to 1 if no callback was
"specified
function! s:MenuItem.enabled()
    if self.isActiveCallback != -1
        return {self.isActiveCallback}()
    endif
    return 1
endfunction

"FUNCTION: MenuItem.execute() {{{3
"perform the action behind this menu item, if this menuitem has children then
"display a new menu for them, otherwise deletegate off to the menuitem's
"callback
function! s:MenuItem.execute()
    if len(self.children)
        let mc = s:MenuController.New(self.children)
        call mc.showMenu()
    else
        if self.callback != -1
            call {self.callback}()
        endif
    endif
endfunction

"FUNCTION: MenuItem.isSeparator() {{{3
"return 1 if this menuitem is a separator
function! s:MenuItem.isSeparator()
    return self.callback == -1 && self.children == []
endfunction

"FUNCTION: MenuItem.isSubmenu() {{{3
"return 1 if this menuitem is a submenu
function! s:MenuItem.isSubmenu()
    return self.callback == -1 && !empty(self.children)
endfunction

"CLASS: TreeFileNode {{{2
"This class is the parent of the TreeDirNode class and constitures the
"'Component' part of the composite design pattern between the treenode
"classes.
"============================================================
let s:TreeFileNode = {}
"FUNCTION: TreeFileNode.activate(forceKeepWinOpen) {{{3
function! s:TreeFileNode.activate(forceKeepWinOpen)
    call self.open()
    if !a:forceKeepWinOpen
        call s:closeTreeIfQuitOnOpen()
    end
endfunction
"FUNCTION: TreeFileNode.bookmark(name) {{{3
"bookmark this node with a:name
function! s:TreeFileNode.bookmark(name)
    try
        let oldMarkedNode = s:Bookmark.GetNodeForName(a:name, 1)
        call oldMarkedNode.path.cacheDisplayString()
    catch /^NERDTree.BookmarkNotFoundError/
    endtry

    call s:Bookmark.AddBookmark(a:name, self.path)
    call self.path.cacheDisplayString()
    call s:Bookmark.Write()
endfunction
"FUNCTION: TreeFileNode.cacheParent() {{{3
"initializes self.parent if it isnt already
function! s:TreeFileNode.cacheParent()
    if empty(self.parent)
        let parentPath = self.path.getParent()
        if parentPath.equals(self.path)
            throw "NERDTree.CannotCacheParentError: already at root"
        endif
        let self.parent = s:TreeFileNode.New(parentPath)
    endif
endfunction
"FUNCTION: TreeFileNode.compareNodes {{{3
"This is supposed to be a class level method but i cant figure out how to
"get func refs to work from a dict..
"
"A class level method that compares two nodes
"
"Args:
"n1, n2: the 2 nodes to compare
function! s:compareNodes(n1, n2)
    return a:n1.path.compareTo(a:n2.path)
endfunction

"FUNCTION: TreeFileNode.clearBoomarks() {{{3
function! s:TreeFileNode.clearBoomarks()
    for i in s:Bookmark.Bookmarks()
        if i.path.equals(self.path)
            call i.delete()
        end
    endfor
    call self.path.cacheDisplayString()
endfunction
"FUNCTION: TreeFileNode.copy(dest) {{{3
function! s:TreeFileNode.copy(dest)
    call self.path.copy(a:dest)
    let newPath = s:Path.New(a:dest)
    let parent = b:NERDTreeRoot.findNode(newPath.getParent())
    if !empty(parent)
        call parent.refresh()
    endif
    return parent.findNode(newPath)
endfunction

"FUNCTION: TreeFileNode.delete {{{3
"Removes this node from the tree and calls the Delete method for its path obj
function! s:TreeFileNode.delete()
    call self.path.delete()
    call self.parent.removeChild(self)
endfunction

"FUNCTION: TreeFileNode.displayString() {{{3
"
"Returns a string that specifies how the node should be represented as a
"string
"
"Return:
"a string that can be used in the view to represent this node
function! s:TreeFileNode.displayString()
    return self.path.displayString()
endfunction

"FUNCTION: TreeFileNode.equals(treenode) {{{3
"
"Compares this treenode to the input treenode and returns 1 if they are the
"same node.
"
"Use this method instead of ==  because sometimes when the treenodes contain
"many children, vim seg faults when doing ==
"
"Args:
"treenode: the other treenode to compare to
function! s:TreeFileNode.equals(treenode)
    return self.path.str() ==# a:treenode.path.str()
endfunction

"FUNCTION: TreeFileNode.findNode(path) {{{3
"Returns self if this node.path.Equals the given path.
"Returns {} if not equal.
"
"Args:
"path: the path object to compare against
function! s:TreeFileNode.findNode(path)
    if a:path.equals(self.path)
        return self
    endif
    return {}
endfunction
"FUNCTION: TreeFileNode.findOpenDirSiblingWithVisibleChildren(direction) {{{3
"
"Finds the next sibling for this node in the indicated direction. This sibling
"must be a directory and may/may not have children as specified.
"
"Args:
"direction: 0 if you want to find the previous sibling, 1 for the next sibling
"
"Return:
"a treenode object or {} if no appropriate sibling could be found
function! s:TreeFileNode.findOpenDirSiblingWithVisibleChildren(direction)
    "if we have no parent then we can have no siblings
    if self.parent != {}
        let nextSibling = self.findSibling(a:direction)

        while nextSibling != {}
            if nextSibling.path.isDirectory && nextSibling.hasVisibleChildren() && nextSibling.isOpen
                return nextSibling
            endif
            let nextSibling = nextSibling.findSibling(a:direction)
        endwhile
    endif

    return {}
endfunction
"FUNCTION: TreeFileNode.findSibling(direction) {{{3
"
"Finds the next sibling for this node in the indicated direction
"
"Args:
"direction: 0 if you want to find the previous sibling, 1 for the next sibling
"
"Return:
"a treenode object or {} if no sibling could be found
function! s:TreeFileNode.findSibling(direction)
    "if we have no parent then we can have no siblings
    if self.parent != {}

        "get the index of this node in its parents children
        let siblingIndx = self.parent.getChildIndex(self.path)

        if siblingIndx != -1
            "move a long to the next potential sibling node
            let siblingIndx = a:direction ==# 1 ? siblingIndx+1 : siblingIndx-1

            "keep moving along to the next sibling till we find one that is valid
            let numSiblings = self.parent.getChildCount()
            while siblingIndx >= 0 && siblingIndx < numSiblings

                "if the next node is not an ignored node (i.e. wont show up in the
                "view) then return it
                if self.parent.children[siblingIndx].path.ignore() ==# 0
                    return self.parent.children[siblingIndx]
                endif

                "go to next node
                let siblingIndx = a:direction ==# 1 ? siblingIndx+1 : siblingIndx-1
            endwhile
        endif
    endif

    return {}
endfunction

"FUNCTION: TreeFileNode.getLineNum(){{{3
"returns the line number this node is rendered on, or -1 if it isnt rendered
function! s:TreeFileNode.getLineNum()
    "if the node is the root then return the root line no.
    if self.isRoot()
        return s:TreeFileNode.GetRootLineNum()
    endif

    let totalLines = line("$")

    "the path components we have matched so far
    let pathcomponents = [substitute(b:NERDTreeRoot.path.str({'format': 'UI'}), '/ *$', '', '')]
    "the index of the component we are searching for
    let curPathComponent = 1

    let fullpath = self.path.str({'format': 'UI'})


    let lnum = s:TreeFileNode.GetRootLineNum()
    while lnum > 0
        let lnum = lnum + 1
        "have we reached the bottom of the tree?
        if lnum ==# totalLines+1
            return -1
        endif

        let curLine = getline(lnum)

        let indent = s:indentLevelFor(curLine)
        if indent ==# curPathComponent
            let curLine = s:stripMarkupFromLine(curLine, 1)

            let curPath =  join(pathcomponents, '/') . '/' . curLine
            if stridx(fullpath, curPath, 0) ==# 0
                if fullpath ==# curPath || strpart(fullpath, len(curPath)-1,1) ==# '/'
                    let curLine = substitute(curLine, '/ *$', '', '')
                    call add(pathcomponents, curLine)
                    let curPathComponent = curPathComponent + 1

                    if fullpath ==# curPath
                        return lnum
                    endif
                endif
            endif
        endif
    endwhile
    return -1
endfunction

"FUNCTION: TreeFileNode.GetRootForTab(){{{3
"get the root node for this tab
function! s:TreeFileNode.GetRootForTab()
    if s:treeExistsForTab()
        return getbufvar(t:NERDTreeBufName, 'NERDTreeRoot')
    end
    return {}
endfunction
"FUNCTION: TreeFileNode.GetRootLineNum(){{{3
"gets the line number of the root node
function! s:TreeFileNode.GetRootLineNum()
    let rootLine = 1
    while getline(rootLine) !~ '^\(/\|<\)'
        let rootLine = rootLine + 1
    endwhile
    return rootLine
endfunction

"FUNCTION: TreeFileNode.GetSelected() {{{3
"gets the treenode that the cursor is currently over
function! s:TreeFileNode.GetSelected()
    try
        let path = s:getPath(line("."))
        if path ==# {}
            return {}
        endif
        return b:NERDTreeRoot.findNode(path)
    catch /NERDTree/
        return {}
    endtry
endfunction
"FUNCTION: TreeFileNode.isVisible() {{{3
"returns 1 if this node should be visible according to the tree filters and
"hidden file filters (and their on/off status)
function! s:TreeFileNode.isVisible()
    return !self.path.ignore()
endfunction
"FUNCTION: TreeFileNode.isRoot() {{{3
"returns 1 if this node is b:NERDTreeRoot
function! s:TreeFileNode.isRoot()
    if !s:treeExistsForBuf()
        throw "NERDTree.NoTreeError: No tree exists for the current buffer"
    endif

    return self.equals(b:NERDTreeRoot)
endfunction

"FUNCTION: TreeFileNode.makeRoot() {{{3
"Make this node the root of the tree
function! s:TreeFileNode.makeRoot()
    if self.path.isDirectory
        let b:NERDTreeRoot = self
    else
        call self.cacheParent()
        let b:NERDTreeRoot = self.parent
    endif

    call b:NERDTreeRoot.open()

    "change dir to the dir of the new root if instructed to
    if g:NERDTreeChDirMode ==# 2
        exec "cd " . b:NERDTreeRoot.path.str({'format': 'Edit'})
    endif
endfunction
"FUNCTION: TreeFileNode.New(path) {{{3
"Returns a new TreeNode object with the given path and parent
"
"Args:
"path: a path object representing the full filesystem path to the file/dir that the node represents
function! s:TreeFileNode.New(path)
    if a:path.isDirectory
        return s:TreeDirNode.New(a:path)
    else
        let newTreeNode = copy(self)
        let newTreeNode.path = a:path
        let newTreeNode.parent = {}
        return newTreeNode
    endif
endfunction

"FUNCTION: TreeFileNode.open() {{{3
"Open the file represented by the given node in the current window, splitting
"the window if needed
"
"ARGS:
"treenode: file node to open
function! s:TreeFileNode.open()
    if b:NERDTreeType ==# "secondary"
        exec 'edit ' . self.path.str({'format': 'Edit'})
        return
    endif

    "if the file is already open in this tab then just stick the cursor in it
    let winnr = bufwinnr('^' . self.path.str() . '$')
    if winnr != -1
        call s:exec(winnr . "wincmd w")

    else
        if !s:isWindowUsable(winnr("#")) && s:firstUsableWindow() ==# -1
            call self.openSplit()
        else
            try
                if !s:isWindowUsable(winnr("#"))
                    call s:exec(s:firstUsableWindow() . "wincmd w")
                else
                    call s:exec('wincmd p')
                endif
                exec ("edit " . self.path.str({'format': 'Edit'}))
            catch /^Vim\%((\a\+)\)\=:E37/
                call s:putCursorInTreeWin()
                throw "NERDTree.FileAlreadyOpenAndModifiedError: ". self.path.str() ." is already open and modified."
            catch /^Vim\%((\a\+)\)\=:/
                echo v:exception
            endtry
        endif
    endif
endfunction
"FUNCTION: TreeFileNode.openSplit() {{{3
"Open this node in a new window
function! s:TreeFileNode.openSplit()

    if b:NERDTreeType ==# "secondary"
        exec "split " . self.path.str({'format': 'Edit'})
        return
    endif

    " Save the user's settings for splitbelow and splitright
    let savesplitbelow=&splitbelow
    let savesplitright=&splitright

    " 'there' will be set to a command to move from the split window
    " back to the explorer window
    "
    " 'back' will be set to a command to move from the explorer window
    " back to the newly split window
    "
    " 'right' and 'below' will be set to the settings needed for
    " splitbelow and splitright IF the explorer is the only window.
    "
    let there= g:NERDTreeWinPos ==# "left" ? "wincmd h" : "wincmd l"
    let back = g:NERDTreeWinPos ==# "left" ? "wincmd l" : "wincmd h"
    let right= g:NERDTreeWinPos ==# "left"
    let below=0

    " Attempt to go to adjacent window
    call s:exec(back)

    let onlyOneWin = (winnr("$") ==# 1)

    " If no adjacent window, set splitright and splitbelow appropriately
    if onlyOneWin
        let &splitright=right
        let &splitbelow=below
    else
        " found adjacent window - invert split direction
        let &splitright=!right
        let &splitbelow=!below
    endif

    let splitMode = onlyOneWin ? "vertical" : ""

    " Open the new window
    try
        exec(splitMode." sp " . self.path.str({'format': 'Edit'}))
    catch /^Vim\%((\a\+)\)\=:E37/
        call s:putCursorInTreeWin()
        throw "NERDTree.FileAlreadyOpenAndModifiedError: ". self.path.str() ." is already open and modified."
    catch /^Vim\%((\a\+)\)\=:/
        "do nothing
    endtry

    "resize the tree window if no other window was open before
    if onlyOneWin
        let size = exists("b:NERDTreeOldWindowSize") ? b:NERDTreeOldWindowSize : g:NERDTreeWinSize
        call s:exec(there)
        exec("silent ". splitMode ." resize ". size)
        call s:exec('wincmd p')
    endif

    " Restore splitmode settings
    let &splitbelow=savesplitbelow
    let &splitright=savesplitright
endfunction
"FUNCTION: TreeFileNode.openVSplit() {{{3
"Open this node in a new vertical window
function! s:TreeFileNode.openVSplit()
    if b:NERDTreeType ==# "secondary"
        exec "vnew " . self.path.str({'format': 'Edit'})
        return
    endif

    let winwidth = winwidth(".")
    if winnr("$")==#1
        let winwidth = g:NERDTreeWinSize
    endif

    call s:exec("wincmd p")
    exec "vnew " . self.path.str({'format': 'Edit'})

    "resize the nerd tree back to the original size
    call s:putCursorInTreeWin()
    exec("silent vertical resize ". winwidth)
    call s:exec('wincmd p')
endfunction
"FUNCTION: TreeFileNode.openInNewTab(options) {{{3
function! s:TreeFileNode.openInNewTab(options)
    let currentTab = tabpagenr()

    if !has_key(a:options, 'keepTreeOpen')
        call s:closeTreeIfQuitOnOpen()
    endif

    exec "tabedit " . self.path.str({'format': 'Edit'})

    if has_key(a:options, 'stayInCurrentTab') && a:options['stayInCurrentTab']
        exec "tabnext " . currentTab
    endif

endfunction
"FUNCTION: TreeFileNode.putCursorHere(isJump, recurseUpward){{{3
"Places the cursor on the line number this node is rendered on
"
"Args:
"isJump: 1 if this cursor movement should be counted as a jump by vim
"recurseUpward: try to put the cursor on the parent if the this node isnt
"visible
function! s:TreeFileNode.putCursorHere(isJump, recurseUpward)
    let ln = self.getLineNum()
    if ln != -1
        if a:isJump
            mark '
        endif
        call cursor(ln, col("."))
    else
        if a:recurseUpward
            let node = self
            while node != {} && node.getLineNum() ==# -1
                let node = node.parent
                call node.open()
            endwhile
            call s:renderView()
            call node.putCursorHere(a:isJump, 0)
        endif
    endif
endfunction

"FUNCTION: TreeFileNode.refresh() {{{3
function! s:TreeFileNode.refresh()
    call self.path.refresh()
endfunction
"FUNCTION: TreeFileNode.rename() {{{3
"Calls the rename method for this nodes path obj
function! s:TreeFileNode.rename(newName)
    let newName = substitute(a:newName, '\(\\\|\/\)$', '', '')
    call self.path.rename(newName)
    call self.parent.removeChild(self)

    let parentPath = self.path.getParent()
    let newParent = b:NERDTreeRoot.findNode(parentPath)

    if newParent != {}
        call newParent.createChild(self.path, 1)
        call newParent.refresh()
    endif
endfunction
"FUNCTION: TreeFileNode.renderToString {{{3
"returns a string representation for this tree to be rendered in the view
function! s:TreeFileNode.renderToString()
    return self._renderToString(0, 0, [], self.getChildCount() ==# 1)
endfunction


"Args:
"depth: the current depth in the tree for this call
"drawText: 1 if we should actually draw the line for this node (if 0 then the
"child nodes are rendered only)
"vertMap: a binary array that indicates whether a vertical bar should be draw
"for each depth in the tree
"isLastChild:true if this curNode is the last child of its parent
function! s:TreeFileNode._renderToString(depth, drawText, vertMap, isLastChild)
    let output = ""
    if a:drawText ==# 1

        let treeParts = ''

        "get all the leading spaces and vertical tree parts for this line
        if a:depth > 1
            for j in a:vertMap[0:-2]
                if j ==# 1
                    let treeParts = treeParts . '| '
                else
                    let treeParts = treeParts . '  '
                endif
            endfor
        endif

        "get the last vertical tree part for this line which will be different
        "if this node is the last child of its parent
        if a:isLastChild
            let treeParts = treeParts . '`'
        else
            let treeParts = treeParts . '|'
        endif


        "smack the appropriate dir/file symbol on the line before the file/dir
        "name itself
        if self.path.isDirectory
            if self.isOpen
                let treeParts = treeParts . '~'
            else
                let treeParts = treeParts . '+'
            endif
        else
            let treeParts = treeParts . '-'
        endif
        let line = treeParts . self.displayString()

        let output = output . line . "\n"
    endif

    "if the node is an open dir, draw its children
    if self.path.isDirectory ==# 1 && self.isOpen ==# 1

        let childNodesToDraw = self.getVisibleChildren()
        if len(childNodesToDraw) > 0

            "draw all the nodes children except the last
            let lastIndx = len(childNodesToDraw)-1
            if lastIndx > 0
                for i in childNodesToDraw[0:lastIndx-1]
                    let output = output . i._renderToString(a:depth + 1, 1, add(copy(a:vertMap), 1), 0)
                endfor
            endif

            "draw the last child, indicating that it IS the last
            let output = output . childNodesToDraw[lastIndx]._renderToString(a:depth + 1, 1, add(copy(a:vertMap), 0), 1)
        endif
    endif

    return output
endfunction
"CLASS: TreeDirNode {{{2
"This class is a child of the TreeFileNode class and constitutes the
"'Composite' part of the composite design pattern between the treenode
"classes.
"============================================================
let s:TreeDirNode = copy(s:TreeFileNode)
"FUNCTION: TreeDirNode.AbsoluteTreeRoot(){{{3
"class method that returns the highest cached ancestor of the current root
function! s:TreeDirNode.AbsoluteTreeRoot()
    let currentNode = b:NERDTreeRoot
    while currentNode.parent != {}
        let currentNode = currentNode.parent
    endwhile
    return currentNode
endfunction
"FUNCTION: TreeDirNode.activate(forceKeepWinOpen) {{{3
unlet s:TreeDirNode.activate
function! s:TreeDirNode.activate(forceKeepWinOpen)
    call self.toggleOpen()
    call s:renderView()
    call self.putCursorHere(0, 0)
endfunction
"FUNCTION: TreeDirNode.addChild(treenode, inOrder) {{{3
"Adds the given treenode to the list of children for this node
"
"Args:
"-treenode: the node to add
"-inOrder: 1 if the new node should be inserted in sorted order
function! s:TreeDirNode.addChild(treenode, inOrder)
    call add(self.children, a:treenode)
    let a:treenode.parent = self

    if a:inOrder
        call self.sortChildren()
    endif
endfunction

"FUNCTION: TreeDirNode.close() {{{3
"Closes this directory
function! s:TreeDirNode.close()
    let self.isOpen = 0
endfunction

"FUNCTION: TreeDirNode.closeChildren() {{{3
"Closes all the child dir nodes of this node
function! s:TreeDirNode.closeChildren()
    for i in self.children
        if i.path.isDirectory
            call i.close()
            call i.closeChildren()
        endif
    endfor
endfunction

"FUNCTION: TreeDirNode.createChild(path, inOrder) {{{3
"Instantiates a new child node for this node with the given path. The new
"nodes parent is set to this node.
"
"Args:
"path: a Path object that this node will represent/contain
"inOrder: 1 if the new node should be inserted in sorted order
"
"Returns:
"the newly created node
function! s:TreeDirNode.createChild(path, inOrder)
    let newTreeNode = s:TreeFileNode.New(a:path)
    call self.addChild(newTreeNode, a:inOrder)
    return newTreeNode
endfunction

"FUNCTION: TreeDirNode.findNode(path) {{{3
"Will find one of the children (recursively) that has the given path
"
"Args:
"path: a path object
unlet s:TreeDirNode.findNode
function! s:TreeDirNode.findNode(path)
    if a:path.equals(self.path)
        return self
    endif
    if stridx(a:path.str(), self.path.str(), 0) ==# -1
        return {}
    endif

    if self.path.isDirectory
        for i in self.children
            let retVal = i.findNode(a:path)
            if retVal != {}
                return retVal
            endif
        endfor
    endif
    return {}
endfunction
"FUNCTION: TreeDirNode.getChildCount() {{{3
"Returns the number of children this node has
function! s:TreeDirNode.getChildCount()
    return len(self.children)
endfunction

"FUNCTION: TreeDirNode.getChild(path) {{{3
"Returns child node of this node that has the given path or {} if no such node
"exists.
"
"This function doesnt not recurse into child dir nodes
"
"Args:
"path: a path object
function! s:TreeDirNode.getChild(path)
    if stridx(a:path.str(), self.path.str(), 0) ==# -1
        return {}
    endif

    let index = self.getChildIndex(a:path)
    if index ==# -1
        return {}
    else
        return self.children[index]
    endif

endfunction

"FUNCTION: TreeDirNode.getChildByIndex(indx, visible) {{{3
"returns the child at the given index
"Args:
"indx: the index to get the child from
"visible: 1 if only the visible children array should be used, 0 if all the
"children should be searched.
function! s:TreeDirNode.getChildByIndex(indx, visible)
    let array_to_search = a:visible? self.getVisibleChildren() : self.children
    if a:indx > len(array_to_search)
        throw "NERDTree.InvalidArgumentsError: Index is out of bounds."
    endif
    return array_to_search[a:indx]
endfunction

"FUNCTION: TreeDirNode.getChildIndex(path) {{{3
"Returns the index of the child node of this node that has the given path or
"-1 if no such node exists.
"
"This function doesnt not recurse into child dir nodes
"
"Args:
"path: a path object
function! s:TreeDirNode.getChildIndex(path)
    if stridx(a:path.str(), self.path.str(), 0) ==# -1
        return -1
    endif

    "do a binary search for the child
    let a = 0
    let z = self.getChildCount()
    while a < z
        let mid = (a+z)/2
        let diff = a:path.compareTo(self.children[mid].path)

        if diff ==# -1
            let z = mid
        elseif diff ==# 1
            let a = mid+1
        else
            return mid
        endif
    endwhile
    return -1
endfunction

"FUNCTION: TreeDirNode.GetSelected() {{{3
"Returns the current node if it is a dir node, or else returns the current
"nodes parent
unlet s:TreeDirNode.GetSelected
function! s:TreeDirNode.GetSelected()
    let currentDir = s:TreeFileNode.GetSelected()
    if currentDir != {} && !currentDir.isRoot()
        if currentDir.path.isDirectory ==# 0
            let currentDir = currentDir.parent
        endif
    endif
    return currentDir
endfunction
"FUNCTION: TreeDirNode.getVisibleChildCount() {{{3
"Returns the number of visible children this node has
function! s:TreeDirNode.getVisibleChildCount()
    return len(self.getVisibleChildren())
endfunction

"FUNCTION: TreeDirNode.getVisibleChildren() {{{3
"Returns a list of children to display for this node, in the correct order
"
"Return:
"an array of treenodes
function! s:TreeDirNode.getVisibleChildren()
    let toReturn = []
    for i in self.children
        if i.path.ignore() ==# 0
            call add(toReturn, i)
        endif
    endfor
    return toReturn
endfunction

"FUNCTION: TreeDirNode.hasVisibleChildren() {{{3
"returns 1 if this node has any childre, 0 otherwise..
function! s:TreeDirNode.hasVisibleChildren()
    return self.getVisibleChildCount() != 0
endfunction

"FUNCTION: TreeDirNode._initChildren() {{{3
"Removes all childen from this node and re-reads them
"
"Args:
"silent: 1 if the function should not echo any "please wait" messages for
"large directories
"
"Return: the number of child nodes read
function! s:TreeDirNode._initChildren(silent)
    "remove all the current child nodes
    let self.children = []

    "get an array of all the files in the nodes dir
    let dir = self.path
    let globDir = dir.str({'format': 'Glob'})
    let filesStr = globpath(globDir, '*') . "\n" . globpath(globDir, '.*')
    let files = split(filesStr, "\n")

    if !a:silent && len(files) > g:NERDTreeNotificationThreshold
        call s:echo("Please wait, caching a large dir ...")
    endif

    let invalidFilesFound = 0
    for i in files

        "filter out the .. and . directories
        "Note: we must match .. AND ../ cos sometimes the globpath returns
        "../ for path with strange chars (eg $)
        if i !~ '\/\.\.\/\?$' && i !~ '\/\.\/\?$'

            "put the next file in a new node and attach it
            try
                let path = s:Path.New(i)
                call self.createChild(path, 0)
            catch /^NERDTree.\(InvalidArguments\|InvalidFiletype\)Error/
                let invalidFilesFound += 1
            endtry
        endif
    endfor

    call self.sortChildren()

    if !a:silent && len(files) > g:NERDTreeNotificationThreshold
        call s:echo("Please wait, caching a large dir ... DONE (". self.getChildCount() ." nodes cached).")
    endif

    if invalidFilesFound
        call s:echoWarning(invalidFilesFound . " file(s) could not be loaded into the NERD tree")
    endif
    return self.getChildCount()
endfunction
"FUNCTION: TreeDirNode.New(path) {{{3
"Returns a new TreeNode object with the given path and parent
"
"Args:
"path: a path object representing the full filesystem path to the file/dir that the node represents
unlet s:TreeDirNode.New
function! s:TreeDirNode.New(path)
    if a:path.isDirectory != 1
        throw "NERDTree.InvalidArgumentsError: A TreeDirNode object must be instantiated with a directory Path object."
    endif

    let newTreeNode = copy(self)
    let newTreeNode.path = a:path

    let newTreeNode.isOpen = 0
    let newTreeNode.children = []

    let newTreeNode.parent = {}

    return newTreeNode
endfunction
"FUNCTION: TreeDirNode.open() {{{3
"Reads in all this nodes children
"
"Return: the number of child nodes read
unlet s:TreeDirNode.open
function! s:TreeDirNode.open()
    let self.isOpen = 1
    if self.children ==# []
        return self._initChildren(0)
    else
        return 0
    endif
endfunction

" FUNCTION: TreeDirNode.openExplorer() {{{3
" opens an explorer window for this node in the previous window (could be a
" nerd tree or a netrw)
function! s:TreeDirNode.openExplorer()
    let oldwin = winnr()
    call s:exec('wincmd p')
    if oldwin ==# winnr() || (&modified && s:bufInWindows(winbufnr(winnr())) < 2)
        call s:exec('wincmd p')
        call self.openSplit()
    else
        exec ("silent edit " . self.path.str({'format': 'Edit'}))
    endif
endfunction
"FUNCTION: TreeDirNode.openInNewTab(options) {{{3
unlet s:TreeDirNode.openInNewTab
function! s:TreeDirNode.openInNewTab(options)
    let currentTab = tabpagenr()

    if !has_key(a:options, 'keepTreeOpen') || !a:options['keepTreeOpen']
        call s:closeTreeIfQuitOnOpen()
    endif

    tabnew
    call s:initNerdTree(self.path.str())

    if has_key(a:options, 'stayInCurrentTab') && a:options['stayInCurrentTab']
        exec "tabnext " . currentTab
    endif
endfunction
"FUNCTION: TreeDirNode.openRecursively() {{{3
"Opens this treenode and all of its children whose paths arent 'ignored'
"because of the file filters.
"
"This method is actually a wrapper for the OpenRecursively2 method which does
"the work.
function! s:TreeDirNode.openRecursively()
    call self._openRecursively2(1)
endfunction

"FUNCTION: TreeDirNode._openRecursively2() {{{3
"Opens this all children of this treenode recursively if either:
"   *they arent filtered by file filters
"   *a:forceOpen is 1
"
"Args:
"forceOpen: 1 if this node should be opened regardless of file filters
function! s:TreeDirNode._openRecursively2(forceOpen)
    if self.path.ignore() ==# 0 || a:forceOpen
        let self.isOpen = 1
        if self.children ==# []
            call self._initChildren(1)
        endif

        for i in self.children
            if i.path.isDirectory ==# 1
                call i._openRecursively2(0)
            endif
        endfor
    endif
endfunction

"FUNCTION: TreeDirNode.refresh() {{{3
unlet s:TreeDirNode.refresh
function! s:TreeDirNode.refresh()
    call self.path.refresh()

    "if this node was ever opened, refresh its children
    if self.isOpen || !empty(self.children)
        "go thru all the files/dirs under this node
        let newChildNodes = []
        let invalidFilesFound = 0
        let dir = self.path
        let globDir = dir.str({'format': 'Glob'})
        let filesStr = globpath(globDir, '*') . "\n" . globpath(globDir, '.*')
        let files = split(filesStr, "\n")
        for i in files
            "filter out the .. and . directories
            "Note: we must match .. AND ../ cos sometimes the globpath returns
            "../ for path with strange chars (eg $)
            if i !~ '\/\.\.\/\?$' && i !~ '\/\.\/\?$'

                try
                    "create a new path and see if it exists in this nodes children
                    let path = s:Path.New(i)
                    let newNode = self.getChild(path)
                    if newNode != {}
                        call newNode.refresh()
                        call add(newChildNodes, newNode)

                    "the node doesnt exist so create it
                    else
                        let newNode = s:TreeFileNode.New(path)
                        let newNode.parent = self
                        call add(newChildNodes, newNode)
                    endif


                catch /^NERDTree.InvalidArgumentsError/
                    let invalidFilesFound = 1
                endtry
            endif
        endfor

        "swap this nodes children out for the children we just read/refreshed
        let self.children = newChildNodes
        call self.sortChildren()

        if invalidFilesFound
            call s:echoWarning("some files could not be loaded into the NERD tree")
        endif
    endif
endfunction

"FUNCTION: TreeDirNode.reveal(path) {{{3
"reveal the given path, i.e. cache and open all treenodes needed to display it
"in the UI
function! s:TreeDirNode.reveal(path)
    if !a:path.isUnder(self.path)
        throw "NERDTree.InvalidArgumentsError: " . a:path.str() . " should be under " . self.path.str()
    endif

    call self.open()

    if self.path.equals(a:path.getParent())
        let n = self.findNode(a:path)
        call s:renderView()
        call n.putCursorHere(1,0)
        return
    endif

    let p = a:path
    while !p.getParent().equals(self.path)
        let p = p.getParent()
    endwhile

    let n = self.findNode(p)
    call n.reveal(a:path)
endfunction
"FUNCTION: TreeDirNode.removeChild(treenode) {{{3
"
"Removes the given treenode from this nodes set of children
"
"Args:
"treenode: the node to remove
"
"Throws a NERDTree.ChildNotFoundError if the given treenode is not found
function! s:TreeDirNode.removeChild(treenode)
    for i in range(0, self.getChildCount()-1)
        if self.children[i].equals(a:treenode)
            call remove(self.children, i)
            return
        endif
    endfor

    throw "NERDTree.ChildNotFoundError: child node was not found"
endfunction

"FUNCTION: TreeDirNode.sortChildren() {{{3
"
"Sorts the children of this node according to alphabetical order and the
"directory priority.
"
function! s:TreeDirNode.sortChildren()
    let CompareFunc = function("s:compareNodes")
    call sort(self.children, CompareFunc)
endfunction

"FUNCTION: TreeDirNode.toggleOpen() {{{3
"Opens this directory if it is closed and vice versa
function! s:TreeDirNode.toggleOpen()
    if self.isOpen ==# 1
        call self.close()
    else
        call self.open()
    endif
endfunction

"FUNCTION: TreeDirNode.transplantChild(newNode) {{{3
"Replaces the child of this with the given node (where the child node's full
"path matches a:newNode's fullpath). The search for the matching node is
"non-recursive
"
"Arg:
"newNode: the node to graft into the tree
function! s:TreeDirNode.transplantChild(newNode)
    for i in range(0, self.getChildCount()-1)
        if self.children[i].equals(a:newNode)
            let self.children[i] = a:newNode
            let a:newNode.parent = self
            break
        endif
    endfor
endfunction
"============================================================
"CLASS: Path {{{2
"============================================================
let s:Path = {}
"FUNCTION: Path.AbsolutePathFor(str) {{{3
function! s:Path.AbsolutePathFor(str)
    let prependCWD = 0
    if s:running_windows
        let prependCWD = a:str !~ '^.:\(\\\|\/\)'
    else
        let prependCWD = a:str !~ '^/'
    endif

    let toReturn = a:str
    if prependCWD
        let toReturn = getcwd() . s:Path.Slash() . a:str
    endif

    return toReturn
endfunction
"FUNCTION: Path.bookmarkNames() {{{3
function! s:Path.bookmarkNames()
    if !exists("self._bookmarkNames")
        call self.cacheDisplayString()
    endif
    return self._bookmarkNames
endfunction
"FUNCTION: Path.cacheDisplayString() {{{3
function! s:Path.cacheDisplayString()
    let self.cachedDisplayString = self.getLastPathComponent(1)

    if self.isExecutable
        let self.cachedDisplayString = self.cachedDisplayString . '*'
    endif

    let self._bookmarkNames = []
    for i in s:Bookmark.Bookmarks()
        if i.path.equals(self)
            call add(self._bookmarkNames, i.name)
        endif
    endfor
    if !empty(self._bookmarkNames)
        let self.cachedDisplayString .= ' {' . join(self._bookmarkNames) . '}'
    endif

    if self.isSymLink
        let self.cachedDisplayString .=  ' -> ' . self.symLinkDest
    endif

    if self.isReadOnly
        let self.cachedDisplayString .=  ' [RO]'
    endif
endfunction
"FUNCTION: Path.changeToDir() {{{3
function! s:Path.changeToDir()
    let dir = self.str({'format': 'Cd'})
    if self.isDirectory ==# 0
        let dir = self.getParent().str({'format': 'Cd'})
    endif

    try
        execute "cd " . dir
        call s:echo("CWD is now: " . getcwd())
    catch
        throw "NERDTree.PathChangeError: cannot change CWD to " . dir
    endtry
endfunction

"FUNCTION: Path.compareTo() {{{3
"
"Compares this Path to the given path and returns 0 if they are equal, -1 if
"this Path is "less than" the given path, or 1 if it is "greater".
"
"Args:
"path: the path object to compare this to
"
"Return:
"1, -1 or 0
function! s:Path.compareTo(path)
    let thisPath = self.getLastPathComponent(1)
    let thatPath = a:path.getLastPathComponent(1)

    "if the paths are the same then clearly we return 0
    if thisPath ==# thatPath
        return 0
    endif

    let thisSS = self.getSortOrderIndex()
    let thatSS = a:path.getSortOrderIndex()

    "compare the sort sequences, if they are different then the return
    "value is easy
    if thisSS < thatSS
        return -1
    elseif thisSS > thatSS
        return 1
    else
        "if the sort sequences are the same then compare the paths
        "alphabetically
        let pathCompare = g:NERDTreeCaseSensitiveSort ? thisPath <# thatPath : thisPath <? thatPath
        if pathCompare
            return -1
        else
            return 1
        endif
    endif
endfunction

"FUNCTION: Path.Create(fullpath) {{{3
"
"Factory method.
"
"Creates a path object with the given path. The path is also created on the
"filesystem. If the path already exists, a NERDTree.Path.Exists exception is
"thrown. If any other errors occur, a NERDTree.Path exception is thrown.
"
"Args:
"fullpath: the full filesystem path to the file/dir to create
function! s:Path.Create(fullpath)
    "bail if the a:fullpath already exists
    if isdirectory(a:fullpath) || filereadable(a:fullpath)
        throw "NERDTree.CreatePathError: Directory Exists: '" . a:fullpath . "'"
    endif

    try

        "if it ends with a slash, assume its a dir create it
        if a:fullpath =~ '\(\\\|\/\)$'
            "whack the trailing slash off the end if it exists
            let fullpath = substitute(a:fullpath, '\(\\\|\/\)$', '', '')

            call mkdir(fullpath, 'p')

        "assume its a file and create
        else
            call writefile([], a:fullpath)
        endif
    catch
        throw "NERDTree.CreatePathError: Could not create path: '" . a:fullpath . "'"
    endtry

    return s:Path.New(a:fullpath)
endfunction

"FUNCTION: Path.copy(dest) {{{3
"
"Copies the file/dir represented by this Path to the given location
"
"Args:
"dest: the location to copy this dir/file to
function! s:Path.copy(dest)
    if !s:Path.CopyingSupported()
        throw "NERDTree.CopyingNotSupportedError: Copying is not supported on this OS"
    endif

    let dest = s:Path.WinToUnixPath(a:dest)

    let cmd = g:NERDTreeCopyCmd . " " . self.str() . " " . dest
    let success = system(cmd)
    if success != 0
        throw "NERDTree.CopyError: Could not copy ''". self.str() ."'' to: '" . a:dest . "'"
    endif
endfunction

"FUNCTION: Path.CopyingSupported() {{{3
"
"returns 1 if copying is supported for this OS
function! s:Path.CopyingSupported()
    return exists('g:NERDTreeCopyCmd')
endfunction


"FUNCTION: Path.copyingWillOverwrite(dest) {{{3
"
"returns 1 if copy this path to the given location will cause files to
"overwritten
"
"Args:
"dest: the location this path will be copied to
function! s:Path.copyingWillOverwrite(dest)
    if filereadable(a:dest)
        return 1
    endif

    if isdirectory(a:dest)
        let path = s:Path.JoinPathStrings(a:dest, self.getLastPathComponent(0))
        if filereadable(path)
            return 1
        endif
    endif
endfunction

"FUNCTION: Path.delete() {{{3
"
"Deletes the file represented by this path.
"Deletion of directories is not supported
"
"Throws NERDTree.Path.Deletion exceptions
function! s:Path.delete()
    if self.isDirectory

        let cmd = g:NERDTreeRemoveDirCmd . self.str({'escape': 1})
        let success = system(cmd)

        if v:shell_error != 0
            throw "NERDTree.PathDeletionError: Could not delete directory: '" . self.str() . "'"
        endif
    else
        let success = delete(self.str())
        if success != 0
            throw "NERDTree.PathDeletionError: Could not delete file: '" . self.str() . "'"
        endif
    endif

    "delete all bookmarks for this path
    for i in self.bookmarkNames()
        let bookmark = s:Bookmark.BookmarkFor(i)
        call bookmark.delete()
    endfor
endfunction

"FUNCTION: Path.displayString() {{{3
"
"Returns a string that specifies how the path should be represented as a
"string
function! s:Path.displayString()
    if self.cachedDisplayString ==# ""
        call self.cacheDisplayString()
    endif

    return self.cachedDisplayString
endfunction
"FUNCTION: Path.extractDriveLetter(fullpath) {{{3
"
"If running windows, cache the drive letter for this path
function! s:Path.extractDriveLetter(fullpath)
    if s:running_windows
        let self.drive = substitute(a:fullpath, '\(^[a-zA-Z]:\).*', '\1', '')
    else
        let self.drive = ''
    endif

endfunction
"FUNCTION: Path.exists() {{{3
"return 1 if this path points to a location that is readable or is a directory
function! s:Path.exists()
    let p = self.str()
    return filereadable(p) || isdirectory(p)
endfunction
"FUNCTION: Path.getDir() {{{3
"
"Returns this path if it is a directory, else this paths parent.
"
"Return:
"a Path object
function! s:Path.getDir()
    if self.isDirectory
        return self
    else
        return self.getParent()
    endif
endfunction
"FUNCTION: Path.getParent() {{{3
"
"Returns a new path object for this paths parent
"
"Return:
"a new Path object
function! s:Path.getParent()
    if s:running_windows
        let path = self.drive . '\' . join(self.pathSegments[0:-2], '\')
    else
        let path = '/'. join(self.pathSegments[0:-2], '/')
    endif

    return s:Path.New(path)
endfunction
"FUNCTION: Path.getLastPathComponent(dirSlash) {{{3
"
"Gets the last part of this path.
"
"Args:
"dirSlash: if 1 then a trailing slash will be added to the returned value for
"directory nodes.
function! s:Path.getLastPathComponent(dirSlash)
    if empty(self.pathSegments)
        return ''
    endif
    let toReturn = self.pathSegments[-1]
    if a:dirSlash && self.isDirectory
        let toReturn = toReturn . '/'
    endif
    return toReturn
endfunction

"FUNCTION: Path.getSortOrderIndex() {{{3
"returns the index of the pattern in g:NERDTreeSortOrder that this path matches
function! s:Path.getSortOrderIndex()
    let i = 0
    while i < len(g:NERDTreeSortOrder)
        if  self.getLastPathComponent(1) =~ g:NERDTreeSortOrder[i]
            return i
        endif
        let i = i + 1
    endwhile
    return s:NERDTreeSortStarIndex
endfunction

"FUNCTION: Path.ignore() {{{3
"returns true if this path should be ignored
function! s:Path.ignore()
    let lastPathComponent = self.getLastPathComponent(0)

    "filter out the user specified paths to ignore
    if b:NERDTreeIgnoreEnabled
        for i in g:NERDTreeIgnore
            if lastPathComponent =~ i
                return 1
            endif
        endfor
    endif

    "dont show hidden files unless instructed to
    if b:NERDTreeShowHidden ==# 0 && lastPathComponent =~ '^\.'
        return 1
    endif

    if b:NERDTreeShowFiles ==# 0 && self.isDirectory ==# 0
        return 1
    endif

    return 0
endfunction

"FUNCTION: Path.isUnder(path) {{{3
"return 1 if this path is somewhere under the given path in the filesystem.
"
"a:path should be a dir
function! s:Path.isUnder(path)
    if a:path.isDirectory == 0
        return 0
    endif

    let this = self.str()
    let that = a:path.str()
    return stridx(this, that . s:Path.Slash()) == 0
endfunction

"FUNCTION: Path.JoinPathStrings(...) {{{3
function! s:Path.JoinPathStrings(...)
    let components = []
    for i in a:000
        let components = extend(components, split(i, '/'))
    endfor
    return '/' . join(components, '/')
endfunction

"FUNCTION: Path.equals() {{{3
"
"Determines whether 2 path objects are "equal".
"They are equal if the paths they represent are the same
"
"Args:
"path: the other path obj to compare this with
function! s:Path.equals(path)
    return self.str() ==# a:path.str()
endfunction

"FUNCTION: Path.New() {{{3
"The Constructor for the Path object
function! s:Path.New(path)
    let newPath = copy(self)

    call newPath.readInfoFromDisk(s:Path.AbsolutePathFor(a:path))

    let newPath.cachedDisplayString = ""

    return newPath
endfunction

"FUNCTION: Path.Slash() {{{3
"return the slash to use for the current OS
function! s:Path.Slash()
    return s:running_windows ? '\' : '/'
endfunction

"FUNCTION: Path.readInfoFromDisk(fullpath) {{{3
"
"
"Throws NERDTree.Path.InvalidArguments exception.
function! s:Path.readInfoFromDisk(fullpath)
    call self.extractDriveLetter(a:fullpath)

    let fullpath = s:Path.WinToUnixPath(a:fullpath)

    if getftype(fullpath) ==# "fifo"
        throw "NERDTree.InvalidFiletypeError: Cant handle FIFO files: " . a:fullpath
    endif

    let self.pathSegments = split(fullpath, '/')

    let self.isReadOnly = 0
    if isdirectory(a:fullpath)
        let self.isDirectory = 1
    elseif filereadable(a:fullpath)
        let self.isDirectory = 0
        let self.isReadOnly = filewritable(a:fullpath) ==# 0
    else
        throw "NERDTree.InvalidArgumentsError: Invalid path = " . a:fullpath
    endif

    let self.isExecutable = 0
    if !self.isDirectory
        let self.isExecutable = getfperm(a:fullpath) =~ 'x'
    endif

    "grab the last part of the path (minus the trailing slash)
    let lastPathComponent = self.getLastPathComponent(0)

    "get the path to the new node with the parent dir fully resolved
    let hardPath = resolve(self.strTrunk()) . '/' . lastPathComponent

    "if  the last part of the path is a symlink then flag it as such
    let self.isSymLink = (resolve(hardPath) != hardPath)
    if self.isSymLink
        let self.symLinkDest = resolve(fullpath)

        "if the link is a dir then slap a / on the end of its dest
        if isdirectory(self.symLinkDest)

            "we always wanna treat MS windows shortcuts as files for
            "simplicity
            if hardPath !~ '\.lnk$'

                let self.symLinkDest = self.symLinkDest . '/'
            endif
        endif
    endif
endfunction

"FUNCTION: Path.refresh() {{{3
function! s:Path.refresh()
    call self.readInfoFromDisk(self.str())
    call self.cacheDisplayString()
endfunction

"FUNCTION: Path.rename() {{{3
"
"Renames this node on the filesystem
function! s:Path.rename(newPath)
    if a:newPath ==# ''
        throw "NERDTree.InvalidArgumentsError: Invalid newPath for renaming = ". a:newPath
    endif

    let success =  rename(self.str(), a:newPath)
    if success != 0
        throw "NERDTree.PathRenameError: Could not rename: '" . self.str() . "'" . 'to:' . a:newPath
    endif
    call self.readInfoFromDisk(a:newPath)

    for i in self.bookmarkNames()
        let b = s:Bookmark.BookmarkFor(i)
        call b.setPath(copy(self))
    endfor
    call s:Bookmark.Write()
endfunction

"FUNCTION: Path.str() {{{3
"
"Returns a string representation of this Path
"
"Takes an optional dictionary param to specify how the output should be
"formatted.
"
"The dict may have the following keys:
"  'format'
"  'escape'
"  'truncateTo'
"
"The 'format' key may have a value of:
"  'Cd' - a string to be used with the :cd command
"  'Edit' - a string to be used with :e :sp :new :tabedit etc
"  'UI' - a string used in the NERD tree UI
"
"The 'escape' key, if specified will cause the output to be escaped with
"shellescape()
"
"The 'truncateTo' key causes the resulting string to be truncated to the value
"'truncateTo' maps to. A '<' char will be prepended.
function! s:Path.str(...)
    let options = a:0 ? a:1 : {}
    let toReturn = ""

    if has_key(options, 'format')
        let format = options['format']
        if has_key(self, '_strFor' . format)
            exec 'let toReturn = self._strFor' . format . '()'
        else
            raise 'NERDTree.UnknownFormatError: unknown format "'. format .'"'
        endif
    else
        let toReturn = self._str()
    endif

    if has_key(options, 'escape') && options['escape']
        let toReturn = shellescape(toReturn)
    endif

    if has_key(options, 'truncateTo')
        let limit = options['truncateTo']
        if len(toReturn) > limit
            let toReturn = "<" . strpart(toReturn, len(toReturn) - limit + 1)
        endif
    endif

    return toReturn
endfunction

"FUNCTION: Path._strForUI() {{{3
function! s:Path._strForUI()
    let toReturn = '/' . join(self.pathSegments, '/')
    if self.isDirectory && toReturn != '/'
        let toReturn  = toReturn . '/'
    endif
    return toReturn
endfunction

"FUNCTION: Path._strForCd() {{{3
"
" returns a string that can be used with :cd
function! s:Path._strForCd()
    return escape(self.str(), s:escape_chars)
endfunction
"FUNCTION: Path._strForEdit() {{{3
"
"Return: the string for this path that is suitable to be used with the :edit
"command
function! s:Path._strForEdit()
    let p = self.str({'format': 'UI'})
    let cwd = getcwd()

    if s:running_windows
        let p = tolower(self.str())
        let cwd = tolower(getcwd())
    endif

    let p = escape(p, s:escape_chars)

    let cwd = cwd . s:Path.Slash()

    "return a relative path if we can
    if stridx(p, cwd) ==# 0
        let p = strpart(p, strlen(cwd))
    endif

    if p ==# ''
        let p = '.'
    endif

    return p

endfunction
"FUNCTION: Path._strForGlob() {{{3
function! s:Path._strForGlob()
    let lead = s:Path.Slash()

    "if we are running windows then slap a drive letter on the front
    if s:running_windows
        let lead = self.drive . '\'
    endif

    let toReturn = lead . join(self.pathSegments, s:Path.Slash())

    if !s:running_windows
        let toReturn = escape(toReturn, s:escape_chars)
    endif
    return toReturn
endfunction
"FUNCTION: Path._str() {{{3
"
"Gets the string path for this path object that is appropriate for the OS.
"EG, in windows c:\foo\bar
"    in *nix  /foo/bar
function! s:Path._str()
    let lead = s:Path.Slash()

    "if we are running windows then slap a drive letter on the front
    if s:running_windows
        let lead = self.drive . '\'
    endif

    return lead . join(self.pathSegments, s:Path.Slash())
endfunction

"FUNCTION: Path.strTrunk() {{{3
"Gets the path without the last segment on the end.
function! s:Path.strTrunk()
    return self.drive . '/' . join(self.pathSegments[0:-2], '/')
endfunction

"FUNCTION: Path.WinToUnixPath(pathstr){{{3
"Takes in a windows path and returns the unix equiv
"
"A class level method
"
"Args:
"pathstr: the windows path to convert
function! s:Path.WinToUnixPath(pathstr)
    if !s:running_windows
        return a:pathstr
    endif

    let toReturn = a:pathstr

    "remove the x:\ of the front
    let toReturn = substitute(toReturn, '^.*:\(\\\|/\)\?', '/', "")

    "convert all \ chars to /
    let toReturn = substitute(toReturn, '\', '/', "g")

    return toReturn
endfunction

" SECTION: General Functions {{{1
"============================================================
"FUNCTION: s:bufInWindows(bnum){{{2
"[[STOLEN FROM VTREEEXPLORER.VIM]]
"Determine the number of windows open to this buffer number.
"Care of Yegappan Lakshman.  Thanks!
"
"Args:
"bnum: the subject buffers buffer number
function! s:bufInWindows(bnum)
    let cnt = 0
    let winnum = 1
    while 1
        let bufnum = winbufnr(winnum)
        if bufnum < 0
            break
        endif
        if bufnum ==# a:bnum
            let cnt = cnt + 1
        endif
        let winnum = winnum + 1
    endwhile

    return cnt
endfunction " >>>
"FUNCTION: s:checkForBrowse(dir) {{{2
"inits a secondary nerd tree in the current buffer if appropriate
function! s:checkForBrowse(dir)
    if a:dir != '' && isdirectory(a:dir)
        call s:initNerdTreeInPlace(a:dir)
    endif
endfunction
"FUNCTION: s:compareBookmarks(first, second) {{{2
"Compares two bookmarks
function! s:compareBookmarks(first, second)
    return a:first.compareTo(a:second)
endfunction

" FUNCTION: s:completeBookmarks(A,L,P) {{{2
" completion function for the bookmark commands
function! s:completeBookmarks(A,L,P)
    return filter(s:Bookmark.BookmarkNames(), 'v:val =~ "^' . a:A . '"')
endfunction
" FUNCTION: s:exec(cmd) {{{2
" same as :exec cmd  but eventignore=all is set for the duration
function! s:exec(cmd)
    let old_ei = &ei
    set ei=all
    exec a:cmd
    let &ei = old_ei
endfunction
" FUNCTION: s:findAndRevealPath() {{{2
function! s:findAndRevealPath()
    try
        let p = s:Path.New(expand("%"))
    catch /^NERDTree.InvalidArgumentsError/
        call s:echo("no file for the current buffer")
        return
    endtry

    if !s:treeExistsForTab()
        call s:initNerdTree(p.getParent().str())
    else
        if !p.isUnder(s:TreeFileNode.GetRootForTab().path)
            call s:initNerdTree(p.getParent().str())
        else
            if !s:isTreeOpen()
                call s:toggle("")
            endif
        endif
    endif
    call s:putCursorInTreeWin()
    call b:NERDTreeRoot.reveal(p)
endfunction
"FUNCTION: s:initNerdTree(name) {{{2
"Initialise the nerd tree for this tab. The tree will start in either the
"given directory, or the directory associated with the given bookmark
"
"Args:
"name: the name of a bookmark or a directory
function! s:initNerdTree(name)
    let path = {}
    if s:Bookmark.BookmarkExistsFor(a:name)
        let path = s:Bookmark.BookmarkFor(a:name).path
    else
        let dir = a:name ==# '' ? getcwd() : a:name

        "hack to get an absolute path if a relative path is given
        if dir =~ '^\.'
            let dir = getcwd() . s:Path.Slash() . dir
        endif
        let dir = resolve(dir)

        try
            let path = s:Path.New(dir)
        catch /^NERDTree.InvalidArgumentsError/
            call s:echo("No bookmark or directory found for: " . a:name)
            return
        endtry
    endif
    if !path.isDirectory
        let path = path.getParent()
    endif

    "if instructed to, then change the vim CWD to the dir the NERDTree is
    "inited in
    if g:NERDTreeChDirMode != 0
        call path.changeToDir()
    endif

    if s:treeExistsForTab()
        if s:isTreeOpen()
            call s:closeTree()
        endif
        unlet t:NERDTreeBufName
    endif

    let newRoot = s:TreeDirNode.New(path)
    call newRoot.open()

    call s:createTreeWin()
    let b:treeShowHelp = 0
    let b:NERDTreeIgnoreEnabled = 1
    let b:NERDTreeShowFiles = g:NERDTreeShowFiles
    let b:NERDTreeShowHidden = g:NERDTreeShowHidden
    let b:NERDTreeShowBookmarks = g:NERDTreeShowBookmarks
    let b:NERDTreeRoot = newRoot

    let b:NERDTreeType = "primary"

    call s:renderView()
    call b:NERDTreeRoot.putCursorHere(0, 0)
endfunction

"FUNCTION: s:initNerdTreeInPlace(dir) {{{2
function! s:initNerdTreeInPlace(dir)
    try
        let path = s:Path.New(a:dir)
    catch /^NERDTree.InvalidArgumentsError/
        call s:echo("Invalid directory name:" . a:name)
        return
    endtry

    "we want the directory buffer to disappear when we do the :edit below
    setlocal bufhidden=wipe

    let previousBuf = expand("#")

    "we need a unique name for each secondary tree buffer to ensure they are
    "all independent
    exec "silent edit " . s:nextBufferName()

    let b:NERDTreePreviousBuf = bufnr(previousBuf)

    let b:NERDTreeRoot = s:TreeDirNode.New(path)
    call b:NERDTreeRoot.open()

    "throwaway buffer options
    setlocal noswapfile
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal nowrap
    setlocal foldcolumn=0
    setlocal nobuflisted
    setlocal nospell
    if g:NERDTreeShowLineNumbers
        setlocal nu
    else
        setlocal nonu
    endif

    iabc <buffer>

    if g:NERDTreeHighlightCursorline
        setlocal cursorline
    endif

    call s:setupStatusline()

    let b:treeShowHelp = 0
    let b:NERDTreeIgnoreEnabled = 1
    let b:NERDTreeShowFiles = g:NERDTreeShowFiles
    let b:NERDTreeShowHidden = g:NERDTreeShowHidden
    let b:NERDTreeShowBookmarks = g:NERDTreeShowBookmarks

    let b:NERDTreeType = "secondary"

    call s:bindMappings()
    setfiletype nerdtree
    " syntax highlighting
    if has("syntax") && exists("g:syntax_on")
        call s:setupSyntaxHighlighting()
    endif

    call s:renderView()
endfunction
" FUNCTION: s:initNerdTreeMirror() {{{2
function! s:initNerdTreeMirror()

    "get the names off all the nerd tree buffers
    let treeBufNames = []
    for i in range(1, tabpagenr("$"))
        let nextName = s:tabpagevar(i, 'NERDTreeBufName')
        if nextName != -1 && (!exists("t:NERDTreeBufName") || nextName != t:NERDTreeBufName)
            call add(treeBufNames, nextName)
        endif
    endfor
    let treeBufNames = s:unique(treeBufNames)

    "map the option names (that the user will be prompted with) to the nerd
    "tree buffer names
    let options = {}
    let i = 0
    while i < len(treeBufNames)
        let bufName = treeBufNames[i]
        let treeRoot = getbufvar(bufName, "NERDTreeRoot")
        let options[i+1 . '. ' . treeRoot.path.str() . '  (buf name: ' . bufName . ')'] = bufName
        let i = i + 1
    endwhile

    "work out which tree to mirror, if there is more than 1 then ask the user
    let bufferName = ''
    if len(keys(options)) > 1
        let choices = ["Choose a tree to mirror"]
        let choices = extend(choices, sort(keys(options)))
        let choice = inputlist(choices)
        if choice < 1 || choice > len(options) || choice ==# ''
            return
        endif

        let bufferName = options[sort(keys(options))[choice-1]]
    elseif len(keys(options)) ==# 1
        let bufferName = values(options)[0]
    else
        call s:echo("No trees to mirror")
        return
    endif

    if s:treeExistsForTab() && s:isTreeOpen()
        call s:closeTree()
    endif

    let t:NERDTreeBufName = bufferName
    call s:createTreeWin()
    exec 'buffer ' .  bufferName
    if !&hidden
        call s:renderView()
    endif
endfunction
" FUNCTION: s:nextBufferName() {{{2
" returns the buffer name for the next nerd tree
function! s:nextBufferName()
    let name = s:NERDTreeBufName . s:next_buffer_number
    let s:next_buffer_number += 1
    return name
endfunction
" FUNCTION: s:tabpagevar(tabnr, var) {{{2
function! s:tabpagevar(tabnr, var)
    let currentTab = tabpagenr()
    let old_ei = &ei
    set ei=all

    exec "tabnext " . a:tabnr
    let v = -1
    if exists('t:' . a:var)
        exec 'let v = t:' . a:var
    endif
    exec "tabnext " . currentTab

    let &ei = old_ei

    return v
endfunction
" Function: s:treeExistsForBuffer()   {{{2
" Returns 1 if a nerd tree root exists in the current buffer
function! s:treeExistsForBuf()
    return exists("b:NERDTreeRoot")
endfunction
" Function: s:treeExistsForTab()   {{{2
" Returns 1 if a nerd tree root exists in the current tab
function! s:treeExistsForTab()
    return exists("t:NERDTreeBufName")
endfunction
" Function: s:unique(list)   {{{2
" returns a:list without duplicates
function! s:unique(list)
  let uniqlist = []
  for elem in a:list
    if index(uniqlist, elem) ==# -1
      let uniqlist += [elem]
    endif
  endfor
  return uniqlist
endfunction
" SECTION: Public API {{{1
"============================================================
let g:NERDTreePath = s:Path
let g:NERDTreeDirNode = s:TreeDirNode
let g:NERDTreeFileNode = s:TreeFileNode
let g:NERDTreeBookmark = s:Bookmark

function! NERDTreeAddMenuItem(options)
    call s:MenuItem.Create(a:options)
endfunction

function! NERDTreeAddMenuSeparator(...)
    let opts = a:0 ? a:1 : {}
    call s:MenuItem.CreateSeparator(opts)
endfunction

function! NERDTreeAddSubmenu(options)
    return s:MenuItem.Create(a:options)
endfunction

function! NERDTreeAddKeyMap(options)
    call s:KeyMap.Create(a:options)
endfunction

function! NERDTreeRender()
    call s:renderView()
endfunction

" SECTION: View Functions {{{1
"============================================================
"FUNCTION: s:centerView() {{{2
"centers the nerd tree window around the cursor (provided the nerd tree
"options permit)
function! s:centerView()
    if g:NERDTreeAutoCenter
        let current_line = winline()
        let lines_to_top = current_line
        let lines_to_bottom = winheight(s:getTreeWinNum()) - current_line
        if lines_to_top < g:NERDTreeAutoCenterThreshold || lines_to_bottom < g:NERDTreeAutoCenterThreshold
            normal! zz
        endif
    endif
endfunction
"FUNCTION: s:closeTree() {{{2
"Closes the primary NERD tree window for this tab
function! s:closeTree()
    if !s:isTreeOpen()
        throw "NERDTree.NoTreeFoundError: no NERDTree is open"
    endif

    if winnr("$") != 1
        call s:exec(s:getTreeWinNum() . " wincmd w")
        close
        call s:exec("wincmd p")
    else
        close
    endif
endfunction

"FUNCTION: s:closeTreeIfOpen() {{{2
"Closes the NERD tree window if it is open
function! s:closeTreeIfOpen()
   if s:isTreeOpen()
      call s:closeTree()
   endif
endfunction
"FUNCTION: s:closeTreeIfQuitOnOpen() {{{2
"Closes the NERD tree window if the close on open option is set
function! s:closeTreeIfQuitOnOpen()
    if g:NERDTreeQuitOnOpen && s:isTreeOpen()
        call s:closeTree()
    endif
endfunction
"FUNCTION: s:createTreeWin() {{{2
"Inits the NERD tree window. ie. opens it, sizes it, sets all the local
"options etc
function! s:createTreeWin()
    "create the nerd tree window
    let splitLocation = g:NERDTreeWinPos ==# "left" ? "topleft " : "botright "
    let splitSize = g:NERDTreeWinSize

    if !exists('t:NERDTreeBufName')
        let t:NERDTreeBufName = s:nextBufferName()
        silent! exec splitLocation . 'vertical ' . splitSize . ' new'
        silent! exec "edit " . t:NERDTreeBufName
    else
        silent! exec splitLocation . 'vertical ' . splitSize . ' split'
        silent! exec "buffer " . t:NERDTreeBufName
    endif

    setlocal winfixwidth

    "throwaway buffer options
    setlocal noswapfile
    setlocal buftype=nofile
    setlocal nowrap
    setlocal foldcolumn=0
    setlocal nobuflisted
    setlocal nospell
    if g:NERDTreeShowLineNumbers
        setlocal nu
    else
        setlocal nonu
    endif

    iabc <buffer>

    if g:NERDTreeHighlightCursorline
        setlocal cursorline
    endif

    call s:setupStatusline()

    call s:bindMappings()
    setfiletype nerdtree
    " syntax highlighting
    if has("syntax") && exists("g:syntax_on")
        call s:setupSyntaxHighlighting()
    endif
endfunction

"FUNCTION: s:dumpHelp  {{{2
"prints out the quick help
function! s:dumpHelp()
    let old_h = @h
    if b:treeShowHelp ==# 1
        let @h=   "\" NERD tree (" . s:NERD_tree_version . ") quickhelp~\n"
        let @h=@h."\" ============================\n"
        let @h=@h."\" File node mappings~\n"
        let @h=@h."\" ". (g:NERDTreeMouseMode ==# 3 ? "single" : "double") ."-click,\n"
        let @h=@h."\" <CR>,\n"
        if b:NERDTreeType ==# "primary"
            let @h=@h."\" ". g:NERDTreeMapActivateNode .": open in prev window\n"
        else
            let @h=@h."\" ". g:NERDTreeMapActivateNode .": open in current window\n"
        endif
        if b:NERDTreeType ==# "primary"
            let @h=@h."\" ". g:NERDTreeMapPreview .": preview\n"
        endif
        let @h=@h."\" ". g:NERDTreeMapOpenInTab.": open in new tab\n"
        let @h=@h."\" ". g:NERDTreeMapOpenInTabSilent .": open in new tab silently\n"
        let @h=@h."\" middle-click,\n"
        let @h=@h."\" ". g:NERDTreeMapOpenSplit .": open split\n"
        let @h=@h."\" ". g:NERDTreeMapPreviewSplit .": preview split\n"
        let @h=@h."\" ". g:NERDTreeMapOpenVSplit .": open vsplit\n"
        let @h=@h."\" ". g:NERDTreeMapPreviewVSplit .": preview vsplit\n"

        let @h=@h."\"\n\" ----------------------------\n"
        let @h=@h."\" Directory node mappings~\n"
        let @h=@h."\" ". (g:NERDTreeMouseMode ==# 1 ? "double" : "single") ."-click,\n"
        let @h=@h."\" ". g:NERDTreeMapActivateNode .": open & close node\n"
        let @h=@h."\" ". g:NERDTreeMapOpenRecursively .": recursively open node\n"
        let @h=@h."\" ". g:NERDTreeMapCloseDir .": close parent of node\n"
        let @h=@h."\" ". g:NERDTreeMapCloseChildren .": close all child nodes of\n"
        let @h=@h."\"    current node recursively\n"
        let @h=@h."\" middle-click,\n"
        let @h=@h."\" ". g:NERDTreeMapOpenExpl.": explore selected dir\n"

        let @h=@h."\"\n\" ----------------------------\n"
        let @h=@h."\" Bookmark table mappings~\n"
        let @h=@h."\" double-click,\n"
        let @h=@h."\" ". g:NERDTreeMapActivateNode .": open bookmark\n"
        let @h=@h."\" ". g:NERDTreeMapOpenInTab.": open in new tab\n"
        let @h=@h."\" ". g:NERDTreeMapOpenInTabSilent .": open in new tab silently\n"
        let @h=@h."\" ". g:NERDTreeMapDeleteBookmark .": delete bookmark\n"

        let @h=@h."\"\n\" ----------------------------\n"
        let @h=@h."\" Tree navigation mappings~\n"
        let @h=@h."\" ". g:NERDTreeMapJumpRoot .": go to root\n"
        let @h=@h."\" ". g:NERDTreeMapJumpParent .": go to parent\n"
        let @h=@h."\" ". g:NERDTreeMapJumpFirstChild  .": go to first child\n"
        let @h=@h."\" ". g:NERDTreeMapJumpLastChild   .": go to last child\n"
        let @h=@h."\" ". g:NERDTreeMapJumpNextSibling .": go to next sibling\n"
        let @h=@h."\" ". g:NERDTreeMapJumpPrevSibling .": go to prev sibling\n"

        let @h=@h."\"\n\" ----------------------------\n"
        let @h=@h."\" Filesystem mappings~\n"
        let @h=@h."\" ". g:NERDTreeMapChangeRoot .": change tree root to the\n"
        let @h=@h."\"    selected dir\n"
        let @h=@h."\" ". g:NERDTreeMapUpdir .": move tree root up a dir\n"
        let @h=@h."\" ". g:NERDTreeMapUpdirKeepOpen .": move tree root up a dir\n"
        let @h=@h."\"    but leave old root open\n"
        let @h=@h."\" ". g:NERDTreeMapRefresh .": refresh cursor dir\n"
        let @h=@h."\" ". g:NERDTreeMapRefreshRoot .": refresh current root\n"
        let @h=@h."\" ". g:NERDTreeMapMenu .": Show menu\n"
        let @h=@h."\" ". g:NERDTreeMapChdir .":change the CWD to the\n"
        let @h=@h."\"    selected dir\n"

        let @h=@h."\"\n\" ----------------------------\n"
        let @h=@h."\" Tree filtering mappings~\n"
        let @h=@h."\" ". g:NERDTreeMapToggleHidden .": hidden files (" . (b:NERDTreeShowHidden ? "on" : "off") . ")\n"
        let @h=@h."\" ". g:NERDTreeMapToggleFilters .": file filters (" . (b:NERDTreeIgnoreEnabled ? "on" : "off") . ")\n"
        let @h=@h."\" ". g:NERDTreeMapToggleFiles .": files (" . (b:NERDTreeShowFiles ? "on" : "off") . ")\n"
        let @h=@h."\" ". g:NERDTreeMapToggleBookmarks .": bookmarks (" . (b:NERDTreeShowBookmarks ? "on" : "off") . ")\n"

        "add quickhelp entries for each custom key map
        if len(s:KeyMap.All())
            let @h=@h."\"\n\" ----------------------------\n"
            let @h=@h."\" Custom mappings~\n"
            for i in s:KeyMap.All()
                let @h=@h."\" ". i.key .": ". i.quickhelpText ."\n"
            endfor
        endif

        let @h=@h."\"\n\" ----------------------------\n"
        let @h=@h."\" Other mappings~\n"
        let @h=@h."\" ". g:NERDTreeMapQuit .": Close the NERDTree window\n"
        let @h=@h."\" ". g:NERDTreeMapToggleZoom .": Zoom (maximize-minimize)\n"
        let @h=@h."\"    the NERDTree window\n"
        let @h=@h."\" ". g:NERDTreeMapHelp .": toggle help\n"
        let @h=@h."\"\n\" ----------------------------\n"
        let @h=@h."\" Bookmark commands~\n"
        let @h=@h."\" :Bookmark <name>\n"
        let @h=@h."\" :BookmarkToRoot <name>\n"
        let @h=@h."\" :RevealBookmark <name>\n"
        let @h=@h."\" :OpenBookmark <name>\n"
        let @h=@h."\" :ClearBookmarks [<names>]\n"
        let @h=@h."\" :ClearAllBookmarks\n"
    else
        let @h="\" Press ". g:NERDTreeMapHelp ." for help\n"
    endif

    silent! put h

    let @h = old_h
endfunction
"FUNCTION: s:echo  {{{2
"A wrapper for :echo. Appends 'NERDTree:' on the front of all messages
"
"Args:
"msg: the message to echo
function! s:echo(msg)
    redraw
    echomsg "NERDTree: " . a:msg
endfunction
"FUNCTION: s:echoWarning {{{2
"Wrapper for s:echo, sets the message type to warningmsg for this message
"Args:
"msg: the message to echo
function! s:echoWarning(msg)
    echohl warningmsg
    call s:echo(a:msg)
    echohl normal
endfunction
"FUNCTION: s:echoError {{{2
"Wrapper for s:echo, sets the message type to errormsg for this message
"Args:
"msg: the message to echo
function! s:echoError(msg)
    echohl errormsg
    call s:echo(a:msg)
    echohl normal
endfunction
"FUNCTION: s:firstUsableWindow(){{{2
"find the window number of the first normal window
function! s:firstUsableWindow()
    let i = 1
    while i <= winnr("$")
        let bnum = winbufnr(i)
        if bnum != -1 && getbufvar(bnum, '&buftype') ==# ''
                    \ && !getwinvar(i, '&previewwindow')
                    \ && (!getbufvar(bnum, '&modified') || &hidden)
            return i
        endif

        let i += 1
    endwhile
    return -1
endfunction
"FUNCTION: s:getPath(ln) {{{2
"Gets the full path to the node that is rendered on the given line number
"
"Args:
"ln: the line number to get the path for
"
"Return:
"A path if a node was selected, {} if nothing is selected.
"If the 'up a dir' line was selected then the path to the parent of the
"current root is returned
function! s:getPath(ln)
    let line = getline(a:ln)

    let rootLine = s:TreeFileNode.GetRootLineNum()

    "check to see if we have the root node
    if a:ln == rootLine
        return b:NERDTreeRoot.path
    endif

    " in case called from outside the tree
    if line !~ '^ *[|`]' || line =~ '^$'
        return {}
    endif

    if line ==# s:tree_up_dir_line
        return b:NERDTreeRoot.path.getParent()
    endif

    let indent = s:indentLevelFor(line)

    "remove the tree parts and the leading space
    let curFile = s:stripMarkupFromLine(line, 0)

    let wasdir = 0
    if curFile =~ '/$'
        let wasdir = 1
        let curFile = substitute(curFile, '/\?$', '/', "")
    endif

    let dir = ""
    let lnum = a:ln
    while lnum > 0
        let lnum = lnum - 1
        let curLine = getline(lnum)
        let curLineStripped = s:stripMarkupFromLine(curLine, 1)

        "have we reached the top of the tree?
        if lnum == rootLine
            let dir = b:NERDTreeRoot.path.str({'format': 'UI'}) . dir
            break
        endif
        if curLineStripped =~ '/$'
            let lpindent = s:indentLevelFor(curLine)
            if lpindent < indent
                let indent = indent - 1

                let dir = substitute (curLineStripped,'^\\', "", "") . dir
                continue
            endif
        endif
    endwhile
    let curFile = b:NERDTreeRoot.path.drive . dir . curFile
    let toReturn = s:Path.New(curFile)
    return toReturn
endfunction

"FUNCTION: s:getTreeWinNum() {{{2
"gets the nerd tree window number for this tab
function! s:getTreeWinNum()
    if exists("t:NERDTreeBufName")
        return bufwinnr(t:NERDTreeBufName)
    else
        return -1
    endif
endfunction
"FUNCTION: s:indentLevelFor(line) {{{2
function! s:indentLevelFor(line)
    return match(a:line, '[^ \-+~`|]') / s:tree_wid
endfunction
"FUNCTION: s:isTreeOpen() {{{2
function! s:isTreeOpen()
    return s:getTreeWinNum() != -1
endfunction
"FUNCTION: s:isWindowUsable(winnumber) {{{2
"Returns 0 if opening a file from the tree in the given window requires it to
"be split, 1 otherwise
"
"Args:
"winnumber: the number of the window in question
function! s:isWindowUsable(winnumber)
    "gotta split if theres only one window (i.e. the NERD tree)
    if winnr("$") ==# 1
        return 0
    endif

    let oldwinnr = winnr()
    call s:exec(a:winnumber . "wincmd p")
    let specialWindow = getbufvar("%", '&buftype') != '' || getwinvar('%', '&previewwindow')
    let modified = &modified
    call s:exec(oldwinnr . "wincmd p")

    "if its a special window e.g. quickfix or another explorer plugin then we
    "have to split
    if specialWindow
        return 0
    endif

    if &hidden
        return 1
    endif

    return !modified || s:bufInWindows(winbufnr(a:winnumber)) >= 2
endfunction

" FUNCTION: s:jumpToChild(direction) {{{2
" Args:
" direction: 0 if going to first child, 1 if going to last
function! s:jumpToChild(direction)
    let currentNode = s:TreeFileNode.GetSelected()
    if currentNode ==# {} || currentNode.isRoot()
        call s:echo("cannot jump to " . (a:direction ? "last" : "first") .  " child")
        return
    end
    let dirNode = currentNode.parent
    let childNodes = dirNode.getVisibleChildren()

    let targetNode = childNodes[0]
    if a:direction
        let targetNode = childNodes[len(childNodes) - 1]
    endif

    if targetNode.equals(currentNode)
        let siblingDir = currentNode.parent.findOpenDirSiblingWithVisibleChildren(a:direction)
        if siblingDir != {}
            let indx = a:direction ? siblingDir.getVisibleChildCount()-1 : 0
            let targetNode = siblingDir.getChildByIndex(indx, 1)
        endif
    endif

    call targetNode.putCursorHere(1, 0)

    call s:centerView()
endfunction


"FUNCTION: s:promptToDelBuffer(bufnum, msg){{{2
"prints out the given msg and, if the user responds by pushing 'y' then the
"buffer with the given bufnum is deleted
"
"Args:
"bufnum: the buffer that may be deleted
"msg: a message that will be echoed to the user asking them if they wish to
"     del the buffer
function! s:promptToDelBuffer(bufnum, msg)
    echo a:msg
    if nr2char(getchar()) ==# 'y'
        exec "silent bdelete! " . a:bufnum
    endif
endfunction

"FUNCTION: s:putCursorOnBookmarkTable(){{{2
"Places the cursor at the top of the bookmarks table
function! s:putCursorOnBookmarkTable()
    if !b:NERDTreeShowBookmarks
        throw "NERDTree.IllegalOperationError: cant find bookmark table, bookmarks arent active"
    endif

    let rootNodeLine = s:TreeFileNode.GetRootLineNum()

    let line = 1
    while getline(line) !~ '^>-\+Bookmarks-\+$'
        let line = line + 1
        if line >= rootNodeLine
            throw "NERDTree.BookmarkTableNotFoundError: didnt find the bookmarks table"
        endif
    endwhile
    call cursor(line, 0)
endfunction

"FUNCTION: s:putCursorInTreeWin(){{{2
"Places the cursor in the nerd tree window
function! s:putCursorInTreeWin()
    if !s:isTreeOpen()
        throw "NERDTree.InvalidOperationError: cant put cursor in NERD tree window, no window exists"
    endif

    call s:exec(s:getTreeWinNum() . "wincmd w")
endfunction

"FUNCTION: s:renderBookmarks {{{2
function! s:renderBookmarks()

    call setline(line(".")+1, ">----------Bookmarks----------")
    call cursor(line(".")+1, col("."))

    for i in s:Bookmark.Bookmarks()
        call setline(line(".")+1, i.str())
        call cursor(line(".")+1, col("."))
    endfor

    call setline(line(".")+1, '')
    call cursor(line(".")+1, col("."))
endfunction
"FUNCTION: s:renderView {{{2
"The entry function for rendering the tree
function! s:renderView()
    setlocal modifiable

    "remember the top line of the buffer and the current line so we can
    "restore the view exactly how it was
    let curLine = line(".")
    let curCol = col(".")
    let topLine = line("w0")

    "delete all lines in the buffer (being careful not to clobber a register)
    silent 1,$delete _

    call s:dumpHelp()

    "delete the blank line before the help and add one after it
    call setline(line(".")+1, "")
    call cursor(line(".")+1, col("."))

    if b:NERDTreeShowBookmarks
        call s:renderBookmarks()
    endif

    "add the 'up a dir' line
    call setline(line(".")+1, s:tree_up_dir_line)
    call cursor(line(".")+1, col("."))

    "draw the header line
    let header = b:NERDTreeRoot.path.str({'format': 'UI', 'truncateTo': winwidth(0)})
    call setline(line(".")+1, header)
    call cursor(line(".")+1, col("."))

    "draw the tree
    let old_o = @o
    let @o = b:NERDTreeRoot.renderToString()
    silent put o
    let @o = old_o

    "delete the blank line at the top of the buffer
    silent 1,1delete _

    "restore the view
    let old_scrolloff=&scrolloff
    let &scrolloff=0
    call cursor(topLine, 1)
    normal! zt
    call cursor(curLine, curCol)
    let &scrolloff = old_scrolloff

    setlocal nomodifiable
endfunction

"FUNCTION: s:renderViewSavingPosition {{{2
"Renders the tree and ensures the cursor stays on the current node or the
"current nodes parent if it is no longer available upon re-rendering
function! s:renderViewSavingPosition()
    let currentNode = s:TreeFileNode.GetSelected()

    "go up the tree till we find a node that will be visible or till we run
    "out of nodes
    while currentNode != {} && !currentNode.isVisible() && !currentNode.isRoot()
        let currentNode = currentNode.parent
    endwhile

    call s:renderView()

    if currentNode != {}
        call currentNode.putCursorHere(0, 0)
    endif
endfunction
"FUNCTION: s:restoreScreenState() {{{2
"
"Sets the screen state back to what it was when s:saveScreenState was last
"called.
"
"Assumes the cursor is in the NERDTree window
function! s:restoreScreenState()
    if !exists("b:NERDTreeOldTopLine") || !exists("b:NERDTreeOldPos") || !exists("b:NERDTreeOldWindowSize")
        return
    endif
    exec("silent vertical resize ".b:NERDTreeOldWindowSize)

    let old_scrolloff=&scrolloff
    let &scrolloff=0
    call cursor(b:NERDTreeOldTopLine, 0)
    normal! zt
    call setpos(".", b:NERDTreeOldPos)
    let &scrolloff=old_scrolloff
endfunction

"FUNCTION: s:saveScreenState() {{{2
"Saves the current cursor position in the current buffer and the window
"scroll position
function! s:saveScreenState()
    let win = winnr()
    try
        call s:putCursorInTreeWin()
        let b:NERDTreeOldPos = getpos(".")
        let b:NERDTreeOldTopLine = line("w0")
        let b:NERDTreeOldWindowSize = winwidth("")
        call s:exec(win . "wincmd w")
    catch /^NERDTree.InvalidOperationError/
    endtry
endfunction

"FUNCTION: s:setupStatusline() {{{2
function! s:setupStatusline()
    if g:NERDTreeStatusline != -1
        let &l:statusline = g:NERDTreeStatusline
    endif
endfunction
"FUNCTION: s:setupSyntaxHighlighting() {{{2
function! s:setupSyntaxHighlighting()
    "treeFlags are syntax items that should be invisible, but give clues as to
    "how things should be highlighted
    syn match treeFlag #\~#
    syn match treeFlag #\[RO\]#

    "highlighting for the .. (up dir) line at the top of the tree
    execute "syn match treeUp #". s:tree_up_dir_line ."#"

    "highlighting for the ~/+ symbols for the directory nodes
    syn match treeClosable #\~\<#
    syn match treeClosable #\~\.#
    syn match treeOpenable #+\<#
    syn match treeOpenable #+\.#he=e-1

    "highlighting for the tree structural parts
    syn match treePart #|#
    syn match treePart #`#
    syn match treePartFile #[|`]-#hs=s+1 contains=treePart

    "quickhelp syntax elements
    syn match treeHelpKey #" \{1,2\}[^ ]*:#hs=s+2,he=e-1
    syn match treeHelpKey #" \{1,2\}[^ ]*,#hs=s+2,he=e-1
    syn match treeHelpTitle #" .*\~#hs=s+2,he=e-1 contains=treeFlag
    syn match treeToggleOn #".*(on)#hs=e-2,he=e-1 contains=treeHelpKey
    syn match treeToggleOff #".*(off)#hs=e-3,he=e-1 contains=treeHelpKey
    syn match treeHelpCommand #" :.\{-}\>#hs=s+3
    syn match treeHelp  #^".*# contains=treeHelpKey,treeHelpTitle,treeFlag,treeToggleOff,treeToggleOn,treeHelpCommand

    "highlighting for readonly files
    syn match treeRO #.*\[RO\]#hs=s+2 contains=treeFlag,treeBookmark,treePart,treePartFile

    "highlighting for sym links
    syn match treeLink #[^-| `].* -> # contains=treeBookmark,treeOpenable,treeClosable,treeDirSlash

    "highlighing for directory nodes and file nodes
    syn match treeDirSlash #/#
    syn match treeDir #[^-| `].*/# contains=treeLink,treeDirSlash,treeOpenable,treeClosable
    syn match treeExecFile  #[|`]-.*\*\($\| \)# contains=treeLink,treePart,treeRO,treePartFile,treeBookmark
    syn match treeFile  #|-.*# contains=treeLink,treePart,treeRO,treePartFile,treeBookmark,treeExecFile
    syn match treeFile  #`-.*# contains=treeLink,treePart,treeRO,treePartFile,treeBookmark,treeExecFile
    syn match treeCWD #^/.*$#

    "highlighting for bookmarks
    syn match treeBookmark # {.*}#hs=s+1

    "highlighting for the bookmarks table
    syn match treeBookmarksLeader #^>#
    syn match treeBookmarksHeader #^>-\+Bookmarks-\+$# contains=treeBookmarksLeader
    syn match treeBookmarkName #^>.\{-} #he=e-1 contains=treeBookmarksLeader
    syn match treeBookmark #^>.*$# contains=treeBookmarksLeader,treeBookmarkName,treeBookmarksHeader

    if g:NERDChristmasTree
        hi def link treePart Special
        hi def link treePartFile Type
        hi def link treeFile Normal
        hi def link treeExecFile Title
        hi def link treeDirSlash Identifier
        hi def link treeClosable Type
    else
        hi def link treePart Normal
        hi def link treePartFile Normal
        hi def link treeFile Normal
        hi def link treeClosable Title
    endif

    hi def link treeBookmarksHeader statement
    hi def link treeBookmarksLeader ignore
    hi def link treeBookmarkName Identifier
    hi def link treeBookmark normal

    hi def link treeHelp String
    hi def link treeHelpKey Identifier
    hi def link treeHelpCommand Identifier
    hi def link treeHelpTitle Macro
    hi def link treeToggleOn Question
    hi def link treeToggleOff WarningMsg

    hi def link treeDir Directory
    hi def link treeUp Directory
    hi def link treeCWD Statement
    hi def link treeLink Macro
    hi def link treeOpenable Title
    hi def link treeFlag ignore
    hi def link treeRO WarningMsg
    hi def link treeBookmark Statement

    hi def link NERDTreeCurrentNode Search
endfunction

"FUNCTION: s:stripMarkupFromLine(line, removeLeadingSpaces){{{2
"returns the given line with all the tree parts stripped off
"
"Args:
"line: the subject line
"removeLeadingSpaces: 1 if leading spaces are to be removed (leading spaces =
"any spaces before the actual text of the node)
function! s:stripMarkupFromLine(line, removeLeadingSpaces)
    let line = a:line
    "remove the tree parts and the leading space
    let line = substitute (line, s:tree_markup_reg,"","")

    "strip off any read only flag
    let line = substitute (line, ' \[RO\]', "","")

    "strip off any bookmark flags
    let line = substitute (line, ' {[^}]*}', "","")

    "strip off any executable flags
    let line = substitute (line, '*\ze\($\| \)', "","")

    let wasdir = 0
    if line =~ '/$'
        let wasdir = 1
    endif
    let line = substitute (line,' -> .*',"","") " remove link to
    if wasdir ==# 1
        let line = substitute (line, '/\?$', '/', "")
    endif

    if a:removeLeadingSpaces
        let line = substitute (line, '^ *', '', '')
    endif

    return line
endfunction

"FUNCTION: s:toggle(dir) {{{2
"Toggles the NERD tree. I.e the NERD tree is open, it is closed, if it is
"closed it is restored or initialized (if it doesnt exist)
"
"Args:
"dir: the full path for the root node (is only used if the NERD tree is being
"initialized.
function! s:toggle(dir)
    if s:treeExistsForTab()
        if !s:isTreeOpen()
            call s:createTreeWin()
            if !&hidden
                call s:renderView()
            endif
            call s:restoreScreenState()
        else
            call s:closeTree()
        endif
    else
        call s:initNerdTree(a:dir)
    endif
endfunction
"SECTION: Interface bindings {{{1
"============================================================
"FUNCTION: s:activateNode(forceKeepWindowOpen) {{{2
"If the current node is a file, open it in the previous window (or a new one
"if the previous is modified). If it is a directory then it is opened.
"
"args:
"forceKeepWindowOpen - dont close the window even if NERDTreeQuitOnOpen is set
function! s:activateNode(forceKeepWindowOpen)
    if getline(".") ==# s:tree_up_dir_line
        return s:upDir(0)
    endif

    let treenode = s:TreeFileNode.GetSelected()
    if treenode != {}
        call treenode.activate(a:forceKeepWindowOpen)
    else
        let bookmark = s:Bookmark.GetSelected()
        if !empty(bookmark)
            call bookmark.activate()
        endif
    endif
endfunction

"FUNCTION: s:bindMappings() {{{2
function! s:bindMappings()
    " set up mappings and commands for this buffer
    nnoremap <silent> <buffer> <middlerelease> :call <SID>handleMiddleMouse()<cr>
    nnoremap <silent> <buffer> <leftrelease> <leftrelease>:call <SID>checkForActivate()<cr>
    nnoremap <silent> <buffer> <2-leftmouse> :call <SID>activateNode(0)<cr>

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapActivateNode . " :call <SID>activateNode(0)<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapOpenSplit ." :call <SID>openEntrySplit(0,0)<cr>"
    exec "nnoremap <silent> <buffer> <cr> :call <SID>activateNode(0)<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapPreview ." :call <SID>previewNode(0)<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapPreviewSplit ." :call <SID>previewNode(1)<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapOpenVSplit ." :call <SID>openEntrySplit(1,0)<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapPreviewVSplit ." :call <SID>previewNode(2)<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapOpenRecursively ." :call <SID>openNodeRecursively()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapUpdirKeepOpen ." :call <SID>upDir(1)<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapUpdir ." :call <SID>upDir(0)<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapChangeRoot ." :call <SID>chRoot()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapChdir ." :call <SID>chCwd()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapQuit ." :call <SID>closeTreeWindow()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapRefreshRoot ." :call <SID>refreshRoot()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapRefresh ." :call <SID>refreshCurrent()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapHelp ." :call <SID>displayHelp()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapToggleZoom ." :call <SID>toggleZoom()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapToggleHidden ." :call <SID>toggleShowHidden()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapToggleFilters ." :call <SID>toggleIgnoreFilter()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapToggleFiles ." :call <SID>toggleShowFiles()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapToggleBookmarks ." :call <SID>toggleShowBookmarks()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapCloseDir ." :call <SID>closeCurrentDir()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapCloseChildren ." :call <SID>closeChildren()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapMenu ." :call <SID>showMenu()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapJumpParent ." :call <SID>jumpToParent()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapJumpNextSibling ." :call <SID>jumpToSibling(1)<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapJumpPrevSibling ." :call <SID>jumpToSibling(0)<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapJumpFirstChild ." :call <SID>jumpToFirstChild()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapJumpLastChild ." :call <SID>jumpToLastChild()<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapJumpRoot ." :call <SID>jumpToRoot()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapOpenInTab ." :call <SID>openInNewTab(0)<cr>"
    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapOpenInTabSilent ." :call <SID>openInNewTab(1)<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapOpenExpl ." :call <SID>openExplorer()<cr>"

    exec "nnoremap <silent> <buffer> ". g:NERDTreeMapDeleteBookmark ." :call <SID>deleteBookmark()<cr>"

    "bind all the user custom maps
    call s:KeyMap.BindAll()

    command! -buffer -nargs=1 Bookmark :call <SID>bookmarkNode('<args>')
    command! -buffer -complete=customlist,s:completeBookmarks -nargs=1 RevealBookmark :call <SID>revealBookmark('<args>')
    command! -buffer -complete=customlist,s:completeBookmarks -nargs=1 OpenBookmark :call <SID>openBookmark('<args>')
    command! -buffer -complete=customlist,s:completeBookmarks -nargs=* ClearBookmarks call <SID>clearBookmarks('<args>')
    command! -buffer -complete=customlist,s:completeBookmarks -nargs=+ BookmarkToRoot call s:Bookmark.ToRoot('<args>')
    command! -buffer -nargs=0 ClearAllBookmarks call s:Bookmark.ClearAll() <bar> call <SID>renderView()
    command! -buffer -nargs=0 ReadBookmarks call s:Bookmark.CacheBookmarks(0) <bar> call <SID>renderView()
    command! -buffer -nargs=0 WriteBookmarks call s:Bookmark.Write()
endfunction

" FUNCTION: s:bookmarkNode(name) {{{2
" Associate the current node with the given name
function! s:bookmarkNode(name)
    let currentNode = s:TreeFileNode.GetSelected()
    if currentNode != {}
        try
            call currentNode.bookmark(a:name)
            call s:renderView()
        catch /^NERDTree.IllegalBookmarkNameError/
            call s:echo("bookmark names must not contain spaces")
        endtry
    else
        call s:echo("select a node first")
    endif
endfunction
"FUNCTION: s:checkForActivate() {{{2
"Checks if the click should open the current node, if so then activate() is
"called (directories are automatically opened if the symbol beside them is
"clicked)
function! s:checkForActivate()
    let currentNode = s:TreeFileNode.GetSelected()
    if currentNode != {}
        let startToCur = strpart(getline(line(".")), 0, col("."))
        let char = strpart(startToCur, strlen(startToCur)-1, 1)

        "if they clicked a dir, check if they clicked on the + or ~ sign
        "beside it
        if currentNode.path.isDirectory
            if startToCur =~ s:tree_markup_reg . '$' && char =~ '[+~]'
                call s:activateNode(0)
                return
            endif
        endif

        if (g:NERDTreeMouseMode ==# 2 && currentNode.path.isDirectory) || g:NERDTreeMouseMode ==# 3
            if char !~ s:tree_markup_reg && startToCur !~ '\/$'
                call s:activateNode(0)
                return
            endif
        endif
    endif
endfunction

" FUNCTION: s:chCwd() {{{2
function! s:chCwd()
    let treenode = s:TreeFileNode.GetSelected()
    if treenode ==# {}
        call s:echo("Select a node first")
        return
    endif

    try
        call treenode.path.changeToDir()
    catch /^NERDTree.PathChangeError/
        call s:echoWarning("could not change cwd")
    endtry
endfunction

" FUNCTION: s:chRoot() {{{2
" changes the current root to the selected one
function! s:chRoot()
    let treenode = s:TreeFileNode.GetSelected()
    if treenode ==# {}
        call s:echo("Select a node first")
        return
    endif

    call treenode.makeRoot()
    call s:renderView()
    call b:NERDTreeRoot.putCursorHere(0, 0)
endfunction

" FUNCTION: s:clearBookmarks(bookmarks) {{{2
function! s:clearBookmarks(bookmarks)
    if a:bookmarks ==# ''
        let currentNode = s:TreeFileNode.GetSelected()
        if currentNode != {}
            call currentNode.clearBoomarks()
        endif
    else
        for name in split(a:bookmarks, ' ')
            let bookmark = s:Bookmark.BookmarkFor(name)
            call bookmark.delete()
        endfor
    endif
    call s:renderView()
endfunction
" FUNCTION: s:closeChildren() {{{2
" closes all childnodes of the current node
function! s:closeChildren()
    let currentNode = s:TreeDirNode.GetSelected()
    if currentNode ==# {}
        call s:echo("Select a node first")
        return
    endif

    call currentNode.closeChildren()
    call s:renderView()
    call currentNode.putCursorHere(0, 0)
endfunction
" FUNCTION: s:closeCurrentDir() {{{2
" closes the parent dir of the current node
function! s:closeCurrentDir()
    let treenode = s:TreeFileNode.GetSelected()
    if treenode ==# {}
        call s:echo("Select a node first")
        return
    endif

    let parent = treenode.parent
    if parent ==# {} || parent.isRoot()
        call s:echo("cannot close tree root")
    else
        call treenode.parent.close()
        call s:renderView()
        call treenode.parent.putCursorHere(0, 0)
    endif
endfunction
" FUNCTION: s:closeTreeWindow() {{{2
" close the tree window
function! s:closeTreeWindow()
    if b:NERDTreeType ==# "secondary" && b:NERDTreePreviousBuf != -1
        exec "buffer " . b:NERDTreePreviousBuf
    else
        if winnr("$") > 1
            call s:closeTree()
        else
            call s:echo("Cannot close last window")
        endif
    endif
endfunction
" FUNCTION: s:deleteBookmark() {{{2
" if the cursor is on a bookmark, prompt to delete
function! s:deleteBookmark()
    let bookmark = s:Bookmark.GetSelected()
    if bookmark ==# {}
        call s:echo("Put the cursor on a bookmark")
        return
    endif

    echo  "Are you sure you wish to delete the bookmark:\n\"" . bookmark.name . "\" (yN):"

    if  nr2char(getchar()) ==# 'y'
        try
            call bookmark.delete()
            call s:renderView()
            redraw
        catch /^NERDTree/
            call s:echoWarning("Could not remove bookmark")
        endtry
    else
        call s:echo("delete aborted" )
    endif

endfunction

" FUNCTION: s:displayHelp() {{{2
" toggles the help display
function! s:displayHelp()
    let b:treeShowHelp = b:treeShowHelp ? 0 : 1
    call s:renderView()
    call s:centerView()
endfunction

" FUNCTION: s:handleMiddleMouse() {{{2
function! s:handleMiddleMouse()
    let curNode = s:TreeFileNode.GetSelected()
    if curNode ==# {}
        call s:echo("Put the cursor on a node first" )
        return
    endif

    if curNode.path.isDirectory
        call s:openExplorer()
    else
        call s:openEntrySplit(0,0)
    endif
endfunction


" FUNCTION: s:jumpToFirstChild() {{{2
" wrapper for the jump to child method
function! s:jumpToFirstChild()
    call s:jumpToChild(0)
endfunction

" FUNCTION: s:jumpToLastChild() {{{2
" wrapper for the jump to child method
function! s:jumpToLastChild()
    call s:jumpToChild(1)
endfunction

" FUNCTION: s:jumpToParent() {{{2
" moves the cursor to the parent of the current node
function! s:jumpToParent()
    let currentNode = s:TreeFileNode.GetSelected()
    if !empty(currentNode)
        if !empty(currentNode.parent)
            call currentNode.parent.putCursorHere(1, 0)
            call s:centerView()
        else
            call s:echo("cannot jump to parent")
        endif
    else
        call s:echo("put the cursor on a node first")
    endif
endfunction

" FUNCTION: s:jumpToRoot() {{{2
" moves the cursor to the root node
function! s:jumpToRoot()
    call b:NERDTreeRoot.putCursorHere(1, 0)
    call s:centerView()
endfunction

" FUNCTION: s:jumpToSibling() {{{2
" moves the cursor to the sibling of the current node in the given direction
"
" Args:
" forward: 1 if the cursor should move to the next sibling, 0 if it should
" move back to the previous sibling
function! s:jumpToSibling(forward)
    let currentNode = s:TreeFileNode.GetSelected()
    if !empty(currentNode)
        let sibling = currentNode.findSibling(a:forward)

        if !empty(sibling)
            call sibling.putCursorHere(1, 0)
            call s:centerView()
        endif
    else
        call s:echo("put the cursor on a node first")
    endif
endfunction

" FUNCTION: s:openBookmark(name) {{{2
" put the cursor on the given bookmark and, if its a file, open it
function! s:openBookmark(name)
    try
        let targetNode = s:Bookmark.GetNodeForName(a:name, 0)
        call targetNode.putCursorHere(0, 1)
        redraw!
    catch /^NERDTree.BookmarkedNodeNotFoundError/
        call s:echo("note - target node is not cached")
        let bookmark = s:Bookmark.BookmarkFor(a:name)
        let targetNode = s:TreeFileNode.New(bookmark.path)
    endtry
    if targetNode.path.isDirectory
        call targetNode.openExplorer()
    else
        call targetNode.open()
    endif
endfunction
" FUNCTION: s:openEntrySplit(vertical, forceKeepWindowOpen) {{{2
"Opens the currently selected file from the explorer in a
"new window
"
"args:
"forceKeepWindowOpen - dont close the window even if NERDTreeQuitOnOpen is set
function! s:openEntrySplit(vertical, forceKeepWindowOpen)
    let treenode = s:TreeFileNode.GetSelected()
    if treenode != {}
        if a:vertical
            call treenode.openVSplit()
        else
            call treenode.openSplit()
        endif
        if !a:forceKeepWindowOpen
            call s:closeTreeIfQuitOnOpen()
        endif
    else
        call s:echo("select a node first")
    endif
endfunction

" FUNCTION: s:openExplorer() {{{2
function! s:openExplorer()
    let treenode = s:TreeDirNode.GetSelected()
    if treenode != {}
        call treenode.openExplorer()
    else
        call s:echo("select a node first")
    endif
endfunction

" FUNCTION: s:openInNewTab(stayCurrentTab) {{{2
" Opens the selected node or bookmark in a new tab
" Args:
" stayCurrentTab: if 1 then vim will stay in the current tab, if 0 then vim
" will go to the tab where the new file is opened
function! s:openInNewTab(stayCurrentTab)
    let target = s:TreeFileNode.GetSelected()
    if target == {}
        let target = s:Bookmark.GetSelected()
    endif

    if target != {}
        call target.openInNewTab({'stayInCurrentTab': a:stayCurrentTab})
    endif
endfunction

" FUNCTION: s:openNodeRecursively() {{{2
function! s:openNodeRecursively()
    let treenode = s:TreeFileNode.GetSelected()
    if treenode ==# {} || treenode.path.isDirectory ==# 0
        call s:echo("Select a directory node first" )
    else
        call s:echo("Recursively opening node. Please wait...")
        call treenode.openRecursively()
        call s:renderView()
        redraw
        call s:echo("Recursively opening node. Please wait... DONE")
    endif

endfunction

"FUNCTION: s:previewNode() {{{2
"Args:
"   openNewWin: if 0, use the previous window, if 1 open in new split, if 2
"               open in a vsplit
function! s:previewNode(openNewWin)
    let currentBuf = bufnr("")
    if a:openNewWin > 0
        call s:openEntrySplit(a:openNewWin ==# 2,1)
    else
        call s:activateNode(1)
    end
    call s:exec(bufwinnr(currentBuf) . "wincmd w")
endfunction

" FUNCTION: s:revealBookmark(name) {{{2
" put the cursor on the node associate with the given name
function! s:revealBookmark(name)
    try
        let targetNode = s:Bookmark.GetNodeForName(a:name, 0)
        call targetNode.putCursorHere(0, 1)
    catch /^NERDTree.BookmarkNotFoundError/
        call s:echo("Bookmark isnt cached under the current root")
    endtry
endfunction
" FUNCTION: s:refreshRoot() {{{2
" Reloads the current root. All nodes below this will be lost and the root dir
" will be reloaded.
function! s:refreshRoot()
    call s:echo("Refreshing the root node. This could take a while...")
    call b:NERDTreeRoot.refresh()
    call s:renderView()
    redraw
    call s:echo("Refreshing the root node. This could take a while... DONE")
endfunction

" FUNCTION: s:refreshCurrent() {{{2
" refreshes the root for the current node
function! s:refreshCurrent()
    let treenode = s:TreeDirNode.GetSelected()
    if treenode ==# {}
        call s:echo("Refresh failed. Select a node first")
        return
    endif

    call s:echo("Refreshing node. This could take a while...")
    call treenode.refresh()
    call s:renderView()
    redraw
    call s:echo("Refreshing node. This could take a while... DONE")
endfunction
" FUNCTION: s:showMenu() {{{2
function! s:showMenu()
    let curNode = s:TreeFileNode.GetSelected()
    if curNode ==# {}
        call s:echo("Put the cursor on a node first" )
        return
    endif

    let mc = s:MenuController.New(s:MenuItem.AllEnabled())
    call mc.showMenu()
endfunction

" FUNCTION: s:toggleIgnoreFilter() {{{2
" toggles the use of the NERDTreeIgnore option
function! s:toggleIgnoreFilter()
    let b:NERDTreeIgnoreEnabled = !b:NERDTreeIgnoreEnabled
    call s:renderViewSavingPosition()
    call s:centerView()
endfunction

" FUNCTION: s:toggleShowBookmarks() {{{2
" toggles the display of bookmarks
function! s:toggleShowBookmarks()
    let b:NERDTreeShowBookmarks = !b:NERDTreeShowBookmarks
    if b:NERDTreeShowBookmarks
        call s:renderView()
        call s:putCursorOnBookmarkTable()
    else
        call s:renderViewSavingPosition()
    endif
    call s:centerView()
endfunction
" FUNCTION: s:toggleShowFiles() {{{2
" toggles the display of hidden files
function! s:toggleShowFiles()
    let b:NERDTreeShowFiles = !b:NERDTreeShowFiles
    call s:renderViewSavingPosition()
    call s:centerView()
endfunction

" FUNCTION: s:toggleShowHidden() {{{2
" toggles the display of hidden files
function! s:toggleShowHidden()
    let b:NERDTreeShowHidden = !b:NERDTreeShowHidden
    call s:renderViewSavingPosition()
    call s:centerView()
endfunction

" FUNCTION: s:toggleZoom() {{2
" zoom (maximize/minimize) the NERDTree window
function! s:toggleZoom()
    if exists("b:NERDTreeZoomed") && b:NERDTreeZoomed
        let size = exists("b:NERDTreeOldWindowSize") ? b:NERDTreeOldWindowSize : g:NERDTreeWinSize
        exec "silent vertical resize ". size
        let b:NERDTreeZoomed = 0
    else
        exec "vertical resize"
        let b:NERDTreeZoomed = 1
    endif
endfunction

"FUNCTION: s:upDir(keepState) {{{2
"moves the tree up a level
"
"Args:
"keepState: 1 if the current root should be left open when the tree is
"re-rendered
function! s:upDir(keepState)
    let cwd = b:NERDTreeRoot.path.str({'format': 'UI'})
    if cwd ==# "/" || cwd =~ '^[^/]..$'
        call s:echo("already at top dir")
    else
        if !a:keepState
            call b:NERDTreeRoot.close()
        endif

        let oldRoot = b:NERDTreeRoot

        if empty(b:NERDTreeRoot.parent)
            let path = b:NERDTreeRoot.path.getParent()
            let newRoot = s:TreeDirNode.New(path)
            call newRoot.open()
            call newRoot.transplantChild(b:NERDTreeRoot)
            let b:NERDTreeRoot = newRoot
        else
            let b:NERDTreeRoot = b:NERDTreeRoot.parent
        endif

        if g:NERDTreeChDirMode ==# 2
            call b:NERDTreeRoot.path.changeToDir()
        endif

        call s:renderView()
        call oldRoot.putCursorHere(0, 0)
    endif
endfunction


"reset &cpo back to users setting
let &cpo = s:old_cpo

" vim: set sw=4 sts=4 et fdm=marker:
syntax/jalv2.vim	[[[1
253
" Vim syntax file
" Language:	jalv2
" Version: 0.1
" Last Change:	2003 May 11
" Maintainer:  Mark Gross <mark@thegnar.org>
" This is a syntax definition for the JAL language.
" It is based on the Source Forge compiler source code.
" https://sourceforge.net/projects/jal/
"
" TODO test.

" For version 5.x: Clear all syntax items
" For version 6.x: Quit when a syntax file was already loaded
if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

syn case ignore
syn sync lines=250

syn keyword picTodo NOTE TODO XXX contained

syn match picIdentifier "[a-z_$][a-z0-9_$]*"
syn match picLabel      "^[A-Z_$][A-Z0-9_$]*"
syn match picLabel      "^[A-Z_$][A-Z0-9_$]*:"me=e-1

syn match picASCII      "A\='.'"
syn match picBinary     "B'[0-1]\+'"
syn match picDecimal    "D'\d\+'"
syn match picDecimal    "\d\+"
syn match picHexadecimal "0x\x\+"
syn match picHexadecimal "H'\x\+'"
syn match picHexadecimal "[0-9]\x*h"
syn match picOctal      "O'[0-7]\o*'"

syn match picComment    ";.*" contains=picTodo

syn region picString    start=+"+ end=+"+

syn keyword picRegister indf tmr0 pcl status fsr port_a port_b port_c port_d port_e x84_eedata x84_eeadr pclath intcon
syn keyword picRegister f877_tmr1l   f877_tmr1h   f877_t1con   f877_t2con   f877_ccpr1l  f877_ccpr1h  f877_ccp1con
syn keyword picRegister f877_pir1    f877_pir2    f877_pie1    f877_adcon1  f877_adcon0  f877_pr2     f877_adresl  f877_adresh
syn keyword picRegister f877_eeadr   f877_eedath  f877_eeadrh  f877_eedata  f877_eecon1  f877_eecon2  f628_EECON2
syn keyword picRegister f877_rcsta   f877_txsta   f877_spbrg   f877_txreg   f877_rcreg   f628_EEDATA  f628_EEADR   f628_EECON1

" Register --- bits
" STATUS
syn keyword picRegisterPart status_c status_dc status_z status_pd
syn keyword picRegisterPart status_to status_rp0 status_rp1 status_irp

" pins
syn keyword picRegisterPart pin_a0 pin_a1 pin_a2 pin_a3 pin_a4 pin_a5 pin_a6 pin_a7
syn keyword picRegisterPart pin_b0 pin_b1 pin_b2 pin_b3 pin_b4 pin_b5 pin_b6 pin_b7
syn keyword picRegisterPart pin_c0 pin_c1 pin_c2 pin_c3 pin_c4 pin_c5 pin_c6 pin_c7
syn keyword picRegisterPart pin_d0 pin_d1 pin_d2 pin_d3 pin_d4 pin_d5 pin_d6 pin_d7
syn keyword picRegisterPart pin_e0 pin_e1 pin_e2 pin_e3 pin_e4 pin_e5 pin_e6 pin_e7
syn keyword picRegisterPart pin_f0 pin_f1 pin_f2 pin_f3 pin_f4 pin_f5 pin_f6 pin_f7

syn keyword picPortDir port_a_direction  port_b_direction  port_c_direction  port_d_direction  port_e_direction port_f_direction

syn match picPinDir "pin_a[0-8]_direction "
syn match picPinDir "pin_b[0-8]_direction"
syn match picPinDir "pin_c[0-8]_direction"
syn match picPinDir "pin_d[0-8]_direction"
syn match picPinDir "pin_e[0-8]_direction"
syn match picPinDir "pin_f[0-8]_direction"



" INTCON
syn keyword picRegisterPart intcon_gie intcon_eeie intcon_peie intcon_t0ie intcon_inte
syn keyword picRegisterPart intcon_rbie intcon_t0if intcon_intf intcon_rbif

" TIMER
syn keyword picRegisterPart t1ckps1 t1ckps0 t1oscen t1sync tmr1cs tmr1on tmr1ie tmr1if

"cpp bits
syn keyword picRegisterPart ccp1x ccp1y

" adcon bits
syn keyword picRegisterPart adcon0_go adcon0_ch0 adcon0_ch1 adcon0_ch2

" EECON
syn keyword picRegisterPart  eecon1_rd eecon1_wr eecon1_wren eecon1_wrerr eecon1_eepgd
syn keyword picRegisterPart f628_eecon1_rd f628_eecon1_wr f628_eecon1_wren f628_eecon1_wrerr

" usart
syn keyword picRegisterPart tx9 txen sync brgh tx9d
syn keyword picRegisterPart spen rx9 cren ferr oerr rx9d
syn keyword picRegisterPart TXIF RCIF

" OpCodes...
syn keyword picOpcode addlw andlw call clrwdt goto iorlw movlw option retfie retlw return sleep sublw tris
syn keyword picOpcode xorlw addwf andwf clrf clrw comf decf decfsz incf incfsz retiw iorwf movf movwf nop
syn keyword picOpcode rlf rrf subwf swapf xorwf bcf bsf btfsc btfss skpz skpnz setz clrz skpc skpnc setc clrc
syn keyword picOpcode skpdc skpndc setdc clrdc movfw tstf bank page HPAGE mullw mulwf cpfseq cpfsgt cpfslt banka bankb


syn keyword jalBoolean		true false
syn keyword jalBoolean		off on
syn keyword jalBit		high low
syn keyword jalConstant		Input Output all_input all_output
syn keyword jalConditional	if else then elsif end if case of
syn keyword jalLabel		goto
syn keyword jalRepeat		for while forever loop
syn keyword jalStatement	procedure function
syn keyword jalStatement	return end volatile const var
syn keyword jalType		bit byte word dword

syn keyword jalModifier		interrupt assembler asm put get
syn keyword jalStatement	out in is begin at shared alias
syn keyword jalDirective	pragma jump_table target target_clock target_chip name error test assert inline
syn keyword jalPredefined       hs xt rc lp internal 16c84 16f84 16f877 sx18 sx28 12c509a 12c508
syn keyword jalPredefined       12ce674 16f628 18f252 18f242 18f442 18f452 12f629 12f675 16f88
syn keyword jalPredefined	16f876 16f873 sx_12 sx18 sx28 pic_12 pic_14 pic_16

syn keyword jalDirective chip osc clock  fuses  cpu watchdog powerup protection

syn keyword jalFunction		bank_0 bank_1 bank_2 bank_3 bank_4 bank_5 bank_6 bank_7 trisa trisb trisc trisd trise
syn keyword jalFunction		_trisa_flush _trisb_flush _trisc_flush _trisd_flush _trise_flush

syn keyword jalPIC		local idle_loop

syn region  jalAsm		matchgroup=jalAsmKey start="\<assembler\>" end="\<end assembler\>" contains=jalComment,jalPreProc,jalLabel,picIdentifier, picLabel,picASCII,picDecimal,picHexadecimal,picOctal,picComment,picString,picRegister,picRigisterPart,picOpcode,picDirective,jalPIC
syn region  jalAsm		matchgroup=jalAsmKey start="\<asm\>" end=/$/ contains=jalComment,jalPreProc,jalLabel,picIdentifier, picLabel,picASCII,picDecimal,picHexadecimal,picOctal,picComment,picString,picRegister,picRigisterPart,picOpcode,picDirective,jalPIC

syn region  jalPsudoVars matchgroup=jalPsudoVarsKey start="\<'put\>" end="/<is/>"  contains=jalComment

syn match  jalStringEscape	contained "#[12][0-9]\=[0-9]\="
syn match   jalIdentifier		"\<[a-zA-Z_][a-zA-Z0-9_]*\>"
syn match   jalSymbolOperator		"[+\-/*=]"
syn match   jalSymbolOperator		"!"
syn match   jalSymbolOperator		"<"
syn match   jalSymbolOperator		">"
syn match   jalSymbolOperator		"<="
syn match   jalSymbolOperator		">="
syn match   jalSymbolOperator		"!="
syn match   jalSymbolOperator		"=="
syn match   jalSymbolOperator		"<<"
syn match   jalSymbolOperator		">>"
syn match   jalSymbolOperator		"|"
syn match   jalSymbolOperator		"&"
syn match   jalSymbolOperator		"%"
syn match   jalSymbolOperator		"?"
syn match   jalSymbolOperator		"[()]"
syn match   jalSymbolOperator		"[\^.]"
syn match   jalLabel			"[\^]*:"

syn match  jalNumber		"-\=\<\d[0-9_]\+\>"
syn match  jalHexNumber		"0x[0-9A-Fa-f_]\+\>"
syn match  jalBinNumber		"0b[01_]\+\>"

" String
"wrong strings
syn region  jalStringError matchgroup=jalStringError start=+"+ end=+"+ end=+$+ contains=jalStringEscape

"right strings
syn region  jalString matchgroup=jalString start=+'+ end=+'+ oneline contains=jalStringEscape
" To see the start and end of strings:
syn region  jalString matchgroup=jalString start=+"+ end=+"+ oneline contains=jalStringEscapeGPC

syn keyword jalTodo contained	TODO
syn region jalComment		start=/-- /  end=/$/ oneline contains=jalTodo
syn region jalComment		start=/--\t/  end=/$/ oneline contains=jalTodo
syn match  jalComment		/--\_$/
syn region jalPreProc		start="include"  end=/$/ contains=JalComment,jalToDo


if exists("jal_no_tabs")
	syn match jalShowTab "\t"
endif


" Define the default highlighting.
" For version 5.7 and earlier: only when not done already
" For version 5.8 and later: only when an item doesn't have highlighting yet
if version >= 508 || !exists("did_jal_syn_inits")
if version < 508
  let did_jal_syn_inits = 1
  command -nargs=+ HiLink hi link <args>
else
  command -nargs=+ HiLink hi def link <args>
endif

  HiLink jalAcces		jalStatement
  HiLink jalBoolean		Boolean
  HiLink jalBit			Boolean
  HiLink jalComment		Comment
  HiLink jalConditional		Conditional
  HiLink jalConstant		Constant
  HiLink jalDelimiter		Identifier
  HiLink jalDirective		PreProc
  HiLink jalException		Exception
  HiLink jalFloat		Float
  HiLink jalFunction		Function
  HiLink jalPsudoVarsKey	Function
  HiLink jalLabel		Label
  HiLink jalMatrixDelimiter	Identifier
  HiLink jalModifier		Type
  HiLink jalNumber		Number
  HiLink jalBinNumber		Number
  HiLink jalHexNumber		Number
  HiLink jalOperator		Operator
  HiLink jalPredefined		Constant
  HiLink jalPreProc		PreProc
  HiLink jalRepeat		Repeat
  HiLink jalStatement		Statement
  HiLink jalString		String
  HiLink jalStringEscape	Special
  HiLink jalStringEscapeGPC	Special
  HiLink jalStringError		Error
  HiLink jalStruct		jalStatement
  HiLink jalSymbolOperator	jalOperator
  HiLink jalTodo		Todo
  HiLink jalType		Type
  HiLink jalUnclassified	Statement
  HiLink jalAsm			Assembler
  HiLink jalError		Error
  HiLink jalAsmKey		Statement
  HiLink jalPIC			Statement

  HiLink jalShowTab		Error

  HiLink picTodo		Todo
  HiLink picComment		Comment
  HiLink picDirective		Statement
  HiLink picLabel		Label
  HiLink picString		String

  HiLink picOpcode		Keyword
  HiLink picRegister		Structure
  HiLink picRegisterPart	Special
  HiLink picPinDir		SPecial
  HiLink picPinAliases		SPecial
  HiLink picPortDir		SPecial

  HiLink picASCII		String
  HiLink picBinary		Number
  HiLink picDecimal		Number
  HiLink picHexadecimal		Number
  HiLink picOctal		Number

  HiLink picIdentifier		Identifier

  delcommand HiLink
endif


let b:current_syntax = "jalv2"

" vim: ts=8 sw=2
doc/snipMate.txt	[[[1
286
*snipMate.txt*  Plugin for using TextMate-style snippets in Vim.

snipMate                                       *snippet* *snippets* *snipMate*
Last Change: July 13, 2009

|snipMate-description|   Description
|snipMate-syntax|        Snippet syntax
|snipMate-usage|         Usage
|snipMate-settings|      Settings
|snipMate-features|      Features
|snipMate-disadvantages| Disadvantages to TextMate
|snipMate-contact|       Contact

For Vim version 7.0 or later.
This plugin only works if 'compatible' is not set.
{Vi does not have any of these features.}

==============================================================================
DESCRIPTION                                             *snipMate-description*

snipMate.vim implements some of TextMate's snippets features in Vim. A
snippet is a piece of often-typed text that you can insert into your
document using a trigger word followed by a <tab>.

For instance, in a C file using the default installation of snipMate.vim, if
you type "for<tab>" in insert mode, it will expand a typical for loop in C: >

 for (i = 0; i < count; i++) {

 }


To go to the next item in the loop, simply <tab> over to it; if there is
repeated code, such as the "i" variable in this example, you can simply
start typing once it's highlighted and all the matches specified in the
snippet will be updated. To go in reverse, use <shift-tab>.

==============================================================================
SYNTAX                                                        *snippet-syntax*

Snippets can be defined in two ways. They can be in their own file, named
after their trigger in 'snippets/<filetype>/<trigger>.snippet', or they can be
defined together in a 'snippets/<filetype>.snippets' file. Note that dotted
'filetype' syntax is supported -- e.g., you can use >

	:set ft=html.eruby

to activate snippets for both HTML and eRuby for the current file.

The syntax for snippets in *.snippets files is the following: >

 snippet trigger
 	expanded text
	more expanded text

Note that the first hard tab after the snippet trigger is required, and not
expanded in the actual snippet. The syntax for *.snippet files is the same,
only without the trigger declaration and starting indentation.

Also note that snippets must be defined using hard tabs. They can be expanded
to spaces later if desired (see |snipMate-indenting|).

"#" is used as a line-comment character in *.snippets files; however, they can
only be used outside of a snippet declaration. E.g.: >

 # this is a correct comment
 snippet trigger
 	expanded text
 snippet another_trigger
 	# this isn't a comment!
	expanded text
<
This should hopefully be obvious with the included syntax highlighting.

                                                               *snipMate-${#}*
Tab stops ~

By default, the cursor is placed at the end of a snippet. To specify where the
cursor is to be placed next, use "${#}", where the # is the number of the tab
stop. E.g., to place the cursor first on the id of a <div> tag, and then allow
the user to press <tab> to go to the middle of it:
 >
 snippet div
 	<div id="${1}">
		${2}
	</div>
<
                        *snipMate-placeholders* *snipMate-${#:}* *snipMate-$#*
Placeholders ~

Placeholder text can be supplied using "${#:text}", where # is the number of
the tab stop. This text then can be copied throughout the snippet using "$#",
given # is the same number as used before. So, to make a C for loop: >

 snippet for
 	for (${2:i}; $2 < ${1:count}; $1++) {
		${4}
	}

This will cause "count" to first be selected and change if the user starts
typing. When <tab> is pressed, the "i" in ${2}'s position will be selected;
all $2 variables will default to "i" and automatically be updated if the user
starts typing.
NOTE: "$#" syntax is used only for variables, not for tab stops as in TextMate.

Variables within variables are also possible. For instance: >

 snippet opt
 	<option value="${1:option}">${2:$1}</option>

Will, as usual, cause "option" to first be selected and update all the $1
variables if the user starts typing. Since one of these variables is inside of
${2}, this text will then be used as a placeholder for the next tab stop,
allowing the user to change it if he wishes.

To copy a value throughout a snippet without supplying default text, simply
use the "${#:}" construct without the text; e.g.: >

 snippet foo
 	${1:}bar$1
<                                                          *snipMate-commands*
Interpolated Vim Script ~

Snippets can also contain Vim script commands that are executed (via |eval()|)
when the snippet is inserted. Commands are given inside backticks (`...`); for
TextMates's functionality, use the |system()| function. E.g.: >

 snippet date
 	`system("date +%Y-%m-%d")`

will insert the current date, assuming you are on a Unix system. Note that you
can also (and should) use |strftime()| for this example.

Filename([{expr}] [, {defaultText}])             *snipMate-filename* *Filename()*

Since the current filename is used often in snippets, a default function
has been defined for it in snipMate.vim, appropriately called Filename().

With no arguments, the default filename without an extension is returned;
the first argument specifies what to place before or after the filename,
and the second argument supplies the default text to be used if the file
has not been named. "$1" in the first argument is replaced with the filename;
if you only want the filename to be returned, the first argument can be left
blank. Examples: >

 snippet filename
 	`Filename()`
 snippet filename_with_default
 	`Filename('', 'name')`
 snippet filename_foo
 	`filename('$1_foo')`

The first example returns the filename if it the file has been named, and an
empty string if it hasn't. The second returns the filename if it's been named,
and "name" if it hasn't. The third returns the filename followed by "_foo" if
it has been named, and an empty string if it hasn't.

                                                                   *multi_snip*
To specify that a snippet can have multiple matches in a *.snippets file, use
this syntax: >

 snippet trigger A description of snippet #1
 	expand this text
 snippet trigger A description of snippet #2
 	expand THIS text!

In this example, when "trigger<tab>" is typed, a numbered menu containing all
of the descriptions of the "trigger" will be shown; when the user presses the
corresponding number, that snippet will then be expanded.

To create a snippet with multiple matches using *.snippet files,
simply place all the snippets in a subdirectory with the trigger name:
'snippets/<filetype>/<trigger>/<name>.snippet'.

==============================================================================
USAGE                                                         *snipMate-usage*

                                                 *'snippets'* *g:snippets_dir*
Snippets are by default looked for any 'snippets' directory in your
'runtimepath'. Typically, it is located at '~/.vim/snippets/' on *nix or
'$HOME\vimfiles\snippets\' on Windows. To change that location or add another
one, change the g:snippets_dir variable in your |.vimrc| to your preferred
directory, or use the |ExtractSnips()|function. This will be used by the
|globpath()| function, and so accepts the same syntax as it (e.g.,
comma-separated paths).

ExtractSnipsFile({directory}, {filetype})     *ExtractSnipsFile()* *.snippets*

ExtractSnipsFile() extracts the specified *.snippets file for the given
filetype. A .snippets file contains multiple snippet declarations for the
filetype. It is further explained above, in |snippet-syntax|.

ExtractSnips({directory}, {filetype})             *ExtractSnips()* *.snippet*

ExtractSnips() extracts *.snippet files from the specified directory and
defines them as snippets for the given filetype. The directory tree should
look like this: 'snippets/<filetype>/<trigger>.snippet'. If the snippet has
multiple matches, it should look like this:
'snippets/<filetype>/<trigger>/<name>.snippet' (see |multi_snip|).

                                                            *ResetSnippets()*
The ResetSnippets() function removes all snippets from memory. This is useful
to put at the top of a snippet setup file for if you would like to |:source|
it multiple times.

                                             *list-snippets* *i_CTRL-R_<Tab>*
If you would like to see what snippets are available, simply type <c-r><tab>
in the current buffer to show a list via |popupmenu-completion|.

==============================================================================
SETTINGS                                  *snipMate-settings* *g:snips_author*

The g:snips_author string (similar to $TM_FULLNAME in TextMate) should be set
to your name; it can then be used in snippets to automatically add it. E.g.: >

 let g:snips_author = 'Hubert Farnsworth'
 snippet name
 	`g:snips_author`
<
                                     *snipMate-expandtab* *snipMate-indenting*
If you would like your snippets to be expanded using spaces instead of tabs,
just enable 'expandtab' and set 'softtabstop' to your preferred amount of
spaces. If 'softtabstop' is not set, 'shiftwidth' is used instead.

                                                              *snipMate-remap*
snipMate does not come with a setting to customize the trigger key, but you
can remap it easily in the two lines it's defined in the 'after' directory
under 'plugin/snipMate.vim'. For instance, to change the trigger key
to CTRL-J, just change this: >

 ino <tab> <c-r>=TriggerSnippet()<cr>
 snor <tab> <esc>i<right><c-r>=TriggerSnippet()<cr>

to this: >
 ino <c-j> <c-r>=TriggerSnippet()<cr>
 snor <c-j> <esc>i<right><c-r>=TriggerSnippet()<cr>

==============================================================================
FEATURES                                                   *snipMate-features*

snipMate.vim has the following features among others:
  - The syntax of snippets is very similar to TextMate's, allowing
    easy conversion.
  - The position of the snippet is kept transparently (i.e. it does not use
    markers/placeholders written to the buffer), which allows you to escape
    out of an incomplete snippet, something particularly useful in Vim.
  - Variables in snippets are updated as-you-type.
  - Snippets can have multiple matches.
  - Snippets can be out of order. For instance, in a do...while loop, the
    condition can be added before the code.
  - [New] File-based snippets are supported.
  - [New] Triggers after non-word delimiters are expanded, e.g. "foo"
    in "bar.foo".
  - [New] <shift-tab> can now be used to jump tab stops in reverse order.

==============================================================================
DISADVANTAGES                                         *snipMate-disadvantages*

snipMate.vim currently has the following disadvantages to TextMate's snippets:
    - There is no $0; the order of tab stops must be explicitly stated.
    - Placeholders within placeholders are not possible. E.g.: >

      '<div${1: id="${2:some_id}}">${3}</div>'
<
      In TextMate this would first highlight ' id="some_id"', and if
      you hit delete it would automatically skip ${2} and go to ${3}
      on the next <tab>, but if you didn't delete it it would highlight
      "some_id" first. You cannot do this in snipMate.vim.
    - Regex cannot be performed on variables, such as "${1/.*/\U&}"
    - Placeholders cannot span multiple lines.
    - Activating snippets in different scopes of the same file is
      not possible.

Perhaps some of these features will be added in a later release.

==============================================================================
CONTACT                                   *snipMate-contact* *snipMate-author*

To contact the author (Michael Sanders), please email:
 msanders42+snipmate <at> gmail <dot> com

I greatly appreciate any suggestions or improvements offered for the script.

==============================================================================

vim:tw=78:ts=8:ft=help:norl:
snippets/objc.snippets	[[[1
184
# #import <...>
snippet Imp
	#import <${1:Cocoa/Cocoa.h}>${2}
# #import "..."
snippet imp
	#import "${1:`Filename()`.h}"${2}
# @selector(...)
snippet sel
	@selector(${1:method}:)${3}
# @"..." string
snippet s
	@"${1}"${2}
# Object
snippet o
	${1:NSObject} *${2:foo} = [${3:$1 alloc}]${4};${5}
# NSLog(...)
snippet log
	NSLog(@"${1:%@}"${2});${3}
# Class
snippet objc
	@interface ${1:`Filename('', 'someClass')`} : ${2:NSObject}
	{
	}
	@end

	@implementation $1
	${3}
	@end
# Class Interface
snippet int
	@interface ${1:`Filename('', 'someClass')`} : ${2:NSObject}
	{${3}
	}
	${4}
	@end
# Class Implementation
snippet impl
	@implementation ${1:`Filename('', 'someClass')`}
	${2}
	@end
snippet init
	- (id)init
	{
		[super init];
		return self;
	}
snippet ifself
	if (self = [super init]) {
		${1:/* code */}
	}
	return self;
snippet ibo
	IBOutlet ${1:NSSomeClass} *${2:$1};${3}
# Category
snippet cat
	@interface ${1:NSObject} (${2:Category})
	@end

	@implementation $1 ($2)
	${3}
	@end
# Category Interface
snippet cath
	@interface ${1:NSObject} (${2:Category})
	${3}
	@end
# NSArray
snippet array
	NSMutableArray *${1:array} = [NSMutable array];${2}
# NSDictionary
snippet dict
	NSMutableDictionary *${1:dict} = [NSMutableDictionary dictionary];${2}
# NSBezierPath
snippet bez
	NSBezierPath *${1:path} = [NSBezierPath bezierPath];${2}
# Method
snippet m
	- (${1:id})${2:method}
	{
		${3}
	}
# Method declaration
snippet md
	- (${1:id})${2:method};${3}
# IBAction declaration
snippet ibad
	- (IBAction)${1:method}:(${2:id})sender;${3}
# IBAction method
snippet iba
	- (IBAction)${1:method}:(${2:id})sender
	{
		${3}
	}
# awakeFromNib method
snippet wake
	- (void)awakeFromNib
	{
		${1}
	}
# Class Method
snippet M
	+ (${1:id})${2:method}
	{${3}
		return nil;
	}
# Sub-method (Call super)
snippet sm
	- (${1:id})${2:method}
	{
		[super $2];${3}
		return self;
	}
# Method: Initialize
snippet I
	+ (void) initialize
	{
		[[NSUserDefaults standardUserDefaults] registerDefaults:[NSDictionary dictionaryWIthObjectsAndKeys:
			${1}@"value", @"key",
			nil]];
	}
# Accessor Methods For:
# Object
snippet objacc
	- (${1:id})${2:thing}
	{
		return $2;
	}

	- (void)set$2:($1)${3:new$2}
	{
		[$3 retain];
		[$2 release];
		$2 = $3;
	}${4}
# for (object in array)
snippet forin
	for (${1:Class} *${2:some$1} in ${3:array}) {
		${4}
	}
snippet forarray
	unsigned int ${1:object}Count = [${2:array} count];

	for (unsigned int index = 0; index < $1Count; index++) {
		${3:id} $1 = [$2 $1AtIndex:index];
		${4}
	}
# IBOutlet
# @property (Objective-C 2.0)
snippet prop
	@property (${1:retain}) ${2:NSSomeClass} ${3:*$2};${4}
# @synthesize (Objective-C 2.0)
snippet syn
	@synthesize ${1:property};${2}
# [[ alloc] init]
snippet alloc
	[[${1:foo} alloc] init${2}];${3}
# retain
snippet ret
	[${1:foo} retain];${2}
# release
snippet rel
	[${1:foo} release];
	${2:$1 = nil;}
# autorelease
snippet arel
	[${1:foo} autorelease];
# autorelease pool
snippet pool
	NSAutoreleasePool *${1:pool} = [[NSAutoreleasePool alloc] init];
	${2:/* code */}
	[$1 drain];
# Throw an exception
snippet except
	NSException *${1:badness};
	$1 = [NSException exceptionWithName:@"${2:$1Name}"
	                             reason:@"${3}"
	                           userInfo:nil];
	[$1 raise];
snippet prag
	#pragma mark ${1:foo}
snippet cl
	@class ${1:Foo};${2}
snippet color
	[[NSColor ${1:blackColor}] set];
snippets/_.snippets	[[[1
7
# Global snippets

# (c) holds no legal value ;)
snippet c)
	`&enc[:2] == "utf" ? "©" : "(c)"` Copyright `strftime("%Y")` ${1:`g:snips_author`}. All Rights Reserved.${2}
snippet date
	`strftime("%Y-%m-%d")`
snippets/python.snippets	[[[1
86
snippet #!
	#!/usr/bin/python

snippet imp
	import ${1:module}
# Module Docstring
snippet docs
	'''
	File: ${1:`Filename('$1.py', 'foo.py')`}
	Author: ${2:`g:snips_author`}
	Description: ${3}
	'''
snippet wh
	while ${1:condition}:
		${2:# code...}
snippet for
	for ${1:needle} in ${2:haystack}:
		${3:# code...}
# New Class
snippet cl
	class ${1:ClassName}(${2:object}):
		"""${3:docstring for $1}"""
		def __init__(self, ${4:arg}):
			${5:super($1, self).__init__()}
			self.$4 = $4
			${6}
# New Function
snippet def
	def ${1:fname}(${2:`indent('.') ? 'self' : ''`}):
		"""${3:docstring for $1}"""
		${4:pass}
snippet deff
	def ${1:fname}(${2:`indent('.') ? 'self' : ''`}):
		${3}
# New Method
snippet defs
	def ${1:mname}(self, ${2:arg}):
		${3:pass}
# New Property
snippet property
	def ${1:foo}():
		doc = "${2:The $1 property.}"
		def fget(self):
			${3:return self._$1}
		def fset(self, value):
			${4:self._$1 = value}
# Lambda
snippet ld
	${1:var} = lambda ${2:vars} : ${3:action}
snippet .
	self.
snippet try Try/Except
	try:
		${1:pass}
	except ${2:Exception}, ${3:e}:
		${4:raise $3}
snippet try Try/Except/Else
	try:
		${1:pass}
	except ${2:Exception}, ${3:e}:
		${4:raise $3}
	else:
		${5:pass}
snippet try Try/Except/Finally
	try:
		${1:pass}
	except ${2:Exception}, ${3:e}:
		${4:raise $3}
	finally:
		${5:pass}
snippet try Try/Except/Else/Finally
	try:
		${1:pass}
	except ${2:Exception}, ${3:e}:
		${4:raise $3}
	else:
		${5:pass}
	finally:
		${6:pass}
# if __name__ == '__main__':
snippet ifmain
	if __name__ == '__main__':
		${1:main()}
# __magic__
snippet _
	__${1:init}__${2}
snippets/ruby.snippets	[[[1
420
# #!/usr/bin/ruby
snippet #!
	#!/usr/bin/ruby

# New Block
snippet =b
	=begin rdoc
		${1}
	=end
snippet y
	:yields: ${1:arguments}
snippet rb
	#!/usr/bin/env ruby -wKU

snippet req
	require "${1}"${2}
snippet #
	# =>
snippet end
	__END__
snippet case
	case ${1:object}
	when ${2:condition}
		${3}
	end
snippet when
	when ${1:condition}
		${2}
snippet def
	def ${1:method_name}
		${2}
	end
snippet deft
	def test_${1:case_name}
		${2}
	end
snippet if
	if ${1:condition}
		${2}
	end
snippet ife
	if ${1:condition}
		${2}
	else
		${3}
	end
snippet elsif
	elsif ${1:condition}
		${2}
snippet unless
	unless ${1:condition}
		${2}
	end
snippet while
	while ${1:condition}
		${2}
	end
snippet until
	until ${1:condition}
		${2}
	end
snippet cla class .. end
	class ${1:`substitute(Filename(), '^.', '\u&', '')`}
		${2}
	end
snippet cla class .. initialize .. end
	class ${1:`substitute(Filename(), '^.', '\u&', '')`}
		def initialize(${2:args})
			${3}
		end


	end
snippet cla class .. < ParentClass .. initialize .. end
	class ${1:`substitute(Filename(), '^.', '\u&', '')`} < ${2:ParentClass}
		def initialize(${3:args})
			${4}
		end


	end
snippet cla ClassName = Struct .. do .. end
	${1:`substitute(Filename(), '^.', '\u&', '')`} = Struct.new(:${2:attr_names}) do
		def ${3:method_name}
			${4}
		end


	end
snippet cla class BlankSlate .. initialize .. end
	class ${1:BlankSlate}
		instance_methods.each { |meth| undef_method(meth) unless meth =~ /\A__/ }
snippet cla class << self .. end
	class << ${1:self}
		${2}
	end
# class .. < DelegateClass .. initialize .. end
snippet cla-
	class ${1:`substitute(Filename(), '^.', '\u&', '')`} < DelegateClass(${2:ParentClass})
		def initialize(${3:args})
			super(${4:del_obj})

			${5}
		end


	end
snippet mod module .. end
	module ${1:`substitute(Filename(), '^.', '\u&', '')`}
		${2}
	end
snippet mod module .. module_function .. end
	module ${1:`substitute(Filename(), '^.', '\u&', '')`}
		module_function

		${2}
	end
snippet mod module .. ClassMethods .. end
	module ${1:`substitute(Filename(), '^.', '\u&', '')`}
		module ClassMethods
			${2}
		end

		module InstanceMethods

		end

		def self.included(receiver)
			receiver.extend         ClassMethods
			receiver.send :include, InstanceMethods
		end
	end
# attr_reader
snippet r
	attr_reader :${1:attr_names}
# attr_writer
snippet w
	attr_writer :${1:attr_names}
# attr_accessor
snippet rw
	attr_accessor :${1:attr_names}
# include Enumerable
snippet Enum
	include Enumerable

	def each(&block)
		${1}
	end
# include Comparable
snippet Comp
	include Comparable

	def <=>(other)
		${1}
	end
# extend Forwardable
snippet Forw-
	extend Forwardable
# def self
snippet defs
	def self.${1:class_method_name}
		${2}
	end
# def method_missing
snippet defmm
	def method_missing(meth, *args, &blk)
		${1}
	end
snippet defd
	def_delegator :${1:@del_obj}, :${2:del_meth}, :${3:new_name}
snippet defds
	def_delegators :${1:@del_obj}, :${2:del_methods}
snippet am
	alias_method :${1:new_name}, :${2:old_name}
snippet app
	if __FILE__ == $PROGRAM_NAME
		${1}
	end
# usage_if()
snippet usai
	if ARGV.${1}
		abort "Usage: #{$PROGRAM_NAME} ${2:ARGS_GO_HERE}"${3}
	end
# usage_unless()
snippet usau
	unless ARGV.${1}
		abort "Usage: #{$PROGRAM_NAME} ${2:ARGS_GO_HERE}"${3}
	end
snippet array
	Array.new(${1:10}) { |${2:i}| ${3} }
snippet hash
	Hash.new { |${1:hash}, ${2:key}| $1[$2] = ${3} }
snippet file File.foreach() { |line| .. }
	File.foreach(${1:"path/to/file"}) { |${2:line}| ${3} }
snippet file File.read()
	File.read(${1:"path/to/file"})${2}
snippet Dir Dir.global() { |file| .. }
	Dir.glob(${1:"dir/glob/*"}) { |${2:file}| ${3} }
snippet Dir Dir[".."]
	Dir[${1:"glob/**/*.rb"}]${2}
snippet dir
	Filename.dirname(__FILE__)
snippet deli
	delete_if { |${1:e}| ${2} }
snippet fil
	fill(${1:range}) { |${2:i}| ${3} }
# flatten_once()
snippet flao
	inject(Array.new) { |${1:arr}, ${2:a}| $1.push(*$2)}${3}
snippet zip
	zip(${1:enums}) { |${2:row}| ${3} }
# downto(0) { |n| .. }
snippet dow
	downto(${1:0}) { |${2:n}| ${3} }
snippet ste
	step(${1:2}) { |${2:n}| ${3} }
snippet tim
	times { |${1:n}| ${2} }
snippet upt
	upto(${1:1.0/0.0}) { |${2:n}| ${3} }
snippet loo
	loop { ${1} }
snippet ea
	each { |${1:e}| ${2} }
snippet eab
	each_byte { |${1:byte}| ${2} }
snippet eac- each_char { |chr| .. }
	each_char { |${1:chr}| ${2} }
snippet eac- each_cons(..) { |group| .. }
	each_cons(${1:2}) { |${2:group}| ${3} }
snippet eai
	each_index { |${1:i}| ${2} }
snippet eak
	each_key { |${1:key}| ${2} }
snippet eal
	each_line { |${1:line}| ${2} }
snippet eap
	each_pair { |${1:name}, ${2:val}| ${3} }
snippet eas-
	each_slice(${1:2}) { |${2:group}| ${3} }
snippet eav
	each_value { |${1:val}| ${2} }
snippet eawi
	each_with_index { |${1:e}, ${2:i}| ${3} }
snippet reve
	reverse_each { |${1:e}| ${2} }
snippet inj
	inject(${1:init}) { |${2:mem}, ${3:var}| ${4} }
snippet map
	map { |${1:e}| ${2} }
snippet mapwi-
	enum_with_index.map { |${1:e}, ${2:i}| ${3} }
snippet sor
	sort { |a, b| ${1} }
snippet sorb
	sort_by { |${1:e}| ${2} }
snippet ran
	sort_by { rand }
snippet all
	all? { |${1:e}| ${2} }
snippet any
	any? { |${1:e}| ${2} }
snippet cl
	classify { |${1:e}| ${2} }
snippet col
	collect { |${1:e}| ${2} }
snippet det
	detect { |${1:e}| ${2} }
snippet fet
	fetch(${1:name}) { |${2:key}| ${3} }
snippet fin
	find { |${1:e}| ${2} }
snippet fina
	find_all { |${1:e}| ${2} }
snippet gre
	grep(${1:/pattern/}) { |${2:match}| ${3} }
snippet sub
	${1:g}sub(${2:/pattern/}) { |${3:match}| ${4} }
snippet sca
	scan(${1:/pattern/}) { |${2:match}| ${3} }
snippet max
	max { |a, b|, ${1} }
snippet min
	min { |a, b|, ${1} }
snippet par
	partition { |${1:e}|, ${2} }
snippet rej
	reject { |${1:e}|, ${2} }
snippet sel
	select { |${1:e}|, ${2} }
snippet lam
	lambda { |${1:args}| ${2} }
snippet do
	do |${1:variable}|
		${2}
	end
snippet :
	:${1:key} => ${2:"value"}${3}
snippet ope
	open(${1:"path/or/url/or/pipe"}, "${2:w}") { |${3:io}| ${4} }
# path_from_here()
snippet patfh
	File.join(File.dirname(__FILE__), *%2[${1:rel path here}])${2}
# unix_filter {}
snippet unif
	ARGF.each_line${1} do |${2:line}|
		${3}
	end
# option_parse {}
snippet optp
	require "optparse"

	options = {${1:default => "args"}}

	ARGV.options do |opts|
		opts.banner = "Usage: #{File.basename($PROGRAM_NAME)}
snippet opt
	opts.on( "-${1:o}", "--${2:long-option-name}", ${3:String},
	         "${4:Option description.}") do |${5:opt}|
		${6}
	end
snippet tc
	require "test/unit"

	require "${1:library_file_name}"

	class Test${2:$1} < Test::Unit::TestCase
		def test_${3:case_name}
			${4}
		end
	end
snippet ts
	require "test/unit"

	require "tc_${1:test_case_file}"
	require "tc_${2:test_case_file}"${3}
snippet as
	assert(${1:test}, "${2:Failure message.}")${3}
snippet ase
	assert_equal(${1:expected}, ${2:actual})${3}
snippet asne
	assert_not_equal(${1:unexpected}, ${2:actual})${3}
snippet asid
	assert_in_delta(${1:expected_float}, ${2:actual_float}, ${3:2 ** -20})${4}
snippet asio
	assert_instance_of(${1:ExpectedClass}, ${2:actual_instance})${3}
snippet asko
	assert_kind_of(${1:ExpectedKind}, ${2:actual_instance})${3}
snippet asn
	assert_nil(${1:instance})${2}
snippet asnn
	assert_not_nil(${1:instance})${2}
snippet asm
	assert_match(/${1:expected_pattern}/, ${2:actual_string})${3}
snippet asnm
	assert_no_match(/${1:unexpected_pattern}/, ${2:actual_string})${3}
snippet aso
	assert_operator(${1:left}, :${2:operator}, ${3:right})${4}
snippet asr
	assert_raise(${1:Exception}) { ${2} }
snippet asnr
	assert_nothing_raised(${1:Exception}) { ${2} }
snippet asrt
	assert_respond_to(${1:object}, :${2:method})${3}
snippet ass assert_same(..)
	assert_same(${1:expected}, ${2:actual})${3}
snippet ass assert_send(..)
	assert_send([${1:object}, :${2:message}, ${3:args}])${4}
snippet asns
	assert_not_same(${1:unexpected}, ${2:actual})${3}
snippet ast
	assert_throws(:${1:expected}) { ${2} }
snippet asnt
	assert_nothing_thrown { ${1} }
snippet fl
	flunk("${1:Failure message.}")${2}
# Benchmark.bmbm do .. end
snippet bm-
	TESTS = ${1:10_000}
	Benchmark.bmbm do |results|
		${2}
	end
snippet rep
	results.report("${1:name}:") { TESTS.times { ${2} }}
# Marshal.dump(.., file)
snippet Md
	File.open(${1:"path/to/file.dump"}, "wb") { |${2:file}| Marshal.dump(${3:obj}, $2) }${4}
# Mashal.load(obj)
snippet Ml
	File.open(${1:"path/to/file.dump"}, "rb") { |${2:file}| Marshal.load($2) }${3}
# deep_copy(..)
snippet deec
	Marshal.load(Marshal.dump(${1:obj_to_copy}))${2}
snippet Pn-
	PStore.new(${1:"file_name.pstore"})${2}
snippet tra
	transaction(${1:true}) { ${2} }
# xmlread(..)
snippet xml-
	REXML::Document.new(File.read(${1:"path/to/file"}))${2}
# xpath(..) { .. }
snippet xpa
	elements.each(${1:"//Xpath"}) do |${2:node}|
		${3}
	end
# class_from_name()
snippet clafn
	split("::").inject(Object) { |par, const| par.const_get(const) }
# singleton_class()
snippet sinc
	class << self; self end
snippet nam
	namespace :${1:`Filename()`} do
		${2}
	end
snippet tas
	desc "${1:Task description\}"
	task :${2:task_name => [:dependent, :tasks]} do
		${3}
	end
snippets/java.snippets	[[[1
78
snippet main
	public static void main (String [] args)
	{
		${1:/* code */}
	}
snippet pu
	public
snippet po
	protected
snippet pr
	private
snippet st
	static
snippet fi
	final
snippet ab
	abstract
snippet re
	return
snippet br
	break;
snippet de
	default:
		${1}
snippet ca
	catch(${1:Exception} ${2:e}) ${3}
snippet th
	throw 
snippet sy
	synchronized
snippet im
	import
snippet j.u
	java.util
snippet j.i
	java.io.
snippet j.b
	java.beans.
snippet j.n
	java.net.
snippet j.m
	java.math.
snippet if
	if (${1}) ${2}
snippet el
	else 
snippet elif
	else if (${1}) ${2}
snippet wh
	while (${1}) ${2}
snippet for
	for (${1}; ${2}; ${3}) ${4}
snippet fore
	for (${1} : ${2}) ${3}
snippet sw
	switch (${1}) ${2}
snippet cs
	case ${1}:
		${2}
	${3}
snippet tc
	public class ${1:`Filename()`} extends ${2:TestCase}
snippet t
	public void test${1:Name}() throws Exception ${2}
snippet cl
	class ${1:`Filename("", "untitled")`} ${2}
snippet in
	interface ${1:`Filename("", "untitled")`} ${2:extends Parent}${3}
snippet m
	${1:void} ${2:method}(${3}) ${4:throws }${5}
snippet v
	${1:String} ${2:var}${3: = null}${4};${5}
snippet co
	static public final ${1:String} ${2:var} = ${3};${4}
snippet cos
	static public final String ${1:var} = "${2}";${3}
snippet as
	assert ${1:test} : "${2:Failure message}";${3}
snippets/cpp.snippets	[[[1
30
# Read File Into Vector
snippet readfile
	std::vector<char> v;
	if (FILE *${2:fp} = fopen(${1:"filename"}, "r")) {
		char buf[1024];
		while (size_t len = fread(buf, 1, sizeof(buf), $2))
			v.insert(v.end(), buf, buf + len);
		fclose($2);
	}${3}
# std::map
snippet map
	std::map<${1:key}, ${2:value}> map${3};
# std::vector
snippet vector
	std::vector<${1:char}> v${2};
# Namespace
snippet ns
	namespace ${1:`Filename('', 'my')`} {
		${2}
	} /* $1 */
# Class
snippet cl
	class ${1:`Filename('$1_t', 'name')`} {
	public:
		$1 (${2:arguments});
		virtual ~$1 ();
	
	private:
		${3:/* data */}
	};
snippets/tcl.snippets	[[[1
92
# #!/usr/bin/tclsh
snippet #!
	#!/usr/bin/tclsh
	
# Process
snippet pro
	proc ${1:function_name} {${2:args}} {
		${3:#body ...}
	}
#xif
snippet xif
	${1:expr}? ${2:true} : ${3:false}
# Conditional
snippet if
	if {${1}} {
		${2:# body...}
	}
# Conditional if..else
snippet ife
	if {${1}} {
		${2:# body...}
	} else {
		${3:# else...}
	}
# Conditional if..elsif..else
snippet ifee
	if {${1}} {
		${2:# body...}
	} elseif {${3}} {
		${4:# elsif...}
	} else {
		${5:# else...}
	}
# If catch then
snippet ifc
	if { [catch {${1:#do something...}} ${2:err}] } {
		${3:# handle failure...}
	}
# Catch
snippet catch
	catch {${1}} ${2:err} ${3:options}
# While Loop
snippet wh
	while {${1}} {
		${2:# body...}
	}
# For Loop
snippet for
	for {set ${2:var} 0} {$$2 < ${1:count}} {${3:incr} $2} {
		${4:# body...}
	}
# Foreach Loop
snippet fore
	foreach ${1:x} {${2:#list}} {
		${3:# body...}
	}
# after ms script...
snippet af
	after ${1:ms} ${2:#do something}
# after cancel id
snippet afc
	after cancel ${1:id or script}
# after idle
snippet afi
	after idle ${1:script}
# after info id
snippet afin
	after info ${1:id}
# Expr
snippet exp
	expr {${1:#expression here}}
# Switch
snippet sw
	switch ${1:var} {
		${3:pattern 1} {
			${4:#do something}
		}
		default {
			${2:#do something}
		}
	}
# Case
snippet ca
	${1:pattern} {
		${2:#do something}
	}${3}
# Namespace eval
snippet ns
	namespace eval ${1:path} {${2:#script...}}
# Namespace current
snippet nsc
	namespace current
snippets/c.snippets	[[[1
110
# main()
snippet main
	int main(int argc, const char *argv[])
	{
		${1}
		return 0;
	}
# #include <...>
snippet inc
	#include <${1:stdio}.h>${2}
# #include "..."
snippet Inc
	#include "${1:`Filename("$1.h")`}"${2}
# #ifndef ... #define ... #endif
snippet Def
	#ifndef $1
	#define ${1:SYMBOL} ${2:value}
	#endif${3}
snippet def
	#define 
snippet ifdef
	#ifdef ${1:FOO}
		${2:#define }
	#endif
snippet #if
	#if ${1:FOO}
		${2}
	#endif
# Header Include-Guard
# (the randomizer code is taken directly from TextMate; it could probably be
# cleaner, I don't know how to do it in vim script)
snippet once
	#ifndef ${1:`toupper(Filename('', 'UNTITLED').'_'.system("/usr/bin/ruby -e 'print (rand * 2821109907455).round.to_s(36)'"))`}

	#define $1

	${2}

	#endif /* end of include guard: $1 */
# If Condition
snippet if
	if (${1:/* condition */}) {
		${2:/* code */}
	}
snippet el
	else {
		${1}
	}
# Tertiary conditional
snippet t
	${1:/* condition */} ? ${2:a} : ${3:b}
# Do While Loop
snippet do
	do {
		${2:/* code */}
	} while (${1:/* condition */});
# While Loop
snippet wh
	while (${1:/* condition */}) {
		${2:/* code */}
	}
# For Loop
snippet for
	for (${2:i} = 0; $2 < ${1:count}; $2${3:++}) {
		${4:/* code */}
	}
# Custom For Loop
snippet forr
	for (${1:i} = ${2:0}; ${3:$1 < 10}; $1${4:++}) {
		${5:/* code */}
	}
# Function
snippet fun
	${1:void} ${2:function_name}(${3})
	{
		${4:/* code */}
	}
# Function Declaration
snippet fund
	${1:void} ${2:function_name}(${3});${4}
# Typedef
snippet td
	typedef ${1:int} ${2:MyCustomType};${3}
# Struct
snippet st
	struct ${1:`Filename('$1_t', 'name')`} {
		${2:/* data */}
	}${3: /* optional variable list */};${4}
# Typedef struct
snippet tds
	typedef struct ${2:_$1 }{
		${3:/* data */}
	} ${1:`Filename('$1_t', 'name')`};
# Typdef enum
snippet tde
	typedef enum {
		${1:/* data */}
	} ${2:foo};
# printf
# unfortunately version this isn't as nice as TextMates's, given the lack of a
# dynamic `...`
snippet pr
	printf("${1:%s}\n"${2});${3}
# fprintf (again, this isn't as nice as TextMate's version, but it works)
snippet fpr
	fprintf(${1:stderr}, "${2:%s}\n"${3});${4}
snippet .
	[${1}]${2}
snippet un
	unsigned
snippets/snippet.snippets	[[[1
7
# snippets for making snippets :)
snippet snip
	snippet ${1:trigger}
		${2}
snippet msnip
	snippet ${1:trigger} ${2:description}
		${3}
snippets/mako.snippets	[[[1
54
snippet def
	<%def name="${1:name}">
		${2:}
	</%def>
snippet call
	<%call expr="${1:name}">
		${2:}
	</%call>
snippet doc
	<%doc>
		${1:}
	</%doc>
snippet text
	<%text>
		${1:}
	</%text>
snippet for
	% for ${1:i} in ${2:iter}:
		${3:}
	% endfor
snippet if if
	% if ${1:condition}:
		${2:}
	% endif
snippet if if/else
	% if ${1:condition}:
		${2:}
	% else:
		${3:}
	% endif
snippet try
	% try:
		${1:}
	% except${2:}:
		${3:pass}
	% endtry
snippet wh
	% while ${1:}:
		${2:}
	% endwhile
snippet $
	${ ${1:} }
snippet <%
	<% ${1:} %>
snippet <!%
	<!% ${1:} %>
snippet inherit
	<%inherit file="${1:filename}" />
snippet include
	<%include file="${1:filename}" />
snippet namespace
	<%namespace file="${1:name}" />
snippet page
	<%page args="${1:}" />
snippets/php.snippets	[[[1
216
snippet php
	<?php
	${1}
	?>
snippet ec
	echo "${1:string}"${2};
snippet inc
	include '${1:file}';${2}
snippet inc1
	include_once '${1:file}';${2}
snippet req
	require '${1:file}';${2}
snippet req1
	require_once '${1:file}';${2}
# $GLOBALS['...']
snippet globals
	$GLOBALS['${1:variable}']${2: = }${3:something}${4:;}${5}
snippet $_ COOKIE['...']
	$_COOKIE['${1:variable}']${2}
snippet $_ ENV['...']
	$_ENV['${1:variable}']${2}
snippet $_ FILES['...']
	$_FILES['${1:variable}']${2}
snippet $_ Get['...']
	$_GET['${1:variable}']${2}
snippet $_ POST['...']
	$_POST['${1:variable}']${2}
snippet $_ REQUEST['...']
	$_REQUEST['${1:variable}']${2}
snippet $_ SERVER['...']
	$_SERVER['${1:variable}']${2}
snippet $_ SESSION['...']
	$_SESSION['${1:variable}']${2}
# Start Docblock
snippet /*
	/**
	 * ${1}
	 **/
# Class - post doc
snippet doc_cp
	/**
	 * ${1:undocumented class}
	 *
	 * @package ${2:default}
	 * @author ${3:`g:snips_author`}
	**/${4}
# Class Variable - post doc
snippet doc_vp
	/**
	 * ${1:undocumented class variable}
	 *
	 * @var ${2:string}
	 **/${3}
# Class Variable
snippet doc_v
	/**
	 * ${3:undocumented class variable}
	 *
	 * @var ${4:string}
	 **/
	${1:var} $${2};${5}
# Class
snippet doc_c
	/**
	 * ${3:undocumented class}
	 *
	 * @packaged ${4:default}
	 * @author ${5:`g:snips_author`}
	 **/
	${1:}class ${2:}
	{${6}
	} // END $1class $2
# Constant Definition - post doc
snippet doc_dp
	/**
	 * ${1:undocumented constant}
	 **/${2}
# Constant Definition
snippet doc_d
	/**
	 * ${3:undocumented constant}
	 **/
	define(${1}, ${2});${4}
# Function - post doc
snippet doc_fp
	/**
	 * ${1:undocumented function}
	 *
	 * @return ${2:void}
	 * @author ${3:`g:snips_author`}
	 **/${4}
# Function signature
snippet doc_s
	/**
	 * ${4:undocumented function}
	 *
	 * @return ${5:void}
	 * @author ${6:`g:snips_author`}
	 **/
	${1}function ${2}(${3});${7}
# Function
snippet doc_f
	/**
	 * ${4:undocumented function}
	 *
	 * @return ${5:void}
	 * @author ${6:`g:snips_author`}
	 **/
	${1}function ${2}(${3})
	{${7}
	}
# Header
snippet doc_h
	/**
	 * ${1}
	 *
	 * @author ${2:`g:snips_author`}
	 * @version ${3:$Id$}
	 * @copyright ${4:$2}, `strftime('%d %B, %Y')`
	 * @package ${5:default}
	 **/
	
	/**
	 * Define DocBlock
	 *//
# Interface
snippet doc_i
	/**
	 * ${2:undocumented class}
	 *
	 * @package ${3:default}
	 * @author ${4:`g:snips_author`}
	 **/
	interface ${1:}
	{${5}
	} // END interface $1
# class ...
snippet class
	/**
	 * ${1}
	 **/
	class ${2:ClassName}
	{
		${3}
		function ${4:__construct}(${5:argument})
		{
			${6:// code...}
		}
	}
# define(...)
snippet def
	define('${1}'${2});${3}
# defined(...)
snippet def?
	${1}defined('${2}')${3}
snippet wh
	while (${1:/* condition */}) {
		${2:// code...}
	}
# do ... while
snippet do
	do {
		${2:// code... }
	} while (${1:/* condition */});
snippet if
	if (${1:/* condition */}) {
		${2:// code...}
	}
snippet ife
	if (${1:/* condition */}) {
		${2:// code...}
	} else {
		${3:// code...}
	}
	${4}
snippet else
	else {
		${1:// code...}
	}
snippet elseif
	elseif (${1:/* condition */}) {
		${2:// code...}
	}
# Tertiary conditional
snippet t
	$${1:retVal} = (${2:condition}) ? ${3:a} : ${4:b};${5}
snippet switch
	switch ($${1:variable}) {
		case '${2:value}':
			${3:// code...}
			break;
		${5}
		default:
			${4:// code...}
			break;
	}
snippet case
	case '${1:value}':
		${2:// code...}
		break;${3}
snippet for
	for ($${2:i} = 0; $$2 < ${1:count}; $$2${3:++}) {
		${4: // code...}
	}
snippet foreach
	foreach ($${1:variable} as $${2:key}) {
		${3:// code...}
	}
snippet fun
	${1:public }function ${2:FunctionName}(${3})
	{
		${4:// code...}
	}
# $... = array (...)
snippet array
	$${1:arrayName} = array('${2}' => ${3});${4}
snippets/vim.snippets	[[[1
32
snippet header
	" File: ${1:`expand('%:t')`}
	" Author: ${2:`g:snips_author`}
	" Description: ${3}
	${4:" Last Modified: `strftime("%B %d, %Y")`}
snippet guard
	if exists('${1:did_`Filename()`}') || &cp${2: || version < 700}
		finish
	endif
	let $1 = 1${3}
snippet f
	fun ${1:function_name}(${2})
		${3:" code}
	endf
snippet for
	for ${1:needle} in ${2:haystack}
		${3:" code}
	endfor
snippet wh
	while ${1:condition}
		${2:" code}
	endw
snippet if
	if ${1:condition}
		${2:" code}
	endif
snippet ife
	if ${1:condition}
		${2}
	else
		${3}
	endif
snippets/tex.snippets	[[[1
115
# \begin{}...\end{}
snippet begin
	\begin{${1:env}}
		${2}
	\end{$1}
# Tabular
snippet tab
	\begin{${1:tabular}}{${2:c}}
	${3}
	\end{$1}
# Align(ed)
snippet ali
	\begin{align${1:ed}}
		${2}
	\end{align$1}
# Gather(ed)
snippet gat
	\begin{gather${1:ed}}
		${2}
	\end{gather$1}
# Equation
snippet eq
	\begin{equation}
		${1}
	\end{equation}
# Unnumbered Equation
snippet \
	\\[
		${1}
	\\]
# Enumerate
snippet enum
	\begin{enumerate}
		\item ${1}
	\end{enumerate}
# Itemize
snippet item
	\begin{itemize}
		\item ${1}
	\end{itemize}
# Description
snippet desc
	\begin{description}
		\item[${1}] ${2}
	\end{description}
# Matrix
snippet mat
	\begin{${1:p/b/v/V/B/small}matrix}
		${2}
	\end{$1matrix}
# Cases
snippet cas
	\begin{cases}
		${1:equation}, &\text{ if }${2:case}\\
		${3}
	\end{cases}
# Split
snippet spl
	\begin{split}
		${1}
	\end{split}
# Part
snippet part
	\part{${1:part name}} % (fold)
	\label{prt:${2:$1}}
	${3}
	% part $2 (end)
# Chapter
snippet cha
	\chapter{${1:chapter name}} % (fold)
	\label{cha:${2:$1}}
	${3}
	% chapter $2 (end)
# Section
snippet sec
	\section{${1:section name}} % (fold)
	\label{sec:${2:$1}}
	${3}
	% section $2 (end)
# Sub Section
snippet sub
	\subsection{${1:subsection name}} % (fold)
	\label{sub:${2:$1}}
	${3}
	% subsection $2 (end)
# Sub Sub Section
snippet subs
	\subsubsection{${1:subsubsection name}} % (fold)
	\label{ssub:${2:$1}}
	${3}
	% subsubsection $2 (end)
# Paragraph
snippet par
	\paragraph{${1:paragraph name}} % (fold)
	\label{par:${2:$1}}
	${3}
	% paragraph $2 (end)
# Sub Paragraph
snippet subp
	\subparagraph{${1:subparagraph name}} % (fold)
	\label{subp:${2:$1}}
	${3}
	% subparagraph $2 (end)
snippet itd
	\item[${1:description}] ${2:item}
snippet figure
	${1:Figure}~\ref{${2:fig:}}${3}
snippet table
	${1:Table}~\ref{${2:tab:}}${3}
snippet listing
	${1:Listing}~\ref{${2:list}}${3}
snippet section
	${1:Section}~\ref{${2:sec:}}${3}
snippet page
	${1:page}~\pageref{${2}}${3}
snippets/perl.snippets	[[[1
91
# #!/usr/bin/perl
snippet #!
	#!/usr/bin/perl
	
# Hash Pointer
snippet .
	 =>
# Function
snippet sub
	sub ${1:function_name} {
		${2:#body ...}
	}
# Conditional
snippet if
	if (${1}) {
		${2:# body...}
	}
# Conditional if..else
snippet ife
	if (${1}) {
		${2:# body...}
	} else {
		${3:# else...}
	}
# Conditional if..elsif..else
snippet ifee
	if (${1}) {
		${2:# body...}
	} elsif (${3}) {
		${4:# elsif...}
	} else {
		${5:# else...}
	}
# Conditional One-line
snippet xif
	${1:expression} if ${2:condition};${3}
# Unless conditional
snippet unless
	unless (${1}) {
		${2:# body...}
	}
# Unless conditional One-line
snippet xunless
	${1:expression} unless ${2:condition};${3}
# Try/Except
snippet eval
	eval {
		${1:# do something risky...}
	};
	if ($@) {
		${2:# handle failure...}
	}
# While Loop
snippet wh
	while (${1}) {
		${2:# body...}
	}
# While Loop One-line
snippet xwh
	${1:expression} while ${2:condition};${3}
# For Loop
snippet for
	for (my $${2:var} = 0; $$2 < ${1:count}; $$2${3:++}) {
		${4:# body...}
	}
# Foreach Loop
snippet fore
	foreach my $${1:x} (@${2:array}) {
		${3:# body...}
	}
# Foreach Loop One-line
snippet xfore
	${1:expression} foreach @${2:array};${3}
# Package
snippet cl
	package ${1:ClassName};
	
	use base qw(${2:ParentClass});
	
	sub new {
		my $class = shift;
		$class = ref $class if ref $class;
		my $self = bless {}, $class;
		$self;
	}
	
	1;${3}
# Read File
snippet slurp
	my $${1:var};
	{ local $/ = undef; local *FILE; open FILE, "<${2:file}"; $$1 = <FILE>; close FILE }${3}
snippets/html.snippets	[[[1
190
# Some useful Unicode entities
# Non-Breaking Space
snippet nbs
	&nbsp;
# ←
snippet left
	&#x2190;
# →
snippet right
	&#x2192;
# ↑
snippet up
	&#x2191;
# ↓
snippet down
	&#x2193;
# ↩
snippet return
	&#x21A9;
# ⇤
snippet backtab
	&#x21E4;
# ⇥
snippet tab
	&#x21E5;
# ⇧
snippet shift
	&#x21E7;
# ⌃
snippet control
	&#x2303;
# ⌅
snippet enter
	&#x2305;
# ⌘
snippet command
	&#x2318;
# ⌥
snippet option
	&#x2325;
# ⌦
snippet delete
	&#x2326;
# ⌫
snippet backspace
	&#x232B;
# ⎋
snippet escape
	&#x238B;
# Generic Doctype
snippet doctype HTML 4.01 Strict
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN""
	"http://www.w3.org/TR/html4/strict.dtd">
snippet doctype HTML 4.01 Transitional
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN""
	"http://www.w3.org/TR/html4/loose.dtd">
snippet doctype HTML 5
	<!DOCTYPE HTML>
snippet doctype XHTML 1.0 Frameset
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
snippet doctype XHTML 1.0 Strict
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
snippet doctype XHTML 1.0 Transitional
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
snippet doctype XHTML 1.1
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
	"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
# HTML Doctype 4.01 Strict
snippet docts
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN""
	"http://www.w3.org/TR/html4/strict.dtd">
# HTML Doctype 4.01 Transitional
snippet doct
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN""
	"http://www.w3.org/TR/html4/loose.dtd">
# HTML Doctype 5
snippet doct5
	<!DOCTYPE HTML>
# XHTML Doctype 1.0 Frameset
snippet docxf
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">
# XHTML Doctype 1.0 Strict
snippet docxs
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
# XHTML Doctype 1.0 Transitional
snippet docxt
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
# XHTML Doctype 1.1
snippet docx
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
	"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
snippet html
	<html>
	${1}
	</html>
snippet xhtml
	<html xmlns="http://www.w3.org/1999/xhtml">
	${1}
	</html>
snippet body
	<body>
		${1}
	</body>
snippet head
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8"`Close()`>

		<title>${1:`substitute(Filename('', 'Page Title'), '^.', '\u&', '')`}</title>
		${2}
	</head>
snippet title
	<title>${1:`substitute(Filename('', 'Page Title'), '^.', '\u&', '')`}</title>${2}
snippet script
	<script type="text/javascript" charset="utf-8">
		${1}
	</script>${2}
snippet scriptsrc
	<script src="${1}.js" type="text/javascript" charset="utf-8"></script>${2}
snippet style
	<style type="text/css" media="${1:screen}">
		${2}
	</style>${3}
snippet base
	<base href="${1}" target="${2}"`Close()`>
snippet r
	<br`Close()[1:]`>
snippet div
	<div id="${1:name}">
		${2}
	</div>
# Embed QT Movie
snippet movie
	<object width="$2" height="$3" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B"
	 codebase="http://www.apple.com/qtactivex/qtplugin.cab">
		<param name="src" value="$1"`Close()`>
		<param name="controller" value="$4"`Close()`>
		<param name="autoplay" value="$5"`Close()`>
		<embed src="${1:movie.mov}"
			width="${2:320}" height="${3:240}"
			controller="${4:true}" autoplay="${5:true}"
			scale="tofit" cache="true"
			pluginspage="http://www.apple.com/quicktime/download/"
		`Close()[1:]`>
	</object>${6}
snippet fieldset
	<fieldset id="$1">
		<legend>${1:name}</legend>

		${3}
	</fieldset>
snippet form
	<form action="${1:`Filename('$1_submit')`}" method="${2:get}" accept-charset="utf-8">
		${3}


	<p><input type="submit" value="Continue &rarr;"`Close()`></p>
	</form>
snippet h1
	<h1 id="${1:heading}">${2:$1}</h1>
snippet input
	<input type="${1:text/submit/hidden/button}" name="${2:some_name}" value="${3}"`Close()`>${4}
snippet label
	<label for="${2:$1}">${1:name}</label><input type="${3:text/submit/hidden/button}" name="${4:$2}" value="${5}" id="${6:$2}"`Close()`>${7}
snippet link
	<link rel="${1:stylesheet}" href="${2:/css/master.css}" type="text/css" media="${3:screen}" charset="utf-8"`Close()`>${4}
snippet mailto
	<a href="mailto:${1:joe@example.com}?subject=${2:feedback}">${3:email me}</a>
snippet meta
	<meta name="${1:name}" content="${2:content}"`Close()`>${3}
snippet opt
	<option value="${1:option}">${2:$1}</option>${3}
snippet optt
	<option>${1:option}</option>${2}
snippet select
	<select name="${1:some_name}" id="${2:$1}">
		<option value="${3:option}">${4:$3}</option>
	</select>${5}
snippet table
	<table border="${1:0}">
		<tr><th>${2:Header}</th></tr>
		<tr><th>${3:Data}</th></tr>
	</table>${4}
snippet textarea
	<textarea name="${1:Name}" rows="${2:8}" cols="${3:40}">${4}</textarea>${5}
snippets/zsh.snippets	[[[1
58
# #!/bin/zsh
snippet #!
	#!/bin/zsh

snippet if
	if ${1:condition}; then
		${2:# statements}
	fi
snippet ife
	if ${1:condition}; then
		${2:# statements}
	else
		${3:# statements}
	fi
snippet elif
	elif ${1:condition} ; then
		${2:# statements}
snippet for
	for (( ${2:i} = 0; $2 < ${1:count}; $2++ )); do
		${3:# statements}
	done
snippet fore
	for ${1:item} in ${2:list}; do
		${3:# statements}
	done
snippet wh
	while ${1:condition}; do
		${2:# statements}
	done
snippet until
	until ${1:condition}; do
		${2:# statements}
	done
snippet repeat
	repeat ${1:integer}; do
		${2:# statements}
	done
snippet case
	case ${1:word} in
		${2:pattern})
			${3};;
	esac
snippet select
	select ${1:answer} in ${2:choices}; do
		${3:# statements}
	done
snippet (
	( ${1:#statements} )
snippet {
	{ ${1:#statements} }
snippet [
	[[ ${1:test} ]]
snippet always
	{ ${1:try} } always { ${2:always} }
snippet fun
	function ${1:name} (${2:args}) {
		${3:# body}
	}
snippets/autoit.snippets	[[[1
66
snippet if
	If ${1:condition} Then
		${2:; True code}
	EndIf
snippet el
	Else
		${1}
snippet elif
	ElseIf ${1:condition} Then
		${2:; True code}
# If/Else block
snippet ifel
	If ${1:condition} Then
		${2:; True code}
	Else
		${3:; Else code}
	EndIf
# If/ElseIf/Else block
snippet ifelif
	If ${1:condition 1} Then
		${2:; True code}
	ElseIf ${3:condition 2} Then
		${4:; True code}
	Else
		${5:; Else code}
	EndIf
# Switch block
snippet switch
	Switch (${1:condition})
	Case {$2:case1}:
		{$3:; Case 1 code}
	Case Else:
		{$4:; Else code}
	EndSwitch
# Select block
snippet select
	Select (${1:condition})
	Case {$2:case1}:
		{$3:; Case 1 code}
	Case Else:
		{$4:; Else code}
	EndSelect
# While loop
snippet while
	While (${1:condition})
		${2:; code...}
	WEnd
# For loop
snippet for
	For ${1:n} = ${3:1} to ${2:count}
		${4:; code...}
	Next
# New Function
snippet func
	Func ${1:fname}(${2:`indent('.') ? 'self' : ''`}):
		${4:Return}
	EndFunc
# Message box
snippet msg
	MsgBox(${3:MsgType}, ${1:"Title"}, ${2:"Message Text"})
# Debug Message
snippet debug
	MsgBox(0, "Debug", ${1:"Debug Message"})
# Show Variable Debug Message
snippet showvar
	MsgBox(0, "${1:VarName}", $1)
snippets/javascript.snippets	[[[1
74
# Prototype
snippet proto
	${1:class_name}.prototype.${2:method_name} =
	function(${3:first_argument}) {
		${4:// body...}
	};
# Function
snippet fun
	function ${1:function_name} (${2:argument}) {
		${3:// body...}
	}
# Anonymous Function
snippet f
	function(${1}) {${2}};
# if
snippet if
	if (${1:true}) {${2}};
# if ... else
snippet ife
	if (${1:true}) {${2}}
	else{${3}};
# tertiary conditional
snippet t
	${1:/* condition */} ? ${2:a} : ${3:b}
# switch
snippet switch
	switch(${1:expression}) {
		case '${3:case}':
			${4:// code}
			break;
		${5}
		default:
			${2:// code}
	}
# case
snippet case
	case '${1:case}':
		${2:// code}
		break;
	${3}
# for (...) {...}
snippet for
	for (var ${2:i} = 0; $2 < ${1:Things}.length; $2${3:++}) {
		${4:$1[$2]}
	};
# for (...) {...} (Improved Native For-Loop)
snippet forr
	for (var ${2:i} = ${1:Things}.length - 1; $2 >= 0; $2${3:--}) {
		${4:$1[$2]}
	};
# while (...) {...}
snippet wh
	while (${1:/* condition */}) {
		${2:/* code */}
	}
# do...while
snippet do
	do {
		${2:/* code */}
	} while (${1:/* condition */});
# Object Method
snippet :f
	${1:method_name}: function(${2:attribute}) {
		${4}
	}${3:,}
# setTimeout function
snippet timeout
	setTimeout(function() {${3}}${2}, ${1:10};
# Get Elements
snippet get
	getElementsBy${1:TagName}('${2}')${3}
# Get Element
snippet gett
	getElementBy${1:Id}('${2}')${3}
snippets/sh.snippets	[[[1
28
# #!/bin/bash
snippet #!
	#!/bin/bash
	
snippet if
	if [[ ${1:condition} ]]; then
		${2:#statements}
	fi
snippet elif
	elif [[ ${1:condition} ]]; then
		${2:#statements}
snippet for
	for (( ${2:i} = 0; $2 < ${1:count}; $2++ )); do
		${3:#statements}
	done
snippet wh
	while [[ ${1:condition} ]]; do
		${2:#statements}
	done
snippet until
	until [[ ${1:condition} ]]; do
		${2:#statements}
	done
snippet case
	case ${1:word} in
		${2:pattern})
			${3};;
	esac
snippets/jalv2/adcdep.snippet	[[[1
10
-- speficy the number of channels
const byte ADC_NCHANNEL = ${1:1}
-- high or low resolution ?
const bit ADC_HIGH_RESOLUTION = ${2:low}
-- Any voltage references ?
const byte ADC_NVREF = ${3:0}
include adc
adc_init()
${4:-- code}

snippets/jalv2/adcindep.snippet	[[[1
9
-- high or low resolution ?
const bit ADC_HIGH_RESOLUTION = ${1:low}
-- Any voltage references ?
const byte ADC_NVREF = ${2:0}
include adc
adc_init()
-- Specify which pins should be configured as analog
${3:set_analog_pin(1)} -- configure AN1

snippets/jalv2/crum.snippet	[[[1
9
-- describe hardware setup by declaring plugged jumpers
const bit CRUMBOARD_LED1_JP1 = on   -- we've put a jumper in JP1 (use LED D1)
const bit CRUMBOARD_LED2_JP2 = on   -- and also on JP2 (use LED D2)
const bit CRUMBOARD_SW1_JP3  = on   -- we've put a jumper in JP3 (use switch SW1)
const bit CRUMBOARD_SW2_JP4  = on   -- and also on JP2 (use switch SW2)
-- now we can include crumboard library
include crumboard_shield
crumboard_init()

snippets/jalv2/'get.snippet	[[[1
5
function ${1:pseudovar}'get() return ${2:byte} is
   ${3:-- code here, don't forget to check returned type}
   return ${4:something}
end function

snippets/jalv2/'put.snippet	[[[1
4
procedure ${1:pseudovar}'put(${2:byte} in data) is
   ${3:-- code here, don't forget to check input data type}
end procedure

snippets/jalv2/serhw.snippet	[[[1
6
-- baudrate
const serial_hw_baudrate = ${1:115_200} -- or 19_200, 9_600, 2_400...
include serial_hardware
serial_hw_init()
${2:-- code}

snippets/jalv2/sersw.snippet	[[[1
15
-- baudrate
const serial_sw_baudrate = ${1:9_600} -- or 19_200, 2_400, ...
-- RX/TX pins
alias serial_sw_tx_pin is pin_${2:A5}
alias serial_sw_rx_pin is pin_${3:A6}
alias serial_sw_tx_pin_direction is pin_$2_direction
alias serial_sw_rx_pin_direction is pin_$3_direction
serial_sw_tx_pin_direction = output
serial_sw_rx_pin_direction = input
-- inverted levels (usually it is)
const serial_sw_invert = ${4:TRUE}
include serial_software
serial_sw_init()
${5:-- code}

snippets/jalv2/jsg.snippet	[[[1
16
-- Title: ${1:title, very small description}
-- Author: ${2:author's name}, Copyright (c) ${3:year}, all rights reserved.
-- Adapted-by: ${4:adapters' name, comma seperated}
-- Compiler: ${5:last compiler version used to test this code}
-- 
-- This file is part of ${6:jallib or jaluino} (http://$6.googlecode.com)
-- Released under the BSD license (http://www.opensource.org/licenses/bsd-license.php)
--
-- Sources: ${7:if relevant, specify what sources of informations you use: website, article, specifications, appnotes, etc...} 
-- 
-- Description: ${8:describe what is the functional purpose of this lib}
--
-- Notes: ${9:put here information not related to functional description}
--

${10 -- put your code here !}
syntax/snippet.vim	[[[1
19
" Syntax highlighting for snippet files (used for snipMate.vim)
" Hopefully this should make snippets a bit nicer to write!
syn match snipComment '^#.*'
syn match placeHolder '\${\d\+\(:.\{-}\)\=}' contains=snipCommand
syn match tabStop '\$\d\+'
syn match snipCommand '`.\{-}`'
syn match snippet '^snippet.*' transparent contains=multiSnipText,snipKeyword
syn match multiSnipText '\S\+ \zs.*' contained
syn match snipKeyword '^snippet'me=s+8 contained
syn match snipError "^[^#s\t].*$"

hi link snipComment   Comment
hi link multiSnipText String
hi link snipKeyword   Keyword
hi link snipComment   Comment
hi link placeHolder   Special
hi link tabStop       Special
hi link snipCommand   String
hi link snipError     Error
ftplugin/html_snip_helper.vim	[[[1
10
" Helper function for (x)html snippets
if exists('s:did_snip_helper') || &cp || !exists('loaded_snips')
	finish
endif
let s:did_snip_helper = 1

" Automatically closes tag if in xhtml
fun! Close()
	return stridx(&ft, 'xhtml') == -1 ? '' : ' /'
endf
autoload/snipMate.vim	[[[1
433
fun! Filename(...)
	let filename = expand('%:t:r')
	if filename == '' | return a:0 == 2 ? a:2 : '' | endif
	return !a:0 || a:1 == '' ? filename : substitute(a:1, '$1', filename, 'g')
endf

fun s:RemoveSnippet()
	unl! g:snipPos s:curPos s:snipLen s:endCol s:endLine s:prevLen
	     \ s:lastBuf s:oldWord
	if exists('s:update')
		unl s:startCol s:origWordLen s:update
		if exists('s:oldVars') | unl s:oldVars s:oldEndCol | endif
	endif
	aug! snipMateAutocmds
endf

fun snipMate#expandSnip(snip, col)
	let lnum = line('.') | let col = a:col

	let snippet = s:ProcessSnippet(a:snip)
	" Avoid error if eval evaluates to nothing
	if snippet == '' | return '' | endif

	" Expand snippet onto current position with the tab stops removed
	let snipLines = split(substitute(snippet, '$\d\+\|${\d\+.\{-}}', '', 'g'), "\n", 1)

	let line = getline(lnum)
	let afterCursor = strpart(line, col - 1)
	" Keep text after the cursor
	if afterCursor != "\t" && afterCursor != ' '
		let line = strpart(line, 0, col - 1)
		let snipLines[-1] .= afterCursor
	else
		let afterCursor = ''
		" For some reason the cursor needs to move one right after this
		if line != '' && col == 1 && &ve != 'all' && &ve != 'onemore'
			let col += 1
		endif
	endif

	call setline(lnum, line.snipLines[0])

	" Autoindent snippet according to previous indentation
	let indent = matchend(line, '^.\{-}\ze\(\S\|$\)') + 1
	call append(lnum, map(snipLines[1:], "'".strpart(line, 0, indent - 1)."'.v:val"))

	" Open any folds snippet expands into
	if &fen | sil! exe lnum.','.(lnum + len(snipLines) - 1).'foldopen' | endif

	let [g:snipPos, s:snipLen] = s:BuildTabStops(snippet, lnum, col - indent, indent)

	if s:snipLen
		aug snipMateAutocmds
			au CursorMovedI * call s:UpdateChangedSnip(0)
			au InsertEnter * call s:UpdateChangedSnip(1)
		aug END
		let s:lastBuf = bufnr(0) " Only expand snippet while in current buffer
		let s:curPos = 0
		let s:endCol = g:snipPos[s:curPos][1]
		let s:endLine = g:snipPos[s:curPos][0]

		call cursor(g:snipPos[s:curPos][0], g:snipPos[s:curPos][1])
		let s:prevLen = [line('$'), col('$')]
		if g:snipPos[s:curPos][2] != -1 | return s:SelectWord() | endif
	else
		unl g:snipPos s:snipLen
		" Place cursor at end of snippet if no tab stop is given
		let newlines = len(snipLines) - 1
		call cursor(lnum + newlines, indent + len(snipLines[-1]) - len(afterCursor)
					\ + (newlines ? 0: col - 1))
	endif
	return ''
endf

" Prepare snippet to be processed by s:BuildTabStops
fun s:ProcessSnippet(snip)
	let snippet = a:snip
	" Evaluate eval (`...`) expressions.
	" Using a loop here instead of a regex fixes a bug with nested "\=".
	if stridx(snippet, '`') != -1
		while match(snippet, '`.\{-}`') != -1
			let snippet = substitute(snippet, '`.\{-}`',
						\ substitute(eval(matchstr(snippet, '`\zs.\{-}\ze`')),
						\ "\n\\%$", '', ''), '')
		endw
		let snippet = substitute(snippet, "\r", "\n", 'g')
	endif

	" Place all text after a colon in a tab stop after the tab stop
	" (e.g. "${#:foo}" becomes "${:foo}foo").
	" This helps tell the position of the tab stops later.
	let snippet = substitute(snippet, '${\d\+:\(.\{-}\)}', '&\1', 'g')

	" Update the a:snip so that all the $# become the text after
	" the colon in their associated ${#}.
	" (e.g. "${1:foo}" turns all "$1"'s into "foo")
	let i = 1
	while stridx(snippet, '${'.i) != -1
		let s = matchstr(snippet, '${'.i.':\zs.\{-}\ze}')
		if s != ''
			let snippet = substitute(snippet, '$'.i, s.'&', 'g')
		endif
		let i += 1
	endw

	if &et " Expand tabs to spaces if 'expandtab' is set.
		return substitute(snippet, '\t', repeat(' ', &sts ? &sts : &sw), 'g')
	endif
	return snippet
endf

" Counts occurences of haystack in needle
fun s:Count(haystack, needle)
	let counter = 0
	let index = stridx(a:haystack, a:needle)
	while index != -1
		let index = stridx(a:haystack, a:needle, index+1)
		let counter += 1
	endw
	return counter
endf

" Builds a list of a list of each tab stop in the snippet containing:
" 1.) The tab stop's line number.
" 2.) The tab stop's column number
"     (by getting the length of the string between the last "\n" and the
"     tab stop).
" 3.) The length of the text after the colon for the current tab stop
"     (e.g. "${1:foo}" would return 3). If there is no text, -1 is returned.
" 4.) If the "${#:}" construct is given, another list containing all
"     the matches of "$#", to be replaced with the placeholder. This list is
"     composed the same way as the parent; the first item is the line number,
"     and the second is the column.
fun s:BuildTabStops(snip, lnum, col, indent)
	let snipPos = []
	let i = 1
	let withoutVars = substitute(a:snip, '$\d\+', '', 'g')
	while stridx(a:snip, '${'.i) != -1
		let beforeTabStop = matchstr(withoutVars, '^.*\ze${'.i.'\D')
		let withoutOthers = substitute(withoutVars, '${\('.i.'\D\)\@!\d\+.\{-}}', '', 'g')

		let j = i - 1
		call add(snipPos, [0, 0, -1])
		let snipPos[j][0] = a:lnum + s:Count(beforeTabStop, "\n")
		let snipPos[j][1] = a:indent + len(matchstr(withoutOthers, '.*\(\n\|^\)\zs.*\ze${'.i.'\D'))
		if snipPos[j][0] == a:lnum | let snipPos[j][1] += a:col | endif

		" Get all $# matches in another list, if ${#:name} is given
		if stridx(withoutVars, '${'.i.':') != -1
			let snipPos[j][2] = len(matchstr(withoutVars, '${'.i.':\zs.\{-}\ze}'))
			let dots = repeat('.', snipPos[j][2])
			call add(snipPos[j], [])
			let withoutOthers = substitute(a:snip, '${\d\+.\{-}}\|$'.i.'\@!\d\+', '', 'g')
			while match(withoutOthers, '$'.i.'\(\D\|$\)') != -1
				let beforeMark = matchstr(withoutOthers, '^.\{-}\ze'.dots.'$'.i.'\(\D\|$\)')
				call add(snipPos[j][3], [0, 0])
				let snipPos[j][3][-1][0] = a:lnum + s:Count(beforeMark, "\n")
				let snipPos[j][3][-1][1] = a:indent + (snipPos[j][3][-1][0] > a:lnum
				                           \ ? len(matchstr(beforeMark, '.*\n\zs.*'))
				                           \ : a:col + len(beforeMark))
				let withoutOthers = substitute(withoutOthers, '$'.i.'\ze\(\D\|$\)', '', '')
			endw
		endif
		let i += 1
	endw
	return [snipPos, i - 1]
endf

fun snipMate#jumpTabStop(backwards)
	let leftPlaceholder = exists('s:origWordLen')
	                      \ && s:origWordLen != g:snipPos[s:curPos][2]
	if leftPlaceholder && exists('s:oldEndCol')
		let startPlaceholder = s:oldEndCol + 1
	endif

	if exists('s:update')
		call s:UpdatePlaceholderTabStops()
	else
		call s:UpdateTabStops()
	endif

	" Don't reselect placeholder if it has been modified
	if leftPlaceholder && g:snipPos[s:curPos][2] != -1
		if exists('startPlaceholder')
			let g:snipPos[s:curPos][1] = startPlaceholder
		else
			let g:snipPos[s:curPos][1] = col('.')
			let g:snipPos[s:curPos][2] = 0
		endif
	endif

	let s:curPos += a:backwards ? -1 : 1
	" Loop over the snippet when going backwards from the beginning
	if s:curPos < 0 | let s:curPos = s:snipLen - 1 | endif

	if s:curPos == s:snipLen
		let sMode = s:endCol == g:snipPos[s:curPos-1][1]+g:snipPos[s:curPos-1][2]
		call s:RemoveSnippet()
		return sMode ? "\<tab>" : TriggerSnippet()
	endif

	call cursor(g:snipPos[s:curPos][0], g:snipPos[s:curPos][1])

	let s:endLine = g:snipPos[s:curPos][0]
	let s:endCol = g:snipPos[s:curPos][1]
	let s:prevLen = [line('$'), col('$')]

	return g:snipPos[s:curPos][2] == -1 ? '' : s:SelectWord()
endf

fun s:UpdatePlaceholderTabStops()
	let changeLen = s:origWordLen - g:snipPos[s:curPos][2]
	unl s:startCol s:origWordLen s:update
	if !exists('s:oldVars') | return | endif
	" Update tab stops in snippet if text has been added via "$#"
	" (e.g., in "${1:foo}bar$1${2}").
	if changeLen != 0
		let curLine = line('.')

		for pos in g:snipPos
			if pos == g:snipPos[s:curPos] | continue | endif
			let changed = pos[0] == curLine && pos[1] > s:oldEndCol
			let changedVars = 0
			let endPlaceholder = pos[2] - 1 + pos[1]
			" Subtract changeLen from each tab stop that was after any of
			" the current tab stop's placeholders.
			for [lnum, col] in s:oldVars
				if lnum > pos[0] | break | endif
				if pos[0] == lnum
					if pos[1] > col || (pos[2] == -1 && pos[1] == col)
						let changed += 1
					elseif col < endPlaceholder
						let changedVars += 1
					endif
				endif
			endfor
			let pos[1] -= changeLen * changed
			let pos[2] -= changeLen * changedVars " Parse variables within placeholders
                                                  " e.g., "${1:foo} ${2:$1bar}"

			if pos[2] == -1 | continue | endif
			" Do the same to any placeholders in the other tab stops.
			for nPos in pos[3]
				let changed = nPos[0] == curLine && nPos[1] > s:oldEndCol
				for [lnum, col] in s:oldVars
					if lnum > nPos[0] | break | endif
					if nPos[0] == lnum && nPos[1] > col
						let changed += 1
					endif
				endfor
				let nPos[1] -= changeLen * changed
			endfor
		endfor
	endif
	unl s:endCol s:oldVars s:oldEndCol
endf

fun s:UpdateTabStops()
	let changeLine = s:endLine - g:snipPos[s:curPos][0]
	let changeCol = s:endCol - g:snipPos[s:curPos][1]
	if exists('s:origWordLen')
		let changeCol -= s:origWordLen
		unl s:origWordLen
	endif
	let lnum = g:snipPos[s:curPos][0]
	let col = g:snipPos[s:curPos][1]
	" Update the line number of all proceeding tab stops if <cr> has
	" been inserted.
	if changeLine != 0
		let changeLine -= 1
		for pos in g:snipPos
			if pos[0] >= lnum
				if pos[0] == lnum | let pos[1] += changeCol | endif
				let pos[0] += changeLine
			endif
			if pos[2] == -1 | continue | endif
			for nPos in pos[3]
				if nPos[0] >= lnum
					if nPos[0] == lnum | let nPos[1] += changeCol | endif
					let nPos[0] += changeLine
				endif
			endfor
		endfor
	elseif changeCol != 0
		" Update the column of all proceeding tab stops if text has
		" been inserted/deleted in the current line.
		for pos in g:snipPos
			if pos[1] >= col && pos[0] == lnum
				let pos[1] += changeCol
			endif
			if pos[2] == -1 | continue | endif
			for nPos in pos[3]
				if nPos[0] > lnum | break | endif
				if nPos[0] == lnum && nPos[1] >= col
					let nPos[1] += changeCol
				endif
			endfor
		endfor
	endif
endf

fun s:SelectWord()
	let s:origWordLen = g:snipPos[s:curPos][2]
	let s:oldWord = strpart(getline('.'), g:snipPos[s:curPos][1] - 1,
				\ s:origWordLen)
	let s:prevLen[1] -= s:origWordLen
	if !empty(g:snipPos[s:curPos][3])
		let s:update = 1
		let s:endCol = -1
		let s:startCol = g:snipPos[s:curPos][1] - 1
	endif
	if !s:origWordLen | return '' | endif
	let l = col('.') != 1 ? 'l' : ''
	if &sel == 'exclusive'
		return "\<esc>".l.'v'.s:origWordLen."l\<c-g>"
	endif
	return s:origWordLen == 1 ? "\<esc>".l.'gh'
							\ : "\<esc>".l.'v'.(s:origWordLen - 1)."l\<c-g>"
endf

" This updates the snippet as you type when text needs to be inserted
" into multiple places (e.g. in "${1:default text}foo$1bar$1",
" "default text" would be highlighted, and if the user types something,
" UpdateChangedSnip() would be called so that the text after "foo" & "bar"
" are updated accordingly)
"
" It also automatically quits the snippet if the cursor is moved out of it
" while in insert mode.
fun s:UpdateChangedSnip(entering)
	if exists('g:snipPos') && bufnr(0) != s:lastBuf
		call s:RemoveSnippet()
	elseif exists('s:update') " If modifying a placeholder
		if !exists('s:oldVars') && s:curPos + 1 < s:snipLen
			" Save the old snippet & word length before it's updated
			" s:startCol must be saved too, in case text is added
			" before the snippet (e.g. in "foo$1${2}bar${1:foo}").
			let s:oldEndCol = s:startCol
			let s:oldVars = deepcopy(g:snipPos[s:curPos][3])
		endif
		let col = col('.') - 1

		if s:endCol != -1
			let changeLen = col('$') - s:prevLen[1]
			let s:endCol += changeLen
		else " When being updated the first time, after leaving select mode
			if a:entering | return | endif
			let s:endCol = col - 1
		endif

		" If the cursor moves outside the snippet, quit it
		if line('.') != g:snipPos[s:curPos][0] || col < s:startCol ||
					\ col - 1 > s:endCol
			unl! s:startCol s:origWordLen s:oldVars s:update
			return s:RemoveSnippet()
		endif

		call s:UpdateVars()
		let s:prevLen[1] = col('$')
	elseif exists('g:snipPos')
		if !a:entering && g:snipPos[s:curPos][2] != -1
			let g:snipPos[s:curPos][2] = -2
		endif

		let col = col('.')
		let lnum = line('.')
		let changeLine = line('$') - s:prevLen[0]

		if lnum == s:endLine
			let s:endCol += col('$') - s:prevLen[1]
			let s:prevLen = [line('$'), col('$')]
		endif
		if changeLine != 0
			let s:endLine += changeLine
			let s:endCol = col
		endif

		" Delete snippet if cursor moves out of it in insert mode
		if (lnum == s:endLine && (col > s:endCol || col < g:snipPos[s:curPos][1]))
			\ || lnum > s:endLine || lnum < g:snipPos[s:curPos][0]
			call s:RemoveSnippet()
		endif
	endif
endf

" This updates the variables in a snippet when a placeholder has been edited.
" (e.g., each "$1" in "${1:foo} $1bar $1bar")
fun s:UpdateVars()
	let newWordLen = s:endCol - s:startCol + 1
	let newWord = strpart(getline('.'), s:startCol, newWordLen)
	if newWord == s:oldWord || empty(g:snipPos[s:curPos][3])
		return
	endif

	let changeLen = g:snipPos[s:curPos][2] - newWordLen
	let curLine = line('.')
	let startCol = col('.')
	let oldStartSnip = s:startCol
	let updateTabStops = changeLen != 0
	let i = 0

	for [lnum, col] in g:snipPos[s:curPos][3]
		if updateTabStops
			let start = s:startCol
			if lnum == curLine && col <= start
				let s:startCol -= changeLen
				let s:endCol -= changeLen
			endif
			for nPos in g:snipPos[s:curPos][3][(i):]
				" This list is in ascending order, so quit if we've gone too far.
				if nPos[0] > lnum | break | endif
				if nPos[0] == lnum && nPos[1] > col
					let nPos[1] -= changeLen
				endif
			endfor
			if lnum == curLine && col > start
				let col -= changeLen
				let g:snipPos[s:curPos][3][i][1] = col
			endif
			let i += 1
		endif

		" "Very nomagic" is used here to allow special characters.
		call setline(lnum, substitute(getline(lnum), '\%'.col.'c\V'.
						\ escape(s:oldWord, '\'), escape(newWord, '\&'), ''))
	endfor
	if oldStartSnip != s:startCol
		call cursor(0, startCol + s:startCol - oldStartSnip)
	endif

	let s:oldWord = newWord
	let g:snipPos[s:curPos][2] = newWordLen
endf
" vim:noet:sw=4:ts=4:ft=vim
plugin/snipMate.vim	[[[1
247
" File:          snipMate.vim
" Author:        Michael Sanders
" Last Updated:  July 13, 2009
" Version:       0.83
" Description:   snipMate.vim implements some of TextMate's snippets features in
"                Vim. A snippet is a piece of often-typed text that you can
"                insert into your document using a trigger word followed by a "<tab>".
"
"                For more help see snipMate.txt; you can do this by using:
"                :helptags ~/.vim/doc
"                :h snipMate.txt

if exists('loaded_snips') || &cp || version < 700
	finish
endif
let loaded_snips = 1
if !exists('snips_author') | let snips_author = 'Me' | endif

au BufRead,BufNewFile *.snippets\= set ft=snippet
au FileType snippet setl noet fdm=indent

let s:snippets = {} | let s:multi_snips = {}

if !exists('snippets_dir')
	let snippets_dir = substitute(globpath(&rtp, 'snippets/'), "\n", ',', 'g')
endif

fun! MakeSnip(scope, trigger, content, ...)
	let multisnip = a:0 && a:1 != ''
	let var = multisnip ? 's:multi_snips' : 's:snippets'
	if !has_key({var}, a:scope) | let {var}[a:scope] = {} | endif
	if !has_key({var}[a:scope], a:trigger)
		let {var}[a:scope][a:trigger] = multisnip ? [[a:1, a:content]] : a:content
	elseif multisnip | let {var}[a:scope][a:trigger] += [[a:1, a:content]]
	else
		echom 'Warning in snipMate.vim: Snippet '.a:trigger.' is already defined.'
				\ .' See :h multi_snip for help on snippets with multiple matches.'
	endif
endf

fun! ExtractSnips(dir, ft)
	for path in split(globpath(a:dir, '*'), "\n")
		if isdirectory(path)
			let pathname = fnamemodify(path, ':t')
			for snipFile in split(globpath(path, '*.snippet'), "\n")
				call s:ProcessFile(snipFile, a:ft, pathname)
			endfor
		elseif fnamemodify(path, ':e') == 'snippet'
			call s:ProcessFile(path, a:ft)
		endif
	endfor
endf

" Processes a single-snippet file; optionally add the name of the parent
" directory for a snippet with multiple matches.
fun s:ProcessFile(file, ft, ...)
	let keyword = fnamemodify(a:file, ':t:r')
	if keyword  == '' | return | endif
	try
		let text = join(readfile(a:file), "\n")
	catch /E484/
		echom "Error in snipMate.vim: couldn't read file: ".a:file
	endtry
	return a:0 ? MakeSnip(a:ft, a:1, text, keyword)
			\  : MakeSnip(a:ft, keyword, text)
endf

fun! ExtractSnipsFile(file, ft)
	if !filereadable(a:file) | return | endif
	let text = readfile(a:file)
	let inSnip = 0
	for line in text + ["\n"]
		if inSnip && (line[0] == "\t" || line == '')
			let content .= strpart(line, 1)."\n"
			continue
		elseif inSnip
			call MakeSnip(a:ft, trigger, content[:-2], name)
			let inSnip = 0
		endif

		if line[:6] == 'snippet'
			let inSnip = 1
			let trigger = strpart(line, 8)
			let name = ''
			let space = stridx(trigger, ' ') + 1
			if space " Process multi snip
				let name = strpart(trigger, space)
				let trigger = strpart(trigger, 0, space - 1)
			endif
			let content = ''
		endif
	endfor
endf

fun! ResetSnippets()
	let s:snippets = {} | let s:multi_snips = {} | let g:did_ft = {}
endf

let g:did_ft = {}
fun! GetSnippets(dir, filetypes)
	for ft in split(a:filetypes, '\.')
		if has_key(g:did_ft, ft) | continue | endif
		call s:DefineSnips(a:dir, ft, ft)
		if ft == 'objc' || ft == 'cpp' || ft == 'cs'
			call s:DefineSnips(a:dir, 'c', ft)
		elseif ft == 'xhtml'
			call s:DefineSnips(a:dir, 'html', 'xhtml')
		endif
		let g:did_ft[ft] = 1
	endfor
endf

" Define "aliasft" snippets for the filetype "realft".
fun s:DefineSnips(dir, aliasft, realft)
	for path in split(globpath(a:dir, a:aliasft.'/')."\n".
					\ globpath(a:dir, a:aliasft.'-*/'), "\n")
		call ExtractSnips(path, a:realft)
	endfor
	for path in split(globpath(a:dir, a:aliasft.'.snippets')."\n".
					\ globpath(a:dir, a:aliasft.'-*.snippets'), "\n")
		call ExtractSnipsFile(path, a:realft)
	endfor
endf

fun! TriggerSnippet()
	if exists('g:SuperTabMappingForward')
		if g:SuperTabMappingForward == "<tab>"
			let SuperTabKey = "\<c-n>"
		elseif g:SuperTabMappingBackward == "<tab>"
			let SuperTabKey = "\<c-p>"
		endif
	endif

	if pumvisible() " Update snippet if completion is used, or deal with supertab
		if exists('SuperTabKey')
			call feedkeys(SuperTabKey) | return ''
		endif
		call feedkeys("\<esc>a", 'n') " Close completion menu
		call feedkeys("\<tab>") | return ''
	endif

	if exists('g:snipPos') | return snipMate#jumpTabStop(0) | endif

	let word = matchstr(getline('.'), '\S\+\%'.col('.').'c')
	for scope in [bufnr('%')] + split(&ft, '\.') + ['_']
		let [trigger, snippet] = s:GetSnippet(word, scope)
		" If word is a trigger for a snippet, delete the trigger & expand
		" the snippet.
		if snippet != ''
			let col = col('.') - len(trigger)
			sil exe 's/\V'.escape(trigger, '/.').'\%#//'
			return snipMate#expandSnip(snippet, col)
		endif
	endfor

	if exists('SuperTabKey')
		call feedkeys(SuperTabKey)
		return ''
	endif
	return "\<tab>"
endf

fun! BackwardsSnippet()
	if exists('g:snipPos') | return snipMate#jumpTabStop(1) | endif

	if exists('g:SuperTabMappingForward')
		if g:SuperTabMappingBackward == "<s-tab>"
			let SuperTabKey = "\<c-p>"
		elseif g:SuperTabMappingForward == "<s-tab>"
			let SuperTabKey = "\<c-n>"
		endif
	endif
	if exists('SuperTabKey')
		call feedkeys(SuperTabKey)
		return ''
	endif
	return "\<s-tab>"
endf

" Check if word under cursor is snippet trigger; if it isn't, try checking if
" the text after non-word characters is (e.g. check for "foo" in "bar.foo")
fun s:GetSnippet(word, scope)
	let word = a:word | let snippet = ''
	while snippet == ''
		if exists('s:snippets["'.a:scope.'"]["'.escape(word, '\"').'"]')
			let snippet = s:snippets[a:scope][word]
		elseif exists('s:multi_snips["'.a:scope.'"]["'.escape(word, '\"').'"]')
			let snippet = s:ChooseSnippet(a:scope, word)
			if snippet == '' | break | endif
		else
			if match(word, '\W') == -1 | break | endif
			let word = substitute(word, '.\{-}\W', '', '')
		endif
	endw
	if word == '' && a:word != '.' && stridx(a:word, '.') != -1
		let [word, snippet] = s:GetSnippet('.', a:scope)
	endif
	return [word, snippet]
endf

fun s:ChooseSnippet(scope, trigger)
	let snippet = []
	let i = 1
	for snip in s:multi_snips[a:scope][a:trigger]
		let snippet += [i.'. '.snip[0]]
		let i += 1
	endfor
	if i == 2 | return s:multi_snips[a:scope][a:trigger][0][1] | endif
	let num = inputlist(snippet) - 1
	return num == -1 ? '' : s:multi_snips[a:scope][a:trigger][num][1]
endf

fun! ShowAvailableSnips()
	let line  = getline('.')
	let col   = col('.')
	let word  = matchstr(getline('.'), '\S\+\%'.col.'c')
	let words = [word]
	if stridx(word, '.')
		let words += split(word, '\.', 1)
	endif
	let matchlen = 0
	let matches = []
	for scope in [bufnr('%')] + split(&ft, '\.') + ['_']
		let triggers = has_key(s:snippets, scope) ? keys(s:snippets[scope]) : []
		if has_key(s:multi_snips, scope)
			let triggers += keys(s:multi_snips[scope])
		endif
		for trigger in triggers
			for word in words
				if word == ''
					let matches += [trigger] " Show all matches if word is empty
				elseif trigger =~ '^'.word
					let matches += [trigger]
					let len = len(word)
					if len > matchlen | let matchlen = len | endif
				endif
			endfor
		endfor
	endfor

	" This is to avoid a bug with Vim when using complete(col - matchlen, matches)
	" (Issue#46 on the Google Code snipMate issue tracker).
	call setline(line('.'), substitute(line, repeat('.', matchlen).'\%'.col.'c', '', ''))
	call complete(col, matches)
	return ''
endf
" vim:noet:sw=4:ts=4:ft=vim
after/plugin/snipMate.vim	[[[1
35
" These are the mappings for snipMate.vim. Putting it here ensures that it
" will be mapped after other plugins such as supertab.vim.
if !exists('loaded_snips') || exists('s:did_snips_mappings')
	finish
endif
let s:did_snips_mappings = 1

ino <silent> <tab> <c-r>=TriggerSnippet()<cr>
snor <silent> <tab> <esc>i<right><c-r>=TriggerSnippet()<cr>
ino <silent> <s-tab> <c-r>=BackwardsSnippet()<cr>
snor <silent> <s-tab> <esc>i<right><c-r>=BackwardsSnippet()<cr>
ino <silent> <c-r><tab> <c-r>=ShowAvailableSnips()<cr>

" The default mappings for these are annoying & sometimes break snipMate.
" You can change them back if you want, I've put them here for convenience.
snor <bs> b<bs>
snor <right> <esc>a
snor <left> <esc>bi
snor ' b<bs>'
snor ` b<bs>`
snor % b<bs>%
snor U b<bs>U
snor ^ b<bs>^
snor \ b<bs>\
snor <c-x> b<bs><c-x>

" By default load snippets in snippets_dir
if empty(snippets_dir)
	finish
endif

call GetSnippets(snippets_dir, '_') " Get global snippets

au FileType * if &ft != 'help' | call GetSnippets(snippets_dir, &ft) | endif
" vim:noet:sw=4:ts=4:ft=vim
