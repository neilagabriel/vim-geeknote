import vim

#======================== Vim Helper Functions  ==============================#

def autocmd(event, pattern, cmd):
    vim.command("autocmd {} {} {}".format(event, pattern, cmd))

def winnr(number=None):
    if number:
        vim.command("let l:num = winnr('{}')".format(number))
    else:
        vim.command("let l:num = winnr()")
    return int(vim.eval("l:num"))

def winbufnr(number=None):
    if number:
        vim.command("let l:num = winbufnr('{}')".format(number))
    else:
        vim.command("let l:num = winbufnr()")
    return int(vim.eval("l:num"))

def vsplit(bufname, width):
    vim.command('topleft vertical ' + str(width) + ' new')
    vim.command('setlocal winfixwidth')
    vim.command('edit {}'.format(bufname))

    # Window options 
    vim.current.window.options["wrap"] = False

    # Buffer options
    vim.command('setfiletype geeknote')

    vim.command('normal! ggdG')
    vim.command('setlocal noswapfile')
    vim.command('setlocal buftype=nofile')
    vim.command('setlocal bufhidden=hide')
    vim.command('setlocal cursorline')

def modified():
    isModified = vim.eval("&modified")
    return isModified == "1"

def hidden():
    isHidden = vim.eval("&hidden")
    return isHidden == "1"

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
    while wnum <= winnr("$"):
        bnum         = winbufnr(wnum)
        buftype      = getbufvar(bnum, 'buftype')
        isPreviewWin = getwinvar(wnum, 'previewwindow')
        isModified   = getbufvar(bnum, 'modified')

        if (bnum != -1) and (buftype == "") and (isPreviewWin is False) and ((isModified is False) or hidden()): 
            return wnum
        wnum += 1
    return -1

def isWindowUsable(num):
    if winnr('$') == 1:
        return False

    oldwin = winnr()
    vim.command("exec {} . \"wincmd p\"".format(num))

    isSpecialWin = vim.current.buffer.options["buftype"]
    if isSpecialWin != '':
        isSpecialWin = vim.current.window.options["previewwindow"]
    isModified = modified()

    vim.command("exec {} . \"wincmd p\"".format(oldwin))

    if isSpecialWin: return False
    if hidden():     return True

    return (isModified is False) or (bufInWindows(winbufnr(num)) >= 2)
