import psycopg2
from psycopg2 import Error
import serial
from pydantic import BaseModel
from time import sleep

# Datetime нужен для временной отметки
# Datetime is required for timestamp
from datetime import datetime, timezone

# Данные для подключения к БД
# По уму их тоже нужно импортировать из
# внешнего защищенного файла, а не прописывать здесь
# Data for establishing DB connection
# Smart thing to do is to import this
# data from external protected file (localhost, access rules etc.)
dbuser = "username"
dbpassword = "password"
dbhost = "1.1.1.1"
dbport = "5432"
dbname = "databasename"

# С помощью Pydantic расписываем получаемый JSON
# Формат его выдачи определяется в EnvSens.ino
# Здесь мы только раскладываем "по полочкам" 
# Data validation in recieved JSON using Pydantic  
# It's format is established in ENVSens.ino
class Envmeter(BaseModel):
    P2_5: float
    P10: float
    CO2_Level: int
    Rad_dynamic: float
    Rad_static: float
    Rad_pulses: int

# Временная отметка (В перспективе будем брать с GPS модуля)
# Timestamp (in future it may be recieved from GPS module)
dt = datetime.now(timezone.utc)

# Подключение к Arduino через serial
# Обратите внимание на порт - здесь 'COM20'
# Его нужно заменить на порт к которму подключена Arduino
# В будущем передачу лучше вести по беспроводной сети
# Establishing serial connection to Arduino
# 'COM20' must be changed to port, to which Arduino
# is connected in your system
# In future is better to use wireless network
arduino = serial.Serial(port='COM20', baudrate=115200, timeout=0.88)

try:
    # Подключение к существующей базе данных
    # Connection to existing Database
    connection = psycopg2.connect(user = dbuser,
                                  # пароль, который указали при установке PostgreSQL
                                  # password, that was set during PostgreSQL setup
                                  password = dbpassword,
                                  host = dbhost,
                                  port = dbport,
                                  database = dbname)

    # Курсор для выполнения операций с базой данных
    # Cursor for making operations with Database
    cursor = connection.cursor()

    # Вывести сведения о PostgreSQL
    # Output info about PostgreSQL
    print("Server information: Информация о сервере PostgreSQL")
    print(connection.get_dsn_parameters(), "\n")

    # SQL-запрос для создания новой таблицы
    # Не забываем, что "DROP TABLE..." здесь
    # только для отладки, чтобы не забивать базу
    # SQL request to create new table  
    # "DROP TABLE" here only for debuging
    # and preventing garbage filing of Database  
    create_table_query = '''DROP TABLE IF EXISTS Location1;
                            CREATE TABLE Location1
                          (ID SERIAL PRIMARY KEY,
                          TIME       TIMESTAMP,
                          P2_5           REAL,
                          P10           REAL,
                          CO2           REAL,
                          Rad_dynamic           REAL,
                          Rad_static           REAL,
                          Rad_pulses           INTEGER); '''

    # Выполнение команды: это создает новую таблицу
    # Running the command: Creating a new table
    cursor.execute(create_table_query)
    connection.commit()
    print("Table is successfully created: Таблица успешно создана в PostgreSQL")
    sleep(1)
    for i in range(100):
        line = arduino.readline()
        if line:
            string = line.decode()
            print(string)
            json_data = Envmeter.parse_raw(string)
            print(json_data)
            print(json_data.P2_5)
            #sleep(3)

            # Выполнение SQL-запроса
            # Making SQL request
            cursor.execute('''INSERT INTO Location1 (TIME, P2_5, P10, CO2, Rad_dynamic, Rad_static, Rad_Pulses) VALUES (%s,%s,%s,%s,%s,%s,%s)''',(dt.now(),json_data.P2_5, json_data.P10, json_data.CO2_Level, json_data.Rad_dynamic, json_data.Rad_static, json_data.Rad_pulses))
            #cursor.execute(insert_query)
            connection.commit()
            print("1 record is inserted successfully: 1 запись успешно вставлена")
    
    # Получить результат
    # Recieving the result
    cursor.execute("SELECT * from Location1")
    record = cursor.fetchall()
    print("Результат", record)

    #cursor.execute("SELECT version();")
    # Получить результат
    #record = cursor.fetchone()
    #print("Вы подключены к - ", record, "\n")

# Обработка ошибок
# Handling of an errors
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL *** PostgreSQL ERROR", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто *** PostgreSQL connection closed")
