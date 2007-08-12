from django.conf import settings

def caslogin(user):
    print "Hello!"
    print "User: ", user

def get_applications(clean=True):
    if clean:
        return [".".join(app.split(".")[1:]) for app in settings.INSTALLED_APPS if not app.startswith('django')]
    else:
        return [app for app in settings.INSTALLED_APPS if not app.startswith('django')]
