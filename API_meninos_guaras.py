from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import configparser
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import pandas as pd
import psycopg2 as pg

controller = Flask(__name__)
CORS(controller)

config = configparser.ConfigParser()
config.read('application.properties')

database_uri = f"postgresql://{config['postgres']['user']}:{config['postgres']['password']}@{config['postgres']['host']}:{config['postgres']['port']}/{config['postgres']['database']}"
engine = create_engine(database_uri)

connection = pg.connect(
        database = 'railway',
        host = 'containers-us-west-147.railway.app',
        user = 'postgres',
        password = 'jwiQVvjFu8nG2Yw3rpt5',
        port = '5545'
    )

cursor = connection.cursor()

@controller.route('/crianca', methods=['POST'])
def incluir_registro_anemometro():
    uuidRandom = uuid.uuid4()

    query = "INSERT INTO criancas (id, nome, apelido, responsavel, telefone, numero_tenis, posicao, posicao_secundaria, categoria, tamanho_camiseta, tamanho_calca, data_nascimento ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    data_nascimento_str = request.get_json().get('data_nascimento')
    data_nascimento = datetime.strptime(data_nascimento_str, "%d/%m/%Y")
    data_nascimento_corrigida = data_nascimento + timedelta(days=1)

    cursor.execute(query, (
        str(uuidRandom),
        str(request.get_json().get('nome')),
        str(request.get_json().get('apelido')),
        str(request.get_json().get('responsavel')),
        str(request.get_json().get('telefone')),
        str(request.get_json().get('numero_tenis')),
        str(request.get_json().get('posicao')),
        str(request.get_json().get('posicao_secundaria')),
        str(request.get_json().get('categoria')),
        str(request.get_json().get('tamanho_camiseta')),
        str(request.get_json().get('tamanho_calca')),
        data_nascimento_corrigida,
    ))

    connection.commit()
    return obter_registro_criancas_id(str(uuidRandom))

@controller.route('/crianca/<id>', methods=['PUT'])
def atualizar_registro_crianca(id):
    uuid_atualizar = id  
    query = """
        UPDATE criancas
        SET nome = %s,
            apelido = %s,
            responsavel = %s,
            telefone = %s,
            numero_tenis = %s,
            posicao = %s,
            posicao_secundaria = %s,
            categoria = %s,
            tamanho_camiseta = %s,
            tamanho_calca = %s,
            data_nascimento = %s
        WHERE id = %s
    """

    data_nascimento_str = request.get_json().get('data_nascimento')
    data_nascimento = datetime.strptime(data_nascimento_str, "%d/%m/%Y")
    data_nascimento_corrigida = data_nascimento + timedelta(days=1)

    cursor.execute(query, (
        str(request.get_json().get('nome')),
        str(request.get_json().get('apelido')),
        str(request.get_json().get('responsavel')),
        str(request.get_json().get('telefone')),
        str(request.get_json().get('numero_tenis')),
        str(request.get_json().get('posicao')),
        str(request.get_json().get('posicao_secundaria')),
        str(request.get_json().get('categoria')),
        str(request.get_json().get('tamanho_camiseta')),
        str(request.get_json().get('tamanho_calca')),
        data_nascimento_corrigida.date(),
        uuid_atualizar
    ))

    connection.commit()
    return obter_registro_criancas_id(uuid_atualizar)

@controller.route('/crianca/<id>', methods=['GET'])
def obter_registro_criancas_id(id):
    query = "SELECT * FROM criancas as l where l.id = '" + id + "'"
    df = pd.read_sql_query(query, con=connection)
    return df.to_dict(orient='records')[0]

@controller.route('/crianca', methods=['GET'])
def obter_registros_paginados_criancas_id():
    query = f"SELECT * FROM criancas"
    df = pd.read_sql_query(query, con=connection)
    return df.to_dict(orient='records')

@controller.route('/crianca/<id>', methods=['DELETE'])
def delete_registro_crainca(id):
    query = "DELETE FROM criancas as l where l.id = '" + id + "'"
    cursor.execute(query, str(id))
    connection.commit()
    return "Excluído"

if __name__ == "__main__":
    controller.run(port=5000, host='0.0.0.0', debug=True)