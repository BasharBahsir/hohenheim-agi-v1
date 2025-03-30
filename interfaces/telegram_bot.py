import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
from core.agi_core import HohenheimAGI

class TelegramInterface:
    def __init__(self, agi: HohenheimAGI):
        self.agi = agi
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.allowed_user_id = os.getenv('TELEGRAM_USER_ID')
        self.logger = logging.getLogger(__name__)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process incoming Telegram messages"""
        if str(update.effective_user.id) != self.allowed_user_id:
            await update.message.reply_text("Unauthorized access")
            return

        user_input = update.message.text
        self.logger.info(f"Received Telegram message: {user_input}")
        
        # Get AGI response
        response = self.agi.process_input(user_input)
        
        # Send response back
        await update.message.reply_text(response)

    def run(self):
        """Start the Telegram bot"""
        application = ApplicationBuilder().token(self.token).build()
        
        # Add handlers
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))
        
        self.logger.info("Telegram bot started")
        application.run_polling()