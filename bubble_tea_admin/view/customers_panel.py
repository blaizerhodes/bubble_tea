import wx
import  wx.lib.newevent

from wx.lib.agw.ultimatelistctrl import UltimateListItem, UltimateListCtrl
import wx.lib.agw.ultimatelistctrl as ULC

# as UlListControl

LIST_AUTOSIZE_FILL = -3


class PasswordDialog(wx.Dialog):
    
    def __init__(self, parent, control, customer_key):
        wx.Dialog.__init__(self, parent = parent)

        # save for later
        self.control = control
        self.customer_key = customer_key
            
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.pwd = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sb = wx.StaticBox(panel, label='Enter New Password')
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)        
        hbox1.Add(sb)
        hbox1.Add(self.pwd, flag=wx.LEFT, border=5)        
        panel.SetSizer(hbox1)
       
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(panel, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)
        
        okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

        self.SetSize((250, 200))
        self.SetTitle("Change Password")
        self.Fit()
        return

    def OnOK(self, event):
        print self.customer_key
        print self.pwd.GetValue()
        self.control.change_customer_password(self.customer_key, self.pwd.GetValue())        
        self.Destroy()
        return
                       
    def OnClose(self, e):        
        self.Destroy()
        return
        
        


class AddCustomerDialog(wx.Dialog):
    
    def __init__(self, parent, control):
        wx.Dialog.__init__(self, parent = parent)

        # save for later
        self.control = control
            
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.user = wx.TextCtrl(panel)
        self.pwd = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        user_sb = wx.StaticBox(panel, label='Username')
        pwd_sb = wx.StaticBox(panel, label='Password')
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)        
        hbox1.Add(user_sb)
        hbox1.Add(self.user, flag=wx.LEFT, border=5)        
        hbox1.Add(pwd_sb)
        hbox1.Add(self.pwd, flag=wx.LEFT, border=5)        
        panel.SetSizer(hbox1)
       
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(panel, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)
        
        okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

        self.SetSize((250, 200))
        self.SetTitle("Change Password")
        self.Fit()
        return

    def OnOK(self, event):
        self.control.add_customer(self.user.GetValue(), self.pwd.GetValue())        
        self.Destroy()
        return
                       
    def OnClose(self, e):        
        self.Destroy()
        return
        
        


class CustomersPanel(wx.Panel):
 
    def __init__(self, parent, control):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
 
        # Add a panel so it looks the correct on all platforms
        self.index = 0

        self.list_ctrl = UltimateListCtrl(self,
                                          agwStyle = wx.LC_REPORT 
                                          | wx.LC_VRULES
                                          | wx.LC_HRULES 
                                          | ULC.ULC_REPORT
                                          | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        
        self.list_ctrl.InsertColumn(0, 'No#')
        self.list_ctrl.InsertColumn(1, 'Username')
        self.list_ctrl.InsertColumn(2, 'Key')
        self.list_ctrl.InsertColumn(3, 'Edit')
        self.list_ctrl.InsertColumn(4, 'Delete')
        #self.list_ctrl.InsertColumn(2, 'Key', width = LIST_AUTOSIZE_FILL)
        
        btn = wx.Button(self, label="Add Customer")
        btn.Bind(wx.EVT_BUTTON, self.add_customer)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, proportion = 1, flag = wx.ALL|wx.EXPAND, border = 5)
        sizer.Add(btn, proportion = 0, flag = wx.ALL|wx.ALIGN_RIGHT, border = 5)
        self.SetSizer(sizer)

        # keep a handle on this (do this last)
        self.control = control
        self.control.add_customers_listener(self)
        self.control.get_customers()        
        return
        
 
    def add_customer(self, event):
        add_customer_dialog = AddCustomerDialog(parent = self,
                                                control = self.control)
        add_customer_dialog.ShowModal()
        return

    def change_password(self, event):
        button = event.GetEventObject()        
        customer_key = button.key
        password_dialog = PasswordDialog(parent = self,
                                         control = self.control,
                                         customer_key = customer_key)
        password_dialog.ShowModal()
        return
    
    def delete_customer(self, event):
        button = event.GetEventObject()        
        customer_key = button.key
        self.control.delete_customer(customer_key)
        return

    def update_customers(self, customers):
        self.list_ctrl.DeleteAllItems()
        self.index = 0
        for customer in customers:
            key = customer["key"]
            self.list_ctrl.InsertStringItem(self.index, str(self.index))
            self.list_ctrl.SetStringItem(self.index, 1, customer["username"])
            self.list_ctrl.SetStringItem(self.index, 2, key)
            button = wx.Button(self.list_ctrl, id=wx.ID_ANY, label="Change Password")
            button.key = key
            self.list_ctrl.SetItemWindow(self.index, col=3, wnd=button, expand=True)            
            button.Bind(wx.EVT_BUTTON, self.change_password)
            
            button = wx.Button(self.list_ctrl, id=wx.ID_ANY, label="Delete")
            self.list_ctrl.SetItemWindow(self.index, col=4, wnd=button, expand=True)
            button.key = key
            button.Bind(wx.EVT_BUTTON, self.delete_customer)
            self.index += 1
        return
            
