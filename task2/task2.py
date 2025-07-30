from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import string
import matplotlib.pyplot as plt
from colorama import Fore, Style, init
init(autoreset=True)  # Ініціалізація colorama для автоматичного скидання кольорів 



def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        print(f"This is name of exeption: {e}")
        return None



# Додано для видалення знаків пунктуації
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


# Просте створення СТОП-СЛІВ, щоб не враховувати їх у підрахунках, просто для прикладу
STOP_WORDS = {"the", "and", "is", "in", "to", "of", "a", "on", "for", "with", "as", "by", "at", "it", "that", "this", "an", "be", "are", "was", "were", "or", "not", "but", "if", "so", "which", "there", "when", "who", "what", "where", "why", "how", "he", "she", "they", "we", "you", "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their", "these", "those", "such", "more", "most", "some", "any", "no", "yes", "like", "just", "than", "then", "now", "up", "down", "out", "over", "under", "again", "also", "very", "even", "back", "after", "I", "i"}
def map_function(word):
    word = word.lower().strip(",.?!;:") # Видалення знаків пунктуації з початку та кінця слова(github)
    if word in STOP_WORDS or not word:
        return None
    return word.lower(), 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_value):
    key, values = key_value
    return key, sum(values)


# Виконання MapReduce модифіковано для цього варіанту коду
def map_reduce(text, search_words=None):
    # Видалення знаків пунктуації
    text = remove_punctuation(text)
    words = text.split()
    # Якщо задано список слів для пошуку, враховувати тільки ці слова
    if search_words:
        words = [word for word in words if word in search_words]

    # Паралельний маппінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(filter(None, executor.map(map_function, words))) # Додано filter у зв'язку з додаванням STOP_WORDS

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Пералельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

        return dict(reduced_values)
    
def visualize_top_words(word_counts, top_n=10):
    # Сортування слів за частотою
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    if not sorted_words:
        print(f"{Fore.RED}[INFO] Нажаль, немає слів для візуалізації.{Style.RESET_ALL}")
        return
    words, counts = zip(*sorted_words)

    # Візуалізація за завданням
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.xlabel('Words (Слова)')
    plt.ylabel('Counts(Кількість)')
    plt.title(f'Top {top_n} Words Frequency\n(ТОП {top_n} найчастіше вживаних слів)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('top_words_frequency.png')  # Збереження графіка якщо нема графічного інтерфейсу як в мене
    plt.show()




if __name__ == "__main__":

    # Вхідний текст для обробки
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"

    text = get_text(url)    
    if text:
        # Виконання MapReduce на вхідному тексті та задаємо слова пошуку
        search_words = ['love', 'himself',
                        'war', 'peace', 'house']  # слова для пошуку
        result = map_reduce(text, search_words)  # додано search_words

        print(f"Результат підрахунку слів: ", result)

        # Виконання MapReduce на всьому тексті
        print(f"{Fore.GREEN}Виконання MapReduce на всьому тексті")
        full_words_counts = map_reduce(text)

        print(f"{Fore.LIGHTCYAN_EX}Візуалізуємо результати для всього тексту, або зберігаємо у файл, якщо немає графічного інтерфейсу{Style.RESET_ALL}")
        visualize_top_words(full_words_counts, top_n=10)
        
    else:
        print(f"{Fore.RED}[INFO-ERROR]: Не вдалося отримати вхідний текст!{Style.RESET_ALL}")