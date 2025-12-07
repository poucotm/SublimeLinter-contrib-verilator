# SublimeLinter-contrib-verilator

[![Package Control](https://img.shields.io/packagecontrol/dt/SublimeLinter-contrib-verilator?logo=github&color=FF1919)][PKG]
[![PayPal](https://img.shields.io/badge/paypal-donate-blue.svg)][PM]

This linter plugin for [SublimeLinter][docs] provides an interface to __Verilator__.
__Verilator__ is a open source HDL simulator and can be used as a linter with --lint-only option.
For more information, you can see here, [https://www.veripool.org/wiki/verilator][linter_homepage]
**Verilator** is fast and easy to use to link with Sublime Text Editor on variable OS before runnning commercial simulaton and synthesis tools.

### Prerequisite

 * __SublimeLinter 4 installation__ - Guide from [here][installation]
 * __Verilator installation__
	
	Original Guide from [here][linter-install]  
	Use MSYS for Windows (Download [https://www.msys2.org](https://www.msys2.org/))

```bash
	pacman -Syu
	pacman -S mingw-w64-x86_64-verilator
```

 * __Verilator PATH settings__ - SublimeLinter-contrib-verilator uses __*verilator_bin*__ or __*verilator_bin.exe*__ instead of __*verilator*__. You have to add __PATH__ environment variable for __*verilator_bin*__ or __*verilator_bin.exe*__

### Lint based on multiple files

Two options are added to support linting based on multiple files. If you set full paths, the original version of verilator can be used.

 * "use_multiple_source": true
 * "search_project_path": true

an example of settings in a sublime-project file:
```json
    "sources":
    [
        "D:\\project\\srcs",
        "D:\\project\\working"
    ]
```

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
                "1800-2017",
                "-Wall",
                "-Wno-WIDTHTRUNC",
                "-Wno-WIDTHEXPAND",
                "-Wno-INITIALDLY",
                "-Wno-UNDRIVEN",
                "-Wno-UNOPTFLAT",
                "-Wno-UNUSEDPARAM",
                "-Wno-SIDEEFFECT",
                "-Wno-PINCONNECTEMPTY",
                "-Wno-BLKSEQ",
            ],

            "verilator_version"  : 5,
            "use_multiple_source": false,
            "search_project_path": false,

            // to lint based on multiple files (searching external sources - the same directory or project path)
            //   "use_multiple_source": true,
            //   "search_project_path": true,
            //  example) example.sublime-project
            //       "sources": [ "D:\\project\\srcs", "D:\\project\\working" ]

            // windows subsystem for linux (wsl verilator_bin)
            "use_wsl": false,

            // additional option to filter file type
            "extension": [
                ".v", ".sv"
            ],
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
[PKG]:https://packagecontrol.io/packages/SublimeLinter-contrib-verilator "SublimeLinter-contrib-verilator"
