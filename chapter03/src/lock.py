VALUE_OF_LOCK = ""

class Lock:

    def __init__(self, client, key):
        self.client = client
        self.key = key

    def acquire(self):
        """
        尝试获取锁，成功时返回True，失败时则返回False。
        """
        return self.client.set(self.key, VALUE_OF_LOCK, nx=True) is True

    def release(self):
        """
        尝试释放锁，成功时返回True，失败时则返回False。
        """
        return self.client.delete(self.key) == 1
    

if __name__ == '__main__':
  import os

  from redis import Redis

  host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") else "localhost"
  client = Redis(host)

  locker = Lock(client, "Lock:10086")

  assert locker.acquire()
  
  assert locker.release()