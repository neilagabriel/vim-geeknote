# vim:fileencoding=utf-8:noet
from __future__ import (unicode_literals, division, absolute_import, print_function)

try:
	import vim
except ImportError:
	vim = object()

from powerline.bindings.vim import bufvar_exists
from powerline.segments.vim import window_cached


@window_cached
def geeknote_get_note_title(pl):
	if not bufvar_exists(None, 'GeeknoteTitle'):
		return None

	title = vim.eval('getbufvar("%", "GeeknoteTitle")')
	return [{
		'contents': title,
		'highlight_group': ['file_name'],
	}]

def geeknote_get_notebook_name(pl):
	if not bufvar_exists(None, 'GeeknoteNotebook'):
		return None

	name = vim.eval('getbufvar("%", "GeeknoteNotebook")')
	return [{
		'contents': name,
		'highlight_group': ['file_name'],
	}]
