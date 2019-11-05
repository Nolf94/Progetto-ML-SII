from scipy import spatial

class Recommender(object):

    def get_cosine_similarity(self, vec1, vec2):
        similarity = 1 - spatial.distance.cosine(vec1, vec2)
        return similarity

    def rank_items(self, clusters, items):
        
        # TODO rank items
        # for each cluster calculate a ranking using cossim
            # assign a score to each vector the following way:
            # score(v) = cossim(v) / sum(cossim_all_ranked_vectors) * weight(cluster)
        # sum vector scores across all rankings
        # re-rank vectors based on total score
        
        pass
  
