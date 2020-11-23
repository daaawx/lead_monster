import configparser
import csv
import json
import os
import random
import re
import time
import traceback
from urllib.parse import quote_plus
import chromedriver_autoinstaller
import pandas as pd
from rich import pretty
from rich.console import Console
from rich.progress import track
from selenium import webdriver
from SeleniumBot import SeleniumBot
from email_generator.EmailGenerator import EmailGenerator
from utils import generate_md5

__NAME__ = 'LeadMonster'
__VERSION__ = '1.3'
__FIGLET__ = '''
  @@@@@@@@@@@@@@@@@@@@@@@@@@@0LfffffLL0@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@0GGGGGCG0@@@ffG8@@@@8Gtt8@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@0LC08@@@80LfG1LCi:;t8@@@@Li8@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@0t8@@@@@@@@@8;18     i@@@@@1L@@@@@8@@@@@@@@@@@
  @@@@@@@@@@@10@@@@@L;:iL@01@i.  :C@@@@@i1LLLL1:G@@@@@@@@@@
  @@@@@@@@@@@iG@@@@f     C8,L@800@@@@@@f;tiii11:1t10@@@@@@@
  @@@@@@@@@08C;0@@@G:  .;G1tiiC0@@@80L1ifffffffftti,L@@@@@@
  @@@@@@@@L:1t11LG8@@GCLL1tfft1i1111i1tfftttttfffff1:tfG@@@
  @@@@@0fii1tffft1tttttttffttfffffffffftftttttffftift,.G@@@
  @@@@G:,ifffftffffffffffttttffffffffffffffffff11iifff110@@
  @Lif11ttftffffttttttttffffffi:i1fi;i1fft;;;;:;tffftf1,t@@
  @G::tffffttttffffffffff1:1;.    .    ...    ;ffftffft:;18
  @@t,fi:ttffffti1ti,;;;,                     1ftffftfi;i18
  @0.tf1iiii;:,. .                           .tffffftfi1@@@
  @8,1ffffft1,                               iftfffftfit@@@
  @@L.1fttffffi.                            ,ffffffft::G@@@
  @@@G,tftffttf1                           .tftffftf:;8@@@@
  @@@@L:fftffftf1,                        :tftffftff:C@@@@@
  @@@@C,i:ftttftffi,                    :1fftftttf1:,C@@@@@
  @@@@G11;iffftftfff1:.             .,itfftttffffi;fL0@@@@@
  @@@@@@@81;1tfftttffft1i;:,,,,,:;i1tfffttffff;;ii0@@@@@@@@
  @@@@@@@@@fi.;ffffftffffffffffffffffttfffft1:1C0@@@@@@@@@@
  @@@@@@@@@@@G::i;itfttffffffffffffffffti;i1fG@@@@@@@@@@@@@
  @@@@@@@@@@@@@Cttfi;:,;i11i1tttt1iiii11L08@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@0G80f1tttfttttLG008@@@@@@@@@@@@@@@@@@@@
▄▄▌  ▄▄▄ . ▄▄▄· ·▄▄▄▄  • ▌ ▄ ·.        ▐ ▄ .▄▄ · ▄▄▄▄▄▄▄▄ .▄▄▄
██•  ▀▄.▀·▐█ ▀█ ██▪ ██ ·██ ▐███▪▪     •█▌▐█▐█ ▀. •██  ▀▄.▀·▀▄ █·
██▪  ▐▀▀▪▄▄█▀▀█ ▐█· ▐█▌▐█ ▌▐▌▐█· ▄█▀▄ ▐█▐▐▌▄▀▀▀█▄ ▐█.▪▐▀▀▪▄▐▀▀▄
▐█▌▐▌▐█▄▄▌▐█ ▪▐▌██. ██ ██ ██▌▐█▌▐█▌.▐▌██▐█▌▐█▄▪▐█ ▐█▌·▐█▄▄▌▐█•█▌
.▀▀▀  ▀▀▀  ▀  ▀ ▀▀▀▀▀• ▀▀  █▪▀▀▀ ▀█▄▀▪▀▀ █▪ ▀▀▀▀  ▀▀▀  ▀▀▀ .▀  ▀

                          ░▀█░░░░░▀▀█
                          ░░█░░░░░░▀▄
                          ░▀▀▀░▀░░▀▀░
'''

DATE_FILTERS = ['daily', 'weekly', 'monthly']


class Bot(SeleniumBot):
    JOB_TITLE = 'h2.jobs-details-top-card__job-title'

    COMPANY_NAME = '.jobs-details-top-card__company-url'
    JOB_LOCATION = '.jobs-details-top-card__company-info'

    POSTED = '.jobs-details-top-card__content-container p'

    EMPLOYEE_NO = '.jobs-details-job-summary__text--ellipsis'  # 3

    JOB_CARD = '[data-job-id]>div>div>[href*="/jobs/view"]'

    JOB_POSTER_NAME = '.jobs-poster__name'
    JOB_POSTER_LINK = '[data-control-name="jobdetails_profile_poster"]'

    INDUSTRIES = '//h3[text()="Industry"]//following-sibling::ul//li'  # xpath list

    SEE_MORE = '[data-control-name="about_company_life_link"]'

    NEXT_PAGE = '//li[contains(@class, "active")]//following-sibling::li'  # xpath

    # Page
    WEBSITE = 'dl a'

    PEOPLE_TAB = 'li a[href*="/people/"]'
    PROFILE_CARDS = '.org-people-profile-card__profile-info'

    CARD_NAME = '.org-people-profile-card__profile-title'
    CARD_DESC = '.lt-line-clamp.lt-line-clamp--multi-line'
    CARD_LINK = 'a[href*="/in/"]'

    SIGN_IN = '//*[text()="Sign in"]'

    LEAD_TITLE = 'h2.break-words'
    LEAD_LOCATION = '.pv-top-card--list-bullet li.t-16'
    LEAD_UNIVERSITY = '.pv-entity__degree-info h3'

    CONTACT_INFO = '//*[text()="Contact Info"]'  # xpath
    CONTACT_INFO_LINKS = 'a.pv-contact-info__contact-link'

    # DEV_SETTINGS = True
    # HEADLESS = True
    DATA_DIR = r'User Data'

    @staticmethod
    def get_after_list(li, term):
        for idx, i in enumerate(li):
            if term in i:
                return li[idx + 1]
        return None

    @staticmethod
    def lowercase_set(li):
        return set(map(lambda x: x.lower(), li))

    def save_posting_history(self, posting_hash):
        self.posting_history.append(posting_hash)
        try:
            with open('posting_history.json') as f:
                obj = json.loads(f.read())
        except:
            obj = []
        obj.append(posting_hash)
        with open('posting_history.json', 'w') as f:
            f.write(json.dumps(obj))

    def random_delay(self):
        if self.max_random_delay:
            time.sleep(random.uniform(0.1, self.max_random_delay))

    def run(self):
        self.clean_up()

        if self.automatic:
            self.bot_print('Automatic mode enabled.')
            obj = self.read_csv('auto.csv')
            for search_conf in obj:
                self.search = search_conf.get('search')
                self.location = search_conf.get('location')
                self.keywords = self.lowercase_set(search_conf.get('keywords', '').split(','))
                self.max_company_size = int(search_conf.get('max_company_size', 0))
                self.job_count = int(search_conf.get('job_count', 0))
                self.date_filter = search_conf.get('date_filter', '').strip()
                self._run()
            quit()
        else:
            self.search = self.bot_print('Enter search term:', input_msg='> ')
            self.location = self.bot_print('Enter location:', input_msg='> ')
            self.keywords = self.lowercase_set(
                self.bot_print('Lead keywords (comma separated):', input_msg='> ').split(','))
            self.max_company_size = int(self.bot_print('Enter max company size:', input_msg='> '))
            self.job_count = int(self.bot_print('How many jobs to scrape?', input_msg='> '))
            self._run()

    def _run(self):
        self.bot_print(
            f'{self.search} @ {self.location} [<{self.max_company_size}] [{self.job_count}]')
        url = f"https://www.linkedin.com/jobs/search?keywords={self.search}&location={self.location}"

        if not self.driver:
            self.create_driver()
        self.get(url)

        sign_in = self.xpath(self.SIGN_IN)
        if sign_in:
            self.bot_print('Please sign in.')
            self.get('https://www.linkedin.com/login')

        # Wait for sign-in
        while self.xpath(self.SIGN_IN):
            time.sleep(2.5)

        if sign_in:
            self.get(url)

        if self.automatic:
            if self.date_filter:
                self.click('[aria-controls="date-posted-facet-values"]', css=True, wait=3)
                date_radios = self.css('#date-posted-facet-values input', getall=True, wait_for=3)
                if date_radios:
                    self.click(date_radios[DATE_FILTERS.index(self.date_filter)])
                    self.click('#date-posted-facet-values .artdeco-button--primary', css=True)
                    time.sleep(3)
        else:
            while not self.script('''return document.querySelector('#runLM')'''):
                self.script('''
                let span = document.createElement('span');
                span.innerHTML = `<button id="runLM" style="background-color: #2db0ad;" class="artdeco-button artdeco-button--3 artdeco-button--primary ember-view mt4"> 
                <span class="artdeco-button__text">
                    Run LeadMonster
                </span></button>`;
                let btn = span.firstElementChild;
                document.querySelector('section .neptune-grid').appendChild(btn);
                document.querySelector('#runLM').addEventListener('click', (e) => {
                   let lmBtn = document.querySelector('#runLM');
                   lmBtn.classList.add('run');
                   lmBtn.querySelector('span').innerHTML = 'Running...';
                });
                ''')
                time.sleep(3)

            while not self.script("return document.querySelector('#runLM').classList.contains('run')"):
                time.sleep(.3)

        page = 1
        while len(self.scraped_postings) < self.job_count:
            self.bot_print(
                f'{self.search} @ {self.location} [<{self.max_company_size}] [{len(self.scraped_postings)}/{self.job_count}] [Page {page}]')
            for _ in range(4):
                job_cards = self.css(self.JOB_CARD, getall=True, wait=3)
                if not job_cards:
                    break

                self.script(
                    'arguments[0].scrollIntoView()',
                    job_cards[-1],
                )
                time.sleep(1.5)

            cards = self.css(self.JOB_CARD, getall=True)
            for idx, card in enumerate(cards):
                self.click(
                    self.css(self.JOB_CARD, getall=True)[idx]
                )
                time.sleep(1.5)
                self.parse_posting()
                if len(self.scraped_postings) == self.job_count:
                    break

            next_page = self.xpath(self.NEXT_PAGE)
            if next_page:
                self.click(next_page)
                page += 1
                time.sleep(3)
            else:
                break

        self.bot_print(f"Scraped {len(self.scraped_postings)} jobs.")
        for posting in self.scraped_postings:
            if posting.get('Company LinkedIn'):
                self.bot_print(f"{posting.get('Company')}")
                self.parse_company(posting)

        for lead in track(self.lead_list, description=f"Processing {len(self.lead_list)} leads..."):
            if lead.get('Lead LinkedIn'):
                self.parse_lead(lead)

        filename = os.path.join(
            'data',
            f'{len(self.lead_list)}_{self.search}_{self.location}.csv'
        )
        self.export_csv(self.lead_list, filename)
        self.bot_print(f'Saved as {filename}')

    def scrape_company_url(self, obj):
        query = quote_plus(f"{obj.get('Company')} company")
        url = f'https://www.google.com/search?q={query}'
        self.driver.execute_script(f"window.open('{url}', '_blank')")

        links = self.css('#search a', getall=True, attr='href')
        for link in links:
            if 'linkedin' not in link:
                obj['Company URL'] = link
                self.driver.execute_script('window.close();')
                return

    @staticmethod
    def average_company_size(company_size):
        cs = company_size.replace(',', '')
        sizes = [int(i) for i in re.findall('\d+', cs) if i.isdigit()]
        if not sizes:
            return 1
        return sum(sizes) / len(sizes)

    @staticmethod
    def highest_company_size(company_size):
        cs = company_size.replace(',', '')
        sizes = [int(i) for i in re.findall('\d+', cs) if i.isdigit()]
        if not sizes:
            return 1
        return sizes[-1]

    def keyword_filter(self, description):
        if any(True for i in self.keywords if i in description.lower()):
            return True

    def is_bad_posting(self, scraped_data):
        company_size = self.highest_company_size(scraped_data.get('Employees', '1'))
        company_name = scraped_data.get('Company', '')
        # Skip if company size > self.max_company_size
        if company_size > self.max_company_size:
            return True
        # Skip if name in blacklist
        if any(True for i in self.blacklist if i in company_name.lower()):
            return True
        return False

    def parse_posting(self):
        try:
            location = self.css(self.JOB_LOCATION, attr='text').split('\n')
            employees = self.css(self.EMPLOYEE_NO, attr='text', getall=True)
            if employees:
                try:
                    employees = employees[2]
                except IndexError:
                    employees = 'Unknown'
            scraped_data = {
                'Job Title': self.css(self.JOB_TITLE, attr='text'),
                'Job Location': self.get_after_list(location, 'Company Location'),
                'Company': self.get_after_list(location, 'Company Name'),
                'Posted': self.get_after_list(self.css(self.POSTED, attr='text').split('\n'), 'Posted Date'),
                'Employees': employees,
                'Industry': ', '.join(self.xpath(self.INDUSTRIES, attr='text', getall=True))
            }
            posting_hash = generate_md5(str(scraped_data))
            if posting_hash in self.posting_history:
                self.bot_print('Posting already in history. Skipping.')
                return
            if self.is_bad_posting(scraped_data):
                return
            self.save_posting_history(posting_hash)
            self.scraped_postings.append(scraped_data)
            job_poster = self.css(self.JOB_POSTER_NAME, attr='text')
            if job_poster:
                scraped_data.update({
                    'Lead - First Name': job_poster.split(' ', 1)[0],
                    'Lead - Last Name': job_poster.split(' ', 1)[1],
                    'Did Lead Post Job (Y/N)?': 'Y',
                    'Location': scraped_data.get('Job Location'),
                    'Lead LinkedIn': self.css(self.JOB_POSTER_LINK, attr='href'),
                })

            see_more = self.css('[href$="/life/"]', attr='href')
            if see_more:
                scraped_data['Company LinkedIn'] = see_more.replace('/life/', '/about/')
        except Exception as e:
            e = traceback.format_exc()
            bot.log(screenshot=True, error=e)

    def parse_company(self, posting):
        try:

            url = posting.get('Company LinkedIn')
            self.get(url)
            website = self.css(self.WEBSITE, attr='href')
            if website:
                posting['Company URL'] = website
            else:
                self.scrape_company_url(posting)

            poster = posting.get('Lead - First Name')
            if poster:
                temp_obj = posting.copy()
                email, status = self.email_generator.get_email_and_status(temp_obj)
                temp_obj['Email'] = email
                self.lead_list.append(temp_obj)
                return
            self.click(self.PEOPLE_TAB, css=True)
            self.wait_show_element(self.PROFILE_CARDS, wait=5)
            self.scroll_until_end(self.PROFILE_CARDS, wait=5, max_total=self.max_company_size * 2)

            cards = self.css(self.PROFILE_CARDS, getall=True)
            total_leads = 0
            for card in track(cards, f'Processing {len(cards)} leads...'):
                if total_leads >= self.max_leads_per_company:
                    break
                lead_name = self.css(self.CARD_NAME, node=card, attr='text')
                if lead_name:
                    lead_name = lead_name.strip()
                    desc = self.css(self.CARD_DESC, node=card, attr='text').lower()
                    if self.keyword_filter(desc):
                        temp_obj = posting.copy()
                        try:
                            temp_obj.update({
                                'Lead - First Name': lead_name.split(' ', 1)[0],
                                'Lead - Last Name': lead_name.split(' ', 1)[1],
                                'Did Lead Post Job (Y/N)?': 'N',
                                'Location': posting.get('Job Location'),
                                'Lead LinkedIn': self.css(self.CARD_LINK, node=card, attr='href'),
                            })
                            email, status = self.email_generator.get_email_and_status(temp_obj)
                            temp_obj['Email'] = email
                            self.lead_list.append(temp_obj)
                            total_leads += 1
                        except Exception as e:
                            print(e)
        except Exception as e:
            e = traceback.format_exc()
            bot.log(screenshot=True, error=e)

    def parse_lead(self, lead):
        try:
            url = lead.get('Lead LinkedIn')
            self.get(url)
            lead.update({
                'Lead - Contact Info': self.get_contact_info(),
                'Lead - Job Title': self.css(self.LEAD_TITLE, attr='text'),
                'Lead - Location': self.css(self.LEAD_LOCATION, attr='text'),
                'Lead - University': self.get_university(),
            })
        except Exception as e:
            e = traceback.format_exc()
            bot.log(screenshot=True, error=e)

    def get_contact_info(self):
        try:
            self.click(self.CONTACT_INFO, xpath=True)
            time.sleep(1)
            '\n'.join(self.css(self.CONTACT_INFO_LINKS, attr='href', getall=True))
            return 'Not found'
        except Exception as e:
            e = traceback.format_exc()
            bot.log(screenshot=True, error=e)

    def get_university(self):
        try:
            education = self.css(self.LEAD_UNIVERSITY, attr='text', getall=True)
            for edu in education:
                if 'university' in edu.lower():
                    return edu
            return 'Not provided'
        except Exception as e:
            e = traceback.format_exc()
            bot.log(screenshot=True, error=e)

    def create_driver(self):

        chrome_options = webdriver.ChromeOptions()

        if self.HEADLESS:
            chrome_options.add_argument("--headless")

        if self.DISABLE_IMAGES:
            chrome_options.add_argument('blink-settings=imagesEnabled=false')
            chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

        if self.DEV_SETTINGS:
            chrome_options.add_argument('--fast-start')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--window-position=1072,642')

        if self.DATA_DIR:
            chrome_options.add_argument(f'--user-data-dir={self.DATA_DIR}')
            chrome_options.add_argument(f'--profile-directory={self.PROFILE if self.PROFILE else "Default"}')

        if self.EXTENSIONS:
            for ext in self.EXTENSIONS:
                chrome_options.add_extension(f'{ext}.zip')

        chrome_options.add_argument("--silent")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-infobars')
        # # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-notifications')
        # chrome_options.add_argument("--disable-plugins-discovery")
        # # chrome_options.add_argument('--profile-directory=default')
        chrome_options.add_experimental_option("excludeSwitches",
                                               ["enable-automation",
                                                # "ignore-certificate-errors",
                                                "enable-logging"  # Disable logging
                                                ])

        self.driver = webdriver.Chrome(options=chrome_options)

        if not self.RANDOM_WINDOW:
            self.driver.maximize_window()

    @staticmethod
    def read_csv(filename):
        with open(filename, encoding='utf-8-sig') as f:
            data = csv.DictReader(f)
            return list(data)

    @staticmethod
    def export_csv(obj, filename='output.csv'):
        df = pd.DataFrame(obj)
        df.to_csv(filename, index=False)

    def spawn_driver(self):
        if not self.driver:
            self.create_driver()

    def restart_driver(self):
        if self.driver:
            self.close()
            time.sleep(3)
        self.create_driver()

    def bot_print(self, message, input_msg=None, figlet=False):
        if figlet:
            # msg = f"[bold light_cyan1]{__FIGLET__}[/bold light_cyan1]"
            msg = __FIGLET__
            self.c.print(msg, style='#00eeff')
        else:
            self.c.print(
                f"[bold blue][{__NAME__} {__VERSION__}][/bold blue] {message}"
            )

        if input_msg:
            return input(input_msg)

    def clean_up(self):
        self.search = ''
        self.keywords = []
        self.max_company_size = 9999999
        self.location = ''
        self.scraped_postings = []
        self.lead_list = []
        self.output = []
        self.job_count = 0
        self.date_filter = None
        self.email_generator = EmailGenerator()
        with open('blacklist.txt') as f:
            self.blacklist = self.lowercase_set([i.strip() for i in f.readlines() if i.strip()])
        with open('posting_history.json') as f:
            self.posting_history = json.loads(f.read())

    def __init__(self):
        pretty.install()
        self.c = Console()
        self.bot_print(__FIGLET__, figlet=True)

        self.bot_print('Checking chromedriver version...')
        chromedriver_autoinstaller.install(cwd=True)

        config = configparser.ConfigParser()
        config.read('config.txt')
        self.automatic = config.getboolean('leadmonster', 'auto_mode')
        self.max_leads_per_company = config.getint('leadmonster', 'max_leads_per_company')
        self.max_random_delay = config.getint('leadmonster', 'max_random_delay')

        self.search = ''
        self.keywords = []
        self.location = ''
        self.max_company_size = 9999999
        self.scraped_postings = []
        self.lead_list = []
        self.output = []
        self.job_count = 0
        self.date_filter = None
        self.email_generator = EmailGenerator()
        with open('blacklist.txt') as f:
            self.blacklist = self.lowercase_set([i.strip().lower() for i in f.readlines() if i.strip()])
        with open('posting_history.json') as f:
            self.posting_history = json.loads(f.read())

        # Create folders
        if not os.path.exists('data'):
            os.mkdir('./data')


if __name__ == '__main__':
    bot = Bot()
    while True:
        bot.run()
