syn match GeeknoteSep      #=\+#
syn match GeeknoteGUID     #\[.\+\]#

syn match GeeknoteNotebook #^[+-].\+\[.\+\]# contains=GeeknoteGUID
syn match GeeknoteNote     #^    .\+\[.\+\]# contains=GeeknoteGUID

hi def link GeeknoteGUID     ignore
hi def link GeeknoteSep      Question
hi def link GeeknoteNotebook Title
hi def link GeeknoteNote     Type
