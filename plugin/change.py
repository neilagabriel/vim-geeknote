from conn import *

#======================== Change =============================================#

class Change(object):
    def apply(self):
        pass

#======================== NoteRenamed ========================================#

class NoteRenamed(Change):
    def __init__(self, note, newTitle):
        self.note = note
        self.newTitle = newTitle

    def apply(self):
        self.note.title = self.newTitle
        GeeknoteUpdateNote(self.note)

#======================== NoteMoved ==========================================#

class NoteMoved(Change):
    def __init__(self, note, newNotebookGuid):
        self.note = note
        self.newNotebookGuid = newNotebookGuid

    def apply(self):
        self.note.notebookGuid = self.newNotebookGuid
        GeeknoteUpdateNote(self.note)

#======================== NotebookRenamed ====================================#

class NotebookRenamed(Change):
    def __init__(self, notebook, newName):
        self.notebook = notebook
        self.newName = newName

    def apply(self):
        self.notebook.name = self.newName
        GeeknoteUpdateNotebook(self.notebook)

