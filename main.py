import gratzbot
import time
from usertypes import Update

bot = gratzbot.Gratzbot()
while True:
    updates = bot.request_updates()
    for o in updates:
        update = Update.model_validate(o)
        if bot.update_id >= update.update_id:
            continue
        bot.update_id = update.update_id
        username: str = update.message.user_from.first_name
        text: str = update.message.text
        print(f"{username}: {text}")
    time.sleep(5)
