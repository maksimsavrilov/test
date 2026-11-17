import random
import psycopg2
from faker import Faker

# Настройки подключения к PostgreSQL
DB_CONFIG = {
    "dbname": "orders",
    "user": "ocado",       # Замените на вашего пользователя, если отличается
    "password": "ocado-dev", # Укажите ваш пароль
    "host": "localhost",
    "port": 5434
}

def create_tables(cursor):
    """Создание структуры таблиц в базе данных."""
    print("Создание таблиц...")
    
    # Таблица авторов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authors (
            author_id SERIAL PRIMARY KEY,
            author_name VARCHAR(255) NOT NULL,
            country VARCHAR(100)
        );
    """)
    
    # Таблица книг
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id SERIAL PRIMARY KEY,
            book_name VARCHAR(255) NOT NULL,
            isbn VARCHAR(20),
            cost DECIMAL(10, 2),
            book_sold INT
        );
    """)
    
    # Промежуточная таблица связей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books_authors (
            id SERIAL PRIMARY KEY,
            author_id INT REFERENCES authors(author_id) ON DELETE CASCADE,
            book_id INT REFERENCES books(book_id) ON DELETE CASCADE
        );
    """)

def generate_data():
    fake = Faker(['ru_RU', 'en_US']) # Использование локализаций для реалистичности
    
    try:
        # Подключение к БД
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Создаем таблицы
        create_tables(cursor)
        
        print("Генерация данных для 2000 авторов и их книг...")
        
        # Списки для массовой вставки (Bulk Insert) для ускорения работы
        authors_to_insert = []
        books_to_insert = []
        relations_to_insert = []
        
        # Счётчики ID (так как мы используем SERIAL, проще отслеживать их в памяти для связей)
        current_book_id = 1
        
        for author_id in range(1, 2001):
            # Генерируем автора
            author_name = fake.name()
            country = fake.country()
            authors_to_insert.append((author_name, country))
            
            # Генерируем случайное количество книг для текущего автора (от 2 до 20)
            num_books = random.randint(2, 20)
            for _ in range(num_books):
                # Генерируем данные книги
                # fake.sentence изображает название книги из 1-3 слов
                book_name = fake.sentence(nb_words=random.randint(1, 3)).rstrip('.')
                isbn = fake.isbn13()
                cost = round(random.uniform(150.00, 1500.00), 2) # Цена от 150 до 1500 руб.
                book_sold = random.randint(0, 50000)            # Продано от 0 до 50к копий
                
                books_to_insert.append((book_name, isbn, cost, book_sold))
                
                # Запоминаем связь (текущий автор + текущая книга)
                relations_to_insert.append((author_id, current_book_id))
                current_book_id += 1

        # Вставка авторов
        print("Запись авторов в БД...")
        cursor.executemany(
            "INSERT INTO authors (author_name, country) VALUES (%s, %s);",
            authors_to_insert
        )
        
        # Вставка книг
        print("Запись книг в БД...")
        cursor.executemany(
            "INSERT INTO books (book_name, isbn, cost, book_sold) VALUES (%s, %s, %s, %s);",
            books_to_insert
        )
        
        # Вставка связей
        print("Создание связей между авторами и книгами...")
        cursor.executemany(
            "INSERT INTO books_authors (author_id, book_id) VALUES (%s, %s);",
            relations_to_insert
        )
        
        # Фиксация изменений в БД
        conn.commit()
        print(f"Успешно добавлено: 2000 авторов и {len(books_to_insert)} книг.")
        
    except Exception as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")
        if 'conn' in locals():
            conn.rollback()
            
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("Соединение с БД закрыто.")

if __name__ == "__main__":
    generate_data()

