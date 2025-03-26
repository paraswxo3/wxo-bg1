import requests
import os
import time
from urllib.parse import urlparse
from googlesearch import search

def search_and_download_pdfs(search_query, download_folder, max_results=10):
    """
    Search for PDFs related to a specific query and download them to a local folder.
    Uses googlesearch-python for more reliable search results.
    
    Args:
        search_query (str): The query to search for
        download_folder (str): The folder to download PDFs to
        max_results (int): Maximum number of PDFs to download
    """
    # Create download directory if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Format the search query to specifically look for PDFs
    formatted_query = f"{search_query} filetype:pdf"
    
    # Use a realistic user agent to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Searching for: {formatted_query}")
    
    # Use googlesearch-python to get search results
    pdf_links = []
    try:
        # The search function returns URLs directly
        for url in search(formatted_query, num_results=max_results*2):  # Request more results as some might not be PDFs
            if url.lower().endswith('.pdf'):
                pdf_links.append(url)
                if len(pdf_links) >= max_results:
                    break
            time.sleep(2)  # Sleep between searches to avoid being blocked
    except Exception as e:
        print(f"Search error: {str(e)}")
        return
    
    print(f"Found {len(pdf_links)} PDF links")
    
    downloaded_count = 0
    for i, pdf_url in enumerate(pdf_links):
        try:
            # Get the PDF filename from the URL
            parsed_url = urlparse(pdf_url)
            filename = os.path.basename(parsed_url.path)
            
            # Ensure filename is valid and ends with .pdf
            if not filename or not filename.lower().endswith('.pdf'):
                filename = f"bank_guarantee_doc_{i+1}.pdf"
            
            # Create the full path for saving the file
            save_path = os.path.join(download_folder, filename)
            
            # Download the PDF
            print(f"Downloading: {pdf_url}")
            pdf_response = requests.get(pdf_url, headers=headers, timeout=30)
            
            if pdf_response.status_code == 200:
                # Check if content is actually a PDF
                content_type = pdf_response.headers.get('Content-Type', '').lower()
                if 'pdf' in content_type or pdf_response.content[:4] == b'%PDF':
                    with open(save_path, 'wb') as f:
                        f.write(pdf_response.content)
                    print(f"Downloaded: {filename}")
                    downloaded_count += 1
                else:
                    print(f"Skipped: {pdf_url} - Not a valid PDF file")
            else:
                print(f"Failed to download: {pdf_url} - Status code: {pdf_response.status_code}")
                
            # Sleep to avoid overloading the server
            time.sleep(2)
            
        except Exception as e:
            print(f"Error downloading {pdf_url}: {str(e)}")
    
    print(f"\nDownload complete. {downloaded_count} PDF files downloaded to {download_folder}")

if __name__ == "__main__":
    search_query = "Bank Guarantee document samples"
    download_folder = "bank_guarantee_pdfs"
    max_results = 5  # Adjust as needed
    
    search_and_download_pdfs(search_query, download_folder, max_results)