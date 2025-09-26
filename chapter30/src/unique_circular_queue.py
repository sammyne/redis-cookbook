from circular_queue import CircularQueue


class UniqueCircularQueue(CircularQueue):

    def insert(self, *items):
        """
        将给定的一个或多个各不相同的元素插入至队列末尾，然后返回队列的长度作为结果。
        如果给定的某个或某些元素已经存在，那么它们会先从队列中被移除，然后再进行插入。
        """
        # 检查给定元素是否包含了重复元素
        if len(items) != len(set(items)):
            raise ValueError("Input items must be unique!")

        tx = self.client.pipeline()
        # 先从队列中移除与给定元素相同的元素
        for item in items:
            tx.lrem(self.key, 1, item)
        # 然后再将给定元素插入至队列末尾
        tx.rpush(self.key, *items)
        return tx.execute()[-1]  # 返回RPUSH的执行结果

    def remove(self, item):
        """
        从队列中移除指定元素。
        """
        return self.client.lrem(self.key, 1, item)


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    q = UniqueCircularQueue(r, "unique-rota")

    users = ["peter", "jack", "mary"]

    got = q.insert(*users)
    assert len(users) == got, f"Expected {len(users)}, got {got}"

    for i in range(3):
        got = q.rotate()
        assert (
            users[i % len(users)] == got
        ), f"expected {users[i%len(users)]}, got {got}"

    new_users  = ["jack", "mary", "peter"]

    got = q.insert('peter')
    assert len(users) == got, f"after re-inserting 'peter', expected {len(users)}, got {got}"

    for i in range(3):
        got = q.rotate()
        assert (
            new_users[i % len(new_users)] == got
        ), f"expected {new_users[i%len(new_users)]}, got {got}"
