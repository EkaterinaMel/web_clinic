import pandas as pd
import sqlite3
from models.index_model import make_timetable, make_reception
import pandas as pd
# устанавливаем соединение
con = sqlite3.connect("clinic.sqlite")

# таблицы:
# доктор
# пациент
# график докторов
# расписание (на месяц)
# запись (все возможные времена записи)

con.executescript('''
CREATE TABLE IF NOT EXISTS doctor (
doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
doctor_name VARCHAR(30),
specification VARCHAR(30)
);
INSERT INTO doctor (doctor_name, specification)
VALUES
('Буланова Н.С.', 'Терапевт'),
('Дурова Е.П.', 'Терапевт'),
('Князева Т.И.', 'Хирург'),
('Шевцова А.О.', 'Терапевт'),
('Яковлева М.Т.', 'Хирург'),
('Амазонова А.О.', 'Офтальмолог'),
('Игорев А.С.', 'Офтальмолог');

CREATE TABLE IF NOT EXISTS patient (
patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
patient_name VARCHAR(30),
number VARCHAR(6)
);
INSERT INTO patient (patient_name, number)
VALUES
('Омарова Р.С.', '122333'),
('Иванов Е.Ш.', '666666'),
('Валиев Т.З.', '123456'),
('Акробатова Ч.О.', '908954'),
('Макарова М.И.', '374927'),
('Котов Т.И.', '977322'),
('Пуринов Е.С.', '675394');

CREATE TABLE IF NOT EXISTS timetable (
timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
doctor_id INT,
weekday INTEGER(1),
start_time TIME,
finish_time TIME,
FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
);
INSERT INTO timetable (doctor_id, weekday, start_time, finish_time)
VALUES
(1, 1, '08:00:00', '17:00:00'),
(1, 2, '08:00:00', '17:00:00'),
(2, 1, '13:00:00', '15:00:00'),
(2, 3, '15:00:00', '18:00:00'),
(3, 4, '08:00:00', '12:00:00'),
(3, 5, '12:00:00', '18:00:00'),
(4, 1, '08:00:00', '12:00:00'),
(4, 3, '08:00:00', '12:00:00'),
(4, 5, '08:00:00', '12:00:00'),
(5, 1, '12:00:00', '18:00:00'),
(5, 3, '12:00:00', '18:00:00'),
(5, 5, '12:00:00', '18:00:00'),
(6, 4, '08:00:00', '12:00:00'),
(6, 5, '09:00:00', '13:00:00'),
(6, 6, '12:00:00', '14:00:00'),
(7, 3, '11:00:00', '14:00:00'),
(7, 4, '15:00:00', '18:00:00'),
(7, 5, '09:00:00', '14:00:00');

CREATE TABLE IF NOT EXISTS timetable_date (
timetable_date_id INTEGER PRIMARY KEY AUTOINCREMENT,
timetable_id INT,
receipt_date DATE,
FOREIGN KEY (timetable_id) REFERENCES timetable(timetable_id)
);

CREATE TABLE IF NOT EXISTS reception (
reception_id INTEGER PRIMARY KEY AUTOINCREMENT,
timetable_date_id INT,
patient_id INT DEFAULT -1,
reception_time TIME,
FOREIGN KEY (timetable_date_id) REFERENCES timetable_date(timetable_date_id),
FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);
''')

make_timetable(con, '2024-01-17')
make_reception(con)
print(pd.read_sql('''
SELECT * FROM doctor
''', con))
print(pd.read_sql('''
SELECT * FROM patient
''', con))
print(pd.read_sql('''
SELECT * FROM timetable
''', con))
print(pd.read_sql('''
SELECT * FROM timetable_date
''', con))
print(pd.read_sql('''
SELECT * FROM reception
ORDER BY timetable_date_id
''', con))
con.commit()
con.close()

