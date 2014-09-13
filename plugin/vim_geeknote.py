import vim
import re

from geeknote.geeknote import *

#======================== Vimscript Entry-points =============================#

def vim_geeknote_activate_node():
    current_line = vim.current.line
    note = re.compile('\s+n.+ \[(.+)\]$')
    m = note.match(current_line)
    if m:
        guid = m.group(1)
        print GeekNote().getNote(guid)
    else:
        print "Opening something else: " + current_line

def vim_geeknote_toggle():
    notebooks_buffer = 't:vim_geeknote_notebooks'
    VimVerticalSplit(notebooks_buffer, 50)
    explorer = Explorer()

    notebooks = GeekNote().findNotebooks()
    for notebook in notebooks:
        explorer.add(notebook)
    explorer.expandAll()
    explorer.render()

#======================== Classes ============================================#

class Explorer(object):
    nodes = []

    def add(self, notebook):
        notes = GeeknoteGetNotes(notebook)
        node  = {'notebook':notebook, 'notes':notes, 'expand':False}
        self.nodes.append(node)

    def expandAll(self):
        for node in self.nodes:
            node['expand'] = True

    def render(self):
        content = []
        content.append("Notebooks:")
        content.append("{:=^50}".format("="))

        for node in self.nodes:
            notebook = node['notebook']
            notes    = node['notes']

            total = len(notes)
            content.append('N {0} ({1})'.format(notebook.name, str(total)))

            if node['expand']:
                for note in notes:
                    name = ""
                    if hasattr(note, 'title'):
                        name = note.title
                    elif hasattr(note, 'name'):
                        name = notes.name

                    name = (name[:38] + '..') if len(name) > 40 else name
                    line = "    n {:<40} [{}]".format(name, note.guid)
                    content.append(line)

        vim.command('call append(0, {0})'.format(content))
        vim.command('setlocal nomodifiable')
        vim.current.window.cursor = (1, 0)

#======================== Geeknote Helper Functions  =========================#

def GeeknoteGetNotes(notebook):
    notes = []
    results = Notes().get(None, None, notebook.name)
    total = len(results.notes)
    for key, note in enumerate(results.notes):
        notes.append(note)
    return notes

#======================== Vim Helper Functions  ==============================#

def VimVerticalSplit(bufname, width):
    vim.command('topleft vertical ' + str(width) + ' new')
    vim.command('setlocal winfixwidth')
    vim.command('edit {0}'.format(bufname))

    # Window options 
    vim.current.window.options["wrap"] = False

    # Buffer options
    vim.command('setfiletype geeknote')

    vim.command('normal! ggdG')
    vim.command('setlocal noswapfile')
    vim.command('setlocal buftype=nofile')
    vim.command('setlocal bufhidden=hide')
    vim.command('setlocal cursorline')

