from flask import Flask, render_template, redirect, request, flash, send_from_directory, make_response, jsonify
import json
import ast
import os
from pathlib import Path
import mysql.connector

caminho = Path(__file__)
pasta_atual = caminho.parent

app = Flask(__name__)
app.config['SECRET_KEY'] = '71ecabb15a22589b237d0c3cbe56f086'
app.config['JSON_SORT_KEYS'] = False

logado = False


@app.route('/')
def home():
    global logado
    logado = False
    return render_template('login.html')


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/usuariocriarconta')
def usuariocriarconta():
    return render_template('/usuariocriarconta.html')


@app.route('/adm')
def adm():
    if logado == True:
        conect_BD = mysql.connector.connect(host='localhost', database='usuarios', user='root', password='')
        if conect_BD.is_connected():
            cursur = conect_BD.cursor()
            cursur.execute('select * from usuario;')
            usuarios = cursur.fetchall()
        return render_template("administrador.html", usuarios=usuarios)
    if logado == False:
        return redirect('/')


#Conexão para o GET no Postman
@app.route('/api', methods=['GET'])
def get_usuarios():
    usuario = request.json
    #Conexão com o banco de dados
    conect_BD = mysql.connector.connect(host='localhost', database='usuarios', user='root', password='')
    cursur = conect_BD.cursor()
    cursur.execute('select * from usuario')
    #Busca todos os registros no banco de dados
    api = cursur.fetchall()

    #Organização da lista de usuários na API
    usuarios = list()
    for usuario in api:
        usuarios.append(
            {
                'id': usuario[0],
                'email': usuario[1],
                'senha': usuario[2],
            }
        )

    #Retorna uma lista de lista de todos os usuários cadastrados no Banco de Dados
    return make_response(
        jsonify(
            memsagem='Lista de usuarios.',
            usuario=usuarios
        )
    )


#Conexão para o POST no Postman
@app.route('/api', methods=['POST'])
def create_usuarios():
    usuario = request.json
    # Conexão com o banco de dados
    conect_BD = mysql.connector.connect(host='localhost', database='usuarios', user='root', password='')
    cursur = conect_BD.cursor()
    # Insert no banco de dados
    sql = f"insert into usuario (nome, senha) values ('{usuario['nome']}', '{usuario['senha']}')"
    cursur.execute(sql)
    conect_BD.commit()

    return make_response(
        jsonify(
            mensagem='Usuário cadastrado com sucesso.',
            usuario=usuario
        )
    )


@app.route('/usuarios')
def usuarios():
    if logado == True:
        arquivo = []
        for documento in os.listdir(f'{pasta_atual}/arquivos'):
            arquivo.append(documento)
        return render_template("usuarios.html", arquivos=arquivo)
    else:
        return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    global logado
    nome = request.form.get('nome')
    senha = request.form.get('senha')

    conect_BD = mysql.connector.connect(host='localhost', database='usuarios', user='root', password='')
    cont = 0
    if conect_BD.is_connected():
        cursur = conect_BD.cursor()
        cursur.execute('select * from usuario;')
        usuariosBD = cursur.fetchall()

        for usuario in usuariosBD:
            cont += 1
            usuarioNome = str(usuario[1])
            usuarioSenha = str(usuario[2])

            if nome == 'adm@artflex.com.br' and senha == '000111222':
                logado = True
                return redirect('/adm')

            if usuarioNome == nome and usuarioSenha == senha:
                logado = True
                return redirect('/usuarios')

            if cont >= len(usuariosBD):
                flash('Usuário inválido')
                return redirect("/")
    else:
        return redirect('/')


@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    global logado
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    conect_BD = mysql.connector.connect(host='localhost', database='usuarios', user='root', password='')

    if conect_BD.is_connected():
        cursur = conect_BD.cursor()
        cursur.execute(f"insert into usuario values (default, '{nome}', '{senha}');")
        conect_BD.commit()

    if conect_BD.is_connected():
        cursur.close()
        conect_BD.close()


    logado = True
    flash(F'{nome} foi cadastrado(a)!')
    return redirect('/adm')


@app.route('/excluirUsuario', methods=['POST'])
def excluirUsuario():
    global logado
    logado = True
    nome = request.form.get('nome')
    usuarioID = request.form.get('usuarioPexcluir')
    conect_BD = mysql.connector.connect(host='localhost', database='usuarios', user='root', password='')

    if conect_BD.is_connected():
        cursur = conect_BD.cursor()
        cursur.execute(f"delete from usuario where id='{usuarioID}'; ")
        conect_BD.commit()

    if conect_BD.is_connected():
        cursur.close()
        conect_BD.close()


    flash(F'{nome} foi excluído(a)!')
    return redirect('/adm')


@app.route("/upload", methods=['POST'])
def upload():
    global logado
    logado = True

    arquivo = request.files.get('documento')
    nome_arquivo = arquivo.filename.replace(" ", "-")
    arquivo.save(os.path.join(f'{pasta_atual}/arquivos/', nome_arquivo))

    flash('Arquivo salvo')
    return redirect('/adm')


@app.route('/download', methods=['POST'])
def download():
    nomeArquivo = request.form.get('arquivosParaDownload')

    return send_from_directory('arquivos', nomeArquivo, as_attachment=True)


if __name__ in "__main__":
    app.run(debug=True)