# -*- coding: utf-8 -*-
'''
Create Date: 2023/07/07
Author: @1chooo(Hugo ChunHo Lin)
Version: v0.0.1
'''

import os
import json
from datetime import datetime
from Monster.Drama import AboutUsDrama
from Monster.Drama import TestHandler
from Monster.Drama import ErrorHandler
from Monster.Drama import message_handlers
from Monster.Utils import ConsoleLogger
from Monster.Utils import FileHandler
from flask import Flask, request, abort
from linebot import LineBotApi
from linebot import WebhookHandler
from linebot.models import TextMessage
from linebot.models import ImageMessage
from linebot.models import VideoMessage
from linebot.models import AudioMessage
from linebot.models.events import FollowEvent
from linebot.models.events import MessageEvent
from linebot.exceptions import LineBotApiError
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.', 'config')
config_path = os.path.join(config_dir, 'linebot.conf')
line_bot_config = json.load(open(config_path, 'r', encoding='utf8'))

CURRENT_DATE = datetime.today().strftime('%Y%m%d')

LINE_BOT_API = LineBotApi(line_bot_config['CHANNEL_ACCESS_TOKEN'])
HANDLER = WebhookHandler(line_bot_config['CHANNEL_SECRET'])
USER_LOG_PATH = os.path.join('.', 'log', CURRENT_DATE)

about_us_drama = AboutUsDrama(LINE_BOT_API, HANDLER)
test_handler = TestHandler(LINE_BOT_API, HANDLER)
error_handler = ErrorHandler(LINE_BOT_API, HANDLER)
console_logger = ConsoleLogger(LINE_BOT_API, HANDLER, USER_LOG_PATH)
file_handler = FileHandler(LINE_BOT_API, USER_LOG_PATH, CURRENT_DATE)

file_handler.create_directory(USER_LOG_PATH)

READY_TO_GET_MONSTER_NAME = False

@app.route('/callback', methods=['POST'])
def callback() -> str:
    global USER_LOG_PATH

    signature = request.headers['X-Line-Signature'] # get X-Line-Signature header value
    body = request.get_data(as_text=True)   # get request body as text

    console_logger.store_user_event(body)

    try:        # handle webhook body
        HANDLER.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@HANDLER.add(FollowEvent)
def handle_user_profile(event: FollowEvent) -> None:
    global USER_LOG_PATH
    
    try:
        user_profile = LINE_BOT_API.get_profile(event.source.user_id)
    except LineBotApiError as e:    # Handling the fails when obtaining the user profile
        console_logger.line_bot_api_error_console(e)
        return

    console_logger.store_user_info(user_profile)
        
@HANDLER.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent) -> None:
    try:
        message_text = event.message.text
        message_handler = message_handlers.get(
            message_text, # Retrieve the corresponding message handler function from the dictionary,
            error_handler.handle_unknown_text_message # error handler if not found
        )

        message_handler(event)  # Call the corresponding message handler function to process the message

    except Exception as e:
        console_logger.text_exception_console(e)
        error_handler.handle_invalid_text_message(event)

@HANDLER.add(MessageEvent, message=ImageMessage)
def handle_image_message(event: MessageEvent) -> None:
    global USER_LOG_PATH

    test_handler.handle_test_image_message(event)

    try:    # Download the image
        file_handler.download_file(event, 'imgs', '.jpg')

    except LineBotApiError as e:
        console_logger.image_exception_console(e)
        error_handler.handle_invalid_image_message(event)

@HANDLER.add(MessageEvent, message=VideoMessage)
def handle_video_message(event: MessageEvent) -> None:
    global USER_LOG_PATH

    test_handler.handle_test_video_message(event)

    try:    # Download the audio
        file_handler.download_file(event, 'video', '.mp4')

    except LineBotApiError as e:
        console_logger.image_exception_console(e)
        error_handler.handle_invalid_video_message(event)

@HANDLER.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event: MessageEvent) -> None:
    global USER_LOG_PATH

    test_handler.handle_test_audio_message(event)

    try:    # Download the audio
        file_handler.download_file(event, 'audio', '.mp3')

    except LineBotApiError as e:
        console_logger.audio_exception_console(e)
        error_handler.handle_invalid_audio_message(event)

def start_flask() -> None:
    app.run(port=5002)

def main() -> None:
    start_flask()

if __name__ == '__main__':
    main()
