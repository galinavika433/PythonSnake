import random

# Константы игры
SUITS = ['♥️', '♦️', '♣️', '♠️']
RANKS = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return self.__str__()

class DurakGame:
    def __init__(self):
        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(self.deck)
        self.trump_card = self.deck[-1]
        self.trump_suit = self.trump_card.suit
        self.player_hand = []
        self.bot_hand = []
        self.table = [] # Список пар (атака, защита)

    def deal_cards(self):
        while len(self.player_hand) < 6 and self.deck:
            self.player_hand.append(self.deck.pop(0))
        while len(self.bot_hand) < 6 and self.deck:
            self.bot_hand.append(self.deck.pop(0))

    def can_beat(self, attack_card, defend_card):
        if attack_card.suit == defend_card.suit:
            return RANK_VALUES[defend_card.rank] > RANK_VALUES[attack_card.rank]
        if defend_card.suit == self.trump_suit:
            return True
        return False

    def show_state(self):
        print("\n" + "="*30)
        print(f"Козырь: {self.trump_card}")
        print(f"Карт в колоде: {len(self.deck)}")
        print(f"Бот: [{len(self.bot_hand)} карт]")
        print(f"Стол (атака-защита): {self.table}")
        print(f"Ваша рука: {self.player_hand}")
        print("="*30)

    def player_turn(self):
        while True:
            self.show_state()
            print("Ваш ход! Выберите номер карты для атаки (или '0' для конца хода):")
            for i, card in enumerate(self.player_hand):
                print(f"{i+1}: {card}")

            choice = input("> ")
            if choice == '0':
                return "pass"

            try:
                idx = int(choice) - 1
                card = self.player_hand[idx]

                # Проверка: можно ли подкинуть эту карту
                if self.table:
                    table_ranks = [c.rank for pair in self.table for c in pair if c]
                    if card.rank not in table_ranks:
                        print("Нельзя подкинуть эту карту!")
                        continue

                # Бот пытается отбиться
                self.player_hand.pop(idx)
                print(f"Вы ходите: {card}")

                defended = False
                for b_idx, b_card in enumerate(self.bot_hand):
                    if self.can_beat(card, b_card):
                        print(f"Бот отбивается: {b_card}")
                        self.table.append((card, b_card))
                        self.bot_hand.pop(b_idx)
                        defended = True
                        break

                if not defended:
                    print("Бот берет карты!")
                    self.table.append((card, None))
                    # Бот забирает всё со стола позже
                    return "take"
            except:
                print("Ошибка ввода.")

    def play(self):
        print("Игра Дурак начинается!")
        self.deal_cards()

        while self.player_hand and self.bot_hand:
            self.deal_cards()
            res = self.player_turn()

            # Обработка конца хода
            cards_to_take = []
            for attack, defend in self.table:
                cards_to_take.append(attack)
                if defend: cards_to_take.append(defend)

            if res == "take":
                self.bot_hand.extend(cards_to_take)

            self.table = []
            if not self.deck and not self.player_hand:
                print("Вы победили!")
                break
            if not self.deck and not self.bot_hand:
                print("Бот победил!")
                break

if __name__ == "__main__":
    game = DurakGame()
    game.play()