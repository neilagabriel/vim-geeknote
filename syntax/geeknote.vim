syn match GeeknoteSep      #=\+#
syn match GeeknoteFlag     #^T\ #
syn match GeeknoteFlag     #^N\ #
syn match GeeknoteFlag     #^\ \+n\ #

syn match GeeknoteGUID     #\[.\+\]#

syn match GeeknoteTag      #^T\ .\+# contains=GeeknoteFlag
syn match GeeknoteNotebook #^N\ .\+# contains=GeeknoteFlag
syn match GeeknoteNote     #^\ \+n\ .\+ \[.\+\]# contains=GeeknoteFlag,GeeknoteGUID

hi def link GeeknoteFlag     ignore
hi def link GeeknoteGUID     ignore
hi def link GeeknoteSep      Question
hi def link GeeknoteTag      Type
hi def link GeeknoteNotebook Title
hi def link GeeknoteNote     Type
