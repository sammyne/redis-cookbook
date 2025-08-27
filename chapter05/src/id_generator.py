class IdGenerator:

    def __init__(self, client, name):
        self.client = client
        self.name = name

    def produce(self):
        """
        生成并返回下一个ID。
        """
        return self.client.incr(self.name)

    def reserve(self, n):
        """
        尝试保留前N个ID，使得之后生成的ID都大于N。
        这个方法只能在执行produce()之前执行，否则函数将返回False表示执行失败。
        返回True则表示保留成功。
        """
        return self.client.set(self.name, n, nx=True) is True

if __name__ == '__main__':
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    g = IdGenerator(r, "user-id")

    assert g.reserve(1000000)

    assert g.produce() == 1000001
    assert g.produce() == 1000002
    assert g.produce() == 1000003

    assert not g.reserve(9999)
