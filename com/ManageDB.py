import sqlite3
import os


class ManageDB():
    def __init__(self, dbFile):
        self.database = sqlite3.connect(dbFile)
        self.conn = self.database.cursor()

        sql = "select count(*)  from sqlite_master where type='table' and name = 'info';"

        cursor = self.conn.execute(sql)

        tblCnt = cursor.fetchall()[0][0]

        if tblCnt == 0:
            datas = {}

            # 创建初始化数据
            datas["products"] = "towel,pest repeller"
            datas["rating"] = "4.3"
            datas["googleUrl"] = "https://www.google.com"
            datas["amazonUrl"] = "amazon.com"
            datas["interval"] = "20"
            datas["resultFilePath"] = r"C:\coding"
            self.createTable()
            self.insertToInfo(datas)

    def createTable(self):
        # 创建info表
        sql = '''CREATE TABLE info
        (id INTEGER PRIMARY KEY autoincrement,
         name TEXT NOT NULL,
         value TEXT NOT NULL 
        );
        '''
        self.conn.execute(sql)


    def insertToInfo(self, datas):
        for name, value in datas.items():
            sql = '''
                INSERT INTO info VALUES (NULL, "{}", "{}")
            '''.format(name, value)
            self.conn.execute(sql)
            self.database.commit()

    def updateInfo(self, datas):
        for name, value in datas.items():
            sql = '''
                UPDATE info set value="{}" where name = "{}";
            '''.format(value, name)
            self.conn.execute(sql)
            self.database.commit()

    def close(self):
        self.conn.close()


    def selectFromInfo(self):
        datas = {}
        sql = "select name,value from info"
        cursor = self.conn.execute(sql)

        for data in cursor:
            datas[data[0]] = data[1]

        return datas