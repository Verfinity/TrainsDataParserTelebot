from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from exceptions import *
from train_parser import TrainParser
from train_request_info_serializer import TrainRequestInfoSerializer
from train_request_info import TrainRequestInfo


router = Router()


async def send_exception(message: Message, exception_text: str) -> None:
    await message.answer(f"Ошибка: {exception_text}")


async def send_train_full_info(message: Message, full_train_info: dict) -> None:
    send_str = f"""Номер поезда: {full_train_info['train-number']}\n
Отправление: {full_train_info['from-city']}, {full_train_info['from-time']}\n
Прибытие: {full_train_info['to-city']}, {full_train_info['to-time']}\n
Время поездки: {full_train_info['train-duration']}\n
Наличие мест: {'Есть' if full_train_info['have-places'] else 'Нет'}"""
    await message.answer(send_str)


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer("Hello there!")


async def get_trains_list(state: FSMContext) -> list:
    state_data = await state.get_data()
    trains_list = list()
    try:
        trains_list = state_data['trains_list']
    except KeyError:
        pass

    return trains_list


@router.message(Command('add'))
async def command_add(message: Message, state: FSMContext) -> None:
    # Train info format: from_city, to_city, date, train_number

    train_request_info_list = message.text.split()[1::]
    if len(train_request_info_list) != 4:
        await send_exception(message, 'Неверное количество данных')
        return

    train_parser = TrainParser()
    try:
        await message.answer('Отправка запроса...')
        train_request_info = TrainRequestInfo(train_request_info_list[0], train_request_info_list[1], train_request_info_list[2], train_request_info_list[3])
        train_full_info = await train_parser.get_train_full_info(train_request_info)

        trains_list = await get_trains_list(state)
        trains_list.append(TrainRequestInfoSerializer.serialize(train_request_info))
        await state.update_data(trains_list=trains_list)
        await message.answer('Поезд добавлен в список проверок')

        await send_train_full_info(message, train_full_info)
    except BadRequestException:
        await send_exception(message, 'Не удалось обратиться к сайту')
    except IncorrectRequestDataException:
        await send_exception(message, 'Неправильный формат данных')
    except IncorrectTrainNumberException:
        await send_exception(message, 'Не удалось найти поезд с данных номером')


@router.message(Command('list'))
async def show_list(message: Message, state: FSMContext) -> None:
    trains_list = await get_trains_list(state)

    if len(trains_list) == 0:
        await message.answer('Список поездов пуст')
        return

    for index, train in enumerate(trains_list):
        try:
            await message.answer('Отправка запроса...')
            train_parser = TrainParser()
            train_request_info = TrainRequestInfoSerializer.deserialize(train)
            train_full_info = await train_parser.get_train_full_info(train_request_info)

            await message.answer(f'Номер поезда в списке: {index}')
            await send_train_full_info(message, train_full_info)
        except BadRequestException:
            await message.answer('Не удалось обратиться к сайту')
            break
        except:
            await message.answer(f'Номер поезда в списке: {index}')
            await message.answer('Данные поезда устарели, поезд удалён из списка')


@router.message(Command('remove'))
async def remove_train_from_list(message: Message, state: FSMContext) -> None:
    trains_list = await get_trains_list(state)

    if len(trains_list) == 0:
        await message.answer('Список поездов пуст')
        return

    message_data = message.text.split()
    if len(message_data) != 2:
        await message.answer('Некорректный формат запроса')
        return

    remove_train_id = None
    try:
        remove_train_id = int(message_data[1])
    except ValueError:
        await message.answer('Необходимо ввести числовой номер')
        return

    try:
        trains_list.pop(remove_train_id)
        await state.update_data(trains_list=trains_list)
        await message.answer('Поезд успешно удалён')
    except IndexError:
        await message.answer('Поезда с таким номером нет в списке')
