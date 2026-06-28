from asyncio import sleep
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from logging import info
from vagas.envio import enviar_vagas
import bot.comandos as comandos

TZ = ZoneInfo("America/Sao_Paulo")

proxima_execucao = None

async def iniciar_agendador():
    global proxima_execucao

    while True:

        agora = datetime.now(TZ)

        proxima_execucao = agora.replace(
            hour=17,
            minute=0,
            second=0,
            microsecond=0
        )

        if agora >= proxima_execucao:
            proxima_execucao += timedelta(days=2)

        segundos = (
            proxima_execucao - agora
        ).total_seconds()

        await sleep(segundos)

        chave = (0, "/vagas")

        busca_em_andamento = False

        for _, comando in comandos.comandos_em_andamento:

            if comando == "/vagas":
                busca_em_andamento = True
                break

        if busca_em_andamento:
            info("Execução automática ignorada porque o comando /vagas já está em andamento.")
            continue

        try:
            info("Iniciando execução automática de vagas.")

            comandos.comandos_em_andamento.add(chave)

            await enviar_vagas()

            info("Execução automática finalizada.")

        finally:
            comandos.comandos_em_andamento.discard(chave)


