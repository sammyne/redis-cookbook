# Redis 应用实例

## 环境
- redis v8.2.0
- docker v24.0.6, build ed223bc

## 快速开始
### 1. 启动 redis 服务
```bash
bash redis.sh up
```

> 关闭命令为 `bash redis.sh down`

启动后，样例日志如下
```bash
redis 的监听地址为 172.17.0.6:6379
```

### 2. 设置环境变量
```bash
# 上一步样例日志输出的地址的 IP 部分
export REDIS_HOST=172.17.0.6
```

### 3. 运行代码
进入各章的 python 项目文件夹，用 uv 执行 src 目录下的 python 脚本即可。

## 进度
- [ ] 第一部分 内部组件
  - [x] 01. 缓存文本数据
  - [x] 04. 带密码保护的锁
  - [x] 09. 二元操作记录器
  - [x] 10. 资源池

## 参考文献
- https://github.com/huangzworks/rediscookbook
