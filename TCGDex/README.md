# Requirements
Listen to kafka topic, when receiving anything, react to this.
 - Fetch the new pokemon card (potentially historical data)

Run a cron job, where whenever the cron schedule lines up, fetch all tracked cards.  
Push this to a kafka topic.

## Jobs
### New card tracked
```mermaid
sequenceDiagram
    Kafka ->>+ Application: New card<br>tracked
    Application ->>+ TCGDex: Request card<br>info
    TCGDex -->>- Application: Card info
    Application -->>- Kafka: New card<br>info
```

### Cron job
```mermaid
sequenceDiagram
    Participant App@{type: , alias: "Application"}
    Participant HDFS@{type: "database"}
    Participant Kafka@{type: "queue"}
    Participant TCG

    loop Every cron interval
        App ->>+ HDFS: Request cards
        HDFS -->>- App: Tracked cards
        loop Every card
            App ->>+ TCG: Request card price
            TCG -->>- App: Card price
            App ->> Kafka: New card price
        end
    end
```