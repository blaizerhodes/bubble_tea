import wx

from view.admin import AdminFrame


class LoginDialog(wx.Dialog):
    """
    Class to define login dialog

    """
 
    def __init__(self, control):        
        wx.Dialog.__init__(self, None, title = "Login")

        # save referene to the controller for later and listen for events
        self.control = control
        self.control.add_listener(self)
 
        # widgets
        user_label = wx.StaticText(self, label="Username:")
        self.user = wx.TextCtrl(self)
        password_label = wx.StaticText(self, label="Password:")
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
        btn = wx.Button(self, label="Login")
        btn.Bind(wx.EVT_BUTTON, self.onLogin)
        btn.SetFocus()

        # layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(user_label)
        hbox.Add(self.user, wx.EXPAND)
        vbox.Add(hbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(password_label)
        hbox.Add(self.password, wx.EXPAND)
        vbox.Add(hbox)
  
        vbox.Add(btn, 0, wx.ALL|wx.CENTER, 5)         
        self.SetSizer(vbox)
        self.Fit()
        return
 

    def onLogin(self, event):
        """
        Check credentials and login
        
        """
        username = self.user.GetValue()
        password = self.password.GetValue()
        self.control.login(username, password)
        
        ## stupid_password = "pa$$w0rd!"
        ## if user_password == stupid_password:
        ## else:
        ##     print "Username or password is incorrect!"
        return

    def OnExit(self):
        # close the frame when the little x thing is clicked.
        print "----"
        self.Destroy()
        self.Close(True)
        return


    def on_logged_in(self):
        admin_frame = AdminFrame(control = self.control)
        admin_frame.Show(True)
        self.Destroy()
        return
