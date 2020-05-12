class Config(object):

    # this currently does nothing; CSRF doesn apply if forms aren't posted.
    # if we switch to aform post pattern then this will be needed to send
    # forms to the backend through fetch/ajax
    SECRET_KEY = "this-is-just-a-test"
