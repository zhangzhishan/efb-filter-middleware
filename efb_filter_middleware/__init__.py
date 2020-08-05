# coding=utf-8

import os
import pickle
import logging
import uuid
from typing import Optional, Dict, Tuple

from ehforwarderbot import Middleware, Message, utils, MsgType, Chat, coordinator
from ehforwarderbot.exceptions import EFBException
from ehforwarderbot.chat import GroupChat, SelfChatMember
import yaml

from enum import Enum

from .__version__ import __version__ as version

class WorkMode(Enum):
    black_person = "black_persons"
    white_person = "white_persons"
    black_public = "black_publics"
    white_public = "white_publics"
    black_group = "black_groups"
    white_group = "white_groups"


class FilterMiddleware(Middleware):
    middleware_id: str = "zhangzhishan.filter"
    middleware_name: str = "Filter Middleware"
    __version__: str = version

    mappings: Dict[Tuple[str, str], str] = {}
    chat: Chat = None


    def __init__(self, instance_id: str = None):
        super().__init__(instance_id)

        storage_path = utils.get_data_path(self.middleware_id)
        config_path = utils.get_config_path(self.middleware_id)
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        if not os.path.exists(config_path):
            raise EFBException("Filter middleware is not configured.")
        else:
            config = yaml.load(open(config_path, encoding ="UTF-8"))
            self.config_version = 0
            self.match_mode = config.get("match_mode") # fuzz and exact
            if self.match_mode is None:
                self.match_mode = "fuzz"

        self.logger = logging.getLogger("zhangzhishan.filter")
        hdlr = logging.FileHandler('./zhangzhishan.filter.log', encoding ="UTF-8")
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.ERROR)

    def process_message(self, message: Message) -> Optional[Message]:
        config = yaml.full_load(open(utils.get_config_path(self.middleware_id), encoding ="UTF-8"))
        if isinstance(message.author, SelfChatMember):
            return message
        if self.config_version != config.get('version'):
            self.logger.debug("config changed!")
            self.config_version = config.get('version')
            self.work_modes = config.get('work_mode')
        for work_mode in WorkMode:
            if work_mode.value in self.work_modes:
                if config.get(work_mode.value) and self.is_keep_message(work_mode, message, config.get(work_mode.value)):
                    return message

    def black_match(self, from_, from_alias, configs):
        if self.match_mode == "fuzz":
            for config in configs:
                if config in from_ or config in from_alias:
                    return False
            return True
            
        else:     
            if from_ in configs or from_alias in configs:
                return False
            else:
                return True
            

    def white_match(self, from_, from_alias, configs):
        if self.match_mode == "fuzz": 
            for config in configs:
                if config in from_ or config in from_alias:
                    return True
            return False
        else:          
            if from_ in configs or from_alias in configs:
                return True
            else:
                return False

    def is_keep_message(self, work_mode: WorkMode, message: Message, configs: list) -> bool:
        self.logger.debug("message is_mp type:%s", message.chat.vendor_specific['is_mp'])
        self.logger.debug("Received message from chat: %s--%s", message.chat.alias, message.chat.name)
        self.logger.debug("match_mode: %s", self.match_mode)
        from_ = message.author.name
        from_alias = message.author.alias
        if from_alias is None:
            from_alias = from_
        chat_name = message.chat.name
        chat_alias = message.chat.alias
        if chat_alias is None:
            chat_alias = chat_name
        self.logger.debug("Received message from : %s--%s", from_, from_alias)
        if isinstance(message.chat, GroupChat):
            self.logger.debug("Receive group chat")
            if work_mode is WorkMode.black_group:
                return self.black_match(chat_name, chat_alias, configs)
            if work_mode is WorkMode.white_group:
                return self.white_match(chat_name, chat_alias, configs)
        else:
            if message.chat.vendor_specific is not None and message.chat.vendor_specific['is_mp']:
                if work_mode is WorkMode.black_public:
                    self.logger.debug("Receive black public")
                    return self.black_match(from_, from_alias, configs)
                if work_mode is WorkMode.white_public:
                    return self.white_match(from_, from_alias, configs)
            else:                
                if work_mode is WorkMode.black_person:
                    self.logger.debug("Receive black person")
                    return self.black_match(from_, from_alias, configs)
                if work_mode is WorkMode.white_person:
                    return self.white_match(from_, from_alias, configs)
