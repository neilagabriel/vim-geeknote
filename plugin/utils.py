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

def vsplit(bufname, width):
    vim.command('topleft vertical ' + str(width) + ' new')
    vim.command('setlocal winfixwidth')
    vim.command('edit {}'.format(bufname))

    # Window options 
    vim.current.window.options['wrap'] = False

    # Buffer options
    vim.command('setfiletype geeknote')

    vim.command('normal! ggdG')
    vim.command('setlocal noswapfile')
    vim.command('setlocal buftype=nofile')
    vim.command('setlocal bufhidden=hide')
    vim.command('setlocal cursorline')

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

def getbufvar(bnum, var):
    return vim.buffers[bnum].options[var]
 
def getwinvar(wnum, var):
    return vim.windows[wnum-1].options[var]

def firstUsableWindow():
    wnum = 1
    while wnum <= winnr('$'):
        bnum         = winbufnr(wnum)
        buftype      = getbufvar(bnum, 'buftype')
        isPreviewWin = getwinvar(wnum, 'previewwindow')
        isModified   = getbufvar(bnum, 'modified')

        if ((bnum != -1)            and 
            (buftype == '')         and
            (isPreviewWin is False) and
            ((isModified  is False) or hidden())):
            return wnum
        wnum += 1
    return -1

def isWindowUsable(wnum):
    if winnr('$') == 1:
        return False

    bnum    = vim.windows[wnum-1].buffer.number
    buftype = getbufvar(bnum, 'buftype')
    preview = getwinvar(wnum, 'previewwindow')

    if buftype != '' or preview is True:
        return False

    if hidden():
        return True

    isModified = getbufvar(bnum, 'modified')
    return (isModified is False) or (bufInWindows(winbufnr(wnum)) >= 2)
