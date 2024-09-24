import json
import datetime

from typing import Optional

from .helpers import get_content
from xml.etree.ElementTree import Element


class PubMedBookArticle:
    """ Data class that contains a PubMed article.
    """

    __slots__ = (
        "pubmed_id",
        "title",
        "abstract",
        "publication_date",
        "authors",
        "copyrights",
        "doi",
        "isbn",
        "language",
        "publication_type",
        "sections",
        "publisher",
        "publisher_location",
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
        path = ".//BookTitle"
        return get_content(element=xml_element, path=path)

    def _extract_abstract(self, xml_element: Element) -> str:
        path = ".//AbstractText"
        return get_content(element=xml_element, path=path)

    def _extract_copyrights(self, xml_element: Element) -> str:
        path = ".//CopyrightInformation"
        return get_content(element=xml_element, path=path)

    def _extract_doi(self, xml_element: Element) -> str:
        path = ".//ArticleId[@IdType='doi']"
        return get_content(element=xml_element, path=path)

    def _extract_isbn(self, xml_element: Element) -> str:
        path = ".//Isbn"
        return get_content(element=xml_element, path=path)

    def _extract_language(self, xml_element: Element) -> str:
        path = ".//Language"
        return get_content(element=xml_element, path=path)

    def _extract_publication_type(self, xml_element: Element) -> str:
        path = ".//PublicationType"
        return get_content(element=xml_element, path=path)

    def _extract_publication_date(self, xml_element: Element) -> str:
        path = ".//PubDate/Year"
        return get_content(element=xml_element, path=path)

    def _extract_publisher(self, xml_element: Element) -> str:
        path = ".//Publisher/PublisherName"
        return get_content(element=xml_element, path=path)

    def _extract_publisher_location(self, xml_element: Element) -> str:
        path = ".//Publisher/PublisherLocation"
        return get_content(element=xml_element, path=path)

    def _extract_authors(self, xml_element: Element) -> list:
        return [
            {
                "collective": get_content(author, path=".//CollectiveName"),
                "lastname": get_content(element=author, path=".//LastName"),
                "firstname": get_content(element=author, path=".//ForeName"),
                "initials": get_content(element=author, path=".//Initials"),
            }
            for author in xml_element.findall(".//Author")
        ]

    def _extract_sections(self, xml_element: Element) -> list:
        return [
            {
                "title": get_content(section, path=".//SectionTitle"),
                "chapter": get_content(element=section, path=".//LocationLabel"),
            }
            for section in xml_element.findall(".//Section")
        ]

    def _initialize_from_xml(self, xml_element: Element) -> None:
        """ Helper method that parses an XML element into an article object.
        """

        # Parse the different fields of the article
        self.pubmed_id = self._extract_pubmed_id(xml_element)
        self.title = self._extract_title(xml_element)
        self.abstract = self._extract_abstract(xml_element)
        self.copyrights = self._extract_copyrights(xml_element)
        self.doi = self._extract_doi(xml_element)
        self.isbn = self._extract_isbn(xml_element)
        self.language = self._extract_language(xml_element)
        self.publication_date = self._extract_publication_date(xml_element)
        self.authors = self._extract_authors(xml_element)
        self.publication_type = self._extract_publication_type(xml_element)
        self.publisher = self._extract_publisher(xml_element)
        self.publisher_location = self._extract_publisher_location(xml_element)
        self.sections = self._extract_sections(xml_element)

    def to_dict(self) -> dict:
        """ Helper method to convert the parsed information to a Python dict.
        """

        return {
            key: (self.__getattribute__(key) if hasattr(self, key) else None)
            for key in self.__slots__
        }

    def to_json(self) -> str:
        """ Helper method for debugging, dumps the object as JSON string.
        """

        return json.dumps(
            {
                key: (value if not isinstance(value, datetime.date) else str(value))
                for key, value in self.toDict().items()
            },
            sort_keys=True,
            indent=4,
        )
