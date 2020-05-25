#!/usr/bin/env python3
#
# FossDash Project
#
# Copyright 2020 Orange
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Software Name : FossDash
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020 Orange
# SPDX-License-Identifier: MIT
#
# This software is distributed under the MIT license,
# the text of which is available at https://opensource.org/licenses/MIT
# or see the "license.txt" file for more details.

# Author: Drozdz Bartlomiej, Nicolas Toussaint
# Software description: FossDash collects and displays metrics produced by FOSSology.


import random
from uuid import uuid4
import argparse
import math
import pprint
import datetime
import time

FOSSOLOGY_INSTANCES = 1
SLEEP_SEC=0

# some random uiid not to need change the metrics each time
# set USE_STATIC_UUID to True
# ADD Some more so the number of uuid is equal or more the FOSSOLOGY_INSTANCES count
STATIC_UUIDS=[
    "c75317be-d7d3-44e1-bfd3-14af799ac99b",
    "c9725b85-3836-4e0c-8caa-2e34a6c17f74",
    "5f7a246b-7b98-4cf8-8ecc-d5b5fa9b5b0d",
    "267ebe2a-6587-4425-afc9-8ff44ed10c2a"
    ]

USE_STATIC_UUID=True
NUMBER_OF_DAYS_SINCE_TODAY_OLDEST=7
NUMBER_OF_DAYS_SINCE_TODAY_NEWEST=0

METRICS=[
    'number_of_groups,instance=${fossology_id}',
    'agents_count.wget_agent,instance=${fossology_id}',
    'agents_count.keyword,instance=${fossology_id}',
    'agents_count.buckets,instance=${fossology_id}',
    'agents_count.nomos,instance=${fossology_id}',
    'agents_count.copyright,instance=${fossology_id}',
    'agents_count.reuser,instance=${fossology_id}',
    'agents_count.spdx2,instance=${fossology_id}',
    'agents_count.readmeoss,instance=${fossology_id}',
    'agents_count.delagent,instance=${fossology_id}',
    'agents_count.pkgagent,instance=${fossology_id}',
    'agents_count.maintagent,instance=${fossology_id}',
    'agents_count.ecc,instance=${fossology_id}',
    'agents_count.monk,instance=${fossology_id}',
    'agents_count.decider,instance=${fossology_id}',
    'agents_count.mimetype,instance=${fossology_id}',
    'agents_count.deciderjob,instance=${fossology_id}',
    'agents_count.monkbulk,instance=${fossology_id}',
    'agents_count.spdx2tv,instance=${fossology_id}',
    'agents_count.dep5,instance=${fossology_id}',
    'agents_count.ojo,instance=${fossology_id}',
    'agents_count.ununpack,instance=${fossology_id}',
    'agents_count.unifiedreport,instance=${fossology_id}',
    'agents_count.adj2nest,instance=${fossology_id}',
    'agents_count.reportImport,instance=${fossology_id}',
    'number_of_users,instance=${fossology_id}',
    'number_of_url_uploads,instance=${fossology_id}',
    'number_of_projects__theoretically,instance=${fossology_id}',
    'number_of_file_uploads,instance=${fossology_id}'
];

class FossologyInstance(object):

    def __init__(self, index):
        if (USE_STATIC_UUID):
            self.id = STATIC_UUIDS[index]
        else:
            self.id = f"{uuid4()}"
        self.metrics =  { f"{x}".replace("${fossology_id}",self.id):1 for x in METRICS }
        self.instance_factor = random.randrange(80)+60

    def __metric_full_name(self,metric_name):
        return f"{metric_name},instance={self.id}"

    def __increase_metric(self, metric_name, value):
        self.metrics[self.__metric_full_name(metric_name)] += round((value * self.instance_factor / 100))

    def __metric_value(self, metric_name,value=None):
        metric_full_name =  f"{metric_name},instance={self.id}"
        if value:
            self.self.metrics[metric_full_name] = value
        return self.metrics[metric_full_name]

    def increase_random_all(self):

        current_users = self.__metric_value("number_of_users")
        current_groups = self.__metric_value("number_of_groups")

        increase_users = random.choices([True, False],weights=[0,40])
        increase_groups = random.choices([True,False],weights=[1,10])
        increase_projects = random.choices([True,False], weights=[5,40])
        increase_url_uploads = random.choices([True, False],weights=[1+current_users,50])
        increase_file_uploads = random.choices([True, False],weights=[1+current_users,50])

        if increase_users:
            self.__increase_metric("number_of_users",random.randrange(2))

        if increase_groups:
            self.__increase_metric("number_of_groups", random.choices([0,0,0,1,2],weights=[100,60,40,20,4])[0])

        if increase_file_uploads or increase_url_uploads:

            if increase_file_uploads:
                self.__increase_metric("number_of_file_uploads", random.randrange(2))
            if increase_url_uploads:
                self.__increase_metric("number_of_url_uploads", random.randrange(2))

            current_url_uploads = self.__metric_value("number_of_url_uploads")
            current_file_uploads = self.__metric_value("number_of_file_uploads")

            if increase_projects:
                self.__increase_metric("number_of_projects__theoretically", \
                        random.choices([0,0,0,1,2],weights=[100,60,40,20,1])[0])

            for agent_metric in [metric for metric in self.metrics if '.agents_count.' in metric]:
                self.metrics[agent_metric]+=random.randrange(2+math.floor(\
                        (current_file_uploads+current_url_uploads)/20))


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='description')
    parser.add_argument('days_oldest', type=int, nargs='?', default=NUMBER_OF_DAYS_SINCE_TODAY_OLDEST)
    parser.add_argument('days_newest', type=int, nargs='?', default=NUMBER_OF_DAYS_SINCE_TODAY_NEWEST)
    args = parser.parse_args()

    fossologies = [FossologyInstance(index) for index in range(FOSSOLOGY_INSTANCES)]
    today = datetime.datetime.today().date()
    for d in reversed(list(range(args.days_newest, args.days_oldest))):
        date = today - datetime.timedelta(days=d)
        timestamp = date.strftime("%s")
        for fossology in fossologies:
            fossology.increase_random_all()
            for metric_name in fossology.metrics:
                print (f"{metric_name} value={fossology.metrics[metric_name]} {timestamp}000000000")
            time.sleep(SLEEP_SEC)
