from flask import Flask, render_template, request, jsonify
import requests
import mysql.connector
import datetime

app = Flask(__name__)

# Konfiguracja połączenia z bazą danych MySQL
db_config = {
    'host': 'twoj_serwer_mysql',
    'user': 'twoj_uzytkownik',
    'password': 'twoje_haslo',
    'database': 'twoja_baza_danych'
}

NBP_JSON_PATTERN = 'http://api.nbp.pl/api/exchangerates/rates/A/{}/{}/?format=json'

class NbpNoDataException(Exception):
    pass

def pobierz_kurs_z_nbp(waluta, data):
    response = requests.get(NBP_JSON_PATTERN.format(waluta, data))
    if response.ok:
        dane = response.json()
        kurs = dane["rates"][0]["mid"]
        return kurs
    else:
        raise NbpNoDataException

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        waluta = request.form.get('waluta')
        data = request.form.get('data')
        try:
            kurs = pobierz_kurs_z_nbp(waluta, data)
            return render_template('index.html', kurs=kurs, waluta=waluta, data=data)
        except NbpNoDataException:
            return render_template('index.html', error="Brak danych dla podanej waluty lub daty.")
        except Exception as e:
            return render_template('index.html', error=f"Wystąpił błąd: {e}")
    return render_template('index.html')

@app.route('/rates', methods=['GET'])
def all_rates():
    try:
        response = requests.get("https://api.nbp.pl/api/exchangerates/tables/a/?format=json")
        response.raise_for_status()
        dane = response.json()[0]
        return render_template('rates.html', rates=dane['rates'], effective_date=dane['effectiveDate'])
    except requests.exceptions.HTTPError:
        return "Błąd: Nie można pobrać danych z API", 500

def fetch_currency_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT currency_code, currency_name, exchange_rate, last_updated
        FROM currency_data
        """
        cursor.execute(query)
        results = cursor.fetchall()

        processed_data = []
        for row in results:
            row['last_updated'] = row['last_updated'].strftime('%Y-%m-%d') if row['last_updated'] else None
            processed_data.append(row)

        return processed_data

    except mysql.connector.Error as err:
        print("Błąd połączenia z bazą danych:", err)
        return []

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/currency-data', methods=['GET'])
def get_currency_data():
    data = fetch_currency_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
