import logging
import os

import emailUtils
import jdUtils

import schedule
import time

from dotenv import load_dotenv

_logger = logging.getLogger("cronjobs")

def job():

	_logger.debug("Start read email job")
	emailUtils.readEmails()
	_logger.debug("read email job completed")

	_logger.debug("Start update job stats job")
	jdUtils.update_job_stats()
	_logger.debug("Completed update job stats job")

if __name__ == "__main__":	
	
	load_dotenv()

	logging.basicConfig(filename='werecruit.log', level=int(os.environ.get("LOG_LEVEL",20)))

	schedule.every(1).minutes.do(job)

	try:
		
		_logger.info("scheduler started")

		while 1:
			schedule.run_pending()
			time.sleep(1)

		_logger.warn("Scheduler stopped normally.")

	except KeyboardInterrupt:
		_logger.warn("Scheduler stopped bcas of keyboard interrupt.")
		schedule.clear()

	except Exception as e:
		_logger.error("Exception occured during running scheduled jobs.")
		_logger.error(e)
		_logger.warn("Scheduler stopped with errors.")

