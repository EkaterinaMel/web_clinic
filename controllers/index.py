from app import app
from flask import render_template, request, session
import sqlite3
from utils import get_db_connection
from models.index_model import *
import pandas as pd

@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    if request.values.get('specific'):
        specific = request.values.get('specific')
        session['specific'] = specific
    elif request.values.get('data'):
        data = request.values.get('data')
        session['data']= data
        if request.values.get('days'):
            days = request.values.get('days')
            session['days']= days
    elif request.values.get('watch'):
        ind = request.values.get('watch')
        session['ind']= ind
    elif request.values.get('number'):
        patient_id = search_patient(conn, request.values.get('number'))
        if patient_id.empty:
            print("INCORRECT NUMBER")
        else:
            take_receipt(conn, request.values.get('doc_id'), str(patient_id.iloc[0,0]))
    elif request.values.get('menu'):
        session['menu'] = request.values.get('menu')
        session['ind']= -1
    else :
        session['menu'] = '1'
        session['specific']= "Терапевт"
        session['data']= "2024-01-18"
        session['days']= '7'
        session['ind']= -1

    doctors = []
    if session['menu'] == '2':
        count = get_amount_doctors(conn, session['specific'])
        session['times'] = int(count.iloc[0,0])
        schedule = get_schedule_doctors(conn, session['data'], session['days'], session['specific'])
        all_doctors = get_all_doctors(conn, session['data'], session['days'], session['specific'])
        schedule = all_doctors.merge(schedule, how="outer").fillna(0)
        schedule["count"] = schedule["count"].astype(int)
        if int(session['ind']) > -1:
            doctors = get_times(conn, schedule.loc[int(session['ind']), 'date'], schedule.loc[int(session['ind']),'doctor_name'],
                                  session['specific'])
    else:
        session['times'] = 11
        schedule = get_schedule_days(conn, session['data'], session['days'], session['specific'])
        all_times = get_all_times(conn, session['data'], session['days'])
        schedule = all_times.merge(schedule, how="outer").fillna(0)
        schedule["count"] = schedule["count"].astype(int)
        if int(session['ind']) > -1:
            doctors = get_doctors(conn, schedule.loc[int(session['ind']), 'date'], schedule.loc[int(session['ind']),'time'],
                                  session['specific'])

    all_dates = get_all_dates(conn, session['data'], session['days'])
    all_dates['weekday'] = all_dates['weekday'].replace([1, 2, 3, 4, 5, 6],
                                                        ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'])
    df_specific = get_specific(conn)
    # выводим форму
    html = render_template(
        'index.html',
        spec = session['specific'],
        combo_box = df_specific,
        data = session['data'],
        days = session["days"],
        schedule = schedule,
        dates = all_dates,
        ind = int(session['ind']),
        doctors = doctors,
        times = session['times'],
        menu_ind = session['menu'],
        len = len )
    return html

app.run(debug=True)