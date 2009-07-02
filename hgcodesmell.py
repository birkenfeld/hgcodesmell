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

BAD_STUFF = [
    (re.compile(r'^\+\s*print\b'), 'print statement'),
    (re.compile(r'^\+\s*1/0'), 'zero division error'),
    (re.compile(r'\bpdb\.set_trace\(\)'), 'set_trace'),
    (re.compile(r':(w|wq|q|x)$'), 'stupid vim command'),
]

def new_commit(orig_commit, ui, repo, *pats, **opts):
    smelly = 0
    diff = patch.diff(repo, *cmdutil.revpair(repo, None))
    for chunk in diff:
        chunklines = chunk.splitlines()
        indexline = 0
        hunkstart = 0
        for i, line in enumerate(chunklines):
            if line.startswith('diff'):
                indexline = i
            elif line.startswith('@@'):
                hunkstart = i
            elif line.startswith('+'):
                for rex, reason in BAD_STUFF:
                    if rex.search(line):
                        ui.warn('Smelly change (%s):\n' % reason)
                        colorwrap(ui.write,
                                  '\n'.join(chunklines[indexline:indexline+3]
                                            + chunklines[hunkstart:i+4] + ['']))
                        smelly += 1
                        break
                else:
                    continue
                break
    if smelly:
        if not ui.prompt('Found %d smelly change%s. Continue (y/N)?' %
                         (smelly, smelly != 1 and 's' or ''),
                         default='n').lower().startswith('y'):
            return
    return orig_commit(ui, repo, *pats, **opts)

def uisetup(ui):
    extensions.wrapcommand(commands.table, 'commit', new_commit)
