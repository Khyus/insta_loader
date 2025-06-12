from redmail import gmail

gmail.username = 'sagelensanalytics@gmail.com'
gmail.password = 'opveoyjshlvwowae'

gmail.send(
    subject='Example email',
    receivers=['fadhilatize@gmail.com'],
    text='Hi, this is an email.'
)