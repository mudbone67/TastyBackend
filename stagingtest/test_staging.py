import requests
import json
import pymysql
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import xml.etree.ElementTree as ET
import unittest
import xmlrunner

# Parse the XML configuration file
tree = ET.parse('staging_test_config.xml')
root = tree.getroot()

# Retrieve the values from the XML
frontendurl = root.find('frontendurl').text
backendurl = root.find('backendurl').text
dbHost = root.find('dbHost').text
dbPort = root.find('dbPort')
dbName = root.find('dbName').text
dbUser = root.find('dbUser').text
dbPassword = root.find('dbPassword').text

#Frontend Check
class FrontendCheckTestCase(unittest.TestCase):
    def test_frontend(self):
        try:
            response = requests.get(frontendurl)
            self.assertEqual(response.status_code, 200, "Frontend returned an error.")
        except requests.exceptions.RequestException as e:
            self.fail("An error occurred for the Frontend: " + str(e))

class BackendCheckTestCase(unittest.TestCase):
    def test_backend(self):
        try:
            response = requests.get(backendurl + ':7200/python')
            self.assertEqual(response.status_code, 200, "Backend returned an error.")
        except requests.exceptions.RequestException as e:
            self.fail("An error occurred for the Backend: " + str(e))

class DBCheckTestCase(unittest.TestCase):
    def test_db(self):
        try:
            conn = pymysql.connect(
                host=dbHost,
                port=dbPort,
                database=dbName,
                user=dbUser,
                password=dbPassword
            )
            self.assertTrue(conn.is_connected(), "Database is not running.")
            conn.close()
        except pymysql.Error as e:
            self.fail("An error occurred while connecting to the database: " + str(e))

class FrontendBackendCheckTestCase(unittest.TestCase):
    def setUp(self):
        #remote_url = "http://selenchrome.adahckfdc0g4bkbv.eastus.azurecontainer.io:4444"
        #remote_url = "http://192.168.2.130:4444/wd/hub"
        #chrome_options = webdriver.ChromeOptions()
        #chrome_options.set_capability("browserVersion", "67")
        #chrome_options.set_capability("platformName", "Windows XP")
        #self.driver = webdriver.Remote(command_executor=remote_url, options=chrome_options)
        #self.driver = webdriver.Chrome(options=webdriver.ChromeOptions().add_argument('--no-sandbox'))
        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_capability("browserVersion", "67")
        chrome_options.set_capability("platformName", "Windows XP")
        driver = webdriver.Remote(
        command_executor='http://192.168.2.130:4444/',
        options=chrome_options
        )
        driver.get("http://www.google.com")
        driver.quit()

    def tearDown(self):
        self.driver.quit()

    def test_frontend_backend(self):
        try:
            self.driver.get(frontendurl + '/pythontest')
            response_text = self.driver.page_source
            self.assertEqual(self.driver.execute_script('return document.readyState'), 'complete', "Frontend-Backend connection error.")
            self.assertIn("Hello", response_text, "Server returned an error or 'Hello world' was not returned.")
        except Exception as e:
            self.fail("An error occurred for the Frontend-Backend connection: " + str(e))

class BackendDBCheckTestCase(unittest.TestCase):
    def test_backend_db(self):
        try:
            response = requests.get(backendurl+':7200/recipes/num/1')
            self.assertEqual(response.status_code, 200, "Backend-DB returned an error.")
        except requests.exceptions.RequestException as e:
            self.fail("An error occurred for the Backend-DB connection: " + str(e))

if __name__ == '__main__':
    test_cases = [
        FrontendCheckTestCase,
        BackendCheckTestCase,
        DBCheckTestCase,
        FrontendBackendCheckTestCase,
        BackendDBCheckTestCase
    ]

    # Create a test suite
    test_suite = unittest.TestSuite()
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)

    # Run the test suite with the XMLTestRunner to generate JUnit XML reports
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    runner.run(test_suite)