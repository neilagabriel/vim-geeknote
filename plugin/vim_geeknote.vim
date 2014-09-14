python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" ---------------------- Functions --------------------------------------------

function! Vim_GeeknoteToggle()
python << endOfPython
from vim_geeknote import GeeknoteToggle
GeeknoteToggle()
endOfPython
exec "nnoremap <silent> <buffer> <cr> :call Vim_GeeknoteActivateNode()<cr>"
endfunction

function! Vim_GeeknoteActivateNode()
python << endOfPython
from vim_geeknote import GeeknoteActivateNode
GeeknoteActivateNode()
endOfPython
endfunction

function! Vim_GeeknoteSaveNote()
python << endOfPython
from vim_geeknote import GeeknoteSaveNote
GeeknoteSaveNote()
endOfPython
endfunction

" ---------------------- User Commands ----------------------------------------

command! Geeknote call Vim_GeeknoteToggle()
