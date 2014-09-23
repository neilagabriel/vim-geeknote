import vim
import re
import tempfile

from explorer          import *
from utils             import *
from geeknote.geeknote import *
from geeknote.tools    import *
from geeknote.editor   import Editor

import evernote.edam.type.ttypes as Types

#======================== Globals ============================================#

explorer  = None
openNotes = {}
geeknote  = GeekNote()

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
        note = GeeknoteGetNote(guid)

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

def GeeknoteGetNote(guid):
    geeknote = GeekNote()
    return geeknote.getNoteStore().getNote(
               geeknote.authToken, guid, True, False, False, False)

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
    global geeknote

    if explorer is None:
        dataFile = tempfile.NamedTemporaryFile(delete=True)
        vim.command('topleft 50 vsplit {}'.format(dataFile.name))

        noremap("<silent> <buffer> <cr>", 
                ":call Vim_GeeknoteActivateNode()<cr>")

        explorer = Explorer(geeknote, dataFile, vim.current.buffer)
    else:
        explorer.render()

    explorer.selectNotebookIndex(0)

