import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)

# Define states for conversation flow
CATEGORY, FULL_NAME, AGE, SUBMISSION_TEXT, PHOTO_OPTION = range(5)

# Load environment variables
BOT_TOKEN = os.getenv("7263594502:AAECaDzlqJqHuZ-mMIiUiHfItvGc29ETZW8")
GROUP_CHAT_ID = int(os.getenv("+rIWRz_ILrNhlZjI1"))

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 Story", callback_data="story")],
        [InlineKeyboardButton("💬 Quote", callback_data="quote")],
        [InlineKeyboardButton("📝 Poem", callback_data="poem")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to our content submission system! 😊\nPlease choose a category:",
        reply_markup=reply_markup,
    )
    return CATEGORY

# Handle category selection
async def category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    context.user_data["category"] = category.capitalize()  # Store selected category
    await query.edit_message_text(f"You selected {category.capitalize()}! Now, please enter your full name:")
    return FULL_NAME

# Collect full name
async def collect_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text
    context.user_data["full_name"] = full_name
    await update.message.reply_text(f"Thank you, {full_name}! How old are you?")
    return AGE

# Collect age
async def collect_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text
    if not age.isdigit():
        await update.message.reply_text("Please enter a valid age (numbers only):")
        return AGE
    context.user_data["age"] = age
    await update.message.reply_text("Great! Please send your text submission now.")
    return SUBMISSION_TEXT

# Collect text submission
async def collect_submission_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    submission_text = update.message.text
    context.user_data["submission_text"] = submission_text
    keyboard = [
        [InlineKeyboardButton("Yes ✅", callback_data="yes")],
        [InlineKeyboardButton("No ❌", callback_data="no")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Would you like to upload a photo related to your submission?", reply_markup=reply_markup)
    return PHOTO_OPTION

# Handle photo option
async def handle_photo_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "yes":
        await query.edit_message_text("Please upload your photo now.")
        return PHOTO_OPTION
    else:
        context.user_data["photo"] = None
        await finalize_submission(update, context)
        return ConversationHandler.END

# Handle photo upload
async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"{update.message.from_user.id}_photo.jpg"
    await photo_file.download_to_drive(photo_path)
    context.user_data["photo"] = photo_path
    await finalize_submission(update, context)
    return ConversationHandler.END

# Finalize submission and forward to group
async def finalize_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = context.user_data["category"]
    full_name = context.user_data["full_name"]
    age = context.user_data["age"]
    submission_text = context.user_data["submission_text"]
    photo = context.user_data.get("photo")

    # Prepare message
    message = f"Category: {category}\nName: {full_name}\nAge: {age}\nSubmission:\n{submission_text}"
    
    # Forward to group
    if photo:
        with open(photo, "rb") as photo_file:
            await context.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=photo_file, caption=message)
    else:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

    # Confirm to user
    await update.message.reply_text("Thank you for your submission! 🎉")
    keyboard = [
        [InlineKeyboardButton("Submit Another Entry 🔁", callback_data="restart")],
        [InlineKeyboardButton("Contact Admin 📩", url="https://t.me/your_admin_username")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What would you like to do next?", reply_markup=reply_markup)

# Restart conversation
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Restarting...")
    return await start(update, context)

# Cancel conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Submission canceled. Feel free to start again with /start.")
    return ConversationHandler.END

# Main function to run the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CATEGORY: [CallbackQueryHandler(category_selection)],
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_full_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_age)],
            SUBMISSION_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_submission_text)],
            PHOTO_OPTION: [
                CallbackQueryHandler(handle_photo_option),
                MessageHandler(filters.PHOTO, handle_photo_upload),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    application.run_polling()

if __name__ == "__main__":
    main()