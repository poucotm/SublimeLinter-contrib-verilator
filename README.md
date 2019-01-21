# SublimeLinter-contrib-verilator

[![Package Control](https://packagecontrol.herokuapp.com/downloads/SublimeLinter-contrib-verilator.svg?style=round-square)](https://packagecontrol.io/packages/SublimeLinter-contrib-verilator) [![Build Status](https://api.travis-ci.org/poucotm/SublimeLinter-contrib-verilator.svg?branch=master)](https://travis-ci.org/poucotm/SublimeLinter-contrib-verilator)
[![PayPal](https://img.shields.io/badge/paypal-donate-blue.svg)][PM]

This linter plugin for [SublimeLinter][docs] provides an interface to __Verilator__.
__Verilator__ is a open source HDL simulator and can be used as a linter with --lint-only option.
For more information, you can see here, [https://www.veripool.org/wiki/verilator][linter_homepage]
**Verilator** is fast and easy to use to link with Sublime Text Editor on variable OS before runnning commercial simulaton and synthesis tools.

### Prerequisite

 * __SublimeLinter 4 installation__ - Guide from [here][installation]
 * __Verilator installation__ - Guide from [here][linter-install]
 * __Modified version of Verilator__ - Get source from [https://github.com/poucotm/verilator](https://github.com/poucotm/verilator) (update for verilator-4.008, v1.2.2) 
   or download [compiled version for Windows (v1.2.2)](https://raw.githubusercontent.com/poucotm/Links/master/tools/verilator/verilator-v1.2.2.zip) with 2 MinGW libraries.
 * __Verilator PATH settings__ - SublimeLinter-contrib-verilator uses __*verilator_bin*__ or __*verilator_bin.exe*__ instead of __*verilator*__. You have to add __PATH__ environment variable for __*verilator_bin*__ or __*verilator_bin.exe*__

#### Verilator Original vs. Modified Version

__Verilator__ originally simulates all entities having all __*include*__ and __*module*__ files. If you miss even a file, it will generate an error message and stop simulation or linting. It is not good to be used with a editor. People don't open all files to edit or it is tired to pass the file list to Verilator every time. In order to lint single file based, the original codes are modified. It can ignore __*include*__ and externally defined module's instance and its port connection even if there's a real error in port connection. You can select one of them. If you want to use original version, you may have to put all files in the same directory. Because, __Verilator__ basically searches missed files in the same directory.

#### Options for Modified Version

 * -Wno-IGNINC : Ignores __*include*__ files
 * -Wno-IGNDEF : Ignores __*define*__ which may have been defined outside

### Screenshot

![Image](https://raw.githubusercontent.com/poucotm/Links/master/image/SublimeLinter-Contrib-Verilator/vl-cap.gif)

### Settings

In order to set arguments of Verilator or control lint message, Use SublimeLinter's user settings like the following.

```js
{
    "no_column_highlights_line": true,
    "linters":
    {
        "verilator": {
            "lint_mode": "load_save",
            "styles" : [
                {
                    "types": ["warning"],
                    "mark_style": "squiggly_underline",
                    "icon": "Packages/SublimeLinter/gutter-themes/Default/cog.png"
                },
                {
                    "types": ["error"],
                    "mark_style": "fill",
                    "icon": "Packages/SublimeLinter/gutter-themes/Default/cog.png"
                }
            ],
            "args": [
                "--error-limit",
                "500",
                "--default-language",
                "1800-2012",
                "--bbox-sys",
                "--bbox-unsup",
                "-Wall",
                "-Wno-DECLFILENAME",
                "-Wno-IGNINC",
                "-Wno-IGNDEF",
                "-Wno-WIDTH",
                "-Wno-STMTDLY",
                "-Wno-PINCONNECTEMPTY",
                "-Wno-INPUTPINEMPTY",
                "-Wno-OUTPUTPINEMPTY"
            ],
            "filter_errors": [
                "Unsupported:",
                "\\[IGNDEF\\]"
            ],
            // additional option to filter file type
            "extension": [
                ".v"
            ],
            // additional option for better highlighting near
            "message_near_map": [
                ["Case values", "case"],
                ["Suggest casez", "casex"]
            ]
        }
    }
}
```

### Key Map

__'F1'__ : SublimeLinter Show All Errors  
__'Shift+F1'__ : SublimeLinter Lint This View

### Troubleshooting

Turn on SublimeLinter's __*Debug Mode*__ and Open the console of Sublime Text. You can check the communication status from SublimeLinter to Verilator.
You can also add your own __*filter_errors*__ messages by using them.

```
SublimeLinter: verilator: shift_reg.v ['D:\\Program\\verilator-3.902\\verilator_bin.exe', '--lint-only', ...
SublimeLinter: verilator output:
%Warning-LITENDIAN: c:/users/shift_reg.v:14: Little bit endian vector: MSB < LSB of bit range: 0:7
%Warning-LITENDIAN: Use "/* verilator lint_off LITENDIAN */" and lint_on around source to disable this message.
%Error: Exiting due to 1 warning(s)
```

### Donate

[![Doate Image](https://raw.githubusercontent.com/poucotm/Links/master/image/PayPal/donate-paypal.png)][PM]  
Thank you for donating. It is helpful to continue to improve the plug-in.

### Credits

Thanks to [__SublimeLinter Team__](https://github.com/SublimeLinter/SublimeLinter3) and [__Veripool Organization__](https://www.veripool.org).

### Issues

When you have an issue, tell me through [https://github.com/poucotm/SublimeLinter-contrib-verilator/issues](https://github.com/poucotm/SublimeLinter-contrib-verilator/issues), or send me an e-mail poucotm@gmail.com

[docs]: http://sublimelinter.readthedocs.org
[linter_homepage]: https://www.veripool.org/wiki/verilator
[installation]: https://packagecontrol.io/packages/SublimeLinter
[download]: https://github.com/SublimeLinter/SublimeLinter/releases/tag/v3.10.10
[linter-install]: https://www.veripool.org/projects/verilator/wiki/Installing
[PP]:https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=89YVNDSC7DZHQ "PayPal"
[PM]:https://www.paypal.me/poucotm/2.5 "PayPal"
