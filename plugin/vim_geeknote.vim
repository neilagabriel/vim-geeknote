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

function! Vim_GeeknoteCreateNotebook(arg1)
python << endOfPython
from vim_geeknote import GeeknoteCreateNotebook
name = vim.eval("a:arg1")
GeeknoteCreateNotebook(name)
endOfPython
endfunction

function! Vim_GeeknoteSaveNote(arg1)
python << endOfPython
from vim_geeknote import GeeknoteSaveNote
filename = vim.eval("a:arg1")
GeeknoteSaveNote(filename)
endOfPython
endfunction

" ---------------------- User Commands ----------------------------------------

command!          Geeknote               call Vim_GeeknoteToggle()
command! -nargs=1 GeeknoteCreateNotebook call Vim_GeeknoteCreateNotebook(<f-args>)
