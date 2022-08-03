import os
import time
from lxml import etree
import xml.etree.ElementTree as ET
import wget
import zipfile
import logger as log
import shutil
from toStrAux import toStr
from tqdm import tqdm


def formated_document(name_with_xml):
    # giving some pretty identation
    log.logger.info("Getting xml file tree")
    tree = etree.parse(f"../input/{name_with_xml}/{name_with_xml}")
    root = tree.getroot()

    if root is None:
        log.logger.info("Unable to get xml file tree. Aborting.")
        exit()

    pretty = etree.tostring(tree, encoding="unicode", pretty_print=True)
    formated = open('../input/input_formated.xml', 'w')
    formated.write(pretty)

    if not os.path.exists("../input/input_formated.xml"):
        log.logger.info("Unable to create formatted xml file. Aborting.")
        exit()

    log.logger.info("Successfully created formatted xml file")
    new_filename = "input_formated.xml"
    return new_filename


def remove_namespaces(file_name):
    log.logger.info("Getting xml file tree")
    tree = etree.parse(f"../input/{file_name}/{file_name}")
    root = tree.getroot()

    if root is None:
        log.logger.info("Unable to get xml file tree. Aborting.")
        exit()

    # Iterate through all XML elements
    for elem in root.getiterator():
        # Skip comments and processing instructions, because they do not have names
        if not (isinstance(elem, etree._Comment) or isinstance(elem, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname

    # Remove unused namespace declarations
    etree.cleanup_namespaces(root)
    out = open(f"../input/{file_name}/{file_name}", 'w+')
    out.write(etree.tostring(root).decode())

    for i in tqdm(range(100), disable=False, desc="Formating"):
        time.sleep(0.01)

    if not os.path.exists(f"../input/{file_name}"):
        log.logger.info("Unable to create clean xml file. Aborting.")
        exit()

    log.logger.info("Successfully created clean formatted xml file (Ready for parsing)")
    out.close()


def get_link(doc_name, doc_number):
    log.logger.info("Getting xml file tree")
    tree = etree.parse(f"../input/{doc_name}")
    root = tree.getroot()

    if root is None:
        log.logger.info("Problem getting root of xml file. Aborting.")
        exit()
    else:
        log.logger.info("Successfully got root, iniciating link search")
        # number os fields of each document
        docn = 1
        list_num_fields = []
        num_fields = 0
        keys = []
        texts = []
        fields = {}
        for doc in root.iter("result"):
            for child in doc.iter("doc"):
                for subchild in child.getiterator():
                    k = str(subchild.attrib.values()).replace("[", "").replace("]", "").replace("\'", "")
                    v = str(subchild.text)
                    if k != '' and v != '':
                        keys.append(k)
                        texts.append(v)
                        num_fields = num_fields + 1
                list_num_fields.append(num_fields)
                if docn == doc_number:
                    break
                else:
                    docn = docn + 1
                num_fields = 0

        i = 0
        start = list_num_fields[doc_number - 1] * (doc_number - 1)
        # end = (start + list_num_fields[doc_number - 1])

        while i < list_num_fields[doc_number - 1]:
            fields[keys[i + start]] = texts[i + start]
            i = i + 1

        link = fields.get('download_link')

        if link is None:
            log.logger.info("Field of link is empty. Aborting.")
            exit()
        log.logger.info("Successfully got link")
        return link


def download_zip(link):
    log.logger.info("Downloading iniciated")
    zip_name = link.rsplit('/', 1)[1]

    if os.path.exists(f"../parser/{zip_name}"):
        log.logger.info("File already exists, no need for downloading")
        return

    file_name = wget.download(link)
    print("\n")

    if file_name is None:
        log.logger.info("Error downloading the zip file. Aborting.")
        exit()

    log.logger.info("Waiting file to be downloaded")

    zip_len = os.path.getsize(f"../parser/{zip_name}")
    for i in tqdm(range(100), disable=False, desc="Extracting"):
        time.sleep(0.01)
    time.sleep(1)
    log.logger.info("Zip file successfully downloaded")

    # move xml to input
    src_path = f"../parser/{file_name}"
    dst_path = "../input/"
    shutil.move(src_path, dst_path)


def extract_zip(url):
    log.logger.info("Extracting Zip file")
    zip_name = url.rsplit('/', 1)[1]
    name_without_zip = zip_name.rsplit('.', 1)[0]
    name_with_xml = name_without_zip + ".xml"

    if os.path.exists(f"../input/{name_with_xml}"):
        log.logger.info("File already exists, no need for extracting")
        return
    i = 0
    with zipfile.ZipFile(f"../input/{zip_name}", 'r') as zipObj:
        # Get a list of all archived file names from the zip
        listOfFileNames = zipObj.namelist()
        # Iterate over the file names
        for fileName in listOfFileNames:
            # Check filename endswith csv
            if fileName.endswith('.xml'):
                # Extract a single file from zip
                zip_len = zipfile.ZipFile.getinfo(zipObj, fileName).file_size
                zipObj.extract(fileName, f"../input/{name_with_xml}")
                for i in tqdm(range(100), disable=False, desc="Extracting"):
                    time.sleep(0.01)

    log.logger.info("File successfully extracted from zip")
    # remove zip and dir
    os.remove(f"../input/{zip_name}")
    shutil.rmtree(f"../parser/{name_with_xml}", ignore_errors=True)


def xml2csv(file_name, output_file_name):
    log.logger.info("Getting xml file tree")
    new_tree = ET.parse(f"../input/{file_name}/{file_name}")
    new_root = new_tree.getroot()

    if new_root is None:
        log.logger.info("Problem getting root of xml file. Aborting.")
        exit()

    cols = ["Id", "FullNm", "ClssfctnTp", "CmmdtyDerivInd", "NtnlCcy", "Issr"]

    log.logger.info("Writing csv iniciated")
    with open(f'../output/{output_file_name}.csv', 'w+') as out:
        out.write("FinInstrmGnlAttrbts.Id, FinInstrmGnlAttrbts.FullNm, FinInstrmGnlAttrbts.ClssfctnTp, "
                  "FinInstrmGnlAttrbts.CmmdtyDerivInd, FinInstrmGnlAttrbts.NtnlCcy, Issr\n")

        list_issr = []

        for child in new_root.iter('Issr'):
            list_issr.append(toStr(child.text))

        i = 0
        for atrib in new_root.iter('FinInstrmGnlAttrbts'):
            id1 = atrib.find(cols[0]).text
            fn = atrib.find(cols[1]).text
            cls = atrib.find(cols[2]).text
            deriv = atrib.find(cols[3]).text
            ntccy = atrib.find(cols[4]).text
            out.write(toStr(id1) + ', ' + toStr(fn) + ', ' + toStr(cls) + ', ' + toStr(deriv) + ', ' +
                      toStr(ntccy) + ', ' + (list_issr[i]) + '\n')
            i = i + 1
    out.close()

    for i in tqdm(range(100), disable=False, desc="Writing to CSV"):
        time.sleep(0.01)

    if not os.path.exists(f"../output/{output_file_name}.csv"):
        log.logger.info("Unable to create csv file. Aborting.")
        exit()

    log.logger.info("Csv file successfully created")
