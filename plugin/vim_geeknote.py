import vim

from geeknote.geeknote import *

notebooks_buffer = 't:vim_geeknote_notebooks'
tags_buffer      = 't:vim_geeknote_tags'

def vim_geeknote_find():
    Notes().find()

def vim_geeknote_tags():
    return GeekNote().findTags()

def vim_geeknote_notebooks():
    notebooks = GeekNote().findNotebooks()
    for notebook in notebooks:
        print notebook.name

def vim_geeknote_toggle():
    global notebooks_buffer

    vim_new_window_vsplit(notebooks_buffer, 30)

    content = []
    content.append("Notebooks:")
    content.append("====================")

    notebooks = GeekNote().findNotebooks()
    for notebook in notebooks:
        content.append("N " + notebook.name)

    vim.command('call append(0, {0})'.format(content))
    vim.command('normal! 0')
    vim.command('setlocal nomodifiable')

    vim_new_window_hsplit(tags_buffer)

    del content[:]
    content.append("Tags:")
    content.append("====================")

    tags = GeekNote().findTags()
    for tag in tags:
        content.append("T " + tag.name)

    vim.command('call append(0, {0})'.format(content))
    vim.command('normal! 0')
    vim.command('setlocal nomodifiable')

def vim_new_window_vsplit(bufname, width):
    vim.command('topleft vertical ' + str(width) + ' new')
    vim.command('setlocal winfixwidth')
    vim.command('edit {0}'.format(bufname))
    vim.command('normal! ggdG')
    vim.command('setlocal noswapfile')
    vim.command('setlocal buftype=nofile')
    vim.command('setlocal bufhidden=hide')
    vim.command('setfiletype geeknote')

def vim_new_window_hsplit(bufname):
    vim.command('belowright split new')
    vim.command('setlocal winfixwidth')
    vim.command('edit {0}'.format(bufname))
    vim.command('normal! ggdG')
    vim.command('setlocal noswapfile')
    vim.command('setlocal buftype=nofile')
    vim.command('setlocal bufhidden=hide')
    vim.command('setfiletype geeknote')
