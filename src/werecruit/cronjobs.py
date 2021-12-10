import logging
import os

import emailUtils
import jdUtils

from dotenv import load_dotenv

_logger = logging.getLogger("cronjobs")

if __name__ == "__main__":
	
	
	load_dotenv()
	print(int(os.environ.get("LOG_LEVEL")))

	logging.basicConfig(filename='werecruit.log', level=int(os.environ.get("LOG_LEVEL",20)))

	try:
		
		_logger.info("Inside scheduled job")

		_logger.debug("Start read email job")
		emailUtils.readEmails()
		_logger.debug("read email job completed")

		_logger.debug("Start update job stats job")
		jdUtils.update_job_stats()
		_logger.debug("Completed update job stats job")

	except Exception as e:
		_logger.error("Exception occured during running scheduled jobs.")
		_logger.error(e)
	finally:
		_logger.info("Completed scheduled job. Will sleep now.!!!")

	#thread = Thread(target=start_read_email_bg_job)
	#thread.daemon = True
	#thread.start()