python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" ---------------------- Configuration ----------------------------------------

if has('nvim')
    let g:GeeknoteNeovimMode="True"
endif

" ---------------------- Functions --------------------------------------------

function! Vim_GeeknoteTerminate()
python << endOfPython
from vim_geeknote import GeeknoteTerminate
GeeknoteTerminate()
endOfPython
endfunction

function! Vim_GeeknoteToggle()
python << endOfPython
from vim_geeknote import GeeknoteToggle
GeeknoteToggle()
endOfPython
endfunction

function! Vim_GeeknoteActivateNode()
python << endOfPython
from vim_geeknote import GeeknoteActivateNode
GeeknoteActivateNode()
endOfPython
endfunction

function! Vim_GeeknoteCloseNote(arg1)
python << endOfPython
from vim_geeknote import GeeknoteCloseNote
filename = vim.eval("a:arg1")
GeeknoteCloseNote(filename)
endOfPython
endfunction

function! Vim_GeeknoteCreateNotebook(arg1)
python << endOfPython
from vim_geeknote import GeeknoteCreateNotebook
name = vim.eval("a:arg1")
GeeknoteCreateNotebook(name)
endOfPython
endfunction

function! Vim_GeeknoteCreateNote(arg1)
python << endOfPython
from vim_geeknote import GeeknoteCreateNote
name = vim.eval("a:arg1")
GeeknoteCreateNote(name)
endOfPython
endfunction

function! Vim_GeeknoteSaveAsNote()
python << endOfPython
from vim_geeknote import GeeknoteSaveAsNote
GeeknoteSaveAsNote()
endOfPython
endfunction

function! Vim_GeeknoteSearch(arg1)
python << endOfPython
from vim_geeknote import GeeknoteSearch
args = vim.eval("a:arg1")
GeeknoteSearch(args)
endOfPython
endfunction

function! Vim_GeeknotePrepareToSaveNote(arg1)
python << endOfPython
from vim_geeknote import GeeknotePrepareToSaveNote
filename = vim.eval("a:arg1")
GeeknotePrepareToSaveNote(filename)
endOfPython
endfunction

function! Vim_GeeknoteSaveNote(arg1)
python << endOfPython
from vim_geeknote import GeeknoteSaveNote
filename = vim.eval("a:arg1")
GeeknoteSaveNote(filename)
endOfPython
endfunction

function! Vim_GeeknoteSync()
python << endOfPython
from vim_geeknote import GeeknoteSync
GeeknoteSync()
endOfPython
endfunction

function! Vim_GeeknoteCommitStart()
python << endOfPython
from vim_geeknote import GeeknoteCommitStart
GeeknoteCommitStart()
endOfPython
endfunction

function! Vim_GeeknoteCommitComplete()
python << endOfPython
from vim_geeknote import GeeknoteCommitComplete
GeeknoteCommitComplete()
endOfPython
endfunction

" ---------------------- User Commands ----------------------------------------

command!          Geeknote               call Vim_GeeknoteToggle()
command! -nargs=1 GeeknoteCreateNotebook call Vim_GeeknoteCreateNotebook(<f-args>)
command! -nargs=1 GeeknoteCreateNote     call Vim_GeeknoteCreateNote(<f-args>)
command!          GeeknoteSaveAsNote     call Vim_GeeknoteSaveAsNote()
command! -nargs=* GeeknoteSearch         call Vim_GeeknoteSearch(<q-args>)
command!          GeeknoteSync           call Vim_GeeknoteSync()
