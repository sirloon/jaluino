
" only trigger plugin if launched from wrapper
if $JVIM_ROOT == ""
    "finish
endif

" detect if windows is with us or not
let s:running_windows = has("win16") || has("win32") || has("win64")

" ctags options to generate tags for jalv2
let g:jalv2_ctags_opts="--langdef=jal --langmap=jal:.jal --regex-jal=\"/procedure\\s*(\\w+(\\'put|))/\\1/p,procedure/i\" --regex-jal=\"/function\\s*(\\w+(\\'get|))/\\1/f,function/i\" --regex-jal=\"/const\\s*(\\w+)/\\1/c,constant/i\" --regex-jal=\"/record\\s*(\\w+)/\\1/s,structure/i\" --regex-jal=\"/var\\s*(volatile|)\\s*\\w+(\\*\\d+|)\\s*(\\+)/\\3/v,variable/i\""

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

let g:jalmain = ""

function DoCompile(...)
    "" Quickfix
    let l:jalfile = g:jalmain
    if jalfile == ""
       let l:jafile = expand("%")
    endif

    let l:cmd = "jaluino compile " + jalfile
    echo cmd
    "set makeprg=cmd
    set efm=%f:%l:%m
    "tabnew
    exec cmd
    "make
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

" extract ctags from jallib repository
function DoExtractTags()
    if $JALLIB_REPOS == ""
        let l:repos = input("JALLIB_REPOS isn't defined, please provide absolute path to your jallib repository: ","","dir")
        if l:repos == "" 
            echomsg "No path provided, give up..."
            return
        endif
    else
        let l:repos = expand($JALLIB_REPOS)
    endif    
    
    " TODO: split on ";" under windows (see s:running_windows)
    echomsg "JALLIB_REPOS=" . l:repos
    for dir in split(l:repos,":")
        echomsg "Extracting tags from " . dir
        let cmd = "!find " . dir . " -name \\\*.jal -type f | xargs ctags " . g:jalv2_ctags_opts . " -a -f jallib.tmp"
        exec cmd
    endfor
    let cmd = "!mv jallib.tmp jallib.tags"
    exec cmd
    set tags+=jallib.tags
 
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

map <C-F12> :call DoExtractTags()<CR>

map <silent> <F5> :call DoCompile()<CR><CR>
map <silent> <F6> :call DoValidate()<CR>
map <F7> :!jaluino reindent %<CR>
map <silent> <F8> :call DoUpload()<CR>

" taglist
" ctags definition
set tags+=jallib.tags
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

