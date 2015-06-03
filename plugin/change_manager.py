class ChangeManager(object):
    def __init__(self):
        self.changes = []

    def applyChanges(self):
        for change in self.changes:
            change.apply()
        self.clear()

    def clear(self):
        del self.changes[:]

    def pendChange(self, change):
        self.changes.append(change)

