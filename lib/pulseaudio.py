import pulsectl
from .exceptions import SpotifyIsNotRunningError


def _updatesink(method):
    def new_method(*args):
        self = args[0]
        
        self._spotify_sink_input = None
        for sink_input in self._pulse.sink_input_list():
            if sink_input.name == "Spotify":
                self._spotify_sink_input = sink_input
                break

        if self._spotify_sink_input is None:
            raise SpotifyIsNotRunningError()

        return method(*args)

    return new_method


class PulseAudioController:
    def __init__(self):
        self._pulse = pulsectl.Pulse('spotifyctl')
        self._spotify_sink_input = None

    @_updatesink
    def set_volume(self, volume) -> None:
        spotify_volume = self._spotify_sink_input.volume
        spotify_volume.value_flat = self._fix_volume(volume)
        self._pulse.volume_set(self._spotify_sink_input, spotify_volume)

    @_updatesink
    def get_volume(self):
        try:  # when you open spotify, you should play track to make spotify connect to pulseaudio.
            return round(self._spotify_sink_input.volume.value_flat * 100)
        except SpotifyIsNotRunningError:
            return None

    @_updatesink
    def mute(self):
        self._pulse.mute(self._spotify_sink_input, True)

    @_updatesink
    def unmute(self):
        self._pulse.mute(self._spotify_sink_input, False)

    @_updatesink
    def mute_unmute(self):
        self._pulse.mute(self._spotify_sink_input, self._spotify_sink_input.mute == 0)

    def increase_volume(self, number):
        self.set_volume(self.get_volume() + number)

    def decrease_volume(self, number):
        self.set_volume(self.get_volume() - number)

    def _fix_volume(self, volume):
        return (
            0 if volume < 0 else
            volume if volume < 100 else
            100
        ) / 100

    def __del__(self):
        self._pulse.disconnect()
