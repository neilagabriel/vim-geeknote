import vim
import re
import tempfile

from view  import *
from utils import *

from geeknote.geeknote import *

import evernote.edam.limits.constants as Limits

#======================== Classes ============================================#

class Node(object):
    def __init__(self):
        self.children = []
        self.guid     = None
        self.row      = -1
        self.close()

    def addChild(self, node):
        self.children.append(node)

    def close(self):
        self.expanded = False

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
        self.notes    = []
        self.setName(notebook.name)

    def setName(self, name):
        self.name = name

class NoteNode(Node):
    def __init__(self, note, notebook):
        super(NoteNode, self).__init__()

        self.note     = note
        self.notebook = notebook
        self.setTitle(note.title)

    def setTitle(self, title):
        self.title = title

class TagNode(Node):
    def __init__(self, tag):
        super(TagNode, self).__init__()

        self.tag = tag
        self.setName(tag.name)

    def render(self, buffer):
        row      = len(buffer) + 1
        numNotes = len(self.children)

        line  = '-' if self.expanded or numNotes == 0 else '+'
        line += ' ' + self.name
        buffer.append('{:<50} [{}]'.format(line, self.tag.guid))

        self.row = row
        row += 1

        if self.expanded:
            for noteNode in self.children:
                note  = noteNode.note
                title = noteNode.title

                line  = '    {:<46} [{}]'.format(title, note.guid)
                buffer.append(line)
                noteNode.row = row
                row += 1

class Explorer(object):
    notebooks     = []
    tags          = []
    guidMap       = {}
    expandState   = {}
    modifiedNodes = []
    dataFile      = None
    buffer        = None

    def __init__(self, geeknote):
        self.geeknote  = geeknote
        self.noteStore = self.geeknote.getNoteStore()
        self.authToken = self.geeknote.authToken
        self.hidden    = True

        self.refresh()

        self.dataFile = tempfile.NamedTemporaryFile(delete=True)
        autocmd('BufWritePre', self.dataFile.name, ':call Vim_GeeknoteSync()')

    def __del__(self):
        try:
            self.dataFile.close()
        except:
            pass

    def activateNode(self, line):
        r = re.compile('^.+\[(.+)\]$')
        m = r.match(line)
        if not m: return

        guid = m.group(1)
        node = self.guidMap[guid]

        if isinstance(node, NotebookNode):
            notebook = node.notebook
            self.toggleNotebook(notebook.guid)

            # Rerender the navigation window. Keep the current cursor postion.
            row, col = vim.current.window.cursor
            self.render()
            vim.current.window.cursor = (row, col)
            return
         
        if isinstance(node, NoteNode):
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

            GeeknoteOpenNote(node.note)
            setActiveWindow(origWin)
            return

        if isinstance(node, TagNode):
            node.toggle()

            # Rerender the navigation window. Keep the current cursor postion.
            row, col = vim.current.window.cursor
            self.render()
            vim.current.window.cursor = (row, col)

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
                node  = self.guidMap[guid]
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
                node = self.guidMap[guid]
                if isinstance(node, NotebookNode):
                    if name != node.name:
                        node.setName(name)
                        self.modifiedNodes.append(node)
                continue

    def addNotebook(self, notebook):
        node = NotebookNode(notebook)
        self.notebooks.append(node)
        self.notebooks.sort(key=lambda n: n.notebook.name.lower())

        self.guidMap[notebook.guid] = node

        notes = self.getNotes(notebook)
        notes.sort(key=lambda n: n.title)
        for note in notes:
            self.addNote(note)

        if notebook.guid not in self.expandState:
            self.expandState[notebook.guid] = False

    def addNote(self, note):
        notebook = self.guidMap[note.notebookGuid].notebook

        node = NoteNode(note, notebook)
        notebookNode = self.guidMap[notebook.guid]
        notebookNode.notes.append(node)

        self.guidMap[note.guid] = node

    def addTag(self, tag):
        tagNode = TagNode(tag)

        for notebookNode in self.notebooks:
            for noteNode in notebookNode.notes:
                if noteNode.note.tagGuids is not None:
                    if tag.guid in noteNode.note.tagGuids:
                        tagNode.addChild(
                            NoteNode(noteNode.note, noteNode.notebook))

        self.tags.append(tagNode)
        self.tags.sort(key=lambda t: t.tag.name.lower())

        self.guidMap[tag.guid] = tagNode

    def closeAll(self):
        for guid in self.expandState:
            self.closeNotebook(guid)

    def closeNotebook(self, guid):
        self.expandState[guid] = False

    def expandAll(self):
        for guid in self.expandState:
            self.expandNotebook(guid)

    def expandNotebook(self, guid):
        self.expandState[guid] = True

    #
    # Search upwards, starting at the given row number and return the first
    # note node found. 
    #
    def findNotebookForNode(self, nodeRow):
        while nodeRow > 0:
            guid = self.getNodeGuid(self.buffer[nodeRow])
            if guid is not None: 
                node = self.guidMap[guid]
                if isinstance(node, NotebookNode):
                    return node.notebook
            nodeRow -= 1
        return None

    def getBuffer(self):
        return self.buffer

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

    def getNoteCount(self, notebook):
        if notebook.guid in self.noteCounts.notebookCounts:
            return self.noteCounts.notebookCounts[notebook.guid]
        return 0

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

    def getContainingNotebook(self, guid):
        node = self.guidMap[guid]
        if isinstance(node, NoteNode):
            return node.notebook
        return None

    def getSelectedNotebook(self):
        if self.buffer is None:
            return None

        prevWin = getActiveWindow()
        setActiveBuffer(self.buffer)
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

    #
    # Move the given note into the specified notebook.
    #
    def moveNote(self, note, notebook):
        note.notebookGuid = notebook.guid
        try:
            return self.noteStore.updateNote(self.authToken, note)
        except:
            vim.command('echoerr "Failed to move note."')
        return None

    def refresh(self):
        del self.notebooks[:]
        self.guidMap.clear()

        self.noteCounts = self.noteStore.findNoteCounts(
            self.authToken, NoteStore.NoteFilter(), False)

        notebooks = GeekNote().findNotebooks()
        for notebook in notebooks:
            self.addNotebook(notebook)

        tags = self.noteStore.listTags(self.authToken)
        for tag in tags:
            self.addTag(tag)

    def renameNotebook(self, notebook, name):
        notebook.name = name
        try:
            return self.noteStore.updateNotebook(self.authToken, notebook)

        except Errors.EDAMUserException as e:
            vim.command('echoerr "%s"' % e.string)

        except Errors.EDAMSystemException as e:
            vim.command('echoerr "Error %d: %s"' % \
                (e.errorCode, e.string))

        except Errors.EDAMNotFoundException as e:
            vim.command('echoerr "Error: not found %s (type=%s)"' % \
                (e.key, e.identifier))

        return None

    def renameNote(self, note, title):
        note.title = title
        try:
            return self.noteStore.updateNote(self.authToken, note)

        except Errors.EDAMUserException as e:
            vim.command('echoerr "%s"' % e.string)

        except Errors.EDAMSystemException as e:
            vim.command('echoerr "Error %d: %s"' % \
                (e.errorCode, e.string))

        except Errors.EDAMNotFoundException as e:
            vim.command('echoerr "Error: not found %s (type=%s)"' % \
                (e.key, e.identifier))

        return None

    def selectNode(self, guid):
        if self.buffer is None:
            return

        origWin = getActiveWindow()
        setActiveBuffer(self.buffer)
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
            if self.expandState[guid] is True:
                self.closeNotebook(guid)
            else:
                self.expandNotebook(guid)

    #
    # Switch to the navigation buffer in the currently active window.
    #
    def show(self):
        vim.command('topleft 50 vsplit {}'.format(self.dataFile.name))
        self.buffer = vim.current.buffer

        self.initView()
        self.render()

        noremap("<silent> <buffer> <cr>", 
            ":call Vim_GeeknoteActivateNode()<cr>")

        self.hidden = False

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

        #
        # Render notebooks and notes
        #

        row = 3
        for node in self.notebooks:
            notebook = node.notebook
            numNotes = self.getNoteCount(notebook)
            expand   = self.expandState[notebook.guid]

            line  = '-' if expand is True or numNotes == 0 else '+'
            line += ' ' + node.name
            content.append('{:<50} [{}]'.format(line, notebook.guid))
            node.row = row
            row += 1

            if expand is True:
                for noteNode in node.notes:
                    note  = noteNode.note
                    title = noteNode.title

                    line  = '    {:<46} [{}]'.format(title, note.guid)
                    content.append(line)
                    noteNode.row = row
                    row += 1
        content.append('')
        row += 1

        #
        # Render tags
        #
        content.append('Tags:')
        content.append('{:=^90}'.format('='))
        row += 2

        for node in self.tags:
            node.render(content)

        # Write the content list to the buffer starting at row zero.
        self.buffer.append(content, 0)

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
                 self.renameNotebook(node.notebook, node.name)
                 continue
             if isinstance(node, NoteNode):
                 if node.title != node.note.title:
                     self.renameNote(node.note, node.title)
                 if node.notebook.guid != node.note.notebookGuid:
                     self.moveNote(node.note, node.notebook)
                 continue
        del self.modifiedNodes[:]

