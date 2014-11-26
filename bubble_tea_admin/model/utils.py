"""

    Deal with the http requests/responses.
    FIXME: This is hacky.. needs security and should be asynchronous.
    
"""
import urllib
import urllib2
import json

BUBBLE_URL = "http://bubble-tea.appspot.com/"
#BUBBLE_URL = "http://localhost:8080/"

def get_customers(customers_cb):
    response = urllib2.urlopen(BUBBLE_URL + "get_customers")
    json_msg = response.read()
    msg = json.loads(json_msg)
    
    # just pretend to be asynchronous for the moment FIXME: sometime
    customers_cb(msg)
    return


def change_customer_password(customer_key, new_pwd):
    response = urllib2.urlopen(BUBBLE_URL + "change_password",
                               json.dumps({"customer_key": customer_key,
                                           "new_password": new_pwd}))
    msg = response.read()
    return msg  # a human readable string


def delete_customer(customer_key):
    response = urllib2.urlopen(BUBBLE_URL + "delete_customer",
                               json.dumps({"customer_key": customer_key}))
    msg = response.read()
    return msg


def add_customer(username, password):
    # wrap up args for a get request
    args = {"username": username, "password": password}
    encoded_args = urllib.urlencode(args)    
    response = urllib2.urlopen(BUBBLE_URL + "add_customer?" + encoded_args)
    msg = response.read()
    return msg
