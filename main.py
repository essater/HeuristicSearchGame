import random
import tkinter as tk
from typing import List
from PIL import Image, ImageTk


# ---- Kart Sınıfı ----
class Card:
    def __init__(self, suit, value):
        self.suit = suit  # Kupa, Maça, Sinek, Karo
        self.value = value  # 2-10, J, Q, K, A

    def __str__(self):
        return f"{self.suit} {self.value}"

    def get_value(self):
        if self.value == 'J':
            return 11
        elif self.value == 'Q':
            return 12
        elif self.value == 'K':
            return 13
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
def choose_card_to_discard(
        hand: List[Card],
        new_card: Card,
        deck: List[Card],
        discard_pile: List[Card],
        difficulty: str,
        opponent_hand: List[Card]
) -> (Card, float):

    full_hand = hand + [new_card]
    probability = get_winning_probability(full_hand, len(deck), difficulty)

    if difficulty == 'easy':
        metrics = evaluate_hand(full_hand, difficulty)
        best_suit = metrics['best_suit']
        if probability < 0.3:
            return max(full_hand, key=lambda x: x.get_value()), probability
        non_best_suit_cards = [card for card in full_hand if card.suit != best_suit]
        if non_best_suit_cards:
            return max(non_best_suit_cards, key=lambda x: x.get_value()), probability
        else:
            return max(full_hand, key=lambda x: x.get_value()), probability

    # HARD mod
    target = 6
    total_per_suit = 13
    deck_remaining = len(deck)
    suits_in_hand = set(card.suit for card in full_hand)
    suit_scores = {}

    for suit in suits_in_hand:
        count_in_hand = sum(1 for card in full_hand if card.suit == suit)
        count_in_discard = sum(1 for card in discard_pile if card.suit == suit)
        count_in_opponent = sum(1 for card in opponent_hand if card.suit == suit)

        count_remaining = total_per_suit - count_in_hand - count_in_discard - count_in_opponent
        need = target - count_in_hand

        # Dinamik ağırlıklar
        elde_weight = 0.5 + 0.3 * (count_in_hand / target) + 0.2 * (1 - len(deck) / 52)
        elde_weight = min(1.0, max(0.0, elde_weight))  # Güvenlik sınırı
        deste_weight = 1 - elde_weight

        # Skor hesabı
        if count_remaining <= 0 or need > deck_remaining: #4 tane kartımız var ancak destede artık yok çekemiyoruz hemen bu suits i terk et.
            score = 0.0
        elif count_in_hand >= 4 or need <= 0:
            score = 1.0
        else:
            score = elde_weight * (count_in_hand / target) + deste_weight * (count_remaining / deck_remaining)

        score = round(score, 4)
        suit_scores[suit] = score

        print(f"[DEBUG] {suit}: elde={count_in_hand}, atıldı={count_in_discard}, kalan={count_remaining}, gerekli={need}, elde_w={elde_weight:.3f}, deste_w={deste_weight:.3f}, skor={score}")

    # En düşük skora sahip suit(ler)
    min_score = min(suit_scores.values())
    tied_weak_suits = [suit for suit, score in suit_scores.items() if score == min_score]

    # Bu suitlere ait eldeki kartlar
    discard_candidates = [card for card in full_hand if card.suit in tied_weak_suits]

    if discard_candidates:
        discard_card = max(discard_candidates, key=lambda x: x.get_value())
        print(f"[DEBUG] En düşük skor suit(ler): {tied_weak_suits} → Atılacak kart: {discard_card}")
        print()
    else:
        discard_card = max(full_hand, key=lambda x: x.get_value())
        print(f"[DEBUG] Uyarı: discard_candidates boş! Fallback → Atılacak kart: {discard_card}")

    return discard_card, probability



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
            computer_discard, computer_prob = choose_card_to_discard(computer_hand, new_computer_card, deck, discard_pile, difficulty, player_hand)


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

    def get_card_image(card: Card, size=(80, 120)):
        suit_map = {
            "Kupa": "hearts",
            "Maça": "spades",
            "Sinek": "clubs",
            "Karo": "diamonds"
        }

        value_map = {
            "A": "ace",
            "J": "jack",
            "Q": "queen",
            "K": "king"
        }

        suit = suit_map[card.suit]
        value = value_map.get(card.value, card.value)
        file_path = f"cards/{value}_of_{suit}.png"

        try:
            img = Image.open(file_path).resize(size, Image.Resampling.LANCZOS)

            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"[ERROR] Görsel yüklenemedi: {file_path} → {e}")
            return None

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
                img = get_card_image(card)
                if img:
                    btn = tk.Button(row1, image=img, relief="groove", command=lambda c=card: discard_callback(c))
                    btn.image = img  # ⚠️ referansı koru
                    btn.pack(side=tk.LEFT, padx=4)

        row2 = tk.Frame(frame_player)
        row2.pack(pady=5)
        img_new = get_card_image(player_new_card)
        if img_new:
            btn_new = tk.Button(row2, image=img_new, relief="groove", bg="#d0f0d0",
                                command=lambda c=player_new_card: discard_callback(c))
            btn_new.image = img_new
            btn_new.pack(side=tk.LEFT, padx=4)


        tk.Label(root, text="\nBilgisayar Eli:", font=("Arial", 12, "bold"), fg="blue").pack()
        frame_computer = tk.Frame(root)
        frame_computer.pack()
        for card in comp_hand:
            if card != comp_new_card:
                img = get_card_image(card)
                if img:
                    lbl = tk.Label(frame_computer, image=img, relief="ridge", bg="#f0f0f0")
                    lbl.image = img  # ⚠️ Referansı korumazsan görsel görünmez
                    lbl.pack(side=tk.LEFT, padx=4)

        row2_comp = tk.Frame(root)
        row2_comp.pack(pady=5)
        img_comp = get_card_image(comp_new_card)
        if img_comp:
            lbl = tk.Label(row2_comp, image=img_comp, relief="ridge", bg="#a8c0ff")
            lbl.image = img_comp
            lbl.pack(side=tk.LEFT, padx=4)

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
    root.title("Sezgisel Kart Oyunu")
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
