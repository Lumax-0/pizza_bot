# Импортируем встроенный модуль sqlite3 для работы с базой данных SQLite
import sqlite3

# Определяем имя файла базы данных как константу для удобства
DB_NAME = 'barbershop.db'


# Функция для инициализации базы данных (создания таблиц, если их нет)
def init_db():
    # Устанавливаем соединение с файлом БД. Если файла нет, он будет создан.
    conn = sqlite3.connect(DB_NAME)
    # Создаем объект курсора, который позволяет выполнять SQL-запросы
    cursor = conn.cursor()

    # Создаем таблицу 'masters' (мастера), если она еще не существует
    # id: Уникальный идентификатор мастера (первичный ключ)
    # name: Имя мастера (текст)
    # rating: Рейтинг мастера (вещественное число)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS masters (
            id INTEGER PRIMARY KEY,
            name TEXT,
            rating REAL
        )
    ''')

    # Создаем таблицу 'services' (услуги), если она еще не существует
    # id: Уникальный идентификатор услуги (первичный ключ)
    # name: Название услуги (текст)
    # price: Цена услуги (целое число)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER
        )
    ''')

    # Создаем таблицу 'branches' (филиалы), если она еще не существует
    # id: Уникальный идентификатор филиала (первичный ключ)
    # name: Название/адрес филиала (текст)
    # url_map: Ссылка на карту (текст)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY,
            name TEXT,
            url_map TEXT
        )
    ''')

    # Создаем таблицу 'bookings' (записи), если она еще не существует
    # id: Уникальный идентификатор записи (первичный ключ)
    # name: Имя клиента (текст)
    # phone: Телефон клиента (текст)
    # master: Имя выбранного мастера (текст)
    # service: Название выбранной услуги (текст)
    # date: Выбранная дата (текст)
    # time: Выбранное время (текст)
    # branch: Выбранный филиал (текст)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            master TEXT,
            service TEXT,
            date TEXT,
            time TEXT,
            branch TEXT
        )
    ''')

    # Сохраняем все изменения (создание таблиц) в базе данных
    conn.commit()
    # Закрываем соединение с базой данных
    conn.close()


# Функция для наполнения таблиц начальными данными (мастера, услуги, филиалы)
def populate_data():
    # Устанавливаем соединение с БД
    conn = sqlite3.connect(DB_NAME)
    # Создаем курсор
    cursor = conn.cursor()

    # Добавляем мастеров. INSERT OR IGNORE предотвращает ошибку, если запись с таким id уже существует.
    conn.execute('''
        INSERT OR IGNORE INTO masters (id, name, rating) VALUES 
        (1, 'Маргарита', 4.6), 
        (2, 'Пеперони', 4.8), 
        (3, 'Диабло', 4.5),
        (4, 'Детская', 4.6), 
        (5, 'Цыплёнок', 4.8)
    ''')

    # Добавляем услуги
    conn.execute('''
        INSERT OR IGNORE INTO services (id, name, price) VALUES 
        (1, 'Самовывоз', 0), 
        (2, 'Доствка на мопеде', 3000), 
        (3, 'Доставка на авто', 7000)
    ''')

    # Добавляем филиалы
    conn.execute('''
        INSERT OR IGNORE INTO branches (id, name, url_map) VALUES 
        (1, 'Абая 52', 'https://2gis.kz/almaty/search/%D0%90%D0%B1%D0%B0%D1%8F%2052/geo/9430047375009170/76.91341%2C43.23982'), 
        (2, 'Сатпаева 66', 'https://2gis.kz/almaty/geo/9430047375103401?m=77.066627%2C43.309279%2F16')
    ''')

    # Сохраняем добавленные данные
    conn.commit()
    # Закрываем соединение
    conn.close()


# Функция для получения списка всех мастеров (имя и рейтинг)
def get_masters():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Выполняем SQL-запрос на выборку имени и рейтинга из таблицы masters
    cursor.execute("SELECT name, rating FROM masters")
    # Получаем все строки результата запроса в виде списка кортежей
    masters = cursor.fetchall()
    conn.close()
    # Возвращаем список мастеров
    return masters


# Функция для получения списка всех услуг (название и цена)
def get_services():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM services")
    services = cursor.fetchall()
    conn.close()
    return services


# Функция для получения списка всех филиалов (название и ссылка на карту)
def get_branches():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, url_map FROM branches")
    branches = cursor.fetchall()
    conn.close()
    return branches


# Функция для добавления новой записи (бронирования) в таблицу bookings
# Принимает все данные о записи в качестве аргументов
def add_booking(name, phone, master, service, date, time, branch):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Выполняем SQL-запрос INSERT для добавления новой строки
    # Используем плейсхолдеры (?) для безопасной вставки данных (защита от SQL-инъекций)
    cursor.execute(
        'INSERT INTO bookings (name, phone, master, service, date, time, branch) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (name, phone, master, service, date, time, branch))
    # Сохраняем изменения
    conn.commit()
    conn.close()


# Функция для получения списка всех существующих записей (бронирований)
def get_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Выбираем все поля из таблицы bookings
    cursor.execute('''
        SELECT id, name, phone, master, service, date, time, branch FROM bookings
    ''')
    # Получаем все записи
    bookings = cursor.fetchall()
    conn.close()
    # Возвращаем список записей
    return bookings


# Функция для удаления записи по её ID
def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Выполняем SQL-запрос DELETE для удаления строки, где id совпадает с переданным booking_id
    # Используем плейсхолдер (?) для безопасности
    cursor.execute('''
        DELETE FROM bookings WHERE id = ?
    ''', (booking_id,))  # Передаем booking_id как кортеж из одного элемента
    # Сохраняем изменения (удаление)
    conn.commit()
    conn.close()