__author__ = 'north1'
"""
This is a GUI implementation of RedditImageSaver
(which itself might not be 100% working but it's a
bitch to test on large data sets without a GUI).

RedditImageSaver( RIS ) is designed to allow a user
to set a local destination for all images that user
has saved in a particular subreddit, for as many
subreddits as desired.

Example: Say I like to download a lot of wallpapers for use in windows.
(Note: this should work cross-platform, just giving an exmaple because
windows does that neat wallpaper slideshow thing)
I like to keep them organized according to catagory, and those catagories
happen to line up roughly with subreddits.

This utility could be set to download all reddit saved images from the subreddit
/r/spaceporn to E:\user\Pictures\wallpapers\space, and all images from
/r/CityPorn to E:\user\Pictures\wallpapers\urban, etc etc.

Feel free to edit the source, fork, contribute, whatever you want, but please let me know.
My github username is north1. My reddit username is /u/neph001

If you like it, please consider donating BTC:
1LEWTykyZzrtiQb5xChu9aK2R55iaxEgC4
"""


import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ColumnSorterMixin
import redSaver
import praw
import sys


class SignInDialog(wx.Dialog):
    def __init__(self, reddit, errorText=""):
        super(SignInDialog, self).__init__(None, title="Sign In To Reddit")
        self.r = reddit
        self.error = errorText
        self.InitUI()
        self.SetSize(self.GetEffectiveMinSize())
        self.SetTitle("Sign In To Reddit")

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        sb = wx.StaticBox(panel, label='Enter your Reddit credentials:')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        self.errorText = wx.StaticText(self, label=self.error)
        self.errorText.SetForegroundColour((255, 0, 0))
        self.usernameText = wx.TextCtrl(panel, value="Username")
        self.passwordText = wx.TextCtrl(panel, value="Password", style=wx.TE_PASSWORD)
        sbs.Add(self.errorText, flag=wx.LEFT, border=5)
        sbs.Add(self.usernameText, flag=wx.CENTER, border=5)
        sbs.Add(self.passwordText, flag=wx.CENTER, border=5)


        panel.SetSizer(sbs)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        signInButton = wx.Button(self, label='Sign In')
        cancelButton = wx.Button(self, label='Cancel')
        hbox.Add(signInButton)
        hbox.Add(cancelButton)

        vbox.Add(panel, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10)

        self.SetSizer(vbox)

        signInButton.Bind(wx.EVT_BUTTON, self.signIn)
        cancelButton.Bind(wx.EVT_BUTTON, self.onClose)


    def signIn(self, e):
        try:
            self.r.login(username=self.usernameText.GetValue(), password=self.passwordText.GetValue())
        except praw.errors.APIException:
            pass

        if not self.r.is_logged_in():
            self.errorText.SetLabelText("Invalid Username or Password")
            self.SetSize(self.GetEffectiveMinSize())
        else:
            self.Destroy()


    def onClose(self, e):
        self.Destroy()

class RuleListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, ColumnSorterMixin):
    def __init__(self, parent, rules={}):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        #ColumnSorterMixin.__init__(self, len(rules))
        #self.itemDataMap = rules

    def GetListCtrl(self):
        return self

class RedSaverWindow(wx.Frame):

    r = praw.Reddit(user_agent = 'RedditImageSaver by /u/neph001')
    saver = redSaver.RedSaver(r)

    def __init__(self, *args, **kwargs):
        super(RedSaverWindow, self).__init__(*args, **kwargs)
        self.InitUI()
        self.SetSize((500,600))

    def InitUI(self):
        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        helpMenu = wx.Menu()

        self.signInButton = wx.MenuItem(fileMenu, 101, 'Sign &In', 'Sign in to Reddit')
        self.Bind(wx.EVT_MENU, self.signIn, self.signInButton)
        self.signOutButton = wx.MenuItem(fileMenu, 102, 'Sign &Out', 'Sign out of your Reddit Account')
        self.signOutButton.Enable(False)
        self.Bind(wx.EVT_MENU, self.signOut, self.signOutButton)
        quitButton = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit', 'Exit Reddit Image Saver')
        self.Bind(wx.EVT_MENU, self.onQuit, quitButton)

        fileMenu.AppendItem(self.signInButton)
        fileMenu.AppendItem(self.signOutButton)
        fileMenu.AppendSeparator()
        fileMenu.AppendItem(quitButton)

        self.aboutButton = wx.MenuItem(helpMenu, 103, '&About')
        #self.Bind(wx.EVT_MENU, self.onAbout, self.aboutButton)
        helpMenu.Append(103, '&About')

        menubar.Append(fileMenu, '&File')
        menubar.Append(helpMenu, '&Help')


        self.SetMenuBar(menubar)
        self.CreateStatusBar()

        vbox = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self, -1)

        self.loginStatusText = wx.StaticText(panel, label="Not logged in", style=wx.ALIGN_LEFT)
        vbox.Add(self.loginStatusText, flag=wx.ALL, border=5)

        initRules = self.saver.loadRules()
        self.ruleList = RuleListCtrl(panel, rules=initRules)
        self.ruleList.InsertColumn(0, 'Subreddit', wx.LIST_FORMAT_LEFT, width=80)
        self.ruleList.InsertColumn(1, 'Destination Path', wx.LIST_FORMAT_LEFT, 90)
        for subreddit, dest in initRules.items():
            index = self.ruleList.InsertStringItem(sys.maxint, subreddit)
            self.ruleList.SetStringItem(index, 1, dest)
            #self.ruleList.SetItemData(index, count)
        vbox.Add(self.ruleList, flag=wx.EXPAND|wx.ALL, border=5)

        self.removeButton = wx.Button(panel, label="Remove Selected")
        self.removeButton.Bind(wx.EVT_BUTTON, self.onRemove)
        self.removeButton.Enable(False)
        self.ruleList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onRuleSelected)
        vbox.Add(self.removeButton)

        addRuleStaticBox = wx.StaticBox(panel, label="Add rule:")
        addBoxSizer = wx.StaticBoxSizer(addRuleStaticBox, wx.HORIZONTAL)

        self.subredditEntry = wx.TextCtrl(panel, value="Subreddit")
        addBoxSizer.Add(self.subredditEntry, flag=wx.EXPAND, border=5)

        self.destEntry = wx.TextCtrl(panel, value="Destination")
        addBoxSizer.Add(self.destEntry,flag=wx.EXPAND, border=5)

        destBrowse = wx.Button(panel, label="Browse...", style=wx.BU_EXACTFIT)
        destBrowse.Bind(wx.EVT_BUTTON, self.onBrowse)
        addBoxSizer.Add(destBrowse, border=5)

        addRuleButton = wx.Button(panel, label="Add Rule", style=wx.BU_EXACTFIT)
        addRuleButton.Bind(wx.EVT_BUTTON, self.onAdd)
        addBoxSizer.Add(addRuleButton, flag=wx.RIGHT, border=5)

        vbox.Add(addBoxSizer, flag=wx.EXPAND, border=5)

        downloadBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.downloadButton = wx.Button(panel, label="Download Images", style=wx.BU_EXACTFIT)
        self.downloadButton.Bind(wx.EVT_BUTTON, self.onDownload)
        self.downloadButton.Enable(False)
        downloadBoxSizer.Add(self.downloadButton, border=5)
        self.unsaveCheck = wx.CheckBox(panel, label="Unsave downloaded submissions?")
        self.unsaveCheck.SetValue(False)
        downloadBoxSizer.Add(self.unsaveCheck, flag=wx.ALIGN_CENTER, border=5)

        vbox.Add(downloadBoxSizer, flag=wx.EXPAND, border=5)

        panel.SetSizer(vbox)

    def onDownload(self, e):
        print self.saver.r.is_logged_in()
        self.saver.save(gui=True, unsave=self.unsaveCheck.GetValue())

    def onRuleSelected(self, e):
        self.removeButton.Enable(True)

    def onRemove(self, e):
        current = self.ruleList.GetFirstSelected()
        for i in range(self.ruleList.GetSelectedItemCount()):
            self.saver.deleteRule(gui=True, subreddit=self.ruleList.GetItemText(current))
            next = self.ruleList.GetNextSelected(current)
            self.ruleList.DeleteItem(current)
            current = next

    def onAdd(self, e):
        self.saver.makeRule(gui=True, subreddit=self.subredditEntry.GetValue(), dir=self.destEntry.GetValue())
        if (self.subredditEntry.GetValue() != "Subreddit" and self.destEntry.GetValue() != "Destination") and (self.subredditEntry.GetValue() != "" and self.destEntry.GetValue() != ""):
            index = self.ruleList.InsertStringItem(sys.maxint, self.subredditEntry.GetValue())
            self.ruleList.SetStringItem(index, 1, self.destEntry.GetValue())

    def onBrowse(self, e):
        dialog = wx.DirDialog(None, "Choose a folder:", style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.destEntry.SetValue(dialog.GetPath())
        dialog.Destroy()

    def onQuit(self, e):
        self.Close()

    def signIn(self, e):
        dialog = SignInDialog(self.r)
        dialog.ShowModal()
        dialog.Destroy()
        if self.r.is_logged_in():
            self.loginStatusText.SetLabelText("Logged in as /u/" + self.r.user.name + ".")
            self.signInButton.Enable(False)
            self.signOutButton.Enable(True)
            self.downloadButton.Enable(True)

    def signOut(self, e):
        self.r.clear_authentication()
        if not self.r.is_logged_in():
            self.loginStatusText.SetLabelText("Logged out successfully.")
            self.signInButton.Enable(True)
            self.signOutButton.Enable(False)
            self.downloadButton.Enable(False)



def main():
    app = wx.App()
    frame = RedSaverWindow(None, -1, 'Reddit Image Saver')
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()