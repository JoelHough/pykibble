import wx

selected_id = None
class FoodSelectionFrame(wx.Frame):

    def add_to_tree(self, parent, name, tree):
        new_parent = self.tree.AppendItem(parent, name, data = wx.TreeItemData(tree[0]))
        if not tree[0] == None:
            self.values[new_parent] = tree[0]

        for key in sorted(tree[1].keys()):
            self.add_to_tree(new_parent, key, tree[1][key])

    def __init__(self, parent, id, title, food_tree):
        self.values = dict()
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(450, 350))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self, -1)
        panel2 = wx.Panel(self, -1)

        self.tree = wx.TreeCtrl(panel1, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)

        # Append ALL THE THINGS
        root = self.tree.AddRoot('sr24')
        for key in sorted(food_tree.keys()):
            self.add_to_tree(root, key, food_tree[key])
        
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
        self.display = wx.StaticText(panel2, -1, '', (10,10), style=wx.ALIGN_CENTRE)
        vbox.Add(self.tree, 1, wx.EXPAND)
        hbox.Add(panel1, 1, wx.EXPAND)
        hbox.Add(panel2, 1, wx.EXPAND)
        panel1.SetSizer(vbox)
        self.SetSizer(hbox)
        self.Centre()

    def OnSelChanged(self, event):
        global selected_id
        item = event.GetItem()
        text = ''
        food = self.tree.GetItemData(item).GetData()
        if food == None:
            text = self.tree.GetItemText(item)
            selected_id = None
        else:
            text = str(food.id) + ': ' + str(food)
            selected_id = food.id
        self.display.SetLabel(text)

class FoodSelectorApp(wx.App):
    def __init__(self, id, food_tree):
        self.food_tree = food_tree
        wx.App.__init__(self, id)
        
    def OnInit(self):
        frame = FoodSelectionFrame(None, -1, 'Food Selector', self.food_tree)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def select_foods(food_tree):
    app = FoodSelectorApp(0, food_tree)
    app.MainLoop()
    return selected_id
