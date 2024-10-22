import itertools

import xml.etree.ElementTree as xml

from typing import Optional

from .helpers import batches
from .article import PubMedArticle
from .book import PubMedBookArticle
from .summary import ArticleSummary
from .pubmed_client_base import PubMedClientBase
from .utils import extract_xml

class PubMed(PubMedClientBase):
    """ Wrapper around the PubMed API [pubmed db].
    """

    def __init__(
        self,
        tool: str = "my_tool",
        email: str = "my_email@example.com",
        api_key: Optional[str] = None
    ) -> None:

        super().__init__(
            tool=tool,
            email=email,
            api_key=api_key,
            db='pubmed'
        )

    def query(self, query: str, max_results: int = 100):
        """ Method that executes a query agains the GraphQL schema, automatically
            inserting the PubMed data loader.

            Parameters:
                - query     String, the GraphQL query to execute against the schema.

            Returns:
                - result    ExecutionResult, GraphQL object that contains the result
                            in the "data" attribute.
        """
        if (self.parameters['db'] != 'pubmed'):
            raise Exception(f"can query only 'pubmed' database, your database: {self.parameters['db']}")
        # Retrieve the article IDs for the query
        article_ids = self.get_article_ids(query=query, max_results=max_results)

        # Get the articles themselves
        articles = list(
            [
                self.get_articles(article_ids=batch)
                for batch in batches(article_ids, 250)
            ]
        )

        # Chain the batches back together and return the list
        return itertools.chain.from_iterable(articles)
    
    def get_articles(self, article_ids: list):
        """ Helper method that batches a list of article IDs and retrieves the content.

            Parameters:
                - article_ids   List, article IDs.

            Returns:
                - articles      List, article objects.
        """

        if (self.parameters['db'] != 'pubmed'):
            raise Exception(f"can get articles of only 'pubmed' database, your database: {self.parameters['db']}")
        # Get the default parameters
        parameters = self.parameters.copy()
        parameters["id"] = article_ids

        # Make the request
        response = self._get(
            url="/entrez/eutils/efetch.fcgi", parameters=parameters, output="xml"
        )

        # Parse as XML
        root = xml.fromstring(response)

        # Loop over the articles and construct article objects
        for article in root.iter("PubmedArticle"):
            yield PubMedArticle(xml_element=article)
        for book in root.iter("PubmedBookArticle"):
            yield PubMedBookArticle(xml_element=book)

    def get_articles_summaries(self, article_ids: list[str]):
        """ Helper method to retrieve the article summaries for an ids list.

            Parameters:
                - article_ids                 List[Str], list of article ids.

            Returns:
                - articles_summaries   List[ArticleSummary], list of article summaries.
        """

        # Get the default parameters
        parameters = self.parameters.copy()
        parameters["id"] = article_ids

        # Make the request
        response = self._get(
            url="/entrez/eutils/esummary.fcgi", parameters=parameters, output="xml"
        )

        root = xml.fromstring(response)
        
        for docsum in root.findall('DocSum'):
            yield ArticleSummary.from_xml(docsum=docsum)

    def get_article_download_url(self, article_id: str, accepted_formats: list[str] = ['pdf', 'tgz']):
        if self.parameters["db"] != "pmc":
            raise Exception(f"Can't download Pubmed Documents from {self.parameters["db"]} database!\n list of available databases: ['pmc']")
        
        parameters = self.parameters.copy()
        parameters["id"] = article_id

        res = self._get("/pmc/utils/oa/oa.fcgi", parameters=parameters, output="xml")
        root = extract_xml(res)
        if root is None: return None

        err = root.find("error")
        if not (err is None): return None
        
        record = root.find(".//record")

        for accepted_format in accepted_formats:
            link = record.find(f".//link[@format='{accepted_format}']")
            if link is not None:
                return link.attrib['href']
        
        return None

    def query_article_download_urls(self, query: str, max_results: int = 100, accepted_formats: list[str] = ['pdf', 'tgz']):
        if self.parameters["db"] != "pmc":
            raise Exception(
                f"Can't download Pubmed Documents from {self.parameters["db"]} database!\n list of available databases: ['pmc']"
            )
        
        articles_ids = self.get_article_ids(
            query=query,
            max_results=max_results
        )

        return [self.get_article_download_url(article_id=article_id, accepted_formats=accepted_formats) for article_id in articles_ids]


