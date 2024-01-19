import pandas
import pandas as pd

def get_doctors(conn, data, time, spec):
    return pandas.read_sql( ''' 
    SELECT reception_id, doctor_name
    FROM doctor
    JOIN timetable USING (doctor_id)
    JOIN timetable_date USING (timetable_id)
    JOIN reception USING (timetable_date_id)
    WHERE receipt_date = :data AND reception_time = :time
    AND specification = :spec AND patient_id = -1;
    ''', conn, params={"data": data, "time":time, "spec":spec})

def search_patient(conn, number):
    return pandas.read_sql( ''' 
    SELECT patient_id
    FROM patient
    WHERE number = '''+number+''';
    ''', conn)

def take_receipt(conn, rec_id, patient_id):
    cursor = conn.cursor()
    cursor.executescript( ''' 
    UPDATE reception
    SET patient_id = '''+patient_id+'''
    WHERE reception_id='''+rec_id+''';
    ''')
    conn.commit()
    cursor.close()

def get_all_dates(conn, data, days):
    return pandas.read_sql( ''' 
    SELECT DISTINCT receipt_date AS date, weekday
    FROM timetable_date
    JOIN timetable USING (timetable_id)
    WHERE receipt_date < DATE(:data, '+'''+days+''' day') AND receipt_date >= :data;
    ''', conn, params={"data": data, "days":days})

def get_all_times(conn, data, days):
    return pandas.read_sql( ''' 
    WITH RECURSIVE create_time(cur_time)
    AS (
    SELECT '08:00:00'
    UNION ALL
    SELECT TIME(cur_time, '+1 hour')
    FROM create_time
    WHERE cur_time < '18:00:00'
    )
    SELECT DISTINCT receipt_date AS date, weekday, cur_time AS time
    FROM timetable_date, create_time
    JOIN timetable USING (timetable_id)
    WHERE receipt_date < DATE(:data, '+'''+days+''' day') AND receipt_date >= :data
    ORDER BY date, time;
    ''', conn, params={"data": data, "days":days})

def get_specific(conn):
    return pandas.read_sql( ''' 
    SELECT DISTINCT specification FROM doctor 
    ''', conn)

def get_schedule(conn, data, days, spec):
    return pandas.read_sql( '''
    SELECT DISTINCT receipt_date AS date, weekday, reception_time AS time, COUNT(timetable.doctor_id) AS count
    FROM timetable_date
    JOIN timetable USING (timetable_id)
    JOIN doctor USING (doctor_id)
    JOIN reception USING (timetable_date_id)
    WHERE receipt_date < DATE(:data, '+'''+days+''' day') AND receipt_date >= :data
    AND specification = :spec AND patient_id = -1
    GROUP BY date, time
    ORDER BY date, time;
    ''', conn, params={"data": data, "days":days, "spec":spec})

def make_timetable(conn, p_first_date):
    cursor = conn.cursor()
    cursor.executescript( ''' 
    WITH RECURSIVE create_date(cur_date) 
    AS ( 
    SELECT "'''+p_first_date+'''"
    UNION ALL 
    SELECT DATE(cur_date, '+1 day') 
    FROM create_date 
    WHERE cur_date < DATE("'''+p_first_date+'''", '+1 month','-1 day')
    ) 
    INSERT INTO timetable_date (timetable_id, receipt_date)
    SELECT timetable_id, cur_date
    FROM timetable
    JOIN create_date ON weekday = strftime('%w', cur_date);
    ''')
    cursor.close()

def make_reception(conn):
    cursor = conn.cursor()
    cursor.executescript( '''
    WITH RECURSIVE create_time(cur_time)
    AS (
    SELECT '08:00:00'
    UNION ALL
    SELECT TIME(cur_time, '+1 hour')
    FROM create_time
    WHERE cur_time < '19:00:00'
    )
    INSERT INTO reception (timetable_date_id, reception_time)
    SELECT timetable_date_id, cur_time
    FROM create_time, timetable_date
    JOIN timetable USING (timetable_id)
    WHERE cur_time >= start_time AND cur_time <= TIME(finish_time, '-1 hour');
    ''')
    cursor.close()
