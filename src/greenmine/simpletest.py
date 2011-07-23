# -*- coding: utf-8 -*-

import os, os.path, sys
root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(root_path, '..'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from django.test.client import Client
client = Client()


def test_request_password():
    response = client.get("/api/request/password?username=andrei&email=niwi@niwi.be")
    print response

def test_upload_user_photo():
    response = client.post("/api/user/edit", {'username':'andrei', 'photo': open('/home/niwi/mifoto.png')})
    print response


if __name__ == '__name__':
    pass
