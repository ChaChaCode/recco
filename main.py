import os
import logging
import importlib.util
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import exceptions as aiogram_exceptions
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telegraph import Telegraph, exceptions as telegraph_exceptions
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound
import re

class TestState(StatesGroup):
    choosing_test = State()  # Выбор теста
    answering_question = State()  # Ответ на вопросы
    test_completed = State()  # Тест завершен

# Инициализируем объект Telegraph
telegraph = Telegraph()
telegraph.create_account(short_name='aiogram_bot')  # Создаем аккаунт на Telegraph

# Initialize memory storage
storage = MemoryStorage()
# Инициализация асинхронной блокировки
lock = asyncio.Lock()
# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token="7126363612:AAG1pIZWRSrWdOHKCHkglUQ_8U1YmK5qaKw")
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Словарь для хранения результатов тестов
test_results = {}
previous_questions = {}
# Словарь для хранения названия текущего теста для каждого пользователя
current_test_names = {}

#@dp.message_handler(commands=['otchetall'])
@dp.message_handler(commands=['otchetall'])
async def view_all_reports(message: types.Message):
    # Проверяем, является ли отправитель администратором (можно изменить логику для проверки прав доступа)
    if message.from_user.id == YOUR_ADMIN_USER_ID:  # Замените YOUR_ADMIN_USER_ID на реальный ID администратора
        # Получаем список всех пользователей
        all_users = os.listdir(REPORTS_FOLDER)

        # Создаем сообщение с отчетами для каждого пользователя
        all_reports_text = "Отчеты по пользователям:\n\n"
        for user_folder in all_users:
            user_reports_folder = os.path.join(REPORTS_FOLDER, user_folder)
            user_reports = os.listdir(user_reports_folder)
            if user_reports:
                user_report_text = f"Пользователь: {user_folder}\n"
                for report in user_reports:
                    if '_link.txt' in report:
                        with open(os.path.join(user_reports_folder, report), 'r') as file:
                            url = file.read().strip()
                            report_name = report.replace('_link.txt', '')
                            user_report_text += f"- {report_name}: {url}\n"
                all_reports_text += user_report_text + "\n"

        # Отправляем сообщение с отчетами администратору
        await bot.send_message(chat_id=message.chat.id, text=all_reports_text)
    else:
        await bot.send_message(chat_id=message.chat.id, text="Извините, у вас нет доступа к этой функции.")


# Константа для папки с отчетами
REPORTS_FOLDER = "reports"

# Замените YOUR_ADMIN_USER_ID на реальный ID администратора
YOUR_ADMIN_USER_ID = 5429082466  # Пример: 123456789


# Функция импорта модуля вопросов
def import_question_module(module_name):
    current_directory = os.path.dirname(__file__)
    module_path = os.path.join(current_directory, f"{module_name}.py")
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, f"questions_answers_{module_name.replace('questions_', '')}", None)
    except FileNotFoundError:
        logging.error(f"Module {module_name} not found.")
        return None


# Создание кнопок для выбора тестов с маленькими кнопками
start_keyboard = InlineKeyboardMarkup()
question_modules = [
    "pc1_1","pc1_2","pc1_3","pc1_4","pc1_5","pc2_1",
    "pc2_2","pc2_3","pc2_4","pc2_5","pc3_1","pc3_2",
    "pc3_3","pc3_4","pc4_1","pc4_2","pc4_3","pc4_4","pc4_5"
]
row_buttons = []
for index, module_name in enumerate(question_modules, start=1):
    questions_answers = import_question_module(f"questions_{module_name}")
    if questions_answers:
        test_name = module_name.replace("_", ".").replace("pc", "PC ", 1).upper()
        row_buttons.append(InlineKeyboardButton(test_name, callback_data=f"test:questions_{module_name}"))
        if index % 4 == 0 or index == len(question_modules):
            start_keyboard.row(*row_buttons)
            row_buttons = []

# Создание кнопок для подготовки с маленькими кнопками
preparation_keyboard = InlineKeyboardMarkup(row_width=4)

preparation_links = [
    ("PK-1.1", "https://telegra.ph/PK-11-03-12-2"),
    ("PK-1.2", "https://telegra.ph/PK-12-03-12-2"),
    ("PK-1.3", "https://telegra.ph/PK-13-03-12"),
    ("PK-1.4", "https://telegra.ph/PK-14-03-12"),
    ("PK-1.5", "https://telegra.ph/PK-15-03-12"),
    ("PK-2.1", "https://telegra.ph/PK-21-03-12"),
    ("PK-2.2", "https://telegra.ph/PK-22-03-12"),
    ("PK-2.3", "https://telegra.ph/PK-23-03-12"),
    ("PK-2.4", "https://telegra.ph/PK-24-03-12"),
    ("PK-2.5", "https://telegra.ph/PK-25-03-12"),
    ("PK-3.1", "https://telegra.ph/PK-31-03-12"),
    ("PK-3.2", "https://telegra.ph/PK-32-03-12"),
    ("PK-3.3", "https://telegra.ph/PK-33-03-12"),
    ("PK-3.4", "https://telegra.ph/PK-34-03-12"),
    ("PK-4.1", "https://telegra.ph/PK-41-03-12"),
    ("PK-4.2", "https://telegra.ph/PK-42-03-12"),
    ("PK-4.3", "https://telegra.ph/PK-43-03-12"),
    ("PK-4.4", "https://telegra.ph/PK-44-03-12"),
    ("PK-4.5", "https://telegra.ph/PK-45-03-12")
]

row_buttons = []  # Создаем список для хранения кнопок в строке
for index, (link_name, link_url) in enumerate(preparation_links, start=1):
    row_buttons.append(InlineKeyboardButton(link_name, url=link_url))  # Добавляем кнопку в текущую строку
    if index % 4 == 0 or index == len(preparation_links):  # Если достигнуто 4 кнопки или это последняя кнопка
        preparation_keyboard.row(*row_buttons)  # Добавляем текущую строку кнопок к клавиатуре
        row_buttons = []  # Очищаем список для следующей строки

# Добавляем кнопку "назад"
preparation_keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main_menu"))

@dp.callback_query_handler(lambda query: query.data == 'preparation')
async def show_preparation_menu(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id, text="Выберите тестовый линк для подготовки:", reply_markup=preparation_keyboard)
    # Мгновенное удаление свечения кнопки
    await bot.answer_callback_query(callback_query.id, text="", show_alert=True)
@dp.callback_query_handler(lambda query: query.data == 'back_to_main_menu')
async def back_to_main_menu(callback_query: types.CallbackQuery):
    try:
        # Удаляем предыдущее сообщение
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id - 1)
    except MessageToDeleteNotFound:
        pass  # Просто игнорируем ошибку, если сообщение не найдено или уже удалено

    await send_welcome(callback_query.message)
    # Теперь удаляем сообщение с меню подготовки
    try:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    except MessageToDeleteNotFound:
        pass  # Просто игнорируем ошибку, если сообщение не найдено или уже удалено

    await bot.answer_callback_query(callback_query.id, text="", show_alert=True)


async def show_main_menu(callback_query: types.CallbackQuery):
    main_menu_keyboard = InlineKeyboardMarkup(row_width=2)
    main_menu_keyboard.row(
        InlineKeyboardButton("Тесты", callback_data="tests"),
        InlineKeyboardButton("Аккаунт", callback_data="account")
    )
    main_menu_keyboard.row(
        InlineKeyboardButton("Подготовка", callback_data="preparation")
    )
    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,text="Главное меню:", reply_markup=main_menu_keyboard)


# Создание главного меню
main_menu_keyboard = InlineKeyboardMarkup(row_width=2)
main_menu_keyboard.row(InlineKeyboardButton("Тесты", callback_data="tests"), InlineKeyboardButton("Аккаунт", callback_data="account"))
main_menu_keyboard.row(InlineKeyboardButton("Подготовка", callback_data="preparation"))


# Создание кнопки "Меню"
menu_button = KeyboardButton("Меню")

# Создание клавиатуры с кнопкой "Меню"
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(menu_button)


# Обработчик команды /menu
@dp.message_handler(commands=['menu'])
async def return_to_main_menu(message: types.Message):
    global current_test
    await bot.send_message(chat_id=message.chat.id, text="Выбери пункт из меню:", reply_markup=main_menu_keyboard)



# Ваши существующие обработчики

@dp.message_handler(lambda message: message.text == "Меню")
async def return_to_main_menu_keyboard(message: types.Message):
    await return_to_main_menu(message)

# Путь к папке для сохранения отчетов
REPORTS_FOLDER = "reports"

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Изменено с message.reply на bot.send_message и удален reply_to_message_id
    await bot.send_message(chat_id=message.chat.id, text="Привет! Я бот для проверки знаний. Выбери пункт из главного меню:", reply_markup=main_menu_keyboard)


@dp.callback_query_handler(lambda query: query.data == 'tests')
async def show_tests_menu(callback_query: types.CallbackQuery):
    async with lock:  # Используем блокировку здесь
        await bot.send_message(chat_id=callback_query.from_user.id, text="Выбери тест:", reply_markup=start_keyboard)
    # Мгновенное удаление свечения кнопки
    await bot.answer_callback_query(callback_query.id, text="", show_alert=True)


# Обработчик нажатия кнопки "Главное меню"
@dp.callback_query_handler(lambda query: query.data == 'main_menu')
async def return_to_main_menu(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id, text="Выбери пункт из главного меню:", reply_markup=main_menu_keyboard)
    await bot.answer_callback_query(callback_query.id, text="", show_alert=True)

@dp.callback_query_handler(lambda query: query.data.startswith('view_report:'))
async def view_report(callback_query: types.CallbackQuery, state: FSMContext):
    report_name = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    report_path = os.path.join(REPORTS_FOLDER, str(user_id), report_name)
    if os.path.exists(report_path):
        with open(report_path, 'r') as file:
            report_content = file.read()
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"Содержимое отчета {report_name}:\n{report_content}")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text="Отчет не найден.")
    await bot.answer_callback_query(callback_query.id)


async def delete_message_with_delay(message: types.Message, delay: int):
    await asyncio.sleep(delay)
    await message.delete()


@dp.callback_query_handler(lambda query: query.data == 'delete_reports')
async def delete_reports_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем список отчетов пользователя и отправляем клавиатуру для выбора отчетов для удаления
    user_id = callback_query.from_user.id
    user_reports_folder = os.path.join(REPORTS_FOLDER, str(user_id))
    if os.path.exists(user_reports_folder):
        reports = os.listdir(user_reports_folder)
        if reports:
            async with state.proxy() as data:
                selected_reports = data.get("selected_reports", set())
            keyboard = generate_reports_keyboard_with_checkbox(reports, selected_reports)  # Передача selected_reports
            sent_message = await bot.send_message(chat_id=callback_query.from_user.id, text="Выберите отчеты для удаления:", reply_markup=keyboard)
            print("Sent message:", sent_message.message_id)  # Отладочный вывод
            await state.update_data(delete_reports_message_id=sent_message.message_id)
        else:
            sent_message = await bot.send_message(chat_id=callback_query.from_user.id, text="У вас пока нет отчетов.")
            print("Sent message:", sent_message.message_id)  # Отладочный вывод
            # Удаляем сообщение через 3 секунды
            asyncio.ensure_future(delete_message_with_delay(sent_message, 3))
    else:
        sent_message = await bot.send_message(chat_id=callback_query.from_user.id, text="У вас пока нет отчетов.")
        print("Sent message:", sent_message.message_id)  # Отладочный вывод
        # Удаляем сообщение через 3 секунды
        asyncio.ensure_future(delete_message_with_delay(sent_message, 3))

    # Мгновенное удаление свечения кнопки
    await bot.answer_callback_query(callback_query.id, text="", show_alert=True)



@dp.callback_query_handler(lambda query: query.data == 'confirm_delete_reports')
async def confirm_delete_reports_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_reports_folder = os.path.join(REPORTS_FOLDER, str(user_id))
    async with state.proxy() as data:
        selected_reports = data.get("selected_reports", set())
        delete_reports_message_id = data.get("delete_reports_message_id")
    if selected_reports:
        for report_file in selected_reports:
            report_file_path = os.path.join(user_reports_folder, report_file)
            if os.path.exists(report_file_path):
                os.remove(report_file_path)
        success_message = await bot.send_message(chat_id=callback_query.from_user.id,
                                                 text="Выбранные отчеты успешно удалены.")
        # Удаляем сообщение через 3 секунды
        asyncio.ensure_future(delete_message_with_delay(success_message, 3))
    else:
        no_reports_message = await bot.send_message(chat_id=callback_query.from_user.id,
                                                    text="Не выбраны отчеты для удаления.")
        # Удаляем сообщение через 3 секунды
        asyncio.ensure_future(delete_message_with_delay(no_reports_message, 3))

    # Если сообщение с отчетами отправлено и message_id сохранено в состоянии, то редактируем его
    if delete_reports_message_id:
        # Удаляем message_id из состояния
        await state.update_data(delete_reports_message_id=None)
        # Удаляем клавиатуру из сообщения
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=delete_reports_message_id, reply_markup=None)
    # Возвращаем пользователя в главное меню после удаления отчетов
    await show_main_menu(callback_query)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda query: query.data == 'account')
async def show_account_menu(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_reports_folder = os.path.join(REPORTS_FOLDER, str(user_id))

    if os.path.exists(user_reports_folder):
        reports = os.listdir(user_reports_folder)
        if reports:
            keyboard = generate_reports_keyboard(reports)
            # Добавляем кнопку "Удалить отчеты" только если есть отчеты
            keyboard.row(InlineKeyboardButton("Удалить отчеты", callback_data="delete_reports"))
            keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main_menu"))
            await bot.answer_callback_query(callback_query.id, text="", show_alert=True)
            sent_message = await bot.send_message(chat_id=callback_query.message.chat.id, text="Ваши отчеты:", reply_markup=keyboard)
            print("Sent message:", sent_message.message_id)  # Отладочный вывод
        else:
            sent_message = await bot.send_message(chat_id=callback_query.from_user.id, text="У вас пока нет отчетов.")
            print("Sent message:", sent_message.message_id)  # Отладочный вывод
            # Удаляем сообщение через 3 секунды
            asyncio.ensure_future(delete_message_with_delay(sent_message, 2))
    else:
        sent_message = await bot.send_message(chat_id=callback_query.from_user.id, text="У вас пока нет отчетов.")
        print("Sent message:", sent_message.message_id)  # Отладочный вывод
        # Удаляем сообщение через 3 секунды
        asyncio.ensure_future(delete_message_with_delay(sent_message, 2))

    await bot.answer_callback_query(callback_query.id, text="", show_alert=True)


def generate_reports_keyboard_with_checkbox(reports, selected_reports):
    keyboard = InlineKeyboardMarkup()
    for report_file in reports:
        checkbox = "📌 " if report_file in selected_reports else ""
        keyboard.add(InlineKeyboardButton(f"{checkbox} {report_file}", callback_data=f"toggle_report:{report_file}"))

    # Добавляем кнопку "Удалить выбранные" только если есть выбранные отчеты
    if selected_reports:
        keyboard.add(InlineKeyboardButton("Удалить выбранные", callback_data="confirm_delete_reports"))

    return keyboard

@dp.callback_query_handler(lambda query: query.data.startswith('toggle_report:'))
async def toggle_report_callback(callback_query: types.CallbackQuery, state: FSMContext):
    report_file = callback_query.data.split(":")[1]
    async with state.proxy() as data:
        selected_reports = data.get("selected_reports", set())
        if report_file in selected_reports:
            selected_reports.remove(report_file)
        else:
            selected_reports.add(report_file)
        data["selected_reports"] = selected_reports
    # Получаем список отчетов пользователя и отправляем клавиатуру для выбора отчетов для удаления
    user_id = callback_query.from_user.id
    user_reports_folder = os.path.join(REPORTS_FOLDER, str(user_id))
    reports = os.listdir(user_reports_folder) if os.path.exists(user_reports_folder) else []
    # Обновляем клавиатуру с чекбоксами
    await callback_query.message.edit_reply_markup(reply_markup=generate_reports_keyboard_with_checkbox(reports, selected_reports))
    # Мгновенное удаление свечения кнопки
    await bot.answer_callback_query(callback_query.id, text="", show_alert=True)

async def update_reports_keyboard(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    # Получаем список отчетов пользователя
    user_reports_folder = os.path.join(REPORTS_FOLDER, str(user_id))
    reports = os.listdir(user_reports_folder) if os.path.exists(user_reports_folder) else []
    # Извлекаем список уже отмеченных отчетов из данных пользователя
    async with state.proxy() as data:
        selected_reports = data.get("selected_reports", set())
    # Генерируем клавиатуру с чекбоксами
    keyboard = InlineKeyboardMarkup()
    for report_file in reports:
        checked = "☑️" if report_file in selected_reports else "⬜️"
        keyboard.add(InlineKeyboardButton(f"{checked} {report_file}", callback_data=f"toggle_report:{report_file}"))
    await message.edit_reply_markup(reply_markup=keyboard)

def generate_reports_keyboard(reports):
    keyboard = InlineKeyboardMarkup()
    for report_file in reports:
        # Добавляем кнопку для каждого отчета, в callback_data можно добавить уникальный идентификатор отчета
        keyboard.add(InlineKeyboardButton(report_file, callback_data=f"view_report:{report_file}"))
    return keyboard

@dp.callback_query_handler(lambda query: query.data.startswith('test:'))
async def choose_test(callback_query: types.CallbackQuery, state: FSMContext):
    test_name = callback_query.data.split(":")[1]
    questions_answers = import_question_module(test_name)
    if questions_answers:
        # Сохраняем текущий тест и его имя в состояние пользователя
        await state.update_data(current_test=questions_answers, current_test_name=test_name)
        await start_test(callback_query.message, questions_answers, state)
        # Удалить сообщение с выбором теста
        await bot.delete_message(chat_id=callback_query.message.chat.id,message_id=callback_query.message.message_id)       # Мгновенное удаление свечения кнопки
        await bot.answer_callback_query(callback_query.id, text="", show_alert=True)

async def start_test(message: types.Message, questions_answers, state: FSMContext):
    # Сброс предыдущих результатов и вопросов
    await state.update_data(test_results={}, previous_questions={})
    first_question_number = "1"
    first_question_data = questions_answers[first_question_number]
    await ask_question(message, first_question_number, first_question_data, questions_answers, state)

async def ask_question(message: types.Message, q_number: str, q_data: dict, questions_answers, state: FSMContext):
    question_text = f"Вопрос {q_number}: {q_data['question']}"
    async with state.proxy() as data:
        previous_questions = data.get('previous_questions', {})

    if "options" in q_data:
        options = q_data["options"]
        keyboard = generate_keyboard(options, q_number)
        try:
            if message.chat.id in previous_questions:
                await bot.edit_message_text(chat_id=message.chat.id, message_id=previous_questions[message.chat.id],
                                            text=question_text, reply_markup=keyboard)
            else:
                sent_message = await bot.send_message(chat_id=message.chat.id, text=question_text,
                                                      reply_markup=keyboard)
                previous_questions[message.chat.id] = sent_message.message_id
        except aiogram_exceptions.MessageCantBeEdited:
            pass
    else:
        try:
            if message.chat.id in previous_questions:
                await bot.edit_message_text(chat_id=message.chat.id, message_id=previous_questions[message.chat.id],
                                            text=f"{question_text}\n\nПожалуйста, напишите ответ письменно.")
            else:
                sent_message = await bot.send_message(chat_id=message.chat.id,
                                                      text=f"{question_text}\n\nПожалуйста, напишите ответ письменно.")
                previous_questions[message.chat.id] = sent_message.message_id
        except aiogram_exceptions.MessageCantBeEdited:
            pass

    # Обновляем состояние с предыдущими вопросами
    await state.update_data(previous_questions=previous_questions)

# Функция создания клавиатуры для ответов
def generate_keyboard(options, q_number):
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    for idx, option in enumerate(options, start=1):
        callback_data = f"answer:{q_number}:{idx}"
        keyboard_markup.add(InlineKeyboardButton(text=option, callback_data=callback_data))
    return keyboard_markup

@dp.callback_query_handler(lambda query: query.data.startswith('answer:'), state='*')
async def process_callback_answer(callback_query: types.CallbackQuery, state: FSMContext):
    _, q_number, user_answer_index = callback_query.data.split(':')
    user_answer_index = int(user_answer_index)  # Индекс ответа пользователя

    async with state.proxy() as data:
        current_test = data['current_test']
        test_results = data.get('test_results', {})
        q_data = current_test[q_number]

    user_answer_options = list(q_data['options'])
    user_answer = user_answer_options[user_answer_index - 1]  # Получение ответа из списка вариантов

    # Сохраняем ответ пользователя
    correct_answer = q_data.get('correct_answer', None)
    test_results[q_number] = {
        'question': q_data['question'],
        'user_answer': user_answer,
        'correct_answer': correct_answer
    }

    # Обновляем результаты теста в состоянии пользователя
    await state.update_data(test_results=test_results)

    # Проверяем, есть ли еще вопросы в текущем тесте
    if str(int(q_number) + 1) in current_test:
        # Если есть, задаем следующий вопрос, передавая state
        await ask_question(callback_query.message, str(int(q_number) + 1), current_test[str(int(q_number) + 1)],
                           current_test, state)
    else:
        # Если вопросы закончились, перезапускаем тест или генерируем отчет
        await generate_report_with_limit(callback_query.message, test_results, 4000, data.get('current_test_name'),state)

@dp.message_handler(content_types=types.ContentType.TEXT, state='*')
async def handle_text_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        current_test = data.get('current_test')
        test_results = data.get('test_results', {})

    if current_test:
        # Получаем номер текущего вопроса
        current_question_number = str(max(map(int, test_results.keys())) + 1 if test_results else 1)
        # Проверяем, существует ли вопрос с таким номером
        if current_question_number in current_test:
            # Добавляем ответ пользователя к текущему вопросу
            test_results[current_question_number] = {
                'question': current_test[current_question_number]['question'],
                'user_answer': message.text,
                'correct_answer': current_test[current_question_number].get('correct_answer', None)
            }
            # Обновляем результаты теста в состоянии пользователя
            await state.update_data(test_results=test_results)
            # Переходим к следующему вопросу
            await ask_next_question(message, current_question_number, state)
        else:
            # Если вопрос не существует, выводим сообщение об ошибке
            await bot.send_message(chat_id=message.chat.id, text="Ошибка: текущий вопрос не найден.")
    else:
        # Если текущий тест не выбран, выводим сообщение об ошибке
        await bot.send_message(chat_id=message.chat.id, text="Ошибка: тест не выбран.")

async def ask_next_question(message: types.Message, q_number: str, state: FSMContext):
    async with state.proxy() as data:
        current_test = data.get('current_test')
        test_results = data.get('test_results')
        current_test_name = data.get('current_test_name')

    if current_test:
        next_q_number = str(int(q_number) + 1)
        if next_q_number in current_test:
            # Удаляем предыдущее сообщение пользователя
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # Задаем следующий вопрос, передавая состояние в функцию
            await ask_question(message, next_q_number, current_test[next_q_number], current_test, state)
        else:
            # Удаляем ответ пользователя на последний вопрос
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # Передаем название текущего теста и результаты из состояния пользователя
            await generate_report_with_limit(message, test_results, 4000, current_test_name, state)

            # Удаление всех сообщений с вопросами
            previous_question_message_ids = data.get('previous_questions', {}).values()
            for question_message_id in previous_question_message_ids:
                await bot.delete_message(chat_id=message.chat.id, message_id=question_message_id)

async def generate_report_with_limit(message: types.Message, results: dict, max_message_length: int, test_name: str,
                                     state: FSMContext):
    try:
        # Определяем сообщение с вопросом
        question_message_id = results.get('previous_questions', {}).get(message.chat.id)

        # Удаляем сообщение с вопросом
        if question_message_id:
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=question_message_id)
            except MessageToDeleteNotFound:
                pass

        # Получаем информацию о пользователе
        user = message.from_user
        user_full_name = user.full_name  # Получаем полное имя пользователя
        user_username = user.username or "без username"  # Получаем юзернейм пользователя, если доступен

        # Подсчет количества правильных ответов
        total_questions = len(results)
        correct_answers = sum(1 for result in results.values() if is_answer_correct(result['user_answer'], result.get('correct_answer', '')))

        # Проверка на прохождение теста
        pass_threshold = 0.7 * total_questions
        test_passed = correct_answers >= pass_threshold

        # Определяем статус прохождения теста
        status_message = ""
        if test_passed:
            status_message = f"Тест пройден! Количество правильных ответов: {correct_answers}/{total_questions}\n\n"
        else:
            status_message = f"Тест не пройден. Количество правильных ответов: {correct_answers}/{total_questions}\n\n"

        # Формируем заголовок страницы с отчетом
        title = f"Результаты теста '{test_name}' пользователя {user_full_name} ({user_username})"

        # Формируем содержимое страницы с отчетом
        content = status_message
        for q_num, result in results.items():
            # Добавляем текст вопроса и ответы к содержимому
            content += f"<b>Вопрос {q_num}:</b><br>{result['question']}<br>"
            content += f"Ваш ответ: {result['user_answer']}<br>"
            content += f"Правильный ответ: {result.get('correct_answer', 'Не указан')}<br>"

            # Проверяем правильность ответа пользователя
            if is_answer_correct(result['user_answer'], result.get('correct_answer', '')):
                content += "Статус: Правильно<br><br>"
            else:
                content += "Статус: Неправильно<br><br>"

        # Создаем страницу на Telegraph
        response = telegraph.create_page(
            title=title,
            html_content=content
        )

        # Получаем и отправляем ссылку на созданную страницу
        page_url = 'https://telegra.ph/{}'.format(response['path'])

        # Определяем путь к папке пользователя
        user_id = message.from_user.id
        user_reports_folder = os.path.join(REPORTS_FOLDER, str(user_id))

        # Создаем папку, если она не существует
        if not os.path.exists(user_reports_folder):
            os.makedirs(user_reports_folder)

        # Сохраняем ссылку в файл
        link_file_name = f"{test_name}_link.txt"
        link_file_path = os.path.join(user_reports_folder, link_file_name)
        with open(link_file_path, "w") as link_file:
            link_file.write(page_url)

        # Отправляем файл пользователю
        main_menu_button = InlineKeyboardButton("Главное меню", callback_data="main_menu")
        main_menu_keyboard = InlineKeyboardMarkup().add(main_menu_button)
        await bot.send_message(chat_id=message.chat.id,
                               text=f"Отчет сформирован.\nВы можете посмотреть его по ссылке или же в личном кабинете:\n {page_url}",
                               reply_markup=main_menu_keyboard)
        # Возвращаем путь к файлу
        return link_file_path
    except telegraph_exceptions.TelegraphException as e:
        logging.error(f"Telegraph error: {e}")
        return None


def parse_answer(answer: str) -> set:
    # Приведение ответа к нижнему регистру и удаление лишних символов
    answer = answer.lower().strip()
    # Удаление всех нецифровых символов кроме запятых и дефисов
    answer = re.sub(r'[^0-9а-я]', '', answer)
    # Разбиение на отдельные элементы по запятым, точкам с запятой и буквенным символам
    elements = re.split(r'[,;]', answer)
    # Удаление символов "-" и лишних пробелов, а также пустых строк
    elements = [element.strip().replace('-', '') for element in elements if element.strip()]
    return set(elements)

def is_answer_correct(user_answer: str, correct_answer: str) -> bool:
    # Получаем множества элементов из ответов пользователя и правильного ответа
    user_elements = parse_answer(user_answer)
    correct_elements = parse_answer(correct_answer)

    # Проверяем равенство множеств ответов
    return user_elements == correct_elements



async def save_report_to_account(user_id, report_file_name, report):
    user_reports_folder = os.path.join(REPORTS_FOLDER, str(user_id))
    if not os.path.exists(user_reports_folder):
        os.makedirs(user_reports_folder)  # Создаем папку, если она не существует
    report_file_path = os.path.join(user_reports_folder, report_file_name)
    try:
        with open(report_file_path, "w") as report_file:
            report_file.write(report)
        logging.info(f"Report saved to account: {report_file_path}")
        return report_file_path
    except Exception as e:
        logging.error(f"Error while saving report: {e}")
        return None

# Запуск бота
async def startup(dispatcher):
    pass

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=startup)



