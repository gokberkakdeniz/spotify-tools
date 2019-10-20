from lib.plugin import SpotifyCtlPlugin


class Info(SpotifyCtlPlugin):
    def __init__(self, subparsers):
        subparser = subparsers.add_parser(
            "info",
            help="shows metadata, volume etc."
        )

        subparser.add_argument(
            "-t", "--truncation-length",
            type=int, default=72, metavar="N",
            dest="truncation_length", help="truncate output after it reaches N characters"
        )
        subparser.add_argument(
            "--play-indicator",
            type=str, default=chr(0xe099), metavar="ICON",
            dest="play_indicator", help="an icon to show while playing"
        )
        subparser.add_argument(
            "--pause-indicator",
            type=str, default=chr(0xe058), metavar="ICON",
            dest="pause_indicator", help="an icon to show when paused"
        )
        subparser.add_argument(
            "-f", "--format",
            type=str, default="$icon $artist — $clean_title{ // ${volume}%| @IfNotNone 'volume'}", metavar="FORMAT",
            dest="format", help="an output format. "  # TODO: add doc
        )
        subparser.add_argument(
            "-O", "--observe",
            action="store_true",
            dest="observe", help="observe player state"
        )

        subparser.add_argument(
            "--debug",
            action="store_true", dest="debug",
            help="shows error messages"
        )

        self._parser = subparser

    def _format(self, formatter, clean_title, format_, play_indicator, pause_indicator, player_state):
        if player_state is None or player_state.status == "" or format_ == "":
            return ""

        functions = {
            "@IfNotNone": lambda content, args_: "" if variables.get(args_[0], None) is None else content,
            "@Truncate": lambda content, args_: content[:args_[0]]
        }

        variables = {
            "trackid": player_state.metadata.trackid,
            "length": player_state.metadata.length,
            "art_url": player_state.metadata.art_url,
            "album": player_state.metadata.album,
            "album_artist": player_state.metadata.album_artist[0],
            "artist": player_state.metadata.artist[0],
            "auto_rating": player_state.metadata.auto_rating,
            "disc_number": player_state.metadata.disc_number,
            "title": player_state.metadata.title,
            "clean_title": clean_title(player_state.metadata.title),
            "track_number": player_state.metadata.track_number,
            "url": player_state.metadata.url,
            "status": player_state.status,
            "volume": player_state.volume,
            "icon": (play_indicator if player_state.status == "Playing" else
                     pause_indicator if player_state.status == "Paused" else
                     "")
        }

        return formatter.format(format_, variables, functions)

    def print_player_state(self, formatter, clean_title, args, player_state):
        result = self._format(formatter, clean_title, args.format, args.play_indicator, args.pause_indicator, player_state)
        if not args.format == "":
            print(result)

    def run(self, args):
        from lib.title import clean as clean_title
        from lib.xformat import XFormat
        from lib.exceptions import PlayerStateServerIsAlreadyRunningError, PlayerStateServerIsNotRunning, SpotifyIsNotRunningError
        formatter = XFormat()

        if args.observe:
            try:
                from lib.ipc import PlayerStateServer
                from lib.player import PlayerObserver

                observer = PlayerObserver()
                server = PlayerStateServer()

                def callback(player_state):
                    self.print_player_state(formatter, clean_title, args, player_state)
                    server.send(player_state)

                observer.set_callback(callback)

                observer.start()
            except PlayerStateServerIsAlreadyRunningError as err:
                print("error:", err.message)
            except Exception as err:
                if args.debug:
                    print(err)
        else:
            try:
                from lib.ipc import PlayerStateReceiver

                receiver = PlayerStateReceiver()
                receiver.start(lambda player_state: self.print_player_state(formatter, clean_title, args, player_state))
            except PlayerStateServerIsNotRunning:
                from lib.player import PlayerController

                try:
                    player = PlayerController()
                    self.print_player_state(formatter, clean_title, args, player.get_player_state())
                except Exception as err:
                    if args.debug:
                        print(err)
            except Exception as err:
                if args.debug:
                    print(err)
