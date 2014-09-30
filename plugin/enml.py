import vim
import os
import re

from geeknote.editor import Editor
from bs4             import BeautifulSoup

def ENMLtoText(contentENML):
    format = 'geeknote'
    if int(vim.eval('exists("g:GeeknoteFormat")')):
        format = vim.eval('g:GeeknoteFormat')

    if format != 'geeknote':
        soup = BeautifulSoup(contentENML.decode('utf-8'))
        sections = soup.select('pre')
        if len(sections) >= 1:
            content = ''
            for c in sections[0].contents:
                content = u''.join((content, c))
            content = re.sub(r' *\n', os.linesep, content)
            return content.encode('utf-8')
    return Editor.ENMLtoText(contentENML)


def textToENML(content):
    format = 'geeknote'
    if int(vim.eval('exists("g:GeeknoteFormat")')):
        format = vim.eval('g:GeeknoteFormat')

    if format == 'geeknote':
        return Editor.textToENML(content) 

    content = content.replace('<', '&lt;')
    content = content.replace('>', '&gt;')
    content = unicode(content, "utf-8")
    contentHTML = u''.join(('<pre>', content, '</pre>')).encode("utf-8")

    enml = Editor.wrapENML(contentHTML)
    return enml
