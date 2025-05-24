# bybit wallet 06.10.2024
import sys, os, json, requests
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QDateEdit, QHBoxLayout, QVBoxLayout, QApplication, QComboBox, QLabel, QMenuBar, QMenu, QAction, QStatusBar, QWidget, QFrame, QLineEdit, QPushButton, QDialog, QFormLayout
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5 import QtGui
from pybit.unified_trading import HTTP
from datetime import datetime

from assets.scripts.Chart import CandlestickChart

API_FILE_PATH="assets/api_keys.json"
ICON_PATH = 'assets/ico.png'

screen_width=0
screen_height=0

coin="USDT"

class ByBitWallet(QMainWindow):
    def __init__(self):
        super().__init__()
        screen_rect = QDesktopWidget().screenGeometry()
        global screen_width, screen_height
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()
        self.setGeometry(screen_width//2-300, screen_height//2-200, 600, 400)
        self.setWindowTitle("ByBitWallet")
        self.setStyleSheet("background-color: #0b1619;")      
        self.central_widget = QWidget(self)
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(10)

        self.balance_label = QLabel("Balance: Loading...", self)
        self.balance_label.setStyleSheet("color: white; font-size: 18px;")
        self.balance_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.balance_label)

        self.balance_line = QFrame(self)
        self.balance_line.setFrameShape(QFrame.HLine)
        self.balance_line.setFrameShadow(QFrame.Plain)
        self.balance_line.setStyleSheet("background-color: #eca92f;")
        self.balance_line.setFixedHeight(20)
        self.layout.addWidget(self.balance_line)

        self.price_label = QLabel(f"BTCUSDT: Loading...", self)
        self.price_label.setStyleSheet("color: white; font-size: 18px;")
        self.price_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.price_label)

        self.price_line = QFrame(self)
        self.price_line.setFrameShape(QFrame.HLine)
        self.price_line.setFrameShadow(QFrame.Plain)
        self.price_line.setStyleSheet("background-color: #eca92f;")
        self.price_line.setFixedHeight(20)
        self.layout.addWidget(self.price_line)

        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        menubar.setStyleSheet("""
        QMenuBar {
            background-color: #0b1619;
            color: white;
        }
        QMenuBar::item {
            background-color: #0b1619;
            color: white;
        }
        QMenuBar::item:selected { 
            background-color: #eca92f; 
        }
        QMenu {
            background-color: #0b1619;
            color: white;
        }
        QMenu::item:selected {
            background-color: #eca92f;
        }
    """)
        menu_trade = QMenu("Trade", self)
        menubar.addMenu(menu_trade)
        menu_settings = QMenu("Settings", self)
        menubar.addMenu(menu_settings)
        menu_predict = QMenu("Chart", self)
        menubar.addMenu(menu_predict)
        action_wallet_get = QAction("Get", self)
        menu_trade.addAction(action_wallet_get)
        action_wallet_send = QAction("Send", self)
        menu_trade.addAction(action_wallet_send)
        action_wallet_send.triggered.connect(self.open_withrawal_dialog)
        action_api = QAction("API", self)
        action_api.triggered.connect(self.open_api_key_dialog)
        menu_settings.addAction(action_api)
        action_predicts = QAction("Candlestick", self)
        action_predicts.triggered.connect(self.show_prediction_window)
        menu_trade.setStyleSheet("background-color: #262627; color: white; font-size: 14px;")
        menu_settings.setStyleSheet("background-color: #262627; color: white; font-size: 14px;")
        menu_predict.setStyleSheet("background-color: #262627; color: white; font-size: 14px;")
        menu_predict.addAction(action_predicts)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.load_data()

        self.timer = QTimer(self)
        self.timer.setInterval(60000)
        self.timer.timeout.connect(self.load_data)
        self.timer.start()

    def open_api_key_dialog(self):
        api_dialog = ApiKeyDialog()
        api_dialog.exec_()
    
    def open_withrawal_dialog(self):
        withdrawal_dialog = WithdrawalDialog()
        withdrawal_dialog.exec_()

    def get_rub_to_usdt_rate(self):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=rub"
            response = requests.get(url)
            data = response.json()
            rub_to_usdt_rate = float(data['tether']['rub'])
            return rub_to_usdt_rate
        except Exception as e:
            print(f"Ошибка при получении курса RUB/USDT: {e}")
            return None
    
    def show_prediction_window(self):
        dialog = CandlestickSettings()
        dialog.exec_()
        
    def load_api_keys(self):
        if os.path.exists(API_FILE_PATH):
            try:
                with open(API_FILE_PATH, "r") as file:
                    data = json.load(file)
                    return data.get("api_key", ""), data.get("api_secret", "")
            except (json.JSONDecodeError, ValueError):
                return None, None
        return None, None

    def load_data(self):
        api_key, api_secret = self.load_api_keys()
        if api_key and api_secret:
            try:
                session = HTTP(
                    testnet=False,
                    api_key=api_key,
                    api_secret=api_secret,
                )
                account_info = session.get_wallet_balance(accountType="UNIFIED")["result"]["list"][0]
                balance_usdt = float(account_info['totalEquity'])
                rub_to_usdt_rate = self.get_rub_to_usdt_rate()
                balance_rub = round(rub_to_usdt_rate  * balance_usdt, 5)
                self.balance_label.setText(f"Trade Balance: {balance_usdt} USDT ~ {balance_rub} RUB")
                
                ticker_info_btc = session.get_tickers(category="spot", symbol="BTCUSDT")["result"]["list"][0]
                ticker_info_eth = session.get_tickers(category="spot", symbol="ETHUSDT")["result"]["list"][0]
                ticker_info_sol = session.get_tickers(category="spot", symbol="SOLUSDT")["result"]["list"][0]
                ticker_info_ton = session.get_tickers(category="spot", symbol="TONUSDT")["result"]["list"][0]
                last_price_BTC = ticker_info_btc["lastPrice"]
                last_price_ETH = ticker_info_eth["lastPrice"]
                last_price_SOL = ticker_info_sol["lastPrice"]
                last_price_TON = ticker_info_ton["lastPrice"]
                
                self.price_label.setText(f"BTC: {last_price_BTC} | ETH: {last_price_ETH} | SOL: {last_price_SOL} | TON: {last_price_TON} USDT")
            except Exception as e:
                self.balance_label.setText("Error loading balance")
                self.price_label.setText("Error loading price")
                print(f"Ошибка: {e}")
        else:
            self.balance_label.setText("API keys not set")
            self.price_label.setText("API keys not set")

class CandlestickSettings(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.setWindowTitle("CandleStickSettings")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        global screen_width, screen_height
        self.setGeometry((screen_width//2)-200, (screen_height//2)-150, 400, 300)

        layout = QVBoxLayout(self)

        self.pair_label = QLabel("Choose trading pair:", self)
        layout.addWidget(self.pair_label)

        self.pair_combo = QComboBox(self)
        self.pair_combo.addItems(["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", 'TON/USDT', 'USDC/USDT', 'DOGE/USDT', ])
        layout.addWidget(self.pair_combo)

        self.market_type_label = QLabel("Choose exchange type:", self)
        layout.addWidget(self.market_type_label)

        self.market_type_combo = QComboBox(self)
        self.market_type_combo.addItems(["spot", "inverse", "linear"])
        layout.addWidget(self.market_type_combo)

        date_layout = QHBoxLayout()

        self.start_date = QDateEdit(self)
        self.start_date.setDate(QDate.currentDate().addDays(-1))
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(QLabel("Start date:"))
        date_layout.addWidget(self.start_date)

        self.end_date = QDateEdit(self)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(QLabel("End date:"))
        date_layout.addWidget(self.end_date)

        layout.addLayout(date_layout)

        
        self.predict_button = QPushButton("Candlestick", self)
        self.predict_button.clicked.connect(self.open_chart)
        layout.addWidget(self.predict_button)

        self.result_label = QLabel("", self)
        layout.addWidget(self.result_label)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0b1619;
                color: white;
            }
            QLabel {
                color: white;
            }
            QComboBox, QPushButton, QDateEdit {
                background-color: #eca92f;
                color: black;
                font-size: 14px;
            }
        """)

    def open_chart(self):
        try:
            category = self.market_type_combo.currentText()
            
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            start_time = int(datetime.timestamp(datetime.combine(start_date, datetime.min.time()))) * 1000
            end_time = int(datetime.timestamp(datetime.combine(end_date, datetime.min.time()))) * 1000
            name = self.pair_combo.currentText()
            pair = self.pair_combo.currentText().replace('/', '') 
            chart = CandlestickChart(name=name,category=category,start_time=start_time, end_time=end_time, symbol=pair)  
            chart.plot()
            self.accept()
        except Exception as e:
            print(f"Ошибка: {e}")

class ApiKeyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.setWindowTitle("API Key Settings")
        global screen_width, screen_height
        self.setGeometry(screen_width//2-150, screen_height//2-75, 300, 150)
        layout = QFormLayout(self)
        self.api_key_input = QLineEdit(self)
        self.api_secret_input = QLineEdit(self)
        self.api_secret_input.setEchoMode(QLineEdit.Password)
        layout.addRow("API Key:", self.api_key_input)
        layout.addRow("API Secret:", self.api_secret_input)
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_api_keys)
        layout.addWidget(self.save_button)
        self.load_api_keys()
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0b1619;
                color: white;
            }
            QLabel {
                color: white;
            }
            QComboBox, QPushButton, QDateEdit {
                background-color: #eca92f;
                color: black;
                font-size: 14px;
            }
        """)

    def save_api_keys(self):
        api_key = self.api_key_input.text()
        api_secret = self.api_secret_input.text()
        data = {
            "api_key": api_key,
            "api_secret": api_secret
        }
        with open(API_FILE_PATH, "w") as file:
            json.dump(data, file)
        self.accept()

    def load_api_keys(self):
        if os.path.exists(API_FILE_PATH):
            try:
                with open(API_FILE_PATH, "r") as file:
                    data = json.load(file)
                    self.api_key_input.setText(data.get("api_key", ""))
                    self.api_secret_input.setText(data.get("api_secret", ""))
            except (json.JSONDecodeError, ValueError):
                self.api_key_input.setText("")
                self.api_secret_input.setText("")

class WithdrawalDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Withdrawal Settings")
        global screen_width, screen_height
        self.setGeometry(screen_width // 2 - 200, screen_height // 2 - 125, 400, 250)

        layout = QFormLayout(self)

        self.wallet_address_input = QLineEdit(self)
        layout.addRow("Wallet Address:", self.wallet_address_input)
        self.message_input = QLineEdit(self)
        layout.addRow("Comment(MemoTag):", self.message_input)

        amount_coin_layout = QHBoxLayout()

        self.amount_input = QLineEdit(self)
        amount_coin_layout.addWidget(QLabel("Amount:"))
        amount_coin_layout.addWidget(self.amount_input)

        self.coin_input = QComboBox(self)
        self.coin_input.addItems(["USDT", "BTC", "ETH", "XRP", "DOGE"])
        amount_coin_layout.addWidget(self.coin_input)

        layout.addRow(amount_coin_layout)

        self.network_input = QComboBox(self)
        self.network_input.addItems(["ERC20", "TRC20", "BEP20", "Arbitrum", "Polygon"])
        layout.addRow("Network:", self.network_input)

        self.save_button = QPushButton("Send", self)
        self.save_button.clicked.connect(self.send_withdrawal)
        layout.addWidget(self.save_button)

        self.setStyleSheet("""
            QDialog {
                background-color: #0b1619;
                color: white;
            }
            QLabel {
                color: white;
            }
            QComboBox, QPushButton, QLineEdit {
                background-color: #eca92f;
                color: black;
                font-size: 14px;
            }
        """)

        self.load_api_keys()

    def send_withdrawal(self):
        address = self.wallet_address_input.text()
        coin = self.coin_input.currentText()
        network = self.network_input.currentText()
        amount = self.amount_input.text()

        print(f"Address: {address}")
        print(f"Coin: {coin}")
        print(f"Network: {network}")
        print(f"Amount: {amount}")
        
        # need code..

    def load_api_keys(self):
        try:
            with open(API_FILE_PATH, "r") as file:
                data = json.load(file)
                api_key = data.get("api_key", "")
                api_secret = data.get("api_secret", "")
        except (json.JSONDecodeError, ValueError):
            pass
       
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    window = ByBitWallet()
    window.show()
    sys.exit(app.exec_())
