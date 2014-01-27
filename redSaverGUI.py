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
import redSaver
import praw


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


class RedSaverWindow(wx.Frame):

    r = praw.Reddit(user_agent = 'RedditImageSaver by /u/neph001')

    def __init__(self, *args, **kwargs):
        super(RedSaverWindow, self).__init__(*args, **kwargs)
        self.InitUI()

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

        helpMenu.Append(101, '&About')

        menubar.Append(fileMenu, '&File')
        menubar.Append(helpMenu, '&Help')


        self.SetMenuBar(menubar)
        self.CreateStatusBar()

        vbox = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self, -1)

        self.loginStatusText = wx.StaticText(panel, label="Not logged in", style=wx.ALIGN_LEFT)
        vbox.Add(self.loginStatusText, flag=wx.ALL, border=5)



        panel.SetSizer(vbox)





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

    def signOut(self, e):
        self.r.clear_authentication()
        if not self.r.is_logged_in():
            self.loginStatusText.SetLabelText("Logged out successfully.")
            self.signInButton.Enable(True)
            self.signOutButton.Enable(False)



def main():
    app = wx.App()
    frame = RedSaverWindow(None, -1, 'Reddit Image Saver')
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()