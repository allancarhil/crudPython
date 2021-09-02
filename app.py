
from flask import Flask, Response, request #pip install flask
from flask_sqlalchemy import SQLAlchemy #pip install Flask-SQLAlchemy
import datetime
from sqlalchemy import Column, Integer, DateTime
import mysql.connector  #pip install mysqlclient     pip install mysql-connector-python
import jsons #pip install jsons
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2


#CONEXÃO COM O  BANCO DE DADOS E CRIAÇÃO DE DATABASE
app = Flask(__name__)
engine = sqlalchemy.create_engine('postgresql://postgres:12345@localhost')
conn = engine.connect()
conn.execute("commit")
conn.execute("create database test")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/test'
db = SQLAlchemy(app)

#CRIAÇÃO DE TABLE
from app import db
@app.before_first_request
def create_tables():
    db.create_all()

#CRIAÇÃO DA CLASSE CLIENTE
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)        
    nome = db.Column(db.String(50), nullable=False)
    razao_social = db.Column(db.String(50), nullable=False)
    cnpj = db.Column(db.Numeric(14), nullable=False)
    data_inclusao = db.Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


    def to_json(self):
        return {"id": id, "nome": self.nome, "razao_social": self.razao_social, "cnpj": self.cnpj, "data_inclusao": self.data_inclusao}
db.create_all()

# SELECIONA TODOS OS CLIENTES
@app.route("/clientes", methods=["GET"])
def seleciona_todos():
    clientes_obj = Cliente.query.all()
    clientes_json = [cliente.to_json() for cliente in clientes_obj]
    print(clientes_json) 
    #return Response(jsons.dumps(clientes_json))
    return geraResponse(200,"clientes",clientes_json,"deu bom")


#SELECIONA POR ID
@app.route("/cliente/<id>", methods=["GET"])
def seleciona_cliente_por_id(id):
    cliente_obj = Cliente.query.filter_by(id=id).first()
    cliente_json= cliente_obj.to_json()
    return geraResponse(200,"cliente",cliente_json,"deu bom")
    
#CADASTRO DE CLIENTES
@app.route("/cliente", methods=["POST"])
def cadstro_cliente():
    body=request.get_json()
    try:
        cliente=Cliente(nome=body["nome"],razao_social=body["razao_social"],cnpj=body["cnpj"],data_inclusao=body["data_inclusao"])
        db.session.add(cliente)
        db.session.commit()
        return geraResponse(201,"cliente",cliente.to_json(),"criado com sucesso")
    except Exception as e:
        print('Erro',e)
        return geraResponse(400,"cliente",{},"erro no cadastro")

#UPDATE DE CLIENTES
@app.route("/cliente/<id>", methods=["PUT"])
def atualiza_cliente(id):
    cliente_obj = Cliente.query.filter_by(id=id).first()
    body = request.get_json()

    try:
        if('nome' in body):
            cliente_obj.nome = body['nome']
        if('razao_social' in body):
            cliente_obj.razao_social = body['razao_social']
        if('cnpj' in body):
            cliente_obj.cnpj = body['cnpj']
        if('data_inclusao' in body):
            cliente_obj.data_inclusao = body['data_inclusao']
        db.session.add(cliente_obj)
        db.session.commit()
        return geraResponse(200, "cliente", cliente_obj.to_json(), "Atualizado com sucesso")
    except Exception as e:
        print('Erro', e)
        return geraResponse(400, "cliente", {}, "Erro ao atualizar")


#DELETAR CLIENTES
@app.route("/cliente/<id>", methods=["DELETE"])
def deletar_cliente(id):
    cliente_obj = Cliente.query.filter_by(id=id).first()
    body=request.get_json()
    try:
        db.session.delete(cliente_obj)
        db.session.commit()
        return geraResponse(200,"cliente",cliente_obj.to_json(), "deletado com sucesso")
    except Exception as e:
        print('Erro',e)
        return geraResponse(400,"cliente",{},"erro na deleção")



def geraResponse(status,nome_do_conteudo,conteudo,mensagem=False):
    body={}
    body[nome_do_conteudo]=conteudo
    if(mensagem):
        body["mensagem"]=mensagem

    return Response(jsons.dumps(body),status=status,mimetype="application/json")

   
if __name__ == '__main__':
    app.debug = True
    app.run()
