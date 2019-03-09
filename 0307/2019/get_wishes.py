import requests
from threading import Thread


luckyUrl = "https://api-game.wutnews.net"

# 给wishId设置个集合，方便后续去重
idSet = set()
# 判断是否已经存储了部分wishes，若存在则读取所有wishId
try:
	f = open("wishes.txt", encoding='utf-8')
	for line in f:
		wishId = line.replace("\n", " ").strip().split("\t")[0]
		idSet.add(int(wishId))
	f.close()
except OSError as e:
	pass
finally:
	f = open("wishes.txt", 'a', encoding='utf-8')

# 无需cookies
def GetWish():
	# 由于wish总数未知，给wish重复次数设定一个阈值，超过阈值时判定wish已取完
	n = 0
	while n < 100:
		res = requests.post(url=luckyUrl+"/lucky_2019/Center/get_wish")
		data = res.json()['data']
		wishId = data['id']
		if wishId in idSet:
			n += 1
		else:
			n = 0
			idSet.add(wishId)
			line = "{:<5}\t姓名： {:<4s}\t专业： {:{blank}<12}\t愿望： \"{}\"\n".format(wishId, data['name'], data['major'], data['content'].replace("\n", " ").strip(), blank=chr(12288))
			# 忽略特殊字符打印
			print(line.encode("gbk", 'ignore').decode("gbk", "ignore"), end='')
			f.write(line)
	return

def main():
	# 默认跑20个线程
	try:
		threads = [ Thread(target=GetWish) for _ in range(20) ]
		for t in threads:
			t.start()
		for t in threads:
			t.join()
		print("所有愿望抓取完成！！")
	except Exception as e:
		print(e)
	finally:
		print("退出程序！")
		f.close()

if __name__ == '__main__':
	main()
