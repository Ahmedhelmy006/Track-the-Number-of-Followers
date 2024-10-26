import time as t
from bs4 import BeautifulSoup
import pandas as pd
from CookiesCleaner import CookiesCleaner
from LinkedIn import NormalPageView as NPV
from LinkedIn import ProfileView as PV
import json
import os

class InfoParser:
    def __init__(self, context):
        self.context = context

    def scrap_info(self, link):
        page = self.context.new_page()
        page.goto(link, timeout=1200000000)
        t.sleep(5)
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        page.close()
        return self._parse_info(soup)

class AccountInfoParser(InfoParser):
    def _parse_info(self, soup):
        number_of_followers = soup.find('li', class_=PV.number_of_followers_class) 
        if number_of_followers:
            raw_text = number_of_followers.get_text(strip=True).replace('followers', '').strip()
            return FollowersTracker.clean_text(raw_text)
        return 'Not Found'

class PageInfoParser(InfoParser):
    def _parse_info(self, soup):
        number_of_followers = soup.find('p', class_=NPV.number_of_followers_class)  
        if number_of_followers:
            return FollowersTracker.clean_text(number_of_followers.get_text(strip=True))
        return 'Not Found'

class FollowersTracker:
    def __init__(self, context, accounts_file, pages_file):
        self.context = context
        self.accounts = self.read_excel(accounts_file)
        self.pages = self.read_excel(pages_file)

    def login(self):
        username = os.getenv("LINKEDIN_USERNAME")
        password = os.getenv("LINKEDIN_PASSWORD")
        page = self.context.new_page()
        page.goto("https://www.linkedin.com/login", timeout=60000)
        page.fill('input[name="session_key"]', username)
        page.fill('input[name="session_password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        self._update_cookies_file()

        page.close()
        print("Login successful, cookies saved.")

    def _update_cookies_file(self):
        new_cookies = self.context.cookies()
        cleaned_cookies = CookiesCleaner.clean_cookies(new_cookies)
        cookies_path = os.path.join(os.getcwd(), 'cookies.json')
        with open(cookies_path, 'w') as file:
            json.dump(cleaned_cookies, file, indent=4)
        print(f"Cookies updated at: {cookies_path}")

    def read_excel(self, file_path):
        return pd.read_excel(file_path)

    def get_links(self):
        account_links = self.accounts['Link'].tolist()
        page_links = self.pages['Link'].tolist()
        return account_links, page_links

    def scrap_info(self):
        account_parser = AccountInfoParser(self.context)
        page_parser = PageInfoParser(self.context)
        account_links, page_links = self.get_links()

        followers_data = []

        for link in account_links:
            info = self._scrap_with_retry(account_parser, link)
            followers_data.append(info)
            print(f"Account info: {info}")

        for link in page_links:
            info = self._scrap_with_retry(page_parser, link)
            followers_data.append(info)
            print(f"Page info: {info}")

        return followers_data

    def _scrap_with_retry(self, parser, link, retry=True):
        info = parser.scrap_info(link)
        if info == 'Not Found' and retry:
            print("Info not found, attempting login...")
            self.login()
            info = parser.scrap_info(link)
        return info

    @staticmethod
    def clean_text(text):
        if text:
            text = text.replace(",", "")
            text = text.split(' ')[0]
            return int(text)
        return None
