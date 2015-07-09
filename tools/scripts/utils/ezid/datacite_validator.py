from lxml import etree
from io import StringIO

def _validateXML(xml_doc):
    xsd_doc = etree.parse('./schema/datacite-schema-v3.xsd')
    xsd = etree.XMLSchema(xsd_doc)
    xml = etree.fromstring(xml_doc)
    return xsd.validate(xml)
