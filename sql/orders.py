import io
import random
import psycopg2

# Настройки подключения к PostgreSQL
DB_CONFIG = {
    "dbname": "orders",
    "user": "ocado",          # Укажите вашего пользователя
    "password": "ocado-dev", # Укажите ваш пароль
    "host": "localhost",
    "port": 5434
}

def create_tables(cursor):
    """Создание чистых таблиц без индексов и ключей для максимальной скорости вставки."""
    print("Создание таблиц orders и order_items...")
    cursor.execute("DROP TABLE IF EXISTS order_items CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS orders CASCADE;")
    
    cursor.execute("""
        CREATE TABLE orders (
            order_id INT NOT NULL,
            customer_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL
        );
    """)
    
    cursor.execute("""
        CREATE TABLE order_items (
            item_id BIGINT NOT NULL,
            order_id INT NOT NULL,
            product_id INT NOT NULL
        );
    """)

def generate_and_load():
    # Параметры генерации
    NUM_CUSTOMERS = 4_000_000   # 4 миллиона покупателей
    NUM_ORDERS = 10_000_000     # 10 миллионов заказов
    NUM_PRODUCTS = 50_000       # Пул из 50 тыс. различных товаров
    BATCH_SIZE = 250_000        # Размер пачки (250 тыс. заказов за проход ~1.6 млн айтемов)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        create_tables(cursor)
        conn.commit()
        
        print(f"Старт генерации: {NUM_ORDERS:,} заказов для {NUM_CUSTOMERS:,} покупателей...")
        
        current_item_id = 1
        
        # Идем по заказам порциями (батчами), чтобы не переполнить оперативную память
        for batch_start in range(1, NUM_ORDERS + 1, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, NUM_ORDERS + 1)
            
            orders_buf = io.StringIO()
            items_buf = io.StringIO()
            
            for order_id in range(batch_start, batch_end):
                customer_id = random.randint(1, NUM_CUSTOMERS)
                amount = round(random.uniform(10.0, 5000.0), 2)
                
                # Пишем строку заказа в буфер
                orders_buf.write(f"{order_id}\t{customer_id}\t{amount}\n")
                
                # Генерируем от 1 до 12 товаров для этого заказа
                num_items = random.randint(1, 12)
                for _ in range(num_items):
                    product_id = random.randint(1, NUM_PRODUCTS)
                    items_buf.write(f"{current_item_id}\t{order_id}\t{product_id}\n")
                    current_item_id += 1
            
            # Перематываем буферы в начало
            orders_buf.seek(0)
            items_buf.seek(0)
            
            # Заливаем заказы
            cursor.copy_expert("COPY orders (order_id, customer_id, amount) FROM STDIN", orders_buf)
            # Заливаем товары из этих заказов
            cursor.copy_expert("COPY order_items (item_id, order_id, product_id) FROM STDIN", items_buf)
            
            conn.commit()
            
            orders_buf.close()
            items_buf.close()
            
            print(f"Загружено заказов: {batch_end - 1:,} / {NUM_ORDERS:,} (Всего позиций: {current_item_id - 1:,})")

        # Навешиваем ключи и индексы ПОСЛЕ заливки данных
        print("Заливка завершена. Создаем PRIMARY KEY и FOREIGN KEY (займет около 1-2 минут)...")
        
        cursor.execute("ALTER TABLE orders ADD PRIMARY KEY (order_id);")
        cursor.execute("ALTER TABLE order_items ADD PRIMARY KEY (item_id);")
        
        # Добавляем внешний ключ и индекс для быстрых JOIN-ов
        cursor.execute("""
            ALTER TABLE order_items 
            ADD CONSTRAINT fk_order 
            FOREIGN KEY (order_id) REFERENCES orders(order_id);
        """)
        cursor.execute("CREATE INDEX idx_order_items_order_id ON order_items(order_id);")
        cursor.execute("CREATE INDEX idx_orders_customer_id ON orders(customer_id);")
        
        conn.commit()
        print("База данных полностью готова к работе!")

    except Exception as error:
        print(f"Ошибка при работе с БД: {error}")
        if 'conn' in locals():
            conn.rollback()
            
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("Соединение закрыто.")

if __name__ == "__main__":
    generate_and_load()

