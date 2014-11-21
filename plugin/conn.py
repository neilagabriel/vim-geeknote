import evernote.edam.limits.constants as Limits

from geeknote.geeknote import *

# Connection to Geeknote
geeknote  = GeekNote()
authToken = geeknote.authToken
noteStore = geeknote.getNoteStore()

def GeeknoteCreateNewNote(note):
    return noteStore.createNote(authToken, note)

def GeeknoteCreateNewNotebook(notebook):
    return noteStore.createNotebook(authToken, notebook)

def GeeknoteFindNoteCounts():
    return noteStore.findNoteCounts(authToken, NoteStore.NoteFilter(), False)

def GeeknoteGetDefaultNotebook():
    return noteStore.getDefaultNotebook(authToken)

def GeeknoteGetNotes(searchWords=""):
    filter = NoteStore.NoteFilter(order = Types.NoteSortOrder.UPDATED)
    filter.words = searchWords

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
        result.notes += noteStore.findNotesMetadata(
            authToken, filter, offset, count, meta).notes
        count = update_count(count)

    notes = []
    for key, note in enumerate(result.notes):
        notes.append(note)

    return notes

def GeeknoteGetNotebook(guid):
    try:
        return noteStore.getNotebook(authToken, guid)
    except:
        return None

def GeeknoteGetNotebooks():
    return noteStore.listNotebooks(authToken)

def GeeknoteGetTags():
    return noteStore.listTags(authToken)

def GeeknoteLoadNote(note):
    return noteStore.getNote(authToken, note.guid, True, False, False, False)

def GeeknoteRefreshNoteMeta(note):
    return noteStore.getNote(authToken, note.guid, False, False, False, False)

def GeeknoteUpdateNote(note):
    noteStore.updateNote(authToken, note)

def GeeknoteUpdateNotebook(notebook):
    noteStore.updateNotebook(authToken, notebook)

