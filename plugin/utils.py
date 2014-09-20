import vim

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

def getBufferVariable(bnum, var):
    return vim.buffers[bnum].options[var]
 
def getWindowVariable(wnum, var):
    return vim.windows[wnum-1].options[var]

def setBufferVariable(bnum, var, value):
    vim.buffers[bnum].options[var] = value
 
def setWindowVariable(wnum, var, value):
    vim.windows[wnum-1].options[var] = value

def getFirstUsableWindow():
    wnum = 1
    while wnum <= winnr('$'):
        bnum         = winbufnr(wnum)
        buftype      = getBufferVariable(bnum, 'buftype')
        isModified   = getBufferVariable(bnum, 'modified')
        isPreviewWin = getWindowVariable(wnum, 'previewwindow')

        if ((bnum != -1)            and 
            (buftype == '')         and
            (isPreviewWin is False) and
            ((isModified  is False) or hidden())):
            return wnum
        wnum += 1
    return -1

def isBufferModified(bnum):
    return getBufferVariable(bnum, 'modified')

def isWindowUsable(wnum):
    if winnr('$') == 1:
        return False

    bnum    = vim.windows[wnum-1].buffer.number
    buftype = getBufferVariable(bnum, 'buftype')
    preview = getWindowVariable(wnum, 'previewwindow')

    if buftype != '' or preview is True:
        return False

    if hidden():
        return True

    isModified = getBufferVariable(bnum, 'modified')
    return (isModified is False) or (bufInWindows(winbufnr(wnum)) >= 2)
