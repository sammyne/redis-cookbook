class BinaryRecorder:

    def __init__(self, client, key):
        self.client = client
        self.key = key

    def setbit(self, index):
        """
        将指定索引上的二进制位设置为1。
        """
        self.client.setbit(self.key, index, 1)

    def clearbit(self, index):
        """
        将指定索引上的二进制位设置为0。
        """
        self.client.setbit(self.key, index, 0)

    def getbit(self, index):
        """
        获取指定索引上的二进制位的值。
        """
        return self.client.getbit(self.key, index)

    def countbits(self, start, end):
        """
        统计指定索引区间内，值为1的二进制位数量。
        """
        return self.client.bitcount(self.key, start, end, "BIT")

if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    client = Redis(host=host, decode_responses=True)

    r = BinaryRecorder(client, "user:256512:sign-in")

    r.setbit(0)
    r.setbit(3)

    assert r.countbits(0, 6) == 2