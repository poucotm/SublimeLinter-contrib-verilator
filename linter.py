# -*- coding: utf8 -*-

## -----------------------------------------------------------------------------
## Author : yongchan jeon (Kris) poucotm@gmail.com
## File   : SublimeLinter-contrib-verilator/linter.py
## Create : 2017-05-22 19:41:37
## Editor : sublime text3, tab size (3)
## -----------------------------------------------------------------------------

"""This module exports the Verilator plugin class."""

from SublimeLinter.lint import Linter, util
import sublime
import SublimeLinter.lint.util
import os
import tempfile
import getpass
import re

class Verilator(Linter):
    """Provides an interface to verilator."""

    syntax = ('verilog', 'systemverilog')
    cmd = 'verilator_bin --lint-only --bbox-unsup --bbox-sys'
    tempfile_suffix = 'verilog'
    multiline = False
    error_stream = util.STREAM_BOTH

    if sublime.platform() == 'windows':
        filepath = r'[^:]+:[^:]+'
    else:
        filepath = r'[^:]+'

    regex = (
        r'((?P<warning>%Warning.*: )|(?P<error>%Error: |))'
        r'(?P<file>{0}):(?P<line>\d+): '
        r'(?P<message>.*)'
        .format(filepath)
    )

    tempdir = os.path.join(tempfile.gettempdir(), 'SublimeLinter3-' + getpass.getuser())

    def tmpfile(self, cmd, code, suffix=''):
        """override tmpfile for windows"""

        if not self.filename:
            file = UNSAVED_FILENAME
        else:
            file = os.path.basename(self.filename)
        if suffix:
            file = os.path.splitext(self.filename)[0] + suffix

        path = os.path.join(self.tempdir, file)

        try:
            with open(path, mode='wb') as f:
                if isinstance(self.code, str):
                    code = self.code.encode('utf-8')
                f.write(code)
                f.flush()

            cmd = list(self.cmd)

            if sublime.platform() == 'windows':
                vpath = re.sub(re.compile(r'\\'), '/', path)
            else:
                vpath = path

            if '@' in self.cmd:
                cmd[cmd.index('@')] = vpath
            else:
                cmd.append(vpath)

            return util.communicate(cmd, output_stream=self.error_stream, env=self.env)
        finally:
            os.remove(path)
