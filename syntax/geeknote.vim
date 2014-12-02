syn match GeeknoteSep         #=\+#

syn match GeeknoteNotebookKey #N\[.\+\]#
syn match GeeknoteNoteKey     #n\[.\+\]#
syn match GeeknoteTagKey      #T\[.\+\]#

syn match GeeknoteNotebook    #^.\+N\[.\+\]# contains=GeeknoteNotebookKey
syn match GeeknoteNote        #^.\+n\[.\+\]# contains=GeeknoteNoteKey
syn match GeeknoteTag         #^.\+T\[.\+\]# contains=GeeknoteTagKey

hi def link GeeknoteNotebookKey ignore
hi def link GeeknoteNoteKey     ignore
hi def link GeeknoteTagKey      ignore
hi def link GeeknoteSep         Question
hi def link GeeknoteNotebook    Title
hi def link GeeknoteTag         Title
hi def link GeeknoteNote        Type
