import random
import io
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
    
    # Таблица зарплат
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees_income (
            id SERIAL PRIMARY KEY,
            income DECIMAL(10,2)
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
        # 1. ОТКЛЮЧАЕМ PRIMARY KEY (и его индекс)
        print("Удаляем ограничение PRIMARY KEY для ускорения загрузки...")
        cursor.execute("""
            ALTER TABLE employees_income 
            DROP CONSTRAINT IF EXISTS employees_income_pkey;
        """)
        conn.commit()

        # 2. ГЕНЕРАЦИЯ И ЗАЛИВКА ДАННЫХ ПОРЦИЯМИ (ЧАНКАМИ)
        total_rows = 20_000_000
        chunk_size = 5_000_000  # Оптимальный размер порции (~250-300 МБ в RAM)
        
        print(f"Начинаем генерацию и заливку {total_rows:,} строк порциями по {chunk_size:,}...")
        
        for chunk_start in range(0, total_rows, chunk_size):
            # Создаем временный текстовый буфер в памяти для текущего чанка
            buffer = io.StringIO()
            
            # Генерируем данные для текущей порции
            for _ in range(chunk_size):
                salary = random.randint(10002, 80020)
                buffer.write(f"{salary}\n")
            
            # Сбрасываем указатель буфера в начало перед чтением
            buffer.seek(0)
            
            # Моментальная вставка текущего чанка через COPY
            cursor.copy_expert(
                "COPY employees_income (income) FROM STDIN WITH (FORMAT text)", 
                buffer
            )
            conn.commit()
            
            current_progress = min(chunk_start + chunk_size, total_rows)
            print(f"Успешно загружено: {current_progress:,} / {total_rows:,} строк.")
            
            # Очищаем буфер из памяти
            buffer.close()

        # 3. ВОЗВРАЩАЕМ PRIMARY KEY (индекс пересоздается один раз для всей таблицы)
        print("Данные загружены. Пересоздаем PRIMARY KEY (это может занять около минуты)...")
        cursor.execute("""
            ALTER TABLE employees_income 
            ADD PRIMARY KEY (id);
        """)
        conn.commit()
        print("Индекс успешно создан. Процесс полностью завершен!")
 
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

