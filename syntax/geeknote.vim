syn match GeeknoteSep      #=\+#
syn match GeeknoteGUID     #\[.\+\]#

syn match GeeknoteChild    #^.\+\[.\+\]#     contains=GeeknoteGUID
syn match GeeknoteParent   #^[+-].\+\[.\+\]# contains=GeeknoteGUID

hi def link GeeknoteGUID   ignore
hi def link GeeknoteSep    Question
hi def link GeeknoteParent Title
hi def link GeeknoteChild  Type
