from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password


class Comment(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.String(50), primary_key=True)
    app_id = db.Column(db.Integer, nullable=False)
    comment_text = db.Column(db.String(255), nullable=False)
    flavor = db.Column(db.Integer, nullable=False)
    environment = db.Column(db.Integer, nullable=False)
    service = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    shop_id = db.Column(db.String(50), nullable=False)
    comment_date = db.Column(db.DateTime, nullable=False)
    sentiment_score = db.Column(db.Float, nullable=False)