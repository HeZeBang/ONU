# ONU template by Asta

from enum import IntEnum, unique
from typing import Tuple, List
import copy

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
    
class Card:
    def __init__(self, color: Color) -> None:
        self._color = color
        
    def get_color(self) -> Color:
        return self._color

class NumericCard(Card):
    def __init__(self, color: Color, number: int) -> None:
        super().__init__(color)
        assert(int(number) == number)
        self._number = number

    def __repr__(self) -> str:
        return f"Numeric card {self._color.name} {self._number}"

    def __lt__(self, other: Card) -> bool:
        if not isinstance(other, NumericCard) and not isinstance(other, SpecialCard):
            raise Exception("Invalid Card Type")
        if self._color == other.get_color():
            if isinstance(other, NumericCard):
                return self._number < other.get_number()
            elif isinstance(other, SpecialCard):
                return True
            else:
                raise Exception("Invalid Card Type")
        return self._color < other.get_color()

    def __eq__(self, other: Card) -> bool:
        if not isinstance(other, NumericCard) and not isinstance(other, SpecialCard):
            raise Exception("Invalid Card Type")
        if isinstance(other, SpecialCard) :
            return False
        if self._color != other.get_color() :
            return False
        if self._number != other.get_number() :
            return False
        return True
        
    def get_number(self) -> int:
        return self._number


class SpecialCard(Card):
    def __init__(self, color: Color, effect: Effect) -> None:
        super().__init__(color)
        self._effect = effect

    def __repr__(self) -> str:
        return f"{self._effect.name} card {self._color.name}"

    def __lt__(self, other: Card) -> bool:
        if not isinstance(other, NumericCard) and not isinstance(other, SpecialCard):
            raise Exception("Invalid Card Type")   
        if self._color == other.get_color():
            if isinstance(other, NumericCard):
                return False
            elif isinstance(other, SpecialCard):
                return self._effect < other.get_effect()
            else:
                raise Exception("Invalid Card Type")
        return self._color < other.get_color()

    def __eq__(self, other: Card) -> bool:
        if not isinstance(other, NumericCard) and not isinstance(other, SpecialCard):
            raise Exception("Invalid Card Type")
        if isinstance(other, NumericCard) :
            return False
        if self._color != other.get_color() :
            return False
        if self._effect != other.get_effect() :
            return False
        return True
    
    def get_effect(self) -> Effect:
        return self._effect

class CardSet:
    _cards: List[Card]

    def __init__(self, cards: List[Card]) -> None:
        self._cards = copy.deepcopy(cards)

    def __repr__(self) -> str:
        return repr(self._cards)    

    def is_empty(self) -> bool:
        return not self._cards

    def get_cards(self) -> List[Card]:
        return copy.deepcopy(self._cards)

class Hand(CardSet):
    def add_card(self, card: Card) -> None:
        self._cards.append(card)
    
    def remove_card(self, card: Card) -> None:
        self._cards.remove(card)


class Deck(CardSet):
    def get_next_card(self) -> Card:
        if self.is_empty():
            raise Exception("No Card Left")
        return self._cards.pop(0)

class Player:
    def sort_cards(self, cards: List[Card]) -> List[Card]:
        return sorted(cards, reverse = True)

    def action(self, cards: List[Card], last_card: Card, is_last_player_drop: bool) -> Tuple[ActionType, Card | None]: 
        rule = lambda c, lc : True
        def judge_drop_next(c : Card, lc : Card) -> bool:
            if c.get_color() == lc.get_color() :
                return True
            if isinstance(c, NumericCard) :
                if isinstance(lc, NumericCard) :
                    return c.get_number() == lc.get_number()
                return False
            elif isinstance(c, SpecialCard) :
                if c.get_effect() == Effect.CHANGE_COLOR :
                    return True
                if isinstance(lc, SpecialCard) and c.get_effect() == lc.get_effect() :
                    return True
                return False
            else :
                raise Exception("Invalid Card Type")
        result = ActionType.DRAW
        if is_last_player_drop :
            if isinstance(last_card, SpecialCard):
                match last_card.get_effect() :
                    case Effect.BAN :
                        return ActionType.PASS, None
                    case Effect.PLUS_TWO :
                        rule = lambda c, lc : isinstance(c, SpecialCard) and c.get_effect() == Effect.PLUS_TWO
                        result = ActionType.PASS
                    case Effect.CHANGE_COLOR :
                        rule = judge_drop_next
            elif isinstance(last_card, NumericCard):
                rule = judge_drop_next
            else :
                raise Exception("Invalid Card Type")
        else :
            if isinstance(last_card, Card) :
                rule = judge_drop_next
        for card in self.sort_cards(cards) :
            if rule(card, last_card) :
                return ActionType.DROP, card
        return result, None

class Game:
    _player_hands: List[Hand]
    
    def __init__(self, cards: List[Card], num_player: int = 7, hand_card_num: int = 7, dealer_id: int = 0) -> None:
        self._deck = Deck(cards)
        self._players = [Player() for _ in range(num_player)]
        self._player_hands = []
        for _ in range(num_player):
            hand_cards = [self._deck.get_next_card() for _ in range(hand_card_num)]
            self._player_hands.append(Hand(hand_cards))
        self._current_player_id = dealer_id - 1
        self._last_card = None
        self._is_last_player_drop = False
        self._plus_two_cnt = 0
        
    def get_info(self) -> Tuple[int, Card, bool, int, List[Hand]]:
        return self._current_player_id, self._last_card, self._is_last_player_drop, self._plus_two_cnt, self._player_hands

    def is_end(self) -> bool:
        return self._deck.is_empty() or any(hand.is_empty() for hand in self._player_hands)

    def is_not_end(self) -> bool:
        return not self.is_end()

    def current_player_drop_card(self, card: Card) -> None:
        self._player_hands[self._current_player_id].remove_card(card)
        self._last_card = card
        if isinstance(card, SpecialCard) and card.get_effect() == Effect.PLUS_TWO :
            self._plus_two_cnt += 1
        
    def get_scores(self) -> List[int]:
        scores = []
        for hand in self._player_hands :
            numeric_sum, special_sum = 0, 0
            for card in hand.get_cards() :
                if isinstance(card, NumericCard) :
                    numeric_sum += card.get_number()
                elif isinstance(card, SpecialCard) :
                    special_sum += (card.get_effect().value + 1)
                else :
                    raise Exception("Invalid Card Type")
            scores.append(numeric_sum + special_sum * 10)
        return scores
    
    def get_winner(self) -> int:
        if self.is_not_end():
            raise Exception("Game is not end")
        for i, hand in enumerate(self._player_hands) :
            if hand.is_empty() :
                return i
        score_list = self.get_scores()
        min_index, min_score = 0, score_list[0]
        for i, score in enumerate(score_list) :
            if score < min_score :
                min_index, min_score = i, score
        return min_index
        
    
    def turn(self) -> Tuple[Tuple[ActionType, Card | None], Tuple[int, Card, bool, int, List[Hand]], bool]:
        if self.is_end():
            raise Exception("Game is end")
        
        self._current_player_id = (self._current_player_id + 1) % len(self._players)
        action = self._players[self._current_player_id].action(
            self._player_hands[self._current_player_id].get_cards(), self._last_card, self._is_last_player_drop)
        
        if action[0] == ActionType.DRAW:
            self._player_hands[self._current_player_id].add_card(self._deck.get_next_card())
            self._is_last_player_drop = False
        
        elif action[0] == ActionType.DROP:
            self.current_player_drop_card(action[1])
            self._is_last_player_drop = True
        
        elif action[0] == ActionType.PASS:
            self._is_last_player_drop = False
            if self._last_card.get_effect() == Effect.PLUS_TWO :
                for _ in range(self._plus_two_cnt * 2) :
                    if not self._deck.is_empty() :
                        self._player_hands[self._current_player_id].add_card(self._deck.get_next_card())
                    else :
                        break
                self._plus_two_cnt = 0
        
        else:
            raise Exception("Invalid Action")

        return action, self.get_info(), self.is_not_end()