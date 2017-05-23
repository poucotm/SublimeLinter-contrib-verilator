# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : SublimeLinter-contrib-verilator/linter.py
# Create : 2017-05-22 19:41:37
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

"""This module exports the Verilator plugin class."""

from SublimeLinter.lint import Linter, util
import sublime
import os
import tempfile
import getpass
import re


class Verilator(Linter):
    """Provides an interface to verilator."""

    syntax = ('verilog', 'systemverilog')
    cmd = 'verilator_bin --lint-only'
    tempfile_suffix = 'verilog'
    multiline = False
    error_stream = util.STREAM_BOTH

    if sublime.platform() == 'windows':
        filepath = r'[^:]+:[^:]+'
    else:
        filepath = r'[^:]+'

    regex = (
        r'((?P<warning>%Warning.*: )|(?P<error>%Error.*: |))'
        r'(?P<file>{0}):(?P<line>\d+): '
        r'(?P<message>.*)'
        .format(filepath)
    )

    tempdir = os.path.join(tempfile.gettempdir(), 'SublimeLinter3-' + getpass.getuser())

    def lint(self, hit_time):
        """override lint() to check file extension"""

        # check file extension
        vl_settings = self.get_view_settings(inline=False)
        ext_setting = vl_settings.get('extension', [])
        if len(ext_setting) > 0:
            ext = os.path.splitext(self.filename)[1].lower()
            if ext not in ext_setting:
                return

        # call parent's
        super(Verilator, self).lint(hit_time)
        return

    def error(self, line, col, message, error_type):
        """override error() for '<', '>'"""

        self.highlight.line(line, error_type)

        # replace <, > as &lt; &gt;
        message = message.replace('<', '&lt;').replace('>', '&gt;')

        # Strip trailing CR, space and period
        message = ((col or 0), str(message).rstrip('\r .'))

        if line in self.errors:
            self.errors[line].append(message)
        else:
            self.errors[line] = [message]

    def tmpfile(self, cmd, code, suffix=''):
        """override tmpfile() for windows"""

        if not self.filename:
            file = 'untitled'
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

            # to apply args
            cmd = self.get_cmd()
            cmd = list(cmd)

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
