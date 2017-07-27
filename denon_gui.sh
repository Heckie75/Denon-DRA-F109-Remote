#!/bin/bash
DIR="$(dirname "$0")"
DENON="ssh 192.168.178.28 $HOME/bin/denon.py"
ME="$DIR/denon_cli.sh"
ICON="$HOME/opt/denon.png"

command=""
hold=""

function ask_command() {

  c=`zenity \
  --title="DENON DRA-F109 Remote Control"\
  --text="Please select command:" \
  --width=640 \
  --height=480 \
  --list \
  --column="Command" \
  --column="Description" \
    "vol"            "Volume"\
    "mute"           "Mute"\
    "fm"             "FM"\
    "cd"             "CD (Coax. digital in)"\
    "net"            "Network (Coax. digital in)"\
    "optical"        "Optical digital in"\
    "off"            "Turn Off"\
    "preset +"       "Preset next"\
    "preset -"       "Preset prev"\
    "macro preset"   "Preset station"\
    "mode"           "FM-Stereo/Mono"\
    "sdirect"        "S.Direct"\
    "sdb"            "SDB"\
    "sleep"          "Sleep"\
    "alarm"          "Activate/deactivate alarm"\
    "set-alarm"      "Alarm Set"\
    "info"           "Info"\
    "dimmer"         "Dimmer"`  
  echo $c
}

function ask_volume() {
  
  text="Set volume"
  min=0
  max=25
  step=1
  default=10
  
  h=`zenity --scale --width=640 --height=480 --title="Select" --text="$text" --value=$default --min-value=$min --max-value=$max --step=$step`
  
  echo $h
}

function ask_preset() {
  
  text="Select preset"
  min=1
  max=49
  step=1
  default=15
  
  h=`zenity --scale --width=640 --height=480 --title="Select" --text="$text" --value=$default --min-value=$min --max-value=$max --step=$step`
  
  echo $h
}

function ask_options() {
 o=`zenity \
  --title="DENON DRA-F109 Remote Control"\
  --text="Please select:" \
  --width=240 \
  --height=240 \
  --list \
  --column="Option" \
    $@`
  
  echo $o
}

function ask_sleep() {
  
  text="Set sleep timer in minutes"
  min=1
  max=255
  step=1
  default=30
  
  h=`zenity --scale --width=640 --height=480 --title="Select" --text="$text" --value=$default --min-value=$min --max-value=$max --step=$step`
  
  echo $h
}



function ask_schedule() {
  text="Please enter time (hh:mm) or schedule in minutes"
  s=`zenity --entry --title="Schedule timer" --text="$text"`
  
  echo $s
}

if [ "$DISPLAY" == "" ]
then
  $DENON  $@
  exit $?
fi

# command
command=$1
shift
if [ "$command" == "" ]
then
  command=`ask_command`
  if [ "$command" == "" ]
  then
    exit 1
  fi
fi

# on/off
case "$command" in 
  "sdirect" | "sdb" | "mute" )
    param=$1
    shift
    
    if [ "$param" == "" ]
    then
      param=`ask_options on off`
      if [ "$param" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# Dimmer
case "$command" in 
  "dimmer" )
    param=$1
    shift
    
    if [ "$param" == "" ]
    then
      param=`ask_options high normal low off`
      if [ "$param" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# Alarm
case "$command" in 
  "alarm" )
    param=$1
    shift
    
    if [ "$param" == "" ]
    then
      param=`ask_options on everyday once off`
      if [ "$param" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# Set-alarm
case "$command" in 
  "set-alarm" )
    atype=$1
    shift
    
    if [ "$atype" == "" ]
    then
      atype=`ask_options everyday once`
      if [ "$atype" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# alarm start time
case "$command" in
  "set-alarm" )
    start=$1
    shift

    if [ "$start" == "" ]
    then
      start=`ask_schedule $command`
      if [ "$start" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# alarm stop time
case "$command" in
  "set-alarm" )
    stop=$1
    shift

    if [ "$stop" == "" ]
    then
      stop=`ask_schedule $command`
      if [ "$stop" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# alarm source
source=""
case "$command" in
  "set-alarm" )
    source=$1
    shift

    if [ "$source" == "" ]
    then
      source=`ask_options analog1 analog2 optical net cd preset`
      if [ "$source" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# Volume
case "$command" in 
  "vol" )
    param=$1
    shift
    
    if [ "$param" == "" ]
    then
      param=`ask_volume $command`
      if [ "$param" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# Preset
case "${command}${source}" in 
  "macro preset" | "set-alarmpreset" )
    param=$1
    shift
    
    if [ "$param" == "" ]
    then
      param=`ask_preset`
      if [ "$param" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# Sleep
case "$command" in 
  "sleep" )
    param=$1
    shift
    
    if [ "$param" == "" ]
    then
      param=`ask_sleep`
      if [ "$param" == "" ]
      then
        exit 1
      fi
    fi
  ;;
esac

# execute
param="$atype $start $stop $source$param"
$DENON $command $param & notify-send -i $ICON "DENON Remote Control" "$command $param"

