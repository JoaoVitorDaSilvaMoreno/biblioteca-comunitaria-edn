from flask import Flask, render_template, request, redirect, session
from datetime import date
import subprocess

app = Flask(__name__)
app.secret_key = "biblioteca_edn"

biblioteca = []
usuarios = []
historico = []


# =====================================
# FUNÇÃO DE ÁUDIO
# =====================================

def falar(texto):

    try:

        mensagem = str(texto).replace("'", "''")

        comando = (
            "Add-Type -AssemblyName System.Speech; "
            "$voz = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$voz.Speak('{mensagem}')"
        )

        subprocess.run(
            ["powershell", "-NoProfile", "-Command", comando],
            capture_output=True
        )

    except:
        pass


# =====================================
# LOGIN ADMINISTRATIVO
# =====================================

def acesso_adm(usuario, senha):

    administrador = "Camilla Cleanne"
    senha_adm = "EscolaDaNuvem1234"

    return usuario == administrador and senha == senha_adm


# =====================================
# LOGIN
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if acesso_adm(usuario, senha):

            session["logado"] = True

            falar("Acesso permitido")

            return redirect("/")

        falar("Acesso negado")

    return render_template("login.html")


# =====================================
# HOME
# =====================================

@app.route("/")
def home():

    if not session.get("logado"):
        return redirect("/login")

    return render_template("index.html")


# =====================================
# LIVROS
# =====================================

@app.route("/livros", methods=["GET", "POST"])
def livros():

    if not session.get("logado"):
        return redirect("/login")

    if request.method == "POST":

        codigo = request.form["codigo"]
        titulo = request.form["titulo"]
        autor = request.form["autor"]

        for livro in biblioteca:

            if livro["codigo"] == codigo:
                return redirect("/livros")

        biblioteca.append({
            "codigo": codigo,
            "titulo": titulo,
            "autor": autor,
            "disponivel": True,
            "emprestado_para": None
        })

        historico.append(
            f"Livro '{titulo}' cadastrado."
        )

        falar("Livro cadastrado com sucesso")

        return redirect("/livros")

    return render_template(
        "livros.html",
        livros=biblioteca
    )


# =====================================
# USUÁRIOS
# =====================================

@app.route("/usuarios", methods=["GET", "POST"])
def usuarios_page():

    if not session.get("logado"):
        return redirect("/login")

    if request.method == "POST":

        nome = request.form["nome"]
        cpf = request.form["cpf"]

        for usuario in usuarios:

            if usuario["cpf"] == cpf:
                return redirect("/usuarios")

        usuarios.append({
            "nome": nome,
            "cpf": cpf,
            "telefone": request.form["telefone"],
            "email": request.form["email"],
            "endereco": request.form["endereco"]
        })

        historico.append(
            f"Usuário '{nome}' cadastrado."
        )

        falar("Usuário cadastrado com sucesso")

        return redirect("/usuarios")

    return render_template(
        "usuarios.html",
        usuarios=usuarios
    )


# =====================================
# EMPRÉSTIMO
# =====================================

@app.route("/emprestimo", methods=["GET", "POST"])
def emprestimo():

    if not session.get("logado"):
        return redirect("/login")

    if request.method == "POST":

        codigo = request.form["codigo"]
        usuario = request.form["usuario"]

        for livro in biblioteca:

            if livro["codigo"] == codigo:

                if livro["disponivel"]:

                    livro["disponivel"] = False
                    livro["emprestado_para"] = usuario
                    livro["emprestimo_data"] = str(date.today())

                    historico.append(
                        f"{usuario} pegou '{livro['titulo']}' em {date.today()}"
                    )

                    falar("Empréstimo realizado")

                break

        return redirect("/emprestimo")

    return render_template(
        "emprestimos.html",
        livros=biblioteca,
        usuarios=usuarios
    )


# =====================================
# DEVOLVER LIVRO
# =====================================

@app.route("/devolver", methods=["GET", "POST"])
def devolver():

    if not session.get("logado"):
        return redirect("/login")

    if request.method == "POST":

        codigo = request.form["codigo"]

        for livro in biblioteca:

            if livro["codigo"] == codigo:

                if not livro["disponivel"]:

                    usuario = livro["emprestado_para"]

                    livro["disponivel"] = True
                    livro["emprestado_para"] = None

                    historico.append(
                        f"{usuario} devolveu '{livro['titulo']}'"
                    )

                    falar("Livro devolvido")

                break

        return redirect("/devolver")

    return render_template(
        "devolver.html"
    )


# =====================================
# PESQUISAR LIVRO
# =====================================

@app.route("/pesquisar", methods=["GET", "POST"])
def pesquisar():

    if not session.get("logado"):
        return redirect("/login")

    resultado = []

    if request.method == "POST":

        termo = request.form["titulo"].lower()

        for livro in biblioteca:

            if termo in livro["titulo"].lower():

                resultado.append(livro)

    return render_template(
        "pesquisar.html",
        resultado=resultado
    )


# =====================================
# HISTÓRICO
# =====================================

@app.route("/historico")
def historico_page():

    if not session.get("logado"):
        return redirect("/login")

    return render_template(
        "historico.html",
        historico=historico
    )


# =====================================
# SAIR
# =====================================

@app.route("/sair")
def sair():

    session.clear()

    falar("Saindo do sistema")

    return redirect("/login")


# =====================================
# EXECUÇÃO
# =====================================

if __name__ == "__main__":

    app.run(debug=True)