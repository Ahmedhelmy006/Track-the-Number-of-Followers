from PlaywrightDriver import PlaywrightDriver
from core import FollowersTracker
import GoogleFormsSubmitter
import time

def run_scraper(): 
    driver_instance = PlaywrightDriver(cookies_file='LinkedIn Coockies.json')
    context = driver_instance.initialize_driver()
    tracker = FollowersTracker(context, 'Accounts.xlsx', 'Pages.xlsx')

    followers_data = tracker.scrap_info()

    form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSeK_A8x_7ipnICGwK3k3MdTq3vGhXwfu9BhSz37Bgz27T1llw/formResponse'
    
    form_fields = {
        'Business Infographics': 'entry.627780398',
        'Nicolas Boucher Online': 'entry.1247179473',
        'AI Finance Club': 'entry.1150066733',
        'Nicolas Boucher Personal Account': 'entry.269674828'
    }

    mapped_data = {
        'Business Infographics': followers_data[0],
        'Nicolas Boucher Online': followers_data[1],
        'AI Finance Club': followers_data[2],
        'Nicolas Boucher Personal Account': followers_data[3]
    }

    form_submitter = GoogleFormsSubmitter.GoogleFormsSubmitter(form_url, form_fields)
    form_submitter.submit_data(mapped_data)

    driver_instance.close(context)

while True:
    run_scraper()
    time.sleep(60 * 60 * 6)
