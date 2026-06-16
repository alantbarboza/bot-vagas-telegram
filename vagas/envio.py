from asyncio import sleep, to_thread
from logging import error, info
from vagas.buscador import buscar_vagas
from vagas.filtros import contar_vagas, carregar_usuarios, filtrar_vaga
from bot.mensagens import dividir_texto, enviar_mensagem

def formatar_vaga(vaga):

    empresa = vaga.get("company") or "Não informado"

    return (
        f"💼 {vaga['title']}\n"
        f"🏢 Empresa: {empresa}\n"
        f"📍 Local: {vaga['location']}\n"
        f"🌐 Fonte: {vaga['source']}\n"
        f"⭐ Pontuação: {vaga['score']}\n"
        f"📅 Publicação: {vaga['posted_date']}\n"
        f"🔗 Link: {vaga['link']}\n"
        f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )


async def enviar_vagas(chat_id_destino=None):

    usuarios = carregar_usuarios()

    if chat_id_destino:
        chat_id_destino = str(chat_id_destino)
        usuarios = {chat_id_destino: usuarios[chat_id_destino]}

    try:
        for chat_id in usuarios.keys():
            await enviar_mensagem(int(chat_id), "Pesquisando vagas...")

        vagas = await to_thread(buscar_vagas)

        info(f"Busca concluída. {len(vagas)} vagas únicas encontradas.")

        if not vagas:
            for chat_id in usuarios.keys():
                await enviar_mensagem(int(chat_id), "Nenhuma vaga encontrada.")
            return

        for chat_id, usuario in usuarios.items():

            info(f"Processando vagas para {usuario['nome']}")

            vagas_usuario = filtrar_vaga(vagas, usuario)

            if not vagas_usuario:
                await enviar_mensagem(
                    int(chat_id),
                    "Nenhuma vaga compatível foi encontrada."
                )
                continue

            total_vagas = contar_vagas(vagas_usuario)

            await enviar_mensagem(
                int(chat_id),
                f"{total_vagas}\n"
            )

            texto_final = ""

            for vaga in vagas_usuario:
                texto_final += formatar_vaga(vaga)

            partes = dividir_texto(texto_final)

            for parte in partes:
                await enviar_mensagem(int(chat_id), parte)
                await sleep(2)

    except Exception as erro:
        error(f"Erro ao enviar vagas: {erro}")

        for chat_id in usuarios.keys():
            try:
                await enviar_mensagem(int(chat_id), "Erro ao buscar vagas.")
            except:
                pass