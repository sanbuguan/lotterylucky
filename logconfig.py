#!/usr/sbin/env python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import  RotatingFileHandler




# 日志的打印配置
# CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [line:%(lineno)-5d] %(levelname)s -> %(message)s',
                    datefmt='%a , %Y-%m-%d %H:%M:%S'
                    )

#定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
Rthandler = RotatingFileHandler('myapp.log', maxBytes=10*1024*1024,backupCount=1,encoding='utf-8')
Rthandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [line:%(lineno)-5d] %(levelname)s -> %(message)s')
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)
