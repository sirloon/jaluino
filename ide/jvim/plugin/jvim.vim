
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

