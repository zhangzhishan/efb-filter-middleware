# coding=utf-8

import os
import pickle
import logging
import uuid
from typing import Optional, Dict, Tuple

from ehforwarderbot import EFBMiddleware, EFBMsg, utils, MsgType, EFBChat, ChatType, coordinator
from ehforwarderbot.exceptions import EFBException
import yaml

from .__version__ import __version__ as version


class FilterMiddleware(EFBMiddleware):
    middleware_id: str = "zhangzhishan.filter"
    middleware_name: str = "Filter Middleware"
    __version__: str = version

    mappings: Dict[Tuple[str, str], str] = {}
    chat: EFBChat = None


    def __init__(self, instance_id: str = None):
        super().__init__(instance_id)

        storage_path = utils.get_data_path(self.middleware_id)
        config_path = utils.get_config_path(self.middleware_id)
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        if not os.path.exists(config_path):
            raise EFBException("Filter middleware is not configured.")
        else:
            config = yaml.load(open(config_path))
            self.whitelist = config.get('whitelist')


        self.chat = EFBChat()
        self.chat.channel_name = self.middleware_name
        self.chat.channel_id = self.middleware_id
        self.chat.channel_emoji = "📜"
        self.chat.chat_uid = "__zhangzhishan.filter__"
        self.chat.chat_name = self.middleware_name
        self.chat.chat_type = ChatType.System

        self.logger = logging.getLogger("zhangzhishan.filter")
        hdlr = logging.FileHandler('./zhangzhishan.filter.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.DEBUG)

    def process_message(self, message: EFBMsg) -> Optional[EFBMsg]:
        self.logger.debug("Received message: %s", message.author.chat_name)
        for whitechat in self.whitelist:
            if whitechat in message.author.chat_name:
                return message
        # if not message.type == MsgType.Text:
        #     return message
        # self.logger.debug("[%s] is a text message.", message.uid)
        

    def reply_message(self, message: EFBMsg, text: str):
        reply = EFBMsg()
        reply.text = text
        reply.chat = coordinator.slaves[message.chat.channel_id].get_chat(message.chat.chat_uid)
        reply.author = self.chat
        reply.type = MsgType.Text
        reply.deliver_to = coordinator.master
        reply.target = message
        reply.uid = str(uuid.uuid4())
        coordinator.send_message(reply)
