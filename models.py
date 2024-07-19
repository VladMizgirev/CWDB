import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Word(Base):
    __tablename__ = "word"
    id = sq.Column(sq.Integer, primary_key=True)
    rus = sq.Column(sq.String(length=40), unique=True)
    en = sq.Column(sq.String(length=40), unique=True)
    w_en_1 = sq.Column(sq.String(length=40), unique=True)
    w_en_2 = sq.Column(sq.String(length=40), unique=True)
    w_en_3 = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'{self.id}: {self.rus}, {self.en}, {self.w_en}'

class New_word(Base):
    __tablename__ = "new_word"
    id = sq.Column(sq.Integer, primary_key=True)
    rus = sq.Column(sq.String(length=40), unique=True)
    en = sq.Column(sq.String(length=40), unique=True)
    w_en_1 = sq.Column(sq.String(length=40), unique=True)
    w_en_2 = sq.Column(sq.String(length=40), unique=True)
    w_en_3 = sq.Column(sq.String(length=40), unique=True)
    
    def __str__(self):
        return f'{self.id}: {self.id}: {self.rus}, {self.en}'

class Client(Base):
    __tablename__ = "client"
    id = sq.Column(sq.Integer, primary_key=True)

    def __str__(self):
        print(f'{self.id}')
        return f'{self.id}'

class Client_list_word(Base):
    __tablename__ = "client_list_word"
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    id_client = sq.Column(sq.Integer, sq.ForeignKey("client.id"), nullable=False)
    id_word = sq.Column(sq.String, nullable=False)
    id_new_word = sq.Column(sq.String)
    clients = relationship(Client, backref="clients")

    def __str__(self):
        return f'{self.id}, {self.id_client}, {self.id_word}, {self.id_new_word}'

def create_tables(engine):
    Base.metadata.create_all(engine)
