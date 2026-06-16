from dotenv import load_dotenv
from os import getenv

from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from aiohttp import web
from asyncio import run, CancelledError, create_task, Event

from logging import info, warning, basicConfig, INFO, error, getLogger, WARNING

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
WEBHOOK_PATH = "/webhook"
BASE_URL = getenv("WEBHOOK_URL")

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


async def healthcheck(request):
    return web.Response(text="Bot online")

async def iniciar_webhook():
    app = web.Application()

    app.router.add_get("/", healthcheck)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    ).register(app, path=WEBHOOK_PATH)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(getenv("PORT", 10000))

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    info(f"Servidor rodando na porta {port}")

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(f"{BASE_URL}{WEBHOOK_PATH}")


async def main():
    info("Bot iniciado...")

    create_task(execucao_automatica.iniciar_agendador())

    try:
        await iniciar_webhook()
        await Event().wait()

    except (KeyboardInterrupt, CancelledError):
        warning("Bot finalizado manualmente.")

    except Exception as e:
        error(f"Erro inesperado: {e}")

    finally:
        await bot.session.close()
        info("Sessão do bot fechada.")


if __name__ == "__main__":
    run(main())