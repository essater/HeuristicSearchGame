import random
import tkinter as tk
from typing import List

# ---- Kart Sınıfı (Türkçeleştirilmiş) ----
class Card:
    def __init__(self, suit, value):
        self.suit = suit  # Kupa, Maça, Sinek, Karo
        self.value = value  # 2-10, J, Q, K, A

    def __str__(self):
        return f"{self.suit} {self.value}"

    def get_value(self):
        if self.value in ['J', 'Q', 'K']:
            return 10
        elif self.value == 'A':
            return 1
        else:
            return int(self.value)

    def __eq__(self, other):
        return isinstance(other, Card) and self.suit == other.suit and self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.value))

# ---- Deste Oluşturma ----
def create_deck():
    suits = ['Kupa', 'Maça', 'Sinek', 'Karo']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [Card(suit, value) for suit in suits for value in values]
    random.shuffle(deck)
    return deck

# ---- El Değerlendirme ----
def evaluate_hand(hand: List[Card], difficulty: str) -> dict:
    suit_counts = {}
    for card in hand:
        suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
    best_suit = max(suit_counts, key=suit_counts.get)
    return {
        'suit_counts': suit_counts,
        'best_suit': best_suit,
        'best_suit_count': suit_counts[best_suit]
    }

# ---- Kazanma Olasılığı ----
def get_winning_probability(hand: List[Card], remaining_cards: int, difficulty: str) -> float:
    metrics = evaluate_hand(hand, difficulty)
    target_cards = 3 if difficulty == 'easy' else 6
    best_suit_count = metrics['best_suit_count']
    cards_needed = target_cards - best_suit_count
    if cards_needed <= 0:
        return 1.0
    return max(0.0, min(1.0, (remaining_cards / 13) / cards_needed))

# ---- AI Kart Seçimi ----
def choose_card_to_discard(hand: List[Card], new_card: Card, deck: List[Card], difficulty: str) -> (Card, float):
    full_hand = hand + [new_card]
    probability = get_winning_probability(full_hand, len(deck), difficulty)
    metrics = evaluate_hand(full_hand, difficulty)
    best_suit = metrics['best_suit']

    if probability < 0.3:
        return max(full_hand, key=lambda x: x.get_value()), probability

    non_best_suit_cards = [card for card in full_hand if card.suit != best_suit]
    if non_best_suit_cards:
        return max(non_best_suit_cards, key=lambda x: x.get_value()), probability

    return max(full_hand, key=lambda x: x.get_value()), probability

# ---- Deste Dağıtımı ----
def deal_cards(deck, num_cards=3):
    player_hand = deck[:num_cards]
    computer_hand = deck[num_cards:num_cards * 2]
    remaining_deck = deck[num_cards * 2:]
    return player_hand, computer_hand, remaining_deck

# ---- Kazanan Kontrolü ----
def check_winner(hand: List[Card], difficulty: str) -> bool:
    metrics = evaluate_hand(hand, difficulty)
    return metrics['best_suit_count'] >= (3 if difficulty == 'easy' else 6)

# ---- Skor Hesaplama ----
def calculate_score(hand: List[Card]) -> int:
    return sum(card.get_value() for card in hand)

# ---- Kazanan Gösterimi ----
def show_winner(root, message, player_hand, computer_hand, difficulty):
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text=message, font=("Arial", 14, "bold"), fg="green").pack(pady=10)

    hands_frame = tk.Frame(root)
    hands_frame.pack(pady=5)

    # Oyuncu Eli
    tk.Label(hands_frame, text="Oyuncu Eli:", font=("Arial", 12, "bold"), fg="green").pack()
    player_cards_frame = tk.Frame(hands_frame)
    player_cards_frame.pack()
    for card in player_hand:
        tk.Label(player_cards_frame, text=str(card), width=15, height=2,
                 relief="ridge", font=("Courier", 10), bg="#e8f4f8").pack(side=tk.LEFT, padx=2)

    # Bilgisayar Eli
    tk.Label(hands_frame, text="Bilgisayar Eli:", font=("Arial", 12, "bold"), fg="blue").pack(pady=5)
    computer_cards_frame = tk.Frame(hands_frame)
    computer_cards_frame.pack()
    for card in computer_hand:
        tk.Label(computer_cards_frame, text=str(card), width=15, height=2,
                 relief="ridge", font=("Courier", 10), bg="#f8e8e8").pack(side=tk.LEFT, padx=2)

    if "puan" in message.lower() or "berabere" in message.lower():
        stats_frame = tk.Frame(root)
        stats_frame.pack(pady=10)
        player_points = calculate_score(player_hand)
        computer_points = calculate_score(computer_hand)
        tk.Label(stats_frame, text=f"Oyuncu toplam puan: {player_points}", font=("Arial", 11), fg="blue").pack()
        tk.Label(stats_frame, text=f"Bilgisayar toplam puan: {computer_points}", font=("Arial", 11), fg="red").pack()

# ---- Oyun Oynama ----
def start_game(difficulty):
    deck = create_deck()
    num_cards = 3 if difficulty == 'easy' else 6
    player_hand, computer_hand, deck = deal_cards(deck, num_cards=num_cards)
    discard_pile = []
    last_new_player_card = None
    last_new_computer_card = None

    def play_turn():
        nonlocal deck, player_hand, computer_hand, last_new_player_card, last_new_computer_card
        if len(deck) < 2:
            end_game()
            return

        new_player_card = deck.pop(0)
        new_computer_card = deck.pop(0)
        last_new_player_card = new_player_card
        last_new_computer_card = new_computer_card

        def on_player_discard(player_discard):
            if player_discard == new_player_card:
                discard_pile.append(new_player_card)
            else:
                player_hand.remove(player_discard)
                player_hand.append(new_player_card)
                discard_pile.append(player_discard)

            temp_hand = computer_hand + [new_computer_card]
            computer_discard, computer_prob = choose_card_to_discard(computer_hand, new_computer_card, deck, difficulty)
            temp_hand.remove(computer_discard)
            computer_hand.clear()
            computer_hand.extend(temp_hand)
            discard_pile.append(computer_discard)

            if check_winner(player_hand, difficulty):
                show_winner(root, "Oyuncu kazandı!", player_hand, computer_hand, difficulty)
            elif check_winner(computer_hand, difficulty):
                show_winner(root, "Bilgisayar kazandı!", player_hand, computer_hand, difficulty)
            elif not deck:
                end_game()
            else:
                play_turn()

        render_turn(last_new_player_card, last_new_computer_card, player_hand + [new_player_card], computer_hand + [new_computer_card], discard_pile, on_player_discard)

    def render_turn(player_new_card, comp_new_card, hand, comp_hand, discard_pile, discard_callback):
        for widget in root.winfo_children():
            widget.destroy()

        frame_top = tk.Frame(root)
        frame_top.pack(pady=10)
        tk.Label(frame_top, text="Bilgisayara Gelen Kart: " + str(comp_new_card), font=("Arial", 12, "italic"), fg="blue").pack()
        tk.Label(frame_top, text="Oyuncuya Gelen Kart: " + str(player_new_card), font=("Arial", 12, "italic"), fg="green").pack()

        tk.Label(root, text="Kart seçin (yeni kartı da atabilirsiniz):", font=("Arial", 12)).pack()

        frame_player = tk.Frame(root)
        frame_player.pack(pady=5)

        row1 = tk.Frame(frame_player)
        row1.pack()
        for card in hand:
            if card != player_new_card:
                btn = tk.Button(row1, text=str(card), width=18, height=2, relief="groove",
                                font=("Courier", 10), command=lambda c=card: discard_callback(c))
                btn.pack(side=tk.LEFT, padx=4)

        row2 = tk.Frame(frame_player)
        row2.pack(pady=5)
        btn_new = tk.Button(row2, text=str(player_new_card), width=18, height=2, relief="groove",
                            font=("Courier", 10), bg="#d0f0d0", command=lambda c=player_new_card: discard_callback(c))
        btn_new.pack(side=tk.LEFT, padx=4)

        tk.Label(root, text="\nBilgisayar Eli:", font=("Arial", 12, "bold"), fg="blue").pack()
        frame_computer = tk.Frame(root)
        frame_computer.pack()
        for card in comp_hand:
            if card != comp_new_card:
                lbl = tk.Label(frame_computer, text=str(card), width=18, height=2, relief="ridge",
                               font=("Courier", 10), bg="#f0f0f0")
                lbl.pack(side=tk.LEFT, padx=4)

        row2_comp = tk.Frame(root)
        row2_comp.pack(pady=5)
        tk.Label(row2_comp, text=str(comp_new_card), width=18, height=2, relief="ridge",
                 font=("Courier", 10), bg="#a8c0ff").pack(side=tk.LEFT, padx=4)

        tk.Label(root, text="\nAtılan Kartlar:", font=("Arial", 11, "bold"), fg="darkgray").pack()
        frame_discard = tk.Frame(root)
        frame_discard.pack()
        for card in discard_pile[-8:]:
            lbl = tk.Label(frame_discard, text=str(card), width=14, relief="sunken",
                           font=("Courier", 9), bg="#e6e6e6")
            lbl.pack(side=tk.LEFT, padx=2)

    def end_game():
        player_score = calculate_score(player_hand)
        computer_score = calculate_score(computer_hand)
        if player_score < computer_score:
            show_winner(root, f"Oyun bitti! Oyuncu kazandı ({player_score} vs {computer_score})", player_hand, computer_hand, difficulty)
        elif computer_score < player_score:
            show_winner(root, f"Oyun bitti! Bilgisayar kazandı ({computer_score} vs {player_score})", player_hand, computer_hand, difficulty)
        else:
            show_winner(root, "Berabere!", player_hand, computer_hand, difficulty)

    root = tk.Tk()
    root.title("Zeki Kart Oyunu")
    root.configure(bg="white")
    play_turn()
    root.mainloop()

# ---- Zorluk Seçim Ekranı ----
def select_difficulty():
    def start_easy():
        difficulty_window.destroy()
        start_game('easy')

    def start_hard():
        difficulty_window.destroy()
        start_game('hard')

    difficulty_window = tk.Tk()
    difficulty_window.title("Zorluk Seçimi")
    tk.Label(difficulty_window, text="Zorluk seviyesini seçin:", font=("Arial", 13)).pack(pady=10)
    tk.Button(difficulty_window, text="Kolay (3 kart)", font=("Arial", 12), width=20, command=start_easy).pack(pady=5)
    tk.Button(difficulty_window, text="Zor (6 kart)", font=("Arial", 12), width=20, command=start_hard).pack(pady=5)
    difficulty_window.mainloop()

# ---- Oyunu Başlat ----
if __name__ == "__main__":
    select_difficulty()
