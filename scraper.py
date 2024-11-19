# Load libraries
import json, datetime, time, os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Download and install the Chrome driver
firefox_service = FirefoxService(GeckoDriverManager().install())

firefox_options = webdriver.FirefoxOptions()
firefox_options.page_load_strategy = 'eager'
firefox_options.add_argument('--headless')

# Record the current time
current_timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

# Hard-code in the URL we want
# TODO: Soften this so we can get the information about any movie
movie_url = 'https://www.rottentomatoes.com/m/the_marvels'

def rotten_tomatoes_soup(url):
    """
    A function for retrieving a website and converting its content into BeautifulSoup.

    Takes `url` as a string and returns a Soup object.
    """
    # Launch the driver
    driver = webdriver.Firefox(options = firefox_options, service=firefox_service)
    
    # Make the request
    driver.get(url)

    # Wait a few seconds for the page to load completely
    time.sleep(3)
    
    # Get source
    raw = driver.page_source.encode('utf-8')
    
    # Convert to Soup
    soup = BeautifulSoup(raw,features='html.parser')
    
    # Quit the driver
    driver.quit()

    return soup

def parse_data(soup,ts):
    """
    A function for converting parsing the Soup of a Rotten Tomatoes page into a dictionary.

      soup - A BeautifulSoup object, typically created by `rotten_tomatoes_soup`
      tag - A string identifying a tag to be searched in the Soup
      ts - A string with the ISO-8601 timestamp

    Returns a dictionary with "timestamp", "average_rating", "liked_count", "not_liked_count",
      "rating_count", "review_count", and "value" keys.
    """
    
    details_d = {}
    details_d['timestamp'] = ts
    details_d['average_rating'] = soup.find('rt-text',{'slot':'criticsScore'}).text
    details_d['reviews_count'] = soup.find('rt-link',{'slot':'criticsReviews'}).text.strip()
    details_d['average_rating'] = soup.find('rt-text',{'slot':'audienceScore'}).text
    details_d['reviews_count'] = soup.find('rt-link',{'slot':'audienceReviews'}).text.strip()
    return details_d

def update_data(filename,data):
    """
    A function for appending a dictionary to a list of dictionaries in a JSON file.

      filename - The name of the file to create/update
      data - The dictionary to be appended to the file
    """
    if filename in os.listdir():

        with open(filename,'r',encoding='utf-8') as f:
            data_list = json.load(f)

        data_list.append(data)

        with open(filename,'w',encoding='utf-8') as f:
            json.dump(data_list,f)

    else:
        with open(filename,'w',encoding='utf-8') as f:
            json.dump([data],f)


def main():
    """
    Retrieve the content from the page, parse the data into critics and audience responses,
      and create/update the JSON files for critics and audience.
    """
    soup = rotten_tomatoes_soup(movie_url)
    data = parse_data(soup=soup,ts=current_timestamp)
    
    update_data('data.json',data)

if __name__ == "__main__":
    main()