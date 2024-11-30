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


@app.route('/get', methods=['GET'])
def get_currencies():
    url = "https://api.nbp.pl/api/exchangerates/tables/A?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for currency_data in data[0]['rates']:
            currency_code = currency_data['code']
            currency_name = currency_data['currency']
            exchange_rate = currency_data['mid']
            date = datetime.now().date()

            existing_entry = Currencies.query.filter_by(currency_code=currency_code, date=date).first()
            if not existing_entry:
                new_entry = Currencies(currency_name, currency_code, exchange_rate, date)
                db.session.add(new_entry)

        db.session.commit()
        return jsonify({"message": "Waluty zapisane."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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


@app.route('/history/<currency_code>')
def currency_history(currency_code):
    try:
        historical_data = Currencies.query.filter_by(currency_code=currency_code.upper()).order_by(
            Currencies.date).all()

        history = [{
            'date': entry.date,
            'exchange_rate': entry.exchange_rate
        } for entry in historical_data]

        return jsonify({'currency_code': currency_code.upper(), 'history': history})

    except Exception as e:
        return jsonify({"error": f"Nie udało się pobrać danych dla {currency_code}: {str(e)}"})

@app.route('/get/<release_date>', methods=['GET'])
def get_legacy_data(release_date):
    try:
        response = requests.get("https://api.nbp.pl/api/exchangerates/tables/A/" + release_date + "/?format=json")
        data = response.json()

        for currency_data in data[0]['rates']:
            currency_code = currency_data['code']
            currency_name = currency_data['currency']
            exchange_rate = currency_data['mid']
            date = release_date

            existing_entry = Currencies.query.filter_by(currency_code=currency_code, date=date).first()
            if existing_entry:
                existing_entry.exchange_rate = exchange_rate
                db.session.commit()
            else:
                new_entry = Currencies(currency_name, currency_code, exchange_rate, date)
                db.session.add(new_entry)
                db.session.commit()

        db.session.commit()
        return jsonify({"message": "Waluty zapisane dla daty " + release_date})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
