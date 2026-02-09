import secrets
import requests
import tkinter as tk
from tkinter import font

class NewsWordleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Top 5 News Wordle")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2d2d2d") 
        
        self.articles = []
        self.current_index = 0
        self.target = ""
        self.headline_body = ""
        self.source_name = ""
        self.revealed_hint = ""

        # UI Fonts
        self.header_font = font.Font(family="Courier", size=36, weight="bold")
        self.subhead_font = font.Font(family="Courier", size=20, weight="bold")
        self.headline_font = font.Font(family="Verdana", size=24)
        self.source_font = font.Font(family="Verdana", size=18, slant="italic")
        self.input_font = font.Font(family="Courier", size=48, weight="bold")
        self.button_font = font.Font(family="Courier", size=24, weight="bold")

        # --- UI LAYOUT ---
        tk.Label(root, text="TOP 5 DAILY HEADLINES", font=self.header_font, 
                 bg="#2d2d2d", fg="#00ff00").pack(pady=(60, 5))

        self.label_subhead = tk.Label(root, text="", font=self.subhead_font, 
                                      bg="#2d2d2d", fg="#00ff00")
        self.label_subhead.pack(pady=(0, 5))

        self.label_counter = tk.Label(root, text="LOADING...", font=("Courier", 16), 
                                      bg="#2d2d2d", fg="#888")
        self.label_counter.pack()

        self.label_headline = tk.Label(root, text="", wraplength=850, 
                                       font=self.headline_font, bg="#2d2d2d", fg="#ffffff", justify="center")
        self.label_headline.pack(pady=40)

        self.label_source = tk.Label(root, text="", font=self.source_font, 
                                     bg="#2d2d2d", fg="#888888")
        self.label_source.pack(pady=(0, 50))

        # Input Area
        self.entry_guess = tk.Entry(root, font=self.input_font, justify='center', 
                                    width=18, fg="#00ff00", bg="#1a1a1a", 
                                    insertbackground="#00ff00", relief="flat")
        self.entry_guess.pack(pady=10)
        
        self.placeholder = "TYPE ANSWER"
        self.add_placeholder(None) # Initial setup
        
        # Binding events
        self.entry_guess.bind("<FocusIn>", self.clear_placeholder)
        self.entry_guess.bind("<FocusOut>", self.add_placeholder)
        self.entry_guess.bind('<Return>', lambda event: self.check_guess())

        self.btn_guess = tk.Button(root, text="SUBMIT GUESS", command=self.check_guess, 
                                   font=self.button_font, fg="#1a1a1a", bg="#00ff00", 
                                   activebackground="#00cc00", activeforeground="#1a1a1a",
                                   highlightthickness=0, bd=0, padx=80, pady=30, cursor="hand2")
        self.btn_guess.pack(pady=50)

        self.btn_skip = tk.Button(root, text="SKIP TO NEXT >", command=self.load_next_game, 
                                  font=("Courier", 14, "bold"), fg="#666", bg="#2d2d2d",
                                  activebackground="#2d2d2d", activeforeground="#ffffff", 
                                  highlightthickness=0, bd=0, cursor="hand2")
        self.btn_skip.place(relx=1.0, rely=1.0, anchor="se", x=-40, y=-40)

        self.fetch_top_5_news()

    def clear_placeholder(self, event):
        """Standard clear logic"""
        if self.entry_guess.get() == self.placeholder:
            self.entry_guess.delete(0, tk.END)
            self.entry_guess.config(fg="#00ff00")

    def add_placeholder(self, event):
        """Standard add logic"""
        if not self.entry_guess.get():
            self.entry_guess.insert(0, self.placeholder)
            self.entry_guess.config(fg="#444")

    def fetch_top_5_news(self):
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={secrets.NEWS_API_KEY}"
        try:
            response = requests.get(url).json()
            raw_articles = response.get("articles", [])
            count = 0
            for art in raw_articles:
                if count >= 5: break
                parts = art["title"].rsplit(" - ", 1)
                title_text = parts[0]
                source_text = parts[1] if len(parts) > 1 else "Unknown"
                target = self.get_target_word(title_text)
                if target:
                    self.articles.append({"title": title_text, "source": source_text, "target": target})
                    count += 1
            self.load_next_game()
        except Exception:
            self.label_headline.config(text="OFFLINE / ERROR", fg="red")

    def get_target_word(self, title):
        words = title.split()
        for word in words[1:]:
            clean = word.strip('.,?!"()—')
            if clean.istitle() and len(clean) > 4:
                return clean
        return None

    def load_next_game(self):
        if self.current_index >= len(self.articles):
            self.show_custom_popup("FINISH", "MISSION ACCOMPLISHED\nYOU DECODED THE DAILY TOP 5", is_final=True)
            return
            
        current_data = self.articles[self.current_index]
        self.target = current_data["target"]
        self.headline_body = current_data["title"]
        self.source_name = f"SOURCE: {current_data['source']}"
        
        self.label_subhead.config(text=f"GUESS THE {len(self.target)} LETTER SUBJECT")
        self.label_counter.config(text=f"HEADLINE {self.current_index + 1} OF 5")
        
        self.revealed_hint = "_" * len(self.target)
        self.update_display()
        
        # --- THE FIX: Hard Reset for new round ---
        self.entry_guess.delete(0, tk.END)
        self.entry_guess.insert(0, self.placeholder)
        self.entry_guess.config(fg="#444")
        self.root.focus_set() # Moves focus away from the box so FocusIn works again
        
        self.current_index += 1

    def update_display(self):
        masked_word = " ".join(self.revealed_hint)
        masked_title = self.headline_body.replace(self.target, masked_word)
        self.label_headline.config(text=masked_title)
        self.label_source.config(text=self.source_name)

    def check_guess(self):
        user_guess = self.entry_guess.get().strip()
        if user_guess == self.placeholder: return

        if user_guess.lower() == self.target.lower():
            self.show_custom_popup("CORRECT!", self.headline_body)
        else:
            self.reveal_one_letter()
            self.update_display()
            # Wrong guess reset
            self.entry_guess.delete(0, tk.END)
            self.entry_guess.insert(0, self.placeholder)
            self.entry_guess.config(fg="#444")
            self.root.focus_set()

    def reveal_one_letter(self):
        hint_list = list(self.revealed_hint)
        for i in range(len(hint_list)):
            if hint_list[i] == "_":
                hint_list[i] = self.target[i]
                break
        self.revealed_hint = "".join(hint_list)

    def show_custom_popup(self, title, message, is_final=False):
        win = tk.Toplevel()
        win.title(title)
        win.geometry("800x500")
        win.configure(bg="#1a1a1a")
        win.transient(self.root) 
        win.grab_set() 
        
        tk.Label(win, text=title, font=("Courier", 32, "bold"), bg="#1a1a1a", fg="#00ff00").pack(pady=20)
        
        if not is_final:
            tk.Label(win, text=self.target.upper(), font=("Courier", 60, "bold"), bg="#1a1a1a", fg="#ffffff").pack(pady=5)
        
        tk.Label(win, text=message, font=("Verdana", 20), bg="#1a1a1a", fg="#aaaaaa", 
                 wraplength=750, justify="center").pack(pady=20)
        
        btn_text = "CLOSE GAME" if is_final else "NEXT HEADLINE"
        btn_cmd = self.root.destroy if is_final else lambda: [win.destroy(), self.load_next_game()]
        
        pop_btn = tk.Button(win, text=btn_text, command=btn_cmd, font=("Courier", 20, "bold"), 
                            fg="#1a1a1a", bg="#00ff00", relief="flat", padx=40, pady=20)
        pop_btn.pack(pady=20)
        
        win.bind('<Return>', lambda e: btn_cmd())
        pop_btn.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsWordleApp(root)
    root.mainloop()