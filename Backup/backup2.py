from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, Filters
from telegram import Update, ReplyKeyboardMarkup
#import telegram.ext.filters as Filters

class CoffeeCuppingBot:
    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.dp = self.updater.dispatcher

        # Определение состояний для ConversationHandler
        self.CHOOSING, self.RATING, self.NOTES = range(3)

        # Создаем словарь для хранения оценок кофе по каппинг-листу
        self.coffee_ratings = {}

        # Создаем список критериев для оценки
        self.cuppings_criteria = ["Фрагранс", "Аромат", "Вкус", "Кислотность", "Послевкусие", "Баланс", "Общее впечатление"]

        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("start_cupping", self.start_cupping))
        self.dp.add_handler(MessageHandler(Filters.regex('^(Чашка|Фильтр|Хендбрю|Эспрессо|Молочный напиток)$'), self.choose_coffee_type))
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.rate_coffee))
        self.dp.add_handler(MessageHandler(Filters.regex('^(Оставить заметку)$'), self.leave_note))
        self.dp.add_handler(MessageHandler(Filters.regex('^(Прервать оценку)$'), self.end_conversation))

        # Запускаем бота
        self.updater.start_polling()
        self.updater.idle()

    # Функция для обработки команды /start
    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text("Привет! Для начала каппинга используйте команду /start_cupping.")

    # Функция для начала оценки кофе
    def start_cupping(self, update: Update, context: CallbackContext) -> int:
        reply_keyboard = [["Чашка", "Фильтр"], ["Хендбрю", "Эспрессо"], ["Молочный напиток"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        update.message.reply_text("Выберите тип напитка:", reply_markup=markup)

        return self.CHOOSING

    # Функция для обработки выбора типа напитка
    def choose_coffee_type(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        context.user_data['coffee_type'] = update.message.text
        context.user_data['current_criterion'] = 0

        update.message.reply_text(f"Начинаем оценку {context.user_data['coffee_type']}.\n"
                                  f"Оцените {self.cuppings_criteria[0]} (от 1 до 10):")

        return self.RATING

    # Функция для обработки оценок по каппинг-листу
    def rate_coffee(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        rating = int(update.message.text)

        if 1 <= rating <= 10:
            current_criterion = context.user_data['current_criterion']
            self.coffee_ratings.setdefault(user_id, {}).update({self.cuppings_criteria[current_criterion]: rating})

            if current_criterion + 1 < len(self.cuppings_criteria):
                # Продолжаем оценку, если еще есть критерии
                context.user_data['current_criterion'] += 1
                next_criteria = self.cuppings_criteria[current_criterion + 1]
                update.message.reply_text(f"Оцените {next_criteria} (от 1 до 10):")
                return self.RATING
            else:
                # Завершаем оценку и предлагаем оставить заметку
                update.message.reply_text("Оценка завершена. Теперь напишите заметку о сорте кофе и других деталях.")
                return self.NOTES
        else:
            update.message.reply_text("Пожалуйста, введите оценку от 1 до 10.")
            return self.RATING

    # Функция для обработки заметки
    def leave_note(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        note = update.message.text

        self.coffee_ratings[user_id]['note'] = note

        # Рассчитываем общую оценку
        total_rating = sum(self.coffee_ratings[user_id].values()) / len(self.cuppings_criteria)

        # Создаем текст для вывода итоговой оценки и заметки
        result_text = f"Общая оценка: {total_rating}\n"
        result_text += f"Заметка: {note}\n\n"
        result_text += "Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'."

        # Отправляем текст пользователю
        update.message.reply_text(result_text)

        # Сбрасываем данные для новой оценки
        context.user_data.clear()

        return self.CHOOSING

    # Функция для завершения разговора
    def end_conversation(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Оценка прервана. Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")
        context.user_data.clear()

        return self.CHOOSING

# Вместо "YOUR_TELEGRAM_BOT_TOKEN" укажите токен вашего бота
if __name__ == "__main__":
    bot = CoffeeCuppingBot("6532327533:AAGjS66o-57bYtZKli-nYetr3MYn2W_B1Lk")
