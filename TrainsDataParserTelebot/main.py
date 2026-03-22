from exceptions import *
from train_parser import TrainParser
import asyncio


async def main():
    train_parser = TrainParser()
    try:
        print(await train_parser.get_train_info('Гомель', 'Минск', '2026-03-29', '749Б'))
    except IncorrectRequestDataException:
        print('IncorrectRequestDataException')
    except IncorrectTrainNumberException:
        print('IncorrectTrainNumberException')

if __name__ == '__main__':
    asyncio.run(main())
