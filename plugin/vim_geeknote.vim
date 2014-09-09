" -----------------------------------------------------------------------------
" Add our plugin to the path
" -----------------------------------------------------------------------------
"
python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" -----------------------------------------------------------------------------
"  Function(s)
" -----------------------------------------------------------------------------

function! GeeknoteFind()
python << endOfPython
from vim_geeknote import vim_geeknote_find
vim_geeknote_find()
endOfPython
endfunction

" -----------------------------------------------------------------------------

function! GeeknoteToggle()
python << endOfPython
from vim_geeknote import vim_geeknote_toggle
vim_geeknote_toggle()
endOfPython
endfunction

" -----------------------------------------------------------------------------
"  Expose our commands to the user
" -----------------------------------------------------------------------------
"
command! GnoteFind call GeeknoteFind()
command! GnoteToggle call GeeknoteToggle()
