# bot_dictionary.py
texts = {
    "EN": {
        "welcome": "Welcome to the Coffee Cupping Bot! Please choose an option:",
        "choose_language": "Choose your language: EN / RU / UA",
        "menu_start_cupping": "Start Cupping",
        "menu_history": "Cupping History",
        "menu_change_language": "Change Language",
        "rate_parameter": "Please rate {param} from 1 to 10:",
        "brewing_method": "Enter brewing method:",
        "bean_name": "Enter the coffee bean name:",
        "note": "Enter your note:",
        "back": "Back",
        "menu": "Menu",
        "history_button": "Cupping History",
        "final_summary": (
            "Cupping ID: {id}\n"
            "Date: {dt}\n"
            "{params}\n"
            "Average Score: {avg}\n"
            "Brewing Method: {method}\n"
            "Bean Name: {bean}\n"
            "Note: {note}"
        ),
    },
    "RU": {
        "welcome": "Добро пожаловать в бот для каппинга кофе! Выберите опцию:",
        "choose_language": "Выберите язык: EN / RU / UA",
        "menu_start_cupping": "Начать каппинг",
        "menu_history": "История каппинга",
        "menu_change_language": "Сменить язык",
        "rate_parameter": "Оцените {param} от 1 до 10:",
        "brewing_method": "Напишите метод заваривания:",
        "bean_name": "Введите название зерна:",
        "note": "Напишите заметку:",
        "back": "Назад",
        "menu": "Меню",
        "history_button": "История каппинга",
        "final_summary": (
            "Каппинг ID: {id}\n"
            "Дата: {dt}\n"
            "{params}\n"
            "Средняя оценка: {avg}\n"
            "Метод заваривания: {method}\n"
            "Название зерна: {bean}\n"
            "Заметка: {note}"
        ),
    },
    "UA": {
        "welcome": "Ласкаво просимо до бота для капінгу кави! Оберіть опцію:",
        "choose_language": "Оберіть мову: EN / RU / UA",
        "menu_start_cupping": "Почати капінг",
        "menu_history": "Історія капінгу",
        "menu_change_language": "Змінити мову",
        "rate_parameter": "Оцініть {param} від 1 до 10:",
        "brewing_method": "Введіть метод заварювання:",
        "bean_name": "Введіть назву зерна:",
        "note": "Введіть примітку:",
        "back": "Назад",
        "menu": "Меню",
        "history_button": "Історія капінгу",
        "final_summary": (
            "Каппінг ID: {id}\n"
            "Дата: {dt}\n"
            "{params}\n"
            "Середня оцінка: {avg}\n"
            "Метод заварювання: {method}\n"
            "Назва зерна: {bean}\n"
            "Примітка: {note}"
        ),
    }
}

parameter_names = {
    "EN": {
        "fragrance": "Fragrance",
        "aroma": "Aroma",
        "flavor": "Flavor",
        "aftertaste": "Aftertaste",
        "acidity": "Acidity",
        "sweetness": "Sweetness",
        "mouthfeel": "Mouthfeel",
        "overall": "Overall"
    },
    "RU": {
        "fragrance": "Аромат (fragrance)",
        "aroma": "Букет (aroma)",
        "flavor": "Вкус (flavor)",
        "aftertaste": "Послевкусие (aftertaste)",
        "acidity": "Кислотность (acidity)",
        "sweetness": "Сладость (sweetness)",
        "mouthfeel": "Тело (mouthfeel)",
        "overall": "Общее впечатление (overall)"
    },
    "UA": {
        "fragrance": "Аромат (fragrance)",
        "aroma": "Букет (aroma)",
        "flavor": "Смак (flavor)",
        "aftertaste": "Посмак (aftertaste)",
        "acidity": "Кислинка (acidity)",
        "sweetness": "Солодкість (sweetness)",
        "mouthfeel": "Тіло (mouthfeel)",
        "overall": "Загальне вподобання (overall)"
    }
}
