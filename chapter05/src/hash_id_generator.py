class HashIdGenerator:

    def __init__(self, client, key):
        self.client = client
        self.key = key

    def produce(self, name):
        """
        生成并返回下一个ID。
        """
        return self.client.hincrby(self.key, name, 1)

    def reserve(self, name, number):
        """
        保留前N个ID，使得之后生成的ID都大于N。
        这个方法只能在执行produce()之前执行，否则函数将返回False表示执行失败。
        返回True则表示保留成功。
        """
        return self.client.hsetnx(self.key, name, number) == 1


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    g = HashIdGenerator(r, "user-id-coll")

    assert g.reserve("post-id", 1000000)

    assert g.produce("post-id") == 1000001

    assert g.produce("post-id") == 1000002
