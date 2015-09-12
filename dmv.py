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

def get_first_appointment_date(form_data, office_id):
    form_data['officeId'] = office_id
    response = requests.post(APPOINTMENT_URL, data=form_data)
    return parse_respone_for_available_date(response.text)


def parse_respone_for_available_date(html_text):
    format_str = '%A, %B %d, %Y at %I:%M %p'
    doc_tree = html.fromstring(html_text)
    date_str = doc_tree.xpath('//p[@class="alert"]/text()')[1]
    return datetime.strptime(date_str, format_str)


def better_than_current(available_datetime):
    return available_datetime < CURRENT_BEST


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
    msg = MIMEText(message_str)
    msg['From'] = from_address
    msg['To'] = to_address
    smtp_server = smtplib.SMTP('localhost')
    smtp_server.sendmail(from_address, [to_address], msg.as_string())
    smtp_server.quit()


def find_best_available_date(form_data, current_best, best_office, to_address):
    better_result_found = False

    for office_id in OFFICE_IDS:
        matches = {}
        first_available_date = get_first_appointment_date(form_data, office_id)
        if (first_available_date < current_best):
            better_result_found = True
            current_best = first_available_date
            best_office = OFFICE_IDS[office_id]

    if (better_result_found):
        send_success_email(current_best, best_office, to_address)

    return (current_best, best_office)


def parse_cmd_line_args(argv):
    data_file = 'dmv_data_sample.yaml'
    sleep_time = 10
    email_address = ''
    max_tries = 100
    try:
      opts, args = getopt.getopt(argv,"d:s:e:m:",["data-file=", "sleep-time=", "email-address=", "max-tries"])
    except getopt.GetoptError:
        print "dmv.py -d <data-file> -s <sleep-time> (in mins) -e <email-address> -m <max-tries>"
        exit()
    for opt, arg in opts:
        if opt in ('-d', '--data-file'):
            data_file = arg
        elif opt in ('-s', '--sleep-time'):
            sleep_time = float(arg)
        elif opt in ('-e', '--email-address'):
            email_address = arg
        elif opt in ('-m', '--max-tries'):
            max_tries = int(arg)
    return data_file, sleep_time, email_address, max_tries


def run(argv):
    data_file, sleep_time, to_address, max_tries = parse_cmd_line_args(argv)
    data_file = file(data_file, 'r')
    form_data = yaml.load(data_file)
    data_file.close()
    current_best = MAX_DATETIME
    best_office = ''
    number_of_exceptions = 0
    for i in range(0, max_tries):
        try:
            print "Attempt {number}".format(number=i+1)
            current_best, best_office = find_best_available_date(form_data, current_best, best_office, to_address)
        except Exception as e:
            if number_of_exceptions >= MAX_EXCEPTIONS:
                send_failure_email(str(e), to_address)
                exit()
            number_of_exceptions += 1
        sleep(sleep_time * 60)


if __name__ == '__main__':
    run(sys.argv[1:])
