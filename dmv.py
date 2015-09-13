import getopt
import requests
import smtplib
import sys
import yaml
from contextlib import contextmanager
from datetime import datetime
from email.mime.text import MIMEText
from lxml import html
from time import sleep


APPOINTMENT_URL = 'https://www.dmv.ca.gov/wasapp/foa/findDriveTest.do'


OFFICE_IDS = {
    503: 'San Francisco',
    593: 'San Mateo',
    599: 'Daly City'
}


MAX_DATETIME = datetime.max
BEST_OFFICE = ''
MAX_EXCEPTIONS = 5
MAX_TRIES = 100
SLEEP_TIME = 10
TO_ADDRESS = ''


def get_first_appointment_date(form_data, office_id):
    form_data['officeId'] = office_id
    response = requests.post(APPOINTMENT_URL, data=form_data)
    return parse_respone_for_available_date(response.text)


def parse_respone_for_available_date(html_text):
    format_str = '%A, %B %d, %Y at %I:%M %p'
    doc_tree = html.fromstring(html_text)
    date_str = doc_tree.xpath('//p[@class="alert"]/text()')[1]
    return datetime.strptime(date_str, format_str)


def send_success_email(available_datetime, office, to_address):
    from_address = 'dmvscript@example.com'
    send_email (
        'Appointment available at {office} on {time}'.format(office=office, time=available_datetime),
        from_address,
        to_address
    )


def send_failure_email(exception_string, to_address):
    from_address = 'dmvscript@example.com'
    send_email (
        exception_string,
        from_address,
        to_address
    )


def send_email(message_str, from_address, to_address):
    print message_str
    if not to_address:
        return

    print "Sending email"
    # The actual mail send
    msg = MIMEText(message_str)
    msg['from'] = from_address
    msg['to'] = to_address
    msg['subject'] = message_str

    username, password = get_gmail_creds()
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_address, to_address, msg.as_string())
    server.quit()
    print "Email sent"


def get_gmail_creds():
    gmail_creds_file = file('gmail_creds.yaml', 'r')
    gmail_creds = yaml.load(gmail_creds_file)
    return gmail_creds['username'], gmail_creds['password']


def parse_cmd_line_args(argv):
    sleep_time = SLEEP_TIME
    max_tries = MAX_TRIES
    to_address = TO_ADDRESS
    try:
      opts, args = getopt.getopt(argv,"s:e:m:",["sleep-time=", "email-address=", "max-tries"])
    except getopt.GetoptError:
        print "dmv.py -s <sleep-time> (in mins) -e <email-address> -m <max-tries>"
        exit()
    for opt, arg in opts:
        if opt in ('-s', '--sleep-time'):
            sleep_time = float(arg)
        elif opt in ('-e', '--email-address'):
            to_address = arg
        elif opt in ('-m', '--max-tries'):
            max_tries = int(arg)

    return max_tries, to_address, sleep_time


def retry_on_exceptions(func):
    argv = sys.argv[1:]
    max_tries, to_address, sleep_time = parse_cmd_line_args(argv)
    def func_wrapper(form_data, current_best, best_office):
        number_of_exceptions = 0
        for i in range(0, max_tries):
            try:
                print "Attempt {number}".format(number=i+1)
                current_best, best_office = func(form_data, current_best, best_office, to_address)
            except Exception as e:
                print "Error:{error}".format(error=str(e))
                if number_of_exceptions >= MAX_EXCEPTIONS:
                    send_failure_email(str(e), to_address)
                    exit()
                number_of_exceptions += 1
            print "Sleeping"
            print "\n"
            sleep(sleep_time * 60)
    return func_wrapper


@retry_on_exceptions
def find_best_available_date(form_data, current_best, best_office, to_address):
    better_result_found = False

    for office_id in OFFICE_IDS:
        matches = {}
        first_available_date = get_first_appointment_date(form_data, office_id)
        if (first_available_date < current_best):
            better_result_found = True
            current_best = first_available_date
            best_office = OFFICE_IDS[office_id]
        elif (best_office == OFFICE_IDS[office_id]) and (first_available_date != current_best):
            # Whelp! somebody claimed the prev spot. Reset everything
            current_best = MAX_DATETIME
            best_office = ''

    if (better_result_found):
        send_success_email(current_best, best_office, to_address)

    return (current_best, best_office)


def run(argv):
    data_file = file('dmv_data.yaml', 'r')
    form_data = yaml.load(data_file)
    data_file.close()
    current_best = MAX_DATETIME
    best_office = ''
    find_best_available_date(form_data, current_best, best_office)


if __name__ == '__main__':
    run(sys.argv[1:])
