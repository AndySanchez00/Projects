from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests
import time
from datetime import datetime
import csv

URL= '#' #ratemyprofessor link here
driver = webdriver.Chrome()
driver.get(URL)

try: #closes popups
    driver.find_element(By.XPATH, "//div[starts-with(@class, 'FullPageModal__')]//button").click()
    driver.find_element(By.XPATH, "//a[@id='bx-close-inside-1177612']").click()
except:
    pass

while(True): #searches for the load more ratings button
    try:                                                        
        loadmore = driver.find_element(By.XPATH, "//div[@class= 'react-tabs__tab-panel react-tabs__tab-panel--selected']/button[@class='Buttons__Button-sc-19xdot-1 PaginationButton__StyledPaginationButton-txi1dr-1 eUNaBX']")
        driver.execute_script("arguments[0].scrollIntoView();",loadmore)
        ActionChains(driver)\
            .scroll_by_amount(0, -100)\
            .perform()
        time.sleep(1)
        loadmore.click()
        time.sleep(1)
    except NoSuchElementException: #once the button no longer exists, gras the html and puts it in pagesource
        print("Reached bottom of page")
        pagesource = driver.page_source
        driver.close()
        break

#converts datascraped into requests for interaction with beautifulSoup        
response = requests.models.Response() 
response._content = pagesource.encode('utf-8')
response.status_code= 200
response.headers = {'Content-Type': 'text/html'}
Soup1 = BeautifulSoup(response.content, "html.parser")
Soup2 = BeautifulSoup(Soup1.prettify(),"html.parser")

#Gets professors name
prof_name = Soup2.find('title').get_text().strip() 
prof_name = prof_name.split(" ")

professor = ''
for i in prof_name:
    if i == 'at':
        break
    professor += i + " "

professor.strip() 

#Retrieves professors stats
feedback_numbers = Soup2.find_all('div',{'class': 'FeedbackItem__FeedbackNumber-uof32n-1 kkESWs'})

rating = Soup2.find('div',{'class': 'RatingValue__Numerator-qw8sqy-2 liyUjw'}).get_text().strip()
takeAgain = feedback_numbers[0].text.strip()[:2]
Difficulty= feedback_numbers[1].text.strip()
scrapedate =  datetime.today()
scrapedate = scrapedate.strftime("%Y-%m-%d")

#creates the CSV for professor reviews with the following header
header = ['professor','TakeAgain%','Difficulty','Rating','Date','','course', 'Review Date', 
'Quality', 'Difficulty', 'For Credit', 'Attendance', 'Would Take Again', 'Grade', 'Textbook', 
'Online Class', 'Comment']

with open(f'C:/directory_here/{professor}Reviews.csv','w',newline='',encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(header)

#function to convert date for excel to read it properly
def convert_date(date_string):
    # Remove the 'th', 'rd', or 'st' from the day
    day = date_string.split(' ')[1][:-3]
    # Get the month abbreviation from the input string
    month_abbr = date_string.split(' ')[0][:3]
    # Get the year from the input string
    year = date_string.split(' ')[2]
    # Combine the day, month, and year into a string
    date_str = f"{month_abbr}-{day}-{year}"
    # Convert the string to a datetime object and then back to a string in the desired format
    date_obj = datetime.strptime(date_str, '%b-%d-%Y')
    date_obj = date_obj.strftime("%Y-%m-%d")
    return date_obj

#retrieves review data for exporting into csv file
reviews = Soup2.find_all('div',{'class': 'Rating__StyledRating-sc-1rhvpxz-1 jcIQzP'})

counter = 0
#reads review data, removes unnecessary tags, exports to CSV
for i in range(len(reviews)):
    #replaces previous value with NULL incase of no response in review
    review_for_credit = 'NULL'
    review_attendance = 'NULL'
    review_takeAgain  = 'NULL'
    review_grade      = 'NULL'
    review_textbook   = 'NULL'
    review_online     = 'NULL'
    review_comment    = 'NULL'
    reviews_process = reviews[i].get_text().strip()
    reviews_process = reviews_process.split('\n')

    review = [item for item in reviews_process if item.strip() != '' and 
    item.strip() not in ['😎','😖','😐','awesome','awful','average',':',
    'Participation matters','Group projects','GROUP PROJECTS','PROJECTS','CARES ABOUT STUDENTS',
    'So many papers','Amazing lectures','Caring','Inspirational','Respected',
    'Clear grading criteria','Hilarious',"Skip class? You won't pass.",'Gives good feedback',
    'Graded by few things','GRADED BY FEW THINGS','Accessible outside class',
    'EXTRA CREDIT', 'Online Savvy', 'LECTURE HEAVY','ACCESSIBLE OUTSIDE CLASS', 'Test heavy',
    'Get ready to read','Would take again','TEST HEAVY','Participation matters',
    'LOTS OF HOMEWORK','Lots of homework','Tough grader','Tough Grader',
    'Lecture heavy','BEWARE OF POP QUIZZES','Reviewed'] and 
    'Reviewed: ' not in item.strip() and item.strip().isdigit() == False ]
    
    for i,j in enumerate(review):
        review[i] = j.strip()
    
    #removes repeated course and date values in list
    review = [item for i, item in enumerate(review) if not (i == 6) and not (i == 7)]
    
    #goes through list and gives values to variables
    for i,j in enumerate(review):
        
        course = review[0]
        review_date = review[1]
        review_quality = review[3]
        review_difficulty = review[5]
        if j == 'For Credit' or j== 'For Credit:':
            review_for_credit = review[i+1]
        if j == 'Attendance' or j== 'Attendance:':
            review_attendance = review[i+1]
        if j == 'Would Take Again' or j== 'Would Take Again:':
            review_takeAgain  = review[i+1]
        if j == 'Grade' or j== 'Grade:':
            review_grade      = review[i+1]
        if j == 'Textbook' or j== 'Textbook:':
            review_textbook   = review[i+1]
        if j == 'Online Class' or j== 'Online Class:':
            review_online     = review[i+1]
        review_comment    = review[i]
    
    #ignores cases where coursename was not written properly
    if len(course) > 9:
            continue
    
    fixed_date = review_date
    fixed_date = convert_date(fixed_date)
    
    
    review_dict = {'professor':professor,'takeAgain%':takeAgain,'Total Difficulty':Difficulty,
    'Total Rating':rating,'Scrape Date':scrapedate,'blank':' ','course': course,
    'review_date': fixed_date,'review_quality': review_quality,'review_difficulty':review_difficulty,
    'review_for_credit':review_for_credit, 'review_attendance':review_attendance, 
    'review_takeAgain':review_takeAgain, 'review_grade':review_grade, 'review_textbook':review_textbook,
    'review_online': review_online,'review_comment':review_comment}
    
    #only prints professors overall stats on the first row
    if counter == 1:
        review_dict = {'professor':'','takeAgain%':'','Total Difficulty':'','Total Rating':'',
        'Scrape Date':'','blank':' ','course': course, 'review_date': fixed_date,'review_quality': review_quality,
        'review_difficulty':review_difficulty, 'review_for_credit':review_for_credit, 
        'review_attendance':review_attendance, 'review_takeAgain':review_takeAgain, 'review_grade':review_grade, 
        'review_textbook':review_textbook, 'review_online': review_online,'review_comment':review_comment}
    
    #appends data to 
    data = review_dict.values()
    with open(f'C:/directory_here/{professor}Reviews.csv','a+', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(data)
        counter = 1
