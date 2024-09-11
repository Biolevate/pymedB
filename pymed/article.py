import json
import datetime

from xml.etree.ElementTree import Element
from typing import Optional

from .helpers import get_content



class PubMedArticle:
    """ Data class that contains a PubMed article.
    """

    __slots__ = (
        "pubmed_id",
        "title",
        "abstract",
        "keywords",
        "journal",
        "publication_date",
        "authors",
        "methods",
        "conclusions",
        "results",
        "copyrights",
        "doi",
        "xml",
    )

    def __init__(
        self,
        xml_element: Optional[Element] = None,
        *args: list,
        **kwargs: dict,
    ) -> None:
        """ Initialization of the object from XML or from parameters.
        """

        # If an XML element is provided, use it for initialization
        if xml_element is not None:
            self._initializeFromXML(xml_element=xml_element)

        # If no XML element was provided, try to parse the input parameters
        else:
            for field in self.__slots__:
                self.__setattr__(field, kwargs.get(field, None))

    def _extract_pubmed_id(self, xml_element: Element) -> str:
        path = ".//ArticleId[@IdType='pubmed']"
        return get_content(element=xml_element, path=path)

    def _extract_title(self, xml_element: Element) -> str:
        path = ".//ArticleTitle"
        return get_content(element=xml_element, path=path)

    def _extract_keywords(self, xml_element: Element) -> str:
        path = ".//Keyword"
        return [
            keyword.text for keyword in xml_element.findall(path) if keyword is not None
        ]

    def _extract_journal(self, xml_element: Element) -> str:
        path = ".//Journal/Title"
        return get_content(element=xml_element, path=path)

    def _extract_abstract(self, xml_element: Element) -> str:
        path = ".//AbstractText"
        return get_content(element=xml_element, path=path)

    def _extract_conclusions(self, xml_element: Element) -> str:
        path = ".//AbstractText[@Label='CONCLUSION']"
        return get_content(element=xml_element, path=path)

    def _extract_methods(self, xml_element: Element) -> str:
        path = ".//AbstractText[@Label='METHOD']"
        return get_content(element=xml_element, path=path)

    def _extract_results(self, xml_element: Element) -> str:
        path = ".//AbstractText[@Label='RESULTS']"
        return get_content(element=xml_element, path=path)

    def _extract_copyrights(self, xml_element: Element) -> str:
        path = ".//CopyrightInformation"
        return get_content(element=xml_element, path=path)

    def _extract_doi(self, xml_element: Element) -> str:
        path = ".//ArticleId[@IdType='doi']"
        return get_content(element=xml_element, path=path)

    def _extract_publication_date(
        self, xml_element: Element
    ) -> datetime.datetime:
        # Get the publication date
        try:

            # Get the publication elements
            publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
            publication_year = int(get_content(publication_date, ".//Year", None))
            publication_month = int(get_content(publication_date, ".//Month", "1"))
            publication_day = int(get_content(publication_date, ".//Day", "1"))

            # Construct a datetime object from the info
            return datetime.date(
                year=publication_year, month=publication_month, day=publication_day
            )

        # Unable to parse the datetime
        except Exception as e:
            print(e)
            return None

    def _extract_authors(self, xml_element: Element) -> list:
        return [
            {
                "lastname": get_content(author, ".//LastName", None),
                "firstname": get_content(author, ".//ForeName", None),
                "initials": get_content(author, ".//Initials", None),
                "affiliation": get_content(author, ".//AffiliationInfo/Affiliation", None),
            }
            for author in xml_element.findall(".//Author")
        ]

    def _initializeFromXML(self, xml_element: Element) -> None:
        """ Helper method that parses an XML element into an article object.
        """

        # Parse the different fields of the article
        self.pubmed_id = self._extract_pubmed_id(xml_element)
        self.title = self._extract_title(xml_element)
        self.keywords = self._extract_keywords(xml_element)
        self.journal = self._extract_journal(xml_element)
        self.abstract = self._extract_abstract(xml_element)
        self.conclusions = self._extract_conclusions(xml_element)
        self.methods = self._extract_methods(xml_element)
        self.results = self._extract_results(xml_element)
        self.copyrights = self._extract_copyrights(xml_element)
        self.doi = self._extract_doi(xml_element)
        self.publication_date = self._extract_publication_date(xml_element)
        self.authors = self._extract_authors(xml_element)
        self.xml = xml_element

    def toDict(self) -> dict:
        """ Helper method to convert the parsed information to a Python dict.
        """

        return {key: self.__getattribute__(key) for key in self.__slots__}

    def toJSON(self) -> str:
        """ Helper method for debugging, dumps the object as JSON string.
        """

        return json.dumps(
            {
                key: (value if not isinstance(value, (datetime.date, Element)) else str(value))
                for key, value in self.toDict().items()
            },
            sort_keys=True,
            indent=4,
        )
