import csv
import time
from urllib.parse import quote_plus
import chromedriver_autoinstaller
import pandas as pd
from rich import pretty
from rich.console import Console
from rich.progress import track
from selenium import webdriver
from SeleniumBot import SeleniumBot
from email_generator.EmailGenerator import EmailGenerator

__NAME__ = 'LeadMonster'
__VERSION__ = '1.0'
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
  _                   _ __  __                 _
 | |    ___  __ _  __| |  \/  | ___  _ __  ___| |_ ___ _ __
 | |   / _ \/ _` |/ _` | |\/| |/ _ \| '_ \/ __| __/ _ \ '__|
 | |__|  __/ (_| | (_| | |  | | (_) | | | \__ \ ||  __/ |
 |_____\___|\__,_|\__,_|_|  |_|\___/|_| |_|___/\__\___|_|

'''


class Bot(SeleniumBot):
    JOB_TITLE = 'h2.jobs-details-top-card__job-title'

    COMPANY_NAME = '.jobs-details-top-card__company-url'
    JOB_LOCATION = '.jobs-details-top-card__company-info'

    POSTED = '.jobs-details-top-card__content-container p'

    EMPLOYEE_NO = '.jobs-details-job-summary__text--ellipsis'  # 3

    JOB_CARD = '[data-job-id]'

    JOB_POSTER = '.jobs-poster__wrapper'
    JOB_POSTER_TITLE = '.jobs-poster__headline'

    INDUSTRIES = '//h3[text()="Industry"]//following-sibling::ul//li'  # xpath list

    SEE_MORE = '[data-control-name="about_company_life_link"]'

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
    LEAD_UNIVERSITY = '.pv-education-entity h3'

    # DEV_SETTINGS = True
    # HEADLESS = True
    DATA_DIR = r'User Data'

    @staticmethod
    def get_posted_date(li):
        for idx, i in enumerate(li):
            if 'Posted Date' in i:
                return li[idx + 1]
        return None

    def run(self):
        self.clean_up()

        self.keyword = self.bot_print('Enter search keyword:', input_msg='> ')
        self.location = self.bot_print('Enter location:', input_msg='> ')
        job_count = int(self.bot_print('How many jobs?', input_msg='> '))

        url = f"https://www.linkedin.com/jobs/search?keywords={self.keyword}&location={self.location}"

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
           lmBtn.querySelector('span').innerHTML('Running...');
        });
        ''')
        time.sleep(3)

        while True:
            if self.script("return document.querySelector('#runLM').classList.contains('run')"):
                break
            time.sleep(1)

        while len(self.scraped_postings) < job_count:
            for _ in range(4):
                self.script(
                    'arguments[0].scrollIntoView()',
                    self.css(self.JOB_CARD, getall=True)[-1],
                )
                time.sleep(1)

            for card in self.css(self.JOB_CARD, getall=True):
                self.click(card)
                time.sleep(1.5)
                self.parse_posting()
                if len(self.scraped_postings) == job_count:
                    break

        self.bot_print(f"Scraped {len(self.scraped_postings)} jobs.")
        for posting in self.scraped_postings:
            if posting.get('Company LinkedIn'):
                self.bot_print(f"{posting.get('Company')}")
                self.parse_company(posting)

        for lead in track(self.lead_list, description=f"Processing {len(self.lead_list)} leads..."):
            if lead.get('Lead LinkedIn'):
                self.parse_lead(lead)

        filename = f'{len(self.lead_list)}_{self.keyword}_{self.location}.csv'
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

    def parse_posting(self):
        location = self.css(self.JOB_LOCATION, attr='text').split('\n')
        employees = self.css(self.EMPLOYEE_NO, attr='text', getall=True)
        if employees:
            try:
                employees = employees[2]
            except IndexError:
                employees = 'Unknown'
        scraped_data = {
            'Job Title': self.css(self.JOB_TITLE, attr='text'),
            'Job Location': location[3],
            'Company': location[1],
            'Posted': self.get_posted_date(self.css(self.POSTED, attr='text').split('\n')),
            'Employees': employees,
            'Industry': ', '.join(self.xpath(self.INDUSTRIES, attr='text', getall=True))
        }
        self.scraped_postings.append(scraped_data)
        job_poster = self.css(self.JOB_POSTER, attr='text', getall=True)
        if job_poster:
            self.job_posters[id(scraped_data)] = job_poster[0]
        else:
            self.job_posters[id(scraped_data)] = ''

        see_more = self.css('[href$="/life/"]', attr='href')
        if see_more:
            scraped_data['Company LinkedIn'] = see_more.replace('/life/', '/about/')

    def parse_company(self, posting):
        url = posting.get('Company LinkedIn')
        self.get(url)
        website = self.css(self.WEBSITE, attr='href')
        if website:
            posting['Company URL'] = website
        else:
            self.scrape_company_url(posting)

        self.click(self.PEOPLE_TAB, css=True)
        self.wait_show_element(self.PROFILE_CARDS, wait=5)
        self.scroll_until_end(self.PROFILE_CARDS, wait=5)

        cards = self.css(self.PROFILE_CARDS, getall=True)
        for card in track(cards, f'Processing {len(cards)} leads...'):
            lead_name = self.css(self.CARD_NAME, node=card, attr='text')
            if lead_name:
                lead_name = lead_name.strip()
                desc = self.css(self.CARD_DESC, node=card, attr='text').lower()
                if self.keyword.lower() in desc:
                    temp_obj = posting.copy()
                    try:
                        temp_obj.update({
                            'Lead - First Name': lead_name.split(' ', 1)[0],
                            'Lead - Last Name': lead_name.split(' ', 1)[1],
                            'Did Lead Post Job (Y/N)?': 'Y' if lead_name.lower() in str(
                                self.job_posters[id(posting)]).lower() else 'N',
                            'Location': posting.get('Job Location'),
                            'Lead LinkedIn': self.css(self.CARD_LINK, node=card, attr='href'),
                        })
                        email, status = self.email_generator.get_email_and_status(temp_obj)
                        temp_obj['Email'] = email
                        self.lead_list.append(temp_obj)
                    except Exception as e:
                        print(e)

    def parse_lead(self, lead):
        url = lead.get('Lead LinkedIn')
        self.get(url)
        lead.update({
            'Lead - Job Title': self.css(self.LEAD_TITLE, attr='text'),
            'Lead - Location': self.css(self.LEAD_LOCATION, attr='text'),
            'Lead - University': self.get_university(),
        })

    def get_university(self):
        education = self.css(self.LEAD_UNIVERSITY, attr='text', getall=True)
        for edu in education:
            if 'university' in edu.lower():
                return edu
        return 'Not provided'

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
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--log-level=3")
        # chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-infobars')
        # # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        # chrome_options.add_argument('--disable-notifications')
        # chrome_options.add_argument("--disable-plugins-discovery")
        # # chrome_options.add_argument('--profile-directory=default')
        # chrome_options.add_experimental_option("excludeSwitches",
        #                                        ["enable-automation",
        #                                         # "ignore-certificate-errors",
        #                                         "safebrowing-disable-auto-update",
        #                                         "disable-client-side-phishing-detection",
        #                                         "safebrowsing-disable-download-protection",
        #                                         "enable-logging"  # Disable logging
        #                                         ])

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
        self.keyword = ''
        self.location = ''
        self.job_posters = {}
        self.scraped_postings = []
        self.lead_list = []
        self.output = []
        self.email_generator = EmailGenerator()

    def __init__(self):
        pretty.install()
        self.c = Console()
        self.bot_print(__FIGLET__, figlet=True)

        self.bot_print('Checking chromedriver version...')
        chromedriver_autoinstaller.install(cwd=True)

        self.keyword = ''
        self.location = ''
        self.job_posters = {}
        self.scraped_postings = []
        self.lead_list = []
        self.output = []
        self.email_generator = EmailGenerator()


if __name__ == '__main__':
    bot = Bot()
    while True:
        bot.run()
