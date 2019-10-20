from gi.repository import Gio, GLib
from .pulseaudio import PulseAudioController
from .playerinfo import PlayerState, Metadata
from .exceptions import SpotifyIsNotRunningError


class PlayerController:
    def __init__(self):
        from .dbus import SpotifyDBus
        self._pulseaudio_controller = PulseAudioController()
        self._dbus_controller = SpotifyDBus()

    def mute(self):
        self._pulseaudio_controller.mute()

    def unmute(self):
        self._pulseaudio_controller.unmute()

    def get_volume(self):
        return self._pulseaudio_controller.get_volume()

    def decrease_volume(self, number):
        self._pulseaudio_controller.decrease_volume(number)

    def increase_volume(self, number):
        self._pulseaudio_controller.increase_volume(number)

    def set_volume(self, volume):
        self._pulseaudio_controller.set_volume(volume)

    def mute_unmute(self):
        self._pulseaudio_controller.mute_unmute()

    def next(self):
        self._dbus_controller.next()

    def previous(self):
        self._dbus_controller.previous()

    def play(self):
        self._dbus_controller.play()

    def pause(self):
        self._dbus_controller.pause()

    def play_pause(self):
        self._dbus_controller.play_pause()

    def stop(self):
        self._dbus_controller.stop()

    def open_uri(self, uri):
        self._dbus_controller.open_uri(uri)

    def get_metadata(self):
        return self._dbus_controller.get_metadata()

    def get_playback_status(self):
        return self._dbus_controller.get_playback_status()

    def get_player_state(self):
        return PlayerState(
            self.get_metadata(),
            self.get_playback_status(),
            self.get_volume()
        )


class PlayerObserver:
    def __init__(self):
        self._bus = Gio.bus_get_sync(
            Gio.BusType.SESSION,
            None
        )

        self._pulseaudio = PulseAudioController()
        self._callback = lambda player_state: print(player_state)
        self._player_state = PlayerState()

        self._signal_properties_changed = None
        self._signal_name_owner_changed = None

    def start(self):
        self._subscribe_name_owner_changed_signal()

        if self._is_spotify_already_opened():
            self._subscribe_properties_changed_signal()
            self._update_player_state_manually()
            self._callback(self._player_state)

        loop = GLib.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            self.__del__()

    def set_callback(self, callback):
        if not hasattr(callback, "__call__"):
            raise TypeError("callback should be function.")

        self._callback = callback

    def _create_player_state(self, metadata, playback_status, volume):
        state = PlayerState(
            Metadata(
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
            ),
            playback_status,
            volume
        )
        return state

    def _is_spotify_already_opened(self):
        return self._bus.call_sync(
            "org.freedesktop.DBus",
            "/org/freedesktop/DBus",
            "org.freedesktop.DBus",
            "NameHasOwner",
            GLib.Variant("(s)", ("org.mpris.MediaPlayer2.spotify",)),
            None,
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )[0]

    def _update_player_state_manually(self):
        proxy = Gio.DBusProxy.new_sync(
            self._bus,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.mpris.MediaPlayer2.spotify",
            "/org/mpris/MediaPlayer2",
            "org.mpris.MediaPlayer2.Player",
            None
        )

        metadata = proxy.call_sync(
            "org.freedesktop.DBus.Properties.Get",
            GLib.Variant("(ss)", ("org.mpris.MediaPlayer2.Player", "Metadata")),
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )[0]

        playback_status = proxy.call_sync(
            "org.freedesktop.DBus.Properties.Get",
            GLib.Variant("(ss)", ("org.mpris.MediaPlayer2.Player", "PlaybackStatus")),
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )[0]

        volume = self._pulseaudio.get_volume()

        self._player_state = self._create_player_state(metadata, playback_status, volume)

    def _on_name_owner_changed(self, conn, sender_name, obj_path, int_name, sig_name, parameters, user_data):
        name = parameters[0]
        old_owner = parameters[1]
        new_owner = parameters[2]
        
        if name == "org.mpris.MediaPlayer2.spotify":
            assert old_owner == "" or new_owner == "", "spotify changed its behaviour, fix this."
            
            if old_owner == "":
                self._subscribe_properties_changed_signal()
            elif new_owner == "":
                self._unsubscribe_properties_changed_signal()
                self._player_state = PlayerState()
                self._callback(self._player_state)

    def _on_properties_changed(self, conn, sender_name, obj_path, int_name, sig_name, parameters, user_data):
        metadata = parameters[1]["Metadata"]
        playback_status = parameters[1]["PlaybackStatus"]
        try:
            volume = self._pulseaudio.get_volume()
        except:
            volume = None

        current_player_state = self._create_player_state(metadata, playback_status, volume)
        if not current_player_state == self._player_state:
            self._player_state = current_player_state
            self._callback(self._player_state)

    def _subscribe_name_owner_changed_signal(self):
        self._signal_name_owner_changed = self._bus.signal_subscribe(
            None,
            "org.freedesktop.DBus",
            "NameOwnerChanged",
            "/org/freedesktop/DBus",
            None,
            Gio.DBusSignalFlags.NONE,
            self._on_name_owner_changed,
            None
        )

    def _unsubscribe_name_owner_changed_signal(self):
        if self._signal_name_owner_changed is not None:
            self._bus.signal_unsubscribe(self._signal_name_owner_changed)
            self._signal_name_owner_changed = None

    def _subscribe_properties_changed_signal(self):
        self._signal_properties_changed =  self._bus.signal_subscribe(
            "org.mpris.MediaPlayer2.spotify",
            "org.freedesktop.DBus.Properties",
            "PropertiesChanged",
            "/org/mpris/MediaPlayer2",
            None,
            Gio.DBusSignalFlags.NONE,
            self._on_properties_changed ,
            None
        )

    def _unsubscribe_properties_changed_signal(self):
        if self._signal_properties_changed is not None:
            self._bus.signal_unsubscribe(self._signal_properties_changed)
            self._signal_properties_changed = None

    def __del__(self):
        self._unsubscribe_name_owner_changed_signal()
        self._unsubscribe_properties_changed_signal()
        self._bus.close_sync(None)
