from aiogram.fsm.state import StatesGroup, State

class CandidateState(StatesGroup):
    SelectLanguage = State()

class AppState(StatesGroup):
    Menu = State()       # Основная страница (главное меню)
    History = State()    # Этап просмотра истории каппингов

class CuppingState(StatesGroup):
    # Этапы оценки вкусовых характеристик
    RatingFragrance = State()
    RatingAroma = State()
    RatingFlavor = State()
    RatingAftertaste = State()
    RatingAcidity = State()
    RatingSweetness = State()
    RatingMouthfeel = State()
    RatingOverall = State()
    # Этапы текстового ввода
    BrewingMethod = State()
    BeanName = State()
    Note = State()
