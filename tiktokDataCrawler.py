import re 
import time
import urllib.parse
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class TikTokScraper:
    USERNAMES = []
    NAMES = []
    FOLLOWINGS = []
    FOLLOWERS = []
    LIKES = []
    EMAILS = []

    CHROME_OPTIONS = Options()
    CHROME_OPTIONS.add_argument("--headless")

    URL_ENCODE = urllib.parse.quote("#")
    PATH = Service("chromedriver.exe")


    # FUNCTION TO ACCEPT INPUT AS ARGUMENTS FROM TERMINAL
    def get_arguments(self):
        parser = argparse.ArgumentParser(description="Extract account details from TikTok based on hashtag")

        parser.add_argument("-t", dest="hashtag", help="Hashtag to search")
        parser.add_argument("-c", dest="count", help="Number of results")

        args = parser.parse_args()
        return args 



    # FUNCTION TO OPEN URL IN BROWSER
    def open_url(self, hashtag):
        print("[+] Opening Browser...")
        driver = webdriver.Chrome(service=self.PATH)

        driver.get(f"https://www.tiktok.com/search?q={self.URL_ENCODE}{hashtag}")
        time.sleep(10)

        return driver 



    # FUNCTION TO EXTRACT USERNAMES FROM PAGE
    def get_account_url(self, driver, number_of_results):
        count = 0
        while True:
            div = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/div")
            anchor_tag = div.find_elements(By.TAG_NAME, "a")

            for link in anchor_tag:
                account = link.get_attribute("href")

                if account.__contains__("@") and not account.__contains__("video"):
                    self.USERNAMES.append(account)
                
                count += 1

            
            # IF CERTAIN AMOUNT OF USERNAMES HAVE BEEN COLLECTED, WRITE TO FILE AND CLOSE, ELSE LOAD MORE
            if count >= int(number_of_results):
                # BASED ON USERNAME, RUN THIS FUNCTION
                self.get_additional_info()

                # SAVE TO FILE
                self.save_to_file()

                # CLOSE THE BROWSER
                driver.quit()
                break
            else:
                print("[+] Loading more results...")
                button = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/button")
                button.click()
                self.USERNAMES.clear()
                time.sleep(5)

    

    # FUNCTION TO GET NAME, NUMBER OF FOLLOWINGS, NUMBER OF FOLLOWERS, LIKES AND EMAIL IF IT EXISTS
    def get_additional_info(self):
        i = 0
        while i < len(self.USERNAMES):
            # OPENING ANOTHER CHROME BROWSER IN HEADLESS MODE
            secondary_driver = webdriver.Chrome(options=self.CHROME_OPTIONS, service=self.PATH)

            secondary_driver.get(self.USERNAMES[i])
            time.sleep(2)

            source_page = secondary_driver.page_source

            soup = BeautifulSoup(source_page, 'html.parser')
            

            # SEARCHING FOR NAME
            print("[+] Searching additional data...")
            names = soup.find_all(class_="tiktok-qpyus6-H1ShareSubTitle e198b7gd6")
            for name in names:
                self.NAMES.append(name.string)

            # SEARCHING FOR FOLLOWING, FOLLOWER AND LIKE
            follows = soup.find_all(class_="tiktok-xeexlu-DivNumber e1awr0pt1")
            self.FOLLOWINGS.append(follows[0].strong.string)
            self.FOLLOWERS.append(follows[1].strong.string)
            self.LIKES.append(follows[2].strong.string)

            # SEARCHING FOR EMAIL
            emails = soup.find_all(class_="tiktok-b1wpe9-H2ShareDesc e1awr0pt3")
            for email in emails:
                email = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", email.string)
                if len(email) != 0:
                    self.EMAILS.append(email[0])
                else:
                    self.EMAILS.append(None)
        
            secondary_driver.quit()
            i += 1


    # SAVE DETAILS TO FILE
    def save_to_file(self):
        print("[+] Saving to file...")
        with open("usernames.txt", "w", encoding="utf-8") as file:
            for (name,user,following,follower,like,email) in zip(self.NAMES, self.USERNAMES, self.FOLLOWINGS, self.FOLLOWERS, self.LIKES, self.EMAILS):
                file.write(str(name) + "\t\t\t" + str(user) + "\t\t\t" + str(following) + "\t\t\t" + str(follower) + "\t\t\t" + str(like) + "\t\t\t" + str(email))
                file.write("\n\n")
            # for username in self.USERNAMES:
            #     file.write("https://www.tiktok.com" + str(username))
            #     file.write("\n")

        print("[+] DONE!")


obj = TikTokScraper()

args = obj.get_arguments()
driver = obj.open_url(args.hashtag)
obj.get_account_url(driver, args.count) 