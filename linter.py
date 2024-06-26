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

# keywords
KEYWORDS = ['alias', 'always', 'always_comb', 'always_ff', 'always_latch', 'and', 'assert', 'assign', 'assume',
            'automatic', 'before', 'begin', 'bind', 'bins', 'binsof', 'bit', 'break', 'buf', 'bufif0', 'bufif1',
            'byte', 'case', 'casex', 'casez', 'cell', 'chandle', 'class', 'clocking', 'cmos', 'config', 'const',
            'constraint', 'context', 'continue', 'cover', 'covergroup', 'coverpoint', 'cross', 'deassign', 'default',
            'defparam', 'design', 'disable', 'dist', 'do', 'edge', 'else', 'end', 'endcase', 'endclass', 'endclocking',
            'endconfig', 'endfunction', 'endgenerate', 'endgroup', 'endinterface', 'endmodule', 'endpackage',
            'endprimitive', 'endprogram', 'endproperty', 'endspecify', 'endsequence', 'endtable', 'endtask', 'enum',
            'event', 'expect', 'export', 'extends', 'extern', 'final', 'first_match', 'for', 'force', 'foreach',
            'forever', 'fork', 'forkjoin', 'function', 'generate', 'genvar', 'highz0', 'highz1', 'if', 'iff', 'ifnone',
            'ignore_bins', 'illegal_bins', 'import', 'incdir', 'include', 'initial', 'inout', 'input', 'inside',
            'instance', 'int', 'integer', 'interface', 'intersect', 'join', 'join_any', 'join_none', 'large', 'liblist',
            'library', 'local', 'localparam', 'logic', 'longint', 'macromodule', 'matches', 'medium', 'modport',
            'module', 'nand', 'negedge', 'new', 'nmos', 'nor', 'noshowcancelled', 'not', 'notif0', 'notif1', 'null', 'or',
            'output', 'package', 'packed', 'parameter', 'pmos', 'posedge', 'primitive', 'priority', 'program', 'property',
            'protected', 'pull0', 'pull1', 'pulldown', 'pullup', 'pulsestyle_onevent', 'pulsestyle_ondetect', 'pure', 'rand',
            'randc', 'randcase', 'randsequence', 'rcmos', 'real', 'realtime', 'ref', 'reg', 'release', 'repeat', 'return',
            'rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1', 'scalared', 'sequence', 'shortint', 'shortreal', 'showcancelled',
            'signed', 'small', 'solve', 'specify', 'specparam', 'static', 'string', 'strong0', 'strong1', 'struct', 'super',
            'supply0', 'supply1', 'table', 'tagged', 'task', 'this', 'throughout', 'time', 'timeprecision', 'timeunit',
            'tran', 'tranif0', 'tranif1', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'type', 'typedef', 'union',
            'unique', 'unsigned', 'use', 'uwire', 'var', 'vectored', 'virtual', 'void', 'wait', 'wait_order', 'wand', 'weak0',
            'weak1', 'while', 'wildcard', 'wire', 'with', 'within', 'wor', 'xnor', 'x']


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

    svobj = re.compile(r'[^\w](uvm_.*?|\$display|\$monitor|initial|final|real|fork|join|force|release|class|assert|bind|bins|chandle|clocking|cover|covergroup|import|export|constraint|modport)[^\w]')

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

        wslopt = self.settings.get('use_wsl', False) if sublime.platform() == 'windows' else False
        if wslopt:
            cmd.insert(0, 'wsl')
            cmd[1] = 'verilator_bin'
            regexp = (
                r'((?P<warning>%Warning)|(?P<error>%Error))'
                r'(-(?P<code>.*?)|(.*?)): '
                r'(?P<file>{0}):(?P<line>\d+):((?P<col>\d+):|) '
                r'(?P<message>.*)'
                .format(r'[^:]+')
            )
            self.regex = re.compile(regexp)
        cmd.append('-Wno-DECLFILENAME')

        extopt = self.settings.get('use_multiple_source', False)
        prjopt = self.settings.get('search_project_path', False)
        if extopt:
            if prjopt:
                prjfile = self.view.window().project_file_name()
                if isinstance(prjfile, str) and prjfile != "":
                    prjdat = self.view.window().project_data()
                    prjsrc = prjdat.get('sources')
                    for path in prjsrc:
                        if sublime.platform() == 'windows':
                            if wslopt:
                                path = re.sub(r'(^[a-zA-Z])(:)(.*$)',lambda m : ''.join(['/mnt/',m.group(1).lower(),m.group(3)]),path)
                            path = re.sub(re.compile(r'\\'), '/', path)
                        path = '-I' + path
                        cmd.append(path)

            with make_temp_file(suffix, code) as file:
                ctx = get_view_context(self.view)
                ctx['file_on_disk'] = self.filename
                if sublime.platform() == 'windows':
                    if wslopt:
                        orig_file = file.name
                        file.name = re.sub(r'(^[a-zA-Z])(:)(.*$)',lambda m : ''.join(['/mnt/',m.group(1).lower(),m.group(3)]),file.name)
                    file.name = re.sub(re.compile(r'\\'), '/', file.name)
                ctx['temp_file'] = file.name
                cmd.append(file.name)
                out = self.pick_message(str(self._communicate(cmd)), file.name)
                if wslopt:
                    file.name = orig_file
                return out
        else:
            code = self.mask_code(code)
            twrp = self.parse_verilog(code)

            with make_temp_file(suffix, code) as file:
                with make_temp_file(suffix, twrp) as wrap:
                    ctx = get_view_context(self.view)
                    ctx['file_on_disk'] = self.filename
                    if sublime.platform() == 'windows':
                        if wslopt:
                            orig_file = file.name
                            orig_wrap = wrap.name
                            file.name = re.sub(r'(^[a-zA-Z])(:)(.*$)',lambda m : ''.join(['/mnt/',m.group(1).lower(),m.group(3)]),file.name)
                            wrap.name = re.sub(r'(^[a-zA-Z])(:)(.*$)',lambda m : ''.join(['/mnt/',m.group(1).lower(),m.group(3)]),wrap.name)
                        file.name = re.sub(re.compile(r'\\'), '/', file.name)
                        wrap.name = re.sub(re.compile(r'\\'), '/', wrap.name)
                    ctx['temp_file'] = file.name
                    cmd.append(file.name)
                    cmd.append(wrap.name)
                    out = self.pick_message(str(self._communicate(cmd)), file.name)
                    if wslopt:
                        file.name = orig_file
                        wrap.name = orig_wrap
                    return out

    def pick_message(self, msg, name):
        out = ''
        for line in msg.splitlines():
            if name in line:
                out += line + '\n'
        return out

    def mask_code(self, code):

        def remove_comments(pattern, text):
            txts = re.compile(pattern, re.DOTALL).findall(text)
            for txt in txts:
                if isinstance(txt, str):
                    blnk = '\n' * (txt.count('\n'))
                    text = text.replace(txt, blnk)
                elif isinstance(txt, tuple) and txt[1]:
                    blnk = '\n' * (txt[1].count('\n'))
                    text = text.replace(txt[1], blnk)
            return text

        code = remove_comments(SYN_PAT, code)
        code = re.sub(re.compile(r'//.*?$', re.MULTILINE), '', code)
        code = remove_comments(r'/\*.*?\*/', code)
        code = remove_comments(r'(@\s*?\(\s*?\*\s*?\))|(\(\*.*?\*\))', code)

        # don't check lib, testbench
        nots = self.svobj.search(code)
        if nots:
            code = ''

        oobj = re.compile(r'(?<!\w)output\s+(?P<type>(reg|wire|)).*?(?=[,;\)])', re.DOTALL)
        for o in oobj.finditer(code):
            if not o.group('type'):
                w = re.sub(re.compile('^output'), 'output wire', o.group())
                code = code.replace(o.group(), w)
        return code

    def parse_verilog(self, code):
        mobj = re.compile(r'(?<!\S)module\s+(?P<mname>[\w]+).*?;(?P<txts>.*?)(?<!\S)endmodule(?!\S)', re.DOTALL)
        prml = r'[\w\s\.\,\(\)\[\]\{\}\"\'\`\:\+\-\*\/\$\!\~\%\^\&\|]'
        prtl = r'[\w\s\.\,\(\)\[\]\{\}\'\`\:\+\-\*\/\$\!\~\%\^\&\|]'
        insp = r'(?<!\S)(?P<mname>[\w]+)([\s]*\#[\s]*\((?P<params>' + prml + r'*?)\)|\s)[\s]*[\w]+[\s]*\((?P<ports>' + prtl + r'*?)\)[\s]*;'
        iobj = re.compile(insp, re.DOTALL)
        pobj = re.compile(r'[\s]*?\.[\s]*?(?P<dotp>[\w]+)[\s]*|[\s]*(?P<ndot>.+)', re.DOTALL)

        # modules
        defmods = set([])
        insmods = {}
        for m in mobj.finditer(code):
            defmods.add(m.group('mname'))
            # instances
            for i in iobj.finditer(m.group('txts')):
                if not i.group('mname') in defmods and not i.group('mname') in KEYWORDS:
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
