#!/bin/bash

set -e

rm -f MLBModel/testing_dataset.csv

venv/bin/python src/train_test.py