from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, CallbackQueryHandler

class CoffeeCuppingBot:
    CHOOSING, RATING, NOTES, AFTER_NOTES = range(4)

    def after_notes(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id

        # Получаем заметку
        note = update.message.text
        self.coffee_ratings[user_id]['note'] = note

        # Рассчитываем общую оценку
        total_rating = sum(self.coffee_ratings[user_id].values()) / len(self.cuppings_criteria)

        print(f"Total Rating: {total_rating}")

        # Формируем сообщение с результатами
        criteria_ratings = "\n".join(
            f"{criterion}: {rating}" for criterion, rating in self.coffee_ratings[user_id].items())
        result_message = f"Оценки:\n{criteria_ratings}\n\n" \
                         f"Средняя оценка: {total_rating}\n" \
                         f"Заметка: {note}\n\n" \
                         "Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'."

        # Отправляем результат пользователю
        update.message.reply_text(result_message)

        # Сбрасываем данные для новой оценки
        context.user_data.clear()

        # Вызываем метод send_cupping_info для отправки результатов
        self.send_cupping_info(update, context)

        return self.CHOOSING

    def get_rating_keyboard(self) -> ReplyKeyboardMarkup:
        ratings = [str(i) for i in range(1, 11)]
        return ReplyKeyboardMarkup([[rating] for rating in ratings], one_time_keyboard=True)

    def rate_coffee(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        rating = update.message.text

        if rating.isdigit() and 1 <= int(rating) <= 10:
            current_criterion = context.user_data['current_criterion']
            self.coffee_ratings.setdefault(user_id, {}).update({self.cuppings_criteria[current_criterion]: int(rating)})

            if current_criterion + 1 < len(self.cuppings_criteria):
                # Продолжаем оценку, если еще есть критерии
                context.user_data['current_criterion'] += 1
                next_criteria = self.cuppings_criteria[current_criterion + 1]
                update.message.reply_text(f"Оцените {next_criteria} (от 1 до 10):",
                                          reply_markup=self.get_rating_keyboard())
                return self.RATING
            else:
                # Завершаем оценку и предлагаем оставить заметку
                update.message.reply_text("Оценка завершена. Теперь напишите заметку о сорте кофе и других деталях.")
                return self.NOTES
        else:
            # Пропускаем отправку сообщения о вводе оценки и переходим к следующему критерию
            return self.RATING

    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.dp = self.updater.dispatcher

        self.AFTER_NOTES = 3

        # Определение состояний для ConversationHandler
        self.CHOOSING, self.RATING, self.NOTES = range(3)

        # Создаем словарь для хранения оценок кофе по каппинг-листу
        self.coffee_ratings = {}

        # Создаем список критериев для оценки
        self.cuppings_criteria = ["Текстура", "Аромат", "Вкус", "Кислотность", "Послевкусие", "Баланс", "Общее впечатление"]

        # Добавляем обработчики команд и сообщений
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("start_cupping", self.start_cupping))
        self.dp.add_handler(MessageHandler(Filters.regex('^(Чашка|Фильтр|Хендбрю|Эспрессо|Молочный напиток)$'),
                                           self.choose_coffee_type))
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.rate_coffee))
        self.dp.add_handler(MessageHandler(Filters.regex('^(Оставить заметку)$'), self.leave_note))
        self.dp.add_handler(MessageHandler(Filters.regex('^(Прервать оценку)$'), self.end_conversation))
        self.dp.add_handler(CallbackQueryHandler(self.handle_inline_button))

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

        # Сразу отправляем запрос на оценку первого критерия
        next_criteria = self.cuppings_criteria[0]
        update.message.reply_text(f"Начинаем оценку {context.user_data['coffee_type']}.\n"
                                  f"Оцените {next_criteria} (от 1 до 10):", reply_markup=self.get_rating_keyboard())

        return self.RATING

    # Функция для обработки Inline-кнопок оценок
    def handle_inline_button(self, update: Update, context: CallbackContext):
        query = update.callback_query
        user_id = query.from_user.id
        rating = int(query.data)

        current_criterion = context.user_data['current_criterion']
        self.coffee_ratings.setdefault(user_id, {}).update({self.cuppings_criteria[current_criterion]: rating})

        if current_criterion + 1 < len(self.cuppings_criteria):
            context.user_data['current_criterion'] += 1
            self.ask_for_rating(update, context)
        else:
            query.edit_message_text("Оценка завершена. Теперь напишите заметку о сорте кофе и других деталях.")
            context.user_data.clear()

    def ask_for_rating(self, update: Update, context: CallbackContext):
        current_criterion = context.user_data['current_criterion']
        next_criteria = self.cuppings_criteria[current_criterion]

        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(1, 6)],
            [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(6, 11)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(f"Оцените {next_criteria}:", reply_markup=reply_markup)

    # Функция для обработки заметки
    def leave_note(self, update: Update, context: CallbackContext) -> int:
        print("Leave note method called")
        user_id = update.message.from_user.id
        note = update.message.text

        print(f"User ID: {user_id}")
        print(f"Note: {note}")

        # Рассчитываем общую оценку
        total_rating = sum(self.coffee_ratings[user_id].values()) / len(self.cuppings_criteria)

        # Сохраняем данные для последующего использования в состоянии AFTER_NOTES
        context.user_data['total_rating'] = total_rating
        context.user_data['note'] = note

        # Возвращаем новый state - AFTER_NOTES
        return self.AFTER_NOTES

    def send_cupping_info(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id

        # Отправляем сообщение с оценками и средней оценкой
        criteria_ratings = "\n".join(
            f"{criterion}: {rating}" for criterion, rating in self.coffee_ratings[user_id].items())
        update.message.reply_text(f"Оценки:\n{criteria_ratings}\n\n"
                                  f"Средняя оценка: {context.user_data['total_rating']}\n"
                                  f"Заметка: {context.user_data['note']}\n\n"
                                  "Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")

        # Сбрасываем данные для новой оценки
        context.user_data.clear()

    # Функция для завершения разговора
    def end_conversation(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Оценка прервана. Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")
        context.user_data.clear()

        return self.CHOOSING

# Вместо "YOUR_TELEGRAM_BOT_TOKEN" укажите токен вашего бота
if __name__ == "__main__":
    bot = CoffeeCuppingBot("6532327533:AAGjS66o-57bYtZKli-nYetr3MYn2W_B1Lk")
