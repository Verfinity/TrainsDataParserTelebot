from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from Exceptions.exceptions import *
from Parsers.train_parser import TrainParser
from Serializers.train_request_info_serializer import TrainRequestInfoSerializer
from TrainInfo.train_request_info import TrainRequestInfo
from TrainInfo.train_full_info import TrainFullInfo


router = Router()
scheduler = AsyncIOScheduler()


async def send_exception(message: Message, exception_text: str) -> None:
    await message.answer(f"Ошибка: {exception_text}")


async def send_train_full_info(message: Message, full_train_info: TrainFullInfo) -> None:
    send_str = f"""Номер поезда: {full_train_info.train_number}\n
Отправление: {full_train_info.from_city}, {full_train_info.from_time}\n
Прибытие: {full_train_info.to_city}, {full_train_info.to_time}\n
Время поездки: {full_train_info.train_duration}\n
Наличие мест: {'Есть' if full_train_info.have_places else 'Нет'}"""
    await message.answer(send_str)


async def remove_train(message: Message, state: FSMContext, train_index: int) -> None:
    trains_list = await get_trains_list(state)

    try:
        trains_list.pop(train_index)
        await state.update_data(trains_list=trains_list)
        await message.answer('Поезд успешно удалён')

        if len(trains_list) == 0:
            await stop_check_trains(message, state)
    except IndexError:
        await message.answer('Поезда с таким номером нет в списке')


async def remove_schedule_job(state: FSMContext) -> None:
    state_data = await state.get_data()
    try:
        schedule_job_id = state_data['schedule_job_id']
        scheduler.remove_job(schedule_job_id)
    except KeyError:
        pass


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    hello_message = """
Этот бот создан для автоматической проверки наличия билетов на поезда белорусской железной дороги.
    
Вот основные комманды:
/add - добавить поезд в список.
Синтаксис: /add *Откуда* *Куда* *Дата в формате гггг-мм-дд* *Номер поезда*
    
/list - получить список поездов
    
/remove - удалить поезд из списка
Синтаксис: /remove *Номер поезда в списке*
    
/start_check - запустить автоматическую проверку списка
Синтаксис: /start_check *Интервал проверки в минутах (не менее 30)*
    
/stop_check - отключить автоматическую проверку списка
    """
    await message.answer(hello_message)


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
    # Train request info format: from_city, to_city, date, train_number

    train_request_info_list = message.text.split()[1::]
    if len(train_request_info_list) != 4:
        await send_exception(message, 'Неверное количество данных')
        return

    try:
        train_parser = TrainParser()
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

    await message.answer('Проверка списка поездов:')
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
            await message.answer('Данные поезда устарели')
            await remove_train(message, state, index)


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

    await remove_train(message, state, remove_train_id)


@router.message(Command('start_check'))
async def start_check_trains(message: Message, state: FSMContext) -> None:
    trains_list = await get_trains_list(state)

    if len(trains_list) == 0:
        await message.answer('Список поездов пуст')
        return

    message_data = message.text.split()

    if len(message_data) != 2:
        await message.answer('Некорректный формат запроса')
        return

    interval = None
    try:
        interval = int(message_data[1])
    except ValueError:
        await message.answer('Необходимо ввести число')
        return

    if interval < 30:
        await message.answer('Количество минут не может быть менее 30')
        return

    await remove_schedule_job(state)

    schedule_job_id = scheduler.add_job(show_list, 'interval', minutes=interval, args=[message, state]).id
    await state.update_data(schedule_job_id=schedule_job_id)
    await message.answer('Автоматическая проверка списка поездов запущена')


@router.message(Command('stop_check'))
async def stop_check_trains(message: Message, state: FSMContext) -> None:
    await remove_schedule_job(state)
    await message.answer('Автоматическая проверка списка поездов остановлена')
