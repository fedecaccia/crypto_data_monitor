import numpy as np
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
        self.client = getattr(ccxt, exchange.lower())()
        db = dataset.connect(db_name)
        if data_type.lower() == "candles":
            self.data = Candles(exchange, self.client, mutex, barrier, db, table_name)
        elif data_type.lower() == "orderbook":
            self.data = OrderBook(exchange, self.client, mutex, barrier, db, table_name)
        else:
            raise("Invalid data_type")
    
    def run(self):
        
        # start_symbol_time = time.time()
        while True:
            
            # if int(time.time()-start_symbol_time) > self.symbol_freq:

            #     start_symbol_time = time.time()
            for symbol in self.symbols:

                # while int(time.time()-start_req_time) <= self.req_freq:
                start_req_time = time.time()
                while int(time.time()-start_req_time) <= self.client.rateLimit/1000:
                    pass
                self.require_data(symbol)
                

    def require_data(self,symbol):
        self.data.request(symbol)


class Data(object):

    """Data: Generic class to request data from exchanges.
    """

    __metaclass__ = ABCMeta

    def __init__(self, exchange, client, mutex, barrier, db, table_name):
        self.exchange = exchange
        self.client = client
        self.mutex = mutex
        self.barrier = barrier
        self.db = db
        self.table_name = table_name

    @abstractmethod
    def request(self, symbol):
        pass
    
    def store(self, symbol, data):
        self.mutex.acquire()
        self.db[self.table_name+symbol.replace("/", "")+self.exchange].insert(data)
        self.mutex.release()


class Candles(Data):

    """Candles: A class to request candles data from exchange.
    Runs all time because different exchanges returns more or less candles.
    This way, we standarize the request.
    """

    def __init__(self, exchange, client, mutex, barrier, db, table_name):
        super(Candles, self).__init__(exchange, client, mutex, barrier, db, table_name)
        self.last_datetime = 0

    def request(self, symbol):
        self.barrier.wait()
        try:
            n_candles = 10
            candles = self.client.fetch_ohlcv(symbol=symbol, 
                                              timeframe="1m",
                                              since=self.client.milliseconds()-n_candles*60*1000, 
                                              limit=n_candles)
            candles = np.array(candles)
            
            # discard last candle: yet incomplete
            candles = np.delete(candles, -1, 0)
            
            # remove old values
            for time in candles.transpose()[0]:
                if time <= self.last_datetime:
                    candles = np.delete(candles, 0, 0)
                       
            # if new values
            if len(candles)>0:

                # update last datetime
                self.last_datetime = candles[-1][0]
                
                for candle in candles:
                    data = {"datetime": candle[0],
                            # "symbol": symbol,
                            # "exchange": self.exchange,
                            "open":candle[1],
                            "high":candle[2],
                            "low":candle[3],
                            "close":candle[4],
                            "volume":candle[5]}
                    # store                
                    self.store(symbol, data)
        except:
            # print("symbol: "+symbol+" not listed or request limit reached in: "+self.exchange)
            pass

class OrderBook(Data):

    """OrderBook: A class to request orderbook data from exchange"""

    def request(self, symbol):
        self.barrier.wait()
        try:
            book = self.client.fetch_order_book(symbol)
            bid_weight_val_1, bid_weight_count_1 = self.weighted_orders(book['bids'], limit=5)
            bid_weight_val_2, bid_weight_count_2 = self.weighted_orders(book['bids'], limit=5)
            ask_weight_val_1, ask_weight_count_1 = self.weighted_orders(book['asks'], limit=10)
            ask_weight_val_2, ask_weight_count_2 = self.weighted_orders(book['asks'], limit=10)
            data = {"datetime": book['datetime'],
                    # "symbol":symbol,
                    # "exchange":self.exchange,
                    "bid_weight_val_1":bid_weight_val_1,
                    "bid_weight_count_1":bid_weight_count_1,
                    "bid_weight_val_2":bid_weight_val_2,
                    "bid_weight_count_2":bid_weight_count_2,
                    "bid_val_2":book['bids'][2][0],
                    "bid_count_2":book['bids'][2][1],                    
                    "bid_val_1":book['bids'][1][0],
                    "bid_count_1":book['bids'][1][1],
                    "bid_val_0":book['bids'][0][0],
                    "bid_count_0":book['bids'][0][1],
                    "ask_val_0":book['asks'][0][0],
                    "ask_count_0":book['asks'][0][1],
                    "ask_val_1":book['asks'][1][0],
                    "ask_count_1":book['asks'][1][1],
                    "ask_val_2":book['asks'][2][0],
                    "ask_count_2":book['asks'][2][1], 
                    "ask_weight_val_1":ask_weight_val_1, 
                    "ask_weight_count_1":ask_weight_count_1, 
                    "ask_weight_val_2":ask_weight_val_2, 
                    "ask_weight_count_2":ask_weight_count_2}
            self.store(symbol, data)
        except:
            # print("symbol: "+symbol+" not listed or request limit reached in: "+self.exchange)
            pass

    def weighted_orders(self, book, limit):
        
        weighted_value = 0
        count = 0

        for i_order, order in enumerate(book, 0):
            if i_order<limit:              
                weighted_value += order[0]*order[1]
                count += order[1]
            else:
                break

        weighted_value /= count

        return weighted_value, count
                


""" 
# How to read datetime s [milliseconds]
import datetime
datetime.datetime.fromtimestamp(s/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
# with an array:
time = datetime.apply(lambda x: datetime.fromtimestamp(x/1000.0))
"""