#!/bin/bash

docker run -td --rm --name redis -p 6379:6379 redis:8.2.0-bookworm

host=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis`

echo "redis 的监听地址为 $host:6379"
