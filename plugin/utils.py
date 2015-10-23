#!/usr/bin/env python
import vim
import tempfile

GeeknoteNeovimMode = False
if int(vim.eval('exists("g:GeeknoteNeovimMode")')):
    GeeknoteNeovimMode = vim.eval('g:GeeknoteNeovimMode')

def createTempFile(**kwargs):
    if 'prefix' not in kwargs:
        kwargs['prefix'] = '__Geeknote__'

    if 'suffix' not in kwargs:
        geeknoteformat = 'markdown'
        if int(vim.eval('exists("g:GeeknoteFormat")')):
            geeknoteformat = vim.eval('g:GeeknoteFormat')
        kwargs['suffix'] = '.{}'.format(geeknoteformat)

    if 'dir' not in kwargs:
        if int(vim.eval('exists("g:GeeknoteScratchDirectory")')):
            kwargs['dir'] = vim.eval('g:GeeknoteScratchDirectory')

    return tempfile.NamedTemporaryFile(**kwargs)

#======================== Vim Helper Functions  ==============================#

def autocmd(event, pattern, cmd):
    vim.command('autocmd {} {} {}'.format(event, pattern, cmd))

def noremap(lhs, rhs):
    vim.command("nnoremap {} {}".format(lhs, rhs))

def winnr(number=None):
    if number:
        vim.command("let l:num = winnr('{}')".format(number))
    else:
        vim.command('let l:num = winnr()')
    return int(vim.eval('l:num'))

def winbufnr(wnum):
    vim.command("let l:num = winbufnr('{}')".format(wnum))
    return int(vim.eval('l:num'))

# Return a list of windows numbers currently displaying the given buffer.
def bufwinnr(bnum):
    windows = []
    wnum = 1
    while wnum <= winnr('$'):
        buf = vim.windows[wnum-1].buffer
        if buf.number == bnum:
            windows.append(wnum)
        wnum += 1
    return windows

def numberwidth():
    return int(vim.eval('&numberwidth'))

def foldcolumn():
    return int(vim.eval('&foldcolumn'))

def getActiveWindow():
    return winnr()

def getPreviousWindow():
    return winnr('#')

def setActiveWindow(wnum):
    vim.command('exec {} . "wincmd w"'.format(wnum))

def setActiveBuffer(buf):
    bnum    = buf.number
    windows = bufwinnr(bnum)
    if len(windows) > 0:
        wnum = windows[0]
        vim.command('exec {} . "wincmd w"'.format(wnum))

def hidden():
    isHidden = vim.eval('&hidden')
    return isHidden == '1'

def bufInWindows(bnum):
     cnt    = 0
     winnum = 1
     while True:
         bufnum = winbufnr(winnum)
         if bufnum < 0:
             break
         if bufnum == bnum:
             cnt = cnt + 1
         winnum = winnum + 1
     return cnt

def getBufferName(bnum):
    if GeeknoteNeovimMode:
        bnum -= 1
    return vim.buffers[bnum].name

def getBufferVariable(bnum, var):
    if GeeknoteNeovimMode:
        bnum -= 1
    return vim.buffers[bnum].options[var]
 
def getWindowVariable(wnum, var):
    return vim.windows[wnum-1].options[var]

def setBufferVariable(bnum, var, value):
    if GeeknoteNeovimMode:
        bnum -= 1
    vim.buffers[bnum].options[var] = value
 
def setWindowVariable(wnum, var, value):
    vim.windows[wnum-1].options[var] = value

def isBufferModified(bnum):
    return getBufferVariable(bnum, 'modified')
