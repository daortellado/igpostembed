from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import flask
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
import sqlite3
from flask_cors import CORS, cross_origin

# app and db
app = flask.Flask(__name__)
cors = CORS(app)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['CORS_HEADERS'] = 'Content-Type'
database = SQLAlchemy(app)

class Content(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    content = database.Column(database.String(), default='')
database.create_all()
database.session.commit()

#driver
homepage = 'https://www.instagram.com/problemplays/'
PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

#scrape most recent
def get_latest(homepage):
	driver.get(homepage)
	latest = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, ".//article/div/div/div/div/a")))
	latest = latest.get_attribute('href')

#scrape embed and write to db
def scraper(url):
	driver.get(url)
	button = driver.find_element_by_tag_name("button")
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

get_latest(homepage)
scraper(latest)

driver.quit()

@app.route('/api/v1/resources/content', methods=['GET'])
@cross_origin()
def api_content():
    recent_content = Content.query.order_by(Content.id.desc()).first().content
    return jsonify(recent_content)

app.run()