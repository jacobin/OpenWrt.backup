###############################################################################
# https://www.cnblogs.com/lsdb/p/12102418.html
import os
import time
import portalocker

class CSingleRunningInstance():
    def _get_lock(self):
        file_name = os.path.basename(__file__)
        # linux等平台依然使用标准的/var/run，其他nt等平台使用当前目录
        if os.name == "posix":
            lock_file_name = f"/var/run/{file_name}.pid"
        else:
            lock_file_name = f"{file_name}.pid"
        self.fd = open(lock_file_name, "w")
        try:
            portalocker.lock(self.fd, portalocker.LOCK_EX | portalocker.LOCK_NB)
            # 将当前进程号写入文件
            # 如果获取不到锁上一步就已经异常了，所以不用担心覆盖
            self.fd.writelines(str(os.getpid()))
            # 写入的数据太少，默认会先被放在缓冲区，我们强制同步写入到文件
            self.fd.flush()
        except:
            print(f"{file_name} have another instance running.")
            exit(1)

    def __init__(self):
        self._get_lock()

    def hello_world(self):
        print("hello world!")
        time.sleep(30)

    # 和fcntl有点区别，portalocker释放锁直接有unlock()方法
    # 还是一样，其实并不需要在最后自己主动释放锁
    def __del__(self):
        portalocker.unlock(self.fd)


if __name__ == "__main__":
    obj = CSingleRunningInstance()
    #obj.hello_world()
    print("hello world!")
    time.sleep(30)
