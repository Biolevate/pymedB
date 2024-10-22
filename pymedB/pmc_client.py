from typing import Optional

from .pubmed_client_base import PubMedClientBase
from .utils import extract_xml

# Base url for all queries
# /pmc/utils/oa/oa.fcgi

class PMC(PubMedClientBase):
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
            db='pmc'
        )

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


