import re

class NotebookStub(object):
    def __init__(self, name, guid, notes):
        self.name  = name
        self.guid  = guid
        self.notes = notes

        for note in self.notes:
            note.notebookGuid = guid

class NoteStub(object):
    def __init__(self, title, guid):
        self.title = title
        self.guid  = guid
        self.notebookGuid = None

class NoteSearch(object):
    def __init__(self):
        self.notes = []
        self.totalNotes = 0

class NoteStoreStub(object):
    def __init__(self):
        self.notebooks = (
        [
            NotebookStub(
                'Notebook1', '00000000-0000-0000-0000-000000000000',
                ([
                    NoteStub('Note1_1', '00000000-0000-0000-0001-000000000000'),
                    NoteStub('Note1_2', '00000000-0000-0000-0002-000000000000'),
                    NoteStub('Note1_3', '00000000-0000-0000-0003-000000000000'),
                    NoteStub('Note1_4', '00000000-0000-0000-0004-000000000000'),
                    NoteStub('Note1_5', '00000000-0000-0000-0005-000000000000'),
                ])),

            NotebookStub(
                'Notebook2', '00000000-0000-0000-0000-000000000001',
                ([
                    NoteStub('Note2_1', '00000000-0000-0000-0006-000000000000'),
                    NoteStub('Note2_2', '00000000-0000-0000-0007-000000000000'),
                    NoteStub('Note2_3', '00000000-0000-0000-0009-000000000000'),
                    NoteStub('Note2_4', '00000000-0000-0000-000a-000000000000'),
                    NoteStub('Note2_5', '00000000-0000-0000-000b-000000000000'),
                ]))
        ])

    def findNoteCounts(self, authToken, filter, ignored):
        return None

    def findNotesMetadata(self, authToken, filter, offset, count, meta):
        search = NoteSearch()

        r = re.compile('notebook:(?:\s+)?')
        m = r.match(filter.words)

        if m:
            print m.group

        search.notes = self.notebooks[0].notes
        search.totalNotes = len(self.notebooks[0].notes)
        return search

    def getDefaultNotebook(self, authToken):
        return self.notebooks[0]

    def listNotebooks(self, authToken):
        return self.notebooks

    def listTags(self, authToken):
        return []

class GeekNoteStub(object):
    def __init__(self):
        self.noteStore = NoteStoreStub()
        self.authToken = "authToken"

    def getNoteStore(self):
        return self.noteStore
