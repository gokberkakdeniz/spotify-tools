import argparse
from lib.plugin import SpotifyCtlPlugin


class Control(SpotifyCtlPlugin):
    def __init__(self, subparsers):
        subparser = subparsers.add_parser(
            "control",
            help="controls player"
        )
        volumectl = subparser.add_argument_group("volume controller").add_mutually_exclusive_group()
        playerctl = subparser.add_argument_group("playback controller").add_mutually_exclusive_group()  
        
        volumectl.add_argument(
            "-s", "--set-volume",
            type=self._volume_type, metavar="VOLUME", dest="volume", 
            help="set volume to VOLUME (where VOLUME is integer and on interval [0,100])"
        )
        volumectl.add_argument(
            "-m", "--mute",
            action="store_true", dest="mute", 
            help="mute spotify"
        )
        volumectl.add_argument(
            "-u", "--unmute",
            action="store_true", dest="unmute", 
            help="unmute spotify"
        )
        volumectl.add_argument(
            "-t", "--toggle-volume",
            action="store_true", dest="mute_unmute", 
            help="mute/unmute spotify"
        )
        volumectl.add_argument(
            "-i", "--increase-volume",
            type=self._volume_type, nargs="?", const=5, metavar="INCREMENT", dest="increment_value",
            help="increase volume by INCREMENT (default: %(const)s)"
        )
        volumectl.add_argument(
            "-d", "--decrease-volume",
            type=self._volume_type, nargs="?", const=5, metavar="DECREMENT", dest="decrement_value",
            help="decrease volume by DECREMENT (default: %(const)s)"
        )

        playerctl.add_argument(
            "-l", "--play",
            action="store_true", dest="play",
            help="starts or resumes playback"
        )
        playerctl.add_argument(
            "-a", "--pause",
            action="store_true", dest="pause",
            help="pauses playback"
        )
        playerctl.add_argument(
            "-P", "--play-pause",
            action="store_true", dest="play_pause",
            help="if playback is already paused, resumes playback\notherwise, starts playback"
        )
        playerctl.add_argument(
            "-n", "--next",
            action="store_true", dest="next",
            help="skips to the next track in the tracklist"
        )
        playerctl.add_argument(
            "-p", "--previous",
            action="store_true", dest="previous",
            help="skips to the previous track in the tracklist"
        )

        subparser.add_argument(
            "--debug",
            action="store_true", dest="debug",
            help="shows error messages"
        )
        self._parser = subparser

    def _volume_type(self, number):
        try:
            number = int(number)
        except Exception:
            raise argparse.ArgumentTypeError("VOLUME should be integer.")

        if not 0 <= number <= 100:
            raise argparse.ArgumentTypeError("VOLUME should be between 0 and 100 (inclusive).")

        return number

    def run(self, args):
        try:
            from lib.player import PlayerController
            player = PlayerController()
            if args.mute:
                player.mute()
            elif args.unmute:
                player.unmute()
            elif args.mute_unmute:
                player.mute_unmute()
            elif args.volume is not None:
                player.set_volume(args.volume)
            elif args.increment_value is not None:
                player.increase_volume(args.increment_value)
            elif args.decrement_value is not None:
                player.decrease_volume(args.decrement_value)
            elif args.play:
                player.play()
            elif args.pause:
                player.pause()
            elif args.play_pause:
                player.play_pause()
            elif args.next:
                player.next()
            elif args.previous:
                player.previous()
            else:
                self._parser.print_usage()
        except Exception as err:
            if args.debug:
                print(err)
