from aiogram.types import LinkPreviewOptions
from logging import info, error
from bot.bot_instance import bot

mensagens = {}
MAX_TAMANHO = 4000


def dividir_texto(texto):
    partes = []

    while len(texto) > MAX_TAMANHO:
        corte = texto.rfind("\n", 0, MAX_TAMANHO)

        if corte == -1:
            corte = MAX_TAMANHO

        partes.append(texto[:corte])
        texto = texto[corte:]

    if texto:
        partes.append(texto)

    return partes

def resumir_texto_log(texto):
    texto = (
        texto
        .replace("\n", " ")
        .replace("━━━━━━━━━━━━", "|")
    )

    if len(texto) > 200:
        return texto[:200] + "..."

    return texto

async def enviar_mensagem(chat_id, texto):
    try:
        partes = dividir_texto(texto)

        for parte in partes:
            msg = await bot.send_message(
                chat_id=chat_id,
                text=parte,
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )

            mensagens.setdefault(chat_id, []).append(msg.message_id)

        info(f"Mensagem enviada para {chat_id}, texto: {resumir_texto_log(texto)}")

    except Exception as e:
        error(f"Erro ao enviar mensagem: {e}")