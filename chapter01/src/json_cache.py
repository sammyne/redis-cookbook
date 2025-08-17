import json
from cache import Cache

class JsonCache:

    def __init__(self, client):
        self.cache = Cache(client)

    def set(self, name, content, ttl=None):
        """
        为指定名字的缓存设置内容。
        可选的ttl参数用于设置缓存的生存时间。
        """
        json_data = json.dumps(content)
        self.cache.set(name, json_data, ttl)

    def get(self, name):
        """
        尝试获取指定名字的缓存内容，若缓存不存在则返回None。
        """
        json_data = self.cache.get(name)
        if json_data is not None:
            return json.loads(json_data)

if __name__ == "__main__":
  import os

  from redis import Redis

  host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"

  client = Redis(host, port=6379, decode_responses=True)

  cache = JsonCache(client) # 创建缓存对象
  data = {"id":10086,"name":"Peter","gender":"male","age":56}
  cache.set("User:10086", data) # 缓存数据
  print(cache.get("User:10086")) # 获取缓存数据
