from project_data_loader import ProjectDataLoader
from fake_useragent import FakeUserAgent
import requests
from bs4 import BeautifulSoup
from exceptions import *


class TrainParser:
    def __init__(self):
        self.__base_url = ProjectDataLoader.get_project_data()['train_data_parse_path']

    def have_places(self, from_city: str, to_city: str, date: str, train_number: str) -> bool:
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

        have_no_places_div = current_train.find('div', class_='sch-table__no-info')
        if have_no_places_div:
            return False
        return True
