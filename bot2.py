from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = "8709893016:AAHwX9hInT0Q7ckhGd5kkaMlN3TwQ3G-MG0"


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

    await update.message.reply_text(
        text=texto,
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

    await query.edit_message_text(
        text=(
            "💰 *Elegí tu plan de acceso* 💰\n\n"
            "Seleccioná una opción para continuar:"
        ),
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def plan_seleccionado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    planes = {
        "plan_semanal": ("SEMANAL", "5000 ARS"),
        "plan_mensual": ("MENSUAL", "10000 ARS"),
        "plan_permanente": ("PERMANENTE", "50000 ARS"),
    }

    nombre, precio = planes[query.data]

    # Acá podés poner el mensaje/instrucciones de pago que quieras mostrar
    await query.message.reply_text(
        f"✅ Elegiste el plan \"{nombre}\" por \"{precio}\".\n\n"
        f"CBU: 0000000000000000000000\n"
        f"Alias: LAMAFIA-VIP\n"
        f"Nombre: Juan Ignacio Yivotinsky\n\n"
        f"Al realizar el pago enviar comprobante a @dascilia1 o @alvaro909.",
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

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
