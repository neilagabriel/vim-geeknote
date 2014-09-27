import vim
import re
import tempfile

from explorer          import *
from utils             import *
from geeknote.geeknote import *
from geeknote.tools    import *
from enml              import *

import evernote.edam.type.ttypes  as Types
import evernote.edam.error.ttypes as Errors

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
    notebook = None
    if explorer is not None:
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
        if explorer is None:
            return
        explorer.addNotebook(notebook)
    except:
        vim.command('echoerr "Failed to create notebook."')
        return

    explorer.render()
    explorer.selectNotebook(notebook)

def GeeknoteGetDefaultNotebook():
    try:
        noteStore = geeknote.getNoteStore()
        return noteStore.getDefaultNotebook(geeknote.authToken)

    except Errors.EDAMUserException as e:
        vim.command('echoerr "%s"' % e.string)

    except Errors.EDAMSystemException as e:
        vim.command('echoerr "Unexpected error - %d: %s"' % \
            (e.errorCode, e.string))

    return None

def GeeknoteGetNote(guid):
    geeknote = GeekNote()
    return geeknote.getNoteStore().getNote(
               geeknote.authToken, guid, True, False, False, False)

def GeeknoteSaveNote(filename):
    result    = False
    note      = openNotes[filename]['note']
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

    inputData = {}
    inputData['title']    = title
    inputData['content']  = textToENML(content)
    inputData['tags']     = None
    inputData['notebook'] = notebook.guid

    # Saving an existing note.
    if note is not None:
        result = bool(User().getEvernote().updateNote(
            guid=note.guid, **inputData))

        if title != origTitle:
            if explorer is not None:
                explorer.refresh()    
                explorer.render()
                explorer.selectNote(note)

    # Saving a new note.
    else:
        try:
            note = User().getEvernote().createNote(**inputData)
            if explorer is not None:
                explorer.addNote(note, notebook)
                explorer.expandNotebook(notebook.guid)
                explorer.render()
                explorer.selectNote(note)
            openNotes[filename]['note'] = note
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

    opened = False
    for fname in openNotes:
        if openNotes[fname]['title'] == title:
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

    if explorer is None:
        dataFile = tempfile.NamedTemporaryFile(delete=True)
        vim.command('topleft 50 vsplit {}'.format(dataFile.name))

        noremap("<silent> <buffer> <cr>", 
                ":call Vim_GeeknoteActivateNode()<cr>")

        explorer = Explorer(geeknote, dataFile, vim.current.buffer)
        notebook = GeeknoteGetDefaultNotebook()
        if notebook is not None:
            explorer.selectNotebook(notebook)
        else:
            explorer.selectNotebookIndex(0)
    else:
        if explorer.isHidden():
            vim.command('topleft 50 vsplit')
            explorer.show()
        else:
            explorer.hide()

