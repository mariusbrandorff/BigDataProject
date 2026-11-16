import asyncio
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pokecard import PokemonCardInfo


def job():
    engine = create_engine('hive://localhost:10000/default')
    factory = sessionmaker(bind=engine)
    session = factory()
    for instance in session.query(PokemonCardInfo):
        print(instance.id)





async def main(instant: bool = False):
    if instant:
        job()
        return
    
    cron_expr = os.environ["SCHEDULE"]  # e.g. "*/5 * * * *"

    scheduler = BlockingScheduler()
    trigger = CronTrigger.from_crontab(cron_expr)
    scheduler.add_job(job, trigger=trigger)
    scheduler.start()

if __name__ == "__main__":
    asyncio.run(main(True))