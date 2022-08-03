import re
import os
import requests
import sys
import toParseAux as parse
import logger as log
from toStrAux import toStr


# get response from our request and write it to file
log.logger.info("Starting to access to URLs")
URL1 = 'https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q='
URL2 = '*&fq=publication_date:%5B2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100'

log.logger.info("Getting html response")
response = requests.get(URL1 + URL2)
if response is None:
    log.logger.exception("Error getting html response")
    exit()
else:
    log.logger.info("Successfully got response")

# if file does not exists, create one
log.logger.info("Writing response to file")
with open('../input/raw_input.xml', 'wb') as file:
    file.write(response.content)
file.close()
log.logger.info("Successfully written file")

if os.stat("../input/raw_input.xml").st_size == 0:
    log.logger.exception("Response file is empty")
    exit()
else:
    log.logger.info("Response file has content")

# if file exists, identify docs
log.logger.info("Getting first document")
file = open('../input/raw_input.xml', 'r')
nDocs = len(re.findall(r"(<doc>)", file.read()))
file.close()

if nDocs == 0:
    log.logger.info("Error. There's no zip urls for transferring. Aborting.")
    exit()
else:
    log.logger.info(f"There are {toStr(nDocs)} docs")
    try:
        doc_selected = int(input("Select which doc you want to parse [1-4]: "))
        if 1 <= doc_selected <= 4:
            log.logger.info(f"Input validated, user choose {doc_selected}")
            link = parse.get_link('raw_input.xml', doc_selected)
            parse.download_zip(link)
            parse.extract_zip(link)

            zip_name = link.rsplit('/', 1)[1]
            name_without_zip = zip_name.rsplit('.', 1)[0]
            name_with_xml = name_without_zip + ".xml"

            # new_filename = parse.formated_document(name_with_xml)
            parse.remove_namespaces(name_with_xml)
            parse.xml2csv(name_with_xml, sys.argv[1])
            an = input("Do you want to see output file [Y/N]: ")
            if an == 'Y' or an == 'y':
                f = open('../output/output.csv', 'r')
                content = f.read()
                print(content)
                f.close()
            else:
                log.logger.info("Terminatted")
    except FloatingPointError:
        log.logger.exception("Inputted value is not an integer on the range")
        exit()
