#!/usr/bin/python

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

import serial.tools.list_ports
import sys
import time
import re

# Force serial port by setting the constant, e.g. 
# PORT = "/dev/ttyUSB0"
PORT = None 

COMMANDS = {
    "on" : {
         "usage" : "on",
         "descr" : "Turns denon receiver on",
         "statics" : ["\x01\x02\x00"], 
         "params" : [None]
         },
     "off" : {
         "usage" : "off",         
         "descr" : "Turns denon receiver off",
         "statics" : ["\x02\x01\x00"],
         "params" : [None]
         },
     "fm" : {
         "usage" : "fm",
         "descr" : "Sets input source to FM radio",
         "statics" : ["\x10\x00\x00"],
         "params" : [None]
         },
     "dab" : { # can't test
         "usage" : "dab",         
         "descr" : "Sets input source to DAB radio",
         "statics" : ["\x12\x00\x00"],
         "params" : [None]
         },
     "cd" : {
         "usage" : "cd",         
         "descr" : "Sets input source to CD (digital-in for CD)",
         "statics" : ["\x13\x00\x00"],
         "params" : [None]
         }, 
     "net" : {
         "usage" : "net",         
         "descr" : "Sets input source to Network (digital-in NETWORK)",
         "statics" : ["\x14\x00\x00"],
         "params" : [None]
         }, 
     "analog" : {
         "usage" : "analog <1|2>",      
         "descr" : "Sets input source to Analog n, where n is 1 or 2",
         "statics" : ["", "\x00\x00"],
         "params" : [{
             "1" : "\x15",
             "2" : "\x16"
             }, None]
         },
     "optical" : {
         "usage" : "optical",         
         "descr" : "Sets input source to Digital-In optical",
         "statics" : ["\x17\x00\x00"],
         "params" : [None]
         },
     "mode" : {
         "usage" : "mode",       
         "descr" : "Toggles stereo/mono mode",
         "statics" : ["\x28\x00\x00"],
         "params" : [None]
         },
     "play" : { # can't test
         "usage" : "play/pause",         
         "descr" : "Starts playback",
         "statics" : ["\x32\x00\x00"],
         "params" : [None]
         }, 
     "pause" : { # can't test
         "usage" : "play/pause",         
         "descr" : "Pauses current playback",
         "statics" : ["\x32\x00\x00"],
         "params" : [None]
         },
     "stop" : { # can't test
         "usage" : "stop",         
         "descr" : "Stops current playback",
         "statics" : ["\x33\x00\x00"],
         "params" : [None]
         },
     "vol" : {
         "usage" : "volume <0-60>",         
         "descr" : "Sets volume to value whish is between 0 and 60",
         "statics" : ["\x40\x00"],
         "params" : [range(0x3c)]
         },             
     "mute" : {
         "usage" : "mute <on|off>",         
         "descr" : "Mute on/off",
         "statics" : ["\x41\x00"],
         "params" : [{
             "on" : "\x01",
             "off" : "\x00"
             }]
         },             
     "sdb" : {
         "usage" : "sdb <on|off>",         
         "descr" : "SDB sound option on/off",
         "statics" : ["\x42\x00\x00"],
         "params" : [{
             "on" : "\x00",
             "off" : "\x01"
             }]
         },             
     "bass" : {
         "usage" : "bass <+|->",         
         "descr" : "Increases / decreases bass level",
         "statics" : ["\x42\x00\x01"],
         "params" : [{
             "+" : "\x00",
             "-" : "\x01"
             }]
         },             
     "treble" : {
         "usage" : "treble <+|->",         
         "descr" : "Increases / decreases treble level",
         "statics" : ["\x42\x00\x02"],
         "params" : [{
             "+" : "\x00",
             "-" : "\x01"
             }]
         },             
     "balance" : {
         "usage" : "balance <left|right>",         
         "descr" : "Sets balance one step more to left or right",
         "statics" : ["\x42\x00\x03"],
         "params" : [{
             "left" : "\x00",
             "right" : "\x01"
             }]
         },             
     "sdirect" : {
         "usage" : "sdirect <on|off>",         
         "descr" : "Activates/deactivates s.direct input",
         "statics" : ["\x42\x00\x04"],
         "params" : [{
             "on" : "\x00",
             "off" : "\x01"
             }]
         },             
     "dimmer" : {
         "usage" : "dimmer <high|normal|low|off>",         
         "descr" : "Sets brightness of display",
         "statics" : ["\x43\x00"],
         "params" : [{
             "high" : "\x00",
             "normal" : "\x01",
             "low" : "\x02",
             "off" : "\x03"
             }]
         },
     "next" : { # can't test
         "usage" : "next",         
         "descr" : "Jump to next title",
         "statics" : ["\x44\x00\x00"],
         "params" : [None]
         },
     "prev" : { # can't test
         "usage" : "previous",         
         "descr" : "Jump to previous title",
         "statics" : ["\x45\x00\x00"],
         "params" : [None]
         },
     "forward" : { # can't test
         "usage" : "forward",         
         "descr" : "Forwards in current title",
         "statics" : ["\x46\x00\x00"],
         "params" : [None]
         },
     "rewind" : { # can't test
         "usage" : "rewind",         
         "descr" : "Rewinds in current title",
         "statics" : ["\x47\x00\x00"],
         "params" : [None]
         },
     "up" : {
         "usage" : "up",         
         "descr" : "Moves in current menu up",
         "statics" : ["\x48\x00\x00"],
         "params" : [None]
         },
     "down" : {
         "usage" : "down",         
         "descr" : "Moves in current menu down",
         "statics" : ["\x49\x00\x00"],
         "params" : [None]
         },
     "left" : {
         "usage" : "left",         
         "descr" : "Moves in current menu to the left",
         "statics" : ["\x4a\x00\x00"],
         "params" : [None]
         },
     "right" : {
         "usage" : "right",         
         "descr" : "Moves in current menu to the right",
         "statics" : ["\x4b\x00\x00"],
         "params" : [None]
         },
     "enter" : {
         "usage" : "enter",         
         "descr" : "Commit current setting by pressing enter",
         "statics" : ["\x4c\x00\x00"],
         "params" : [None]
         },
     "search" : {
         "usage" : "search",         
         "descr" : "Enter search menu",
         "statics" : ["\x4d\x00\x00"],
         "params" : [None]
         },
     "num" : {
         "usage" : "num <0-9|+10>",
         "descr" : "Sends numeric buttom 0-9 / '+10' to receiver",
         "statics" : ["", "\x00\x00"],
         "params" : [{
             "1" : "\x4f",
             "2" : "\x50",
             "3" : "\x51",
             "4" : "\x52",
             "5" : "\x53",
             "6" : "\x54",
             "7" : "\x55",
             "8" : "\x56",
             "9" : "\x57",
             "0" : "\x58",
             "+10" : "\x59"
             }, None]
         },            
     "clear" : {
         "usage" : "clear",         
         "descr" : "Sends clear command",
         "statics" : ["\x5a\x00\x00"],
         "params" : [None]
         },
     "random" : { # can't test
         "usage" : "random",         
         "descr" : "(does not seem to work)",
         "statics" : ["\x5c\x00\x00"],
         "params" : [None]
         },
     "repeat" : { # can't test
         "usage" : "repeat",         
         "descr" : "Toggles repeat option for playback",
         "statics" : ["\x5d\x00\x00"],
         "params" : [None]
         },
     "info" : {
         "usage" : "info",         
         "descr" : "Toggles display",
         "statics" : ["\x5e\x00\x00"],
         "params" : [None]
         },
     "cda" : {
         "usage" : "cda",         
         "descr" : "Sets input source to CD and selects CD",
         "statics" : ["\x5f\x00\x00"],
         "params" : [None]
         },
     "usb" : {
         "usage" : "usb",
         "descr" : "Sets input source to CD and selects USB",
         "statics" : ["\x60\x00\x00"],
         "params" : [None]
         },                                    
     "online" : {
         "usage" : "online",         
         "descr" : "Sets input source to Network "
            + "and selects online music",
         "statics" : ["\x61\x00\x00"],
         "params" : [None]
         },
     "internet" : {
         "usage" : "internet",         
         "descr" : "Sets input source to Network "
            + "and selects internet radio",
         "statics" : ["\x62\x00\x00"],
         "params" : [None]
         },
     "server" : {
         "usage" : "server",         
         "descr" : "Sets input source to Network and selects server",
         "statics" : ["\x63\x00\x00"],
         "params" : [None]
         },
     "ipod" : {
         "usage" : "ipod",         
         "descr" : "Sets input source to Network and selects iPod",
         "statics" : ["\x63\x00\x00"],
         "params" : [None]
         },                                                                                                                                                                                    
     "preset" : {
         "usage" : "preset <+|->",         
         "descr" : "Zaps to previous / next preset",
         "statics" : ["\x68\x30"],
         "params" : [{
             "+" : "\x00",
             "-" : "\x01"             
             }]
         },
     "sleep" : {
         "usage" : "sleep <0-255>",         
         "descr" : "Activates sleep mode with time in minutes",
         "statics" : ["\x6b\x00"],
         "params" : [range(256)]
         },
     "standby" : {
         "usage" : "standby <on|off>",         
         "descr" : "Sets auto-standby on/off",
         "statics" : ["\x83\x00"],
         "params" : [{
             "off" : "\x00",
             "on" : "\x01"
             }]
         },
     "set-alarm" : {
         "usage" : "set-alarm <once|everyday> <hh:mm> <hh:mm> "
            + "<analog1|analog2|optical|net|netusb|cd|cdusb|preset>"
            + "[<preset no.>]",         
         "descr" : "Configures alarm clock, e.g. set-alarm once " 
            + "21:17 23:45 preset24",
         "statics" : ["", "\x00\x00", "\x00", ""],
         "parser" : [None, 
                     ["$", "$"], 
                     ["$", "$"], 
                     ["#", "#", "#", "#", "#", "#", "#", "#", "$"]],
         "params" : [{
                "once" : "\x88",
                "everyday" : "\x89",
             },
             r"([0-2][0-9]):([0-5][0-9])",
             r"([0-2][0-9]):([0-5][0-9])",
             r"(preset)?(analog1)?(analog2)?" 
             + "(optical)?(net)?(netusb)?(cd)?(cdusb)?([0-9]+)?"
        ]},
     "alarm" : {
         "usage" : "alarm <off|on|once|everyday>",         
         "descr" : "Activates / deactivates alarm clocks",
         "statics" : ["\x8a\x00"],
         "params" : [{
             "off" : "\x00",
             "everyday" : "\x01",
             "once" : "\x02",
             "on" : "\x03"
             }]
        },
     "help" : {
         "usage" : "help",         
         "descr" : "Information about usage, commands and parameters"
        }            
    }

ser = None

def print_help(cmd, header = False, msg = ""):
    if header == True:
        print("Denon DRA-F109 command line remote control "
              + "for Linux / Raspberry Pi via Serial Port, e.g. "
              + "RS-232 / PL2303"        
              + "\n\nUSAGE:\tdenon.py <command1> <params1> <command2> " 
              + "<command2> ...\n")
        print("EXAMPLE:\tSet FM radio as input source, "
              + "select preset 24 and set volume to 12")
        print("\t\t$ ./denon.py fm num +10 num +10 num 4 vol 12\n")
    
    if msg != "":
        print(msg)

    print("  " + cmd["usage"].ljust(24) + "\t" + cmd["descr"])
    if msg != "":
        print("")

def print_all_help():
    
    i = 0
    for cmd in sorted(COMMANDS):
        print_help(COMMANDS[cmd], i == 0, "")
        i += 1
        
    print("")

def parse(matcher, instruc):
    
    s = ""
    for i in range(len(instruc)):
        m = matcher.group(i +1)
        if m == None:
            continue
        elif instruc[i] == "$" :
            s += chr(int(matcher.group(i + 1)))
        elif instruc[i] == "#":
            s += chr(i)
    
    return s
    
def translate_commands(args):
    
    args.pop(0)
    if len(args) == 2 and args[0] == "help" and args[1] in COMMANDS:
        print_help(COMMANDS[args[1]])
        exit(0)
    elif len(args) == 0 or args[0] == "help":
        print_all_help()
        exit(1)
        
    denon_commands = []
    while len(args) > 0:
        # check cli command
        cli_cmd = args.pop(0)
        cli_params = ""
        if cli_cmd not in COMMANDS:
            print_all_help()
            print("ERROR: Invalid command <" + cli_cmd + ">\n")
            exit(1)
        
        raw_cmd = ""    
        command = COMMANDS[cli_cmd]
        for i in range(len(command["statics"])):
            
            raw_cmd += command["statics"][i]
            
            param = command["params"][i]
            if param != None:
                if len(args) == 0:
                    print_help(command, True, 
                               "ERROR: Parameter is missing!")
                    exit(1)
                cli_param = args.pop(0)
                cli_params += " " + cli_param 
                
                # validate parameter value for array
                if type(param) in (tuple, list):
                    if int(cli_param) not in param:
                        print_help(command, True, 
                                   "ERROR: Parameter <" + cli_param 
                                   + "> is not allowed here!")
                        exit(1)
                    else:
                        raw_cmd += chr(int(cli_param))

                # validate parameter value for dictionary
                if type(param) in (tuple, dict):
                    if cli_param not in param:
                        print_help(command, True, "ERROR: Parameter <" 
                                   + cli_param 
                                   + "> is not allowed here!")
                        exit(1)
                    else:
                        raw_cmd += param[cli_param]

                # validate parameter value for string/regular expression
                if type(param) in (tuple, str):
                    matcher = re.search(param, cli_param)
                    if matcher == None:
                        print_help(command, True, "ERROR: Parameter <" 
                                   + cli_param 
                                   + "> is not allowed here!")
                        exit(1)
                    else:
                        s = parse(matcher, command["parser"][i])
                        if s == "":
                            print_help(command, True, 
                                       "ERROR: Parameter <" 
                                       + cli_param 
                                       + "> is not allowed here!")
                            exit(1)
                            
                        raw_cmd += s  
                    
        denon_commands.append({
                "raw" : raw_cmd,
                "command" : cli_cmd + cli_params
            })
    
    return denon_commands
    

def send_commands(commands):
    
    init_serial()

    for cmd in commands:
        package = build_package(cmd["raw"])
        print(" INFO: Send command <" + cmd["command"] + ">")
        send_package(package)
        print(" DONE: <" + cmd["command"] + ">")
        time.sleep(.8)
        
    close_serial()

def init_serial():
    global ser
    
    dev = None
    c = 0
    for p in list(serial.tools.list_ports.comports()):
        c += 1
        dev = p.device
        print(" INFO: Serial device found <" + p.device + ">")
    
    if dev == None:
        print(" FATAL: No serial device found!")
        exit(1)
    elif c > 1 and PORT == None:
        print(" FATAL: Found more than one serial device")
        print(
            """
 Please specify serial device by setting PORT variable inside
 program code, e.g. PORT = "/dev/ttyUSB0"
            """)
        exit(1)
        
    
    ser = serial.Serial(dev, 115200, serial.EIGHTBITS, 
                        serial.PARITY_NONE, serial.STOPBITS_ONE)

def close_serial():
    global ser
    ser.close()

def build_package(data):
    # preample
    package = "\xFF\x55"
    
    # length
    length = len(data) - 2
    package += chr(length)
    
    # static
    package += "\x01\x00"
    
    # data
    package += data
    
    # checksum
    checksum = 0
    for i in package:
        checksum += ord(i)
        
    checksum %= 256
    package += chr(checksum)
    
    return package
    
def send_package(package):
    global ser
    ser.sendBreak()
    time.sleep(.01625)
    ser.write(package)
    ser.flush()

if __name__ == "__main__":
    denon_commands = translate_commands(sys.argv)
    send_commands(denon_commands)
    
