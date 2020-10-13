import tldextract
from .generator import generate_emails
from .validator import check_email
import re


def get_first_and_last_name(name):
    li = re.findall(r'\w+', name)
    return li[0].strip(',').title(), li[1].strip(',').title()


class EmailGenerator:

    @staticmethod
    def run(first_name, last_name, url):
        extracted = tldextract.extract(url)
        domain = "{}.{}".format(extracted.domain, extracted.suffix)

        emails = generate_emails(first_name, last_name, domain)
        for email in emails:
            info = check_email(email)
            if info:
                return info

        return {
            'email': emails[0],
            'valid': False,
            'catchall': False,
        }

    def get_email_and_status(self, lead_obj):

        first_name = lead_obj.get('Lead - First Name')
        last_name = lead_obj.get('Lead - Last Name')
        company_url = lead_obj.get('Company URL')
        company_name = lead_obj.get('Company')

        if company_url:
            lead_email_obj = self.run(
                first_name,
                last_name,
                company_url,
            )

            email = lead_email_obj['email']
            email_valid = lead_email_obj['valid']
            email_catchall = lead_email_obj['catchall']
            if email_valid and not email_catchall:
                status = 'Verified'
            elif email_valid and email_catchall:
                status = 'Catchall'
            else:
                status = 'Unverified'

            return email, status
        else:
            lead_name = first_name.lower()
            company_domain = ''.join(re.findall(r'[A-Za-z]+', company_name)).lower()
            if company_domain:
                company_domain += '.com'
                return f'{lead_name}@{company_domain}', 'Unverified'
