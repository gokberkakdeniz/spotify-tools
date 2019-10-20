from gi.repository import Gio, GLib
from .playerinfo import Metadata
from .exceptions import SpotifyIsNotRunningError


class SpotifyDBus:
    """Sends MPRIS signals to Spotify through DBus

        MPRIS specification: https://specifications.freedesktop.org/mpris-spec/latest/
    """
    def __init__(self):
        self._bus = Gio.bus_get_sync(
            Gio.BusType.SESSION,
            None
        )

        self._proxy = Gio.DBusProxy.new_sync(
            self._bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.mpris.MediaPlayer2.spotify",
            "/org/mpris/MediaPlayer2",
            "org.mpris.MediaPlayer2.Player",
            None
        )

    def play(self):
        self._call_sync("Play")

    def pause(self):
        self._call_sync("Pause")

    def play_pause(self):
        self._call_sync("PlayPause")

    def next(self):
        self._call_sync("Next")

    def previous(self):
        self._call_sync("Previous")

    def stop(self):

        self._call_sync("Stop")

    def open_uri(self, uri):
        self._call_sync(
            "OpenUri",
            GLib.Variant("(s)", (uri,))
        )

    def get_metadata(self):
        metadata = self._call_sync(
            "org.freedesktop.DBus.Properties.Get",
            GLib.Variant("(ss)", ("org.mpris.MediaPlayer2.Player", "Metadata"))
        )[0]

        return Metadata(
            metadata["mpris:trackid"],
            metadata["mpris:length"],
            metadata["mpris:artUrl"],
            metadata["xesam:album"],
            metadata["xesam:albumArtist"],
            metadata["xesam:artist"],
            metadata["xesam:autoRating"],
            metadata["xesam:discNumber"],
            metadata["xesam:title"],
            metadata["xesam:trackNumber"],
            metadata["xesam:url"]
        )
        
    def get_playback_status(self):
        playback_status = self._call_sync(
            "org.freedesktop.DBus.Properties.Get",
            GLib.Variant("(ss)", ("org.mpris.MediaPlayer2.Player", "PlaybackStatus"))
        )[0]

        return playback_status

    def _call_sync(self, method_name, parameters=None):
        try:
            return self._proxy.call_sync(
                method_name,
                parameters,
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )
        except GLib.GError as err:
            if err.domain == "g-dbus-error-quark" and err.code == 2:
                raise SpotifyIsNotRunningError()
            raise err

    def __del__(self):
        self._bus.close_sync(None)