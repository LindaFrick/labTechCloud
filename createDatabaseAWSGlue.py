###### TEDx-Load-Aggregate-Model
######

import sys
import json
import pyspark
from pyspark.sql.functions import col, collect_list, array_join

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job




##### FROM FILES
tedx_dataset_path = "s3://data-techcloud/clean_tedx_dataset.csv/clean_tedx_dataset.csv"

###### READ PARAMETERS
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

##### START JOB CONTEXT AND JOB
sc = SparkContext()


glueContext = GlueContext(sc)
spark = glueContext.spark_session


    
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


#### READ INPUT FILES TO CREATE AN INPUT DATASET
tedx_dataset = spark.read \
    .option("header","true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(tedx_dataset_path)
    
tedx_dataset.printSchema()


#### FILTER ITEMS WITH NULL POSTING KEY
count_items = tedx_dataset.count()
count_items_null = tedx_dataset.filter("idx is not null").count()

print(f"Number of items from RAW DATA {count_items}")
print(f"Number of items from RAW DATA with NOT NULL KEY {count_items_null}")



## READ TAGS DATASET
tags_dataset_path = "s3://data-techcloud/tags_dataset.csv"
tags_dataset = spark.read.option("header","true").csv(tags_dataset_path)

## READ WATCH NEXT
watch_next_dataset_path= "s3://data-techcloud/watch_next_dataset.csv"
watch_next_dataset= spark.read \
    .option("header","true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(watch_next_dataset_path)
    
## READ YT CSV
ted_yt_dataset_path = "s3://data-techcloud/dataset_yt.csv"
ted_yt_dataset = spark.read \
    .option("header","true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
   .csv(ted_yt_dataset_path)
    

# CREATE THE AGGREGATE MODEL, ADD TAGS TO TEDX_DATASET
tags_dataset_agg = tags_dataset.groupBy(col("idx").alias("idx_ref")).agg(collect_list("tag").alias("tags"))
tags_dataset_agg.printSchema()
tedx_dataset_agg = tedx_dataset.join(tags_dataset_agg, tedx_dataset.idx == tags_dataset_agg.idx_ref, "left") \
    .drop("idx_ref") \
    .select(col("idx").alias("_id"), col("*")) \
    .drop("idx") \

watch_next_dataset = watch_next_dataset.withColumnRenamed("url","watch_next_url")
watch_next_dataset = watch_next_dataset.drop_duplicates()
watch_next_dataset = watch_next_dataset.groupBy(col("idx")).agg(collect_list("watch_next_idx").alias("watch_next_ids"),collect_list("watch_next_url").alias("watch_next_urls"))
tedx_all_dataset= watch_next_dataset.join(tedx_dataset_agg, watch_next_dataset.idx== tedx_dataset_agg._id, "inner") \
    .drop("idx") \
    .select(col("*")) \

tedx_complete_dataset = tedx_all_dataset.join(ted_yt_dataset, tedx_all_dataset._id== ted_yt_dataset.idx, "inner") \
    .drop("idx") \
    .select(col("*")) \

tedx_complete_dataset.printSchema()


#mongo_uri = "mongodb://cluster0-shard-00-00.lg7o7.mongodb.net:27017,cluster0-shard-00-01.lg7o7.mongodb.net:27017,cluster0-shard-00-02.lg7o7.mongodb.net:27017"
mongo_uri = "mongodb://clustertechcloud-shard-00-00.nv77c.mongodb.net:27017,clustertechcloud-shard-00-01.nv77c.mongodb.net:27017,clustertechcloud-shard-00-02.nv77c.mongodb.net:27017"
write_mongo_options = {
    "uri": mongo_uri,
    "database": "unibg_tedx_2021",
    "collection": "tedx_data",
    "username": "admin",
    "password": "*WmKEfXy.VkUQ35",
    "ssl": "true",
    "ssl.domain_match": "false"}
from awsglue.dynamicframe import DynamicFrame
tedx_dataset_dynamic_frame = DynamicFrame.fromDF(tedx_complete_dataset, glueContext, "nested")

glueContext.write_dynamic_frame.from_options(tedx_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)
