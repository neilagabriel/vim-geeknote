import vim
import re
import tempfile

from view  import *
from utils import *

from geeknote.geeknote import *

import evernote.edam.limits.constants as Limits

# Connection to Geeknote (XXX: move this out)
geeknote  = GeekNote()
authToken = geeknote.authToken
noteStore = geeknote.getNoteStore()

#
# A dictionary containing an entry for all nodes contained in the explorer
# window, keyed by guid.
#
registry = {}

#======================== Classes ============================================#

class Node(object):
    def __init__(self, indent=0):
        self.children = []
        self.row      = -1
        self.indent   = indent
        self.close()

    def activate(self):
        self.toggle()

    def addChild(self, node):
        self.children.append(node)

    def close(self):
        self.expanded = False

    def commitChanges(self):
        pass

    def expand(self):
        self.expanded = True

    def setName(self, name):
        self.name = name

    def toggle(self):
        if self.expanded:
            self.close()
        else:
            self.expand()

class NotebookNode(Node):
    def __init__(self, notebook):
        super(NotebookNode, self).__init__()

        self.notebook = notebook
        self.setName(notebook.name)

    def commitChanges(self):
        if self.notebook.name != self.name:
            self.notebook.name = self.name
            noteStore.updateNotebook(authToken, self.notebook)

    def render(self, buffer):
        numNotes = len(self.children)

        line  = '-' if self.expanded or numNotes == 0 else '+'
        line += ' ' + self.name
        buffer.append('{:<50} [{}]'.format(line, self.notebook.guid))
        self.row = len(buffer)

        if self.expanded:
            for noteNode in self.children:
                noteNode.render(buffer)

    def setName(self, name):
        self.name = name

class NoteNode(Node):
    def __init__(self, note, notebook, indent=1):
        super(NoteNode, self).__init__(indent)

        self.note     = note
        self.notebook = notebook
        self.setTitle(note.title)

    def activate(self):
        super(NoteNode, self).activate()

        # TODO: move all of this into view.py
        origWin        = getActiveWindow()
        prevWin        = getPreviousWindow()
        firstUsableWin = getFirstUsableWindow()
        isPrevUsable   = isWindowUsable(prevWin)
        
        setActiveWindow(prevWin)
        if (isPrevUsable is False) and (firstUsableWin == -1):
            vim.command('botright vertical new')
        elif isPrevUsable is False:
            setActiveWindow(firstUsableWin)

        GeeknoteOpenNote(self.note)
        setActiveWindow(origWin)
        return

    def commitChanges(self):
        if self.note.title != self.title:
            self.note.title = self.title
            noteStore.updateNote(authToken, self.note)

        if self.note.notebookGuid != self.notebook.guid:
            self.note.notebookGuid = self.notebook.guid
            noteStore.updateNote(authToken, self.note)

    def render(self, buffer):
        line  = ' ' * (self.indent * 4)
        line += '{:<46} [{}]'.format(self.title, self.note.guid)
        buffer.append(line)
        self.row = len(buffer)

    def setTitle(self, title):
        self.title = title

class TagNode(Node):
    def __init__(self, tag, indent=0):
        super(TagNode, self).__init__(indent)

        self.tag = tag
        self.setName(tag.name)

    def addNote(self, note, notebook):
        node = NoteNode(note, notebook, self.indent + 1)
        self.addChild(node)

    def render(self, buffer):
        numNotes = len(self.children)

        line  = '-' if self.expanded or numNotes == 0 else '+'
        line += ' ' + self.name

        if numNotes != 0:
            line += ' (%d)' % numNotes

        buffer.append('{:<50} [{}]'.format(line, self.tag.guid))
        self.row = len(buffer)

        if self.expanded:
            for noteNode in self.children:
                noteNode.render(buffer)

class Explorer(object):
    def __init__(self):
        self.hidden        = True
        self.selectedNode  = None
        self.notebooks     = []
        self.tags          = []
        self.modifiedNodes = []
        self.dataFile      = None
        self.buffer        = None
        self.expandState   = {}

        self.refresh()

        self.dataFile = tempfile.NamedTemporaryFile(delete=True)
        autocmd('BufWritePre', self.dataFile.name, ':call Vim_GeeknoteSync()')

    def __del__(self):
        try:
            self.dataFile.close()
        except:
            pass

    def activateNode(self, line):
        guid = self.getNodeGuid(line)
        if guid is not None:
            node = registry[guid]
            node.activate()

            # Rerender the navigation window. Keep the current cursor postion.
            row, col = vim.current.window.cursor
            self.render()
            vim.current.window.cursor = (row, col)

    def addNotebook(self, notebook):
        node = NotebookNode(notebook)
        self.notebooks.append(node)
        self.notebooks.sort(key=lambda n: n.notebook.name.lower())

        registry[notebook.guid] = node

        notes = self.getNotes(notebook)
        notes.sort(key=lambda n: n.title)
        for note in notes:
            self.addNote(note)

    def addNote(self, note):
        notebook = registry[note.notebookGuid].notebook

        node = NoteNode(note, notebook)
        notebookNode = registry[notebook.guid]
        notebookNode.children.append(node)

        registry[note.guid] = node

    def addTag(self, tag):
        tagNode = TagNode(tag)

        for notebookNode in self.notebooks:
            for noteNode in notebookNode.children:
                if noteNode.note.tagGuids is not None:
                    if tag.guid in noteNode.note.tagGuids:
                        tagNode.addNote(noteNode.note, noteNode.notebook)

        self.tags.append(tagNode)
        self.tags.sort(key=lambda t: t.tag.name.lower())

        registry[tag.guid] = tagNode

    def applyChanges(self):
        if isBufferModified(self.buffer.number) is False:
            return

        for row in xrange(len(self.buffer)):
            line = self.buffer[row]

            # Look for changes to notes.
            r = re.compile('^\s+(.+)\[(.+)\]$')
            m = r.match(line)
            if m: 
                title = m.group(1).strip()
                guid  = m.group(2)
                node  = registry[guid]
                if isinstance(node, NoteNode):
                    # Did the user change the note's title?
                    if title != node.title:
                        node.setTitle(title)
                        if node not in self.modifiedNodes:
                            self.modifiedNodes.append(node)

                    # Did the user move the note into a different notebook?
                    navNotebook = self.findNotebookForNode(row)
                    if navNotebook is not None:
                        if navNotebook.guid != node.notebook.guid:
                            node.notebook = navNotebook
                            if node not in self.modifiedNodes:
                                self.modifiedNodes.append(node)
                continue

            # Look for changes to notebooks.
            r = re.compile('^[\+-](.+)\[(.+)\]$')
            m = r.match(line)
            if m:
                name = m.group(1).strip()
                guid = m.group(2)
                node = registry[guid]
                if isinstance(node, NotebookNode):
                    if name != node.name:
                        node.setName(name)
                        self.modifiedNodes.append(node)
                continue

    def commitChanges(self):
        self.applyChanges()
        for node in self.modifiedNodes:
            node.commitChanges()
        del self.modifiedNodes[:]

    #
    # Search upwards, starting at the given row number and return the first
    # note nodebook found. 
    #
    def findNotebookForNode(self, nodeRow):
        while nodeRow > 0:
            guid = self.getNodeGuid(self.buffer[nodeRow])
            if guid is not None: 
                node = registry[guid]
                if isinstance(node, NotebookNode):
                    return node.notebook
            nodeRow -= 1
        return None

    def getContainingNotebook(self, guid):
        node = registry[guid]
        if isinstance(node, NoteNode):
            return node.notebook
        return None

    #
    # Return a list of all notes contained in the given notebook.
    #
    def getNotes(self, notebook):
        # Ask for notes in the order in which they created.
        filter = NoteStore.NoteFilter(order = Types.NoteSortOrder.CREATED)
        filter.words = 'notebook:"%s" ' % notebook.name

        # Ask for the title, notebook, and tags, for each note.
        meta = NoteStore.NotesMetadataResultSpec()
        meta.includeTitle        = True
        meta.includeNotebookGuid = True
        meta.includeTagGuids     = True

        count  = Limits.EDAM_USER_NOTES_MAX
        result = noteStore.findNotesMetadata(authToken, filter, 0, count, meta)
        update_count = lambda c: max(c - len(result.notes), 0)
        count = update_count(count)
        
        while ((result.totalNotes != len(result.notes)) and count != 0):
            offset = len(result.notes)

            result.notes = noteStore.findNotesMetadata(
                authToken, filter, offset, count, meta)

            count = update_count(count)

        notes = []
        for key, note in enumerate(result.notes):
            notes.append(note)
        return notes

    def getSelectedNotebook(self):
        if self.buffer is None:
            return None

        prevWin = getActiveWindow()
        setActiveBuffer(self.buffer)
        text = vim.current.line
        setActiveWindow(prevWin)

        guid = self.getNodeGuid(text)
        if guid is not None:
            node = registry[guid]
            if isinstance(node, NotebookNode):
                return node.notebook
            if isinstance(node, NoteNode):
                return node.notebook
        return None

    def getNodeGuid(self, nodeText):
        r = re.compile('^.+\[(.+)\]$')
        m = r.match(nodeText)
        if m: 
            return m.group(1)
        return None

    #
    # Hide the navigation buffer. This closes the window it is displayed in but
    # does not destroy the buffer itself.
    #
    def hide(self):
        vim.command('{}bunload'.format(self.buffer.number))
        self.hidden = True

    def initView(self):
        origWin = getActiveWindow()
        setActiveBuffer(self.buffer)

        wnum = getActiveWindow()
        bnum = self.buffer.number

        setWindowVariable(wnum, 'winfixwidth', True)
        setWindowVariable(wnum, 'wrap'       , False)
        setWindowVariable(wnum, 'cursorline' , True)
        setBufferVariable(bnum, 'swapfile'   , False)
        setBufferVariable(bnum, 'buftype'    , 'quickfix')
        setBufferVariable(bnum, 'bufhidden'  , 'hide')

        vim.command('setfiletype geeknote')
        setActiveWindow(origWin)

    #
    # Is the navigation buffer hidden? When hidden, the buffer exists but is
    # not active in any window.
    #
    def isHidden(self):
        return self.hidden

    def refresh(self):
        self.saveExpandState()

        del self.notebooks[:]
        del self.tags[:]
        registry.clear()

        self.noteCounts = noteStore.findNoteCounts(
            authToken, NoteStore.NoteFilter(), False)

        notebooks = GeekNote().findNotebooks()
        for notebook in notebooks:
            self.addNotebook(notebook)

        tags = noteStore.listTags(authToken)
        for tag in tags:
            self.addTag(tag)

        self.restoreExpandState()

        if self.selectedNode is None:
            notebook = noteStore.getDefaultNotebook(authToken)
            self.selectNotebook(notebook)

    # Render the navigation buffer in the navigation window..
    def render(self):
        if self.buffer is None:
            return

        origWin = getActiveWindow()
        setActiveBuffer(self.buffer)

        # 
        # Before overwriting the naviagation window, look for any changes made
        # by the user. Do not synchronize them yet with the server, just make
        # sure they are not lost.
        #
        self.applyChanges()

        # Clear the navigation buffer to get rid of old content (if any).
        del self.buffer[:]

        # Prepare the new content and append it to the navigation buffer.
        content = []
        content.append('Notebooks:')
        content.append('{:=^90}'.format('='))

        # Render notebooks, notes, and tags
        for node in self.notebooks:
            node.render(content)

        content.append('')
        content.append('Tags:')
        content.append('{:=^90}'.format('='))

        for node in self.tags:
            node.render(content)

        # Write the content list to the buffer starting at row zero.
        self.buffer.append(content, 0)

        # Move the cursor over the selected node (if any)
        if self.selectedNode is not None:
            if self.selectedNode.row != -1:
                vim.current.window.cursor = (self.selectedNode.row, 0)

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

    def restoreExpandState(self):
        for guid in self.expandState:
            if guid in registry:
                node = registry[guid]
                if self.expandState[guid]:
                    node.expand()
                else:
                    node.close()

    def saveExpandState(self):
        for node in self.notebooks:
            self.expandState[node.notebook.guid] = node.expanded

        for node in self.tags:
            self.expandState[node.tag.guid] = node.expanded

    def selectNode(self, guid):
        node = registry[guid]
        self.selectedNode = node

        # Move the cursor over the node if the node has been rendered.
        if node.row != -1:
            origWin = getActiveWindow()
            setActiveBuffer(self.buffer)
            vim.current.window.cursor = (node.row, 0)
            setActiveWindow(origWin)

    def selectNote(self, note):
        notebook = registry[note.notebookGuid]
        notebook.expand()
        self.selectNode(note.guid)

    def selectNotebook(self, notebook):
        self.selectNode(notebook.guid)

    def selectNotebookIndex(self, index):
        if index < len(self.notebooks):
            node = self.notebooks[index]
            self.selectNode(node.notebook.guid)

    # Switch to the navigation buffer in the currently active window.
    def show(self):
        vim.command('topleft 50 vsplit {}'.format(self.dataFile.name))
        self.buffer = vim.current.buffer

        self.initView()
        self.render()

        noremap("<silent> <buffer> <cr>", 
            ":call Vim_GeeknoteActivateNode()<cr>")

        self.hidden = False

