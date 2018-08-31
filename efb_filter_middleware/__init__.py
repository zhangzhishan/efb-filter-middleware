# coding=utf-8

import os
import pickle
import logging
import uuid
from typing import Optional, Dict, Tuple

from ehforwarderbot import EFBMiddleware, EFBMsg, utils, MsgType, EFBChat, ChatType, coordinator
from ehforwarderbot.exceptions import EFBException
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
            config = yaml.load(open(config_path, encoding ="UTF-8"))
            self.config_version = 0
            self.match_mode = config.get("match_mode") # fuzz and exact
            if self.match_mode is None:
                self.match_mode = "fuzz"



        self.chat = EFBChat()
        self.chat.channel_name = self.middleware_name
        self.chat.channel_id = self.middleware_id
        self.chat.channel_emoji = "📜"
        self.chat.chat_uid = "__zhangzhishan.filter__"
        self.chat.chat_name = self.middleware_name
        self.chat.chat_type = ChatType.System

        self.logger = logging.getLogger("zhangzhishan.filter")
        hdlr = logging.FileHandler('./zhangzhishan.filter.log', encoding ="UTF-8")
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.DEBUG)

    def process_message(self, message: EFBMsg) -> Optional[EFBMsg]:
        config = yaml.load(open(utils.get_config_path(self.middleware_id), encoding ="UTF-8"))
        if message.author.is_self:
            return message
        if self.config_version != config.get('version'):
            self.logger.debug("config changed!")
            self.config_version = config.get('version')
            self.work_modes = config.get('work_mode')
        for work_mode in WorkMode:
            # print(self.work_modes)
            # print(work_mode.value)
            if work_mode.value in self.work_modes:
                # print(config.get(work_mode.value))
                if config.get(work_mode.value) and self.is_keep_message(work_mode, message, config.get(work_mode.value)):
                    return message

    def black_match(self, from_, from_alias, configs):
        if self.match_mode == "fuzz":
            for config in configs:
                if from_ in config or from_alias in config:
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
                if from_ in config or from_alias in config:
                    return True
            return False
        else:                    
            if from_ in configs or from_alias in configs:
                return True
            else:
                return False

    def is_keep_message(self, work_mode: WorkMode, message: EFBMsg, configs: list) -> bool:
        self.logger.debug("message author type:%s", message.author.chat_type)
        self.logger.debug("message chat type:%s", message.chat.chat_type)
        self.logger.debug("message is_mp type:%s", message.chat.vendor_specific['is_mp'])
        # self.logger.debug("Received message from person: %s--%s", from_person, from_alias)
        self.logger.debug("Received message from myself: %s", message.author.is_self)
        self.logger.debug("Received message from chat: %s--%s", message.chat.chat_alias, message.chat.chat_name)
        
        if message.chat.chat_type.value == "Group":
            self.logger.debug("Received message from group: %s--%s", message.author.group.chat_alias, message.author.group.chat_name)
            from_ = message.author.group.chat_name
            from_alias = message.author.group.chat_alias
            if from_alias is None:
                from_alias = from_
            if work_mode is WorkMode.black_group:
                return self.black_match(from_, from_alias, configs)
            if work_mode is WorkMode.white_group:
                return self.white_match(from_, from_alias, configs)
        else:
            from_ = message.author.chat_name
            from_alias = message.author.chat_alias
            if from_alias is None:
                from_alias = from_
            if message.chat.vendor_specific is not None and message.chat.vendor_specific['is_mp']:
                if work_mode is WorkMode.black_public:
                    return self.black_match(from_, from_alias, configs)
                if work_mode is WorkMode.white_public:
                    return self.white_match(from_, from_alias, configs)
            else:                
                if work_mode is WorkMode.black_person:
                    return self.black_match(from_, from_alias, configs)
                if work_mode is WorkMode.white_person:
                    return self.white_match(from_, from_alias, configs)
           
            



        #             self.white_persons = config.get('white_persons')
        #     self.white_groups = config.get('white_groups')
        # if message.author.group:
            
        #     self.logger.debug("Received message from group: %s", from_group)
        #     for whitechat in self.white_groups:
        #         # self.logger.debug("whitechat: %s", whitechat)
        #         if whitechat in from_group:
        #             return message

        
        # for whitechat in self.white_persons:
        #     from_person = 
            
        #     # self.logger.debug("whitechat: %s", whitechat)
        #     if whitechat in from_person:
        #         return message
        # # if not message.type == MsgType.Text:
        # #     return message
        # # self.logger.debug("[%s] is a text message.", message.uid)
        

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
