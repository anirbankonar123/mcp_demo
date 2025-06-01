from tavily import TavilyClient
import json


class WebExtractor(object):

    def __init__(self):
        global tavily_client
        tavily_client = TavilyClient(api_key="")

    def get_response(self,query):
        response = tavily_client.search(query)

        result = response["results"][0]['url'] + ": " + response["results"][0]['content']
        return result