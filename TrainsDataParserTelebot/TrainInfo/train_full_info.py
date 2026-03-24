class TrainFullInfo:
    def __init__(self, train_number: str, date: str, from_time: str, from_city: str, to_time: str, to_city: str, train_duration: str, have_places: bool):
        self.train_number = train_number
        self.date = date
        self.from_time = from_time
        self.from_city = from_city
        self.to_time = to_time
        self.to_city = to_city
        self.train_duration = train_duration
        self.have_places = have_places
