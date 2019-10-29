import json
import random

import numpy as np
from django.contrib.staticfiles import finders


def get_choices(path='poi'):
    data = open(finders.find(f'js/{path}.json')).read()
    json_data = json.loads(data)
    opts = []
    # json_data = json_data[:3]
    for item in random.sample(json_data, len(json_data)):
    # for item in json_data:
        opts.append(item)
    return opts


def get_vectors_from_selection(selection, choices):
    vectors = []
    for x in selection:
        vectors.append(np.array(choices[int(x)-1]['weights']))
    return vectors