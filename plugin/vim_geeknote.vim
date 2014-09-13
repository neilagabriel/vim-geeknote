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

function! GeeknoteToggle()
python << endOfPython
from vim_geeknote import vim_geeknote_toggle
vim_geeknote_toggle()
endOfPython
exec "nnoremap <silent> <buffer> <cr> :call <SID>GeeknoteActivateNode()<cr>"
endfunction

" -----------------------------------------------------------------------------

function! s:GeeknoteActivateNode()
python << endOfPython
from vim_geeknote import vim_geeknote_activate_node
vim_geeknote_activate_node()
endOfPython
endfunction

" -----------------------------------------------------------------------------
"  Expose our commands to the user
" -----------------------------------------------------------------------------
"
command! Geeknote call GeeknoteToggle()
