import trafilatura

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    
    Args:
        url (str): The URL of the website to scrape
        
    Returns:
        str: The extracted text content from the website
    """
    # Send a request to the website
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    return text

def get_volcano_additional_info(url: str = "https://climatelinks.weebly.com/volcanoes.html") -> dict:
    """
    Fetches educational content about volcanoes from the provided URL.
    
    Args:
        url (str): URL of the educational website about volcanoes
        
    Returns:
        dict: Dictionary containing educational content about volcanoes
    """
    # Get the text content
    content = get_website_text_content(url)
    
    if not content:
        return {
            "status": "error",
            "message": "Could not extract content from the URL",
            "content": "",
            "source_url": url
        }
    
    # Return the extracted content
    return {
        "status": "success",
        "content": content,
        "source_url": url
    }