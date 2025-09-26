from itertools import batched


def make_row_key(matrix_id, row):
    return f"LogicalMatrix:{matrix_id}:{row}"


class LogicalMatrix:

    def __init__(self, client, matrix_id, row_size, col_size):
        self.client = client
        self.matrix_id = matrix_id
        self.ROW_SIZE = row_size
        self.COL_SIZE = col_size

    def init(self, elements=None):
        """
        根据给定数据对矩阵进行初始化。
        如果没有给定数据，那么将矩阵的所有元素初始化为0。
        """
        # 位图的所有位默认都被初始化为0，无需另外进行设置
        if elements is None:
            return

        # 遍历矩阵的每个行和列，对其进行设置
        tx = self.client.pipeline()
        for row in range(self.ROW_SIZE):
            row_key = make_row_key(self.matrix_id, row)
            for col in range(self.COL_SIZE):
                tx.setbit(row_key, col, elements[row][col])
        tx.execute()

    def set(self, row, col, value):
        """
        对矩阵指定行列上的二进制位进行设置。
        """
        row_key = make_row_key(self.matrix_id, row)
        self.client.setbit(row_key, col, value)

    def get(self, row, col):
        """
        获取矩阵指定行列上的二进制位。
        """
        row_key = make_row_key(self.matrix_id, row)
        return self.client.getbit(row_key, col)

    def get_row(self, row):
        """
        获取矩阵指定行中所有列的二进制位。
        """
        row_key = make_row_key(self.matrix_id, row)
        tx = self.client.pipeline()
        for col in range(self.COL_SIZE):
            tx.getbit(row_key, col)
        return tx.execute()

    def get_all(self):
        """
        获取整个矩阵的所有二进制位。
        """
        tx = self.client.pipeline()
        # 遍历所有行
        for row in range(self.ROW_SIZE):
            row_key = make_row_key(self.matrix_id, row)
            # 编列每行的所有列
            for col in range(self.COL_SIZE):
                # 获取二进制位
                tx.getbit(row_key, col)
        # 将整个矩阵的二进制位放到一个列表里面
        all_bits = tx.execute()
        # 将一维列表转换为二维矩阵（Python>=3.12）
        return [list(row) for row in batched(all_bits, self.COL_SIZE)]


if __name__ == "__main__":
    import os
    from redis import Redis

    host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
    r = Redis(host=host, decode_responses=True)

    matrix = LogicalMatrix(r, 10086, 2, 4)

    matrix.init([[1, 0, 1, 0], [0, 1, 0, 1]])

    got = matrix.get_row(0)
    assert got == [1, 0, 1, 0], f"bad 1st row: expect [1,0,1,0], got {got}"

    got = matrix.get_row(1)
    assert got == [0, 1, 0, 1], f"bad 2nd row: expect [0,1,0,1], got {got}"

    got = matrix.get_all()
    assert got == [
        [1, 0, 1, 0],
        [0, 1, 0, 1],
    ], f"bad all: expect [[1,0,1,0],[0,1,0,1]], got {got}"

    matrix.set(0, 0, 0)
    got = matrix.get_all()
    assert got == [
        [0, 0, 1, 0],
        [0, 1, 0, 1],
    ], f"bad all: expect [[0,0,1,0],[0,1,0,1]], got {got}"
