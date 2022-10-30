#!/bin/sh

function get_docker_host_ip () {
  /sbin/ip route|awk '/default/ { print $3 }'
}

export DOCKER_HOST_IP=$(get_docker_host_ip)
echo "Docker host detected: ${DOCKER_HOST_IP}"