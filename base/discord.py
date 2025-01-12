from discord import SyncWebhook
from base.config_reader import Config
from base.enums import Discord

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT, 'config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'discord.json')

class DiscordConnector(object):
    def __init__(self):
        self.config = Config(CONFIG_PATH)[Discord.WEBHOOK]
        
    def send_message(self, channel, message):
        webhook = SyncWebhook.from_url(self.config[channel])
        webhook.send(message)
