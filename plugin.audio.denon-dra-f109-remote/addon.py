import os
import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import denon

__PLUGIN_ID__ = "plugin.audio.denon-dra-f109-remote"

settings = xbmcaddon.Addon(id=__PLUGIN_ID__);
addon_handle = int(sys.argv[1])
addon_dir = xbmc.translatePath( settings.getAddonInfo('path') )

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
            "icon" : "icon_alarm",
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
                "icon" : "icon_alarm",
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
                "icon" : "icon_alarm",
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
                "icon" : "icon_alarm",
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

def __send_kodi():

    sources = [["analog", "1"],
               ["analog", "2"],
               ["optical"], 
               ["cd"],
               ["net"]]

    kodi_input_source = int(settings.getSetting("kodi_input_source"))

    return sources[kodi_input_source]


def __build_presets():

    entries = []

    for i in range(1, 40):
        if settings.getSetting("preset_%s" % str(i)) == "":
            continue

        entries += [
            {
                "path" : str(i),
                "name" : settings.getSetting("preset_%s" % str(i)),
                "icon" : "icon_%s" % (str(i % 10)),
                "send" : ["macro", "preset", str(i)],
            }
        ]

    return entries

def __build_sleep_timer():
    entries = [
        {
            "path" : "off",
            "name" : "Off",
            "icon" : "icon_sleep",
            "send" : ["sleep", "0"]
        }
    ]

    for i in range(1, 6):
        t = settings.getSetting("sleep_preset_%i" % i)
        entries += [
            {
                "path" : str(i),
                "name" : "%s minutes" % t,
                "icon" : "icon_sleep",                
                "send" : ["sleep", t]
            }
        ]

    return entries

def __build_volume():
    entries = [
        {
            "path" : "off",
            "name" : "Mute On",
            "icon" : "icon_mute",            
            "send" : ["mute", "on"]
        },
        {
            "path" : "on",
            "name" : "Mute Off",
            "icon" : "icon_mute_off",
            "send" : ["mute", "off"]
        }
    ]


    _min = int(settings.getSetting("vol_min"))
    _max = int(settings.getSetting("vol_max")) + 1
    _step = int(settings.getSetting("vol_step"))

    icons = ["icon_zero", "icon_low", "icon_medium", "icon_full"]
    icon_div = (_max - _min) / (1.0 * len(icons))

    _range = range(_min, _max, _step)

    for i in _range:
        
        entries += [
            {
                "path" : str(i),
                "name" : str(i),
                "icon" : icons[int(((i - _min) / icon_div))],
                "send" : ["vol", str(i)]
            }
        ]

    return entries

__menu = [
    { # root
        "path" : "",
        "node" : [
            { # kodi
                "path" : "kodi",
                "name" : "KODI",
                "icon" : "icon_kodi",
                "send" : __send_kodi()
            },
            { # fm
                "path" : "fm",
                "name" : "FM Radio",
                "icon" : "icon_radio",
                "send" : ["fm"]
            },
            { # dab
                "path" : "dab",
                "name" : "DAB Radio",
                "icon" : "icon_dab",
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
                        "icon" : "icon_arrow_up",
                        "send" : ["preset", "%2B"]
                    },
                    { # preset -
                        "path" : "preset_prev",
                        "name" : "Preset -",
                        "icon" : "icon_arrow_down",
                        "send" : ["preset", "-"]
                    },
                    { # mode
                        "path" : "mode",
                        "name" : "Stereo / Mono",
                        "icon" : "icon_stereo",
                        "send" : ["mode"]
                    },
                    { # info
                        "path" : "info",
                        "name" : "Info",
                        "icon" : "icon_info",
                        "send" : ["info"]
                    }                          
                ]
            },
            { # cd
                "path" : "cd",
                "name" : "CD",
                "icon" : "icon_cd",
                "send" : ["cd"]
            },
            { # net
                "path" : "net",
                "name" : "Network",
                "icon" : "icon_net",
                "send" : ["net"]
            },
            { # optical
                "path" : "optical",
                "name" : "Optical",
                "icon" : "icon_digital",
                "send" : ["optical"]
            },
            { # analog 1
                "path" : "analog1",
                "name" : "Analog 1",
                "icon" : "icon_analog",
                "send" : ["analog", "1"]
            },
            { # analog 2
                "path" : "analog2",
                "name" : "Analog 2",
                "icon" : "icon_analog",
                "send" : ["analog", "2"]
            },                  
            { # cda
                "path" : "cda",
                "name" : "CD Audio",
                "icon" : "icon_cd",
                "send" : ["cda"]
            },
            { # usb
                "path" : "usb",
                "name" : "USB",
                "icon" : "icon_usb",
                "send" : ["usb"]
            },                  
            { # internet
                "path" : "internet",
                "name" : "Internet radio",
                "icon" : "icon_internet",
                "send" : ["internet"]
            },
            { # online
                "path" : "online",
                "name" : "Online music",
                "icon" : "icon_net",
                "send" : ["online"]
            },
            { # server
                "path" : "server",
                "name" : "Music server",
                "icon" : "icon_server",
                "send" : ["server"]
            },
            { # ipod
                "path" : "ipod",
                "name" : "iPOD",
                "icon" : "icon_usb",
                "send" : ["ipod"]
            },
            { # power off
                "path" : "off",
                "name" : "Power off",
                "icon" : "icon_power",
                "send" : ["off"]
            },
            { # power
                "path" : "power",
                "name" : "Timers",
                "node" : [
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
                                "icon" : "icon_zero",
                                "send" : ["dimmer", "off"]
                            },
                            { # low
                                "path" : "low",
                                "name" : "Low",
                                "icon" : "icon_low",
                                "send" : ["dimmer", "low"]
                            },
                            { # normal
                                "path" : "normal",
                                "name" : "Normal",
                                "icon" : "icon_medium",
                                "send" : ["dimmer", "normal"]
                            },
                            { # high
                                "path" : "high",
                                "name" : "High",
                                "icon" : "icon_full",
                                "send" : ["dimmer", "high"]
                            }
                        ]
                    },
                    { # power off
                        "path" : "off",
                        "name" : "Power off",
                        "icon" : "icon_power",
                        "send" : ["off"]
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
                                "icon" : "icon_sound_up",
                                "send" : ["bass", "%2B"]
                            },
                            { # decr
                                "path" : "decr",
                                "name" : "Bass -",
                                "icon" : "icon_sound_down",
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
                                "icon" : "icon_sound_up",
                                "send" : ["treble", "%2B"]
                            },
                            { # decr
                                "path" : "decr",
                                "name" : "Treble -",
                                "icon" : "icon_sound_down",
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
                                "icon" : "icon_arrow_left",
                                "send" : ["balance", "left"]
                            },
                            { # right
                                "path" : "right",
                                "name" : "Balance right",
                                "icon" : "icon_arrow_right",
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
                                "icon" : "icon_off",
                                "send" : ["sdirect", "off"]
                            },
                            { # on
                                "path" : "on",
                                "name" : "S.Direct On",
                                "icon" : "icon_on",
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
                                "icon" : "icon_off",
                                "send" : ["sdb", "off"]
                            },
                            { # on
                                "path" : "on",
                                "name" : "SDB On",
                                "icon" : "icon_on",
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
    
    if "icon" in entry:
        icon_file = os.path.join(addon_dir, "resources", "assets", entry["icon"] + ".png")
    else:
        icon_file = None

    li = xbmcgui.ListItem(label, iconImage=icon_file)

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
