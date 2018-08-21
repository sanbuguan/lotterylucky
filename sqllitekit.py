#!/usr/sbin/env python
# -*- coding: utf-8 -*-



import sqlite3


class Singleton(type):
    _inst = {}

    def __call__(self, *args, **kw):
        if self not in self._inst:
            self._inst[self] = super(Singleton, self).__call__(*args, **kw)
        return self._inst[self]



class sqllitekit(metaclass = Singleton):
    conn = None
    cursor = None

    def __init__(self,filename):

        self.conn=sqlite3.connect(filename)
        self.conn.row_factory=sqlite3.Row


    def exec_sql_cmd(self,sql_cmd):
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql_cmd)
        change_count=self.cursor.rowcount
        self.cursor.close()
        self.conn.commit()
        return change_count



    def get_data_cmd(self,sql_cmd):
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql_cmd)
        data_set = self.cursor.fetchall()
        self.cursor.close()
        return data_set



    def __del__(self):
        self.conn.close()




if __name__ == '__main__':
    aaa = sqllitekit('lotterYdata.db')
    #print(aaa.exec_sql_cmd("insert into raw_data (lottery_no,lottery_date,red1,red2,red3,red4,red5,red6,rawred1,rawred2,rawred3,rawred4,rawred5,rawred6,raw_red,blue,count1,money1,count2,money2,count3,money3,count4,money4,count5,money5,count6,money6,create_time,modify_time) values(2013004,2013-1-4,'1','2','3','4','5','6','1','2','3','4','5','6','aaaaaaa','32','1','2','3','4','5','6','7','8','9','10','11','12','2013-1-1 11:11:11','2013-1-1 11:11:11')"))
    #print(aaa.exec_sql_cmd("delete from raw_data where Findex=2 or Findex=3"))
    for item in aaa.get_data_cmd('select * from raw_data order by modify_time desc'):
        print(dict(item))







