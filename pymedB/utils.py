import xml.etree.ElementTree as xml

def extract_xml(data: str):
  try:
    return xml.fromstring(data)
  except Exception:
    return None