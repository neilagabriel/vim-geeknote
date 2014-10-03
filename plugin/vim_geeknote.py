import vim
import re

from explorer          import *
from utils             import *
from geeknote.geeknote import *
from geeknote.tools    import *
from enml              import *

import evernote.edam.type.ttypes  as Types
import evernote.edam.error.ttypes as Errors

#======================== Globals ============================================#

geeknote  = GeekNote()
authToken = geeknote.authToken
noteStore = geeknote.getNoteStore()
explorer  = Explorer(geeknote)
openNotes = {}

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

def GeeknoteTerminate():
    for key in openNotes:
        os.remove(key)

def GeeknoteCloseNote(filename):
    if filename in openNotes:
        os.remove(filename)
        del openNotes[filename]

def GeeknoteCreateNote(name):
    #
    # Figure out what notebook to place the note in. Give preference
    # to the notebook selected in the explorer window (if one is 
    # selected). Otherwise, place it into the default notebook.
    #
    notebook = explorer.getSelectedNotebook()
    if notebook is None:
        notebook = GeeknoteGetDefaultNotebook()

    if notebook is None:
        vim.command('echoerr "Please select a notebook first."')
        return

    # Cleanup the name of the note.
    name = name.strip('"\'')

    # Find a good place to open a new window for the note content.
    origWin = getActiveWindow()
    if isWindowUsable(origWin) is False:
        prevWin = getPreviousWindow()
        setActiveWindow(prevWin)
        if isWindowUsable(prevWin) is False:
            vim.command('botright vertical new')

    #
    # Finally, open the blank note. The note will note be saved to the server
    # until the user saves the buffer.
    #
    GeeknoteOpenNote(None, name, notebook)

def GeeknoteCreateNotebook(name):
    name = name.strip('"\'')
    try:
        notebook = Notebooks().create(name)
        explorer.addNotebook(notebook)
    except:
        vim.command('echoerr "Failed to create notebook."')
        return

    explorer.render()
    explorer.selectNotebook(notebook)

def GeeknoteGetDefaultNotebook():
    try:
        return noteStore.getDefaultNotebook(authToken)

    except Errors.EDAMUserException as e:
        vim.command('echoerr "%s"' % e.string)

    except Errors.EDAMSystemException as e:
        vim.command('echoerr "Unexpected error - %d: %s"' % \
            (e.errorCode, e.string))

    return None

def GeeknoteGetNote(guid):
    return geeknote.getNoteStore().getNote(
               authToken, guid, True, False, False, False)

def GeeknoteSaveAsNote():
    global explorer

    #
    # Figure out what notebook to place the note in. Give preference
    # to the notebook selected in the explorer window (if one is 
    # selected). Otherwise, place it into the default notebook.
    #
    notebook = None
    if explorer is not None:
        notebook = explorer.getSelectedNotebook()

    if notebook is None:
        notebook = GeeknoteGetDefaultNotebook()

    if notebook is None:
        vim.command('echoerr "Please select a notebook first."')
        return

    title = ''
    rows  = len(vim.current.buffer)
    if rows > 0:
        title = vim.current.buffer[0].strip()
    else:
        vim.command('echoerr "Cannot save empty note."')
        return

    content = ''
    if rows > 1:
        start = 1
        while start < rows:
            if vim.current.buffer[start].strip() != '':
                break
            start += 1
        for r in range(start, len(vim.current.buffer)):
            content += vim.current.buffer[r] + '\n'

        note         = Types.Note()
        note.title   = title
        note.content = textToENML(content)
        note.created = None
        note.notebookGuid = notebook.guid

    try:
        note = noteStore.createNote(authToken, note)
        note = GeeknoteGetNote(note.guid)
    except Exception as e:
        GeeknoteHandleNoteSaveFailure(note, e)
        return

    explorer.addNote(note, notebook)
    explorer.expandNotebook(notebook.guid)
    explorer.render()
    explorer.selectNote(note)

    GeeknoteOpenNote(note, title, notebook)

def GeeknotePrepareToSaveNote(filename):
    path = os.path.abspath(filename)
    for buffer in vim.buffers:
        if buffer.name == path:
            openNotes[filename]['modified'] = buffer.options['modified']
            return

def GeeknoteSaveNote(filename):
    note = openNotes[filename]['note']
    if openNotes[filename]['modified'] is False:
        return note

    result    = False
    title     = openNotes[filename]['title']
    notebook  = openNotes[filename]['notebook']
    origTitle = title

    content = ''
    lines = open(filename, 'r').readlines()
    if len(lines) > 0:
        title = lines.pop(0).strip()
        while len(lines) > 0:
            if lines[0].strip() == '':
                lines.pop(0)
            else:
                break

    for r in lines:
        content += r

    try:
        # Saving an existing note.
        if note is not None:
            note.title   = title
            note.content = textToENML(content)
            note.notebookGuid = notebook.guid
            noteStore.updateNote(authToken, note)

            if title != origTitle:
                explorer.refresh()    
                explorer.render()

        # Saving a new note.
        else:
            note         = Types.Note()
            note.title   = title
            note.content = textToENML(content)
            note.created = None
            note.notebookGuid = notebook.guid

            note = noteStore.createNote(authToken, note)
            note = GeeknoteGetNote(note.guid)

            explorer.addNote(note, notebook)
            explorer.expandNotebook(notebook.guid)
            explorer.render()

            openNotes[filename]['note'] = note
    except Exception as e:
        GeeknoteHandleNoteSaveFailure(note, e)
        return None

    explorer.selectNote(note)
    return note

def GeeknoteHandleNoteSaveFailure(note, e):
    msg  = '%s\n' % e
    msg += '+------------------- WARNING -------------------+\n'
    msg += '|                                               |\n'
    msg += '| Failed to save note (see error above)         |\n'
    msg += '|                                               |\n'
    msg += '| Save buffer to a file to avoid losing content |\n'
    msg += '|                                               |\n'
    msg += '+------------------- WARNING -------------------+\n'
    vim.command('echoerr "%s"' % msg)

def GeeknoteSync():
    explorer.syncChanges()
    explorer.refresh()    
    explorer.render()

# Open an existing or new note in the active window.
def GeeknoteOpenNote(note, title=None, notebook=None):
    if note is not None:
        title    = note.title
        notebook = explorer.getContainingNotebook(note.guid)

    #
    # Check to see if the note is already opened before opening it in a new
    # buffer. Only do this when opening an existing note.
    #
    opened = False
    if note is not None:
        for fname in openNotes:
            if openNotes[fname]['note'].guid == note.guid:
                opened = True
                break

    if opened is False:
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(title + '\n\n')

        if note is not None:
            text = ENMLtoText(note.content)
            text = tools.stdoutEncode(text)
            f.write(text)
        else:
            f.write("<add content here>\n")
        f.close()

        openNotes[f.name] = {'note':note, 'title':title, 'notebook':notebook}

        vim.command('edit {}'.format(f.name))

        # Position the cursor at a convenient location when opening a new note.
        if note is None:
            vim.current.window.cursor = (3, 0)

        autocmd('BufWritePre', f.name, 
            ':call Vim_GeeknotePrepareToSaveNote("{}")'.format(f.name))

        autocmd('BufWritePost', f.name, 
            ':call Vim_GeeknoteSaveNote("{}")'.format(f.name))
     
        autocmd('BufDelete', f.name, 
            ':call Vim_GeeknoteCloseNote("{}")'.format(f.name))
    else:
        vim.command("buffer {}".format(fname))

    #
    # By default, Geeknote expects to receive notes with markdown-formated
    # content. Set the buffer's 'filetype' and 'syntax' options.
    #
    # TODO: Figure out why setting the 'syntax' buffer option alone does not
    #       enable syntax highlighting and why setlocal is needed instead.
    #
    vim.current.buffer.options['filetype'] = 'markdown'
    vim.command('setlocal syntax=markdown')

def GeeknoteToggle():
    global explorer
    global geeknote

    if explorer.isHidden():
        explorer.show()
    else:
        explorer.hide()

