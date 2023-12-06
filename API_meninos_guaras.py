from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import configparser
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

controller = Flask(__name__)
CORS(controller)

config = configparser.ConfigParser()
config.read('application.properties')

database_uri = f"postgresql://{config['postgres']['user']}:{config['postgres']['password']}@{config['postgres']['host']}:{config['postgres']['port']}/{config['postgres']['database']}"
engine = create_engine(database_uri)

# connection = pg.connect(
#         database = 'railway',
#         host = 'containers-us-west-147.railway.app',
#         user = 'postgres',
#         password = 'jwiQVvjFu8nG2Yw3rpt5',
#         port = '5545'
#     )

# cursor = connection.cursor()

@controller.route('/crianca', methods=['POST'])
def incluir_registro_anemometro():
    uuidRandom = uuid.uuid4()
    
    query = "INSERT INTO criancas (id, nome, apelido, responsavel, telefone, numero_tenis, posicao, posicao_secundaria, categoria, tamanho_camiseta, tamanho_calca, data_nascimento ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    data_nascimento_str = request.get_json().get('data_nascimento')
    data_nascimento = datetime.strptime(data_nascimento_str, "%d/%m/%Y")

    data_nascimento_corrigida = data_nascimento + timedelta(days=1)

    with engine.connect() as connection:
        connection.execute(query, (
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
            data_nascimento_corrigida.date(),
        ))
    
    connection.commit()
    return obter_registro_criancas_id(str(uuidRandom))

@controller.route('/crianca/<id>', methods=['PUT'])
def atualizar_registro_crianca(id):
    uuid_atualizar = id

    query = """
        UPDATE criancas
        SET nome = :nome,
            apelido = :apelido,
            responsavel = :responsavel,
            telefone = :telefone,
            numero_tenis = :numero_tenis,
            posicao = :posicao,
            posicao_secundaria = :posicao_secundaria,
            categoria = :categoria,
            tamanho_camiseta = :tamanho_camiseta,
            tamanho_calca = :tamanho_calca,
            data_nascimento = :data_nascimento
        WHERE id = :uuid_atualizar
    """

    data_nascimento_str = request.get_json().get('data_nascimento')
    data_nascimento = datetime.strptime(data_nascimento_str, "%d/%m/%Y")
    data_nascimento_corrigida = data_nascimento + timedelta(days=1)

    parametros = {
        'nome': request.get_json().get('nome'),
        'apelido': request.get_json().get('apelido'),
        'responsavel': request.get_json().get('responsavel'),
        'telefone': request.get_json().get('telefone'),
        'numero_tenis': request.get_json().get('numero_tenis'),
        'posicao': request.get_json().get('posicao'),
        'posicao_secundaria': request.get_json().get('posicao_secundaria'),
        'categoria': request.get_json().get('categoria'),
        'tamanho_camiseta': request.get_json().get('tamanho_camiseta'),
        'tamanho_calca': request.get_json().get('tamanho_calca'),
        'data_nascimento': data_nascimento_corrigida.date(),
        'uuid_atualizar': uuid_atualizar
    }

    with engine.connect() as connection:
        connection.execute(text(query), parametros)

    return obter_registro_criancas_id(uuid_atualizar)

@controller.route('/crianca/<id>', methods=['GET'])
def obter_registro_criancas_id(id):
    query = "SELECT * FROM criancas WHERE id = :id"
    
    parametros = {'id': id}

    with engine.connect() as connection:
        resultado = connection.execute(text(query), parametros)
        registro = resultado.fetchone()

    if registro:
        registro_dict = dict(registro.items())
        return registro_dict
    else:
        return jsonify({'message': 'Registro não encontrado'}), 404


@controller.route('/crianca', methods=['GET'])
def obter_registros_paginados_criancas_id():
    query = "SELECT * FROM criancas"

    with engine.connect() as connection:
        resultado = connection.execute(text(query))
        colunas = resultado.keys()  # Obter os nomes das colunas
        registros = resultado.fetchall()

    registros_lista = [dict(zip(colunas, registro)) for registro in registros]

    return jsonify(registros_lista)

@controller.route('/crianca/<id>', methods=['DELETE'])
def delete_registro_crainca(id):
    query = "DELETE FROM criancas WHERE id = :id"

    with engine.connect() as connection:
        connection.execute(text(query), id=str(id))

    return "Excluído"

if __name__ == "__main__":
    controller.run(port=5000, host='0.0.0.0', debug=True)