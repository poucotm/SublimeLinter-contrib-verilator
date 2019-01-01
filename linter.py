# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : linter.py
# Create : 2018-12-31 00:34:43
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

"""This module exports the Verilator plugin class."""

from SublimeLinter.lint import Linter
from SublimeLinter.lint.linter import make_temp_file, get_view_context, MATCH_DICT, LintMatch
import sublime
import os
import re


# translate off/on
SYN_PAT = \
 r"\/\*\s*synopsys\s+translate_off\s*\*\/" +\
 r".*?\/\*\s*synopsys\s+translate_on\s*\*\/[\n\r]|" +\
 r"\/\*\s*synthesis\s+translate_off\s*\*\/" +\
 r".*?\/\*\s*synthesis\s+translate_on\s*\*\/[\n\r]"


class Verilator(Linter):
    """Provides an interface to verilator."""

    cmd = ('verilator_bin', '--lint-only')
    tempfile_suffix = 'verilog'
    multiline = False
    defaults = {
        'selector' : 'source.verilog, source.systemverilog'
    }

    if sublime.platform() == 'windows':
        filepath = r'[^:]+:[^:]+'
    else:
        filepath = r'[^:]+'

    regex = (
        r'((?P<warning>%Warning)|(?P<error>%Error))'
        r'(-(?P<code>.*?)|(.*?)): '
        r'(?P<file>{0}):(?P<line>\d+): '
        r'(?P<message>.*)'
        .format(filepath)
    )

    """ SublimeLinter 4 """
    def lint(self, code, view_has_changed):
        """Override lint() for to check file extension"""

        vls = self.get_view_settings()
        ext_setting = vls.get('extension', [])
        if len(ext_setting) > 0:
            ext = os.path.splitext(self.filename)[1].lower()
            if ext not in ext_setting:
                return []

        return super(Verilator, self).lint(code, view_has_changed)

    def parse_output(self, proc, virtual_view):
        """Override parse_output()"""

        output = proc.combined_output
        return self.parse_output_via_regex(output, virtual_view)

    def split_match(self, match):
        """Override split_match()"""

        match_dict = MATCH_DICT.copy()

        match_dict.update({
            k: v
            for k, v in match.groupdict().items()
            if k in match_dict
        })
        match_dict["match"] = match

        line = match_dict["line"]
        if line:
            match_dict["line"] = int(line) - self.line_col_base[0]
        else:
            match_dict["line"] = None

        col = match_dict["col"]
        if col:
            if col.isdigit():
                col = int(col) - self.line_col_base[1]
            else:
                col = len(col)
            match_dict["col"] = col
        else:
            match_dict["col"] = None

        # get near
        mnear = re.search(r': (?P<near>[\w]+)$', match_dict["message"])
        if mnear is not None:
            match_dict["near"] = mnear.group("near")
        else:
            vls = self.get_view_settings()
            near_map = vls.get('message_near_map', [])
            for e in near_map:
                if re.match(e[0], match_dict["message"]):
                    match_dict["near"] = e[1]

        return LintMatch(**match_dict)

    def tmpfile(self, cmd, code, suffix=None):
        """Override tmpfile()"""

        if suffix is None:
            suffix = self.get_tempfile_suffix()

        code = self.mask_code(code)

        with make_temp_file(suffix, code) as file:
            ctx = get_view_context(self.view)
            ctx['file_on_disk'] = self.filename
            if sublime.platform() == 'windows':
                file.name = re.sub(re.compile(r'\\'), '/', file.name)
            ctx['temp_file'] = file.name
            cmd = self.finalize_cmd(
                cmd, ctx, at_value=file.name, auto_append=True)
            return self._communicate(cmd)

    def mask_code(self, code):
        txts = re.compile(SYN_PAT, re.DOTALL).findall(code)
        for txt in txts:
            nlines = len(txt.splitlines())
            repstr = '\n' * nlines
            code = code.replace(txt, repstr)
        return code
