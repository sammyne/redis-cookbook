class Stack:

    def __init__(self, client, key):
        self.client = client
        self.key = key

    def push(self, item):
        """
        将给定元素推入至栈。
        """
        self.client.rpush(self.key, item)

    def pop(self):
        """
        从栈中弹出最近被推入的元素，如果栈为空则返回None。
        """
        return self.client.rpop(self.key)

    def top(self):
        """
        获取（但不弹出）位于栈顶的元素，也即是最近被推入至栈的元素。
        如果栈为空则返回None。
        """
        return self.client.lindex(self.key, -1)

    def size(self):
        """
        返回栈的大小，也即是栈目前包含的元素数量。
        """
        return self.client.llen(self.key)

    def trim(self, N):
        """
        将栈修剪至指定大小，只保留栈中最新的N个元素。
        当N为0时，清空/删除整个栈。
        """
        if N == 0:
            self.client.delete(self.key)
        else:
            # 先计算被保留元素的索引范围，然后执行修剪操作
            start = 0 - N
            end = -1
            self.client.ltrim(self.key, start, end)


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    stack = Stack(r, "stack")

    stack.push("a")
    stack.push("b")
    stack.push("c")

    assert stack.top() == "c", f"expect 'c', got {stack.top()}"
    assert stack.pop() == "c", "expect 'c'"
    assert stack.pop() == "b", "expect 'b'"
    assert stack.pop() == "a", "expect 'a'"
    assert not stack.pop(), "expect None"

    for i in range(8):
        stack.push(i)

    assert stack.size() == 8, f"unexpected stack size: expect 8, got {stack.size()}"

    stack.trim(5)
    assert stack.size() == 5, f"unexpected stack size: expect 5, got {stack.size()}"

    stack.trim(0)
    assert stack.size() == 0, f"unexpected stack size: expect 0, got {stack.size()}"
