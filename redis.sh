#!/bin/bash

case "$1" in
  down)
    docker rm -f redis
  ;; 

  up)
    docker run -td --rm --name redis -p 6379:6379 redis:8.2.0-bookworm

    host=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis`

    echo "redis 的监听地址为 $host:6379"
  ;;

  *)
    echo "未知命令 '$1'"
    exit 1
  ;;
esac
