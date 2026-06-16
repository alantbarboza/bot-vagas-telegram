from dotenv import load_dotenv
from os import getenv
from aiogram import Dispatcher, Router
from aiogram.types import Message
from asyncio import run, sleep, CancelledError, create_task
from logging import info, warning, critical, basicConfig, INFO, error, getLogger, WARNING
from bot.comandos import verificar_comando, salvar_mensagem
from vagas.filtros import usuario_cadastrado
from bot.bot_instance import bot
import agendamento.execucao_automatica as execucao_automatica

basicConfig(
    level=INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)

getLogger("aiogram.event").setLevel(WARNING)

load_dotenv()
TOKEN = getenv("API_KEY")


dp = Dispatcher()

router = Router()

dp.include_router(router)


@router.message()
async def mensagens_router(message: Message):
    if not usuario_cadastrado(message.from_user.id):
        info(f"Usuário {message.from_user.id} não registrado. Ignorando mensagem.")
        return

    await salvar_mensagem(message)
    await verificar_comando(message, message.chat.type)

async def main():
    info("Bot iniciado...")

    create_task(execucao_automatica.iniciar_agendador())

    tentativas = 0
    MAX_TENTATIVAS = 3

    try:
        while tentativas < MAX_TENTATIVAS:
            try:
                await dp.start_polling(bot)

                info("Polling encerrado normalmente.")
                break

            except (KeyboardInterrupt, CancelledError):
                warning("Bot finalizado manualmente.")
                break

            except Exception as e:
                tentativas += 1

                error(f"Erro inesperado: {e}\n"
                      f"Tentativa de reconexão ({tentativas}/{MAX_TENTATIVAS})...")

                if tentativas >= MAX_TENTATIVAS:
                    critical( "Número máximo de tentativas atingido. Encerrando bot.")
                    break

                await sleep(10)

    finally:
        await bot.session.close()
        info("Sessão do bot fechada.")

if __name__ == "__main__":
    run(main())