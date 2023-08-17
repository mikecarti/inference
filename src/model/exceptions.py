class CustomException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InvalidAnswerException(BaseException):
    pass


class UserExistsException(BaseException):
    pass


class InvalidMessageTypeException(BaseException):
    pass


class MessageQueueEmptyException(BaseException):
    pass


class LimitExceededException(BaseException):
    pass


class UnknownIntentException(BaseException):
    pass
