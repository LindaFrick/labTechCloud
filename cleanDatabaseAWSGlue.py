import sys
import json
import pyspark
from pyspark.sql.functions import col, collect_list, array_join, length

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job


##### FROM FILES
tedx_dataset_path = "s3://data-techcloud/tedx_dataset.csv"

##### START JOB CONTEXT AND JOB
sc = SparkContext()

glueContext = GlueContext(sc)
spark = glueContext.spark_session

## READ TAGS DATASET
dataset = spark.read.option("header","true").csv(tedx_dataset_path)
dataset = dataset.where(length(col("idx")) == 32)
dataset = dataset.dropDuplicates()

dataset.repartition(1).write.csv('s3://data-techcloud/clean_tedx_dataset.csv')

#dataset = dataset.rdd.map(list)

#with open('s3://data-techcloud/clean_tedx_dataset.csv', 'w') as f:
#    f.write(dataset)