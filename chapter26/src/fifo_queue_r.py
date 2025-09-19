NON_BLOCK = -1


class FifoQueueR:

    def __init__(self, client, key):
        self.client = client
        self.key = key

    def enqueue(self, *items):
        """
        以先进先出顺序将给定的一个或多个元素推入队列。
        返回推入操作执行之后，队列当前的长度作为结果。
        """
        return self.client.lpush(self.key, *items)

    def dequeue(self, timeout=NON_BLOCK):
        """
        以先进先出顺序弹出队列中的一个元素。
        如果队列为空则返回None。
        可选的timeout参数用于启用/关闭阻塞功能，它的值可以是：
        1) NON_BLOCK ，默认值，不启用阻塞功能；
        2）0 ，一直等待直到有值可弹出为止；
        3）N ，大于0的秒数N，表示等待的最长秒数。
        """
        if timeout == NON_BLOCK:
            return self.client.rpop(self.key)
        else:
            ret = self.client.brpop(self.key, timeout)
            if ret is not None:
                return ret[1]  # 从(list, item)元组中获取被弹出元素

    def length(self):
        """
        返回队列的长度。
        """
        return self.client.llen(self.key)


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    q = FifoQueueR(r, "fifo-queue-r")

    assert q.enqueue("a", "b", "c") == 3, "bad queue length after enqueueing"

    assert q.dequeue() == "a", "bad 1st dequeue"
    assert q.dequeue() == "b", "bad 2nd dequeue"
    assert q.dequeue() == "c", "bad 3rd dequeue"
    assert not q.dequeue(), "4th dequeue is not None"
