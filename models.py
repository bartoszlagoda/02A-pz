from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Currencies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_name = db.Column(db.String(100), nullable=False)
    currency_code = db.Column(db.String(10), nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date)

    __table_args__ = (
        db.UniqueConstraint('currency_code', 'date', name='uix_currency_date'),
    )

    def __init__(self, currency_name, currency_code, exchange_rate, date):
        self.currency_name = currency_name
        self.currency_code = currency_code
        self.exchange_rate = exchange_rate
        self.date = date

    def __repr__(self):
        return f"<Waluta {self.currency_name} ({self.currency_code}) dnia {self.date}>"
