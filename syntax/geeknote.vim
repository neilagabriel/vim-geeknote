syn match GeeknoteSep      #=\+#
syn match GeeknoteFlag     #T\ #
syn match GeeknoteFlag     #N\ #
syn match GeeknoteTag      #T\ .\+# contains=GeeknoteFlag
syn match GeeknoteNotebook #N\ .\+# contains=GeeknoteFlag

hi def link GeeknoteFlag     ignore
hi def link GeeknoteSep      Question
hi def link GeeknoteTag      Type
hi def link GeeknoteNotebook Type
