#! /usr/bin/env python

from __future__ import with_statement

import re
INTRO_LINE_RE = re.compile(r"^c.*interpolation of order\s+([0-9]+).*quadratures of order\s+([0-9]+)\s*$")
DATA_LINE_RE = re.compile(r"^\s*data\s+([xyzw])s([0-9]+)\/")
ENTRY_LINE_RE = re.compile(r"^[0-9* ]{6,6}\s*([- +,.deDE0-9]+)/?\s*$")

import sys
with open(sys.argv[1]) as inf:
    lines = inf.readlines()

rule_name = sys.argv[2]

current_order = None
current_array = None
AXES = "xyz"
table = {}

i = 0
while i < len(lines):
    l = lines[i]
    i += 1
    if not l.strip():
        continue


    intro_match = INTRO_LINE_RE.match(l)
    if intro_match is not None:
        current_order = int(intro_match.group(1))
        assert current_order not in table
        table[current_order] = {
                "points": [[], [], []],
                "weights": [],
                "quad_degree": int(intro_match.group(2))
                }
        continue

    if l[0] in "cC":
        continue

    data_match = DATA_LINE_RE.match(l)
    if data_match is not None:
        what = data_match.group(1)
        data_order = int(data_match.group(2))

        assert data_order == current_order

        if what == "w":
            current_array = table[current_order]["weights"]
        else:
            current_array = table[current_order]["points"][AXES.index(what)]
        continue

    entry_match = ENTRY_LINE_RE.match(l)
    if entry_match is not None:
        data = entry_match.group(1).split(",")
        current_array.extend(e.replace("D", "e") for e in data if e.strip())
        continue

    raise RuntimeError("unmatched line %d: %s" % (i+1, l))


from pprint import pformat
print """# GENERATED by modepy/contrib/weights-from-fortran.py
# DO NOT EDIT

import numpy as np

points = "points"
weights = "weights"
quad_degree = "quad_degree"

def process_rule(table):
    result = {}
    for order, kv in table.iteritems():
        result[order] = order_tbl = {}
        for k, v in kv.iteritems():
            if isinstance(v, list):
                v = [i for i in v if not isinstance(i, list) or len(i)]
                v = np.array(v)

            order_tbl[k] = v

    return result

%s = process_rule(%s)""" % (rule_name, pformat(table).replace("'", ""))