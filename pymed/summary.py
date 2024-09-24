import xml.etree.ElementTree as ET

class ArticleSummary:
    """ Data class that contains a PubMed article summary.
    """
    def __init__(
        self,
        doc_id: str,
        pub_date: str,
        epub_date: str,
        source: str,
        author_list: str,
        title: str,
        volume: str,
        issue: str,
        pages: str,
        article_ids: str,
        doi: str,
        full_journal_name: str,
        so: str,
    ):
        self.doc_id = doc_id
        self.pub_date = pub_date
        self.epub_date = epub_date
        self.source = source
        self.author_list = author_list
        self.title = title
        self.volume = volume
        self.issue = issue
        self.pages = pages
        self.article_ids = article_ids
        self.doi = doi
        self.full_journal_name = full_journal_name
        self.so = so

    def __repr__(self):
        return f"ArticleSummary(Title={self.title}, Id={self.doc_id}, Authors={self.author_list})"

    @classmethod
    def from_xml(cls, docsum):
        """Class method to create a ArticleSummary instance from an XML element."""
        doc_id = docsum.find('Id').text

        # Find other attributes (may be None)
        pub_date = get_item_value(docsum, 'PubDate')
        epub_date = get_item_value(docsum, 'EPubDate')
        source = get_item_value(docsum, 'Source')
        title = get_item_value(docsum, 'Title')
        volume = get_item_value(docsum, 'Volume')
        issue = get_item_value(docsum, 'Issue')
        pages = get_item_value(docsum, 'Pages')
        doi = get_item_value(docsum, 'DOI')
        full_journal_name = get_item_value(docsum, 'FullJournalName')
        so = get_item_value(docsum, 'SO')

        # Get AuthorList
        author_list = []
        author_list_elem = docsum.find(".//Item[@Name='AuthorList']")
        if author_list_elem is not None:
            for author_elem in author_list_elem.findall(".//Item[@Name='Author']"):
                author_list.append(author_elem.text)

        # Get ArticleIds
        article_ids = {}
        article_ids_elem = docsum.find(".//Item[@Name='ArticleIds']")
        if article_ids_elem is not None:
            for item in article_ids_elem.findall("Item"):
                article_ids[item.attrib['Name']] = item.text

        # Create and return a new DocSum instance
        return cls(doc_id, pub_date, epub_date, source, author_list, title, volume, issue, pages, article_ids, doi, full_journal_name, so)


def _parse_xml(xml_string: str):
    # Parse the XML string
    root = ET.fromstring(xml_string)

    # List to hold DocSum objects
    docs = []

    # Iterate over each DocSum element and create ArticleSummary object using from_xml class method
    for docsum in root.findall('DocSum'):
        doc = ArticleSummary.from_xml(docsum)
        docs.append(doc)

    return docs


def get_item_value(docsum, item_name):
    """Helper function to retrieve the text of an Item element by Name attribute."""
    item = docsum.find(f".//Item[@Name='{item_name}']")
    return item.text if item is not None else None


def _test_summary():
    xml_data = '''
    <eSummaryResult>
        <script/>
        <DocSum>
            <Id>2684823</Id>
            <Item Name="PubDate" Type="Date">2008 Nov 13</Item>
            <Item Name="EPubDate" Type="Date">2008 Nov 13</Item>
            <Item Name="Source" Type="String">Science</Item>
            <Item Name="AuthorList" Type="List">
                <Item Name="Author" Type="String">Varambally S</Item>
                <Item Name="Author" Type="String">Cao Q</Item>
            </Item>
            <Item Name="Title" Type="String">Genomic Loss of microRNA-101 Leads to Overexpression of Histone Methyltransferase EZH2 in Cancer</Item>
            <Item Name="Volume" Type="String">322</Item>
            <Item Name="Issue" Type="String">5908</Item>
            <Item Name="Pages" Type="String">1695-1699</Item>
            <Item Name="ArticleIds" Type="List">
                <Item Name="pmid" Type="String">19008416</Item>
                <Item Name="doi" Type="String">10.1126/science.1165395</Item>
            </Item>
            <Item Name="DOI" Type="String">10.1126/science.1165395</Item>
            <Item Name="FullJournalName" Type="String">Science (New York, N.Y.)</Item>
            <Item Name="SO" Type="String">2008 Nov 13;322(5908):1695-1699</Item>
        </DocSum>
        <DocSum>
            <Id>2694957</Id>
            <Item Name="PubDate" Type="Date">2008 Nov 7</Item>
            <Item Name="Source" Type="String">Science</Item>
            <Item Name="AuthorList" Type="List">
                <Item Name="Author" Type="String">Altshuler D</Item>
                <Item Name="Author" Type="String">Daly MJ</Item>
            </Item>
            <Item Name="Title" Type="String">Genetic Mapping in Human Disease</Item>
            <Item Name="Volume" Type="String">322</Item>
            <Item Name="Issue" Type="String">5903</Item>
            <Item Name="Pages" Type="String">881-888</Item>
            <Item Name="ArticleIds" Type="List">
                <Item Name="pmid" Type="String">18988837</Item>
                <Item Name="doi" Type="String">10.1126/science.1156409</Item>
            </Item>
            <Item Name="DOI" Type="String">10.1126/science.1156409</Item>
            <Item Name="FullJournalName" Type="String">Science (New York, N.Y.)</Item>
            <Item Name="SO" Type="String">2008 Nov 7;322(5903):881-888</Item>
        </DocSum>
    </eSummaryResult>
    '''

    docs = _parse_xml(xml_data)

    # Output the parsed DocSum objects
    for doc in docs:
        print(doc)

