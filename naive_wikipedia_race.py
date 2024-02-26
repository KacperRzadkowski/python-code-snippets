from __future__ import annotations
from pprint import pprint
from urllib.parse import urljoin, urlparse
import requests
import re


class Node:
    def __init__(self, url, parent):
        self.url = url
        self.parent = parent

    def __str__(self):
        string = self.url
        if(self.parent is not None):
            string += " -> "+str(self.parent)+"\n"
        return string
      

def get_html(url: str, params: dict | None = None, output: str | None = None) -> str | None:
    """Get an HTML page and return its contents.

    Args:
        url (str):
            The URL to retrieve.
        params (dict, optional):
            URL parameters to add.
        output (str, optional):
            (optional) path where output should be saved.
    Returns:
        html (str):
            The HTML of the page, as text.
    """
    #TODO error handling 
    # GET request to url
    response = requests.get(url, params= params)
    # get the text from the response
    html_str = response.text
    # Write to file if requested
    if output:
        file_contents = url+"\n"+html_str
        with open(output,"w+") as output_file:
            output_file.write(file_contents)
    # return the html string
    return html_str


def find_articles(html: str, output: str | None = None) -> set[str]:
    """Finds all the wiki articles inside a html text. Make call to find urls, and filter
    arguments:
        - text (str) : the html text to parse
        - output (str, optional): the file to write the output to if wanted
    returns:
        - (Set[str]) : a set with urls to all the articles found
    """
    # call find_urls and filter out the non-article urls
    urls = find_urls(html)
    pattern = re.compile(r'https://[a-z\.]*wikipedia\.org/wiki')
    articles = set()
    # iterate over the urls and filter out the non-article urls
    for url in urls:
        parsed_ulr = urlparse(url)
        if(":" in parsed_ulr.path):
            continue
        if(pattern.search(url)):
            articles.add(url)
    # Write to file if wanted
    if output:
        with open(output,"w+") as out_file:
            out_file.write("\n".join(articles))
    return articles


def find_path(start: str, finish: str) -> list[str]:
    """Find the shortest path from `start` to `finish`

    Arguments:
      start (str): wikipedia article URL to start from
      finish (str): wikipedia article URL to stop at

    Returns:
      urls (list[str]):
        List of URLs representing the path from `start` to `finish`.
        The first item should be `start`.
        The last item should be `finish`.
        All items of the list should be URLs for wikipedia articles.
        Each article should have a direct link to the next article in the list.
    """
    path = []
    if(start == finish):
        return path
    queue = [Node(start, None)]
    visited = set()
    node = None
    while(len(queue) > 0):
        if(queue[0] not in visited):
            pprint(f"{queue[0].url}  {len(visited)}")    
            if(queue[0].url == finish):
                node = Node(finish, queue[0])
                break
            for url in find_articles(get_html(queue[0].url)):
                if(url not in visited and filter_url(url)):
                    queue.append(Node(url, queue[0]))
            visited.add(queue[0])
        queue.pop(0)
    if(node is None):
        print("No path found")
    while(node is not None):
        path.append(node.url)
        node = node.parent
    path.reverse()
    assert path[0] == start
    assert path[-1] == finish
    return path


def filter_url(url : str) -> bool:
    if(url.startswith("https://en.wikipedia.org/wiki/")):
        return True
    else:
        return False

if __name__ == "__main__":
    start = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    # finish = "https://en.wikipedia.org/wiki/Peace"
    finish = "https://en.wikipedia.org/wiki/Automation"
    find_path(start, finish)
