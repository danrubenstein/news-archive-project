'''
Do the PCA on the on the article titles, and then reduce ISM
'''

import pandas as pd 
import numpy as np 
from numpy import linalg as LA
from sklearn.decomposition import PCA
from FileDownloads import load_resources
import matplotlib.pyplot as plt
import time

def get_word_decomposition_over_df(df, components=20, words_shown=10):
    '''
    Do the word decomposition over sources
    '''
    start = time.time()
    times = []

    with open("10k.txt") as f:
        common_words = [x.strip("\n") for x in f.readlines()][:2000]

    # Sources that put their organization in their title
    source_words = ["ladbible", "ign", "fox", "sportbible"]

    title_words = df["title"].str.lower().str.split().apply(lambda x:
                                                 [y for y in x if y not in common_words and y not in source_words])
    
    times.append(time.time() - start)
    start = time.time()
    
    title_word_frequencies = pd.Series([x for y in title_words.tolist() for x in y]).str.replace('\W+', '').value_counts()
    
    times.append(time.time() - start)
    start = time.time()

    most_common_words = np.array(title_word_frequencies.index[:1000])
    word_indicator_df = pd.DataFrame()

    df["titles_adjusted"] = df["title"].str.replace('\W+', '').str.split()

    times.append(time.time() - start)
    start = time.time()

    for word in most_common_words[1:]:
        word_indicator_df["contains_{}".format(word)] = df["titles_adjusted"].apply(lambda x: word in x)

    times.append(time.time() - start)
    start = time.time()

    pca = PCA(n_components=components)
    pca.fit(word_indicator_df)

    times.append(time.time() - start)
    start = time.time()

    print(times)

    return [list(most_common_words[np.argsort(x)[-words_shown:]]) for x in pca.components_]


def get_distance_between_sources(source1, source2, percentile=1):
    '''
    Compute the squared distance matrix
    '''
    return np.argsort(np.array([min([np.setxor1d(x, y).size for y in source2]) for x in source1]))[percentile]

'''
ISOMAP routine, applied to minimum-ish headline similarity
'''

def get_word_isomap(word_results):

    distance_squared_matrix = get_distance_squared_matrix(word_results)
    centered_gram = get_double_centered_matrix(distance_squared_matrix)
    isomap = get_isomap(centered_gram)

    return isomap


def get_distance_squared_matrix(results):

    distance_matrix = np.empty((len(results), len(results)))
    
    for i in range(len(sources_grouped)):
        for j in range(i, len(sources_grouped)):
            x = get_distance_between_sources(results[i], results[j])
            distance_matrix[i][j] = x 
            distance_matrix[j][i] = x

    return distance_matrix


def get_double_centered_matrix(distance_matrix):

    n_points = distance_matrix.shape[0]
    centering_matrix = np.identity(n_points) - 1 / n_points * np.ones((n_points, n_points))
    centered_gram = -0.5 * np.dot(np.dot(centering_matrix, distance_matrix), centering_matrix)

    return centered_gram


def get_isomap(centered_gram, num_dims=2):

    u, s, v = LA.svd(centered_gram)
    res = np.dot(u[:, :num_dims], np.sqrt(np.diag(s[:num_dims])))

    return res.tolist()

if __name__ == "__main__":

    articles_df = load_resources(update=False)
    sources_grouped = articles_df.groupby("source")

    results = []
    for name, group in sources_grouped:
        results.append(get_word_decomposition_over_df(group))

    source_names = [name for name, group in sources_grouped]
    isomap = get_word_isomap(results)
    
    fig, ax = plt.subplots(1,1)
    x_coords = [x[0] for x in isomap]
    y_coords = [x[1] for x in isomap]
    ax.scatter(x_coords, y_coords, s=20)
    for i, name in enumerate(source_names):
        print(i, name)
        ax.annotate(name, (isomap[i][0], isomap[i][1]))
    ax.set_title(r"News organization headline similarity")
    plt.savefig("output.png")
    




