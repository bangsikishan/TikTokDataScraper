import time
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class TikTokScraper:
    USERNAMES = []

    URL_ENCODE = urllib.parse.quote("#")
    PATH = Service("D:\TestFolder\chromedriver.exe")
    URL = f"https://www.tiktok.com/search?q={URL_ENCODE}mrrobot"


    # FUNCTION TO OPEN URL IN BROWSER
    def open_url(self):
        print("[+] Opening Browser...")
        driver = webdriver.Chrome(service=self.PATH)

        driver.get(self.URL)
        time.sleep(15)

        return driver 


    # FUNCTION TO EXTRACT USERNAMES FROM PAGE
    def get_username(self, driver):
        source_page = driver.page_source

        time.sleep(2)

        print("[+] Parsing HTML page...")
        document = BeautifulSoup(source_page, "html.parser")


        # FIND ALL THE ANCHOR TAGS IN THE SOURCE PAGE
        links = document.find_all('a', href=True)
        count = 0
        for link in links:
            # GET LINKS FROM A ANCHOR TAG
            username = link["href"]

            # CHECK FOR CORRECT URL WITH USERNAME 
            if username[:2] == "/@":
                self.USERNAMES.append(username)
                count += 1
        
        # IF CERTAIN AMOUNT OF USERNAMES HAVE BEEN COLLECTED, WRITE TO FILE AND CLOSE, ELSE LOAD MORE
        if count >= 20:
            with open("usernames.txt", "w", encoding="utf-8") as file:
                for user in self.USERNAMES:
                    file.write("https://www.tiktok.com" + str(user))
                    file.write("\n\n")

            # CLOSE THE BROWSER
            print("[+] DONE!")
            driver.quit()
        else:
            print("[+] Loading more results...")
            button = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button")
            button.click()
            time.sleep(5)
        

obj = TikTokScraper()

driver = obj.open_url()
obj.get_username(driver)