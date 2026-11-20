import html

import models
import settings


async def send_telegram_message(node: str, data: models.LastLogin) -> None:
    '''
    Send message for telegram CHAT.
    '''
    from telegram import Bot
    from telegram.constants import ParseMode

    message = f"<b>Atualização de login na máquina {node}</b>\n"
    # Create HTML message to send.
    message += f"\n<code>Usuário</code>: {html.escape(str(data.user))}\n" \
        f"<code>TTY</code>: {html.escape(str(data.tty))}\n" \
        f"<code>IP</code>: {html.escape(str(data.hostname))}\n" \
        f"<code>Serviço</code>: {html.escape(str(data.service))}\n" \
        f"<code>Entrada</code>: {html.escape(str(data.login))}\n" \
        f"<code>Saída</code>: {html.escape(str(data.logout))}" \
        "\n\n--\n"

    # Send messagem with BOT.
    async with Bot(settings.TOKEN) as bot:
        await bot.send_message(
            chat_id=settings.CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML,
        )
