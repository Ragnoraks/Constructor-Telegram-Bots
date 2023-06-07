from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import HttpResponse
from django.http import HttpResponseBadRequest

from django.core.files.uploadedfile import InMemoryUploadedFile

import django.views.decorators.csrf
import django.contrib.auth.decorators
import constructor_telegram_bots.decorators
import telegram_bot.decorators

from telegram_bot.models import (
	TelegramBot,
	TelegramBotCommand, TelegramBotCommandKeyboard, TelegramBotCommandKeyboardButton,
	TelegramBotUser
)

from telegram_bots.tasks import start_telegram_bot as start_telegram_bot_
from telegram_bots.tasks import stop_telegram_bot as stop_telegram_bot_

from typing import Union
import json


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@constructor_telegram_bots.decorators.check_post_request_data_items(request_need_items=('api_token', 'is_private',))
@telegram_bot.decorators.check_telegram_bot_api_token
def add_telegram_bot(request: WSGIRequest, api_token: str, is_private: bool) -> HttpResponse:
	TelegramBot.objects.create(owner=request.user, api_token=api_token, is_private=is_private)

	return HttpResponse('Вы успешно добавили Telegram бота.')

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@constructor_telegram_bots.decorators.check_post_request_data_items(request_need_items=('is_private',))
def edit_telegram_bot(request: WSGIRequest, telegram_bot: TelegramBot, is_private: bool) -> HttpResponse:
	telegram_bot.is_private = is_private
	telegram_bot.save()

	return HttpResponse('Вы успешно изменили Telegram бота.')

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
def delete_telegram_bot(request: WSGIRequest, telegram_bot: TelegramBot) -> HttpResponse:
	telegram_bot.delete()

	return HttpResponse('Вы успешно удалили Telegram бота.')


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
def get_telegram_bot_data(request: WSGIRequest, telegram_bot: TelegramBot) -> HttpResponse:
	return HttpResponse(
		json.dumps(
			telegram_bot.to_dict()
		)
	)


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
def start_telegram_bot(request: WSGIRequest, telegram_bot: TelegramBot) -> HttpResponse:
	start_telegram_bot_.delay(telegram_bot_id=telegram_bot.id)

	return HttpResponse()

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
def stop_telegram_bot(request: WSGIRequest, telegram_bot: TelegramBot) -> HttpResponse:
	stop_telegram_bot_.delay(telegram_bot_id=telegram_bot.id)

	return HttpResponse()


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@constructor_telegram_bots.decorators.check_post_request_data_items(request_need_items=('name', 'command', 'message_text', 'keyboard', 'api_request',))
@telegram_bot.decorators.check_data_for_telegram_bot_command
def add_telegram_bot_command(
	request: WSGIRequest,
	telegram_bot: TelegramBot,
	name: str,
	command: Union[str, None],
	image: Union[InMemoryUploadedFile, None],
	message_text: str,
	keyboard: Union[dict, None],
	api_request: Union[list, None]
) -> HttpResponse:
	TelegramBotCommand.objects.create(
		telegram_bot=telegram_bot,
		name=name,
		command=command,
		image=image,
		message_text=message_text,
		keyboard=keyboard,
		api_request=api_request
	)

	return HttpResponse('Вы успешно добавили команду Telegram боту.')

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_command_id
@constructor_telegram_bots.decorators.check_post_request_data_items(request_need_items=('name', 'command', 'message_text', 'keyboard', 'api_request',))
@telegram_bot.decorators.check_data_for_telegram_bot_command
def edit_telegram_bot_command(
	request: WSGIRequest,
	telegram_bot: TelegramBot,
	telegram_bot_command: TelegramBotCommand,
	name: str,
	command: Union[str, None],
	image: InMemoryUploadedFile,
	message_text: str,
	keyboard: Union[dict, None],
	api_request: Union[list, None]
) -> HttpResponse:
	telegram_bot_command.name = name
	telegram_bot_command.command = command

	if image != 'not_edited':
		telegram_bot_command.image.delete(save=False)
		telegram_bot_command.image = image

	telegram_bot_command.message_text = message_text

	telegram_bot_command_keyboard: TelegramBotCommandKeyboard = telegram_bot_command.get_keyboard()

	if keyboard is not None:
		if telegram_bot_command_keyboard is not None:
			telegram_bot_command_keyboard.type = keyboard['type']
			telegram_bot_command_keyboard.save()

			buttons_id = []
			
			for button in keyboard['buttons']:
				if button['id'] == '':
					button_: TelegramBotCommandKeyboardButton = TelegramBotCommandKeyboardButton.objects.create(
						telegram_bot_command_keyboard=telegram_bot_command_keyboard,
						text=button['text']
					)

					buttons_id.append(button_.id)
				else:
					is_finded_keyboard_button = False
					button_id = int(button['id'])

					for button_ in telegram_bot_command_keyboard.buttons.all():
						if button_id == button_.id:
							is_finded_keyboard_button = True
							break
					
					if is_finded_keyboard_button:
						button_: TelegramBotCommandKeyboardButton = telegram_bot_command_keyboard.buttons.get(id=button_id)
						button_.text = button['text']
						button_.save()

					buttons_id.append(button_id)

			for button in telegram_bot_command_keyboard.buttons.all():
				if button.id not in buttons_id:
					button.delete()
		else:
			TelegramBotCommandKeyboard.objects.create(
				telegram_bot_command=telegram_bot_command,
				type=keyboard['type'],
				buttons=keyboard['buttons']
			)
	else:
		if telegram_bot_command_keyboard is not None:
			telegram_bot_command_keyboard.delete()

	telegram_bot_command.api_request = api_request
	telegram_bot_command.save()

	return HttpResponse('Вы успешно изменили команду Telegram бота.')

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_command_id
def delete_telegram_bot_command(request: WSGIRequest, telegram_bot: TelegramBot, telegram_bot_command: TelegramBotCommand) -> HttpResponse:
	telegram_bot_command.delete()

	return HttpResponse('Вы успешно удалили команду Telegram бота.')


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_command_id
def get_telegram_bot_command_data(request: WSGIRequest, telegram_bot: TelegramBot, telegram_bot_command: TelegramBotCommand) -> HttpResponse:
	return HttpResponse(
		json.dumps(
			telegram_bot_command.to_dict()
		)
	)


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_command_id
@telegram_bot.decorators.check_telegram_bot_command_keyboard_button_id
@constructor_telegram_bots.decorators.check_post_request_data_items(request_need_items=('telegram_bot_command_id', 'start_diagram_connector', 'end_diagram_connector',))
def add_telegram_bot_command_keyboard_button_telegram_bot_command(
	request: WSGIRequest,
	telegram_bot: TelegramBot,
	telegram_bot_command: TelegramBotCommand,
	telegram_bot_command_keyboard_button: TelegramBotCommandKeyboardButton,
	start_diagram_connector: str,
	end_diagram_connector: str,
	telegram_bot_command_id: int,
) -> HttpResponse:
	if telegram_bot.commands.filter(id=telegram_bot_command_id).exists():
		telegram_bot_command_keyboard_button.telegram_bot_command = telegram_bot.commands.get(id=telegram_bot_command_id)
		telegram_bot_command_keyboard_button.start_diagram_connector = start_diagram_connector
		telegram_bot_command_keyboard_button.end_diagram_connector = end_diagram_connector
		telegram_bot_command_keyboard_button.save()

		return HttpResponse()
	else:
		return HttpResponseBadRequest('Команда Telegram бота не найдена!')


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_command_id
@telegram_bot.decorators.check_telegram_bot_command_keyboard_button_id
def delete_telegram_bot_command_keyboard_button_telegram_bot_command(
	request: WSGIRequest,
	telegram_bot: TelegramBot,
	telegram_bot_command: TelegramBotCommand,
	telegram_bot_command_keyboard_button: TelegramBotCommandKeyboardButton
) -> HttpResponse:
	telegram_bot_command_keyboard_button.telegram_bot_command = None
	telegram_bot_command_keyboard_button.start_diagram_connector = None
	telegram_bot_command_keyboard_button.end_diagram_connector = None
	telegram_bot_command_keyboard_button.save()

	return HttpResponse()


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_user_id
def add_allowed_user(request: WSGIRequest, telegram_bot: TelegramBot, telegram_bot_user: TelegramBotUser) -> HttpResponse:
	telegram_bot_user.is_allowed = True
	telegram_bot_user.save()

	return HttpResponse('Вы успешно добавили пользователя в список разрешённых пользователей Telegram бота.')

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_user_id
def delete_allowed_user(request: WSGIRequest, telegram_bot: TelegramBot, telegram_bot_user: TelegramBotUser) -> HttpResponse:
	telegram_bot_user.is_allowed = False
	telegram_bot_user.save()

	return HttpResponse('Вы успешно удалили пользователя из списка разрешённых пользователей Telegram бота.')

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_user_id
def delete_telegram_bot_user(request: WSGIRequest, telegram_bot: TelegramBot, telegram_bot_user: TelegramBotUser) -> HttpResponse:
	telegram_bot_user.delete()

	return HttpResponse('Вы успешно удалили пользователя Telegram бота.')


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@constructor_telegram_bots.decorators.check_post_request_data_items(request_need_items=('diagram_current_scale',))
def save_telegram_bot_diagram_current_scale(request: WSGIRequest, telegram_bot: TelegramBot, diagram_current_scale: float) -> HttpResponse:
	if 0.1 <= diagram_current_scale <= 2.0:
		telegram_bot.diagram_current_scale = diagram_current_scale
		telegram_bot.save()

		return HttpResponse()
	else:
		return HttpResponseBadRequest()

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
@telegram_bot.decorators.check_telegram_bot_command_id
@constructor_telegram_bots.decorators.check_post_request_data_items(request_need_items=('x', 'y',))
def save_telegram_bot_command_position(request: WSGIRequest, telegram_bot: TelegramBot, telegram_bot_command: TelegramBotCommand, x: int, y: int) -> HttpResponse:
	telegram_bot_command.x = x
	telegram_bot_command.y = y
	telegram_bot_command.save()
	
	return HttpResponse()


@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
def get_telegram_bot_commands(request: WSGIRequest, telegram_bot: TelegramBot) -> HttpResponse:
	return HttpResponse(
		json.dumps(
			telegram_bot.get_commands_as_dict()
		)
	)

@django.views.decorators.csrf.csrf_exempt
@django.contrib.auth.decorators.login_required
@telegram_bot.decorators.check_telegram_bot_id
def get_telegram_bot_users(request: WSGIRequest, telegram_bot: TelegramBot) -> HttpResponse:
	return HttpResponse(
		json.dumps(
			telegram_bot.get_users_as_dict()
		)
	)