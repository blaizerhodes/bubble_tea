"""

  Using this type of MVC (no filtering stuff back up the control):

    View -> Control -> Model 
     ^                   | 
     +-------------------+

"""

class Control:

    def __init__(self, model):
        self.model = model
        self.listeners = []
        return


    def add_listener(self, listener):
        self.model.add_listener(listener)
        return

    def get_customers(self):
        self.model.get_customers()
        return

    def add_customers_listener(self, listener):
        self.model.add_customers_listener(listener)
        return

    def change_customer_password(self, customer_key, new_pwd):
        self.model.change_customer_password(customer_key, new_pwd)
        return

    def add_status_listener(self, status_listener):
        self.model.status_listeners.append(status_listener)
        return        
    
    def login(self, username, password):
        """async login."""
        self.model.login(username, password)
        return
        
    def delete_customer(self, customer_key):
        self.model.delete_customer(customer_key)
        return

    def add_customer(self, username, password):
        self.model.add_customer(username, password)
        return
