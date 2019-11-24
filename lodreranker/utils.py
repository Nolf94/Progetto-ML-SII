import os
import json
import random
import sys

import numpy as np
from django.contrib.staticfiles import finders


class GeoArea(object):
    """Represents a circular area on a map, centered on given coordinates and with a given radius"""
    def __init__(self, latitude, longitude, radius):
        self.lat=latitude
        self.lng=longitude
        self.rad=radius

    def __str__(self):
        return f"({self.lat}, {self.lng}, {self.rad})"


class RetrievalError(Exception):
    pass


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


def handle_imgform(request, template_name, min_choices, session_obj_name, media_type):
    """Helper function for cold-start form views."""
    MIN_CHOICES = min_choices if min_choices else 5
    context = { 'min_choices': MIN_CHOICES }

    # choices are stored in session so that the random chosen order is kept during the process.
    if session_obj_name in request.session:
        choices = request.session[session_obj_name]
    else:
        # get a new random order
        choices = get_image_choices(media_type)
        request.session[session_obj_name] = choices

    if request.method == 'POST':
        selected_images = []
        try:
            selected_images = list(request.POST.get('selected').split(','))
            if len(selected_images) < MIN_CHOICES:
                raise ValueError
        except ValueError:
            # keep choices in the next attempt
            context['error'] = True
            if selected_images:
                context['selected'] = ','.join(x for x in selected_images)
            return {'success': False, 'data': context}

        # clear the stored order
        request.session.pop(session_obj_name)
        request.session.modified = True
        return {'success': True, 'data': (selected_images, choices)}
    else:
        # load the form with the chosen random order
        return {'success': False, 'data': context}


def disablePrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__
