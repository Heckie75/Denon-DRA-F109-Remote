import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import denon

__PLUGIN_ID__ = "plugin.audio.denon-dra-f109-remote"

settings = xbmcaddon.Addon(id=__PLUGIN_ID__);
addon_handle = int(sys.argv[1])

def __build_alarm():

    sources = ["preset", "optical", "cd", "cdusb",
               "net", "netusb", "analog1", "analog2"]

    everyday_start = settings.getSetting("alarm_everyday_start")
    everyday_end = settings.getSetting("alarm_everyday_end")
    everyday_source = int(settings.getSetting("alarm_everyday_source"))
    
    if everyday_source == 0:
        everyday_preset = settings.getSetting("alarm_everyday_preset")
    else:
        everyday_preset = ""

    once_start = settings.getSetting("alarm_once_start")
    once_end = settings.getSetting("alarm_once_end")
    once_source = int(settings.getSetting("alarm_once_source"))
    
    if once_source == 0:
        once_preset = settings.getSetting("alarm_once_preset")
    else:
        once_preset = ""

    entries = [
        {
            "path" : "off",
            "name" : "Off",
            "send" : ["alarm", "off"]
        }
    ]
    
    if everyday_start != "" and everyday_end != "": 
        entries += [
            {
                "path" : "everyday",
                "name" : "Everyday from %s to %s play %s %s"
                        % (everyday_start, everyday_end,
                           sources[everyday_source], everyday_preset),
                "send" : ["set-alarm", "everyday",
                    everyday_start,
                    everyday_end,
                    sources[everyday_source] + everyday_preset,
                    "wait",
                    "alarm", "everyday"]
            }
        ]
        
    if once_start != "" and once_end != "": 
        entries += [
            {
                "path" : "once",
                "name" : "Once from %s to %s play %s %s"
                        % (once_start, once_end,
                           sources[once_source], once_preset),
                "send" : ["set-alarm", "once",
                    once_start,
                    once_end,
                    sources[once_source] + once_preset,
                    "wait",
                    "alarm", "once"]
            }
        ]
                    
    if everyday_start != "" \
        and everyday_end != "" \
        and once_start != "" \
        and once_end != "": 
        
        entries += [
            {
                "path" : "on",
                "name" : ("Everyday from %s to %s play %s %s\n"
                        + "and Once from %s to %s play %s %s")
                        % (everyday_start, everyday_end,
                           sources[everyday_source], everyday_preset,
                           once_start, once_end,
                           sources[once_source], once_preset),
                "send" : ["set-alarm", "everyday",
                    everyday_start,
                    everyday_end,
                    sources[everyday_source] + everyday_preset,
                    "wait",
                    once_start,
                    once_end,
                    sources[once_source] + once_preset,
                    "wait",
                    "alarm", "on"]
            }
        ]

    return entries

def __build_presets():

    entries = []

    for i in range(1, 40):
        if settings.getSetting("preset_%s" % str(i)) == "":
            continue

        entries += [
            {
                "path" : str(i),
                "name" : settings.getSetting("preset_%s" % str(i)),
                "send" : ["macro", "preset", str(i)],
            }
        ]

    return entries

def __build_sleep_timer():
    entries = [
        {
            "path" : "off",
            "name" : "Off",
            "send" : ["sleep", "0"]
        }
    ]

    for i in range(1, 6):
        t = settings.getSetting("sleep_preset_%i" % i)
        entries += [
            {
                "path" : str(i),
                "name" : "%s minutes" % t,
                "send" : ["sleep", t]
            }
        ]

    return entries

def __build_volume():
    entries = [
        {
            "path" : "off",
            "name" : "Off",
            "send" : ["mute", "on"]
        },
        {
            "path" : "on",
            "name" : "On",
            "send" : ["mute", "off"]
        }
    ]

    _range = range(
        int(settings.getSetting("vol_min")),
        int(settings.getSetting("vol_max")) + 1,
        int(settings.getSetting("vol_step")))

    for i in _range:
        entries += [
            {
                "path" : str(i),
                "name" : str(i),
                "send" : ["vol", str(i)]
            }
        ]

    return entries

__menu = [
    { # root
        "path" : "",
        "node" : [
            { # fm
                "path" : "fm",
                "name" : "FM Radio",
                "send" : ["fm"]
            },
            { # dab
                "path" : "dab",
                "name" : "DAB Radio",
                "send" : ["dab"]
            },
            { # presets
                "path" : "presets",
                "name" : "Radio presets",
                "node" : __build_presets()
            },
            { # preset
                "path" : "preset",
                "name" : "Tune",
                "node" : [
                    { # preset +
                        "path" : "preset_next",
                        "name" : "Preset +",
                        "send" : ["preset", "%2B"]
                    },
                    { # preset -
                        "path" : "preset_prev",
                        "name" : "Preset -",
                        "send" : ["preset", "-"]
                    },
                    { # mode
                        "path" : "mode",
                        "name" : "Stereo / Mono",
                        "send" : ["mode"]
                    }
                ]
            },
            { # cd
                "path" : "cd",
                "name" : "CD",
                "send" : ["cd"]
            },
            { # net
                "path" : "net",
                "name" : "Network",
                "send" : ["net"]
            },
            { # optical
                "path" : "optical",
                "name" : "Optical",
                "send" : ["optical"]
            },
            { # analog 1
                "path" : "analog1",
                "name" : "Analog 1",
                "send" : ["analog", "1"]
            },
            { # analog 2
                "path" : "analog2",
                "name" : "Analog 2",
                "send" : ["analog", "2"]
            },                  
            { # cda
                "path" : "cda",
                "name" : "CD Audio",
                "send" : ["cda"]
            },
            { # usb
                "path" : "usb",
                "name" : "USB",
                "send" : ["usb"]
            },                  
            { # internet
                "path" : "internet",
                "name" : "Internet radio",
                "send" : ["internet"]
            },
            { # online
                "path" : "online",
                "name" : "Online music",
                "send" : ["online"]
            },
            { # server
                "path" : "server",
                "name" : "Music server",
                "send" : ["server"]
            },
            { # ipod
                "path" : "ipod",
                "name" : "iPOD",
                "send" : ["ipod"]
            },                  
            { # power
                "path" : "power",
                "name" : "Power / timers",
                "node" : [
                    { # off
                        "path" : "off",
                        "name" : "Power Off",
                        "send" : ["off"]
                    },
                    { # on
                        "path" : "on",
                        "name" : "Power On",
                        "send" : ["on"]
                    },
                    { # sleep
                        "path" : "sleep",
                        "name" : "Sleep timer",
                        "node" : __build_sleep_timer()
                    },
                    { # alarm
                        "path" : "alarm",
                        "name" : "Alarm",
                        "node" : __build_alarm()
                    },
                    { # dimmer
                        "path" : "dimmer",
                        "name" : "Dimmer",
                        "node" : [
                            { # off
                                "path" : "off",
                                "name" : "Off",
                                "send" : ["dimmer", "off"]
                            },
                            { # low
                                "path" : "low",
                                "name" : "Low",
                                "send" : ["dimmer", "low"]
                            },
                            { # normal
                                "path" : "normal",
                                "name" : "Normal",
                                "send" : ["dimmer", "normal"]
                            },
                            { # high
                                "path" : "high",
                                "name" : "High",
                                "send" : ["dimmer", "high"]
                            }
                        ]
                    },
                    { # standby
                        "path" : "standby",
                        "name" : "Auto standby",
                        "node" : [
                            { # off
                                "path" : "off",
                                "name" : "Auto standby Off",
                                "send" : ["standby", "off"]
                            },
                            { # on
                                "path" : "on",
                                "name" : "Auto standby on",
                                "send" : ["standby", "on"]
                            }
                        ]
                    }
                ]
            },
            { # sound
                "path" : "sound",
                "name" : "Sound settings",
                "node" : [
                    { # volume
                        "path" : "volume",
                        "name" : "Volume",
                        "node" : __build_volume()
                    },
                    { # bass
                        "path" : "bass",
                        "name" : "Bass",
                        "node" : [
                            { # incr
                                "path" : "incr",
                                "name" : "Bass +",
                                "send" : ["bass", "%2B"]
                            },
                            { # decr
                                "path" : "decr",
                                "name" : "Bass -",
                                "send" : ["bass", "-"]
                            }
                        ]
                    },
                    { # treble
                        "path" : "treble",
                        "name" : "Treble",
                        "node" : [
                            { # incr
                                "path" : "incr",
                                "name" : "Treble +",
                                "send" : ["treble", "%2B"]
                            },
                            { # decr
                                "path" : "decr",
                                "name" : "Treble -",
                                "send" : ["treble", "-"]
                            }
                        ]
                    },
                    { # balance
                        "path": "balance",
                        "name" : "Balance",
                        "node" : [
                            { # left
                                "path"  : "left",
                                "name" : "Balance left",
                                "send" : ["balance", "left"]
                            },
                            { # right
                                "path" : "right",
                                "name" : "Balance right",
                                "send" : ["balance", "right"]
                            }
                        ]
                    },
                    { # sdirect
                        "path" : "sdirect",
                        "name" : "S.Direct",
                        "node" : [
                            { # off
                                "path" : "off",
                                "name" : "S.Direct Off",
                                "send" : ["sdirect", "off"]
                            },
                            { # on
                                "path" : "on",
                                "name" : "S.Direct On",
                                "send" : ["sdirect", "on"]
                            }
                        ]
                    },
                    { # sdb
                        "path" : "sdb",
                        "name" : "SDB",
                        "node" : [
                            { # off
                                "path" : "off",
                                "name" : "SDB Off",
                                "send" : ["sdb", "off"]
                            },
                            { # on
                                "path" : "on",
                                "name" : "SDB On",
                                "send" : ["sdb", "on"]
                            }
                        ]
                    }
                ]
            }
        ]
    }
]

def __get_directory_by_path(path):

    if path == "/":
        return __menu[0]

    tokens = path.split("/")[1:]
    directory = __menu[0]

    while len(tokens) > 0:
        path = tokens.pop(0)
        for node in directory["node"]:
            if node["path"] == path:
                directory = node
                break

    return directory

def __fill_directory(path):

    directory = __get_directory_by_path(path)

    for entry in directory["node"]:
        __add_list_item(entry, path)

    xbmcplugin.endOfDirectory(addon_handle)


def __build_param_string(params):

    s = ""
    i = 0
    for param in params:
        if i == 0:
            s = "?"
        else:
            s += "&"

        s += "send=" + param
        i += 1

    return s

def __add_list_item(entry, path):

    if path == "/":
        path = ""

    item_path = path + "/" + entry["path"]
    item_id = item_path.replace("/", "_")

    if "send" in entry:
        param_string = __build_param_string(entry["send"])
    else:
        param_string = ""

    if settings.getSetting("display%s" % item_id) == "false":
        return

    if "node" in entry:
        is_folder = True
    else:
        is_folder = False

    label = entry["name"]
    if settings.getSetting("label%s" % item_id) != "":
        label = settings.getSetting("label%s" % item_id)

    li = xbmcgui.ListItem(label)

    xbmcplugin.addDirectoryItem(handle=addon_handle,
                            listitem=li,
                            url="plugin://" + __PLUGIN_ID__
                            + item_path
                            + param_string,
                            isFolder=is_folder)

def __call_denon(send_params):

    params = [settings.getSetting("device")]
    params += send_params
    denon.sendto_denon(params)

if __name__ == "__main__":

    path = urlparse.urlparse(sys.argv[0]).path
    url_params = urlparse.parse_qs(sys.argv[2][1:])

    if "send" in url_params:
        __call_denon(url_params["send"])
    else:
        __fill_directory(path)

    xbmcplugin.setContent(addon_handle, 'movies')