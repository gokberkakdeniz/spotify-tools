# spotify-tools
A collection of command line applications related to Spotify. It can control player, observe player for changes, search on playlists, be used as custom polybar module...

## Table of **Contents**
- Tools
    - control
    - info
        - Format Language
        - Variables (Metadata values)
        - Functions
        - Example
    - search
- Polybar Example
- Installation
    - Dependencies
## Tools
### control
    usage: spotifyctl control [-h] [-s VOLUME | -m | -u | -t | -i [INCREMENT] | -d
                              [DECREMENT]] [-l | -a | -P | -n | -p] [--debug]
    
    optional arguments:
      -h, --help            show this help message and exit
      --debug               shows error messages
    
    volume controller:
      -s VOLUME, --set-volume VOLUME
                            set volume to VOLUME (where VOLUME is integer and on
                            interval [0,100])
      -m, --mute            mute spotify
      -u, --unmute          unmute spotify
      -t, --toggle-volume   mute/unmute spotify
      -i [INCREMENT], --increase-volume [INCREMENT]
                            increase volume by INCREMENT (default: 5)
      -d [DECREMENT], --decrease-volume [DECREMENT]
                            decrease volume by DECREMENT (default: 5)
    
    playback controller:
      -l, --play            starts or resumes playback
      -a, --pause           pauses playback
      -P, --play-pause      if playback is already paused, resumes playback
                            otherwise, starts playback
      -n, --next            skips to the next track in the tracklist
      -p, --previous        skips to the previous track in the tracklist
    
### info
    usage: spotifyctl info [-h] [-t N] [--play-indicator ICON]
                           [--pause-indicator ICON] [-f FORMAT] [-O] [--debug]
    
    optional arguments:
      -h, --help            show this help message and exit
      -t N, --truncation-length N
                            truncate output after it reaches N characters
      --play-indicator ICON
                            an icon to show while playing
      --pause-indicator ICON
                            an icon to show when paused
      -f FORMAT, --format FORMAT
                            an output format.
      -O, --observe         observe player state
      --debug               shows error messages

#### Format Language
##### Variables (Metadata values)
- $artist _artist name_
- $title _track title_
- $clean_title _track title without remastered, spotify session etc._
- $status _playback status_
- $volume _volume_
- $icon _playback status icon_
- $album _album name_
- $trackid _track id_
- $length _track length_
- $art_url _artwork url_
- $album_artist _album artist name_
- $auto_rating _auto rating_
- $disc_number _disc number_
- $track_number _track number_
- $url _url_

##### Functions
Syntax: `{some expression| @Function1 'arg1' 'arg2'... @Function2 'arg1' 'arg2'...}`
- @IfNotNone 'variable name' _If variable is not None, shows group. Otherwise, doesn't._
- @Truncate 'length' _Truncates the group to given length._

##### Example
Default format: `$icon $artist — $clean_title{ // ${volume}%| @IfNotNone 'volume'}`

- First start up ($volume is None): ` Ashbury — Madman`
- After first play/pause: ` Ashbury — Madman // 63%`

### search
    Not yet.
<!-- TO DO: integrate soapify package. ->

## Polybar Example
`module/spotify` starts an _UNIX Socket_ server and updates playback information whenever volume or track change.
`module/previous` and `module/next` connect this server and show given formatted text if there is playback information.

__Memory Usage:__ 
- Server: ~30MiB
- Client: ~15MiB

__Note:__ Be sure that there should be only one observer script running.

### Playback Status
    [module/spotify]
      type = custom/script
      tail = true
      interval = 0
      exec = spotifyctl.py info -O
    
      format = <label>
      label = %output%
      
      click-left = spotifyctl.py control -P
      click-right = if [[ $(xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) WM_CLASS) == *"spotify"* ]]; then xdotool getactivewindow windowminimize; else wmctrl -x -a spotify.Spotify; fi
      scroll-up = spotifyctl.py control -i
      scroll-down = spotifyctl.py control -d

### Previous Button
    [module/previous]
      type = custom/script
      tail = true
      interval = 0
      exec = python3 -u spotifyctl.py info -f ""
    
      format = <label>
      label = %output%
    
      click-left = spotifyctl.py control -p

__Note:__ Siji font required to see .

### Next Button
    [module/next]
      type = custom/script
      tail = true
      interval = 0
      exec = python3 -u spotifyctl.py info -f ""
    
      format = <label>
      label = %output%
    
      click-left = spotifyctl.py control -n

__Note:__ Siji font required.

## Installation
<!-- TO DO: PyPi release -->
    
### Dependencies
Python 3:
- pulsectl
- lark

Distro specific dependencies:
- Fedora:
    - dbus-devel (?)
    - pygobject3 python3-gobject