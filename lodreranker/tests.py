import numpy as np
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse_lazy

from Clustering.clustering import Clusterer
from lodreranker import constants
from lodreranker.recommendation import Recommender
from lodreranker.lod_queries import Sparql


# TEST CLUSTERING
@login_required
def test_clustering(request):
    epss = np.arange(0.6, 0.7, 0.01)
    for eps in epss:
        print(f'[{eps}]')
        for mtype in [constants.MOVIE, constants.BOOK, constants.MUSIC]:
            mrec = Recommender(mtype, request.user, None)
            print(f"\t++++{mtype}++++")
            clusters = Clusterer().dbscan(mrec.uservectors, eps)
        print("="*100)
    return redirect(reverse_lazy('home'))



@login_required
def test_poiqueries(request):
    sqpl = Sparql(constants.DBPEDIA)
    from pprint import pprint
    for mtype in [constants.MOVIE, constants.BOOK, constants.MUSIC]:
        try:
            query = sqpl.get_query(mtype, 'poi', 'Colosseo')
            # print(query)
            bindings = sqpl.execute(query)
            # pprint(bindings)
            print(len(bindings))
        except Exception as e:
            print(e)
            

    return redirect(reverse_lazy('home'))
