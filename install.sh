#!/bin/sh

#remove old version of grafana and influxdb
apt-get remove --purge influxdb -y
apt-get remove --purge grafana -y
rm -rf /etc/grafana
rm -rf /etc/influxdb

# InfluxDB Installation
wget -qO- https://repos.influxdata.com/influxdb.key |  apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | tee /etc/apt/sources.list.d/influxdb.list

apt-get update && apt-get install influxdb -y

# To start influxDB service
sudo service influxdb start

#creating database
curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE fossology_db"

#creating admin user and password
curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE USER admin WITH PASSWORD 'admin' WITH ALL PRIVILEGES"

# copy influx config files
cp ./influxdb-etc/influxdb.conf /etc/influxdb/

# restart influxDB service
sudo service influxdb restart

# Grafana installation 
apt-get update
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | tee -a /etc/apt/sources.list.d/grafana.list 

apt-get update && apt-get install grafana -y

# To start the service and verify that the service has started:
service grafana-server start

# copy grafana config files
cp ./grafana_local_setup/grafana.ini /etc/grafana/
cp -r ./grafana_local_setup/provisioning /etc/grafana/

#install grafan plugins
grafana-cli plugins install grafana-piechart-panel
grafana-cli plugins install vonage-status-panel
grafana-cli plugins install mxswat-separator-panel
grafana-cli plugins install mtanda-histogram-panel
grafana-cli plugins install michaeldmoore-multistat-panel

# restart grafana
service grafana-server restart