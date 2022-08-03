import logging
# filename="../output/log.log"
logging.basicConfig(level=logging.INFO, filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)
handler = logging.FileHandler('tester.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
