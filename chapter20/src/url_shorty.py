from base62 import base62

URL_ID_COUNTER = "UrlShorty:id_counter"
URL_MAPPING_HASH = "UrlShorty:mapping_hash"


class UrlShorty:

    def __init__(self, client):
        self.client = client

    def shorten(self, url):
        """
        为给定的网址创建并记录一个对应的短网址ID，然后将其返回。
        """
        # 生成10进制数字ID
        origin_id = self.client.incr(URL_ID_COUNTER)
        # 将10进制数字转换为62进制数字ID（短网址ID）
        short_id = base62(origin_id)
        # 在映射中关联短网址ID和原网址
        self.client.hset(URL_MAPPING_HASH, short_id, url)
        # 返回短网址ID
        return short_id

    def restore(self, short_id):
        """
        根据给定的短网址ID找出与之对应的原网址。
        返回None则表示给定的短网址ID不存在。
        """
        # 根据短网址ID从映射中找出并返回与之对应的原网址
        return self.client.hget(URL_MAPPING_HASH, short_id)


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    s = UrlShorty(r)

    assert s.shorten("https://www.example.com") == "1", '1st shortened should be "1"'
    assert s.shorten("https://www.gd.gov.cn") == "2", '2nd shortened should be "2"'

    assert (
        s.restore("1") == "https://www.example.com"
    ), '1st restored should be "https://www.example.com"'
    assert (
        s.restore("2") == "https://www.gd.gov.cn"
    ), '2nd restored should be "https://www.gd.gov.cn"'
