#!/bin/bash

cd `dirname $0`

source env/bin/activate

flask --app run.py start-conf "$1"
