from train_request_info import TrainRequestInfo


class TrainRequestInfoSerializer:
    @staticmethod
    def serialize(train_request_info: TrainRequestInfo) -> str:
        serialized_info = f"{train_request_info.from_city}, {train_request_info.to_city}, {train_request_info.date}, {train_request_info.train_number}"
        return serialized_info

    @staticmethod
    def deserialize(serialized_str: str) -> TrainRequestInfo:
        info = serialized_str.split(', ')
        train_info = TrainRequestInfo(info[0], info[1], info[2], info[3])
        return train_info
