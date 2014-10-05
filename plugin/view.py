import vim
import tempfile

from enml  import *
from utils import *

from geeknote.geeknote import *

# Maps buffer names to NoteTracker objects.
openNotes = {}

# Connection to Geeknote (XXX: move this out)
geeknote  = GeekNote()
authToken = geeknote.authToken
noteStore = geeknote.getNoteStore()

#
# Holds all information that needs to be tracked for any note that has been
# opened.
#
class NoteTracker(object):
    def __init__(self, note, buffer):
        self.note     = note
        self.buffer   = buffer
        self.modified = False

# Close all opened notes.
def GeeknoteCloseAllNotes():
    for filename in openNotes:
        os.remove(filename)
    openNotes.clear()

# Close the note associated with the given buffer name.
def GeeknoteCloseNote(filename):
    if filename in openNotes:
        os.remove(filename)
        del openNotes[filename]

# Commit any changes that were made to the note in the buffer to the note.
def GeeknoteCommitChangesToNote(note):
    tracker = GeeknoteGetNoteTracker(note)

    # If the note has not been modified, there's nothing more to do.
    if tracker.modified is False:
        return False

    #
    # Now that we know the note has been modified, read the note's buffer and
    # pull out the note's title and content.
    #
    content = ''
    title   = tracker.note.title
    lines   = open(tracker.buffer.name, 'r').readlines()
    if len(lines) > 0:
        title = lines.pop(0).strip()
        while len(lines) > 0:
            if lines[0].strip() == '':
                lines.pop(0)
            else:
                break
    for r in lines:
        content += r

    # Update the note's title and content from what was read from the buffer.
    tracker.note.title   = title
    tracker.note.content = textToENML(content)

    return True
 
# Find the object that is tracking the given note (None if note opened).
def GeeknoteGetNoteTracker(note):
    for filename in openNotes:
        if openNotes[filename].note.guid == note.guid:
            return openNotes[filename]
    return None

# Given the name of a buffer, find the note that the buffer represents.
def GeeknoteGetOpenNote(filename):
    if filename in openNotes:
        return openNotes[filename].note
    return None

# Load a given note's content
def GeeknoteLoadNote(note):
    return noteStore.getNote(authToken, note.guid, True, False, False, False)

# Determine if the note has been modified since since it was last saved.
def GeeknoteNoteIsModified(note):
    tracker = GeeknoteGetNoteTracker(note)
    return tracker.modified

# Determine if the user has already opened the given note.
def GeeknoteNoteIsOpened(note):
    tracker = GeeknoteGetNoteTracker(note)
    return True if tracker is not None else False

# Open a note in the active window.
def GeeknoteOpenNote(note):
    #
    # Check to see if the note is already opened before opening it in a new
    # buffer.
    #
    opened = GeeknoteNoteIsOpened(note)
    if opened is False:
        # Load the note's content
        note    = GeeknoteLoadNote(note)
        content = ENMLtoText(note.content)
        content = tools.stdoutEncode(content)

        # Write the note's title and content to a temporary file.
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(note.title + '\n\n')
        
        isNoteEmpty = not content.strip()
        if isNoteEmpty is False:
            f.write(content)
        else:
            f.write("<add content here>\n")
        f.close()

        # Now edit the file in a new buffer within the active window.
        vim.command('edit {}'.format(f.name))

        # Position the cursor at a convenient location if opening an empty note
        if isNoteEmpty:
            vim.current.window.cursor = (3, 0)

        #
        # Create an object to keep track of the note and all associated
        # information while it's opened.
        #
        openNotes[f.name] = NoteTracker(note, vim.current.buffer)

        # Register callbacks for the buffer events that affect the note.
        autocmd('BufWritePre', 
                f.name, 
                ':call Vim_GeeknotePrepareToSaveNote("{}")'.format(f.name))

        autocmd('BufWritePost',
                f.name, 
                ':call Vim_GeeknoteSaveNote("{}")'.format(f.name))
     
        autocmd('BufDelete',
                f.name, 
                ':call Vim_GeeknoteCloseNote("{}")'.format(f.name))
    #
    # Otherwise, the note has aleady been opened. Simply switch the active window
    # to the note's buffer.
    #
    else:
        tracker = GeeknoteGetNoteTracker(note)
        vim.command("buffer {}".format(tracker.buffer.name))

    #
    # By default, Geeknote expects to receive notes with markdown-formated
    # content. Set the buffer's 'filetype' and 'syntax' options.
    #
    # TODO: Figure out why setting the 'syntax' buffer option alone does not
    #       enable syntax highlighting and why setlocal is needed instead.
    #
    vim.current.buffer.options['filetype'] = 'markdown'
    vim.command('setlocal syntax=markdown')

def GeeknotePrepareToSaveNote(filename):
    filename = os.path.abspath(filename)
    tracker  = openNotes[filename]
    tracker.modified = tracker.buffer.options['modified']

