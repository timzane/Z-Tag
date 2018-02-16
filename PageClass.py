#!/usr/bin/env python

import sys

from FileUtils import *
from datetime import datetime, date

if sys.version_info[0] < 3:
    import Tkinter as tk    # Python 2.x
    import tkFont
    import ttk
else:
    import tkinter as tk    # Python 3.x
    import tkinter.font as tkfont
    import tkinter.ttk as ttk


TITLE_FONT = ("Helvetica", 18, "bold")


class MenuContainer(tk.LabelFrame):

    def __init__(self, parent,controller,buttonhide=0):

        tk.LabelFrame.__init__(self, parent)
        # Menu Select Area
        self.labelmenucontainer = tk.LabelFrame(parent, text="Screen")
        self.labelmenucontainer.grid(column=0, row=6, columnspan=5, sticky='ew')

        button0 = tk.Button(self.labelmenucontainer, text="MainPage", bg="blue",
                            command=lambda: controller.show_frame("MainPage"))
        button1 = tk.Button(self.labelmenucontainer, text="Duplicates", bg="light blue",
                            command=lambda: controller.show_frame("PageDuplicate"))
        button2 = tk.Button(self.labelmenucontainer, text="TagSelect",
                            command=lambda: controller.show_frame("TagSelect"))

        button3 = tk.Button(self.labelmenucontainer, text="Category Editor", bg="yellow",
                            command=lambda: controller.show_frame("CategoryPage"))

        button4 = tk.Button(self.labelmenucontainer, text="File Operations", bg="green",
                            command=lambda: controller.show_frame("PageFileOps"))

        button5 = tk.Button(self.labelmenucontainer, text="Import", bg="brown",
                            command=lambda: controller.show_frame("Import"))


        buttondict = {0:button0,1:button1,2:button2,3:button3,4:button4,5:button5}
        showbuttons = [button0,button1,button2,button3,button4,button5]
        showbuttons.remove(buttondict[buttonhide])
        columnpos = 0
        for button in showbuttons:
            button.grid(column=columnpos, row=1, in_=self.labelmenucontainer)
            columnpos = columnpos + 1


class MainPage(tk.Frame):

    def __init__(self, parent, controller):

        self.maincatdict = {}
        self.combotagdict = {}    
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="This is the start page", font=TITLE_FONT)
        self.pack()

        # Menu Select Area
        self.labelmenucontainer = MenuContainer(self, controller)
        self.labelmenucontainer.grid(column=0, row=6, columnspan=5, sticky='ew')

        # Display Count
        labelcountcontainer = tk.LabelFrame(self, text="Count")
        labelcountcontainer.grid(column=5, row=0, rowspan=2, sticky='ew')
        self.countlabel = tk.Label(labelcountcontainer, text="#")
        self.countlabel.grid(column=0, row=0)

        # Display Selected
        labelselectcontainer = tk.LabelFrame(self, text="Selected")
        labelselectcontainer.grid(column=3, row=0, rowspan=2, sticky='ew')
        self.selectlabel = tk.Label(labelselectcontainer, text="#")
        self.selectlabel.grid(column=0, row=0)

        # Display Progress
        self.labelprogresscontainer = tk.LabelFrame(self, text="Progress")
        self.labelprogresscontainer.grid(column=2, row=0, rowspan=2, sticky='ew')
        self.progresslabel = tk.Label(self.labelprogresscontainer, text="#")
        self.progresslabel.grid(column=0, row=0)

        # Action Item Buttons
        labelactioncontainer = tk.LabelFrame(self, text="Action")
        labelactioncontainer.grid(column=0, row=2, rowspan=2, sticky='ns')

        buttonsearch = tk.Button(labelactioncontainer, text='Search')
        buttonsearch.bind('<Button-1>', self.load_listbox)
  
        playv = ttk.Button(labelactioncontainer, text="PlayV")
        playv.bind('<Button-1>', controller.open_file)

        buttonhashfiles = ttk.Button(labelactioncontainer, text='Refresh Files')
        buttonhashfiles.bind('<Button-1>', self.refresh_files)

        buttonsearch.grid(column=0, row=2, sticky='ew', in_=labelactioncontainer)
        buttonhashfiles.grid(column=0, row=5, sticky='ew', in_=labelactioncontainer)
        playv.grid(column=0, row=4, sticky='ew', in_=labelactioncontainer)
        # ----------------------------------------------------------------#

        # Search Area ##------------------------------------------------#
        labelactioncontainer = tk.LabelFrame(self, text="Search")
        labelactioncontainer.grid(column=1, row=2, rowspan=2, sticky='ns')

        self.entryfield = ttk.Entry(labelactioncontainer,)                
        self.entryfield.grid(column=1, row=2, in_=labelactioncontainer)

        self.combosearchtype = ttk.Combobox(labelactioncontainer)
        self.combosearchtype.grid(column=1, row=3, sticky="ew", in_=labelactioncontainer)
        # ----------------------------------------------------------------#

        # # Tag Add/Remove ##------------------------------------------------#
        labeltagactioncontainer = tk.LabelFrame(self, text="Add/Remove Tag")
        labeltagactioncontainer.grid(column=2, row=4, rowspan=2, sticky='ns')
        
        buttonaddtag = ttk.Button(labeltagactioncontainer, text='Add Tag')
        buttonaddtag.bind('<Button-1>', self.link_tag2file)
      
        buttonremovetag = ttk.Button(labeltagactioncontainer, text='Remove Tag')
        buttonremovetag.bind('<Button-1>', self.remove_tag)
     
        buttonaddtag.grid(column=2, row=4, in_=labeltagactioncontainer)
        buttonremovetag.grid(column=3, row=4, in_=labeltagactioncontainer)

        label_auto_tag_container = tk.LabelFrame(self, text="")
        label_auto_tag_container.grid(column=5, row=2, rowspan=2, sticky='ns')

        btn_auto_tag = ttk.Button(label_auto_tag_container, text='Auto Tag')
        btn_auto_tag.bind('<Button-1>', self.auto_tag_filter)

        btn_auto_tag_db = ttk.Button(label_auto_tag_container, text='Auto Tag DB')
        btn_auto_tag_db.bind('<Button-1>', self.auto_tag_db)

        label_combo_main_tag_container = tk.LabelFrame(self, text="")
        label_combo_main_tag_container.grid(column=2, row=2, columnspan=2, sticky='ns')

        label_combo_main_container = tk.LabelFrame(label_combo_main_tag_container, text="Category")
        label_combo_main_container.grid(column=2, row=2, columnspan=2, sticky='ns')
        self.comboMain = ttk.Combobox(label_combo_main_container)
        self.comboMain.bind('<<ComboboxSelected>>', controller.maincat_combo_change)

        self.comboMain.grid(column=0, row=0, columnspan=2, sticky="ew", in_=label_combo_main_container)
            
        labelcombotagcontainer = tk.LabelFrame(label_combo_main_tag_container, text="Tag")
        labelcombotagcontainer.grid(column=2, row=3, columnspan=2, sticky='ns')
        self.combo01 = ttk.Combobox(labelcombotagcontainer)
        self.combo01.grid(column=2, row=1, columnspan=2, sticky="ew", in_=labelcombotagcontainer)
        self.combo01.bind('<KeyRelease>', controller.find_combo_value)

        btn_auto_tag.grid(column=5, row=2, in_=label_auto_tag_container)
        btn_auto_tag_db.grid(column=5, row=3, in_=label_auto_tag_container)

    def load_listbox(self, event):

        for i in self.controller.tree.get_children():
            self.controller.tree.delete(i)

        print("Search Type: ", self.controller.buttoncontainer.frames["MainPage"].combosearchtype.get())
        self.controller.fill_tree_from_sql(self.entryfield.get(), self.combosearchtype.get())

    def remove_tag(self, event):

        item = self.controller.tree.selection()
        if len(item) < 1:
            print("Nothing Selected")

        else:
            print("Single/Multiple Selection")
            for rows in item:
                temparray = self.controller.tree.item(rows, "values")
                file_index = str(temparray[0])

                # First Check if the category exists before trying to remove it

                comboindex = self.controller.buttoncontainer.frames["MainPage"].combo01.current()
                tag_index = self.controller.buttoncontainer.frames["MainPage"].combotagdict[comboindex]
                self.controller.filedb.linking_table_remove("tblfile2tag", "TagID", "FileID", tag_index, file_index)
                # Now add values to refresh row
                newvalue = self.controller.filedb.values_for_tree_insert(file_index)
                allcategories = self.controller.filedb.query_category_output2list(file_index)

                valuestoinsert = newvalue + tuple(allcategories)

                self.controller.tree.item(rows, values=valuestoinsert)
                self.controller.update_tree_leaf(rows, file_index)

    def link_tag2file(self, event):
        #  Links a tag to selected file(s) from the main menu
        item = self.controller.tree.selection()
        if len(item) >= 1:
            # One or more Selected
            for rows in item:
                selection_row = self.controller.tree.item(rows, "values")

                # File Index is First Item in Row
                file_index = selection_row[0]
                comboindex = self.controller.buttoncontainer.frames["MainPage"].combo01.current()
                tagindex = self.controller.buttoncontainer.frames["MainPage"].combotagdict[comboindex]
                # self.controller.filedb.linkfile2tag(tagindex, file_index)
                self.controller.filedb.linking_table_add("tblfile2tag", "TagID", "FileID", tagindex, file_index)
                self.controller.update_tree_leaf(rows, file_index)

    def auto_tag_db(self, event):

        print("Auto Tagging Database")
        result = self.controller.filedb.auto_tag_full_db()
        print(result, " tags added")
        return result

    def auto_tag_filter(self, event):

        print("Auto Tag selected")
        item = self.controller.tree.selection()

        count = (len(item))
        counter = 0

        if len(item) < 1:
            print("Nothing Selected")

        else:
            for rows in item:

                # Show Percentage
                counter = counter + 1
                percent = counter / count
                print("Percentage=", percent)

                temparray = self.controller.tree.item(rows, "values")
                file_index = temparray[0]
                filename = temparray[1]
                result = self.controller.filedb.add_tag_from_filter(filename)
                # Mark file as checked
                updatetime = datetime.now()
                self.controller.filedb.modify_table_column(file_index, "last_checked", updatetime, False)

                # take result of tags and link to filename
                for tagindex in result:
                    link_id = self.controller.filedb.linking_table_add("tblfile2tag", "TagID", "FileID",
                                                                       tagindex, file_index)
                    if link_id > 0:
                        self.controller.filedb.modify_table_column_new("tblfile2tag", link_id, "autotag", -1, False)
                    self.controller.update_tree_leaf(rows, file_index)
                    self.controller.tree.update()
                    self.controller.progress = counter / len(item)
                    self.controller.operation_progress()
                    self.controller.buttoncontainer.frames["MainPage"].progresslabel.update()

    def refresh_files(self, event):

        count = 0
        item = self.controller.tree.selection()
        if len(item) >= 1:
            print("About to refresh ", len(item), " files.")
            for rows in item:
                # Get File Index
                count += 1
                self.controller.progress = count / len(item)
                self.controller.operation_progress()
                self.controller.buttoncontainer.frames["MainPage"].progresslabel.update()
                self.controller.filedb.draw_progress_bar(count / len(item))
                temparray = self.controller.tree.item(rows, "values")
                file_index = str(temparray[0])
                self.controller.filedb.refresh_file(file_index)
                self.controller.update_tree_leaf(rows, file_index)


class PageDuplicate(tk.Frame):

    def __init__(self, parent, controller):


        self.maincatdict = {}
        self.combotagdict = {}  

        tk.Frame.__init__(self, parent)
        self.controller = controller

        # # Menu Buttons
        self.labelmenucontainerfo = MenuContainer(self, controller, 1)
        self.labelmenucontainerfo.grid(column=0, row=6, columnspan=5, sticky='ew')


        filterb1 = tk.Button(self, text='Filter Duplicates')

        filterb1.bind('<Button-1>', self.find_duplicates)

        filterb2 = tk.Button(self, text='Merge Selected')
        filterb2.bind('<Button-1>', self.merge_tags)

        self.comboDuplicate = ttk.Combobox(self)
        self.comboDuplicate.grid(column=0, row=4, in_=self)

        filterb1.grid(column=0, row=2, in_=self)
        filterb2.grid(column=0, row=3, in_=self)

    def find_duplicates(self, event):

        duplicate_search = self.controller.buttoncontainer.frames["PageDuplicate"].comboDuplicate.get()
        for i in self.controller.tree.get_children():
            self.controller.tree.delete(i)

        self.controller.fill_tree_from_sql(None, duplicate_search)

    def merge_tags(self, event):

        getallcategories = None

        item = self.controller.tree.selection()

        if len(item) < 1:
            print("Nothing Selected")

        else:
            print("Single/Multiple Selection")
            for rows in item:
                # Get all the categories:
                temparray = self.controller.tree.item(rows, "values")
                file_index = str(temparray[0])
                newcategories = self.controller.filedb.query_category_output2list_of_cat_index(file_index)
                if getallcategories is not None:
                    getallcategories = getallcategories + newcategories
                else:
                    getallcategories = newcategories

        # Quick Fix to remove All Duplicates
        getallcategories = set(getallcategories)
        getallcategories = list(getallcategories)

        # OK Now have all the categories, now add to each leaf

        if len(item) >= 1:
            for rows in item:
                temparray = self.controller.tree.item(rows, "values")
                file_index = str(temparray[0])
                for tag in getallcategories:
                    # filedb.linkfile2tag(tag, file_index)
                    self.controller.filedb.linking_table_add("tblfile2tag", "TagID", "FileID", tag, file_index)
                self.controller.update_tree_leaf(rows, file_index)


class TagSelect(tk.Frame):

    def __init__(self, parent, controller):

        self.maincatdict = {}
        self.combotagdict = {}  
        tk.Frame.__init__(self, parent)
        self.controller = controller

        filterb1 = tk.Button(self, text='Filter By Tag')
        filterb1.bind('<Button-1>', self.filter_tag)
        filterb1.grid(column=0, row=2, in_=self)

        filterb2 = tk.Button(self, text='Remove Tag')
        filterb2.bind('<Button-1>', controller.remove_tag_tree)
        filterb2.grid(column=0, row=3, in_=self)

        filterb3 = tk.Button(self, text='Find using Filters')
        filterb3.grid(column=0, row=4, in_=self)

        button_start = tk.Button(self, text="Main",
                                 command=lambda: controller.show_frame("MainPage"))
        button_start.grid(column=1, row=6, in_=self)
        button_three = tk.Button(self, text="Page 3",
                                 command=lambda: controller.show_frame("CategoryPage"))
        button_three.grid(column=2, row=6, in_=self)
        self.comboMain = ttk.Combobox(self)
        self.comboMain.bind('<<ComboboxSelected>>', controller.maincat_combo_change)
        self.comboMain.grid(column=1, row=2, in_=self)
        self.combo01 = ttk.Combobox(self)
        self.combo01.grid(column=2, row=2, in_=self)

    def filter_tag(self, event):

        for i in self.controller.tree.get_children():
            self.controller.tree.delete(i)
        self.controller.fill_tree_from_sql(None, "FilterTag")


class CategoryPage(tk.Frame):

    def __init__(self, parent, controller):

        self.maincatdict = {}
        self.combotagdict = {}
        self.filterselected = None
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Frame to Display on Tree
        labelframedisplay = tk.LabelFrame(self, text="Display Options")
        labelframedisplay.grid(column=0, row=0, columnspan=2, rowspan=2, sticky='ew')

        buttonshowtagsselected = tk.Button(labelframedisplay, text='Show Tags for Selected Category')
        buttonshowtagsselected.my_name = "select"
        buttonshowtagsselected.bind('<Button-1>', self.show_categories_tree)
        buttonshowtagsselected.grid(column=0, row=2, in_=labelframedisplay)

        buttonshowtagsall = tk.Button(labelframedisplay, text='Show All Tags')
        buttonshowtagsall.my_name = "all"
        buttonshowtagsall.bind('<Button-1>', self.show_categories_tree)
        buttonshowtagsall.grid(column=0, row=1, sticky='ew', in_=labelframedisplay)

        # Frame to Modify Tags
        labelframeedittag = tk.LabelFrame(self, text="Category Add/Remove")
        labelframeedittag.grid(column=0, row=3, columnspan=1, rowspan=2, sticky='ew')

        buttonaddselectedtag = tk.Button(labelframeedittag, text='Add Category')
        buttonaddselectedtag.bind('<Button-1>', self.add_tag2category)
        buttonaddselectedtag.grid(column=0, row=3, sticky='ew', in_=labelframeedittag)

        buttondeletetagcat = tk.Button(labelframeedittag, text='Remove Category')
        buttondeletetagcat.bind('<Button-1>', self.del_tag2category)
        buttondeletetagcat.grid(column=0, row=4, sticky='ew', in_=labelframeedittag)

        #  Show Combo Boxes
        
        labelselecttag = tk.LabelFrame(self, text="Category/Tag Select")
        labelselecttag.grid(column=2, row=0, columnspan=2, rowspan=2)

        self.combo01 = ttk.Combobox(labelselecttag)
        self.combo01.grid(column=3, row=3, in_=labelselecttag)

        mainlabel = tk.Label(labelselecttag, text="Category")
        mainlabel.grid(column=2, row=2)
        self.comboMain = ttk.Combobox(labelselecttag)
        self.comboMain.bind('<<ComboboxSelected>>', controller.maincat_combo_change)
        self.comboMain.grid(column=2, row=3, in_=labelselecttag)
        taglabel = tk.Label(labelselecttag, text="Tag")
        taglabel.grid(column=3, row=2)

        # Save Tag/Category

        labelsavetagcatcontainer = tk.LabelFrame(self, text="New Tag/Category")
        labelsavetagcatcontainer.grid(column=2, row=4, rowspan=2, columnspan=2, sticky='nsew')
        
        buttonaddcategory = tk.Button(labelsavetagcatcontainer, text='Add Main Category')
        buttonaddcategory.bind('<Button-1>', controller.addMainCat)
        buttonaddcategory.grid(column=0, row=0, in_=labelsavetagcatcontainer)

        buttonaddtag = tk.Button(labelsavetagcatcontainer, text='Add Tag')
        buttonaddtag.bind('<Button-1>', self.addtagdb)
        buttonaddtag.grid(column=1, row=0, in_=labelsavetagcatcontainer)

        self.entryfield = ttk.Entry(labelsavetagcatcontainer,)
        self.entryfield.bind('<KeyRelease>')
        self.entryfield.grid(column=0, row=1, rowspan=2, sticky='ew', in_=labelsavetagcatcontainer)

        # Tag Box and Edit Functions
        
        tagcontainerspan = 5

        self.labeltagcontainer = tk.LabelFrame(self, text="Edit Filter")
        self.labeltagcontainer.grid(column=4, row=0, rowspan=tagcontainerspan, columnspan=2, sticky='ns')
        
        self.tagcontainer = ttk.Frame(self, relief="groove")
        self.tagcontainer.grid(column=4, row=0, rowspan=tagcontainerspan, columnspan=2, sticky='ns', in_=self)

        self.filterentry = ttk.Entry(self)
        self.filterentry.bind('<KeyRelease>')
        self.filterentry.grid(column=0, row=tagcontainerspan-2, columnspan=2, in_=self.labeltagcontainer)

        self.savetag = tk.Button(self, text='Save New Filter')
        self.savetag.bind('<Button-1>', self.savetagfilter)
        self.savetag.grid(column=0, row=tagcontainerspan-1, sticky='ew', in_=self.labeltagcontainer)

        self.edittag = tk.Button(self, text='Save Filter')
        self.edittag.bind('<Button-1>', self.edittagsavefilter)
        self.edittag.grid(column=0, row=tagcontainerspan-1, sticky='ew', in_=self.labeltagcontainer)
        self.edittag.grid_remove()

        self.deletetag = tk.Button(self, text='Remove Filter')
        self.deletetag.bind('<Button-1>', self.remove_filter_from_tag)
        self.deletetag.grid(column=1, row=tagcontainerspan-1, sticky='ew', in_=self.labeltagcontainer)

        self.canceltag = tk.Button(self, text='Cancel')
        self.canceltag.bind('<Button-1>', self.cancelsavetagfilter)
        self.canceltag.grid(column=0, row=tagcontainerspan, sticky='ew', in_=self.labeltagcontainer)

        self.filterlist = tk.Listbox(self, height=3)
        self.filterlist.grid(column=0, row=0, rowspan=tagcontainerspan-2, columnspan=2,
                             in_=self.labeltagcontainer, sticky='nesw')
        self.filterlist.columnconfigure(0, weight=1)
        self.filterlist.bind('<<ListboxSelect>>', self.listboxfilterselect)

        button = tk.Button(self, text="Main",
                           command=lambda: controller.show_frame("MainPage"))
        button.grid(column=1, row=6, in_=self)

        self.labeltagcontainer.grid_remove()
        self.deletetag.grid_remove()
        self.canceltag.grid_remove()

    def remove_filter_from_tag(self, event):

        selection = self.controller.buttoncontainer.frames["CategoryPage"].filterlist.curselection()
        filtertext = self.controller.buttoncontainer.frames["CategoryPage"].filterlist.get(selection[0])

        selectionarray = self.controller.tagtree.item(self.controller.tagtree.selection(), "values")
        tagid = selectionarray[0]
        self.controller.filedb.remove_filter_from_tag(filtertext, tagid)
        self.controller.select_tag_item(None)
        self.controller.update_tree_leaf(self.controller.tagtree.selection(), tagid, False, None, "tag")

    def edittagsavefilter(self, event):

        save_filter = self.controller.buttoncontainer.frames["CategoryPage"].filterselected
        newfiltertext = self.controller.buttoncontainer.frames["CategoryPage"].filterentry.get()
        self.controller.filedb.updatetagfilter(save_filter, newfiltertext)

    def cancelsavetagfilter(self, event):

        self.controller.buttoncontainer.frames["CategoryPage"].deletetag.grid_remove()
        self.controller.buttoncontainer.frames["CategoryPage"].edittag.grid_remove()
        self.controller.buttoncontainer.frames["CategoryPage"].canceltag.grid_remove()
        self.controller.buttoncontainer.frames["CategoryPage"].savetag.grid()
        self.controller.buttoncontainer.frames["CategoryPage"].filterentry.delete(0, 'end')

    def show_categories_tree(self, event):

        self.controller.fill_tagtree_from_sql(event.widget.my_name)

    def listboxfilterselect(self, event):

        print("in FilterSelect")
        self.controller.buttoncontainer.frames["CategoryPage"].deletetag.grid()
        self.controller.buttoncontainer.frames["CategoryPage"].canceltag.grid()
        self.controller.buttoncontainer.frames["CategoryPage"].edittag.grid()
        selection = self.controller.buttoncontainer.frames["CategoryPage"].filterlist.curselection()
        selectedfilter = self.controller.buttoncontainer.frames["CategoryPage"].filterlist.get(selection[0])
        self.controller.buttoncontainer.frames["CategoryPage"].filterentry.delete(0, 'end')
        self.controller.buttoncontainer.frames["CategoryPage"].filterentry.insert(0, selectedfilter)

        self.controller.buttoncontainer.frames["CategoryPage"].filterselected = selectedfilter

    def savetagfilter(self, event):

        filtertext = self.controller.buttoncontainer.frames["CategoryPage"].filterentry.get()
        selectionarray = self.controller.tagtree.item(self.controller.tagtree.selection(), "values")
        tagid = selectionarray[0]
        self.controller.filedb.add_filter_to_tag(filtertext, tagid)
        self.controller.select_tag_item(None)
        self.controller.update_tree_leaf(self.controller.tagtree.selection(), tagid, False, None, "tag")

    def add_tag2category(self, event):

        item = self.controller.tagtree.selection()
        if len(item) >= 1:
            for rows in item:
                temparray = self.controller.tagtree.item(rows, "values")
                tag_index = str(temparray[0])
                maincomboindex = self.controller.buttoncontainer.frames["CategoryPage"].comboMain.current()
                main_category_id = self.controller.buttoncontainer.frames["CategoryPage"].maincatdict[maincomboindex]
                # self.controller.filedb.linkcat2tag( main_category_id, tag_index)
                self.controller.filedb.linking_table_add("tblCat2Tag", "TagID", "CategoryID",
                                                         tag_index, main_category_id)
                self.controller.update_tree_leaf(rows, tag_index, False, None, "tag")

    def del_tag2category(self, event):

        item = self.controller.tagtree.selection()
        if len(item) >= 1:
            for rows in item:
                temparray = self.controller.tagtree.item(rows, "values")
                tag_index = str(temparray[0])
                maincomboindex = self.controller.buttoncontainer.frames["CategoryPage"].comboMain.current()
                main_category_id = self.controller.buttoncontainer.frames["CategoryPage"].maincatdict[maincomboindex]

                # self.controller.filedb.removecat2tag( main_category_id, tag_index)
                self.controller.filedb.linking_table_remove("tblCat2Tag", "TagID", "CategoryID",
                                                            tag_index, main_category_id)
                self.controller.update_tree_leaf(rows, tag_index, False, None, "tag")

    def addtagdb(self, event):

        # Get Tag Name
        tag = self.controller.buttoncontainer.frames["CategoryPage"].entryfield.get()

        # Get Category Index from Combo Box
        maincomboindex = self.controller.buttoncontainer.frames["CategoryPage"].comboMain.current()

        if maincomboindex >= 0:
            main_category_id = self.controller.buttoncontainer.frames["CategoryPage"].maincatdict[maincomboindex]
            self.controller.filedb.add_tag_2_db_and_link(tag, main_category_id)
            return True
        else:
            return False


class PageFileOps(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Menu Buttons
        self.labelmenucontainerfo = MenuContainer(self, controller, 4)
        self.labelmenucontainerfo.grid(column=0, row=6, columnspan=5, sticky='ew')

        # Action Item Buttons
        self.labelactioncontainerdelete = tk.LabelFrame(self, text="Delete Menu")
        self.labelactioncontainerdelete.grid(column=0, row=2, rowspan=2, sticky='ns')

        harddelete = tk.Button(self.labelactioncontainerdelete, text='Delete Tagged File(s)', bg="red")
        harddelete.bind('<Button-1>', self.delete_tagged)
        harddelete.grid(column=1, row=4, in_=self.labelactioncontainerdelete)

        filterb6 = tk.Button(self.labelactioncontainerdelete, text='Tag for Delete', bg="red")
        filterb6.bind('<Button-1>', self.delete_selection)
        filterb6.grid(column=1, row=2, in_=self.labelactioncontainerdelete)

        self.var = tk.IntVar()
        # delete_file = tk.Checkbutton(self.labelactioncontainerdelete, text="Delete File", variable=self.var)
        deletechoice1 = tk.Radiobutton(self.labelactioncontainerdelete,text = "DeleteDB",variable=self.var,value=1)
        deletechoice2 = tk.Radiobutton(self.labelactioncontainerdelete, text="Delete", variable=self.var, value=2)

        # delete_file.grid(column=1, row=3, sticky="ew", in_=self.labelactioncontainerdelete)
        deletechoice1.grid(column=1, row=3, sticky="w", in_=self.labelactioncontainerdelete)
        deletechoice2.grid(column=2, row=3, sticky="w", in_=self.labelactioncontainerdelete)

        batch_rename_button = tk.Button(self, text='Batch Rename')
        batch_rename_button.bind('<Button-1>', self.batch_rename)
        batch_rename_button.grid(column=2, row=1, in_=self)

        #  Rename Portion
        self.batchrenamecontainer = tk.LabelFrame(self, text="Batch Rename")
        self.batchrenamecontainer.columnconfigure('all', minsize=80)

        self.renameregex = ttk.Entry(self.batchrenamecontainer)
        self.renameregex.grid(column=0, row=1, columnspan=4, sticky="ew", in_=self.batchrenamecontainer)

        self.var2 = tk.IntVar()
        regex_check = tk.Checkbutton(self.batchrenamecontainer, text="Regex", variable=self.var2, command=self.test)
        regex_check.grid(column=5, row=1, in_=self.batchrenamecontainer)

        self.renameregexnew = ttk.Entry(self.batchrenamecontainer)
        self.renameregexnew.grid(column=0, row=2, columnspan = 7, sticky="ew", in_=self.batchrenamecontainer)

        self.renamedirentry = ttk.Entry(self.batchrenamecontainer)
        self.renamedirentry.grid(column=0, row=3, columnspan = 6, sticky="ew", in_=self.batchrenamecontainer)

        load_filename = tk.Button(self.batchrenamecontainer, text='Load filename')
        load_filename.grid(column=7, row=2, in_=self.batchrenamecontainer)
        load_filename.bind('<Button-1>',self.load_filename_entry)

        choosedir = tk.Button(self, text="Choose Dir")
        choosedir.grid(column=7, row=3, in_=self.batchrenamecontainer)
        choosedir.bind('<Button-1>',self.choose_dir)

        load_dir = tk.Button(self.batchrenamecontainer, text='Load Dir')
        load_dir.grid(column=8, row=3, in_=self.batchrenamecontainer)
        load_dir.bind('<Button-1>',self.load_dir_entry)

        applydir = tk.Button(self, text="Apply")
        applydir.grid(column=9, row=3, in_=self.batchrenamecontainer)
        applydir.bind('<Button-1>', self.apply_rename_dir)

        self.rename_button = tk.Button(self, text="Apply")
        self.rename_button.bind('<Button-1>', self.apply_rename)
        self.rename_button.grid(column=7, row=1, in_=self.batchrenamecontainer)

        self.rename_button = tk.Button(self, text="Cancel")
        self.rename_button.bind('<Button-1>', self.cancel_batch)
        self.rename_button.grid(column=6, row=5, columnspan=2, in_=self.batchrenamecontainer)

        self.apply_rename = tk.Button(self, text="Perform", bg="yellow")
        self.apply_rename.bind('<Button-1>', self.perform_rename)
        self.apply_rename.grid(column=0, row=5, columnspan=2, sticky='ew', in_=self.batchrenamecontainer)
        self.apply_rename.extra = "Apply"

        self.apply_rename = tk.Button(self, text="Reset", bg="light blue")
        self.apply_rename.bind('<Button-1>', self.batch_rename)
        self.apply_rename.grid(column=2, row=5, columnspan=2, sticky='ew', in_=self.batchrenamecontainer)
        self.apply_rename.extra = "Apply"

    def test(self):
        print("hello")

    def reset_rename_tree(self):
        print("hello")
        
    def load_filename_entry(self, event):

        item = self.controller.tree.selection()
        if len(item) > 1:
            print("Do Nothing")
        else:
            filename = self.controller.tree.item(item, "values")
            insertvalue = filename[1]
            self.renameregexnew.delete(0, 'end')
            self.renameregexnew.insert(0,insertvalue)

    def load_dir_entry(self, event):

        item = self.controller.tree.selection()
        if len(item) > 1:
            print("Do Nothing")
        else:
            filename = self.controller.tree.item(item, "values")
            insertvalue = filename[2]
            self.renamedirentry.delete(0, 'end')
            self.renamedirentry.insert(0,insertvalue)

    def perform_rename(self,event):

        children = self.controller.tree.get_children()
        self.controller.rename_tree(self.controller.tree, children)

    def apply_rename_dir(self,event):

        items = self.controller.tree.selection()
        newdir = self.renamedirentry.get()
        for item in items:
            temparray = self.controller.tree.item(item, "values")
            newlist = list(temparray)
            newlist[4] = newdir
            updatedvalue = tuple(newlist)
            self.controller.tree.item(item, values=updatedvalue)

    def choose_dir(self,event):

        items = self.controller.tree.selection()
        if len(items) == 1:
            tree_values = self.controller.tree.item(items[0], "values")
            initial_dir = tree_values[2]
            searchdir = tk.filedialog.askdirectory(initialdir=initial_dir)
        else:
            searchdir = tk.filedialog.askdirectory()

        searchdir = searchdir + "/"
        self.renamedirentry.delete(0, 'end')
        self.renamedirentry.insert(0, searchdir)

    def apply_rename(self,event):

        items = self.controller.tree.selection()


        if self.var2.get() == 0 and len(items) == 1 and event.widget['text'] == "Apply":

            temparray = self.controller.tree.item(items, "values")
            result = self.renameregexnew.get()
            newlist = list(temparray)
            newlist[3] = result
            updatedvalue = tuple(newlist)
            self.controller.tree.item(items, values=updatedvalue)
            return

        if event.widget['text'] == "Apply":
            pattern = self.renameregex.get()
            substitute = self.renameregexnew.get()

            for item in items:
                temparray = self.controller.tree.item(item, "values")
                result = substitute_regex(pattern, substitute, temparray[1])
                newlist = list(temparray)
                newlist[3] = result
                updatedvalue = tuple(newlist)
                self.controller.tree.item(item, values=updatedvalue)


    def delete_tagged(self, event):

        children = self.controller.tree.get_children()
        self.controller.filedb.delete_children(children, self.controller.tree)

    def delete_selection(self, event):

        item = self.controller.tree.selection()
        type_remove = self.controller.buttoncontainer.frames["PageFileOps"].var.get()

        if type_remove == 1:
            delete_file = "deletedb"
        elif type_remove == 2:
            delete_file = "delete"
        else:
            delete_file = "missingremove"

        if len(item) >= 1:
            for rows in item:
                temparray = self.controller.tree.item(rows, "values")
                file_index = str(temparray[0])

                (file_name, directory) = self.controller.filedb.get_file_and_directory(file_index)
                print("Delete File", file_name, " in directory", directory)
                self.controller.tree.item(rows, tags=delete_file)

    def batch_rename(self,event):

        self.controller.tree.heading('#3', text='NewName')
        self.controller.tree.heading('#4', text='NewDir')
        children = self.controller.tree.get_children()
        self.controller.requery_rename_tree(self.controller.tree, children, "rename")
        self.batchrenamecontainer.grid(column=0, row=2, rowspan=4, columnspan=6, sticky='ew')
        self.labelmenucontainerfo.labelmenucontainer.grid_remove()
        self.labelactioncontainerdelete.grid_remove()
        self.renamedirentry.delete(0, 'end')
        self.renameregexnew.delete(0, 'end')
        self.renameregex.delete(0, 'end')


    def cancel_batch(self,event):

        self.batchrenamecontainer.grid_remove()
        self.labelmenucontainerfo.labelmenucontainer.grid()
        self.labelactioncontainerdelete.grid()
        self.controller.tree.heading('#3', text='Size')
        self.controller.tree.heading('#4', text='Hash')
        children = self.controller.tree.get_children()
        self.controller.requery_rename_tree(self.controller.tree,children)


class Import(tk.Frame):

    def __init__(self, parent, controller):

        self.rootDirDict = {}

        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.rootlabel = tk.Button(self, text="Root Dir",
                                   command=lambda: controller.change_root(True))

        self.rootlabel.grid(column=0, row=2)

        self.var = tk.IntVar()
        dry_run = tk.Checkbutton(self, text="Dry Run", variable=self.var)
        dry_run.grid(column=0, row=5, sticky="ew", in_=self)
        dry_run.select()

        self.importlabel = tk.Label(self, text="Import Dir", relief="groove")
        self.importlabel.grid(column=0, row=3)

        # importdir = read_config_file("Ztag", "importlocation")
        importdir = self.controller.filedb.get_default_parameter("ImportDir")
        self.importdir = tk.Label(self, text=importdir)
        self.importdir.grid(column=1, row=3)
        self.rootDirCombo = ttk.Combobox(self)
        # self.rootDirCombo.bind('<<ComboboxSelected>>', controller.rootDircombochange)
        self.rootDirCombo.grid(column=1, row=2, in_=self)

        buttonimport = tk.Button(self, text="Import",
                                 command=lambda: self.import_files(True))
        buttonimport.grid(column=0, row=4, in_=self)

        buttonstop = tk.Button(self, text="Stop",
                               command=lambda: controller.stop_import("test"))
        buttonstop.grid(column=1, row=4, in_=self)

        button_start = tk.Button(self, text="Main Page",
                                 command=lambda: controller.show_frame("MainPage"))

        button_start.grid(column=3, row=5, in_=self)

    def import_files(self, event):

        if self.controller.buttoncontainer.frames["Import"].var.get():
            print("Performing a Dry Run")
            dry_run = True
        else:
            dry_run = False

        import_dir = self.controller.filedb.get_default_parameter("ImportDir")
        if import_dir is None:
            print("Nothing Selected")
        else:
            print(import_dir)
            comboindex = self.controller.buttoncontainer.frames["Import"].rootDirCombo.current()
            self.controller.filedb.import_filenames(import_dir,
                                                    self.controller.buttoncontainer.frames["Import"].rootDirDict[comboindex],  dry_run)
