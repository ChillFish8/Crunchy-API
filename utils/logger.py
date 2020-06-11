from colorama import Fore, Style
from datetime import datetime
import colorama
colorama.init()


class Logger:
    to_store_in_file = []

    LOG_REQUESTS = True
    LOG_INFO = True
    LOG_DATABASE = True
    LOG_CACHE = True

    @classmethod
    def log_requests(cls, endpoint, addr):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTCYAN_EX + "[ Request ] " +
                Fore.CYAN + f" {endpoint} | " +
                Fore.WHITE + f"{addr}")
        if cls.LOG_REQUESTS:
            print(text)

    @classmethod
    def log_info(cls, msg):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTGREEN_EX + "[ Info ] " +
                Fore.WHITE + msg)
        if cls.LOG_INFO:
            print(text)

    @classmethod
    def log_database(cls, msg):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.MAGENTA + "[ Database ] " +
                Fore.WHITE + msg)
        if cls.LOG_DATABASE:
            print(text)

    @classmethod
    def log_cache(cls, msg):
        text = (Style.BRIGHT + Fore.BLUE + f"[{datetime.now().strftime('%a %m %b | %H:%M:%S')}]" +
                Fore.LIGHTBLUE_EX + "[ Cache ] " +
                Fore.WHITE + msg)
        if cls.LOG_CACHE:
            print(text)