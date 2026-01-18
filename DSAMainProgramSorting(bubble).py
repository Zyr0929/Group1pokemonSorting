import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import urllib.request
import io
import copy

# --- 1. CONFIG AT DATA ---

TYPE_RANK = {
    "Normal": 1, "Fire": 2, "Water": 3, "Electric": 4, "Grass": 5, 
    "Ice": 6, "Fighting": 7, "Poison": 8, "Ground": 9, "Flying": 10, 
    "Psychic": 11, "Bug": 12, "Rock": 13, "Ghost": 14, "Dragon": 15, 
    "Dark": 16, "Steel": 17, "Fairy": 18
}

# --- LISTAHAN---
MASTER_DECK = [
    {"id": 658, "name": "Greninja", "stage": 2, "gen": 6, "hp": 72, "type": ["Water", "Dark"]},
    {"id": 1, "name": "Bulbasaur", "stage": 0, "gen": 1, "hp": 45, "type": ["Grass", "Poison"]},
    {"id": 448, "name": "Lucario", "stage": 1, "gen": 4, "hp": 70, "type": ["Fighting", "Steel"]},
    {"id": 25, "name": "Pikachu", "stage": 0, "gen": 1, "hp": 35, "type": ["Electric", None]},
    {"id": 282, "name": "Gardevoir", "stage": 2, "gen": 3, "hp": 68, "type": ["Psychic", "Fairy"]},
    {"id": 4, "name": "Charmander", "stage": 0, "gen": 1, "hp": 39, "type": ["Fire", None]},
    {"id": 656, "name": "Froakie", "stage": 0, "gen": 6, "hp": 41, "type": ["Water", None]},
    {"id": 2, "name": "Ivysaur", "stage": 1, "gen": 1, "hp": 60, "type": ["Grass", "Poison"]},
    {"id": 571, "name": "Zoroark", "stage": 1, "gen": 5, "hp": 60, "type": ["Dark", None]},
    {"id": 6, "name": "Charizard", "stage": 2, "gen": 1, "hp": 78, "type": ["Fire", "Flying"]},
    {"id": 447, "name": "Riolu", "stage": 0, "gen": 4, "hp": 40, "type": ["Fighting", None]},
    {"id": 395, "name": "Empoleon", "stage": 2, "gen": 4, "hp": 84, "type": ["Water", "Steel"]},
    {"id": 657, "name": "Frogadier", "stage": 1, "gen": 6, "hp": 54, "type": ["Water", None]},
    {"id": 257, "name": "Blaziken", "stage": 2, "gen": 3, "hp": 80, "type": ["Fire", "Fighting"]},
    {"id": 133, "name": "Eevee", "stage": 0, "gen": 1, "hp": 55, "type": ["Normal", None]},
    {"id": 700, "name": "Sylveon", "stage": 1, "gen": 6, "hp": 95, "type": ["Fairy", None]},
    {"id": 248, "name": "Dark Tyranitar", "stage": 2, "gen": 2, "hp": 100, "type": ["Dark", None]},
    {"id": 63, "name": "Abra", "stage": 0, "gen": 1, "hp": 25, "type": ["Psychic", None]}
]


pokemon_deck = copy.deepcopy(MASTER_DECK)

# --- 2. LOGIC DAW ---

def get_type_rank_val(p_type):
    primary = p_type[0] if isinstance(p_type, list) else p_type
    return TYPE_RANK.get(primary, 99)

def should_swap(a, b, choice):
    # 1. Stage
    if choice == 'Stage': return a['stage'] > b['stage']
    # 2. Gen
    elif choice == 'Gen': return a['gen'] > b['gen']
    # 3. HP
    elif choice == 'HP': return a['hp'] > b['hp']
    # 4. Type
    elif choice == 'Type': return get_type_rank_val(a['type']) > get_type_rank_val(b['type'])
    # 5. Name
    elif choice == 'Name': return a['name'] > b['name']
    # 6. OVERALL (Cascading Priority)
    elif choice == 'Overall':
        if a['stage'] != b['stage']: return a['stage'] > b['stage']
        if a['gen'] != b['gen']: return a['gen'] > b['gen']
        if a['hp'] != b['hp']: return a['hp'] > b['hp']
        rank_a, rank_b = get_type_rank_val(a['type']), get_type_rank_val(b['type'])
        if rank_a != rank_b: return rank_a > rank_b
        return a['name'] > b['name']
    return False

# --- 3. GUI & VISUALS ---

image_store = {}

def get_img(p_id, size=(50, 50)):
    key = (p_id, size)
    if key in image_store: return image_store[key]
    try:
        url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{p_id}.png"
        with urllib.request.urlopen(url) as u:
            data = u.read()
        img = Image.open(io.BytesIO(data)).resize(size, Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        image_store[key] = tk_img
        return tk_img
    except Exception as e:
        print(f"Img Error {p_id}: {e}")
        return None

def refresh_ui(criteria):
    global pokemon_deck 
    
    for w in scroll_frame.winfo_children():
        w.destroy()
        
    for idx, p in enumerate(pokemon_deck, 1):
        row = tk.Frame(scroll_frame, bg="#333333", relief="flat")
        row.pack(fill="x", pady=3, padx=10)
        
        # Rank Number
        tk.Label(row, text=f"{idx:02d}", font=("Consolas", 11), fg="#777", bg="#333", width=4).pack(side="left")
        
        # Image
        icon = get_img(p['id'], (50, 50))
        if icon:
            tk.Label(row, image=icon, bg="#333").pack(side="left", padx=8)
        
        # Name
        tk.Label(row, text=p['name'], font=("Segoe UI", 12, "bold"), fg="#87CEFA", bg="#333", width=15, anchor="w").pack(side="left")
        
        # Stats
        detail_str = f"| Stg:{p['stage']} Gen:{p['gen']} HP:{p['hp']} {p['type'][0]}"
        tk.Label(row, text=detail_str, font=("Consolas", 10), fg="white", bg="#333").pack(side="left", padx=10)

def run_simulation(mode):
    global pokemon_deck # <--- CRITICAL: Allows us to modify the real list
    
    print(f"--- Button Clicked: {mode} ---")
    print("Resetting to Master Deck...")
    
    # 1. RESET: Overwrite the current deck with a fresh copy of the Master
    pokemon_deck = copy.deepcopy(MASTER_DECK)
    
    # 2. SORT: Perform Bubble Sort on the fresh list
    n = len(pokemon_deck)
    swaps, comps = 0, 0
    start = time.perf_counter()

    for i in range(n):
        for j in range(0, n - i - 1):
            comps += 1
            if should_swap(pokemon_deck[j], pokemon_deck[j+1], mode):
                pokemon_deck[j], pokemon_deck[j+1] = pokemon_deck[j+1], pokemon_deck[j]
                swaps += 1
    
    duration = time.perf_counter() - start
    print(f"Sort Complete. Swaps: {swaps}")
    
    # 3. UPDATE STATS UI
    stats_display.config(text=f"SORTED BY: {mode.upper()} | Time: {duration:.4f}s | Swaps: {swaps} | Comparisons: {comps}")
    
    # 4. UPDATE TOP FEATURED POKEMON
    winner = pokemon_deck[0]
    big_img = get_img(winner['id'], (120, 120))
    if big_img:
        big_sprite_label.config(image=big_img)
        big_sprite_label.image = big_img
    top_info_label.config(text=f"Rank 1: {winner['name']}")
    
    # 5. REDRAW LIST
    refresh_ui(mode)

# --- 4. MAIN WINDOW SETUP ---
root = tk.Tk()
root.title("Pokémon Sorter ng Group 1 HAHAHAHAHAHAHAHA")
root.geometry("800x800")
root.configure(bg="#1a1a1a")

# Top Section
featured_frame = tk.Frame(root, bg="#1a1a1a")
featured_frame.pack(pady=10)
big_sprite_label = tk.Label(featured_frame, bg="#1a1a1a")
big_sprite_label.pack()
top_info_label = tk.Label(featured_frame, text="Ready to Sort", font=("Verdana", 14, "bold"), fg="#FFDE00", bg="#1a1a1a")
top_info_label.pack()

stats_display = tk.Label(root, text="Select a category below...", font=("Consolas", 10), fg="#00FF7F", bg="#1a1a1a")
stats_display.pack(pady=5)

# Buttons
btn_container = tk.Frame(root, bg="#1a1a1a")
btn_container.pack(pady=10)
btn_configs = [('Stage', 0, 0), ('Gen', 0, 1), ('HP', 0, 2), ('Type', 1, 0), ('Name', 1, 1), ('Overall', 1, 2)]

for txt, r, c in btn_configs:
    color = "#FFD700" if txt == 'Overall' else "#e0e0e0"
    btn = tk.Button(btn_container, text=txt, width=12, bg=color, font=("Arial", 9, "bold"),
                    command=lambda m=txt: run_simulation(m))
    btn.grid(row=r, column=c, padx=5, pady=5)

# Scrollable List Area
main_frame = tk.Frame(root, bg="#262626")
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

canvas = tk.Canvas(main_frame, bg="#262626", highlightthickness=0)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="#262626")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfig(frame_window_id, width=event.width)

frame_window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_window_id, width=e.width))
scroll_frame.bind("<Configure>", on_frame_configure)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Start
run_simulation('Overall')
root.mainloop()
