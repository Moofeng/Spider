import os
import json
import requests
from queue import Queue
from threading import Thread


class DownloadPins():
    def __init__(self):
        self.pins = Queue()
        self.url = "http://img.hb.aicdn.com/"
        with open("pins.json") as f:
            pins = json.load(f)
        for key, pin in pins.items():
            self.pins.put((key, pin[0], pin[1]))

    def download(self):
        while not self.pins.empty():
            key, name, board = self.pins.get()
            # name中存在"/"或者名称为空就取key作为名称，否则取name前15个字符防止文件名过长
            name = key if "/" in name[:15] or not name else name[:15]
            try:
                tmp_dir = os.listdir("./pins/{}/".format(board))
            except FileNotFoundError:
                os.mkdir("./pins/{}".format(board))
                tmp_dir = os.listdir("./pins/{}/".format(board))
            if name not in tmp_dir:
                print("[+] 正在下载图片 —— {} ...".format(name))
                r = requests.get(self.url + key)
                with open("./pins/{}/{}".format(board, name), "wb") as f:
                    f.write(r.content)
                print("[+] 图片 —— {} 下载完成 ！".format(name))
            else:
                print("[+] 图片 —— {} 已经存在。".format(name))


    def start(self):
        threads = [Thread(target=self.download) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print("[+] 所有图片下载完成 ！！")

if __name__ == "__main__":
    s = DownloadPins()
    s.start()
