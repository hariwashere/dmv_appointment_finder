<h3>dmv.py</h3>
dmv.py is a script to automatically find dmv appointment dates in CA. It searches various DMV offices for the
best available appointment dates and emails the user. You probably should not use this

<b>Requirements:</b>

requests, pyyaml, lxml

You can install them with:

    sudo easy_install (package_name)

<b>Usage:</b>

    python dmv.py (Options)

<b>Options:</b>

    -e, --email-address - Email address where you want the updates to be sent (Needs a local smtp server)
    -s, --sleep-time - Time to sleep before retrying
    -m, --maximum-tries - Maximum number of retries

You will also need to include a dmv_data.yaml and gmail_creds.yaml in the same folder as the script containing your license information and your gmail credentials so that the script can send a mail

<b>Data File:</b>

    'numberItems': 1
    'requestedTask': 'DTM'
    'safetyCourseCompletedSelection': 'TRUE'
    'firstName': YOUR_FIRST_NAME
    'lastName': YOUR_LAST_NAME
    'dlNumber': DRIVER_LICENSE_NUMBER
    'birthMonth': BIRTH_MONTH (append 0 if single digit)
    'birthDay': BIRTH_DAY
    'birthYear': BIRTH_YEAR
    'telArea': TELEPHONE_AREA_CODE
    'telPrefix': TELEPHONE_PREFIX
    'telSuffix': TELEPHONE_SUFFIX
    'resetCheckFields': true


<b>Gmail Credentials </b>

    username: USERNAME
    password: ********
