import ccxt
from threading import Thread
import time
from datetime import datetime
from abc import ABCMeta, abstractmethod
import dataset

class ExchangeWorker(Thread):

    """ExchangeWorker: individual connection with an exchange to retrieve data"""

    def __init__(self, exchange, symbols, symbol_freq, req_freq, data_type,
                 mutex, barrier, db_name, table_name):
        
        Thread.__init__(self)
        self.symbols = symbols
        self.symbol_freq = symbol_freq
        self.req_freq = req_freq
        client = getattr(ccxt, exchange.lower())()
        db = dataset.connect(db_name)
        table = db[table_name]
        if data_type.lower() == "candles":
            self.data = Candles(exchange, client, mutex, barrier, table)
        elif data_type.lower() == "orderbook":
            self.data = OrderBook(exchange, client, mutex, barrier, table)
        else:
            raise("Invalid data_type")
    
    def run(self):
        
        start_req_time = time.time()
        start_symbol_time = time.time()
        while True:
            
            if int(time.time()-start_symbol_time) > self.symbol_freq:

                start_symbol_time = time.time()
                for symbol in self.symbols:

                    while int(time.time()-start_req_time) <= self.req_freq:
                        pass

                    if int(time.time()-start_req_time) > self.req_freq:
                        self.require_data(symbol)

                        start_req_time = time.time()       

    def require_data(self,symbol):
        self.data.request(symbol)

class Data(object):

    """Data: Generic class to request data from exchanges"""

    __metaclass__ = ABCMeta

    def __init__(self, exchange, client, mutex, barrier, table):
        self.exchange = exchange
        self.client = client
        self.mutex = mutex
        self.barrier = barrier
        self.table = table

    @abstractmethod
    def request(self, symbol):
        pass
    
    def store(self, data):
        self.mutex.acquire()
        self.table.insert(data)
        self.mutex.release()        

class Candles(Data):

    """Candles: A class to request candles data from exchange"""

    def request(self, symbol):
        self.barrier.wait()
        try:
            candles = self.client.fetch_ohlcv(symbol, "1m")
            dummy = 0
            data = {"datetime": dummy,
                    "symbol": symbol,
                    "exchange": self.exchange,
                    "open": dummy,
                    "high": dummy,
                    "low": dummy,
                    "close": dummy,
                    "volume": dummy}
            self.store(data)
        except:
            # print("symbol: "+symbol+" not listed or request limit reached in: "+self.exchange)
            pass



class OrderBook(Data):

    """OrderBook: A class to request orderbook data from exchange"""

    def request(self, symbol):
        self.barrier.wait()
        try:
            book = self.client.fetch_order_book(symbol)
            data = {"datetime": book['datetime'],
                    "symbol":symbol,
                    "exchange":self.exchange,
                    "bid":book['bids'][0][0],
                    "ask":book['asks'][0][0]}
            self.store(data)
        except:
            # print("symbol: "+symbol+" not listed or request limit reached in: "+self.exchange)
            pass
