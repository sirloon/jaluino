
" only trigger plugin if launched from wrapper
if $JVIM_ROOT == ""
    "finish
endif



" enrich with nice plugins...
"source plugin/NERD_tree.vim
runtime! NERD_tree.vim
runtime! jaluinoide.vim
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

" open quickfix window
copen
wincmd k

