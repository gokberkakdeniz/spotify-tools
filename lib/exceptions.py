class PlayerStateServerIsAlreadyRunningError(Exception):
    message = "player state server is already running. multiple server is not allowed."

    def __str__(self):
        return self.message


class SpotifyIsNotRunningError(Exception):
    message = "spotify is not running."

    def __str__(self):
        return self.message


class PlayerStateServerIsNotRunning(Exception):
    message = "player state server is not running."

    def __str__(self):
        return self.message
