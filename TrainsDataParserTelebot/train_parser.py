from fake_useragent import FakeUserAgent
from bs4 import BeautifulSoup
from bs4 import Tag
from exceptions import *
from dotenv import load_dotenv
from os import getenv
import aiohttp

from train_request_info import TrainRequestInfo
from train_full_info import TrainFullInfo


class TrainParser:
    def __init__(self):
        load_dotenv()
        self.__base_url = getenv('TRAIN_DATA_PARSE_PATH')

    def __clear_time_str(self, time_str) -> str:
        cleaned_str = ''.join(char for char in time_str if char != '\r' and char != '\n' and char != ' ')
        return cleaned_str

    async def __get_train_container(self, train_request_info: TrainRequestInfo) -> Tag:
        user_agent = FakeUserAgent()
        headers = {
            'User-Agent': user_agent.random
        }
        request_url = f"{self.__base_url}/?from={train_request_info.from_city}&to={train_request_info.to_city}&date={train_request_info.date}"

        response_text = ''
        async with aiohttp.ClientSession() as session:
            async with session.get(url=request_url, headers=headers) as response:
                if response.status != 200:
                    raise BadRequestException
                response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')

        trains_container = soup.find('div', class_='sch-table__body js-sort-body')
        if trains_container is None:
            raise IncorrectRequestDataException

        current_train = trains_container.find('div', class_='sch-table__row', attrs={'data-train-number': train_request_info.train_number})
        if current_train is None:
            raise IncorrectTrainNumberException

        return current_train

    async def get_train_full_info(self, train_request_info: TrainRequestInfo) -> TrainFullInfo:
        current_train = await self.__get_train_container(train_request_info)

        train_info_container = current_train.find('div', class_='sch-table__row_2')

        from_time = train_info_container.find('div', class_='sch-table__time train-from-time').text
        from_city = train_info_container.find('div', class_='sch-table__station train-from-name').text

        to_time = train_info_container.find('div', class_='sch-table__time train-to-time').text
        to_city = train_info_container.find('div', class_='sch-table__station train-to-name').text

        train_duration = train_info_container.find('div', class_='sch-table__duration visible-xs').find('span').text

        have_no_places_div = current_train.find('div', class_='sch-table__no-info')
        have_places = True
        if have_no_places_div:
            have_places = False

        train_full_info = TrainFullInfo(
            train_number=train_request_info.train_number,
            from_time=self.__clear_time_str(from_time),
            from_city=from_city,
            to_time=self.__clear_time_str(to_time),
            to_city=to_city,
            train_duration=train_duration,
            have_places=have_places)
        return train_full_info
