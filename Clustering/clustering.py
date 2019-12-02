from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pyplot as plt

# for testing only
def plot(X, labels, n_clusters_):
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each)
              for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        class_member_mask = (labels == k)

        xy = X[class_member_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=14)
        plt.title('Estimated number of clusters: %d' % n_clusters_)

    plt.show()

class Clusterer(object):
    def dbscan(self, vectors, eps=0.49):
        print(f'\t{type(self).__name__}: starting clustering with {len(vectors)} vectors, eps: {eps}')

        ordered_clusters = np.array([])
        X = np.array(vectors)
        db = DBSCAN(algorithm='auto', eps=eps, leaf_size=30, metric='cosine', min_samples=1)
        clustered = db.fit_predict(X)
        labels = db.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

        clusters = [np.array(X[labels == i]) for i in range(n_clusters_)]
        ordered_clusters = sorted(clusters, key=len, reverse=True)

        # Calculate weight for each cluster
        weighted_clusters = []
        for cluster in ordered_clusters:
            weighted_cluster = {
                'centroid' : np.mean(cluster, axis=0).tolist(),
                'weight' : len(cluster)/len(X)
            }
            weighted_clusters.append(weighted_cluster)

        # plot(X, labels, n_clusters_)

        print(f'\t{type(self).__name__}: extracted {len(weighted_clusters)} clusters.')
        for i, cluster in enumerate(weighted_clusters):
                    print(f"\t\tcluster {i+1} - size: {int(cluster['weight']*len(X))}, weight: {cluster['weight']}")

        return weighted_clusters
