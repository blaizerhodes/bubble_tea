import  sys
import wx

from view.customers_panel import CustomersPanel

class AdminNotebook(wx.Notebook):
    def __init__(self, parent, control):
        wx.Notebook.__init__(self, parent, id = wx.ID_ANY, size=(21,21), style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             # | wx.NB_MULTILINE
                             )

        ## p = wx.Panel(self, id = wx.ID_ANY)
        ## self.AddPage(p, text = "Manage Orders")

        ## p = wx.Panel(self, id = wx.ID_ANY)
        ## self.AddPage(p, text = "Manage Customers")
        
        ## p = wx.Panel(self, id = wx.ID_ANY)
        ## self.AddPage(p, text = "Manage Teas")

        ## p = wx.Panel(self, id = wx.ID_ANY)
        ## self.AddPage(p, text = "Manage Flavours")

        customers_panel = CustomersPanel(self, control = control) 
        self.AddPage(customers_panel, text = "Manage Customers")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

        # set focus so the left and right arrow keys work
        self.SetFocus()
        return 

            
    ## def makeColorPanel(self, color):
    ##     p = wx.Panel(self, -1)
    ##     #win = ColorPanel.ColoredPanel(p, color)
    ##     #p.win = win
    ##     #def OnCPSize(evt, win=win):
    ##     #    win.SetPosition((0,0))
    ##     #    win.SetSize(evt.GetSize())
    ##     #p.Bind(wx.EVT_SIZE, OnCPSize)
    ##     return p

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()
        return

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()
        return


    
class AdminFrame(wx.Frame):
    """"""
 
    def __init__(self, control):
        wx.Frame.__init__(self, None, wx.ID_ANY, title = "Bobble Tee Bonanza Admin")
        notebook = AdminNotebook(parent = self, control = control)
        control.add_status_listener(self)

        # add a menu
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        item = file_menu.Append(wx.ID_EXIT, '&Quit', 'Quit application')
        menubar.Append(file_menu, '&File')        
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnQuit, item)

        self.status_bar = self.CreateStatusBar()        
        self.Maximize()
        return

      
    def OnQuit(self, e):
        self.Close()
        return
 
    def on_status_changed(self, status_msg):
        print status_msg
        self.status_bar.SetStatusText(str(status_msg))
        return
