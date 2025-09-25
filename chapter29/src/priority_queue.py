import time

BLOCK_FOREVER = 0


def none_or_single_queue_item(result):
    """
    以{item: priority}形式返回result列表中包含的单个优先队列元素。
    若result为空列表则直接返回None。
    """
    if result == []:
        return None
    else:
        item, priority = result[0]
        return {item: priority}


class PriorityQueue:

    def __init__(self, client, key):
        self.client = client
        self.key = key

    def insert(self, item, priority):
        """
        将带有指定优先级的元素添加至队列，如果元素已存在那么更新它的优先级。
        """
        self.client.zadd(self.key, {item: priority})

    def remove(self, item):
        """
        尝试从队列中移除指定的元素。
        移除成功时返回True，返回False则表示由于元素不存在而导致移除失败。
        """
        return self.client.zrem(self.key, item) == 1

    def min(self):
        """
        获取队列中优先级最低的元素及其优先级，如果队列为空则返回None。
        """
        result = self.client.zrange(self.key, 0, 0, withscores=True)
        return none_or_single_queue_item(result)

    def max(self):
        """
        获取队列中优先级最高的元素及其优先级，如果队列为空则返回None。
        """
        result = self.client.zrange(self.key, -1, -1, withscores=True)
        return none_or_single_queue_item(result)

    def pop_min(self):
        """
        弹出并返回队列中优先级最低的元素及其优先级，如果队列为空则返回None。
        """
        result = self.client.zpopmin(self.key)
        return none_or_single_queue_item(result)

    def pop_max(self):
        """
        弹出并返回队列中优先级最高的元素及其优先级，如果队列为空则返回None。
        """
        result = self.client.zpopmax(self.key)
        return none_or_single_queue_item(result)

    def length(self):
        """
        返回队列的长度，也即是队列包含的元素数量。
        """
        return self.client.zcard(self.key)

    def blocking_pop_min(self, timeout=BLOCK_FOREVER):
        """
        尝试从队列中弹出优先级最低的元素及其优先级，若队列为空则阻塞。
        可选参数timeout用于指定最大阻塞秒数，默认将一直阻塞到有元素可弹出为止。
        """
        result = self.client.bzpopmin(self.key, timeout)
        if result is not None:
            zset_name, item, priority = result
            return {item: priority}

    def blocking_pop_max(self, timeout=BLOCK_FOREVER):
        """
        尝试从队列中弹出优先级最高的元素及其优先级，若队列为空则阻塞。
        可选参数timeout用于指定最大阻塞秒数，默认将一直阻塞到有元素可弹出为止。
        """
        result = self.client.bzpopmax(self.key, timeout)
        if result is not None:
            zset_name, item, priority = result
            return {item: priority}


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    pq = PriorityQueue(r, "priority-queue")

    pq.insert("job a", 100)
    pq.insert("job b", 250)
    pq.insert("job c", 200)
    pq.insert("job d", 330)
    pq.insert("job e", 280)

    assert pq.length() == 5, f"unexpected pq length: expect 5, got {pq.length()}"
    assert pq.min() == {
        "job a": 100
    }, f"unexpected pq min: expect {'job a': 100}, got {pq.min()}"
    assert pq.max() == {
        "job d": 330
    }, f"unexpected pq max: expect {'job d': 330}, got {pq.max()}"

    max = pq.pop_max()
    assert max == {
        "job d": 330
    }, f"unexpected pq pop max: expect {'job d': 330}, got {max}"

    min = pq.pop_min()
    assert min == {
        "job a": 100
    }, f"unexpected pq pop min: expect {'job a': 100}, got {min}"

    pq2 = PriorityQueue(r, "priority-queue-2")

    pq2.insert("job f", 400)

    max = pq2.blocking_pop_max(timeout=5)
    assert max == {
        "job f": 400
    }, f"unexpected pq2 blocking pop max: expect {'job f': 400}, got {max}"

    start = time.time()
    got = pq2.blocking_pop_max(timeout=3)
    elapsed = time.time() - start
    assert not got, f"unexpected pq2 blocking pop max: expect None, got {got}"
    assert elapsed > 3.0, f"timeout too short: expect >5.0, got {elapsed}"
