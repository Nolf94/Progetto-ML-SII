import json
import os
import random
import sys

import numpy as np
from django.contrib.staticfiles import finders
from django.urls import reverse_lazy

from lodreranker import constants


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


def handle_imgform(request, submit_url_name, media_type,  min_choices=constants.COLDSTART_MIN_CHOICES):
    """Helper function for cold-start form views."""
    choices_key = f'choices_{media_type}'
    context = {
        'submit_url': reverse_lazy(submit_url_name),
        'mtype': media_type,
        'min_choices': min_choices,
        'choices_key': choices_key
    }
    # Choices are stored in session so that the random chosen order is kept during the process.
    if choices_key in request.session.keys():
        choices = request.session[choices_key]
    else:
        # Get a new random order
        choices = get_image_choices(media_type)
        request.session[choices_key] = choices

    if request.method == 'GET':
        # Load the form with the chosen random order
        return {'success': False, 'data': context}

    elif request.method == 'POST':
        selected_images = []
        try:
            selected_images = list(request.POST.get('selected').split(','))
            if len(selected_images) < min_choices:
                raise ValueError
        except ValueError:
            # Keep choices in the next attempt
            context['error'] = True
            if selected_images:
                context['selected'] = ','.join(x for x in selected_images)
            return {'success': False, 'data': context}

        # Clear the stored choices
        request.session.pop(choices_key)
        request.session.modified = True
        return {'success': True, 'data': (selected_images, choices)}


def disablePrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
