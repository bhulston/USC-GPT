from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import requests
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

## Scraper ##
URL = "https://classes.usc.edu/term-20241/"

req = requests.get(URL)

content = req.text

soup = BeautifulSoup(content)
raw=soup.findAll('span', class_ = 'prefix')
raw[0]


codes = []
urls = []

## Get the list of program codes ##
for span in raw:
  code = span.text
  codes.append(code)
  urls.append(URL + 'classes/' + code + '/')

print("Program codes grabbed")
## Function for extracting course information ##
def extract_info(soup):
    # 1. Catalogue (description of class) and class info
    catalogue_div = soup.find('div', class_='catalogue')
    catalogue = catalogue_div.text if catalogue_div else 'Not available'

    # Find the anchor tag with class 'courselink'
    course_link = soup.find('a', class_='courselink')

    # Extracting course ID (within <strong> tag)
    course_id_tag = course_link.find('strong')
    course_id = course_id_tag.get_text(strip=True) if course_id_tag else 'Not available'

    # Extracting course name (text after <strong> and before <span>)
    course_name = course_id_tag.next_sibling if course_id_tag else 'Not available'

    # Extracting units (within <span class="units">)
    units_span = course_link.find('span', class_='units')
    units = units_span.get_text(strip=True) if units_span else 'Not available'


    # 2. Prerequisites and Restrictions
    prerequisites_li = soup.find('li', class_='prereq')
    prerequisites = prerequisites_li.text if prerequisites_li else 'Not available'

    restrictions_li = soup.find('li', class_='restriction')
    restrictions = restrictions_li.text if restrictions_li else 'Not available'

    # 3. Class Section
    section_td = soup.find('td', class_='section')
    class_section = section_td.text if section_td else 'Not available'

    # 4. Time, Days, and Class Type
    time_td = soup.find('td', class_='time')
    time = time_td.text if time_td else 'Not available'

    days_td = soup.find('td', class_='days')
    days = days_td.text if days_td else 'Not available'

    type_td = soup.find('td', class_='type')
    class_type = type_td.text if type_td else 'Not available'

    # 5. Instructor
    instructor_td = soup.find('td', class_='instructor')
    instructor = instructor_td.text if instructor_td else 'Not available'

    return course_id, course_name, units, catalogue, prerequisites, restrictions, class_section, time, days, class_type, instructor

## Collect Information ##

classes = []

for i in range(len(urls)):
  print("checking url:", urls[i])
  req = requests.get(urls[i])
  content = req.text
  soup = BeautifulSoup(content)
  raw=soup.findAll('div', class_ = 'course-info expandable')
  for clas in raw:
    class_id, class_name, units, cat, pre, rest, section, time, days, class_type, instructor = extract_info(clas)
    classes.append((codes[i], urls[i], class_id, class_name, cat, units, pre, rest, section, time, days, class_type, instructor))

df = pd.DataFrame(classes, columns=['Program Code', 'Program URL', 'Class ID', 'Class Name', 'Catalogue', 'Units', 'Prerequisites', 'Restrictions', 'Class Section', 'Time', 'Days', 'Class Type', 'Instructor'])
print("Dataframe built")
df.to_csv("course_data.csv", index = False)
del classes
