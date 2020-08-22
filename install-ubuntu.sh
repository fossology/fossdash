#!/bin/bash -e
#
# Copyright (C) 2020 Orange
# SPDX-License-Identifier: GPL-2.0
# Author: Darshan Kansagara <kansagara.darshan97@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 

#remove old version of grafana and influxdb
apt-get remove --purge influxdb -y
apt-get remove --purge grafana -y
rm -rf /etc/grafana
rm -rf /etc/influxdb

# InfluxDB Installation
wget -qO- https://repos.influxdata.com/influxdb.key |  apt-key add -
if [ ! -f /etc/lsb-release ]; then
    echo "ERROR :: FILE /etc/lsb-release does not exist."
    exit 1
fi
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
cp ./grafana-etc/grafana.ini /etc/grafana/
cp -r ./grafana-etc/provisioning /etc/grafana/

#install grafan plugins
grafana-cli plugins install grafana-piechart-panel
grafana-cli plugins install vonage-status-panel
grafana-cli plugins install mxswat-separator-panel
grafana-cli plugins install mtanda-histogram-panel
grafana-cli plugins install michaeldmoore-multistat-panel

# restart grafana
service grafana-server restart