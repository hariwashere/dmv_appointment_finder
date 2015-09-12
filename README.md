dmv.py is a script to automatically find dmv appointment dates in CA. It searches various DMV offices for the
best available appointment dates and emails the user. You probably should not use this

Requirements:
requests, pyyaml, lxml

You can install them with:
    sudo easy_install <package_name>

You would also need to setup a local smtp server if you want to be emailed (see http://stackoverflow.com/questions/14570471/local-smtp-server-to-send-mail)

Usage:
    python dmv.py <Options>

Options:
    -e, --email-address - Email address where you want the updates to be sent (Needs a local smtp server)
    -d, --data-file - A .yaml file containing your details. See format below
    -s, --sleep-time - Time to sleep before retrying
    -m, --maximum-tries - Maximum number of retries

Data File:
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


