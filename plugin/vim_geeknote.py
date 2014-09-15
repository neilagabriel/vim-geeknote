import vim
import re
import tempfile
import utils
import numbers

from utils             import *
from geeknote.geeknote import *
from geeknote.tools    import *
from geeknote.editor   import Editor

#======================== Globals ============================================#

explorer  = None
openNotes = {}

#======================== Classes ============================================#

class Explorer(object):
    nodes   = []
    noteMap = {}

    def __init__(self, buf):
        self.buf = buf
        notebooks = GeekNote().findNotebooks()
        for notebook in notebooks:
            self.add(notebook)

    def add(self, notebook):
        notes = GeeknoteGetNotes(notebook)
        node  = {
                    'notebook':notebook, 
                    'notes':notes, 
                    'expand':False,
                    'row':-1
                }
        self.nodes.append(node)
        self.nodes = sorted(self.nodes, 
                            key=lambda k: k['notebook'].name.lower())

        for note in notes:
            self.noteMap[note.guid] = notebook

    def expandAll(self):
        for node in self.nodes:
            node['expand'] = True

    def selectNotebook(self, notebook):
        # Notebook index 
        if isinstance(notebook, numbers.Number):
            if notebook < len(self.nodes):
                node = self.nodes[notebook]
                vim.current.window.cursor = (node['row'], 0)
                return
        # Notebook instance
        for node in self.nodes:
            if node['notebook'].guid == notebook.guid:
                vim.current.window.cursor = (node['row'], 0)
                return

    def findNotebook(self, note):
        return self.noteMap[note.guid]

    def toggle(self, guid):
        target = None

        for node in self.nodes:
            notebook = node['notebook']
            if notebook.guid == guid:
                target = node
                break

        if target:
            target['expand'] = not target['expand']

    # Render the navigation buffer in the navigation window..
    def render(self):
        prevWin = getActiveWindow()

        # Move to the window displaying the navigation buffer and stay there. 
        setActiveBuffer(self.buf)

        # Clear the navigation buffer to get rid of old content (if any).
        self.buf.options['modifiable'] = True
        clearBuffer(self.buf)

        # Prepare the new content and append it to the navigation buffer.
        content = []
        content.append('Notebooks:')
        content.append('{:=^50}'.format('='))

        row = 3
        for node in self.nodes:
            notebook = node['notebook']
            notes    = node['notes']
            total    = len(notes)

            line  = '-' if node['expand'] or total == 0 else '+'
            line += ' {}'.format(notebook.name)
            if total > 0:
                line += ' ({})'.format(str(total))
            content.append('{:<44} [{}]'.format(line, notebook.guid))
            node['row'] = row
            row += 1

            if node['expand']:
                for note in notes:
                    name = ''
                    if hasattr(note, 'title'):
                        name = note.title
                    elif hasattr(note, 'name'):
                        name = notes.name

                    name = (name[:38] + '..') if len(name) > 40 else name
                    line = '    {:<40} [{}]'.format(name, note.guid)
                    content.append(line)
                    row += 1
        self.buf.append(content, 0)

        # Do not all the user to modify the navigation buffer (for now).
        self.buf.options['modifiable'] = False

        setActiveWindow(prevWin)

#======================== Geeknote Functions  ================================#

def GeeknoteActivateNode():
    global explorer

    #
    # Look at the current line in the navigation window (active) determine if
    # it is a note or a notebook.
    #
    current_line = vim.current.line

    # If the line is a note, open it.
    r = re.compile('^\s+.+\[(.+)\]$')
    m = r.match(current_line)
    if m:
        guid = m.group(1)
        note = GeekNote().getNote(guid)
        GeeknoteOpenNote(note)
        return

    # If the line is a notebook, toggle it (expand/close).
    r = re.compile('^[\+-].+\[(.+)\]$')
    m = r.match(current_line)
    if m:
        guid = m.group(1)
        explorer.toggle(guid)

        # Rerender the navigation window. Keep the current cursor postion.
        row, col = vim.current.window.cursor
        explorer.render()
        vim.current.window.cursor = (row, col)
        return

def GeeknoteCreateNotebook(name):
    name = name.strip('\"')
    try:
        result = Notebooks().create(name)
        if result is False:
            vim.command('echoerr "Failed to create notebook"')
            return
    except:
        vim.command('echoerr "Failed to create notebook"')

    if explorer is None:
        return

    notebooks = GeekNote().findNotebooks()
    for notebook in notebooks:
        if notebook.name == name:
            explorer.add(notebook)
            explorer.render()
            explorer.selectNotebook(notebook)
            return

    vim.command('echoerr "Unexpected error, could not find notebook"')

def GeeknoteGetNotes(notebook):
    notes = []
    results = Notes().get(None, None, notebook.name)
    total = len(results.notes)
    for key, note in enumerate(results.notes):
        notes.append(note)
    return notes

def GeeknoteSaveNote(filename):
    global openNotes

    note = openNotes[filename]
    content = open(filename, 'r').read()

    inputData = {}
    inputData['title']    = note.title
    inputData['content']  = Editor.textToENML(content)
    inputData['tags']     = None
    inputData['notebook'] = explorer.findNotebook(note).guid

    result = bool(User().getEvernote().updateNote(
        guid=note.guid, **inputData))

    if result is False:
        vim.command('echoerr "Failed to save note"')

def GeeknoteOpenNote(note):
    global openNotes

    origWin        = getActiveWindow()
    prevWin        = getPreviousWindow()
    isPrevUsable   = isWindowUsable(prevWin)
    firstUsableWin = firstUsableWindow()

    setActiveWindow(prevWin)
    if (isPrevUsable is False) and (firstUsableWin == -1):
        vim.command('vertical new')
    elif isPrevUsable is False:
        setActiveWindow(firstUsableWin)

    text = Editor.ENMLtoText(note.content)
    text = text + '\n'
    text = tools.stdoutEncode(text)

    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(text)
    f.close()

    vim.command('edit {}'.format(f.name))
    setActiveWindow(origWin)

    autocmd('BufWritePost', 
            f.name, 
            ':call Vim_GeeknoteSaveNote("{}")'.format(f.name))

    openNotes[f.name] = note

def GeeknoteToggle():
    global explorer

    if explorer is None:
        vsplit('t:explorer', 50)
        buf = vim.current.buffer

        noremap("<silent> <buffer> <cr>", 
                ":call Vim_GeeknoteActivateNode()<cr>")

        explorer = Explorer(buf)

    explorer.render()
    explorer.selectNotebook(0)

