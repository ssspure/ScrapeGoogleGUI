import sqlite3
import os


class ManageDB():
    def __init__(self, dbFile):
        # dbFile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), dbFile)
        self.database = sqlite3.connect(dbFile)
        self.conn = self.database.cursor()

    def createTable(self):
        # 创建info表
        sql = '''CREATE TABLE info
        (id INTEGER PRIMARY KEY autoincrement,
         name TEXT NOT NULL,
         value TEXT NOT NULL 
        );
        '''
        self.conn.execute(sql)
        self.conn.close()


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


if __name__ == "__main__":

    def getInfoTableData():
        datas = {}

        datas["products"] = "towel,dog"
        datas["rating"] = "4.3"
        datas["googleUrl"] = "https://www.google.com.tw"
        datas["amazonUrl"] = "amazon.com"
        datas["interval"] = "20"
        datas["resultFilePath"] = "/Users/ssspure/result"

        return datas

    manageDB = ManageDB()

    # manageDB.createTable()
    manageDB.insertToInfo(getInfoTableData())
    # datas = manageDB.selectFromInfo()

    # for data in datas:
    #     print("name:"+data[0] + ",value:"+data[1])

    manageDB.close()

