from flask import Flask, jsonify
import mysql.connector
import datetime

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Konfiguracja połączenia z bazą danych MySQL
db_config = {
    'host': 'twoj_serwer_mysql',
    'user': 'twoj_uzytkownik',
    'password': 'twoje_haslo',
    'database': 'twoja_baza_danych'
}

def fetch_currency_data():
    """
    Pobiera dane o walutach z bazy danych i przetwarza je.
    Zwraca dane jako listę słowników.
    """
    try:
        # Połączenie z bazą danych
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Wykonanie zapytania SQL do pobrania danych
        query = """
        SELECT currency_code, currency_name, exchange_rate, last_updated
        FROM currency_data
        """
        cursor.execute(query)
        results = cursor.fetchall()

         # Przetworzenie danych - konwersja daty, np. na format YYYY-MM-DD
      #  processed_data = []
       # for row in results:
      #      row['last_updated'] = row['last_updated'].strftime('%Y-%m-%d') if row['last_updated'] else None
       #     processed_data.append(row)
        currency_rates = {row['currency_code']: row['exchange_rate'] for row in results}
        return currency_rates

    except mysql.connector.Error as err:
        print("Błąd połączenia z bazą danych:", err)
        return []

    finally:
        # Zamknięcie połączenia
        if conn.is_connected():
            cursor.close()
            conn.close()
@app.route('/convert-currency', methotds=['GET'])
def convert_currency():
    from_currency = request.args.get('from_currency')
    to_currency = request.args.get('to_currency')
    amount = float(request,args.get('amount', 1))

    currency_rates = fetch_currency_data()
    if from_currency not in currency_rates or to_currency not in currency_rates:
        return jsonify({"error": "Nieprawildowy kod waluty"}), 400

    rate_from = currency_rates[from_currency]
    rate_to = currency_rates[to_currency]
    converted_amount = amout * (rate_to / rate_from)

    return jsonify ({
        "from_currency": from_currency,
        "currency": to_currency,
        "original_amout": amount,
        "converted_amount": round(converted_amount, 2)
    })
@app.route('/currency-data', methods=['GET'])
def get_currency_data():
    """
    Endpoint API, który zwraca przetworzone dane o walutach jako array.
    """
    data = fetch_currency_data()
    return jsonify(data)  # Zwracamy dane jako JSON (lista obiektów)

if __name__ == '__main__':
    app.run(debug=True)
