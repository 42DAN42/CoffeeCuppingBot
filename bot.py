import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, CallbackQueryHandler, ConversationHandler

class CoffeeCuppingBot:
    CHOOSING, RATING, NOTES, AFTER_NOTES = range(4)

    def note(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id

        # Создаем словарь с оценками "00" для типа напитка "DEBUG"
        self.ratings.setdefault(user_id, {}).update({
            "DEBUG": {
                'Текстура': 0,
                'Аромат': 0,
                'Вкус': 0,
                'Кислотность': 0,
                'Послевкусие': 0,
                'Баланс': 0,
                'Общее впечатление': 0
            }
        })
        print("Текущее состояние:", context.user_data.get('current_state'))
        context.user_data['current_state'] = self.RATING  # Обновляем состояние

        if context.user_data.get('current_state') == self.RATING:
            # Предлагаем оставить заметку, если это первое завершение оценки
            update.message.reply_text(
                "Оценка завершена. Теперь напишите заметку о сорте кофе и других деталях:",
                reply_markup=ReplyKeyboardMarkup([], one_time_keyboard=True))
            print("Завершаем оценку и предлагаем оставить заметку")
            context.user_data['current_state'] = self.NOTES  # Сохраняем текущее состояние
            self.evaluation_completed = True  # Устанавливаем флаг, что оценка завершена
            print("Текущее состояние:", context.user_data.get('current_state'))
            print("Оценки:", self.ratings)  # Отладочное сообщение
            print("Заметки:", self.notes)  # Отладочное сообщение
            return self.NOTES  # Возвращаем состояние NOTES вместо self.AFTER_NOTES
        else:
            # Оценка завершается, но это не первое завершение оценки
            update.message.reply_text("Оценка прервана. Оставьте заметку:",
                                      reply_markup=ReplyKeyboardMarkup([], one_time_keyboard=True))
            print("Оценка прервана, предлагаем оставить заметку")
            context.user_data['current_state'] = self.NOTES  # Сохраняем текущее состояние
            print("Текущее состояние:", context.user_data.get('current_state'))
            print("Оценки:", self.ratings)  # Отладочное сообщение
            print("Заметки:", self.notes)  # Отладочное сообщение
            return self.NOTES  # Возвращаем состояние NOTES

    def rate_coffee(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        rating = update.message.text

        if rating.isdigit() and 1 <= int(rating) <= 10:
            current_criterion = context.user_data['current_criterion']
            self.ratings.setdefault(user_id, {}).update({self.cuppings_criteria[current_criterion]: int(rating)})

            if current_criterion + 1 < len(self.cuppings_criteria):
                # Продолжаем оценку, если еще есть критерии
                context.user_data['current_criterion'] += 1
                next_criteria = self.cuppings_criteria[current_criterion + 1]
                update.message.reply_text(f"Оцените {next_criteria} (от 1 до 10):",
                                          reply_markup=self.get_rating_keyboard())
                print("Переходим к оценке следующего критерия")
                print("Текущее состояние:", context.user_data.get('current_state'))
                context.user_data['current_state'] = self.RATING  # Обновляем состояние
                return self.RATING
            else:
                if context.user_data.get('current_state') == self.RATING:
                    # Предлагаем оставить заметку, если это первое завершение оценки
                    update.message.reply_text(
                        "Оценка завершена. Теперь напишите заметку о сорте кофе и других деталях:",
                        reply_markup=ReplyKeyboardMarkup([], one_time_keyboard=True))
                    print("Завершаем оценку и предлагаем оставить заметку")
                    context.user_data['current_state'] = self.NOTES  # Сохраняем текущее состояние
                    self.evaluation_completed = True  # Устанавливаем флаг, что оценка завершена
                    print("Текущее состояние:", context.user_data.get('current_state'))
                    print("Оценки:", self.ratings)  # Отладочное сообщение
                    print("Заметки:", self.notes)  # Отладочное сообщение
                    return self.NOTES  # Возвращаем состояние NOTES вместо self.AFTER_NOTES
                else:
                    # Оценка завершается, но это не первое завершение оценки
                    update.message.reply_text("Оценка прервана. Оставьте заметку:",
                                              reply_markup=ReplyKeyboardMarkup([], one_time_keyboard=True))
                    print("Оценка прервана, предлагаем оставить заметку")
                    context.user_data['current_state'] = self.NOTES  # Сохраняем текущее состояние
                    print("Текущее состояние:", context.user_data.get('current_state'))
                    print("Оценки:", self.ratings)  # Отладочное сообщение
                    print("Заметки:", self.notes)  # Отладочное сообщение
                    return self.NOTES  # Возвращаем состояние NOTES

        else:
            # Пропускаем отправку сообщения о вводе оценки и переходим к следующему критерию
            return self.RATING

    def leave_note(self, update: Update, context: CallbackContext) -> int:
        if not self.evaluation_completed:
            # Если оценка не завершена, игнорируем запрос на заметку
            print("Оценка не завершена, игнорируем запрос на заметку")
            return self.RATING

        user_id = update.message.from_user.id
        note = update.message.text
        print("Получаем заметку:", note)

        # Рассчитываем общую оценку
        total_rating = sum(self.ratings[user_id].values()) / len(self.cuppings_criteria)

        # Сохраняем данные для последующего использования в состоянии AFTER_NOTES
        context.user_data['total_rating'] = total_rating
        context.user_data['note'] = note

        # Возвращаем новый state - AFTER_NOTES
        print("Переходим к состоянию AFTER_NOTES")
        context.user_data['current_state'] = self.AFTER_NOTES  # Сохраняем текущее состояние
        print("Текущее состояние:", context.user_data.get('current_state'))
        return self.AFTER_NOTES

    def after_notes(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id

        # Получаем заметку
        note = update.message.text
        self.notes[user_id] = {'note': note}
        print("Заметка получена:", note)

        # Рассчитываем общую оценку
        total_rating = sum(self.ratings[user_id].values()) / len(self.cuppings_criteria)
        context.user_data['total_rating'] = total_rating

        print(f"Total Rating: {total_rating}")

        # Формируем сообщение с результатами
        criteria_ratings = "\n".join(
            f"{criterion}: {rating}" for criterion, rating in self.ratings[user_id].items())
        result_message = f"Оценки:\n{criteria_ratings}\n\n" \
                         f"Средняя оценка: {total_rating}\n" \
                         f"Заметка: {note}\n\n" \
                         "Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'."

        # Отправляем результат пользователю
        update.message.reply_text(result_message)
        print("Результаты отправлены")

        # Вызываем метод send_cupping_info для отправки результатов
        self.send_cupping_info(update, context)

        # Сбрасываем данные для новой оценки
        context.user_data.clear()

        return self.CHOOSING

    def send_ratings(self, update: Update):
        user_id = update.message.from_user.id
        criteria_ratings = "\n".join(
            f"{criterion}: {rating}" for criterion, rating in self.ratings[user_id].items())
        update.message.reply_text(f"Оценки:\n{criteria_ratings}")

    def send_cupping_info(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id

        # Отправляем сообщение с оценками и средней оценкой
        criteria_ratings = "\n".join(
            f"{criterion}: {rating}" for criterion, rating in self.ratings[user_id].items())
        update.message.reply_text(f"Оценки:\n{criteria_ratings}\n\n"
                                  f"Средняя оценка: {context.user_data['total_rating']}\n"
                                  f"Заметка: {context.user_data['note']}\n\n"
                                  "Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")

        # Сбрасываем данные для новой оценки
        context.user_data.clear()

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
        self.cuppings_criteria = ["Текстура", "Аромат", "Вкус", "Кислотность", "Послевкусие", "Баланс",
                                  "Общее впечатление"]

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

    # Функция для обработки команды /start
    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text("Привет! Для начала каппинга используйте команду /start_cupping.")

    # Функция для начала оценки кофе
    def start_cupping(self, update: Update, context: CallbackContext) -> int:
        reply_keyboard = [["Чашка", "Фильтр"], ["Хендбрю", "Эспрессо"], ["Молочный напиток"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        update.message.reply_text("Выберите тип напитка:", reply_markup=markup)
        context.user_data['current_state'] = self.CHOOSING  # Устанавливаем начальное состояние

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
        self.ratings.setdefault(user_id, {}).update({self.cuppings_criteria[current_criterion]: rating})

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

    def get_rating_keyboard(self) -> ReplyKeyboardMarkup:
        # Создаем два ряда кнопок с оценками от 1 до 5 и от 6 до 10
        ratings_row1 = [str(i) for i in range(1, 6)]
        ratings_row2 = [str(i) for i in range(6, 11)]

        # Собираем клавиатуру из двух рядов
        keyboard = [ratings_row1, ratings_row2]

        # Возвращаем ReplyKeyboardMarkup
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # Функция для завершения разговора
    def end_conversation(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Оценка прервана. Вы можете начать новую оценку, нажав кнопку 'Начнём каппинг!'.")
        context.user_data.clear()

        return self.CHOOSING

# Вместо "YOUR_TELEGRAM_BOT_TOKEN" укажите токен вашего бота
if __name__ == "__main__":
    bot = CoffeeCuppingBot("YOUR_TELEGRAM_BOT_TOKEN")
