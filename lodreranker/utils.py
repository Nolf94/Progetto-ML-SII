import json
import random

import numpy as np
from django.contrib.staticfiles import finders


def get_image_choices(media_type):
    data = json.loads(open(finders.find(f'js/{media_type}.json')).read())
    opts = []
    [opts.append(x) for x in random.sample(data, len(data))]
    return opts


def get_vectors_from_selection(selection, choices):
    vectors = []
    for x in selection:
        vectors.append(np.array(choices[int(x)-1]['weights']))
    return vectors