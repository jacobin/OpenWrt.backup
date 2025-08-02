#!/bin/bash
## https://blog.51cto.com/u_15911260/5934639
Njob=10                        # 作业数目
Nproc=5                        # 可同时运行的最大作业数

function CMD {                 # 测试命令，随机等待几秒钟
    n=$((RANDOM % 5 + 1))
    echo "Job $1 Ijob $2 sleeping for $n seconds ..."
    sleep $n
    echo "Job $1 Ijob $2 exiting ..."
}

Pfifo="/tmp/$$.fifo"           # 以PID为名，防止创建命名管道时与已有文件重名，从而失败
mkfifo $Pfifo                  # 创建命名管道
exec 6<>$Pfifo                 # 以读写方式打开命名管道，文件标识符fd为6
                               # fd可取除0，1，2，5外0-9中的任意数字
rm -f $Pfifo                   # 删除文件，也可不删除，不影响后面操作

# 在fd6中放置$Nproc个空行作为令牌
for((i=1; i<=$Nproc; i++)); do
    echo
done >&6

for((i=1; i<=$Njob; i++)); do  # 依次提交作业
    read -u6                   # 领取令牌，即从fd6中读取行，每次一行
                               # 对管道，读一行便少一行，每次只能读取一行
                               # 所有行读取完毕，执行挂起，直到管道再次有可读行
                               # 因此实现了进程数量控制
    {                          # 要批量执行的命令放在大括号内，后台运行
        CMD $i && {            # 可使用判断子进程成功与否的语句
            echo "Job $i finished"
        } || {
            echo "Job $i error"
        }
        sleep 1                # 暂停1秒，可根据需要适当延长，
                               # 关键点，给系统缓冲时间，达到限制并行进程数量的作用
        echo >&6               # 归还令牌，即进程结束后，再写入一行，使挂起的循环继续执行
    } &
done

wait                           # 等待所有的后台子进程结束

exec 6>&-                      # 删除文件标识符
