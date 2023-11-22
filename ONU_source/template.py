'''
We have added some type hints for you. This is to make it easier for you to read the code
and write your implementation. We have also added some exception detections to improve
robustness and help you to debug more efficiently, you could simply ignore them first.

You should write your code in 'YOUR CODE HERE'.
'''

from enum import IntEnum, unique
from typing import Tuple, List
import copy


'''
An enumeration class is used to define a set of finite named constants. It allows you to 
assign easy-to-remember names to a group of related constants to enhance code readability
and maintainability.

We provide some enumerate classes. Please DO NOT CHANGE them.
'''

@unique
class Color(IntEnum):
    RED = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3
    CYAN = 4
    ORANGE = 5
    PURPLE = 6
    WHITE = 7
    BLACK = 8
    VIOLET = 9
    

@unique
class Effect(IntEnum):
    CHANGE_COLOR = 0
    BAN = 1
    PLUS_TWO = 2


@unique
class ActionType(IntEnum):
    DRAW = 0
    DROP = 1
    PASS = 2


'''
A Card object is defined with a color attribute.
Member variables, like self._color, are attributes that store data specific to an instance
of the class.
They are prefixed with underscores to indicate they are intended to be private, meaning they
should NOT be accessed directly from outside the class.
'''
class Card:
    '''
    The constructor (__init__ method) is a special method.
    It gets called when an object of the class is created.
    It takes parameters, and in this case, it takes a 'color' parameter.
    The purpose of 'self._color = color' is to assign the 'color' parameter to the '_color' attribute.
    The 'self' parameter refers to the instance of the class itself.
    '''
    def __init__(self, color: Color) -> None:
        self._color = color

    '''
    This method is a "getter method" that retrieves the color attribute of the Card instance.
    Getter methods are used to access private attributes from outside the class.
    You will implement a lot of similar methods in this assignment.
    ''' 
    def get_color(self) -> Color:
        # YOUR CODE HERE
        pass


'''
Problem 1: Card

We have provided the inheritance relationship for you. You DON'T NEED TO change them. 
'''


class NumericCard(Card):
    def __init__(self, color: Color, number: int) -> None:
        super().__init__(color)
        # YOUR CODE HERE
        pass

    def __repr__(self) -> str:
        # YOUR CODE HERE
        pass

    # We provide some hints for you to implement this method.
    def __lt__(self, other: Card) -> bool:
        if not isinstance(other, NumericCard) and not isinstance(other, SpecialCard):
            raise Exception("Invalid Card Type")
        
        if self._color < other.get_color():
            # YOUR CODE HERE
            pass
        elif self._color > other.get_color():
            # YOUR CODE HERE
            pass
        else:
            if isinstance(other, NumericCard):
                # YOUR CODE HERE
                pass
            else:
                # YOUR CODE HERE
                pass

    # You should implement this method (almost) completely by yourself.
    def __eq__(self, other: Card) -> bool:
        if not isinstance(other, NumericCard) and not isinstance(other, SpecialCard):
            raise Exception("Invalid Card Type")
        # YOUR CODE HERE
        
    def get_number(self) -> int:
        # YOUR CODE HERE
        pass


class SpecialCard(Card):
    def __init__(self, color: Color, effect: Effect) -> None:
        super().__init__(color)
        # YOUR CODE HERE
        pass

    def __repr__(self) -> str:
        # YOUR CODE HERE
        pass

    def __lt__(self, other: Card) -> bool:
        if not isinstance(other, NumericCard) and not isinstance(other, SpecialCard):
            raise Exception("Invalid Card Type")   
        # YOUR CODE HERE

    def __eq__(self, other: Card) -> bool:
        if not isinstance(other, NumericCard) and not isinstance(other, SpecialCard):
            raise Exception("Invalid Card Type")
        # YOUR CODE HERE
    
    def get_effect(self) -> Effect:
        # YOUR CODE HERE
        pass


'''
Problem 2: CardSet

Similarly, we have provided the inheritance relationship for you. You DON'T NEED TO CHANGE them. 
''' 


class CardSet:
    _cards: List[Card]

    def __init__(self, cards: List[Card]) -> None:
        # You should guarantee that we CANNOT modify your self._cards from outside.
        # YOUR CODE HERE
        pass

    def __repr__(self) -> str:
        # YOUR CODE HERE
        pass    

    def is_empty(self) -> bool:
        # YOUR CODE HERE
        pass

    def get_cards(self) -> List[Card]:
        return copy.deepcopy(self._cards)


'''
The constructor (__init__ method) is not explicitly defined here because the Hand class
is inheriting from the CardSet class, which already has a constructor that takes a list of cards.
By not providing a constructor in this subclass, it implicitly uses the constructor of the superclass (CardSet).
This is known as constructor inheritance, where the child class inherits the constructor of its parent class.

The responsibility of initializing the cards in the Hand is delegated to the constructor of the CardSet class.
The situation is similar for the Deck class.
'''
class Hand(CardSet):
    def add_card(self, card: Card) -> None:
        # YOUR CODE HERE
        pass
    
    def remove_card(self, card: Card) -> None:
        # YOUR CODE HERE
        pass


class Deck(CardSet):
    def get_next_card(self) -> Card:
        if self.is_empty():
            raise Exception("No Card Left")
        # YOUR CODE HERE


'''
Problem 3: Player
'''


class Player:
    def sort_cards(self, cards: List[Card]) -> List[Card]:
        # YOUR CODE HERE
        pass

    def action(self, cards: List[Card], last_card: Card, is_last_player_drop: bool) -> Tuple[ActionType, Card | None]: 
        # YOUR CODE HERE
        pass


'''
Problem 4: Game Start!
'''


class Game:
    _player_hands: List[Hand]

    # Construct Game and initialize the deck and players
    def __init__(self, cards: List[Card], num_player: int = 7, hand_card_num: int = 7, dealer_id: int = 0) -> None:
        self._deck = Deck(cards)
        self._players = [Player() for _ in range(num_player)]
        
        '''
        We add a '-1' because _current_player_id will +1 when we call turn() at the first time,
        and we need to -1 before that to keep the correctness.
        '''
        self._current_player_id = dealer_id - 1
        self._last_card = None
        self._is_last_player_drop = False
        self._plus_two_cnt = 0   
        
        # Implement self._player_hands.
        # YOUR CODE HERE

    # This is used for our test. Please DO NOT CHANGE it.
    def get_info(self) -> Tuple[int, Card, bool, int, List[Hand]]:
        return self._current_player_id, self._last_card, self._is_last_player_drop, self._plus_two_cnt, self._player_hands

    def is_end(self) -> bool:
        # YOUR CODE HERE
        pass

    def is_not_end(self) -> bool:
        return not self.is_end()

    def current_player_drop_card(self, card: Card) -> None:
        # YOUR CODE HERE
        pass
        
    def get_scores(self) -> List[int]:
        # YOUR CODE HERE
        pass
    
    def get_winner(self) -> int:
        if self.is_not_end():
            raise Exception("Game is not end")
        # YOUR CODE HERE
    
    def turn(self) -> Tuple[Tuple[ActionType, Card | None], Tuple[int, Card, bool, int, List[Hand]], bool]:
        if self.is_end():
            raise Exception("Game is end")
        
        self._current_player_id = (self._current_player_id + 1) % len(self._players)
        action = self._players[self._current_player_id].action(
            self._player_hands[self._current_player_id].get_cards(), self._last_card, self._is_last_player_drop)

        if action[0] == ActionType.DRAW:
            # YOUR CODE HERE
            pass

        elif action[0] == ActionType.DROP:
            self.current_player_drop_card(action[1])
            
            # What do you still need to do here?
            # YOUR CODE HERE

        elif action[0] == ActionType.PASS:
            # YOUR CODE HERE
            pass

        else:
            raise Exception("Invalid Action")

        return action, self.get_info(), self.is_not_end()