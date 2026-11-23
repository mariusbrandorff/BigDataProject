# BigDataProject


## HDFS structure
```mermaid
treeView-beta
ingestion/
    avro/ ## Raw?
        tcgdex/
        openskin/
        biquote/
    parquet/
        tcgdex/
        openskin/
        biquote/
volatility/
    predictions/
```

## Kafka topics

`{SOURCE}_in` and `{SOURCE}_out`.  
Ex. `/openskin_in` for new skins that are to be tracked and `/openskin_out` for when new data is fetched.


## Dev Container
refer to 