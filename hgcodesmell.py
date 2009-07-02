# -*- coding: utf-8 -*-
"""
    hgcodesmell
    ~~~~~~~~~~~

    Mercurial extension to warn about smelly changes before committing.

    Usage: activate the extension and set the name of your changelog in hgrc::

        [extensions]
        hgcodesmell = path/to/hgcodesmell.py

    :copyright: 2009 by Georg Brandl.
    :license:
        This program is free software; you can redistribute it and/or modify it
        under the terms of the GNU General Public License as published by the
        Free Software Foundation; either version 2 of the License, or (at your
        option) any later version.

        This program is distributed in the hope that it will be useful, but
        WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
        Public License for more details.

        You should have received a copy of the GNU General Public License along
        with this program; if not, write to the Free Software Foundation, Inc.,
        51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import re
from mercurial import commands, cmdutil, extensions, patch
try:
    from hgext.color import colorwrap
except ImportError:
    colorwrap = lambda o, s: o(s)

def new_commit(orig_commit, ui, repo, *pats, **opts):
    smelly = 0
    diff = patch.diff(repo, *cmdutil.revpair(repo, None))
    for chunk in diff:
        chunklines = chunk.splitlines()
        for line in chunklines:
            if line.startswith('+') and 'print' in line:
                ui.warn('Smelly change (print statement):\n')
                colorwrap(ui.write, chunk)
                smelly += 1
                break
    if smelly:
        if not ui.prompt('Found %d smelly changes. Continue (y/N)?' % smelly,
                         default='n').lower().startswith('y'):
            return
    return orig_commit(ui, repo, *pats, **opts)

def uisetup(ui):
    extensions.wrapcommand(commands.table, 'commit', new_commit)
