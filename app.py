from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '02A-pz: PROGRAM DO WYCIAGANIA DANYCH FINANSOWYCH WE FLASKU\nTEST FLASK'

if __name__ == '__main__':
    app.run(debug = True)

