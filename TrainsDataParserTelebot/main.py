from exceptions import *
from train_parser import TrainParser


def main():
    train_parser = TrainParser()

    try:
        result = train_parser.have_places('Гомель', 'Минск', '2026-03-29', '683Б')
        if result:
            print('Места есть')
        else:
            print('Мест нет')
    except IncorrectRequestDataException:
        print('IncorrectRequestDataException')
    except IncorrectTrainNumberException:
        print('IncorrectTrainNumberException')

if __name__ == '__main__':
    main()
