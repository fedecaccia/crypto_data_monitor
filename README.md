# Crypto data monitor
This program aims to be a helpful tool to download online market data from different exchagnes.

## Main features

- It uses [ccxt](https://www.github.com/ccxt/ccxt) library to connect with different exchanges (more than 100).
- Programmed in a multi-threading scheme. All threads request data synchronously so you can retrieve data with precision to the second and analyze arbitrage and other posibilities.
- Data is stored in sql data bases.

## Quickstart
Crypto data monitor currently can be executed in two modes:

- ```orderbook``` mode: requests *bid*/*ask* values from symbols and exchanges configured in settings.
- ```candes``` mode: requests *open*/*high*/*low*/*close*/*volume* values from symbols and exchanges configured in settings.

First, install dependencies. Positioned in the crypto data monitor directory, type:
```bash
pip3 install -r requirements.txt
```
You can modify `requetiments.txt` in to avoid installing `dataset` (in case you use SQLite databases) or `pymongo` (in case you use NoSQL databases). In case you choose to use NoSQL [MongoDB](https://www.mongodb.com/) databases, you should also install mongodb-server:
```bash
sudo apt install mongodb-server
```
Once dependencies have been insalled, if you are using MongoDB start service:
```bash
sudo service mongodb start
```
You can also start service typing:
```bash
sh mongo_start.sh
```
Then run crypto data monitor in your preferred mode:
```bash
python3 monitor.py <data_type>
```
where *<data_type>* should be replaced by ```orderbook``` or ```candles```.
and the program will start downloading data in sql data bases located at ```/orderbook``` or ```/candles```.

Using MongoDB databases, to reinit databases use the following script:
```bash
sudo service mongodb restart
```