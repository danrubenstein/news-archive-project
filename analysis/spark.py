def spark_actions(article_results):
    '''
    A series of spark calls
    '''

    sc = SparkContext()
    article_data = sc.parallelize(article_results)

    # Most common words in title
    title_units = article_data.flatMap(lambda x: (x["title"].split(), 1))
    title_counts = title_units.reduceByKey(lambda x, y: x+y)
    title_counts.takeOrdered(20, lambda x: -x[1])

    # Most common words in description
    description_units = article_data.flatMap(lambda x: (x["description"].split(), 1))
    description_counts = description_units.reduceByKey(lambda x, y: x+y)
    description_counts.takeOrdered(20, lambda x: -x[1])