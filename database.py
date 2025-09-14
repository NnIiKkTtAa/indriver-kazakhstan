import sqlite3
import pandas as pd
import random

class taxi_db:
    @staticmethod
    def init_db():
        conn = sqlite3.connect('taxi.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS drivers
                    (id INTEGER PRIMARY KEY, name TEXT, car_model TEXT, car_number TEXT, rating REAL)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                    (id INTEGER PRIMARY KEY, driver_id INTEGER, from_address TEXT, 
                     to_address TEXT, price INTEGER, cleanliness TEXT, damage TEXT,
                     cleanliness_confidence REAL, damage_confidence REAL)''')
        
        # Добавляем тестовых водителей
        c.execute("SELECT COUNT(*) FROM drivers")
        if c.fetchone()[0] == 0:
            drivers = [
                (1, 'Иван Петров', 'Kia Rio', 'А123ВС77', 4.8),
                (2, 'Мария Сидорова', 'Hyundai Solaris', 'В456ОР77', 4.9),
                (3, 'Алишер Жумабаев', 'Toyota Camry', 'Н789КЗ77', 4.7),
                (4, 'Айгуль Сапарбаева', 'Lada Granta', 'Т321ОК77', 4.6)
            ]
            c.executemany("INSERT INTO drivers VALUES (?, ?, ?, ?, ?)", drivers)
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_available_drivers():
        conn = sqlite3.connect('taxi.db')
        df = pd.read_sql("SELECT * FROM drivers", conn)
        conn.close()
        return df

    @staticmethod
    def create_order(driver_id, from_address, to_address, price, cleanliness, damage, cleanliness_confidence, damage_confidence):
        conn = sqlite3.connect('taxi.db')
        c = conn.cursor()
        c.execute('''INSERT INTO orders (driver_id, from_address, to_address, price, cleanliness, damage, cleanliness_confidence, damage_confidence)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                 (driver_id, from_address, to_address, price, cleanliness, damage, cleanliness_confidence, damage_confidence))
        order_id = c.lastrowid
        conn.commit()
        conn.close()
        return order_id