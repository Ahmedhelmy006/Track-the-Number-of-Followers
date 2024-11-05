import time as t
from bs4 import BeautifulSoup
import pandas as pd
from CookiesCleaner import CookiesCleaner
from LinkedIn import NormalPageView as NPV
from LinkedIn import ProfileView as PV
from LinkedIn import Newsteller as NT
from Youtube import YouTube as YT
from X import X
import json
import os

class InfoParser:
    def __init__(self, context):
        self.context = context

    def scrap_info(self, link):
        page = self.context.new_page()
        page.goto(link, timeout=1200000000)
        t.sleep(5)  # Allow time for the page to load
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

class NewstellerInfoParser(InfoParser):
    def _parse_info(self, soup):
        number_of_subscribers = soup.select_one(NT.number_of_subscribers_selector)
        if number_of_subscribers:
            raw_text = number_of_subscribers.get_text(strip=True).replace('subscribers', '').strip()
            return FollowersTracker.clean_text(raw_text)
        return 'Not Found'

class YouTubeChannelInfoParser(InfoParser):
    def _parse_info(self, soup):
        subscribers_element = soup.find('span', class_=YT.label_class, string=YT.subscribers_label)
        subscribers_value = (
            subscribers_element.find_next('span', class_=YT.value_class).get_text(strip=True)
            if subscribers_element else 'Not Found'
        )
        views_element = soup.find('span', class_=YT.label_class, string=YT.views_label)
        views_value = (
            views_element.find_next('span', class_=YT.value_class).get_text(strip=True)
            if views_element else 'Not Found'
        )

        return {
            'subscribers': FollowersTracker.clean_text(subscribers_value),
            'views': FollowersTracker.clean_text(views_value)
        }

class Instagram:
    def __init__(self, context):
        self.context = context

    def get_instagram_followers(self, link):
        try:
            page = self.context.new_page()
            page.goto(link, wait_until='domcontentloaded', timeout=120000)
            page.fill('input#ig-input', 'nicolasboucherfinance')
            page.click('button[onclick="onSearch()"]')
            t.sleep(12)  # Wait for the animation to settle
            page.wait_for_selector('#igFollowers .odometer-inside', timeout=10000)

            followers_elements = page.query_selector_all('#igFollowers .odometer-value')
            digits = [el.inner_text().strip() for el in followers_elements]
            followers_count = ''.join(digits)

            print(f"Extracted digits: {digits}")
            print(f"Cleaned followers text: {followers_count}")

            return int(followers_count) if followers_count.isdigit() else "Invalid followers count"

        except Exception as e:
            print(f"Error fetching Instagram followers: {e}")
            return "Not Found"
        finally:
            page.close()

class TwitterInfoParser:
    def __init__(self, context):
        self.context = context

    def get_twitter_followers(self, link):
        try:
            page = self.context.new_page()
            page.goto(link, wait_until='domcontentloaded', timeout=120000)
            page.wait_for_selector(X.followers_value_selector, timeout=10000)
            followers_element = page.query_selector(X.followers_value_selector)
            followers = followers_element.inner_text().replace(",", "").strip()
            growth_element = page.query_selector(X.last_30_days_selector)
            growth = growth_element.inner_text().split(" ")[0] if growth_element else "Not Found"
            growth_percentege = growth_element.inner_text().split(" ")[1] if growth_element else "Not Found"

            print(f"Twitter followers: {followers}")
            print(f"Growth over the last 30 days: {growth}")

            return {
                'followers': int(followers),
                'last_30_days_growth': growth,
                'Growth Percentege': growth_percentege
            }
        except Exception as e:
            print(f"Error fetching Twitter followers: {e}")
            return {'followers': 'Not Found', 'last_30_days_growth': 'Not Found'}
        finally:
            page.close()


class FollowersTracker:
    def __init__(self, context, accounts_file, pages_file, newsteller_file, youtube_file, instagram_file, twitter_file):
        self.context = context
        self.accounts = self.read_excel(accounts_file)
        self.pages = self.read_excel(pages_file)
        self.newsteller = self.read_excel(newsteller_file)
        self.youtube_channels = self.read_excel(youtube_file)
        self.instagram_links = self.read_excel(instagram_file)
        self.twitter_links = self.read_excel(twitter_file)

    def login(self, username, password):
        username = os.getenv("LINKEDIN_USERNAME")
        password = os.getenv("LINKEDIN_PASSWORD")
        page = self.context.new_page()
        page.goto("https://www.linkedin.com/login", timeout=60000)
        page.fill('input[name="session_key"]', username)
        page.fill('input[name="session_password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        new_cookies = self.context.cookies()
        cleaned_cookies = CookiesCleaner.clean_cookies(new_cookies)
        with open('cookies.json', 'w') as file:
            json.dump(cleaned_cookies, file)

        page.close()
        print("Login successful, cookies saved.")

    def read_excel(self, file_path):
        return pd.read_excel(file_path)

    def get_links(self):
        account_links = self.accounts['Link'].tolist()
        page_links = self.pages['Link'].tolist()
        newsteller_links = self.newsteller['Link'].tolist()
        youtube_links = self.youtube_channels['Link'].tolist()
        instagram_links = self.instagram_links['Link'].tolist()
        twitter_links = self.twitter_links['Link'].tolist()
        return account_links, page_links, newsteller_links, youtube_links, instagram_links, twitter_links

    def scrap_info(self):
        account_parser = AccountInfoParser(self.context)
        page_parser = PageInfoParser(self.context)
        newsteller_parser = NewstellerInfoParser(self.context)
        youtube_parser = YouTubeChannelInfoParser(self.context)
        instagram_parser = Instagram(self.context)
        twitter_parser = TwitterInfoParser(self.context)

        account_links, page_links, newsteller_links, youtube_links, instagram_links, twitter_links = self.get_links()

        followers_data = []

        for link in account_links:
            info = self._scrap_with_retry(account_parser, link)
            followers_data.append(info)
            print(f"Account info: {info}")

        for link in page_links:
            info = self._scrap_with_retry(page_parser, link)
            followers_data.append(info)
            print(f"Page info: {info}")

        for link in newsteller_links:
            info = self._scrap_with_retry(newsteller_parser, link)
            followers_data.append(info)
            print(f"Newsteller subscribers: {info}")

        for link in youtube_links:
            info = self._scrap_with_retry(youtube_parser, link)
            followers_data.append(info)
            print(f"YouTube info: {info}")

        for link in instagram_links:
            info = self._scrap_with_retry(instagram_parser, link)
            followers_data.append(info)
            print(f"Instagram followers: {info}")

        for link in twitter_links:
            info = self._scrap_with_retry(twitter_parser, link)
            followers_data.append(info)
            print(f"Twitter info: {info}")

        return followers_data

    def _scrap_with_retry(self, parser, link, retry=True):
        if isinstance(parser, Instagram):
            info = parser.get_instagram_followers(link)
        elif isinstance(parser, TwitterInfoParser):
            info = parser.get_twitter_followers(link)
        else:
            info = parser.scrap_info(link)

        if info == 'Not Found' and retry:
            print("Info not found, attempting login...")
            self.login(username='morganfreemanek@gmail.com', password='CGfoxier60###')
            if isinstance(parser, Instagram):
                info = parser.get_instagram_followers(link)
            elif isinstance(parser, TwitterInfoParser):
                info = parser.get_twitter_followers(link)
            else:
                info = parser.scrap_info(link)
        
        return info

    @staticmethod
    def clean_text(text):
        if text:
            text = text.replace(",", "")
            text = text.split(' ')[0]
            try:
                return int(text)
            except ValueError:
                return text
        return None
