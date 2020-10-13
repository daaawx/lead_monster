import smtplib
from dns.resolver import Resolver


def get_records(email):
    try:
        domain = email.split('@')[1]
        resolve = Resolver()
        records = resolve.resolve(domain, 'MX')
        mx = records[0].exchange
        mx = str(mx)
        return mx
    except Exception:
        return None


def check_catchall(email, mx):
    try:
        domain = email.split('@')[1]
        fake_email = 'thisisnotavalidemailaddress123456zzz@{0}'.format(domain)
        return _check_email(fake_email, mx)
    except Exception as e:
        return False


def _check_email(email, mx):
    try:
        server = smtplib.SMTP()
        server.set_debuglevel(0)
        server.connect(mx)
        server.helo('Alice')
        server.mail('me@domain.com')
        code, message = server.rcpt(str(email))
        server.quit()
        return True if code == 250 else False
    except Exception as e:
        return False


def check_email(email):
    mx = get_records(email)
    if mx:
        return {
            'email': email,
            'valid': _check_email(email, mx),
            'catchall': check_catchall(email, mx),
        }
