from datetime import datetime
from flask import Flask, render_template, jsonify, Response
from sqlalchemy import text
import requests
from collections import defaultdict
from models import db, Currencies
from statistics import variance

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)


@app.route('/')
def hello_world():
    return render_template('base.html')


@app.route('/show', methods=['GET'])
def show_currencies():
    dates = db.session.query(Currencies.date).filter(Currencies.date.isnot(None)).distinct().all()
    unique_dates = sorted([d[0] for d in dates])

    currencies = db.session.query(Currencies).all()

    pivot_data = defaultdict(dict)
    for currency in currencies:
        if currency.date:
            pivot_data[currency.currency_name][currency.date] = currency.exchange_rate

    return render_template('vertical_table.html', pivot_data=pivot_data, dates=unique_dates)


@app.route('/test_db')
def test_db():
    try:
        result = db.session.execute(text('SELECT 1'))
        result_data = result.fetchone()

        if result_data is None:
            return jsonify({"error": "Brak rezultatów dla zapytania."})

        result_dict = {'test_column': result_data[0]}

        return jsonify({"message": "Połączenie z bazą prawidłowe", "result": result_dict})
    except Exception as e:
        return jsonify({"error": f"Nieudane połączenie z bazą danych: {str(e)}"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
