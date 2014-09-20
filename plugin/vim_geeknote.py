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

class Node(object):
    guid = None
    row  = -1

class NotebookNode(Node):
    def __init__(self, notebook):
        self.notebook = notebook
        self.notes    = []
        self.setName(notebook.name)

    def setName(self, name):
        self.name = name

class NoteNode(Node):
    def __init__(self, note, notebook):
        self.note     = note
        self.notebook = notebook
        self.setTitle(note.title)

    def setTitle(self, title):
        self.title = title

class Explorer(object):
    # A list of nodes for each notebook display in the explorer.
    notebooks = []

    # Maps the guid of each node to its underlying node object (includes notes)
    guidMap = {}

    # Maps notebook guids to the notebook's expand state (expanded/!explanded)
    expandState = {}

    #
    # A list of nodes (notebooks or nodes) that have been modified since the
    # last time the navigation window was synchronized with the server.
    #
    modifiedNodes = []

    # The file used to back the data store in the navigation window.
    dataFile = None

    def __init__(self, dataFile, buf):
        self.dataFile = dataFile
        self.buf      = buf

        try:
            self.refresh()
        except:
            vim.command('echoerr "Failed to retrieve data from server"')
            raise

        self.initView()
        self.render()

        autocmd('BufWritePre', self.dataFile.name, ':call Vim_GeeknoteSync()')

    def __del__(self):
        try:
            self.dataFile.close()
        except:
            pass

    def applyChanges(self):
        if isBufferModified(self.buf.number) is False:
            return

        for line in self.buf:
            # Look for changes to notes.
            r = re.compile('^\s+(.+)\[(.+)\]$')
            m = r.match(line)
            if m: 
                title = m.group(1).strip()
                guid  = m.group(2)
                node  = self.guidMap[guid]
                if not isinstance(node, NoteNode):
                    vim.command(
                        'echoerr "Cannot transform note {} to notebook"'.format(title))
                elif title != node.title:
                    node.setTitle(title)
                    self.modifiedNodes.append(node)
                continue

            # Look for changes to notebooks.
            r = re.compile('^[\+-](.+)\[(.+)\]$')
            m = r.match(line)
            if m:
                name = m.group(1).strip()
                guid = m.group(2)
                node = self.guidMap[guid]
                if not isinstance(node, NotebookNode):
                    vim.command(
                        'echoerr "Cannot transform notebook {} to note"'.format(name))
                elif name != node.name:
                    node.setName(name)
                    self.modifiedNodes.append(node)
                continue

    def addNotebook(self, notebook):
        node = NotebookNode(notebook)
        self.notebooks.append(node)
        self.notebooks.sort(key=lambda n: n.notebook.name.lower())

        self.guidMap[notebook.guid] = node

        notes = GeeknoteGetNotes(notebook)
        notes.sort(key=lambda n: n.title)
        for note in notes:
            self.addNote(note, notebook)

        if notebook.guid not in self.expandState:
            self.expandState[notebook.guid] = False

    def addNote(self, note, notebook):
        node = NoteNode(note, notebook)
        notebookNode = self.guidMap[notebook.guid]
        notebookNode.notes.append(node)

        self.guidMap[note.guid] = node

    def closeAll(self):
        for guid in self.expandState:
            self.expandState[guid] = False

    def expandAll(self):
        for guid in self.expandState:
            self.expandNotebook(guid)

    def expandNotebook(self, guid):
        self.expandState[guid] = True

    def getBuffer(self):
        return self.buf

    def getNotebook(self, guid):
        node = self.guidMap[guid]
        if isinstance(node, NotebookNode):
            return node.notebook
        return None

    def getNote(self, guid):
        node = self.guidMap[guid]
        if isinstance(node, NoteNode):
            return node.note
        return None

    def getContainingNotebook(self, guid):
        node = self.guidMap[guid]
        if isinstance(node, NoteNode):
            return node.notebook
        return None

    def getSelectedNotebook(self):
        prevWin = getActiveWindow()
        setActiveBuffer(self.buf)
        text = vim.current.line
        setActiveWindow(prevWin)

        guid = self.getNodeGuid(text)
        if guid is not None:
            node = self.guidMap[guid]
            if isinstance(node, NotebookNode):
                return node.notebook
            if isinstance(node, NoteNode):
                return node.notebook
        return None

    def getNodeGuid(self, nodeText):
        r = re.compile('^\s+.+\[(.+)\]$')
        m = r.match(nodeText)
        if m: return m.group(1)

        r = re.compile('^[\+-].+\[(.+)\]$')
        m = r.match(nodeText)
        if m: return m.group(1)

        return None

    def initView(self):
        origWin = getActiveWindow()
        setActiveBuffer(self.buf)

        wnum = getActiveWindow()
        bnum = self.buf.number

        setWindowVariable(wnum, 'winfixwidth', True)
        setWindowVariable(wnum, 'wrap'       , False)
        setWindowVariable(wnum, 'cursorline' , True)
        setBufferVariable(bnum, 'swapfile'   , False)
        setBufferVariable(bnum, 'buftype'    , 'quickfix')
        setBufferVariable(bnum, 'bufhidden'  , 'hide')

        vim.command('setfiletype geeknote')
        setActiveWindow(origWin)

    def refresh(self):
        del self.notebooks[:]
        self.guidMap.clear()

        notebooks = GeekNote().findNotebooks()
        for notebook in notebooks:
            self.addNotebook(notebook)

    def selectNode(self, guid):
        origWin = getActiveWindow()
        setActiveBuffer(self.buf)
        node = self.guidMap[guid]
        if node is not None:
            vim.current.window.cursor = (node.row, 0)
        setActiveWindow(origWin)

    def selectNotebook(self, notebook):
        self.selectNode(notebook.guid)

    def selectNotebookIndex(self, index):
        if index < len(self.notebooks):
            node = self.notebooks[index]
            self.selectNode(node.notebook.guid)

    def selectNote(self, note):
        self.selectNode(note.guid)

    def toggleNotebook(self, guid):
        node = self.guidMap[guid]
        if isinstance(node, NotebookNode):
            self.expandState[guid] = not self.expandState[guid]

    # Render the navigation buffer in the navigation window..
    def render(self):
        origWin = getActiveWindow()
        setActiveBuffer(self.buf)

        # 
        # Before overwriting the naviagation window, look for any changes made
        # by the user. Do not synchronize them yet with the server, just make
        # sure they are not lost.
        #
        self.applyChanges()

        # Clear the navigation buffer to get rid of old content (if any).
        del self.buf[:]

        # Prepare the new content and append it to the navigation buffer.
        content = []
        content.append('Notebooks:')
        content.append('{:=^84}'.format('='))

        row = 3
        for node in self.notebooks:
            notebook = node.notebook
            numNotes = len(node.notes)
            expand   = self.expandState[notebook.guid]

            line  = '-' if expand is True or numNotes == 0 else '+'
            line += ' ' + node.name
            content.append('{:<45} [{}]'.format(line, notebook.guid))
            node.row = row
            row += 1

            if expand is True:
                for noteNode in node.notes:
                    note  = noteNode.note
                    title = noteNode.title

                    line  = '    {:<41} [{}]'.format(title, note.guid)
                    content.append(line)
                    noteNode.row = row
                    row += 1
        self.buf.append(content, 0)

        #
        # Write the navigation window but disable BufWritePre events before
        # doing so. We only want to check for user changes when the user was
        # the one that saved the buffer.
        #
        ei = vim.eval('&ei')
        vim.command('set ei=BufWritePre')
        vim.command("write!")
        vim.command('set ei={}'.format(ei))

        setActiveWindow(origWin)

    def syncChanges(self):
        self.applyChanges()
        for node in self.modifiedNodes:
             if isinstance(node, NotebookNode):
                 GeeknoteRenameNotebook(node.notebook, node.name)
                 continue
             if isinstance(node, NoteNode):
                 GeeknoteRenameNote(node.note, node.title)
                 continue
        del self.modifiedNodes[:]


#======================== Geeknote Functions  ================================#

def GeeknoteActivateNode():
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

        origWin        = getActiveWindow()
        prevWin        = getPreviousWindow()
        firstUsableWin = getFirstUsableWindow()
        isPrevUsable   = isWindowUsable(prevWin)
     
        setActiveWindow(prevWin)
        if (isPrevUsable is False) and (firstUsableWin == -1):
            vim.command('botright vertical new')
        elif isPrevUsable is False:
            setActiveWindow(firstUsableWin)

        GeeknoteOpenNote(note)

        setActiveWindow(origWin)
        return

    # If the line is a notebook, toggle it (expand/close).
    r = re.compile('^[\+-].+\[(.+)\]$')
    m = r.match(current_line)
    if m:
        guid = m.group(1)
        explorer.toggleNotebook(guid)

        # Rerender the navigation window. Keep the current cursor postion.
        row, col = vim.current.window.cursor
        explorer.render()
        vim.current.window.cursor = (row, col)
        return

def GeeknoteCreateNote(name):
    name = name.strip('"\'')
    if explorer is None:
        GeeknoteToggle()
        vim.command('echoerr "Please select a notebook first."')
        return

    notebook = explorer.getSelectedNotebook()
    if notebook is None:
        explorer.selectNotebookIndex(0)
        vim.command('echoerr "Please select a notebook first."')
        return

    origWin = getActiveWindow()
    if isWindowUsable(origWin) is False:
        prevWin = getPreviousWindow()
        setActiveWindow(prevWin)
        if isWindowUsable(prevWin) is False:
            vim.command('botright vertical new')

    GeeknoteOpenNote(None, name, notebook)

def GeeknoteCreateNotebook(name):
    name = name.strip('"\'')
    try:
        notebook = Notebooks().create(name)
        if explorer is None:
            return
        explorer.addNotebook(notebook)
    except:
        vim.command('echoerr "Failed to create notebook."')
        return

    explorer.render()
    explorer.selectNotebook(notebook)

def GeeknoteGetNotes(notebook):
    notes = []
    results = Notes().get(None, None, notebook.name)
    total = len(results.notes)
    for key, note in enumerate(results.notes):
        notes.append(note)
    return notes

def GeeknoteRenameNotebook(notebook, name):
    notebook.name = name
    try:
        noteStore = Notes().getEvernote().getNoteStore()
        authToken = Notes().getEvernote().authToken
        return noteStore.updateNotebook(authToken, notebook)
    except:
        vim.command('echoerr "Failed to rename notebook."')
    return None

def GeeknoteRenameNote(note, title):
    note.title = title
    try:
        noteStore = Notes().getEvernote().getNoteStore()
        authToken = Notes().getEvernote().authToken
        return noteStore.updateNote(authToken, note)
    except:
        vim.command('echoerr "Failed to rename note."')
    return None

def GeeknoteSaveNote(filename):
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

    # Saving an existing note.
    if note is not None:
        result = bool(User().getEvernote().updateNote(
            guid=note.guid, **inputData))

    # Saving a new note.
    else:
        try:
            note = User().getEvernote().createNote(**inputData)

            explorer.addNote(note, notebook)
            explorer.expandNotebook(notebook.guid)
            explorer.render()
            explorer.selectNote(note)
        except:
            vim.command('echoerr "Failed to save note"')

    return note

def GeeknoteSync():
    if explorer is not None:
        explorer.syncChanges()
        explorer.refresh()    
        explorer.render()

# Open an existing or new note in the active window.
def GeeknoteOpenNote(note, title=None, notebook=None):
    if note is not None:
        title    = note.title
        notebook = explorer.getContainingNotebook(note.guid)

    f = tempfile.NamedTemporaryFile(delete=False)

    if note is not None:
        text = Editor.ENMLtoText(note.content)
        text = tools.stdoutEncode(text)
        f.write(text)
    f.close()

    vim.command('edit {}'.format(f.name))

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
        dataFile = tempfile.NamedTemporaryFile(delete=True)
        vim.command('topleft 50 vsplit {}'.format(dataFile.name))

        noremap("<silent> <buffer> <cr>", 
                ":call Vim_GeeknoteActivateNode()<cr>")

        explorer = Explorer(dataFile, vim.current.buffer)
    else:
        explorer.render()

    explorer.selectNotebookIndex(0)

