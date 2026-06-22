from re import search, escape
from datetime import datetime, timedelta
from json import load, dump
import os

PERIODO_DIAS = 2
MAX_PAGINAS = 7

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USUARIOS_PATH = os.path.join(BASE_DIR, "usuarios.json")

def carregar_usuarios():
    with open(
        USUARIOS_PATH,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return load(arquivo)
    
def usuario_cadastrado(user_id):
    usuarios = carregar_usuarios()

    return str(user_id) in usuarios

def c():
    usuarios = carregar_usuarios()

    termos = set()

    for usuario in usuarios.values():
        for termo in usuario["termos_busca"]:
            termos.add(
                termo.lower()
            )

    return list(termos)

def obter_filtros_usuario(user_id):
    usuarios = carregar_usuarios()

    return usuarios.get(str(user_id))

def atualizar_dados_usuario(user_id, campo, valor, adicionar=True):
    usuarios = carregar_usuarios()

    usuario = usuarios[str(user_id)]

    if adicionar:
        if valor not in usuario[campo]:
            usuario[campo].append(valor)

    else:
        if valor in usuario[campo]:
            usuario[campo].remove(valor)

    with open(
        USUARIOS_PATH,
        "w",
        encoding="utf-8"
    ) as arquivo:

        dump(
            usuarios,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

def contem_palavra(texto, palavra):
    texto = (texto or "").lower()
    palavra = palavra.lower()

    padrao = rf"(?<!\w){escape(palavra)}(?!\w)"

    return search(padrao, texto) is not None

def validar_conteudo(vaga, usuario):
    conteudo = (
        f"{vaga.get('title') or ''} "
        f"{vaga.get('extra') or ''}"
    ).lower()

    local = (
        vaga.get("location") or ""
    ).lower()

    empresa = (
        vaga.get("company") or ""
    ).lower()

    score = 0

    for palavra in usuario["excluir"]:
        if (
            contem_palavra(conteudo, palavra)
            or contem_palavra(local, palavra)
            or contem_palavra(empresa, palavra)
        ):
            return False, 0

    localizacao_encontrada = False

    for loc in usuario["localizacoes"]:
        if contem_palavra(local, loc):
            localizacao_encontrada = True
            break
    
    if not localizacao_encontrada:
        return False, 0
    
    for nivel in usuario["niveis"]:
        if contem_palavra(conteudo, nivel):
            score += 1

    for cargo in usuario["cargos"]:
        if contem_palavra(conteudo, cargo):
            score += 1

    for tecnologia in usuario["tecnologias"]:
        if contem_palavra(conteudo, tecnologia):
            score += 1

    if score > 1:
        return True, score
    else:
        return False, 0

def filtrar_vaga(vagas, usuario):
    resultado = []

    for vaga in vagas:

        compativel, score = validar_conteudo(vaga, usuario)

        if compativel:

            nova_vaga = vaga.copy()

            nova_vaga["score"] = score

            resultado.append(
                nova_vaga
            )

    return sorted(
        resultado,
        key=lambda x: x["score"],
        reverse=True
    )

def validar_periodo(vagas):
    resultado = []

    limite = datetime.now() - timedelta(days=PERIODO_DIAS)

    for vaga in vagas:

        site = vaga.get("source")

        # Já filtrados pelo próprio site(url)
        if site in ["Nerdin", "Empregos", "InfoJobs"]:
            resultado.append(vaga)
            continue

        # Sem informação de data
        if site == "99jobs":
            resultado.append(vaga)
            continue

        data = vaga.get("posted_date")

        if not data:
            continue

        try:
            data_vaga = datetime.strptime(
                data,
                "%Y-%m-%d"
            )

            if data_vaga >= limite:
                resultado.append(vaga)

        except Exception:
            continue

    return resultado

def contar_vagas(vagas):
    vagas_por_site = {}

    for vaga in vagas:
        site = vaga["source"]

        if site in vagas_por_site:
            vagas_por_site[site] += 1
        else:
            vagas_por_site[site] = 1

    resultado = [f"Total de vagas: {len(vagas)}"]

    for site, quantidade in vagas_por_site.items():
        resultado.append(f"{site}: {quantidade}")

    return "\n".join(resultado)

def remover_duplicadas(vagas):
    vistos = set()
    resultado = []

    for v in vagas:
        chave = v["link"]
        if chave not in vistos:
            vistos.add(chave)
            resultado.append(v)

    return resultado
