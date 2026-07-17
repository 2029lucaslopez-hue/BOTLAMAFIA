from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import aiohttp
import time

TOKEN = "8600182381:AAGyWKXc3YMpk9cIyKlQONO_wB6BKpvvzd0"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 Ver Precios", callback_data="ver_precios")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    texto = (
        "🔥 *LA MAFIA GRUPO VIP* 🔥\n\n"
        "🇦🇷 El mejor contenido de Argentinas\n\n"
        "👑 Accedé al grupo VIP y disfrutá contenido exclusivo\n"
        "✨ Elegí el plan que más te convenga"
    )

    with open("lamafia.png", "rb") as foto:
        await update.message.reply_photo(
            photo=foto,
            caption=texto,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def ver_precios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("SEMANAL: 5000 ARS", callback_data="plan_semanal")],
        [InlineKeyboardButton("MENSUAL: 10000 ARS", callback_data="plan_mensual")],
        [InlineKeyboardButton("PERMANENTE: 50000 ARS", callback_data="plan_permanente")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_caption(
        caption=(
            "💰 *Elegí tu plan de acceso* 💰\n\n"
            "Seleccioná una opción para continuar:"
        ),
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# --- Cache simple de cotizaciones ---
_CACHE_COTIZACIONES = {"data": None, "timestamp": 0}
_CACHE_TTL_SEGUNDOS = 60  # tiempo que se reutiliza la cotización antes de volver a consultar


async def obtener_cotizaciones():
    """
    Trae las cotizaciones actuales de BTC, ETH, USDT y LTC en ARS
    usando la API pública de CoinGecko, con cache de _CACHE_TTL_SEGUNDOS.
    Devuelve un dict {"bitcoin": valor_ars, "ethereum": valor_ars, ...}
    o None si falla la consulta y no hay nada en cache.
    """
    ahora = time.time()

    # Si el cache todavía es válido, lo reutilizamos sin pegarle a la API
    if (
        _CACHE_COTIZACIONES["data"] is not None
        and ahora - _CACHE_COTIZACIONES["timestamp"] < _CACHE_TTL_SEGUNDOS
    ):
        return _CACHE_COTIZACIONES["data"]

    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin,ethereum,tether,litecoin&vs_currencies=ars"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
        cotizaciones = {
            "bitcoin": data["bitcoin"]["ars"],
            "ethereum": data["ethereum"]["ars"],
            "tether": data["tether"]["ars"],
            "litecoin": data["litecoin"]["ars"],
        }
        # Guardamos en cache para las próximas consultas
        _CACHE_COTIZACIONES["data"] = cotizaciones
        _CACHE_COTIZACIONES["timestamp"] = ahora
        return cotizaciones
    except Exception as e:
        print(f"⚠️ Error obteniendo cotizaciones: {e}")
        # Si falla pero hay algo viejo en cache, mejor usar eso que nada
        if _CACHE_COTIZACIONES["data"] is not None:
            return _CACHE_COTIZACIONES["data"]
        return None


async def plan_seleccionado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    planes = {
        "plan_semanal": ("💰 SEMANAL", 5000),
        "plan_mensual": ("💰 MENSUAL", 10000),
        "plan_permanente": ("💰 PERMANENTE", 50000),
    }

    nombre, precio_ars = planes[query.data]

    cotizaciones = await obtener_cotizaciones()

    if cotizaciones:
        btc = precio_ars / cotizaciones["bitcoin"]
        eth = precio_ars / cotizaciones["ethereum"]
        usdt = precio_ars / cotizaciones["tether"]
        ltc = precio_ars / cotizaciones["litecoin"]

        texto_cripto = (
            f"₿ *BITCOIN (red nativa)*\n"
            f"`{btc:.8f}` BTC\n"
            f"`bc1quft956txvpp6r84pkyv9tx56ql57rshwwugyka`\n\n"
            f"Ξ *ETHEREUM (red ERC20)*\n"
            f"`{eth:.6f}` ETH\n"
            f"`0x697B0c043dB076Af021715400c6673124BdcE87F`\n\n"
            f"💵 *USDT (red TRON - TRC20)*\n"
            f"`{usdt:.2f}` USDT\n"
            f"`THvWwxW2DaLMy3dM6f9u6KHWFJrkEHzwxT`\n\n"
            f"Ł *LITECOIN (red LTC)*\n"
            f"`{ltc:.6f}` LTC\n"
            f"`ltc1qk9tr4pctu3nayp2j57j0e44fcfn0uwethvfg4l`\n\n"
            f"⚠️ _Las cotizaciones son en tiempo real y pueden variar. "
            f"Verificá el monto antes de enviarlo._"
        )
    else:
        texto_cripto = (
            "⚠️ No se pudo obtener la cotización en este momento. "
            "Por favor esperá unos segundos y volvé a intentar, "
            "o consultá el valor manualmente antes de transferir."
        )

    # Acá podés poner el mensaje/instrucciones de pago que quieras mostrar
    await query.message.reply_text(
        f"✅ Elegiste el plan *\"{nombre}\"* por *${precio_ars} ARS*\n\n"
        f"🏦 *Transferencia bancaria*\n"
        f"Alias: LAMAFIA-VIP\n"
        f"Nombre: Gustavo Cardenas\n\n"
        f"🪙 *O pagá con crypto:*\n\n"
        f"{texto_cripto}\n\n"
        f"📩 Al realizar el pago, enviá el comprobante acá mismo en el chat.",
        parse_mode="Markdown",
    )


async def recibir_comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙏💖 *¡Muchísimas gracias por confiar en nosotros!* 💖🙏\n\n"
        "✅ Recibimos tu comprobante con éxito.\n\n"
        "⚡ Para *agilizar el proceso* y activarte cuanto antes, por favor "
        "reenvialo también a @dascilia1 o @alvaro909 📤\n\n"
        "👑 En cuanto lo confirmemos, te damos acceso al *grupo VIP* 🔥\n"
        "⏳ ¡Ya casi estás adentro! 🚀💎",
        parse_mode="Markdown",
    )


async def post_init(app):
    # Elimina cualquier webhook activo y descarta updates pendientes
    # para evitar el error "Conflict: terminated by other getUpdates request"
    await app.bot.delete_webhook(drop_pending_updates=True)


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(ver_precios, pattern="^ver_precios$"))
    app.add_handler(
        CallbackQueryHandler(
            plan_seleccionado,
            pattern="^(plan_semanal|plan_mensual|plan_permanente)$",
        )
    )
    app.add_handler(
        MessageHandler(filters.PHOTO | filters.Document.ALL, recibir_comprobante)
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
