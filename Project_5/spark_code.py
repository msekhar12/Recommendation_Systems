from pyspark import SparkConf, SparkContext
from math import sqrt
import sys

def filterDuplicates((userID, ratings)):
    (joke1,rating1) = ratings[0]
    (joke2,rating2) = ratings[1]
    return joke1 < joke2
 
def computeCosineSimilarity(ratingPairs):
    numPairs = 0
    sum_xx = sum_yy = sum_xy = 0
    for ratingX, ratingY in ratingPairs:
        sum_xx += ratingX * ratingX
        sum_yy += ratingY * ratingY
        sum_xy += ratingX * ratingY
        numPairs += 1
 
    numerator = sum_xy
    denominator = sqrt(sum_xx) * sqrt(sum_yy)
 
    score = 0
    if (denominator):
        score = (numerator / (float(denominator)))
 
    return (score, numPairs)
 
def makePairs((user, ratings)):
    (joke1, rating1) = ratings[0]
    (joke2, rating2) = ratings[1]
    return ((joke1, joke2), (rating1, rating2))
 
 
conf = SparkConf().setMaster("local").setAppName("Ratings..")
sc = SparkContext(conf = conf)
 
#data = sc.textFile("hdfs:///user/a152700/data/jester_ratings.dat")
data = sc.textFile("toy_data.csv")
 
print "Read the file..."
ratings = data.map(lambda x: x.split(",")).map(lambda x: (int(x[0]),(int(x[1]),float(x[2]))))

display_df = ratings.collect()

for i in display_df:
    print i

 
print "Prepared the ratings RDD..."
 
#ratingsPartitioned = ratings.partitionBy(100)
#print "Partitioned the ratings into 100 parts..."
ratingsPartitioned = ratings
 
joinedRatings = ratingsPartitioned.join(ratingsPartitioned)
print "Self join completed ..."
 
uniqueJoinedRatings = joinedRatings.filter(filterDuplicates)
print "Filtered the duplicates..."

display_df = uniqueJoinedRatings.collect()

for i in display_df:
    print i

 
#jokePairs = uniqueJoinedRatings.map(makePairs).partitionBy(100)
jokePairs = uniqueJoinedRatings.map(makePairs)


display_df = jokePairs.collect()

for i in display_df:
    print i
 
jokePairRatings = jokePairs.groupByKey()



print "Computing the cosine similarity ..."
jokePairSimilarities = jokePairRatings.mapValues(computeCosineSimilarity).persist()
 
print "Sorting the results..."
 
jokePairSimilarities.sortByKey()

display_df = jokePairSimilarities.collect()
for i in display_df:
    print i
 
print "Saving the results..."
jokePairSimilarities.saveAsTextFile("joke-sims")
#display_rdd = rdd.collect()
 
#for i in range(10):
#     print display_rdd[i]
 
print "script ends..."
