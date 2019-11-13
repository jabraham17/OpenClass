import argparse
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time

def get_query_str():
    return 'https://webapp4.asu.edu/catalog/classlist'

def get_driver():
    # web browser
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    prefs = {"profile.managed_default_content_settings.images": 2, 
           "profile.default_content_settings.images": 2,
           "disk-cache-size": 4096}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')
    driver = webdriver.Chrome('chromedriver', chrome_options=options)
    return driver

def get_html(query_str, subject, code, section, semester):
    # get web driver
    driver = get_driver()
    driver.get(query_str)

    # add the semester
    semester_dropdown = Select(driver.find_element_by_id('term'))
    semester_dropdown.select_by_value(semester)

    # add the subject
    subject_entry = driver.find_element_by_id('subjectEntry')
    subject_entry.send_keys(subject)

    # add the class code
    classcode_entry = driver.find_element_by_id('catNbr')
    classcode_entry.send_keys(code)

    # add the section code
    section_entry = driver.find_element_by_id('keyword')
    section_entry.send_keys(section)

    # search all classes
    all_button = driver.find_element_by_id('searchTypeOpen')
    all_button.click()

    # search
    search_button = driver.find_element_by_id('go_and_search')
    search_button.click()

    # sleep to allow search to complete
    time.sleep(1)

    html_content = driver.page_source
    driver.quit()
    return html_content
    
def get_parser(html_content):
    return BeautifulSoup(html_content, 'lxml')

# true for open, false for closed
def class_status(soup):
    # find column of table
    available_section = soup.find('td', class_='availableSeatsColumnValue')
    # if availible
    return available_section is not None


def cmd_ln_tool():
    argparser = argparse.ArgumentParser(description='Check if an ASU class is open or not')
    argparser.add_argument('subject', type=str, help='Three letter subject code')
    argparser.add_argument('code', type=str, help='Three digit course code')
    argparser.add_argument('section', type=str, help='Section code')
    argparser.add_argument('-s', nargs='?', type=str, default='2201', help='The semester to search in, default is most current')
    args = argparser.parse_args()
    query = get_query_str()
    html = get_html(query, args.subject, args.code, args.section, args.s)
    soup = get_parser(html)
    status = class_status(soup)
    if status:
        print("Class is open")
    else:
        print("Class is full")


if __name__ == "__main__":
    cmd_ln_tool()