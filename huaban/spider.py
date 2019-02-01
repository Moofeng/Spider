import re
import json
import random
import requests
from time import sleep
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup as bs

USER_NAME = " " # 花瓣用户名


class Huaban():
    def __init__(self):
        self.headers = {"Referer": "http://login.meiwu.co/{}".format(USER_NAME),
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0", "DNT": "1"}
        self.cookies = {} # 填入用户对应的cookies
        self.boards = Queue()  # 用队列存储(board_id, board_title)
        self.pins = {}  # 用队列存储(pin_key, raw_text)

    def get_boards(self):
        while True:
            try:
                r = requests.get("http://login.meiwu.co/{}/".format(USER_NAME),
                                 cookies=self.cookies, headers=self.headers)
                result = re.search(
                    r'app.page\[\"user\"\] = (.*?)};', r.text).group(1) + "}"
            except:
                continue
            break
        boards = json.loads(result)['boards']
        for board in boards:
            self.boards.put((board['board_id'], board['title']))
            print("[+] 已读取画板 —— 《{}》!".format(board['title']))
        while True:
            try:
                # max的值是上一页最后一个board_id
                r = requests.get("http://login.meiwu.co/{}/?jrkb9krs&limit=10&wfl=1&max={}".format(
                    USER_NAME, board['board_id']), cookies=self.cookies, headers=self.headers)
                result = re.search(
                    r'app.page\[\"user\"\] = (.*?)};', r.text
                ).group(1) + "}"
            except Exception as e:
                # 休眠0-1s，避免大量无用功的重连
                sleep(random.randint(1,10) / 10)
                continue
            boards = json.loads(result)['boards']
            if not boards:
                break
            for board in boards:
                self.boards.put((board['board_id'], board['title']))
                print("[+] 已读取画板 —— 《{}》!".format(board['title']))

    def get_pins(self):
        while not self.boards.empty():
            board_id, board_title = self.boards.get()
            print("[+] 正在画板 —— 《{}》 内搜索图片...".format(board_title))
            while True:
                try:
                    r = requests.get(
                        "http://login.meiwu.co/boards/{}/".format(board_id), cookies=self.cookies)
                    result = re.search(
                        r'app.page\[\"board\"\] = (.*?)};', r.text).group(1) + "}"
                except Exception as e:
                    sleep(random.randint(1,10) / 10)
                    continue
                break
            pins = json.loads(result)['pins']
            for pin in pins:
                self.pins[pin['file']['key']] = (pin['raw_text'], board_title)
            while True:
                try:
                    r = requests.get(
                        "http://login.meiwu.co/boards/{}/?jrkgjpug&limit=20&wfl=1&max={}".format(board_id, pin['pin_id']), cookies=self.cookies)
                    result = re.search(
                        r'app.page\[\"board\"\] = (.*?)};', r.text).group(1) + "}"
                except Exception as e:
                    sleep(random.randint(1,10) / 10)
                    continue
                pins = json.loads(result)['pins']
                if not pins:
                    break
                for pin in pins:
                    self.pins[pin['file']['key']] = (pin['raw_text'], board_title)

    def save_data(self):
        with open('pins.json', 'w') as f:
            json.dump(self.pins, f)
        print("[+] 数据存储完成！")

    def start(self):
        print("[+] 开始读取画板信息...")
        self.get_boards()
        print("[+] 画板信息读取完毕！开始读取画板内图片链接...")
        threads = [Thread(target=self.get_pins) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print("[+] 图片读取完毕，开始存储数据...")
        self.save_data()


if __name__ == "__main__":
    s = Huaban()
    s.start()
