import telegram
bot = telegram.Bot(token='')
print([u.message.chat.id for u in bot.get_updates()])
