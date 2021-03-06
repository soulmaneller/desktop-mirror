#!/usr/bin/env python
import wx
from crossplatform import CrossPlatform


class FrmAreaChooser(wx.Frame):
    def __init__(self, parent, id, title, callback=None):
        flag = wx.BORDER_NONE
        if CrossPlatform.get().is_linux():
            flag = wx.RESIZE_BORDER
        wx.Frame.__init__(self, parent, id, title,
                          style=flag | wx.STAY_ON_TOP |
                          wx.FRAME_NO_TASKBAR | wx.CLIP_CHILDREN)
        self._callback = callback

        self.rootPanel = wx.Panel(self)
        self.rootPanel.SetBackgroundColour(wx.Colour(0, 0, 0))

        centerPanel = wx.Panel(self.rootPanel)
        centerPanel.SetBackgroundColour(wx.Colour(0, 0, 0))

        innerPanel = wx.Panel(centerPanel)
        innerPanel.SetBackgroundColour(wx.Colour(0, 0, 0))

        rootBox = wx.BoxSizer(wx.HORIZONTAL)
        centerBox = wx.BoxSizer(wx.HORIZONTAL)
        innerBox = wx.BoxSizer(wx.VERTICAL)

        # I want this line visible in the CENTRE of the inner panel
        self.txt = wx.StaticText(innerPanel, label="")
        self.txt.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD))
        innerBox.Add(self.txt, 0, wx.ALL | wx.ALIGN_CENTER, border=0)
        innerPanel.SetSizer(innerBox)

        centerBox.Add(innerPanel, 1, wx.ALL | wx.ALIGN_CENTER, border=0)
        centerPanel.SetSizer(centerBox)

        rootBox.Add(centerPanel, 1, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND,
                    border=5)
        self.rootPanel.SetSizer(rootBox)

        rootBox.Fit(self)

        centerPanel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseEvents)
        innerPanel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseEvents)
        self.txt.Bind(wx.EVT_LEFT_DOWN, self.OnMouseEvents)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(40)  # in miliseconds
        self.background_colour = 0
        self.mouse_start_pos = None
        self.mouse_end_pos = None
        self.step = 0

        self.dialog = HintDialog(self, -1)
        #self.dialog.Center()
        #self.dialog.SetTransparent(100)
        self.dialog.Show()
        #self.dialog.SetTransparent(100)

    def update_border_color(self, event):
        if self.step >= 1:
            self.background_colour = (self.background_colour + 8) % 512
            if self.background_colour >= 256:
                colour = 511 - self.background_colour
            else:
                colour = self.background_colour
            self.rootPanel.SetBackgroundColour(wx.Colour(colour,
                                                         colour,
                                                         colour))

    def update_window_position_step_2_3(self, event):
        pos = wx.GetMousePosition()
        if self.mouse_end_pos is not None:
            if pos.x == self.mouse_end_pos.x and \
               pos.y == self.mouse_end_pos.y:
                return
        start = self.mouse_start_pos
        x = pos.x if pos.x < start.x else start.x
        y = pos.y if pos.y < start.y else start.y
        w = pos.x if pos.x > start.x else start.x
        h = pos.y if pos.y > start.y else start.y
        #w = x + 10 if (w - x) <= 10 else w + 1
        #h = y + 10 if (h - y) <= 10 else h + 1
        w = w + 1
        h = h + 1
        self.SetPosition((x, y))
        self.SetSize((w - x, h - y))
        self.mouse_end_pos = pos
        #print 'OnTimer, {} {} {} {}'.format(x, y, w - x, h - y)

    def update_window_position(self, event):
        if self.step == 0:
            pos = wx.GetMousePosition()
            self.SetPosition((pos.x, pos.y))
            self.SetSize((1, 1))
            self.mouse_start_pos = pos
        elif self.step == 1:
            pos = wx.GetMousePosition()
            start = self.mouse_start_pos
            x = pos.x if pos.x < start.x else start.x
            y = pos.y if pos.y < start.y else start.y
            w = pos.x if pos.x > start.x else start.x
            h = pos.y if pos.y > start.y else start.y
            if (w - x) >= 10 or (h - y) >= 10:
                self.step = 2
        elif self.step >= 2 and self.step <= 3:
            self.update_window_position_step_2_3(event)

    def OnTimer(self, event):
        self.update_border_color(event)
        self.update_window_position(event)
        is_left_down = wx.GetMouseState().LeftDown()

        # start point
        if self.step == 0 and is_left_down:
            self.txt.SetLabel('')
            self.dialog.Close(True)

        # end point
        if self.step == 3 and not is_left_down:
            #self.txt.SetLabel('Confirm?')
            self.step = 7
            self.Close(True)

        # confirm
        if self.step == 5 and not is_left_down:
            self.Close(True)

        # increment
        odd = (self.step % 2) == 1
        if not odd and is_left_down:
            self.step += 1
        elif odd and not is_left_down:
            self.step += 1

    def OnMouseEvents(self, e):
        self.step = 7
        self.Close(True)

    def OnClose(self, event):
        if self.step >= 7:
            pos = self.mouse_end_pos
            start = self.mouse_start_pos
            x = pos.x if pos.x < start.x else start.x
            y = pos.y if pos.y < start.y else start.y
            w = pos.x if pos.x > start.x else start.x
            h = pos.y if pos.y > start.y else start.y
            #print '{} {} {} {}'.format(x, y, w - x, h - y)
            if self._callback is not None:
                self._callback((x, y, w - x, h - y))
        self.Destroy()


class HintDialog(wx.Dialog):
    def __init__(self, parent, id, title=""):
        wx.Dialog.__init__(self, parent, id, title,
                           style=wx.STAY_ON_TOP | wx.BORDER_STATIC |
                           wx.FRAME_NO_TASKBAR | wx.CLIP_CHILDREN)

        self.rootPanel = wx.Panel(self)
        self.rootPanel.SetBackgroundColour(wx.Colour(0, 0, 0))

        innerBox = wx.BoxSizer(wx.VERTICAL)

        self.txt = wx.StaticText(self.rootPanel, -1,
                                 'Draw a retangular to select area')
        self.txt.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD))
        self.txt.SetForegroundColour(wx.Colour(255, 255, 255))
        innerBox.Add(self.txt, 0, wx.ALL | wx.ALIGN_CENTER, border=20)
        self.rootPanel.SetSizer(innerBox)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        innerBox.Fit(self)

    def OnClose(self, event):
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        frame = FrmAreaChooser(None, -1, 'Live Area')
        frame.Show(True)
        frame.Center()
        frame.SetTransparent(100)
        return True

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
