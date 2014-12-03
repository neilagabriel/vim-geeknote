# vim:fileencoding=utf-8:noet
from __future__ import (unicode_literals, division, absolute_import, print_function)

import os
import re

from powerline.bindings.vim import buffer_name

GEEKNOTE_RE = re.compile('__Geeknote__')

def geeknote(matcher_info):
	name = buffer_name(matcher_info)
	return name and GEEKNOTE_RE.match(os.path.basename(name))

GEEKNOTE_EXPLORER_RE = re.compile('__GeeknoteExplorer__')

def geeknote_explorer(matcher_info):
	name = buffer_name(matcher_info)
	return name and GEEKNOTE_EXPLORER_RE.match(os.path.basename(name))
