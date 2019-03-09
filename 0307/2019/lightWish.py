import os
import sys
import requests
from bs4 import BeautifulSoup as bs


# cookies格式化
# cookies = {x: y for x, y in map(lambda x: x.split("="), cookies.split(";"))}

class LightWish():
    def __init__(self, user, password, wishId):
        self.luckyUrl = "https://api-game.wutnews.net"
        self.loginUrl = "http://zhlgd.whut.edu.cn/tpass/login?service=http%3A%2F%2Fias.sso.wutnews.net%2Fportal.php%3Fposturl%3Dhttps%253A%252F%252Fapi-game.wutnews.net%252Flucky_2019%252flogin%252fias%26continueurl%3D"
        self.s = requests.Session()
        self.user = user
        self.password = password
        self.wishId = wishId

    def _login(self):
        text = self.s.get(self.loginUrl).text
        lt = bs(text, 'html.parser').find('input', {'id': 'lt'})['value']
        execution = bs(text, 'html.parser').find('input', {'name': 'execution'})['value']
        key = self.user + self.password + lt
        rsa = os.popen("node /home/ubuntu/wechat/luckyDay/desEncrypt.js {}".format(key), "r").read().strip()
        data = {"rsa": rsa, "ul": '13', "pl": '6', "lt": lt, "_eventId": "submit", "execution": execution}
        headers = {"Referer": "http://zhlgd.whut.edu.cn/tpass/login?service=http%3A%2F%2Fias.sso.wutnews.net%2Fportal.php%3Fposturl%3Dhttps%253A%252F%252Fapi-game.wutnews.net%252Flucky_2019%252flogin%252fias%26continueurl%3D", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0"}
        text = self.s.post(self.loginUrl, data=data, headers=headers).text
        try:
            user = bs(text, 'html.parser').find('input', {'name': 'user'})['value']
        except TypeError:
            return False
        self.s.post("https://api-game.wutnews.net/lucky_2019/login/ias", data={"user": user})
        return True

    def lightWish(self):
        try:
            wishId = int(self.wishId)
        except ValueError:
            return "请输入正确的愿望ID！"
        if self._login():
            resJson = self.s.post(url=self.luckyUrl+"/lucky_2019/center/wish_light", data={"wish_id": wishId}).json()
            return "msg: {}\ndata: {}".format(resJson['msg'], resJson['data'])
        else:
            return "登录失败，用户名或者密码输入错误！"


if __name__ == '__main__':
	user, password, wishId = sys.argv[1:4]
	t = LightWish(user, password, wishId)
	t.lightWish()

