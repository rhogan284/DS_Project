from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext

spark = SparkSession.builder \
    .appName("Airport Data Streaming") \
    .getOrCreate()

ssc = StreamingContext(spark.sparkContext, 1)

rddQueue = []
for _ in range(5):
    rddQueue.append(ssc.sparkContext.parallelize([
        (123, "Flight Arrival", "JFK", "2024-05-07 12:00:00"),
        (124, "Flight Departure", "LAX", "2024-05-07 12:15:00")
    ]))

inputSteam = ssc.queueStream(rddQueue)

processedStream = inputSteam.map(lambda record: (record[2], record[1]))
processedStream.pprint()

ssc.start()
ssc.awaitTermination()