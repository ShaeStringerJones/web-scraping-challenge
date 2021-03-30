from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time 

def init_browser():    
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    return browser

def scrape():

    browser = init_browser()

    #scrape Nasa site for first headline
    #---------------------------------------#
    #URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    time.sleep(1)

    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')

    # Retrieve all elements that contain header information
    headers = soup.find_all('div', class_='content_title')
    paragraphs = soup.find_all('div', class_='article_teaser_body')

    news_title = headers[1].text
    news_p = paragraphs[0].text
    
    #quit browser
    browser.quit() 


    #--------MARS Image Scrape--------------#

    #URL of page to be scraped
    browser = init_browser()
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)
    time.sleep(1)

    browser.links.find_by_partial_text('FULL IMAGE').click()

    html = browser.html
    soup = bs(html,'html.parser')


    results = soup.find('img', class_='fancybox-image')['src']


    image_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{results}'

    #quit browser
    browser.quit() 


    #--------MARS Facts--------------#

    browser = init_browser()

    #facts url
    facts_url = 'http://space-facts.com/mars/'

    # Use Panda's `read_html` to parse the url
    mars_facts = pd.read_html(facts_url)

    # Find the mars facts DataFrame in the list of DataFrames as assign it to `mars_df`
    mars_df = mars_facts[0]

    # Assign the columns `['Description', 'Value']`
    mars_df.columns = ['Description','Values']


    # Save html code to folder Assets
    marshtml = mars_df.to_html(index=False)

    text_file = open("marsfacts.html", "w")
    text_file.write(marshtml)
    text_file.close()

    #--------MARS Hemispheres--------------#
    # Visit hemispheres website through splinter module 
    hem_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hem_url)

    #html 
    html_hem = browser.html

    #parse with Beautiful Soup
    soup = bs(html_hem, 'html.parser')

    #get items that have mars hemisphere information
    items = soup.find_all('div', class_='item')

    #empty list for urls
    listings =[]

    #base url
    hem_base_url = 'https://astrogeology.usgs.gov'

    #for loop to collect urls

    for i in items:
        #store title
        title = i.find('h3').text
        
        #store link that opens full image
        partial_img_url = i.find('a', class_='itemLink product-item')['href']
        
        #visit link that contains full image
        browser.visit(hem_base_url + partial_img_url)
    
        #HTML Object of full screen
        partial_img_html = browser.html
        
        #Parse with BS
        soup_hem = bs(partial_img_html, 'html.parser')
        
        #Full image souce
        full_img = hem_base_url + soup_hem.find('img', class_='wide-image')['src']
        
        #Append into a list of dictionaries
        listings.append({"title": title, "full_img": full_img})
    
   
    
    browser.quit()

    mars_dict = {}
    mars_dict['news_title'] = news_title,
    mars_dict['news_p'] = news_p,
    mars_dict['image_url'] = image_url,
    mars_dict['mars_table'] = marshtml,
    mars_dict['hemisphere_list'] = listings

    return mars_dict
