def make_row_key(matrix_id, row):
    return f"Matrix:{matrix_id}:{row}"


class ListMatrix:

    def __init__(self, client, matrix_id, M, N):
        """
        创建一个使用ID标识，由指定数量的行和列组成的矩阵。
        """
        self.client = client
        self.matrix_id = matrix_id
        self.M = M
        self.N = N

    def init(self, elements=None):
        """
        根据给定数据对矩阵进行初始化。
        如果没有给定数据，那么将矩阵的所有元素初始化为0。
        """
        # 这个函数只能在矩阵不存在的情况下执行
        key = make_row_key(self.matrix_id, 0)
        assert self.client.exists(key) == 0

        # 如果未给定初始化矩阵，那么创建一个全为0的矩阵
        if elements is None:
            elements = []
            for _ in range(self.M):
                elements.append([0] * self.N)

        # 检查矩阵的行数是否正确
        if len(elements) != self.M:
            raise ValueError(f"Incorrect row number, it should be {self.M}.")
        # 检查矩阵中每个行的列数是否正确
        for row in range(self.M):
            if len(elements[row]) != self.N:
                raise ValueError(f"Incorrect col number, it should be {self.N}.")

        # 将给定的值推入矩阵的每一行中
        for row in range(self.M):
            row_key = make_row_key(self.matrix_id, row)
            self.client.rpush(row_key, *elements[row])

    def set(self, row, col, value):
        """
        将指定行列上的元素设置为给定的值。
        """
        row_key = make_row_key(self.matrix_id, row)
        self.client.lset(row_key, col, value)

    def get(self, row, col):
        """
        获取指定行列的值。
        """
        row_key = make_row_key(self.matrix_id, row)
        raw_value = self.client.lindex(row_key, col)
        return int(raw_value)

    def get_row(self, row):
        """
        获取指定行上所有列的值。
        """
        row_key = make_row_key(self.matrix_id, row)
        raw_cols = self.client.lrange(row_key, 0, -1)
        return list(map(int, raw_cols))

    def get_all(self):
        """
        获取整个矩阵的所有行和列。
        """
        matrix = []
        # 遍历并获取矩阵的每一行
        for row in range(self.M):
            matrix.append(self.get_row(row))
        return matrix


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    m = ListMatrix(r, "matrix", 3, 4)

    expect = [[1, 3, 9, 2], [5, 20, 32, 11], [73, 28, 65, 33]]

    m.init(expect)

    got = m.get(0, 0)
    assert 1 == got, f"(0, 0) expected 1, got {got}"

    got = m.get(0, 1)
    assert 3 == got, f"(0, 1) expected 3, got {got}"

    got = m.get_row(0)
    assert [1, 3, 9, 2] == got, f"row 0 expected [1,3,9,2], got {got}"

    got = m.get_all()
    assert expect == got, f"all expected {expect}, got {got}"
