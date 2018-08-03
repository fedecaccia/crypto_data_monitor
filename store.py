from abc import ABCMeta, abstractmethod
import dataset # sql
import csv # csv
import pymongo # nosql

class Store(object):

    """Store: Abstract class to store data in csv, sql or nosql data bases."""

    __metaclass__=ABCMeta

    def __init__(self):
        pass
    
    @abstractmethod
    def insert(self, item):
        pass


class CsvStore(Store):

    """CsvStore: Class to store value in csv format."""

    def __init__(self, route, table_prefix):
        super(Store, self).__init__()
        self.route = route
        self.table_prefix = table_prefix
        self.headers = set()

    def insert(self, exchange, symbol, item):
        string_file = self.route+self.table_prefix+exchange+symbol.replace("/", "")+'.csv'
        with open(string_file, 'a') as csvfile:            
            writer = csv.DictWriter(csvfile, fieldnames=item.keys())
            if string_file not in self.headers:
                writer.writeheader()
                self.headers.add(string_file)
            writer.writerow(item)

    def order_cols(self):
        pass
        

class SqlStore(Store):

    """SqlStore: Class to store value in SQL format."""

    def __init__(self, route, table_prefix):
        super(Store, self).__init__()
        self.db = dataset.connect(route)
        self.table_prefix = table_prefix

    def insert(self, exchange, symbol, item):
        self.db[self.table_prefix+symbol.replace("/", "")+exchange.lower()].insert(item)


class NoSqlStore(Store):

    """NoSqlStore: Class to store value in NoSQL (mongoDB) format."""

    def __init__(self, table_prefix):
        super(Store, self).__init__()
        myclient = pymongo.MongoClient()
        self.mydb = myclient[table_prefix]

    def insert(self, exchange, symbol, item):
        col = self.mydb[symbol.replace("/", "")+exchange.lower()]
        col.insert_one(item)