# -*- coding: utf-8 -*-
"""

  Bubble Tea Job Application for Nimble.


  FXIME: logging

"""
import os
import logging

import webapp2
from webapp2_extras import json
from webapp2_extras import sessions

from google.appengine.api import users
from google.appengine.ext import ndb

# some limits to the number of things returned by db queries to stop things getting crazy
MAX_FLAVOURS = 30
MAX_TEA_TYPES = 30
MAX_TEA_TOPPINGS = 30
MAX_TEA_SIZES = 6

# return this if someone's used the web api to do something successfully.
OK_RESPONSE = "OK"  # FIXME: debugging.. remove?

# FIXME: !!!
logging.getLogger().setLevel(logging.DEBUG)


# We set a parent key to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.
def bubble_tea_key(bubble_tea_name = 'default_bubble_tea'):
    return ndb.Key('Bubble_tea', bubble_tea_name)

#
# Data Model (uses google ndb).
#

class Customer(ndb.Model):
    """Customer details."""
    #userid = ndb.IntegerProperty()
    username = ndb.StringProperty()
    password = ndb.StringProperty(indexed = False)
    deleted = ndb.BooleanProperty(indexed = False, default = False)
    #banned = ndb.BooleanProperty(indexed = False)
    #email = ndb.StringProperty(indexed = False)
    #phone_number = ndb.StringProperty(indexed = False)
    #user_created_date = ndb.DateTimeProperty(indexed = False)


class TeaType(ndb.Model):
    """Tea type - one per tea order."""
    # human readable id
    name = ndb.StringProperty(indexed=True, required=True) 
    # display name
    verbose_name = ndb.StringProperty(indexed=False, required=True) 
    # use this to order items in lists (indexed so we can order queries using it)
    rank = ndb.IntegerProperty(indexed=True, default=10)
    # price
    cost = ndb.IntegerProperty(indexed=False) 

class TeaFlavour(ndb.Model):
    """Tea flavour - one per tea order."""
    # human readable id
    name = ndb.StringProperty(indexed=True, required=True)
    # display name
    verbose_name = ndb.StringProperty(indexed=False, required=True)
    # use this to order items in lists (indexed so we can order queries using it)
    rank = ndb.IntegerProperty(indexed=True, default=10)
    # price
    additional_cost = ndb.IntegerProperty(indexed=False) 
    
class TeaTopping(ndb.Model):
    """Tea topping - zero or more per tea order."""
    name = ndb.StringProperty(indexed = True)
    # display name
    verbose_name = ndb.StringProperty(indexed=False, required=True) 
    additional_cost = ndb.IntegerProperty()
    # use this to order items in lists (indexed so we can order queries using it)
    rank = ndb.IntegerProperty(indexed=True, default=10)

class TeaSize(ndb.Model):
    """Tea size - one per tea order.  Assumes an additive tea price model!!"""
    name = ndb.StringProperty(indexed = True)
    verbose_name = ndb.StringProperty(indexed=False, required=True) 
    additional_cost = ndb.IntegerProperty()
    # use this to order items in lists (indexed so we can order queries using it)
    rank = ndb.IntegerProperty(indexed=True, default=10)

class TeaOrder(ndb.Model):
    """A description of a cup of tea.  An order is a set of these."""
    tea_type = ndb.StructuredProperty(TeaType)
    tea_flavour = ndb.StructuredProperty(TeaFlavour)
    tea_toppings = ndb.StructuredProperty(TeaTopping, repeated=True) 
    tea_size = ndb.StructuredProperty(TeaSize)
    
class Order(ndb.Model):
    """A customer and a set of TeaOrders."""
    customer = ndb.StructuredProperty(Customer)
    tea_orders = ndb.LocalStructuredProperty(TeaOrder, repeated=True)
    date_time = ndb.DateTimeProperty(auto_now_add = True)

#
# Page Request Handlers
#


## class BaseHandler(webapp2.RequestHandler):
##     def dispatch(self):
##         # Get a session store for this request.
##         self.session_store = sessions.get_store(request=self.request)

##         try:
##             # Dispatch the request.
##             webapp2.RequestHandler.dispatch(self)
##         finally:
##             # Save all sessions.
##             self.session_store.save_sessions(self.response)

##     @webapp2.cached_property
##     def session(self):
##         # Returns a session using the default cookie key.
##         return self.session_store.get_session()


index_html = file("index.html").read()
class MainPage(webapp2.RequestHandler):
# class MainPage(BaseHandler):
    """
    The front page of the application.

    """    
    def get(self):
        self.response.out.write(index_html)
        return
        

#
# HTML Page Request Handlers
#
login_html = file("login.html").read()
class LoginPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(login_html)
        return
    
    
test_html = file("test.html").read()
class TestPage(webapp2.RequestHandler):
    def get(self):
        print test_html
        self.response.out.write(test_html)
        

#
# Control
#

#class DoLoginPage(BaseHandler):
class DoLoginPage(webapp2.RequestHandler):
    """Returns a json list of tea types from the database."""    
    def post(self):
        msg = json.decode(self.request.body)
        if 'username' not in msg:
            print("Request missing username.")            
            self.response.set_status(401)
            return

        if 'password' not in msg:
            print("Request missing password.")            
            self.response.set_status(401)
            return
            
        username = msg['username']
        password = msg['password']

        customers = Customer.query(Customer.username == username).fetch()
        if len(customers) == 0:
            # no such user
            print("Unauthorized access.")            
            self.response.set_status(401)
            return

        if len(customers) > 1:
            print("To many users!!.")  # should never happen
            self.response.set_status(401)
            return
        
        # get the customer record
        customer = customers[0]
        
        # check the password
        if customer.password != password:
            print("Incorrect password.")            
            self.response.set_status(401)
            return

        # successful login (return the customer key and username)
        customer_json = json.encode(
            {"username": username, "key": customer.key.urlsafe()})
        self.response.out.write(customer_json)
        return



class AddCustomerPage(webapp2.RequestHandler):
    """Adds a new customer."""

    def get(self):
        # get the get/post params
        params = self.request.params

        # check inputs
        for param in ("username", "password"):
            if param not in params:
                logging.debug("Malformed request adding Customer, missing %s." % param)
                self.response.set_status(400)
                return

        username = params["username"]
        password = params["password"]
        customer = Customer(parent = bubble_tea_key(),
                            username = username,
                            password = password)
        customer.put()
        
        self.response.out.write("Customer %s added" % customer.username)
        return



class AddTeaFlavourPage(webapp2.RequestHandler):
    def get(self):
        # get the get/post params
        params = self.request.params

        # check inputs
        for param in ("name", "verbose_name", "additional_cost", "rank"):
            if param not in params:
                logging.debug("Malformed request adding Tea Flavour, missing %s." % param)
                self.response.set_status(400)
                return
            
        name = params['name']
        verbose_name = params['verbose_name']
        rank = params['rank']
        additional_cost = self.request.params['additional_cost']

        try:
            additional_cost = int(additional_cost)
        except ValueError:
            logging.debug("Malformed request: want an int.")
            self.response.set_status(400)
            return

        try:
            rank = int(rank)
        except ValueError:
            logging.debug("Malformed request: want an int.")
            self.response.set_status(400)
            return
            
        # args are ok, add the new tea flavour
        tea_flavour = TeaFlavour(
            parent = bubble_tea_key(),
            name = name,
            additional_cost = additional_cost,
            rank = rank) 
        tea_flavour.put()
        self.response.out.write(OK_RESPONSE)
        return


class TeaFlavoursPage(webapp2.RequestHandler):
    """Returns a json list of tea flavours from the database."""    
    def get(self):
        query = TeaFlavour.query(ancestor = bubble_tea_key()).order(TeaFlavour.rank)
        flavours = query.fetch(MAX_FLAVOURS)
        # json encoding doesn't inclue the key by default (?!)
        flavours_json = json.encode(
            [dict(flavour.to_dict(), **dict(key=flavour.key.urlsafe()))
             for flavour in flavours])
        self.response.out.write(flavours_json)
        return


class TeaTypesPage(webapp2.RequestHandler):
    """Returns a json list of tea types from the database."""    
    def get(self):
        query = TeaType.query(ancestor = bubble_tea_key()).order(TeaType.rank)
        types = query.fetch(MAX_TEA_TYPES)
        types_json = json.encode(
            [dict(tea_type.to_dict(), **dict(key=tea_type.key.urlsafe()))
             for tea_type in types])               
        self.response.out.write(types_json)
        return

class TeaSizesPage(webapp2.RequestHandler):
    """Returns a json list of tea sizes from the database."""    
    def get(self):
        query = TeaSize.query(ancestor = bubble_tea_key()).order(TeaSize.rank)
        tea_sizes = query.fetch(MAX_TEA_SIZES)
        tea_sizes_json = json.encode(
            [dict(tea_size.to_dict(), **dict(key=tea_size.key.urlsafe()))
             for tea_size in tea_sizes])
        
        self.response.out.write(tea_sizes_json)
        return

class TeaToppingsPage(webapp2.RequestHandler):
    """Returns a json list of tea types from the database."""    
    def get(self):
        query = TeaTopping.query(ancestor = bubble_tea_key()).order(TeaTopping.rank)
        toppings = query.fetch(MAX_TEA_TOPPINGS)
        toppings_json = json.encode(
            [dict(topping.to_dict(), **dict(key=topping.key.urlsafe()))
             for topping in toppings])                       
        self.response.out.write(toppings_json)
        return


class OrdersPage(webapp2.RequestHandler):
    """Returns a json list of orders from the database."""    
    def get(self):
        query = Order.query(ancestor = bubble_tea_key()).order(TeaTopping.rank)
        orders = query.fetch(MAX_TEA_TOPPINGS)
        ## orders_json = json.encode(
        ##     [dict(topping.to_dict(), **dict(key=topping.key.urlsafe()))
        ##      for topping in toppings])                       
        ## self.response.out.write(toppings_json)
        return

class CustomersPage(webapp2.RequestHandler):
    """Returns a json list of customers from the database."""    
    def get(self):
        query = Customer.query(ancestor = bubble_tea_key()).order(Customer.username)
        customers = query.fetch()
        customers_json = json.encode(
            [dict(customer.to_dict(), **dict(key=customer.key.urlsafe()))
             for customer in customers])                       
        self.response.out.write(customers_json)
        return


class DeleteCustomerPage(webapp2.RequestHandler):
    """Deletes a customer from the db."""    

    def post(self):
        msg = json.decode(self.request.body)
        if 'customer_key' not in msg:
            print("Request missing customer key.")            
            self.response.set_status(400)
            return

        # get the customer model
        customer_key_str = msg["customer_key"]
        customer_key = ndb.Key(urlsafe = customer_key_str)
        customer_model = customer_key.get()        
        status_msg = "Customer %s deleted" % customer_model.username
        customer_key.delete()
        self.response.out.write(status_msg)
        return


class ChangePasswordPage(webapp2.RequestHandler):
    """Returns a json list of customers from the database."""    
    def post(self):

        msg = json.decode(self.request.body)
        print msg
        if 'customer_key' not in msg:
            print("Request missing customer key.")            
            self.response.set_status(400)
            return

        if 'new_password' not in msg:
            print("Request missing new password.")            
            self.response.set_status(400)
            return

        # get the customer model
        customer_key_str = msg["customer_key"]
        customer_key = ndb.Key(urlsafe = customer_key_str)
        customer_model = customer_key.get()        
        customer_model.password = msg["new_password"]
        customer_model.put()
        self.response.out.write("Password for %s changed" % customer_model.password)
        return



class ResetDBPage(webapp2.RequestHandler):
    """DEBUG: Returns the db to its initial state.."""    
    def get(self):
        # clear the tea types 
        query = TeaType.query(ancestor = bubble_tea_key())
        keys = query.fetch(keys_only=True)
        ndb.delete_multi(keys)

        # add the initial tea types back in
        tea_types = []
        for verbose_name, name, cost, rank in (
            ('Green Tea', 'green_tea', 300, 0),
            ('Black Tea', 'black_tea', 400, 1),
            ('Milk Tea', 'milk_tea', 500, 2)):            
            tea_type = TeaType(parent = bubble_tea_key(),
                               name = name,
                               verbose_name = verbose_name,
                               cost = cost,
                               rank = rank)
            tea_types.append(tea_type)            
        ndb.put_multi(tea_types)

        # clear the tea flavours 
        query = TeaFlavour.query(ancestor = bubble_tea_key())
        keys = query.fetch(keys_only=True)
        ndb.delete_multi(keys)

        # add the initial tea flavours back in
        tea_flavours = []
        for verbose_name, name, additional_cost, rank in (
            ('Straight Up', 'straight_up_flavour', 0, 0),
            ('Lemon', 'lemon_flavour', 20, 1),
            ('Passionfruit', 'passionfruit_flavour', 50, 2),
            ('Yoghurt', 'yoghurt_flavour', 30, 3)):
            tea_flavour = TeaFlavour(parent = bubble_tea_key(),
                                     name = name,
                                     verbose_name = verbose_name,
                                     additional_cost = additional_cost,
                                     rank = rank)
            tea_flavours.append(tea_flavour)            
        ndb.put_multi(tea_flavours)
        
        # clear the tea types 
        query = TeaTopping.query(ancestor = bubble_tea_key()) 
        keys = query.fetch(keys_only=True)
        ndb.delete_multi(keys)

        # add the initial tea types back in
        toppings = []
        for verbose_name, name, additional_cost, rank in (
            ('Boba', 'boba', 50, 0),
            ('Red Bean', 'red_bean', 80, 1),
            ('Ai You Jelly', 'ai_yu_jelly', 100, 2),
            ('Basil Seeds', 'basil_seeds', 70, 3)):            
            topping = TeaTopping(parent = bubble_tea_key(),
                                 name = name,
                                 verbose_name = verbose_name,
                                 additional_cost = additional_cost,
                                 rank = rank)
            toppings.append(topping)
        ndb.put_multi(toppings)

        # clear the tea sizes
        query = TeaSize.query(ancestor = bubble_tea_key()) 
        keys = query.fetch(keys_only=True)
        ndb.delete_multi(keys)

        # add the initial tea sizes back in
        tea_sizes = []
        for verbose_name, name, additional_cost, rank in (
            ('Small', 'small', -100, 0),
            ('Medium', 'medium', 0, 1),
            ('Large', 'large', 100, 2)):
            tea_size = TeaSize(parent = bubble_tea_key(),
                               name = name,
                               verbose_name = verbose_name,
                               additional_cost = additional_cost,
                               rank = rank)
            tea_sizes.append(tea_size)
        ndb.put_multi(tea_sizes)

        # clear the customers
        query = Customer.query(ancestor = bubble_tea_key())
        keys = query.fetch(keys_only=True)
        ndb.delete_multi(keys)

        # add the initial tea flavours back in
        customers = []
        for username, password in (
            ('blaize', 'blaize'),
            ('scott', 'scott'),
            ('phil', 'phil')):
            customer = Customer(parent = bubble_tea_key(),
                                username = username,
                                password = password)
            customers.append(customer)            
        ndb.put_multi(customers)
                       
        self.response.out.write(OK_RESPONSE)
        return
    

class PlaceOrderPage(webapp2.RequestHandler):
    """This is the bit that buys stuff!"""    

    @ndb.transactional
    def post(self):
        #params = self.request.params

        msg = json.decode(self.request.body)

        # get the customer model
        customer_key_str = msg["customer_key"]
        customer_key = ndb.Key(urlsafe = customer_key_str)
        customer_model = customer_key.get()

        # now unpack the order
        order = msg["order"]
        try:
            total_cost = int(msg["total_cost"])
        except ValueError:
            # FIXME: log something!!
            self.response.set_status(400)
            return
    
        # get all the tea models in the order
        tea_order_models = []
        for tea_order in order:

            tea_size_dict = tea_order['teaSize']
            tea_toppings_list = tea_order['teaToppings']
            price = tea_order['teaPrice']
            flavour_dict = tea_order['teaFlavour']
            tea_type_dict = tea_order['teaType']

            ## print "----"
            ## print "size: %s:" % tea_size_dict
            ## print "toppings: %s:" % tea_toppings_list
            ## print "price: %s:" % price
            ## print "flavour: %s:" % flavour_dict
            ## print "type: %s:" % tea_type_dict

            # get the tea type
            tea_type_key_str = tea_type_dict["key"]
            tea_type_key = ndb.Key(urlsafe = tea_type_key_str)
            tea_type_model = tea_type_key.get()

            # get the flavour
            tea_flavour_key_str = flavour_dict["key"]
            tea_flavour_key = ndb.Key(urlsafe = tea_flavour_key_str)
            tea_flavour_model = tea_flavour_key.get()

            # get the toppings
            tea_topping_models = []
            for topping in tea_toppings_list:
                topping_checked = topping["checked"]
                if topping_checked:
                    topping_key_str = topping["key"]            
                    topping_key = ndb.Key(urlsafe = topping_key_str)
                    topping_model = topping_key.get()
                    tea_topping_models.append(topping_model)

            # get the size
            tea_size_key_str = tea_size_dict["key"]
            tea_size_key = ndb.Key(urlsafe = tea_size_key_str)
            tea_size_model = tea_size_key.get()

            ## print "===="
            ## print tea_type_model
            ## print tea_flavour_model
            ## print tea_size_model
            ## for topping_model in tea_topping_models:
            ##     print "  " + str(topping_model)

            # there's one of these in the db for every tea ordered.
            tea_order = TeaOrder(parent = bubble_tea_key(),
                                 tea_type = tea_type_model,
                                 tea_flavour = tea_flavour_model,
                                 tea_toppings = tea_topping_models,
                                 tea_size = tea_size_model)
            tea_order_models.append(tea_order)

        # now make the order!    
        order_model = Order(parent = bubble_tea_key(),
                            customer = customer_model,
                            tea_orders = tea_order_models)        
        ndb.put_multi(tea_order_models)
        order_model.put()

        # ok!
        self.response.out.write(OK_RESPONSE)
        return

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': "bubble-tea-super-secret-key",
    }

application = webapp2.WSGIApplication(
    [
        ('/', MainPage),
        ('/login', LoginPage),
        ('/do_login', DoLoginPage),
        ('/add_customer', AddCustomerPage),
        ('/add_tea_flavour', AddTeaFlavourPage),
        ('/get_tea_flavours', TeaFlavoursPage),
        ('/get_tea_types', TeaTypesPage),
        ('/get_tea_toppings', TeaToppingsPage),
        ('/get_tea_sizes', TeaSizesPage),
        ('/get_customers', CustomersPage),
        ('/place_order', PlaceOrderPage),
        ('/change_password', ChangePasswordPage),
        ('/delete_customer', DeleteCustomerPage),
        ('/test', TestPage), # testing only
        ('/reset', ResetDBPage), # testing only    
        #('/logout', LogoutPage),
        ],
    config = config,
    debug = True) # FIXME: debug!!!



