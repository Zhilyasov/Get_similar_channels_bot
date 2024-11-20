from telethon import Button, TelegramClient, events
from telethon.tl.functions.channels import (
    GetChannelRecommendationsRequest,
)
import csv, os


# подставляем собственные значения
# bot
api_id = 20943952
api_hash = "87c18f57dc209acbf7117e359379795f"
bot_token = "7759371744:AAHvS4s5Fmn0HTcK2xckZqYRA3gP_WsBFmE"
phone = "+523461130639"
chanel_name = "myauuuuuun7"


# Алгоритмы работы бота
# Создание файла
def create_file(channels):
    FILENAME = "channels.csv"

    with open(FILENAME, "w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(channels)

# Создание экземпляра сессии
class Account:
    # Инициализация
    def __init__(
        self, name: str, id: int, hash: str, token: str = None, phone_number: str = None
    ):
        self.client = (
            TelegramClient(name, id, hash).start(phone_number)
            if token == None
            else TelegramClient(name, id, hash).start(bot_token=token)
        )

    # Запуск, добавление хэндлеров
    def run(self, account: TelegramClient):
        print("\nBot Starting!\n")

        # команда /start
        @self.client.on(events.NewMessage(pattern="/start"))
        async def start_hnd(event):
            sender = await event.get_sender()

            participants = await self.client.get_participants(f"@{chanel_name}")
            if event.sender_id not in [p.id for p in participants]:
                buttons = [
                    [Button.url("Перейти на канал", f"https://t.me/{chanel_name}")],
                    [Button.inline("Я подписан", b"i_am_subscribed")],
                ]
                # Отправляем сообщение с инлайн-клавиатурой
                await event.respond(
                    "Чтобы пользоваться ботом, пожалуйста, подпишитесь на телеграм-канал.",
                    buttons=buttons,
                )
            else:
                await event.respond(
                    "Привет 👋\nПришли мне **username** или ссылку телеграм-канала.\n\n☝️ Помни, что бот работает только с ОТКРЫТЫМИ каналами. В одном сообщении присылай только один канал."
                )

        # Обработчик нажатий на инлайн-кнопки
        @self.client.on(events.CallbackQuery)
        async def callback(event):
            if event.data == b"i_am_subscribed":
                # Здесь проверка, подписан ли пользователь на канал
                # с помощью метода get_participants
                participants = await self.client.get_participants(f"@{chanel_name}")
                if event.sender_id in [p.id for p in participants]:
                    await event.respond(
                        "Спасибо за подписку! Теперь можете отправить ссылку на канал."
                    )
                else:
                    await event.answer("Пожалуйста, подпишитесь на канал.", alert=True)

        # Обработчик любого входящего сообщения
        @self.client.on(events.NewMessage)
        async def send_channel_hnd(event):
            if event.text != "/start":
                participants = await self.client.get_participants(f"@{chanel_name}")
                if event.sender_id not in [p.id for p in participants]:
                    buttons = [
                        [Button.url("Перейти на канал", f"https://t.me/{chanel_name}")],
                        [Button.inline("Я подписан", b"i_am_subscribed")],
                    ]
                    # Отправляем сообщение с инлайн-клавиатурой
                    await event.respond(
                        "Чтобы пользоваться ботом, пожалуйста, подпишитесь на телеграм-канал.",
                        buttons=buttons,
                    )
                else:
                    try:
                        if event.text.startswith("https://t.me/"):
                            text = event.text[13:]
                        else:
                            text = event.text
                        recommendations = await account(
                            GetChannelRecommendationsRequest(text)
                        )

                        channels = []
                        channels_for_file = [
                            [
                                "link",
                                "created",
                                "id",
                                "username",
                                "title",
                                "verified",
                                "participants_count",
                            ]
                        ]
                        for recommendation in recommendations.chats:
                            # print(recommendation)
                            # print("\n\n")
                            # для текста
                            channels.append(
                                f"{recommendation.title} - t.me/{recommendation.username}"
                            )
                            # Для файла
                            channels_for_file.append(
                                [
                                    f"t.me/{recommendation.username}",
                                    f"{recommendation.date:%d.%m.%Y}",
                                    recommendation.id,
                                    recommendation.username,
                                    recommendation.title,
                                    recommendation.verified,
                                    recommendation.participants_count,
                                ]
                            )
                        await event.respond("\n".join(channels) if channels else "По этому каналу ничего не найдено!", link_preview=False)
                        if channels:
                            create_file(channels_for_file)

                            # Проверка существования файла перед отправкой
                            if os.path.exists("channels.csv"):
                                sender = await event.get_sender()
                                await self.client.send_file(sender, "channels.csv")
                            else:
                                await event.respond("Ошибка: файл не был создан.")

                    except Exception as e:
                        print(f"Error: {e}")
                        await event.reply("Неверные входные данные!")

        # Запуск асинхронно
        self.client.run_until_disconnected()

# Создание экземпляра бота
bot = Account("bot", api_id, api_hash, token=bot_token)
# Создание экземпляра аккаунта
account = TelegramClient("account", api_id, api_hash).start(phone)

bot.run(account)
