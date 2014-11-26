#!/usr/bin/env python
import wx

from model.model import Model
from control.control import Control
from view.login import LoginDialog


if __name__ == "__main__":
    
    app = wx.App(False) 
    #frame = wx.Frame(None, wx.ID_ANY, "Bobble Tee Bonanza Admin")

    model = Model()
    control = Control(model = model)
    
    # Ask user to login
    dlg = LoginDialog(control = control)
    dlg.ShowModal()
     
    app.MainLoop()
