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
    match_mode: fuzz
    work_mode:
        - black_persons
        - white_groups
        - white_publics


    white_publics:
        - 银行
    
    black_persons:
        - enemy

    white_persons:
        - john
        - jack
        - You
        - 李白

    white_groups:
        - family

``version`` is used to monitor configuration change in runtime, it must be changed when changing the configuration. It is a ``float`` number.

There are six different ``work_mode``:

- black_persons
- white_persons
- black_publics
- white_publics
- black_groups
- white_groups

``white_persons`` means the persons you want to receive messages from, ``white_groups`` means groups you want to receive from, ``white_publics`` means subscription account you want to receive from.

There are two matching mode:

- ``fuzz`` This match pattern is a substring matching, which means if you have ``jack`` in your ``white_persons`` setting, ``jackson`` is also matched.
- ``exact`` This match pattern only matches when the whole word is the same. 

Notice
-----------------

- Case sensitive
- All messages from you will be forwarded.

TODO
-----

