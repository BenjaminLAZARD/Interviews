import requests


def test_query_similar_articles(query: str):
    """
    Sends a query to the FastAPI app and returns similar articles.
    """
    url = "http://127.0.0.2:8000/query/"
    params = {"query": query}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check for HTTP errors

        # Return the JSON response
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"OOps: Something Else: {err}")


# Example usage
if __name__ == "__main__":
    query = "Quel est le rapport entre Pierre Garnier et la star academy, cette emission de danse?"
    results = test_query_similar_articles(query)
    print(results)
