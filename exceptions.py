class MessageError(Exception):
    """
    Error during sending the message to Telegram user.
    """
    def __init__(self, error):
        self.error = error
        self.message = f'Message was not send to the user: {error}'.format(
            self.error
        )
        super().__init__(self.message)


class APIResponseError(Exception):
    """
    Error during requesting the API server.
    """
    def __init__(self, error):
        self.error = error
        self.message = f'Request to API server failed: {error}'.format(
            self.error
        )
        super().__init__(self.message)
