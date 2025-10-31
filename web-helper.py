import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser
import requests
from bs4 import BeautifulSoup
import threading

class WebHelperApp:
    def __init__(self, master):
        self.master = master
        master.title("Web-Помощник")
        master.geometry("600x650")
        master.resizable(False, False)

        master.tk_setPalette(background="#51ca29", foreground='#000000',
                             activeBackground="#359bca", activeForeground='#000000')
        self.font_bold = ("Arial", 10, "bold")
        self.font_normal = ("Arial", 10)

        search_frame = tk.LabelFrame(master, text="Быстрый поиск в браузере", padx=10, pady=10, font=self.font_bold)
        search_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(search_frame, text="Что ищем?", font=self.font_normal).pack(pady=5)
        self.search_entry = tk.Entry(search_frame, width=50, font=self.font_normal)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<Return>", lambda event: self.search_google())

        button_frame = tk.Frame(search_frame)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Google", command=self.search_google, width=12, font=self.font_normal).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Yandex", command=self.search_yandex, width=12, font=self.font_normal).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="DuckDuckGo", command=self.search_duckduckgo, width=12, font=self.font_normal).grid(row=0, column=2, padx=5)

        fav_sites_frame = tk.LabelFrame(master, text="Избранные сайты", padx=10, pady=10, font=self.font_bold)
        fav_sites_frame.pack(pady=10, padx=10, fill="x")

        fav_button_frame = tk.Frame(fav_sites_frame)
        fav_button_frame.pack(pady=5)

        tk.Button(fav_button_frame, text="YouTube", command=lambda: self.open_site("https://www.youtube.com"), width=15, font=self.font_normal).grid(row=0, column=0, padx=5, pady=2)
        tk.Button(fav_button_frame, text="Wikipedia", command=lambda: self.open_site("https://ru.wikipedia.org"), width=15, font=self.font_normal).grid(row=0, column=1, padx=5, pady=2)
        tk.Button(fav_button_frame, text="GitHub", command=lambda: self.open_site("https://github.com"), width=15, font=self.font_normal).grid(row=0, column=2, padx=5, pady=2)
        tk.Button(fav_button_frame, text="Stack Overflow", command=lambda: self.open_site("https://stackoverflow.com"), width=15, font=self.font_normal).grid(row=1, column=0, padx=5, pady=2)
        tk.Button(fav_button_frame, text="Google Docs", command=lambda: self.open_site("https://docs.google.com"), width=15, font=self.font_normal).grid(row=1, column=1, padx=5, pady=2)
        tk.Button(fav_button_frame, text="Gmail", command=lambda: self.open_site("https://mail.google.com"), width=15, font=self.font_normal).grid(row=1, column=2, padx=5, pady=2)

        define_frame = tk.LabelFrame(master, text="Определение слова (без браузера)", padx=10, pady=10, font=self.font_bold)
        define_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(define_frame, text="Введите слово:", font=self.font_normal).pack(pady=5)
        self.define_entry = tk.Entry(define_frame, width=50, font=self.font_normal)
        self.define_entry.pack(pady=5)
        self.define_entry.bind("<Return>", lambda event: self.start_define_word_thread())

        tk.Button(define_frame, text="Найти определение", command=self.start_define_word_thread, font=self.font_normal).pack(pady=5)

        self.definition_text = scrolledtext.ScrolledText(define_frame, wrap=tk.WORD, width=60, height=8, font=self.font_normal)
        self.definition_text.pack(pady=10)
        self.definition_text.insert(tk.END, "Здесь появится определение слова...")
        self.definition_text.config(state=tk.DISABLED)

    def get_search_query(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите что-нибудь для поиска.")
            return None
        return query

    def search_google(self):
        query = self.get_search_query()
        if query:
            webbrowser.open_new_tab(f"https://www.google.com/search?q={query}")

    def search_yandex(self):
        query = self.get_search_query()
        if query:
            webbrowser.open_new_tab(f"https://yandex.ru/search/?text={query}")

    def search_duckduckgo(self):
        query = self.get_search_query()
        if query:
            webbrowser.open_new_tab(f"https://duckduckgo.com/?q={query}")

    def open_site(self, url):
        webbrowser.open_new_tab(url)

    def start_define_word_thread(self):
        word = self.define_entry.get().strip()
        if not word:
            self.update_definition_text("Пожалуйста, введите слово для определения.")
            return

        self.update_definition_text("Ищу определение... Пожалуйста, подождите.")
        threading.Thread(target=self._define_word, args=(word,)).start()

    def _define_word(self, word):
        try:
            url = f"https://ru.wiktionary.org/wiki/{word}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            definition_sections = soup.find_all(['h2', 'h3'], text=lambda t: t and 'Значение' in t)
            
            definitions = []
            if definition_sections:
                for section in definition_sections:
                    current_element = section.find_next_sibling()
                    while current_element and current_element.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        if current_element.name in ['ol', 'ul']:
                            for li in current_element.find_all('li', recursive=False):
                                def_text = li.get_text(separator=" ", strip=True)
                                def_text = self._clean_definition_text(def_text)
                                if def_text:
                                    definitions.append(f"• {def_text}")
                            break
                        current_element = current_element.find_next_sibling()
            
            if definitions:
                self.update_definition_text(f"Определение слова '{word}':\n\n" + "\n".join(definitions))
            else:
                self.update_definition_text(f"Не удалось найти чёткого определения для слова '{word}'.\nПопробуйте поискать в браузере или введите другое слово.")

        except requests.exceptions.Timeout:
            self.update_definition_text("Превышено время ожидания при запросе к Викисловарю. Проверьте ваше интернет-соединение.")
        except requests.exceptions.RequestException as e:
            self.update_definition_text(f"Ошибка при подключении к Викисловарю: {e}\nВозможно, проблемы с интернетом или сайтом.")
        except Exception as e:
            self.update_definition_text(f"Произошла непредвиденная ошибка: {e}")

    def _clean_definition_text(self, text):
        import re
        cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text).strip()
        return cleaned_text

    def update_definition_text(self, text):
        self.definition_text.config(state=tk.NORMAL)
        self.definition_text.delete(1.0, tk.END)
        self.definition_text.insert(tk.END, text)
        self.definition_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebHelperApp(root)
    root.mainloop()
