from math import ceil  # 向下取整函数

DEFAULT_SIZE = 10  # 默认每页返回10个元素


class Paging:

    def __init__(self, client, key):
        self.client = client
        self.key = key

    def add(self, *items):
        """
        将给定的一个或多个元素推入到分页列表中，
        成功时返回列表当前包含的元素数量作为结果。
        """
        return self.client.lpush(self.key, *items)

    def get(self, page, size=DEFAULT_SIZE):
        """
        从指定分页中取出指定数量的元素。
        """
        # 根据给定的页数和元素数量计算出索引范围
        start = (page - 1) * size
        end = page * size - 1
        # 根据索引从分页列表中获取元素
        return self.client.lrange(self.key, start, end)

    def length(self):
        """
        返回分页列表包含的元素总数量。
        """
        return self.client.llen(self.key)

    def number(self, size=DEFAULT_SIZE):
        """
        返回在获取指定数量的元素时，分页列表包含的页数量。
        如果分页列表为空则返回0。
        """
        return ceil(self.length() / size)


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    p = Paging(r, "topic-list")

    for i in range(1, 10):
        assert p.add(f"topic:{i}") == i, f"添加第 {i} 个元素失败"

    assert p.length() == 9, "分页列表长度不正确"

    assert p.number(3) == 3, "分页列表页数不正确"

    assert p.get(1, 3) == ["topic:9", "topic:8", "topic:7"], "第 1 页元素不正确"
    assert p.get(2, 3) == ["topic:6", "topic:5", "topic:4"], "第 2 页元素不正确"
    assert p.get(3, 3) == ["topic:3", "topic:2", "topic:1"], "第 3 页元素不正确"
