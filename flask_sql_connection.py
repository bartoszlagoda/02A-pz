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

@app.route('/currency-data', methods=['GET'])
def get_currency_data():
    """
    Endpoint API, który zwraca przetworzone dane o walutach jako array.
    """
    data = fetch_currency_data()
    return jsonify(data)  # Zwracamy dane jako JSON (lista obiektów)

if __name__ == '__main__':
    app.run(debug=True)
