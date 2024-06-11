import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, CallbackQueryHandler, ConversationHandler

class CoffeeCuppingBot:
    CHOOSING, RATING, NOTES, AFTER_NOTES = range(4)

    def __init__(self, token):
        self.evaluation_completed = False  # Инициализация атрибута evaluation_completed

        # Создаем словарь для хранения оценок кофе по каппинг-листу
        self.ratings = {}
        # Создаем словарь для хранения заметок
        self.notes = {}

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.updater = Updater(token, use_context=True)
        self.dp = self.updater.dispatcher

        # Создаем список критериев для оценки
        self.cuppings_criteria = ["Текстура", "Аромат", "Вкус", "Кислотность", "Послевкусие", "Баланс", "Общее впечатление"]

        # Определение состояний для ConversationHandler
        self.CHOOSING, self.RATING, self.NOTES, self.AFTER_NOTES = range(4)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start), CommandHandler('start_cupping', self.start_cupping)],
            states={
                self.CHOOSING: [
                    MessageHandler(Filters.regex('^(Чашка|Фильтр|Хендбрю|Эспрессо|Молочный напиток)$'), self.choose_coffee_type)
                ],
                self.RATING: [
                    MessageHandler(Filters.text & ~Filters.command, self.rate_coffee)
                ],
                self.NOTES: [
                    MessageHandler(Filters.text & ~Filters.command, self.leave_note)
                ],
                self.AFTER_NOTES: [
                    MessageHandler(Filters.text & ~Filters.command, self.after_notes)
                ],
            },
            fallbacks=[MessageHandler(Filters.regex('^(Прервать оценку)$'), self.end_conversation)]
        )

        self.dp.add_handler(conv_handler)
        self.dp.add_handler(CallbackQueryHandler(self.handle_inline_button))

        # Запускаем бота
        self.updater.start_polling()
        self.updater.idle()

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text("Привет! Для начала каппинга используйте команду /start_cupping.")
        context.user_data['current_state'] = self.CHOOSING  # Устанавливаем начальное состояние
        # Добавляем кнопку "Начнём каппинг!"
        reply_keyboard = [["Начнём каппинг!"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("Для начала каппинга нажмите кнопку 'Начнём каппинг!':", reply_markup=markup)

    def start_cupping(self, update: Update, context: CallbackContext) -> int:
        reply_keyboard = [["Чашка", "Фильтр"], ["Хендбрю", "Эспрессо"], ["Молочный напиток"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        update.message.reply_text("Выберите тип напитка:", reply_markup=markup)
        context.user_data['current_state'] = self.CHOOSING  # Устанавливаем начальное состояние

        return self.CHOOSING

    def choose_coffee_type(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        context.user_data['coffee_type'] = update.message.text
        context.user_data['current_criterion'] = 0

        next_criteria = self.cuppings_criteria[0]
        update.message.reply_text(f"Начинаем оценку {context.user_data['coffee_type']}.\n"
                                  f"Оцените {next_criteria} (от 1 до 10):", reply_markup=self.get_rating_keyboard())

        return self.RATING

    def handle_inline_button(self, update: Update, context: CallbackContext):
        query = update.callback_query
        user_id = query.from_user.id
        rating = int(query.data)

        current_criterion = context.user_data['current_criterion']
        self.ratings.setdefault(user_id, {}).update({self.cuppings_criteria[current_criterion]: rating})

        if current_criterion + 1 < len(self.cuppings_criteria):
            context.user_data['current_criterion'] += 1
            self.ask_for_rating(query, context)
        else:
            query.edit_message_text("Оценка завершена. Теперь напишите заметку о сорте кофе и других деталях.")
            context.user_data['current_state'] = self.NOTES
            self.evaluation_completed = True

    def ask_for_rating(self, query, context: CallbackContext):
        current_criterion = context.user_data['current_criterion']
        next_criteria = self.cuppings_criteria[current_criterion]

        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(1, 6)],
            [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(6, 11)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.message.reply_text(f"Оцените {next_criteria}:", reply_markup=reply_markup)

    def rate_coffee(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        rating = update.message.text

        if rating.isdigit() and 1 <= int(rating) <= 10:
            current_criterion = context.user_data['current_criterion']
            self.ratings.setdefault(user_id, {}).update({self.cuppings_criteria[current_criterion]: int(rating)})

            if current_criterion + 1 < len(self.cuppings_criteria):
                context.user_data['current_criterion'] += 1
                next_criteria = self.cuppings_criteria[current_criterion + 1]
                update.message.reply_text(f"Оцените {next_criteria} (от 1 до 10):", reply_markup=self.get_rating_keyboard())
                context.user_data['current_state'] = self.RATING
                return self.RATING
            else:
                update.message.reply_text(
                    "Оценка завершена. Теперь напишите заметку о сорте кофе и других деталях:",
                    reply_markup=ReplyKeyboardMarkup([], one_time_keyboard=True))
                context.user_data['current_state'] = self.NOTES
                self.evaluation_completed = True
                return self.NOTES
        else:
            return self.RATING

    def leave_note(self, update: Update, context: CallbackContext) -> int:
        if not self.evaluation_completed:
            return self.RATING

        user_id = update.message.from_user.id
        note = update.message.text
        self.notes[user_id] = {'note': note}

        total_rating = sum(self.ratings[user_id].values()) / len(self.cuppings_criteria)
        context.user_data['total_rating'] = total_rating
        context.user_data['note'] = note

        update.message.reply_text(f"Заметка сохранена.\n"
                                  f"Оценки:\n{self.format_ratings(user_id)}\n\n"
                                  f"Средняя оценка: {total_rating}\n"
                                  f"Заметка: {note}\n\n"
                                  "Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")
        context.user_data['current_state'] = self.AFTER_NOTES
        self.evaluation_completed = False  # Сбрасываем флаг оценки

        return self.AFTER_NOTES

    def after_notes(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")
        context.user_data.clear()
        return self.CHOOSING

    def format_ratings(self, user_id):
        return "\n".join(f"{criterion}: {rating}" for criterion, rating in self.ratings[user_id].items())

    def get_rating_keyboard(self) -> ReplyKeyboardMarkup:
        ratings_row1 = [str(i) for i in range(1, 6)]
        ratings_row2 = [str(i) for i in range(6, 11)]
        keyboard = [ratings_row1, ratings_row2]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    def end_conversation(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Оценка прервана. Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")
        context.user_data.clear()
        return self.CHOOSING

if __name__ == "__main__":
    bot = CoffeeCuppingBot("")
