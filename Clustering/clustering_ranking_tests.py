from random import randrange, uniform
import numpy as np
import pandas as pd

N = 100
clusters = [37, 25, 19, 14, 5]
num_inputs = 10


def normalize_scores_1(l):
  min_val = min([x[0] for x in l])
  max_val = max([x[0] for x in l])
  return [(round((x[0]-min_val)/(max_val-min_val),4),x[1]) for x in l]

def normalize_scores_2(l):
  min_val = min([x[0] for x in l])
  max_val = max([x[0] for x in l])
  return [(round((x[0]-min_val)/(max_val-min_val) * x[1],4),x[1]) for x in l]

def final_score(mat):
  return pd.DataFrame([x[0] for x in l] for l in mat).sum()

if __name__ == "__main__":
  clusters_weights=[(c/N) for c in clusters]
  similarities = [[(uniform(-1,1) * weight, weight) for x in range(num_inputs)] for weight in clusters_weights]

  print(f"\n{len(clusters)} clusters per {num_inputs} inputs")

  print("\nWEIGHTS:")
  print(pd.DataFrame([x[1] for x in l] for l in similarities))

  print("\nSIMILARITIES:")
  print(pd.DataFrame([x[0] for x in l] for l in similarities))


  normalized_sims_1 = [normalize_scores_1(l) for l in similarities]

  print("\nNormalized scores NOT multiplied for cluster weight")
  print(pd.DataFrame(normalized_sims_1))

  normalized_sims_2 = [normalize_scores_2(l) for l in similarities]

  print("\nNormalized scores considering cluster weight")
  print(pd.DataFrame(normalized_sims_2))

  print("\nFinal score for each item")
  final_scores = final_score(normalized_sims_2)
  print(final_scores)
  

  print("\nRanked")
  ranking = final_scores.sort_values(ascending=False)
  print(ranking)