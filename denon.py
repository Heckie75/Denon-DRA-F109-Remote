#!/usr/bin/python3
#
# MIT License
#
# Copyright (c) 2017 heckie75
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#




class HelpException(Exception):

    def __init__(self, message):

        self.message = message




import serial.tools.list_ports
import sys
import time
import re

# Force serial port by setting the constant, e.g.
# PORT = "/dev/ttyUSB0"
PORT = None

__PARSE_IDX = "#"
__PARSE_VAL = "$"
__PARSE_MUL = "*"

__USAGE = "usage"
__DESCR = "descr"
__STATS = "statics"
__PARAMS = "params"
__PARSER = "parser"

__PARAM = -1

COMMANDS = {
    "on" : {
         __USAGE : "on",
         __DESCR : "Turns denon receiver on",
         __STATS : [ 1, 2, 0 ]
         },
     "off" : {
         __USAGE : "off",
         __DESCR : "Turns denon receiver off",
         __STATS : [ 2, 1, 0 ]
         },
     "fm" : {
         __USAGE : "fm",
         __DESCR : "Sets input source to FM radio",
         __STATS : [ 16, 0, 0 ]
         },
     "dab" : { # can't test
         __USAGE : "dab",
         __DESCR : "Sets input source to DAB radio",
         __STATS : [ 18, 0, 0 ]
         },
     "cd" : {
         __USAGE : "cd",
         __DESCR : "Sets input source to CD (digital-in for CD)",
         __STATS : [ 19, 0, 0 ]
         },
     "net" : {
         __USAGE : "net",
         __DESCR : "Sets input source to Network (digital-in NETWORK)",
         __STATS : [ 20, 0, 0 ]
         },
     "analog" : {
         __USAGE : "analog <1|2>",
         __DESCR : "Sets input source to Analog n, where n is 1 or 2",
         __STATS : [ __PARAM, 0, 0 ],
         __PARAMS : [{
             "1" : 21,
             "2" : 22
             }]
         },
     "optical" : {
         __USAGE : "optical",
         __DESCR : "Sets input source to Digital-In optical",
         __STATS : [ 23, 0, 0 ]
         },
     "mode" : {
         __USAGE : "mode",
         __DESCR : "Toggles stereo/mono mode",
         __STATS : [ 40, 0, 0 ]
         },
     "play" : { # can't test
         __USAGE : "play",
         __DESCR : "Starts playback",
         __STATS : [ 50, 0, 0 ]
         },
     "pause" : { # can't test
         __USAGE : "pause",
         __DESCR : "Pauses current playback",
         __STATS : [ 50, 0, 0 ]
         },
     "stop" : { # can't test
         __USAGE : "stop",
         __DESCR : "Stops current playback",
         __STATS : [ 51, 0, 0 ]
         },
     "vol" : {
         __USAGE : "vol <0-60>",
         __DESCR : "Sets volume to value whish is between 0 and 60",
         __STATS : [ 64, 0, __PARAM ],
         __PARAMS : [ range(60) ]
         },
     "mute" : {
         __USAGE : "mute <on|off>",
         __DESCR : "Mute on/off",
         __STATS : [ 65, 0, __PARAM ],
         __PARAMS : [{
             "on" : 1,
             "off" : 0
             }]
         },
     "sdb" : {
         __USAGE : "sdb <on|off>",
         __DESCR : "SDB sound option on/off",
         __STATS : [ 66, 0, 0, __PARAM ],
         __PARAMS : [{
             "on" : 0,
             "off" : 1
             }]
         },
     "bass" : {
         __USAGE : "bass <+|->",
         __DESCR : "Increases / decreases bass level",
         __STATS : [ 66, 0, 1, __PARAM ],
         __PARAMS : [{
             "+" : 0,
             "-" : 1
             }]
         },
     "treble" : {
         __USAGE : "treble <+|->",
         __DESCR : "Increases / decreases treble level",
         __STATS : [ 66, 0, 2, __PARAM ],
         __PARAMS : [{
             "+" : 0,
             "-" : 1
             }]
         },
     "balance" : {
         __USAGE : "balance <left|right>",
         __DESCR : "Sets balance one step more to left or right",
         __STATS : [ 66, 0, 3, __PARAM ],
         __PARAMS : [{
             "left" : 0,
             "right" : 1
             }]
         },
     "sdirect" : {
         __USAGE : "sdirect <on|off>",
         __DESCR : "Activates/deactivates s.direct input",
         __STATS : [ 66, 0, 4, __PARAM ],
         __PARAMS : [{
             "on" : 0,
             "off" : 1
             }]
         },
     "dimmer" : {
         __USAGE : "dimmer <high|normal|low|off>",
         __DESCR : "Sets brightness of display",
         __STATS : [ 67, 0, __PARAM ],
         __PARAMS : [{
             "high" : 0,
             "normal" : 1,
             "low" : 2,
             "off" : 3
             }]
         },
     "next" : { # can't test
         __USAGE : "next",
         __DESCR : "Jump to next title",
         __STATS : [ 68, 0, 0 ]
         },
     "previous" : { # can't test
         __USAGE : "previous",
         __DESCR : "Jump to previous title",
         __STATS : [ 69, 0, 0 ]
         },
     "forward" : { # can't test
         __USAGE : "forward",
         __DESCR : "Forwards in current title",
         __STATS : [ 70, 0, 0 ]
         },
     "rewind" : { # can't test
         __USAGE : "rewind",
         __DESCR : "Rewinds in current title",
         __STATS : [ 71, 0, 0 ]
         },
     "up" : {
         __USAGE : "up",
         __DESCR : "Moves in current menu up",
         __STATS : [ 72, 0, 0 ]
         },
     "down" : {
         __USAGE : "down",
         __DESCR : "Moves in current menu down",
         __STATS : [ 73, 0, 0 ]
         },
     "left" : {
         __USAGE : "left",
         __DESCR : "Moves in current menu to the left",
         __STATS : [ 74, 0, 0 ]
         },
     "right" : {
         __USAGE : "right",
         __DESCR : "Moves in current menu to the right",
         __STATS : [ 75, 0, 0 ]
         },
     "enter" : {
         __USAGE : "enter",
         __DESCR : "Commit current setting by pressing enter",
         __STATS : [ 76, 0, 0 ]
         },
     "search" : {
         __USAGE : "search",
         __DESCR : "Enter search menu",
         __STATS : [ 77, 0, 0 ]
         },
     "num" : {
         __USAGE : "num <0-9|+10>",
         __DESCR : "Sends numeric buttom 0-9 / '+10' to receiver",
         __STATS : [ __PARAM, 0, 0 ],
         __PARAMS : [{
             "1" : 79,
             "2" : 80,
             "3" : 81,
             "4" : 82,
             "5" : 83,
             "6" : 84,
             "7" : 85,
             "8" : 86,
             "9" : 87,
             "0" : 88,
             "+10" : 89
             }]
         },
     "clear" : {
         __USAGE : "clear",
         __DESCR : "Sends clear command",
         __STATS : [ 90, 0, 0 ]
         },
     "random" : { # can't test
         __USAGE : "random",
         __DESCR : "(does not seem to work)",
         __STATS : [ 92, 0, 0 ]
         },
     "repeat" : { # can't test
         __USAGE : "repeat",
         __DESCR : "Toggles repeat option for playback",
         __STATS : [ 93, 0, 0 ]
         },
     "info" : {
         __USAGE : "info",
         __DESCR : "Toggles display",
         __STATS : [ 94, 0, 0 ]
         },
     "cda" : {
         __USAGE : "cda",
         __DESCR : "Sets input source to CD and selects CD",
         __STATS : [ 95, 0, 0 ]
         },
     "usb" : {
         __USAGE : "usb",
         __DESCR : "Sets input source to CD and selects USB",
         __STATS : [ 96, 0, 0 ]
         },
     "online" : {
         __USAGE : "online",
         __DESCR : "Sets input source to Network "
            + "and selects online music",
         __STATS : [ 97, 0, 0 ]
         },
     "internet" : {
         __USAGE : "internet",
         __DESCR : "Sets input source to Network "
            + "and selects internet radio",
         __STATS : [ 98, 0, 0 ]
         },
     "server" : {
         __USAGE : "server",
         __DESCR : "Sets input source to Network and selects server",
         __STATS : [ 98, 0, 0 ]
         },
     "ipod" : {
         __USAGE : "ipod",
         __DESCR : "Sets input source to Network and selects iPod",
         __STATS : [ 98, 0, 0 ]
         },
     "preset" : {
         __USAGE : "preset <+|->",
         __DESCR : "Zaps to previous / next preset",
         __STATS : [ 104, 48, __PARAM ],
         __PARAMS : [{
             "+" : 0,
             "-" : 1
             }]
         },
     "sleep" : {
         __USAGE : "sleep <0-255>",
         __DESCR : "Activates sleep mode with time in minutes",
         __STATS : [ 107, 0, __PARAM ],
         __PARAMS : [ range(256) ]
         },
     "standby" : {
         __USAGE : "standby <on|off>",
         __DESCR : "Sets auto-standby on/off",
         __STATS : [ 131, 0, __PARAM ],
         __PARAMS : [{
             "off" : 0,
             "on" : 1
             }]
         },
     "set-alarm" : {
         __USAGE : "set-alarm <once|everyday> <hh:mm> <hh:mm> "
            + "<analog1|analog2|optical|net|netusb|cd|cdusb|preset>"
            + "[<preset no.>]",
         __DESCR : "Configures alarm clock, e.g. set-alarm once "
            + "21:17 23:45 preset24",
         __STATS : [ __PARAM, 0, 0, __PARAM, __PARAM, 0, __PARAM, __PARAM, __PARAM ],
         __PARSER : [None,
                     [__PARSE_VAL, __PARSE_VAL],
                     [__PARSE_VAL, __PARSE_VAL],
                     [__PARSE_IDX, __PARSE_IDX, __PARSE_IDX,
                      __PARSE_IDX, __PARSE_IDX,
                      __PARSE_IDX, __PARSE_IDX, __PARSE_IDX,
                      __PARSE_VAL]],
         __PARAMS : [{
                "once" : 136,
                "everyday" : 137,
             },
             r"([0-2]?[0-9]):([0-5][0-9])",
             r"([0-2]?[0-9]):([0-5][0-9])",
             r"(preset)?(analog1)?(analog2)?"
             + "(optical)?(net)?(netusb)?(cd)?(cdusb)?([0-9]+)?"
        ]},
     "alarm" : {
         __USAGE : "alarm <off|on|once|everyday>",
         __DESCR : "Activates / deactivates alarm timers",
         __STATS : [ 138, 0, __PARAM ],
         __PARAMS : [{
             "off" : 0,
             "everyday" : 1,
             "once" : 2,
             "on" : 3
             }]
        },
     "wait" : {
         __USAGE : "wait",
         __DESCR : "Wait for a second before continue",
         __STATS : "__WAIT__"
        },
     "macro preset" : {
         __USAGE : "macro preset <nn>",
         __DESCR : "Changes to preset with given no"
        },
     "macro set-preset-name" : {
         __USAGE : "macro set-preset-name <name>",
         __DESCR : "set name for presets."
        },
     "macro delete-preset" : {
         __USAGE : "macro delete-preset <from> [<to>]",
         __DESCR : "Deletes tuner presets. Note that it gets out of"
            + " sync in case that preset is not available."
        },
     "help" : {
         __USAGE : "help",
         __DESCR : "Information about usage, commands and parameters"
        }
    }

KEY_PAD = [["0", " ", "^", "'", "(", ")", "*", "+", ",", "="],
           ["1", ".", "-", "/"],
           ["A", "B", "C", "2"],
           ["D", "E", "F", "3"],
           ["G", "H", "I", "4"],
           ["J", "K", "L", "5"],
           ["M", "N", "O", "6"],
           ["P", "Q", "R", "S", "7"],
           ["T", "U", "V", "8"],
           ["W", "X", "Y", "Z", "9"]]

port = PORT
ser = None




def __build_help(cmd, header = False, msg = ""):

    s = ""

    if header == True:
        s = """ Denon DRA-F109 command line remote control \
 for Linux / Raspberry Pi via serial port

 USAGE:   denon.py [/dev/ttyUSB0] <command1> <params1> <command2> ...
 EXAMPLE: Set FM radio as input source, select preset 24
          and set volume to 12
          $ ./denon.py fm num +10 num +10 num 4 vol 12
        """

    if msg != "":
        s += "\n " + msg

    s += "\n " + cmd[__USAGE].ljust(32) + "\t" + cmd[__DESCR]

    if msg != "":
        s += "\n"

    return s




def __help():

    s = ""
    i = 0
    for cmd in sorted(COMMANDS):
        s += __build_help(COMMANDS[cmd], i == 0)
        i += 1

    return s




def build_binary_commands_from_rc(rc_commands):

    binary_commands = []

    # process multiple commands
    while len(rc_commands) > 0:
        rc_seq = rc_commands[0]

        cmd_def = __interprete_command(rc_commands.pop(0))

        raw_seq = cmd_def[__STATS]
        params = []

        if __PARAMS in cmd_def:
            cmd_param_def = cmd_def[__PARAMS]
        else:
            cmd_param_def = []

        i = -1

        for param_def in cmd_param_def:

            i += 1

            # validate parameters
            if len(rc_commands) == 0:
                # command requires parameters but there are none
                raise HelpException(__build_help(cmd_def, True,
                                        "ERROR: Parameter is missing:"))

            # interprete given parameters
            rc_key = rc_commands.pop(0)
            rc_seq += " " + rc_key

            # handle parameter of type list (range of int values)
            if type(param_def) in (tuple, list, range):
                params.append(__interprete_param_array(cmd_def,
                                                rc_key,
                                                param_def))

            # handle parameter of type dict (lookup values)
            elif type(param_def) in (tuple, dict):
                params.append(__interprete_param_dict(cmd_def,
                                               rc_key,
                                               param_def))

            # handle parameter of keywords (lookedup by regexp)
            elif type(param_def) in (tuple, str):
                params += __interprete_param_regex(cmd_def,
                                                rc_key,
                                                param_def,
                                                cmd_def[__PARSER][i])

        # collect commands
        binary_commands.append({
                "binary" : __replace_params(raw_seq, params),
                "rc_cmd" : rc_seq
            })

    return binary_commands




def __replace_params(raw_seq, params):

    params.reverse()

    rv = []
    for b in raw_seq:
        if ( b == -1):
            rv += [ params.pop() ]
        else:
            rv += [ b ]

    return rv




def __interprete_command(cli_cmd):

    if cli_cmd not in COMMANDS:
        raise HelpException(__help()
                        + "\n\n ERROR: Invalid command <"
                        + cli_cmd + ">\n")

    return COMMANDS[cli_cmd]




def __interprete_param_array(cmd_def, cli_arg, cmd_param_def):

    # check if cli_arg is in list of allowed int values
    if int(cli_arg) not in cmd_param_def:
        raise HelpException(__build_help(cmd_def, True,
                   "ERROR: Value <" + cli_arg
                   + "> is out of allowed range:"))

    # return int value of cli_arg as char
    return int(cli_arg)




def __interprete_param_dict(cmd_def, cli_arg, cmd_param_def):

    # check if cli_arg is in list of allowed dict values
    if cli_arg not in cmd_param_def:
        raise HelpException(__build_help(cmd_def, True, "ERROR: Keyword <"
                   + cli_arg
                   + "> is not allowed here:"))

    # lookup dict value and return char sequence
    return cmd_param_def[cli_arg]




def __interprete_param_regex(cmd_def, cli_arg, cmd_param_def, parser):

    # validate parameter by matching regular expression
    matcher = re.search(cmd_param_def, cli_arg)

    ex = HelpException(__build_help(cmd_def, True,
                        "ERROR: Syntax of value <"
                        + cli_arg
                        + "> is wrong!"))

    if matcher == None:
        raise ex

    b = __parse(matcher, parser)
    if len(b) == 0:
        raise ex

    return b




def __parse(matcher, instruc):

    b = []
    for i in range(len(instruc)):
        m = matcher.group(i +1)
        if m == None:
            continue
        elif instruc[i] == __PARSE_VAL :
            b += [ int(matcher.group(i + 1)) ]
        elif instruc[i] == __PARSE_IDX:
            b += [ i ]

    return b




def send_serial_commands(commands):

    try:
        __init_serial()

        n = 0
        for cmd in commands:
            if n > 0:
                time.sleep(.8)
            n += 1
            print(" INFO: Send command <" + cmd["rc_cmd"] + ">")

            if cmd["binary"] == "__WAIT__":
                time.sleep(1.2)
            else:
                package = __build_package(cmd["binary"])
                __send_package(package)

            print(" DONE: <" + cmd["rc_cmd"] + ">")

    finally:
        __close_serial()




def __init_serial():

    global ser
    dev = None
    if port == None:
        c = 0
        for p in list(serial.tools.list_ports.comports()):
            c += 1
            dev = p.device
            print(" INFO: Serial device found <" + p.device + ">")

        if dev == None:
            raise HelpException(" FATAL: No serial device found!")

        elif c > 1:
            raise HelpException("""
 FATAL: Found more than one serial device
 Please force serial device by (a) passing it as parameter, e.g.
 $ denon.sh /dev/ttyUSB0 ...
 or (b) by settings PORT constant inside program code, e.g.
 PORT = "/dev/ttyUSB0"
                """)
    else:
        print(" INFO: Force serial device to <" + port + ">")
        dev = port

    ser = serial.Serial(dev, baudrate = 115200, 
                        bytesize = serial.EIGHTBITS,
                        parity = serial.PARITY_NONE, 
                        stopbits = serial.STOPBITS_ONE, 
                        timeout = 5, 
                        write_timeout = 5,
                        rtscts = True, 
                        dsrdtr = True,
                        xonxoff = False,
                        exclusive = True)




def __close_serial():

    global ser

    if ser != None:
        ser.close()




def __build_package(data):

    # preample
    package = [ 255, 85 ]

    # length
    length = len(data) - 2
    package += [ length ]

    # static
    package += [ 1, 0 ]

    # data
    package += data

    # checksum
    checksum = 0
    for i in package:
        checksum += i

    checksum %= 256
    package += [ checksum ]

    return package




def __send_package(package):

    global ser
    ser.sendBreak()
    ser.write(package)
    ser.flush()




def __number_to_rc_commands(no):

    no = int(no)

    rc_commands = []
    while True:
        if no >= 10:
            rc_commands += ["num", "+10"]
            no -= 10
        else:
            rc_commands += ["num", str(no)]
            break

    return rc_commands




def build_macro(macro_call):

    if len(macro_call) == 0:
        raise HelpException(" ERROR: No macro name given.")

    macro_cmd = macro_call.pop(0)

    if macro_cmd == "preset":
        rc_commands = __build_macro_preset(macro_call)

    elif macro_cmd == "delete-preset":
        rc_commands = __build_macro_delete_presets(macro_call)

    elif macro_cmd == "set-preset-name":
        rc_commands = __build_macro_set_preset_name(macro_call)

    else:
        raise HelpException(" ERROR: Macro <" + macro_cmd + "> unknown.")

    return rc_commands




def __build_macro_delete_presets(macro_call):

    # validate parameters
    try:
        if len(macro_call) == 0:
            raise Exception()

        start = int(macro_call.pop(0))
        end = start
        if len(macro_call) > 0:
            end = int(macro_call.pop(0))
    except:
        raise HelpException(__build_help(COMMANDS["macro delete-preset"], True,
                   "ERROR: Invalid parameters."))

    # build rc commands
    rc_commands = ["fm"]
    while start <= end:
        rc_commands += __number_to_rc_commands(start)
        rc_commands += ["clear", "enter"]
        start += 1

    return rc_commands




def __build_macro_preset(macro_call):

    # validate parameters
    try:
        if len(macro_call) == 0:
            raise Exception()

        preset = int(macro_call.pop(0))

    except:
        raise HelpException(__build_help(COMMANDS["macro preset"], True,
                   "ERROR: Invalid parameters."))

    # build rc commands
    rc_commands = ["fm", "wait"]
    rc_commands += __number_to_rc_commands(preset)

    return rc_commands




def __build_macro_set_preset_name(macro_call):

    # validate parameters
    try:
        if len(macro_call) < 2:
            raise Exception()

        preset = int(macro_call.pop(0))
        name = macro_call.pop(0) + (" " * 8)
        name = name.upper()[:8]

    except:
        raise HelpException(__build_help(COMMANDS["macro set-preset-name"], True,
                   "ERROR: Invalid parameters."))

    # build rc commands
    rc_commands = ["fm"]
    rc_commands += __number_to_rc_commands(preset)
    rc_commands += ["enter", "enter"]

    i = 0
    for c in name:
        i += 1
        press = None
        key = None
        for p in range(len(KEY_PAD)):
            if c in KEY_PAD[p]:
                key = p
                press = KEY_PAD[p].index(c) + 1

        if key == None:
            key = 0
            press = 2

        rc_commands += ["clear"]
        if i > 1:
            rc_commands += ["right"]
        rc_commands += __number_to_rc_commands(key) * press
        rc_commands += ["right"]
    rc_commands += ["enter"]

    return rc_commands




def sendto_denon(commands):

    global port

    if len(commands) > 0 and commands[0].startswith("/dev/tty"):
        port = commands.pop(0)

    if commands[0] == "macro":
        commands = build_macro(commands[1:])

    binary_commands = build_binary_commands_from_rc(commands)
    send_serial_commands(binary_commands)




if __name__ == "__main__":

    try:
        commands = sys.argv[1:]
        if len(commands) == 2 and commands[0] == "help" and commands[1] in COMMANDS:
            print(__build_help(COMMANDS[commands[1]]))
        elif len(commands) == 0 or commands[0] == "help":
            print(__help())
        else:
            sendto_denon(commands)

    except HelpException as e:
        print(e.message)
        exit(1)
