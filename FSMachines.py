# FSMachines.py
from aiogram.fsm.state import StatesGroup, State

class CandidateState(StatesGroup):
    SelectLanguage = State()

class CuppingState(StatesGroup):
    # Rate coffee parameters:
    RatingFragrance = State()
    RatingAroma = State()
    RatingFlavor = State()
    RatingAftertaste = State()
    RatingAcidity = State()
    RatingSweetness = State()
    RatingMouthfeel = State()
    RatingOverall = State()
    # Textual inputs:
    BrewingMethod = State()
    BeanName = State()
    Note = State()
