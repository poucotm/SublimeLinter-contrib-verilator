# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : linter.py
# Create : 2018-12-31 00:34:43
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

"""This module exports the Verilator plugin class."""

from SublimeLinter.lint import Linter
from SublimeLinter.lint.linter import make_temp_file, get_view_context, LintMatch
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
        'selector': 'source.verilog, source.systemverilog'
    }

    if sublime.platform() == 'windows':
        filepath = r'[^:]+:[^:]+'
    else:
        filepath = r'[^:]+'

    regex = (
        r'((?P<warning>%Warning)|(?P<error>%Error))'
        r'(-(?P<code>.*?)|(.*?)): '
        r'(?P<file>{0}):(?P<line>\d+):((?P<col>\d+):|) '
        r'(?P<message>.*)'
        .format(filepath)
    )

    """ SublimeLinter 4 """
    def lint(self, code, view_has_changed):
        """Override lint() to check file extension"""

        vls = self.settings
        ext_setting = vls.get('extension', [])
        if len(ext_setting) > 0:
            ext = os.path.splitext(self.filename)[1].lower()
            if ext not in ext_setting:
                return []

        return super(Verilator, self).lint(code, view_has_changed)

    def parse_output(self, proc, virtual_view):
        """Override parse_output()"""

        return self.parse_output_via_regex(proc, virtual_view)

    def split_match(self, match):
        """Override split_match()"""

        error = LintMatch(match.groupdict())
        error["match"] = match

        # Normalize line and col if necessary
        try:
            line = error['line']
        except KeyError:
            pass
        else:
            if line:
                error['line'] = int(line) - self.line_col_base[0]
            else:  # Exchange the empty string with `None`
                error['line'] = None

        try:
            col = error['col']
        except KeyError:
            pass
        else:
            if col:
                if col.isdigit():
                    col = int(col) - self.line_col_base[1]
                else:
                    col = len(col)
                error['col'] = col
            else:  # Exchange the empty string with `None`
                error['col'] = None

        # get near
        mnear = re.search(r': (?P<near>[\w]+)$', error["message"])
        if mnear is not None:
            error["near"] = mnear.group("near")
        else:
            vls = self.settings
            near_map = vls.get('message_near_map', [])
            for e in near_map:
                if re.match(e[0], error["message"]):
                    error["near"] = e[1]

        return error

    def tmpfile(self, cmd, code, suffix=None):
        """Override tmpfile()"""

        if suffix is None:
            suffix = self.get_tempfile_suffix()

        code = self.mask_code(code)
        twrp = self.parse_verilog(code)

        with make_temp_file(suffix, code) as file:
            with make_temp_file(suffix, twrp) as wrap:
                ctx = get_view_context(self.view)
                ctx['file_on_disk'] = self.filename
                if sublime.platform() == 'windows':
                    file.name = re.sub(re.compile(r'\\'), '/', file.name)
                    wrap.name = re.sub(re.compile(r'\\'), '/', wrap.name)
                ctx['temp_file'] = file.name
                cmd.append(file.name)
                cmd.append(wrap.name)
                out = str(self._communicate(cmd))
                out = re.sub(wrap.name, '', out)
                return out

    def mask_code(self, code):
        txts = re.compile(SYN_PAT, re.DOTALL).findall(code)
        for txt in txts:
            nlines = len(txt.splitlines())
            repstr = '\n' * nlines
            code = code.replace(txt, repstr)
        oobj = re.compile(r'\s+output\s+(?P<type>(reg|wire|)).*?[,;\)]', re.DOTALL)
        for o in oobj.finditer(code):
            if not o.group('type'):
                w = re.sub('output', 'output wire', o.group())
                code = code.replace(o.group(), w)
        return code

    def parse_verilog(self, code):
        code = re.sub(re.compile(r'/\*.*?\*/', re.DOTALL), '', code)
        code = re.sub(re.compile(r'\(\*.*?\*\)', re.DOTALL), '', code)
        code = re.sub(re.compile(r'//.*?\n'), '', code)
        code = re.sub(re.compile(r';'), '; ', code)

        mobj = re.compile(r'(?<!\S)module\s+(?P<mname>[\w]+).*?;(?P<txts>.*?)(?<!\S)endmodule(?!\S)', re.DOTALL)
        lnks = r'[\w\s\.\,\(\)\[\]\{\}\"\'\`\:\+\-\*\/\$\!\~\%\^\&\|]'
        insp = r'(?<!\S)(?P<mname>[\w]+)([\s]*\#[\s]*\((?P<params>' + lnks + r'*?)\)|\s)[\s]*[\w]+[\s]*\((?P<ports>' + lnks + r'*?)\)[\s]*;'
        iobj = re.compile(insp, re.DOTALL)
        pobj = re.compile(r'[\s]*?\.[\s]*?(?P<dotp>[\w]+)[\s]*|[\s]*(?P<ndot>.+)', re.DOTALL)

        # modules
        defmods = set([])
        insmods = {}
        for m in mobj.finditer(code):
            defmods.add(m.group('mname'))
            # instances
            for i in iobj.finditer(m.group('txts')):
                if not i.group('mname') in defmods:
                    if not i.group('mname') in insmods:
                        insmods[i.group('mname')] = {}
                        insmods[i.group('mname')]['param'] = []
                        insmods[i.group('mname')]['ports'] = []
                    # params
                    parmnumb = 0
                    if i.group('params'):
                        params = re.sub(re.compile(r'\(.*?\)\s*(?=,)', re.DOTALL), '', i.group('params'))
                        params = re.sub(re.compile(r'\(.*?\)\s*(?=\Z)', re.DOTALL), '', params)
                        for p in params.split(','):
                            s = pobj.match(p)
                            if s:
                                dotp = s.group('dotp')
                                ndot = s.group('ndot')
                                if dotp and dotp not in insmods[i.group('mname')]['param']:
                                    insmods[i.group('mname')]['param'].append(dotp)
                                elif ndot:
                                    parmnumb += 1
                                    ndot = "prm_CtfVFslZ_{}".format(parmnumb)
                                    if ndot not in insmods[i.group('mname')]['param']:
                                        insmods[i.group('mname')]['param'].append(ndot)
                    # ports
                    pinnumb = 0
                    if i.group('ports'):
                        ports = re.sub(re.compile(r'\(.*?\)\s*(?=,)', re.DOTALL), '', i.group('ports'))
                        ports = re.sub(re.compile(r'\(.*?\)\s*(?=\Z)', re.DOTALL), '', ports)
                        for p in ports.split(','):
                            s = pobj.match(p)
                            if s:
                                dotp = s.group('dotp')
                                ndot = s.group('ndot')
                                if dotp and dotp not in insmods[i.group('mname')]['ports']:
                                    insmods[i.group('mname')]['ports'].append(dotp)
                                elif ndot:
                                    pinnumb += 1
                                    ndot = "pin_CtfVFslZ_{}".format(pinnumb)
                                    if ndot not in insmods[i.group('mname')]['ports']:
                                        insmods[i.group('mname')]['ports'].append(ndot)
        anotherv = ''
        # define modules for instances
        for modn, link in insmods.items():
            for i, k in enumerate(link['param']):
                link['param'][i] = 'parameter ' + link['param'][i] + ' = 0'
            for i, k in enumerate(link['ports']):
                link['ports'][i] = 'input [8191:0] ' + link['ports'][i]
            anotherv += 'module {0} #({1})({2}); endmodule\n'.format(modn, ','.join(link['param']), ','.join(link['ports']))
        # define wrapper module for multiple modules
        if len(defmods) > 1:
            anotherv += 'module YGmpvTABcdCDefExIVVx;\n'
            for m in defmods:
                anotherv += m + ' i_' + m + '();\n'
            anotherv += 'endmodule'

        return anotherv
