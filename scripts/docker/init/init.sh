#!/bin/bash

echo 'do init action'

#init network
function checkvar(){
  if [ ! $2 ]; then
    echo ERROR: need  $1
    exit 1
  fi
}

IFACE=${IFACE:-pbond0}

checkvar IP $IP
checkvar NETMASK $NETMASK
checkvar GATEWAY $GATEWAY

#network
cat > /etc/sysconfig/network-scripts/ifcfg-$IFACE << EOF
DEVICE=$IFACE
ONBOOT=yes
BOOTPROTO=static
IPADDR=$IP
NETMASK=$NETMASK
GATEWAY=$GATEWAY
EOF
ifconfig $IFACE $IP/16
echo 'set network successfully'

#route
gateway=`echo $IP | cut -d. -f1,2`.0.1
route add default gw $gateway
route del -net 0.0.0.0 netmask 0.0.0.0 dev eth0

#hosts
umount /etc/hosts
cat > /etc/hosts <<EOF
127.0.0.1 localhost
$IP     `hostname`
EOF
echo 'set host successfully'
cd /usr/local/LeMonitor/monitor-center
sed -i "s/127\.0\.0\.1/${IP}/g" cfg.json
sed -i "s/ihbs\.sys\.monitor\.letv\.cn/10\.183\.96\.57/g" cfg.json
cd -
chmod +x /opt/letv/monitor-center/check_scripts/check_all.sh
echo "*/2 * * * * root /opt/letv/monitor-center/check_scripts/check_all.sh >>/dev/null">> /etc/crontab
