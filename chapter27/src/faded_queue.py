from fifo_queue import FifoQueue


class FadedQueue(FifoQueue):

    def __init__(self, client, key, max_length):
        """
        初始化一个会在长度超限之后接收新元素并淘汰旧元素的先进先出队列。
        其中max_length参数用于指定队列的最大长度。
        """
        self.client = client
        self.key = key
        self.max_length = max_length

    def enqueue(self, *items):
        """
        尝试将给定的一个或多个新元素推入至队列末尾。
        当队列的长度到达最大限制之后，每添加一个新元素，就会有一个最旧的元素被弹出。
        这个方法将返回成功推入且被最终保留的元素数量作为结果。
        """
        tx = self.client.pipeline()
        # 推入所有给定元素
        tx.rpush(self.key, *items)
        # 只保留列表索引区间-MAX_LENGTH至-1内的元素
        # 这些元素都是相对较新的元素
        tx.ltrim(self.key, -self.max_length, -1)
        tx.execute()
        # 计算成功推入且被保留的元素数量
        if len(items) < self.max_length:
            return len(items)
        else:
            return self.max_length


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    q = FadedQueue(r, "faded", 5)

    assert q.enqueue("a", "b") == 2, "enqueue expect 2"
    assert q.enqueue("c", "d", "e", "f", "g") == 5, "enqueue expect 5"
    assert q.enqueue("h") == 1, "enqueue expect 1"

    assert q.length() == 5, "length expect 5"

    got = [q.dequeue() for _ in range(5)]
    expect = ["d", "e", "f", "g", "h"]
    assert got == expect, f"dequeue expect {expect}, got {got}"
