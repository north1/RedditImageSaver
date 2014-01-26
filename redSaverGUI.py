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
        self.menubar = wx.MenuBar()

        self.fileMenu = wx.Menu()
        self.helpMenu = wx.Menu()

        self.signInButton = wx.MenuItem(self.fileMenu, 101, 'Sign &In', 'Sign in to Reddit')
        self.Bind(wx.EVT_MENU, self.signIn, self.signInButton)
        self.signOutButton = wx.MenuItem(self.fileMenu, 102, 'Sign &Out', 'Sign out of your Reddit Account')
        self.signOutButton.Enable(False)
        self.Bind(wx.EVT_MENU, self.signOut, self.signOutButton)
        self.quitButton = wx.MenuItem(self.fileMenu, wx.ID_EXIT, '&Quit', 'Exit Reddit Image Saver')
        self.Bind(wx.EVT_MENU, self.onQuit, self.quitButton)

        self.fileMenu.AppendItem(self.signInButton)
        self.fileMenu.AppendItem(self.signOutButton)
        self.fileMenu.AppendSeparator()
        self.fileMenu.AppendItem(self.quitButton)

        self.helpMenu.Append(101, '&About')

        self.menubar.Append(self.fileMenu, '&File')
        self.menubar.Append(self.helpMenu, '&Help')


        self.SetMenuBar(self.menubar)
        self.CreateStatusBar()


    def onQuit(self, e):
        self.Close()

    def signIn(self, e):
        dialog = SignInDialog(self.r)
        dialog.ShowModal()
        dialog.Destroy()
        if self.r.is_logged_in():
            self.signInButton.Enable(False)
            self.signOutButton.Enable(True)

    def signOut(self, e):
        #What the flying fuck. praw doesn't have the ability to log out once logged in.
        #self.signInButton.Enable(True)
        #self.signOutButton.Enable(False)

        wx.MessageBox('Sorry, praw ("Python Reddit API Wrapper") doesn\'t currently have a way to log out.\n'
                      'As a result, if you want to sign out and into a different account, you will need to\n'
                      'exit the application and launch it again. I am planning on modifying praw myself to\n'
                      'fix this soon.', 'Sorry', wx.OK|wx.ICON_INFORMATION)



def main():
    app = wx.App()
    frame = RedSaverWindow(None, -1, 'Reddit Image Saver')
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()