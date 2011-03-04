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
