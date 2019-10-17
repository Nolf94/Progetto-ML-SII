import json
import random

import numpy as np
from django.contrib.staticfiles import finders


def get_poi_choices():
    data = open(finders.find("js/poi.json")).read()
    json_data = json.loads(data)
    opts = []

    # json_data = json_data[:3]
    for item in random.sample(json_data, len(json_data)):
    # for item in json_data:
        opts.append(item)
    return opts


def get_poi_weights(selection, choices):
    vectors = []

    for x in selection:
        vectors.append(np.array(choices[int(x)-1]['weights']))
        # print(poi_choices[x-1]['name'])
    # print(vectors)
    # print(sum(vectors))

    weights = sum(vectors)
    return json.dumps(weights.tolist())
