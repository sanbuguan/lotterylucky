#!/usr/sbin/env python
# -*- coding: utf-8 -*-

import configparser
import json
import re
import time

import requests

from  logconfig import *
from sqllitekit import sqllitekit


DB_NAME='lotterydata.db'
headers={}
headers['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38'
headers['X-Requested-With'] =  'XMLHttpRequest'
headers['Referer'] = 'http://www.cwl.gov.cn/kjxx/ssq/'

get_raw_data_url="http://www.cwl.gov.cn/cwl_admin/kjxx/findKjxx/forIssue?name=ssq&code=%s"
get_orignal_red_url='http://www.cwl.gov.cn'

class lucky_lottery():

        lucky_lottery_no=''
        req=None
        datail_url=''
        raw_data_dict={}

        #初始化彩票的期号
        def __init__(self,lucky_lottery_no):
            self.lucky_lottery_no = lucky_lottery_no



        #根据id进行json数据的获取
        def get_data_from_id(self):
            logging.info(get_raw_data_url % (self.lucky_lottery_no));
            req = requests.get(get_raw_data_url % (self.lucky_lottery_no), headers=headers)
            result_json = json.loads(req.text)
            logging.info(result_json)

            #成功的查询到了需要的数据
            if result_json['state'] == 0:
                self.raw_data_dict['lottery_no'] = self.lucky_lottery_no
                self.datail_url=get_orignal_red_url+result_json['result'][0]['detailsLink']
                self.get_data_from_json(result_json)
                self.insert_update_lucky_data(self.raw_data_dict)
                
            else:
                logging.error('%s get data detail url fail....'%(self.lucky_lottery_no))
                self.raw_data_dict['lottery_no']=self.lucky_lottery_no
                self.raw_data_dict['Fok']='2'
                self.insert_update_lucky_data(self.raw_data_dict)


        #插入数据或者插入数据
        def insert_update_lucky_data(self,insert_data):
            sql_manager = sqllitekit(DB_NAME)
            sql_cmd="SELECT * FROM raw_data WHERE lottery_no='%s'"%(insert_data['lottery_no'])
            ret=sql_manager.get_data_cmd(sql_cmd)
            if len(ret) > 0 :
                #这里进行insert操作

                if str(ret[0]['Fok']) == '2':
                    logging.info('Data already exist,but need repair....')
                    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    self.raw_data_dict['modify_time'] = time_now
                    self.raw_data_dict['Fok']='0'
                    logging.info(insert_data)

                    sql_cmd='UPDATE raw_data SET '
                    for key in self.raw_data_dict:
                        sql_cmd=sql_cmd + " %s = '%s',"%(key,self.raw_data_dict[key])
                    sql_cmd=sql_cmd[:-1]
                    sql_cmd=sql_cmd+" WHERE lottery_no = '%s' " %(self.lucky_lottery_no)
                    logging.info(sql_cmd)
                    sql_ret=sql_manager.exec_sql_cmd(sql_cmd)
                    logging.info('SQL exec ret : %s'%(sql_ret))


                else:
                    logging.info('Data is ok,not need to update.....')
            else:
                logging.info('Data not exist, will insert data')
                time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                self.raw_data_dict['create_time'] = time_now
                self.raw_data_dict['modify_time'] = time_now
                self.raw_data_dict['Fok'] = '0'
                logging.info(self.raw_data_dict)

                sql_cmd = 'INSERT INTO raw_data '
                sql_cmd_key=''
                sql_cmd_value=''
                for key in self.raw_data_dict:
                    sql_cmd_key = sql_cmd_key + " %s," % (key)
                    sql_cmd_value =  sql_cmd_value + " '%s'," % (self.raw_data_dict[key])
                sql_cmd = sql_cmd + "(%s) VALUES (%s) "%( sql_cmd_key[:-1] , sql_cmd_value[:-1] )
                logging.info(sql_cmd)
                sql_ret = sql_manager.exec_sql_cmd(sql_cmd)
                logging.info('SQL exec ret : %s' % (sql_ret))


        def get_data_from_json(self,ret_json):
            self.raw_data_dict['lottery_date']=ret_json['result'][0]['date']
            red_balls=ret_json['result'][0]['red'].split(',')
            red_balls.sort()
            self.raw_data_dict['red1'] =red_balls[0]
            self.raw_data_dict['red2'] =red_balls[1]
            self.raw_data_dict['red3'] =red_balls[2]
            self.raw_data_dict['red4'] =red_balls[3]
            self.raw_data_dict['red5'] =red_balls[4]
            self.raw_data_dict['red6'] =red_balls[5]

            self.raw_data_dict['raw_red']=ret_json['result'][0]['red'].replace(',','-')

            #是否需要真实原始的红球顺序，需要一次网络请求
            self.raw_data_dict['raw_red']=self.get_raw_red_balls()

            self.raw_data_dict['blue']=ret_json['result'][0]['blue']
            self.raw_data_dict['count1'] = ret_json['result'][0]['prizegrades'][0]['typenum']
            self.raw_data_dict['money1'] = ret_json['result'][0]['prizegrades'][0]['typemoney']
            self.raw_data_dict['count2'] = ret_json['result'][0]['prizegrades'][1]['typenum']
            self.raw_data_dict['money2'] = ret_json['result'][0]['prizegrades'][1]['typemoney']
            self.raw_data_dict['count3'] = ret_json['result'][0]['prizegrades'][2]['typenum']
            self.raw_data_dict['money3'] = ret_json['result'][0]['prizegrades'][2]['typemoney']
            self.raw_data_dict['count4'] = ret_json['result'][0]['prizegrades'][3]['typenum']
            self.raw_data_dict['money4'] = ret_json['result'][0]['prizegrades'][3]['typemoney']
            self.raw_data_dict['count5'] = ret_json['result'][0]['prizegrades'][4]['typenum']
            self.raw_data_dict['money5'] = ret_json['result'][0]['prizegrades'][4]['typemoney']
            self.raw_data_dict['count6'] = ret_json['result'][0]['prizegrades'][5]['typenum']
            self.raw_data_dict['money6'] = ret_json['result'][0]['prizegrades'][5]['typemoney']

            self.raw_data_dict['html']=self.datail_url



        def get_raw_red_balls(self):
            logging.info(self.datail_url)
            req = requests.get(self.datail_url, headers=headers)
            req.encoding = 'utf-8'
            reg_str = 'var khHq = \[(\S+)\];'
            return re.findall(reg_str, req.text)[0].replace('"','').replace(',','-')

            



if __name__ == '__main__':

        #先进行数据的修改
        sql_manager = sqllitekit(DB_NAME)
        sql_cmd = "SELECT * FROM raw_data WHERE Fok = '2'"
        ret = sql_manager.get_data_cmd(sql_cmd)
        if len(ret) > 0:
            for item in ret:
                logging.info("will repair data ----> %s"%(item['lottery_no']))
                composer = lucky_lottery('%s' % (item['lottery_no']))
                logging.info('start------> %s' % (item['lottery_no']))
                composer.get_data_from_id()
                logging.info('end--------> %s' % (item['lottery_no']))

        else:
            logging.info('No data is need repair.......')


        #在进行新数据的拉取
        lucky_start=2018090
        lucky_end=2018096
        logging.info('get lottery data from %s - %s'%(lucky_start,lucky_end))
        for item in range(lucky_start,lucky_end+1):

            composer=lucky_lottery('%s'%(item))
            logging.info('start------> %s'%(item))

            composer.get_data_from_id()

            logging.info('end--------> %s' % (item))



