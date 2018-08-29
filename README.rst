A filter middleware for EFB
==============
A filter middleware for EFB can help you only receive messages from persons and groups you want.

Install
-----------------
install using pip3::
    
    pip3 install git+https://github.com/zhangzhishan/efb-filter-middleware

Configuration
-----------------
config files is located in ``~\.ehforwarderbot\profiles\default\zhangzhishan.filter\config.yaml``, a sample config files::

    version: 0.1
    white_persons:
        - john
        - jack
        - You
        - 李白

    white_groups:
        - family
    
``white_persons`` means the persons you want to receive messages from, and ``white_groups`` means groups you want to receive from.

The match pattern is a substring matching, which means if you have ``jack`` in your ``white_persons`` setting, ``jackson`` is also matched.

``version`` is used to monitor configuration change in runtime, it must be changed when changing the configuration.

Notice
-----------------

- Case sensitive
- You should be included to receive your sending messages.

TODO
-----

- different work mode: blacklist, whitelist and so on.