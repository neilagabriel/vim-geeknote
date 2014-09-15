import vim
import re
import tempfile
import utils
import numbers

from utils             import *
from geeknote.geeknote import *
from geeknote.tools    import *
from geeknote.editor   import Editor

import evernote.edam.type.ttypes as Types

#======================== Globals ============================================#

explorer  = None
openNotes = {}

#======================== Classes ============================================#

class Explorer(object):
    #
    # A list of nodes that comprise the explorer. Each node represents a
    # notebook. This list is recreated each time the explorer is refreshed.
    #
    nodes = []

    #
    # A dictionary that maps notes to the notebooks they are contained in as
    # well as other data related to navigation. This dictionary is recreated
    # each time the explorer is refreshed.
    #
    noteMap = {}

    #
    # A dictionary that maps notebooks to their expand state (expanded or not
    # expanded). This dictionary is not recreated when the explorer is
    # refreshed.
    #
    expandState = {}

    def __init__(self, buf):
        self.buf = buf
        self.refresh()

    def add(self, notebook):
        notes = GeeknoteGetNotes(notebook)
        node  = {
                    'notebook':notebook, 
                    'notes':notes, 
                    'row':-1
                }
        self.nodes.append(node)
        self.nodes = sorted(self.nodes, 
                            key=lambda k: k['notebook'].name.lower())

        for note in notes:
            self.noteMap[note.guid] = (
                {
                    'notebook':notebook, 
                    'note':note, 
                    'row':-1
                })

        self.expandState[notebook.guid] = False

    def expandAll(self):
        for node in self.nodes:
            notebook = node['notebook']
            self.expandState[notebook.guid] = True

    def getNotebook(self, guid):
        for node in self.nodes:
            notebook = node['notebook']
            if notebook.guid == guid:
                return notebook
        return None

    def getNote(self, guid):
        return self.noteMap[guid]['note']

    def getContainingNotebook(self, guid):
        return self.noteMap[guid]['notebook']

    def getSelectedNotebook(self):
        # Get the text selected in the navigation window.
        prevWin = getActiveWindow()
        setActiveBuffer(self.buf)
        text = vim.current.line
        setActiveWindow(prevWin)

        nodeObj = self.getNodeBase(text)
        if isinstance(nodeObj, Types.Notebook):
            return nodeObj
        if isinstance(nodeObj, Types.Note):
            return self.getContainingNotebook(nodeObj.guid)
        return None

    def getNodeBase(self, nodeText):
        # Check for notes first
        r = re.compile('^\s+.+\[(.+)\]$')
        m = r.match(nodeText)
        if m:
            guid = m.group(1)
            return self.getNote(guid)

        # Check if its a notebook
        r = re.compile('^[\+-].+\[(.+)\]$')
        m = r.match(nodeText)
        if m:
            guid = m.group(1)
            return self.getNotebook(guid)

        # Otherwise the user has not selected anything of importance.
        return None

    def refresh(self):
        del self.nodes[:]
        self.noteMap.clear()

        notebooks = GeekNote().findNotebooks()
        for notebook in notebooks:
            self.add(notebook)

    # TODO: save/restore window
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

    # TODO: save/restore window
    def selectNote(self, note):
         row = self.noteMap[note.guid]['row']
         if row >= 0:
             vim.current.window.cursor = (row, 0)

    def toggle(self, guid):
        target = None

        for node in self.nodes:
            notebook = node['notebook']
            if notebook.guid == guid:
                target = node
                break

        if target:
            self.expandState[guid] = not self.expandState[guid]

    # Render the navigation buffer in the navigation window..
    def render(self):
        prevWin = getActiveWindow()

        # Move to the window displaying the navigation buffer.
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
            expand   = self.expandState[notebook.guid]

            line  = '-' if expand is True or total == 0 else '+'
            line += ' {}'.format(notebook.name)
            if total > 0:
                line += ' ({})'.format(str(total))
            content.append('{:<44} [{}]'.format(line, notebook.guid))
            node['row'] = row
            row += 1

            if expand is True:
                for note in notes:
                    name = ''
                    if hasattr(note, 'title'):
                        name = note.title
                    elif hasattr(note, 'name'):
                        name = notes.name

                    name = (name[:38] + '..') if len(name) > 40 else name
                    line = '    {:<40} [{}]'.format(name, note.guid)
                    content.append(line)
                    self.noteMap[note.guid]['row'] = row
                    row += 1
        self.buf.append(content, 0)

        # Do not all the user to modify the navigation buffer (for now).
        self.buf.options['modifiable'] = False

        # Return to the previously active window.
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

def GeeknoteCreateNote(name):
    global explorer

    name = name.strip('"\'')
    if explorer is None:
        GeeknoteToggle()
        vim.command('echoerr "Please select a notebook first."')
        return

    notebook = explorer.getSelectedNotebook()
    if notebook is None:
        explorer.selectNotebook(0)
        vim.command('echoerr "Please select a notebook first."')
        return

    GeeknoteOpenNote(None, name, notebook)

def GeeknoteCreateNotebook(name):
    name = name.strip('\"\'')
    try:
        result = Notebooks().create(name)
        if result is False:
            vim.command('echoerr "Failed to create notebook."')
            return
    except:
        vim.command('echoerr "Failed to create notebook."')

    if explorer is None:
        return

    notebooks = GeekNote().findNotebooks()
    for notebook in notebooks:
        if notebook.name == name:
            explorer.add(notebook)
            explorer.render()
            explorer.selectNotebook(notebook)
            return

    vim.command('echoerr "Unexpected error, could not find notebook."')

def GeeknoteGetNotes(notebook):
    notes = []
    results = Notes().get(None, None, notebook.name)
    total = len(results.notes)
    for key, note in enumerate(results.notes):
        notes.append(note)
    return notes

def GeeknoteSaveNote(filename):
    global openNotes

    result   = False
    note     = openNotes[filename]['note']
    title    = openNotes[filename]['title']
    notebook = openNotes[filename]['notebook']
    content  = open(filename, 'r').read()

    inputData = {}
    inputData['title']    = title
    inputData['content']  = Editor.textToENML(content)
    inputData['tags']     = None
    inputData['notebook'] = notebook.guid

    if note is not None:
        result = bool(User().getEvernote().updateNote(
            guid=note.guid, **inputData))
    else:
        result = User().getEvernote().createNote(**inputData)
        explorer.refresh()
        explorer.toggle(notebook.guid)
        explorer.render()
        #explorer.selectNote(note.guid)

    if result is False:
        vim.command('echoerr "Failed to save note"')

def GeeknoteOpenNote(note, title=None, notebook=None):
    global openNotes

    if note is not None:
        title    = note.title
        notebook = explorer.getContainingNotebook(note.guid)

    origWin        = getActiveWindow()
    prevWin        = getPreviousWindow()
    isPrevUsable   = isWindowUsable(prevWin)
    firstUsableWin = firstUsableWindow()

    setActiveWindow(prevWin)
    if (isPrevUsable is False) and (firstUsableWin == -1):
        vim.command('vertical new')
    elif isPrevUsable is False:
        setActiveWindow(firstUsableWin)

    f = tempfile.NamedTemporaryFile(delete=False)

    if note is not None:
        text = Editor.ENMLtoText(note.content)
        text = text + '\n'
        text = tools.stdoutEncode(text)

        f.write(text)
    f.close()

    vim.command('edit {}'.format(f.name))

    if note is not None:
        setActiveWindow(origWin)

    autocmd('BufWritePost', 
            f.name, 
            ':call Vim_GeeknoteSaveNote("{}")'.format(f.name))

    openNotes[f.name] = (
        {
            'note':note,
            'title':title,
            'notebook':notebook
        })

def GeeknoteToggle():
    global explorer

    if explorer is None:
        #vsplit('t:explorer', 50)
        vsplit('t:explorer', 80)
        buf = vim.current.buffer

        noremap("<silent> <buffer> <cr>", 
                ":call Vim_GeeknoteActivateNode()<cr>")

        explorer = Explorer(buf)

    explorer.render()
    explorer.selectNotebook(0)

