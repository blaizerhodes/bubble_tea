from __future__ import absolute_import

import model
print model.__file__
from model import utils



#LOGIN_URL = 'http://localhost:8080/_ah/login'

class Model:

    def __init__(self):        
        self.listeners = []        
        self.customer_listeners = []
        self.status_listeners = []
        return

    def add_listener(self, listener):
        self.listeners.append(listener)
        return

    def login(self, customername, password):
        # FIXME: everyone logs in .. yay!
        self.logged_in() # Fake async for the moment
        return    

    def logged_in(self):
        for listener in self.listeners:
            listener.on_logged_in()
        return
        

    #
    # Customer Listeners 
    #
    def get_customers(self):
        utils.get_customers(self.get_customers_cb)
        return

    def get_customers_cb(self, customers):
        for customer_listener in self.customer_listeners:
            # following method needs to be implemented by customer listeners
            customer_listener.update_customers(customers) 
        return

    def add_customers_listener(self, customer_listener):
        self.customer_listeners.append(customer_listener)
        return
        
    def change_customer_password(self, customer_key, new_pwd):
        response = utils.change_customer_password(customer_key, new_pwd)
        self.set_status(response)
        return


    #
    # Status listener stuff
    #
    def add_status_listener(self, status_listener):
        self.status_listeners.append(status_listener)
        return
        
    def set_status(self, status_msg):
        for status_listener in self.status_listeners:
            status_listener.on_status_changed(status_msg)
        return
        
        

    #
    # Operations
    #
    def delete_customer(self, customer_key):
        msg = utils.delete_customer(customer_key)
        self.set_status(msg)
        self.get_customers()
        return

    def add_customer(self, username, pwd):
        msg = utils.add_customer(username, pwd)
        self.set_status(msg)
        self.get_customers()
        return 
        
