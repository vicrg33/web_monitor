import requests
import json


def telegram_notify(text):
    # Load json with the sensitive data
    json_info = open('../bot_data.json')
    bot_data = json.load(json_info)
    json_info.close()
    bot_token = bot_data["bot_token"]  # Bot token
    bot_chat_id = bot_data["chat_id"]  # Chat id

    # We will communicate with the bot via HTTPS, so we build the REST request...
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + text
    response = requests.get(send_text)  # And send it

    del json_info, bot_data, bot_token, bot_chat_id, send_text, response  # Clear the variables, as they contain
    # sensitive information

    return None
