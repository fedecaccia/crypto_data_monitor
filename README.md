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
Once dependencies have been insalled, run crypto data monitor in your preferred mode:
```bash
python3 monitor.py <data_type>
```
where *<data_type>* should be replaced by ```orderbook``` or ```candles```.
and the program will start downloading data in sql data bases located at ```/orderbook``` or ```/candles```.