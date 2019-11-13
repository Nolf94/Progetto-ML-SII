from scipy import spatial

class Recommender(object):

    def cosine_similarity(self, vec1, vec2):
        return 1 - spatial.distance.cosine(vec1, vec2)

    def rank_clustering_items(self, clusters, items):
        # initialize empty scores
        items = [dict(item, score=0) for item in items]
        for cluster in clusters:
            # calculate similarity between each item and current cluster's centroid
            relative_sims = {}
            for item in items:
                similarity = self.cosine_similarity(cluster["centroid"], item["vector"])
                relative_sims[item['id']] = similarity
            # sum similarities for normalization
            relative_sims_tot = sum(x for x in relative_sims.values())
            # item partial score = normalized similarity * cluster's weight
            for item in items:
                item['score'] += (relative_sims[item['id']]/relative_sims_tot) * cluster['weight']

        ranked_items = sorted(items, reverse=True, key=lambda item: item['score'])
        for i, item in enumerate(ranked_items):
            print(f"{str(i+1)}, {item['score']}, {item['id']}, {item['name']}")
        return ranked_items

    def rank_summarize_items(self, sum, items):
        items = [dict(item, score=self.cosine_similarity(sum, item["vector"])) for item in items]
        ranked_items = sorted(items, reverse=True, key=lambda item: item['score'])
        for i, item in enumerate(ranked_items):
            print(f"{str(i+1)}, {item['score']}, {item['id']}, {item['name']}")
        return ranked_items
