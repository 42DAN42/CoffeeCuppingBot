from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram import Update, ReplyKeyboardMarkup

# Определение состояний для ConversationHandler
CHOOSING, RATING, NOTES = range(3)

# Создаем словарь для хранения оценок кофе по каппинг-листу
coffee_ratings = {}

# Создаем список критериев для оценки
cuppings_criteria = ["Фрагранс", "Аромат", "Вкус", "Кислотность", "Послевкусие", "Баланс", "Общее впечатление"]

# Функция для начала оценки кофе
def start_cupping(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [["Чашка", "Фильтр"], ["Хендбрю", "Эспрессо"], ["Молочный напиток"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text("Выберите тип напитка:", reply_markup=markup)

    return CHOOSING

# Функция для обработки выбора типа напитка
def choose_coffee_type(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    context.user_data['coffee_type'] = update.message.text
    context.user_data['current_criterion'] = 0

    update.message.reply_text(f"Начинаем оценку {context.user_data['coffee_type']}.\n"
                              f"Оцените {cuppings_criteria[0]} (от 1 до 10):")

    return RATING

# Функция для обработки оценок по каппинг-листу
def rate_coffee(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    rating = int(update.message.text)

    if 1 <= rating <= 10:
        current_criterion = context.user_data['current_criterion']
        coffee_ratings.setdefault(user_id, {}).update({cuppings_criteria[current_criterion]: rating})

        if current_criterion + 1 < len(cuppings_criteria):
            # Продолжаем оценку, если еще есть критерии
            context.user_data['current_criterion'] += 1
            next_criteria = cuppings_criteria[current_criterion + 1]
            update.message.reply_text(f"Оцените {next_criteria} (от 1 до 10):")
            return RATING
        else:
            # Завершаем оценку и предлагаем оставить заметку
            update.message.reply_text("Оценка завершена. Теперь напишите заметку о сорте кофе и других деталях.")
            return NOTES
    else:
        update.message.reply_text("Пожалуйста, введите оценку от 1 до 10.")
        return RATING

# Функция для обработки заметки
def leave_note(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    note = update.message.text

    coffee_ratings[user_id]['note'] = note

    # Рассчитываем общую оценку
    total_rating = sum(coffee_ratings[user_id].values()) / len(cuppings_criteria)

    update.message.reply_text(f"Общая оценка: {total_rating}\n"
                              f"Заметка: {note}\n\n"
                              "Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")

    # Сбрасываем данные для новой оценки
    context.user_data.clear()

    return CHOOSING

# Функция для завершения разговора
def end_conversation(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Оценка прервана. Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")
    context.user_data.clear()

    return CHOOSING

# Вместо "YOUR_TELEGRAM_BOT_TOKEN" укажите токен вашего бота
updater = Updater("6532327533:AAGjS66o-57bYtZKli-nYetr3MYn2W_B1Lk", use_context=True)
dp = updater.dispatcher

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Для начала каппинга используйте команду /start_cupping.")

# Добавляем обработчик команды /start
dp.add_handler(CommandHandler("start", start))

# Добавляем обработчики
dp.add_handler(CommandHandler("start_cupping", start_cupping))
dp.add_handler(MessageHandler(Filters.regex('^(Чашка|Фильтр|Хендбрю|Эспрессо|Молочный напиток)$'), choose_coffee_type))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, rate_coffee))
dp.add_handler(MessageHandler(Filters.regex('^(Оставить заметку)$'), leave_note))
dp.add_handler(MessageHandler(Filters.regex('^(Прервать оценку)$'), end_conversation))

# Запускаем бота
updater.start_polling()
updater.idle()
