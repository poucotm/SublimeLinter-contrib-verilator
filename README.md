SublimeLinter-contrib-verilator
================================

[![Package Control](https://packagecontrol.herokuapp.com/downloads/SublimeLinter-contrib-verilator.svg?style=flat-square)](https://packagecontrol.io/packages/SublimeLinter-contrib-verilator)
[![Build Status](https://travis-ci.org/SublimeLinter/SublimeLinter-contrib-verilator.svg?branch=master)](https://travis-ci.org/SublimeLinter/SublimeLinter-contrib-verilator)

This linter plugin for [SublimeLinter][docs] provides an interface to **Verilator**.
**Verilator** is a open source HDL simulator and can be used as a linter with --lint-only option.
For more information, you can check here, [https://www.veripool.org/wiki/verilator][linter_homepage]
**Verilator** is fast and easy to use to link with Sublime Text Editor on variable OS, before runnning commercial simulaton and synthesis tools.

### Prerequisite

- **SublimeLinter 3 installation** - Guide from [here][installation]
- **Verilator installation** - Guide from [here][linter-install]
- **Verilator settings** - SublimeLinter-contrib-verilator uses ```verilator_bin``` or ```verilator_bin.exe``` instead of ```verilator```. You have to add ```PATH``` environment for ```verilator_bin``` or ```verilator_bin.exe```
- **Modified version of Verilator** - For linting single file, it is modified to ignore `include files and other module files. You can get from [https://github.com/poucotm/verilator](https://github.com/poucotm/verilator). ```-Wno-IGNINC, -Wno-IGNMOD, -Wno-IGNDEF, -Wno-IGNUNUSED``` options are added. Installation is the same as original after getting by cloning or downloading.

### Screenshot

![Image](https://raw.githubusercontent.com/poucotm/Links/master/image/verilator.png)

### Settings

In order to set arguments of Verilator or control lint message, Use SublimeLinter's user settings like the following.

```js
      "verilator": {
          "@disable": false,
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
              "-Wno-IGNMOD",
              "-Wno-IGNDEF",
              "-Wno-IGNUNUSED",
              "-Wno-WIDTH",
              "-Wno-CASEX",
              "-Wno-STMTDLY"
          ],
          "excludes": [],
          "extension": [
              ".v"
          ],
          "ignore_match": [
              "Unsupported:",
              "\\[IGNDEF\\]"
          ]
      }
```

### Troubleshooting

Turn on SublimeLinter's ```Debug Mode``` and Open the console of Sublime Text. You can check the communication status from SublimeLinter to Verilator.
You can also add more ```ignore_match``` message by using them.

```
SublimeLinter: verilator: shift_reg.v ['D:\\Program\\verilator-3.902\\verilator_bin.exe', '--lint-only', ...
SublimeLinter: verilator output:
%Warning-LITENDIAN: c:/users/shift_reg.v:14: Little bit endian vector: MSB < LSB of bit range: 0:7
%Warning-LITENDIAN: Use "/* verilator lint_off LITENDIAN */" and lint_on around source to disable this message.
%Error: Exiting due to 1 warning(s)
```

### Credits

Thanks to SublimeLinter Team and Veripool Organization.

### issues

When you have an issue, tell me through [https://github.com/poucotm/SublimeLinter-contrib-verilator/issues](https://github.com/poucotm/SublimeLinter-contrib-verilator/issues), or send me an e-mail poucotm@gmail.com, yongchan.jeon@samsung.com

[docs]: http://sublimelinter.readthedocs.org
[linter_homepage]: https://www.veripool.org/wiki/verilator
[installation]: http://sublimelinter.readthedocs.org/en/latest/installation.html
[linter-install]: https://www.veripool.org/projects/verilator/wiki/Installing