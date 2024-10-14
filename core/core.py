import time as t
from bs4 import BeautifulSoup
import pandas as pd
from LinkedIn import NormalPageView as NPV
from LinkedIn import ProfileView as PV

class InfoParser:
    def __init__(self, context):
        self.context = context

    def scrap_info(self, link):
        page = self.context.new_page()
        page.goto(link)
        page.wait_for_timeout(2000)  # Wait for the page to load

        html_content = page.content()  # Get the page source
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
            info = account_parser.scrap_info(link)
            followers_data.append(info)
            print(f"Account info: {info}")

        for link in page_links:
            info = page_parser.scrap_info(link)
            followers_data.append(info)
            print(f"Page info: {info}")

        return followers_data

    @staticmethod
    def clean_text(text):
        if text:
            text = text.replace(",", "")
            text = text.split(' ')[0]
            return int(text)
        return None
