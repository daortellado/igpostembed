from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import DesiredCapabilities
# from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time
import flask
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
import os
from flask_cors import CORS, cross_origin
# from pyvirtualdisplay import Display

#proxy
# PROXY = os.environ.get('FIXIE_URL', '')

#chromeoptions for heroku
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--window-size=1280,1000')
# chrome_options.add_argument('--allow-insecure-localhost')
# chrome_options.add_argument('--allow-running-insecure-content')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--ignore-ssl-errors')
# chrome_options.add_argument('--proxy-server=%s' % PROXY)
# capabilities = DesiredCapabilities.CHROME.copy()
# capabilities['acceptSslCerts'] = True
# capabilities['acceptInsecureCerts'] = True

# app and db
app = flask.Flask(__name__)
cors = CORS(app)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:problemplays@database-1.cqzway4arj7b.us-east-1.rds.amazonaws.com/site'
app.config['CORS_HEADERS'] = 'Content-Type'
database = SQLAlchemy(app)

class Content(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    content = database.Column(database.String(10000), default='')

class IGUrl(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    igurl = database.Column(database.String(100), default='')

database.create_all()
database.session.commit()

#virtualdisplay
# display = Display(visible=0, size=(800, 600))
# display.start()

#driver
homepage = 'https://www.instagram.com/problemplays/'
#local path not for heroku
#PATH = "C:\Program Files (x86)\chromedriver.exe"
#driver = webdriver.Chrome(PATH)
options = webdriver.ChromeOptions() 
options.add_argument("user-data-dir=C:\\Users\\rocki\\AppData\\Local\\Google\\Chrome\\User Data")
driver = webdriver.Chrome(executable_path='C:/chromedriver', chrome_options=options)
#cloud path for heroku
# chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
# driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options, desired_capabilities=capabilities)

#test
# driver.get(homepage)
# html = driver.page_source
# print(html)

#scrape most recent
def get_latest(homepage):
	driver.get(homepage)
	latest = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, ".//article/div/div/div/div/a")))
	get_latest.latest = latest.get_attribute('href')
	
#scrape embed and write to db
def scraper(url):
	driver.get(url)
	driver.implicitly_wait(10)
	button = driver.find_element_by_class_name("_abl-")
	print button
	button.click()
	try:
		embed = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, ".//div[@role = 'dialog']/div/div/div/button[5]"))) 
		time.sleep(1)
		embed.click()
		time.sleep(1)
		content = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, ".//div/div/textarea")))
		final = content.get_attribute('value')
		content_object = Content(content=final)
		database.session.add(content_object)
		database.session.commit()
	except StaleElementReferenceException:  # ignore this error
		pass  

#run the job to fetch latest post
get_latest(homepage)

#compare to DB entry and write if it is empty
if IGUrl.query.order_by(IGUrl.id.desc()).first() == None:
	first_record = IGUrl(id = 1, igurl = 'nothing yet')
	database.session.add(first_record)   
	database.session.commit()
	recent_url = IGUrl.query.order_by(IGUrl.id.desc()).first().igurl
else:
	recent_url = IGUrl.query.order_by(IGUrl.id.desc()).first().igurl

#compare latest to DB entry and run scraper + write new url if it doesn't match
if str(get_latest.latest) != str(recent_url):
	scraper(get_latest.latest)
	url_object = IGUrl(igurl=get_latest.latest)
	database.session.add(url_object)
	database.session.commit()

driver.close()
# display.stop()

#api

@app.route('/api/v1/resources/content', methods=['GET'])
@cross_origin()
def api_content():
    recent_content = Content.query.order_by(Content.id.desc()).first().content
    return jsonify(recent_content)

app.run()