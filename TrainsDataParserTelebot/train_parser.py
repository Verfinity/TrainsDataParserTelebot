from project_data_loader import ProjectDataLoader
from fake_useragent import FakeUserAgent
import requests
from bs4 import BeautifulSoup
from exceptions import *


class TrainParser:
    def __init__(self):
        self.__base_url = ProjectDataLoader.get_project_data()['train_data_parse_path']

    def __clear_time_str(self, time_str) -> str:
        cleaned_str = ''.join(char for char in time_str if char != '\r' and char != '\n' and char != ' ')
        return cleaned_str

    def __get_train_container(self, from_city: str, to_city: str, date: str, train_number: str) -> BeautifulSoup:
        user_agent = FakeUserAgent()
        headers = {
            'User-Agent': user_agent.random
        }
        request_url = f"{self.__base_url}/?from={from_city}&to={to_city}&date={date}"

        response = requests.get(request_url, headers=headers)
        if response.status_code != 200:
            raise BadRequestException
        soup = BeautifulSoup(response.text, 'lxml')

        trains_container = soup.find('div', class_='sch-table__body js-sort-body')
        if trains_container is None:
            raise IncorrectRequestDataException

        current_train = trains_container.find('div', class_='sch-table__row', attrs={'data-train-number': train_number})
        if current_train is None:
            raise IncorrectTrainNumberException

        return current_train

    def get_train_info(self, from_city: str, to_city: str, date: str, train_number: str) -> dict:
        current_train = self.__get_train_container(from_city, to_city, date, train_number)

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

        train_info = {
            'train_number': train_number,
            'from_time': self.__clear_time_str(from_time),
            'from_city': from_city,
            'to_time': self.__clear_time_str(to_time),
            'to_city': to_city,
            'train_duration': train_duration,
            'have_places': have_places
        }
        return train_info
