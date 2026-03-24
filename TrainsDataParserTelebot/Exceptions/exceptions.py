class GetTrainDataException(Exception):
    pass

class IncorrectRequestDataException(GetTrainDataException):
    pass

class IncorrectTrainNumberException(GetTrainDataException):
    pass

class BadRequestException(Exception):
    pass
