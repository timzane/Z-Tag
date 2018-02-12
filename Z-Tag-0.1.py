#!/usr/bin/python3.5
# Created by Tim Zane

import sqlite3
import sys
import argparse

# test

from DBToolsClass import *
from sys import platform as _platform

def get_platform():

        if _platform == "linux" or _platform == "linux2":
            print("Running on Linux...")
            return "Linux"

        elif _platform == "darwin":
            return "Darwin"
        elif _platform == "win32":
            return "Windows"


TreeColumns = ["Index", "Filename", "Dir", "Size", "Hash", "Tags"]
TagTreeColumns = ["Index", "Tag", "Category", "Filter Count"]




class MultiColumnListbox(object):

    MainCategory = None
    CurrentFrame = ""
    StopImport = False
    DBDirectory = None
    progress = 1.0

    def __init__(self):

        self.filedb = DBFileListing(None)
        self.tree = None
        self._setup_widgets()
        self._build_tree()
        self.fill_tree_from_sql()
        self.query_rootDir_combo()

    def select_item(self, event):
        item = self.tree.selection()
        count = len(item)
        self.buttoncontainer.frames["MainPage"].selectlabel['text'] = count
        if len(item) > 1:
            print("More than 1 item selected")
            # print(self.tree.item(item,"values"))

    def fill_filter_list_box(self, tag_id):

        result = self.filedb.query_filter_from_tag_id(tag_id)
        self.buttoncontainer.frames["CategoryPage"].filterlist.delete(0, 'end')
        self.buttoncontainer.frames["CategoryPage"].filterentry.delete(0, 'end')
        for item in result:
            filtertxt = str(item[0])
            self.buttoncontainer.frames["CategoryPage"].filterlist.insert(0, filtertxt)

    def add_rootdir_dialog(self):

        directory = tk.filedialog.askdirectory()
        self.filedb.add_root_dir(directory)

    def add_importdir_dialog(self):

        searchdir = tk.filedialog.askdirectory(initialdir = os.getenv("HOME"))
        self.ImportDir = searchdir
        self.buttoncontainer.frames["Import"].importdir.config(text=searchdir)
        write_config_file("Ztag", "ImportLocation", searchdir)

    def add_db_dialog(self):
        self.DBDirectory = tk.filedialog.askopenfilename()
        write_config_file(get_platform(), "DBLocation", self.DBDirectory)

    def select_item_double(self, event):
        # item = self.tree.selection()
        # print("# of Items:",len(item))
        print("Double Click")

        item = self.tree.selection()

        temparray = self.tree.item(item, "values")
        filename = str(temparray[1])
        directory = str(temparray[2])
        path_and_file = str(directory + filename)
        cmdstring = "/usr/bin/kaffeine '%s' &" % (path_and_file)
        cmdstring.replace(" ", "\\\ ")
        print(cmdstring)
        #print(duration(path_and_file))
        os.system(cmdstring)

    def stop_import(self, event):
        stop_import = True
        print(stop_import)
        return stop_import

    def query_main_combo_boxes(self):

        for Page in ("CategoryPage","MainPage","TagSelect"):
            self.buttoncontainer.frames[Page].comboMain['values'] = (self.query_category_main(Page))
            # Check if there are any value in Main Combo and select first
            if len(self.buttoncontainer.frames[Page].comboMain['values']) > 0:
                self.buttoncontainer.frames[Page].comboMain.current(0)

                maincombovalue = self.buttoncontainer.frames[Page].comboMain.current()
                categoryindex = self.buttoncontainer.frames[Page].maincatdict[maincombovalue]

                self.buttoncontainer.frames[Page].combo01['values'] = (self.query_category_all(Page, categoryindex))
                # Check if there are any value in Tag Combo and select first
                if len(self.buttoncontainer.frames[Page].combo01['values']) > 0:
                    self.buttoncontainer.frames[Page].combo01.current(0)

    def addMainCat(self,event):

        print("In Main Cat")
        categoryname = self.buttoncontainer.frames["CategoryPage"].entryfield.get()

        flag = self.filedb.add_main_category(categoryname)

        if flag:
            self.query_main_combo_boxes()

    def show_frame(self, page_name):
        # Show a frame for the given page name

        frame = self.buttoncontainer.frames[page_name]
        self.CurrentFrame = page_name
        frame.tkraise()
        if page_name == "CategoryPage":
            self.tagtree.tkraise()
            self.tvsb.tkraise()
            self.thsb.tkraise()
        if page_name == "PageDuplicate":
            self.tree.tkraise()
        if page_name == "MainPage":
            self.tree.tkraise()
            self.vsb.tkraise()
            self.hsb.tkraise()
        if page_name == "Import":
            self.tree.tkraise()
            self.vsb.tkraise()
            self.hsb.tkraise()

    def select_tag_item(self, event):

        item = self.tagtree.selection()
        if len(item) > 1:
            self.buttoncontainer.frames["CategoryPage"].labeltagcontainer.grid_remove()
        if (len(item)) == 1:
            # Show Container Box
            self.buttoncontainer.frames["CategoryPage"].labeltagcontainer.grid()
            temparray = self.tagtree.item(item, "values")
            tagid = temparray[0]

            # Put Filters in Box
            self.fill_filter_list_box(tagid)

            # Hide Edit Fields (if Open)

            self.buttoncontainer.frames["CategoryPage"].deletetag.grid_remove()
            self.buttoncontainer.frames["CategoryPage"].edittag.grid_remove()

    def _setup_widgets(self):

        title_string = """Category Editor"""
        msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
                        padding=(10, 2, 10, 6), text=title_string)
        msg.pack(fill='x')
        container = ttk.Frame(height=10,width=200)
        container.pack(fill='both', expand=True)


        self.buttoncontainer = ttk.Frame(container)
        self.buttoncontainer.pack(fill='both', expand=True)
        self.buttoncontainer.grid(column=0, row=2, sticky='ns', in_=container)

        # Create Main Tree and Scroll Bars
        self.tree = ttk.Treeview(columns=TreeColumns, show="headings")

        self.vsb = ttk.Scrollbar(orient="vertical",
                                 command=self.tree.yview)
        self.hsb = ttk.Scrollbar(orient="horizontal",
                                 command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set,
                            xscrollcommand=self.hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        self.vsb.grid(column=1, row=0, sticky='ns', in_=container)
        self.hsb.grid(column=0, row=1, sticky='ew', in_=container)
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        # self.tree.bind('<Double-1>', self.select_item_double)

        # Hide Index Column of Main Tree
        self.tree["displaycolumns"] = ("Filename", "Dir", "Size", "Hash", "Tags")

        # Create Tag Tree

        self.tagtree = ttk.Treeview(columns=TagTreeColumns, show="headings")
        self.tagtree["displaycolumns"] = ("Tag", "Category", "Filter Count")
        # self.tagtree.bind('<Button-1>', self.select_tag_item)
        self.tagtree.bind('<<TreeviewSelect>>', self.select_tag_item)
        self.tvsb = ttk.Scrollbar(orient="vertical",
                                  command=self.tagtree.yview)
        self.thsb = ttk.Scrollbar(orient="horizontal",
                                  command=self.tagtree.xview)
        self.tagtree.configure(yscrollcommand=self.tvsb.set,
                               xscrollcommand=self.thsb.set)
        self.tagtree.grid(column=0, row=0, sticky='nsew', in_=container)
        self.tvsb.grid(column=1, row=0, sticky='ns', in_=container)
        self.thsb.grid(column=0, row=1, sticky='ew', in_=container)

        self.buttoncontainer.frames = {}
        for F in (MainPage, PageDuplicate, TagSelect, CategoryPage, PageFileOps, Import):
            page_name = F.__name__
            frame = F(parent=self.buttoncontainer, controller=self)
            self.buttoncontainer.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")
        self.query_main_combo_boxes()
        self.buttoncontainer.frames["MainPage"].combosearchtype['values'] = ("Plain Text", "Dir",
                                                                             "regex", "newest", "random 100", "Oldest 100","Missing")
        search_choices = self.filedb.get_search_combo_values()
        self.buttoncontainer.frames["MainPage"].combosearchtype['values'] = search_choices
        self.buttoncontainer.frames["MainPage"].combosearchtype.current(0)

        self.buttoncontainer.frames["PageDuplicate"].comboDuplicate['values'] =  self.filedb.get_search_combo_values("duplicatepage")

        if len(self.buttoncontainer.frames["PageDuplicate"].comboDuplicate['values']) > 0:
            self.buttoncontainer.frames["PageDuplicate"].comboDuplicate.current(0)

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        self.buttoncontainer.grid(column=0, row=2, sticky='ns', in_=container)

        ##
        self.buttoncontainer.after(1000, self.updater())

    def operation_progress(self):

            self.buttoncontainer.frames["MainPage"].progresslabel['text'] = self.progress

    def updater(self):
        self.operation_progress()
        self.buttoncontainer.frames["MainPage"].progresslabel.after(1000, self.updater)

    def remove_tag_tree(self, event):

        # Get Tag

        comboindex = self.buttoncontainer.frames["TagSelect"].combo01.current()
        tagindex = self.buttoncontainer.frames["TagSelect"].combotagdict[comboindex]

        for i in self.tree.get_children():
            # get File Tag
            temparray = self.tree.item(i, "values")
            file_id = temparray[0]
            print("Id of leaf:", temparray[0])
            answer = self.filedb.query_tag_from_file_id(file_id, tagindex)
            if answer is True:
                self.tree.delete(i)

    def open_file(self, event):

        print("Play")

        item = self.tree.selection()

        print("Number of selections:", len(item))

        temparray = self.tree.item(item, "values")
        filename = str(temparray[1])
        directory = str(temparray[2])
        path_and_file = str(directory + filename)
        cmdstring = "/usr/bin/kaffeine '%s' &" % path_and_file
        cmdstring.replace(" ", "\\\ ")
        print(cmdstring)

        os.system(cmdstring)

    def change_root_delete(self, event):

        print(self.buttoncontainer.frames["Import"].rootDirDict)

    def find_combo_value(self, event):

        entrytext = self.buttoncontainer.frames[self.CurrentFrame].combo01.get()
        for ix, combotext in enumerate(self.buttoncontainer.frames[self.CurrentFrame].combo01['values']):
            print(combotext.find(entrytext, 0))
            lowercombotext = combotext.lower()
            if lowercombotext.find(entrytext.lower(), 0) == 0:
                print("Found", entrytext, "in", combotext, " ", ix)
                self.buttoncontainer.frames[self.CurrentFrame].combo01.current(ix)
                return

    def maincat_combo_change(self, event):

        maincombovalue = self.buttoncontainer.frames[self.CurrentFrame].comboMain.current()
        categoryindex = self.buttoncontainer.frames[self.CurrentFrame].maincatdict[maincombovalue]

        self.buttoncontainer.frames[self.CurrentFrame].combo01['values'] = \
            (self.query_category_all(self.CurrentFrame, categoryindex))
        self.buttoncontainer.frames[self.CurrentFrame].combo01.set('')

    def _build_tree(self):

        for col in TreeColumns:
            self.tree.heading(col, text=col.title(),
                              command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                             width=tkFont.Font().measure(col.title()))

        for col in TagTreeColumns:
            self.tagtree.heading(col, text=col.title(),
                                 command=lambda c=col: sortby(self.tagtree, c, 0))
            # adjust the column's width to the header string
            self.tagtree.column(col,
                                width=tkFont.Font().measure(col.title()))

    def tree_change_column(self, tree, search_type):
        if search_type == "Oldest 100":
            tree.heading('#4', text ='date')

    def fix_columns_delete(self):

        print("In Fix Columns")

        for col in self.tree["displaycolumns"]:
            self.tree.heading(col, text=col.title(),
                              command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                             width=tkFont.Font().measure(col.title()))

        for col in TagTreeColumns:
            self.tagtree.heading(col, text=col.title(),
                                 command=lambda c=col: sortby(self.tagtree, c, 0))
            # adjust the column's width to the header string
            self.tagtree.column(col,
                                width=tkFont.Font().measure(col.title()))

    def query_category_all(self, Page=None, main_cat_id=None):

        if not main_cat_id:
            allcategories = self.filedb.query_tags("All")
        else:
            allcategories = self.filedb.query_tags(main_cat_id)


            catlist = list()
            for idx, tag in enumerate(allcategories):
                catlist.append(tag[1])
                self.buttoncontainer.frames[Page].combotagdict[idx] = tag[0]

            return (catlist)

    def query_rootDir_combo(self):


            result = self.filedb.query_root_dir()

            rootDirlist = list()
            for idx, dirname in enumerate(result):
                self.buttoncontainer.frames["Import"].rootDirDict[idx] = dirname[0]
                rootDirlist.append(dirname[1])

            self.buttoncontainer.frames["Import"].rootDirCombo['values'] = rootDirlist
            if len(self.buttoncontainer.frames["Import"].rootDirCombo['values']) > 0:
                self.buttoncontainer.frames["Import"].rootDirCombo.current(0)

    def query_category_main(self, Page):
            # Get ALL Categories of Main List

            allcategories = self.filedb.query_categories_return_list()
            catlist = list()
            for idx, tag in enumerate(allcategories):
                catlist.append(tag[1])
                self.buttoncontainer.frames[Page].maincatdict[idx] = tag[0]
            return (catlist)

    def rename_tree(self, tree, children):

        for child in children:
            item = tree.item(child, "values")
            (oldfile,olddir,newfile,newdir) = item[1:5]
            old = olddir + oldfile
            new = newdir + newfile

            if old != new:
                flag = self.filedb.rename_operation(olddir, oldfile, newdir, newfile)
                if flag:
                    root_dir_id = self.filedb.get_root_dir_id(item[0])
                    rootDir = self.filedb.get_root_dir(root_dir_id)
                    localdirname = newdir[len(rootDir):]
                    self.filedb.modify_table_column(item[0], "filename", newfile, False)
                    self.filedb.modify_table_column(item[0], "filedirlocal", localdirname, False)
                    self.update_tree_leaf(child, item[0], False, None, "rename")

            anychildren = tree.get_children(child)
            if anychildren:
                self.rename_tree(tree, anychildren)

    def requery_rename_tree(self, tree, children, type=None):

        for child in children:
                items = tree.item(child,"values")
                test = items[0]
                self.update_tree_leaf(child, items[0], False, None, type)
                anychildren = tree.get_children(child)
                if anychildren:
                        self.requery_rename_tree(tree, anychildren, type)

    def update_tree_leaf(self, leafid=None,file_id=None,newleaf=False,parentleaf=None,tree=None):

        search_type = self.buttoncontainer.frames["MainPage"].combosearchtype.get()
        if search_type == "Oldest 100":
            fieldreplace = "ddd"



        if tree==None:
            sql1 = '''SELECT fileID,filename,(tblRootDir.DirName || filedirlocal) as filedir,filesize,md5hash_partial FROM tblfilelisting
                                            inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID  WHERE fileID =?'''
            UpdateTree = self.tree

        elif tree=="tag":
            sql1=  'select tblTags.TagId,TagName,tblMainCategory.MainCategoryName,count(tblTag2Filter.FilterID ) from tblTags  \
                    left  join  tblCat2Tag on  tblCat2Tag.TagID =  tblTags.TagID \
                    left join tblTag2Filter on  tblTag2Filter.TagID = tblTags.TagID \
                    left join tblTagFilters on tblTagFilters.ID = tblTag2Filter.FilterID \
                    left join tblMainCategory on tblMainCategory.MainCatID	= tblCat2Tag.CategoryID \
                    where tblTags.TagID = ? \
                    group by  tblTags.TagId,TagName \
                    ORDER BY TagName'
            UpdateTree = self.tagtree
        elif tree=="rename":
            sql1 = '''SELECT fileID,filename,(tblRootDir.DirName || filedirlocal) as filedir,filename,(tblRootDir.DirName || filedirlocal) as filedir FROM tblfilelisting
                                            inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID  WHERE fileID =?'''
            UpdateTree = self.tree

        else:
            UpdateTree = self.tree
            sql1 = None

        item = self.filedb.query_leaf(file_id, sql1)
        itemlist = list(item)

        if tree is None:
            categorylistformat = self.filedb.query_category_output2list(file_id)
            updatedvalues = tuple(itemlist) + tuple(categorylistformat)
        elif tree == "tag":
            categorylistformat = self.filedb.query_maincategory_output2list(file_id)
            itemlist[2] = tuple(categorylistformat)
            updatedvalues = tuple(itemlist)
        elif tree=="rename":
            categorylistformat = self.filedb.query_maincategory_output2list(file_id)
            updatedvalues = tuple(itemlist) + tuple(categorylistformat)
        else:
            updatedvalues = None
            categorylistformat = None

        if newleaf is False and leafid is not None:
            UpdateTree.item(leafid, values=updatedvalues)
        elif newleaf is True and parentleaf is None:
            leafid = UpdateTree.insert('', itemlist[0], values=updatedvalues, tags=categorylistformat)
        elif newleaf is True and parentleaf is not None:
            leafid = UpdateTree.insert(parentleaf, itemlist[0], values=updatedvalues, tags=categorylistformat)
        else:
            print("Error")

        if tree  is None:
            if self.filedb.is_file_missing(file_id):
                self.tree.item(leafid, tags='missing')
            else:
                self.tree.item(leafid, tags='')

        self.tree.tag_configure('missing', background='blue')
        self.tree.tag_configure('duplicate', background='lightgrey')
        self.tree.tag_configure('delete', background='red')
        self.tree.tag_configure('deletedb', background='yellow')

        return leafid

    def fill_tagtree_from_sql(self, all_tags=None):

        # Clear Tree
        for i in self.tagtree.get_children():
            self.tagtree.delete(i)

        combovalue = self.buttoncontainer.frames["CategoryPage"].comboMain.current()

        self.tagtree.column("Category", stretch=1)

        if combovalue < 0 or all_tags == "all":
            print("Printing ALL tags")
            result = self.filedb.query_tag_tree("all")

        else:
            print("ComboSelected", combovalue)
            main_index = self.buttoncontainer.frames["CategoryPage"].maincatdict[combovalue]
            result = self.filedb.query_tag_tree(main_index)

        counter = 0
        count = (len(result))

        for item in result:

            # Show Percentage
            counter = counter + 1
            percent = counter / count
            print("Percentage=", percent)

            # Take out Index of Database for use in queries
            itemindex = item[0]
            itemlist = item[0:4]

            # Get Categories associated with this item from joining table

            self.update_tree_leaf('', itemindex, True, None, "tag")

            # adjust column's width if necessary to fit each value, this has trouble !!!
            for ix, val in enumerate(itemlist):

                # col_w = tkFont.Font().measure(str(val))
                col_w = tkFont.Font().measure("testaaaaaaa")
                if self.tree.column(TreeColumns[ix], width=None) < col_w:
                    self.tree.column(TreeColumns[ix], width=col_w)

    def fill_tree_from_sql(self, filefilter=None, searchtype=None, duplicate_type=None):

        if not filefilter and not searchtype:
            return

        # Get Search Type

        duplicate_match = self.filedb.get_duplicate_field(searchtype)

        if searchtype == "FilterTag":
            comboindex = self.buttoncontainer.frames["TagSelect"].combo01.current()
            tag_index = self.buttoncontainer.frames["TagSelect"].combotagdict[comboindex]
            result = self.filedb.filter_tag_query(tag_index)
        else:
            result = self.filedb.tree_query(searchtype,filefilter,duplicate_type)

        lasthash = ""
        self.tree_change_column(self.tree,searchtype)
        if result is None:
            return

        counter = 0
        count = (len(result))
        id2 = None

        self.buttoncontainer.frames["MainPage"].countlabel['text'] = count

        print("Total Records found: ", count)
        for item in result:

            # Show Percentage
            counter = counter + 1
            percent = counter / count
            self.filedb.update_progress(percent)
            # Take out Index of Database for use in queries
            itemindex = item[0]

            if duplicate_match is None :
                self.update_tree_leaf(None, itemindex, True)
            else:
                if lasthash == self.filedb.get_duplicate_parameter(itemindex, duplicate_match):
                    self.update_tree_leaf(None, itemindex, True, id2)
                else:
                    id2 = self.update_tree_leaf('', itemindex, True)
                    lasthash = self.filedb.get_duplicate_parameter(itemindex, duplicate_match)


def sortby(tree, col, descending):
    # sort tree contents when a column header is clicked on

    # grab values to sort
    data = [(tree.set(child, col), child)
            for child in tree.get_children('')]

    # now sort the data in place
    data.sort(reverse=descending)

    # if the data to be sorted is numeric change to integer
    if (col == "Size") or (col == "Index"):
        print("Size Column")
        data.sort(key=lambda t: int(t[0]), reverse=descending)

    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, int(not descending)))

def client_exit():
    exit()


if __name__ == '__main__':


    # Add Command Line Parsing Tools
    parser = argparse.ArgumentParser(description='Z-Tag')
    parser.add_argument('--local', action="store_true", default=False,dest="local")
    parser.add_argument('--gui', action="store_false", default=False, dest="local")
    result = parser.parse_args()
    print("Status: ",result.local)

    if result.local is True:
        print("Going Local")
        print(os.getcwd())
        filedblocal = DBFileListing(os.getenv("HOME") + "/FileListingShort.db3",True)
        filedblocal.import_filenames(os.getcwd(), None, False, False)
        exit()
    else:
        if sys.version_info[0] < 3:
            import Tkinter as tk  ## Python 2.x
            import tkFont
            import ttk
        else:
            import tkinter as tk  # Python 3.x
            import tkinter.font as tkFont
            import tkinter.ttk as ttk
            import tkinter.filedialog

        from PageClass import *
        root = tk.Tk()
        root.title("Z-Tag")

    listbox = MultiColumnListbox()

    # create a toplevel menu
    menubar = tk.Menu(root)
    file = tk.Menu(menubar)
    file.add_command(label="Select Base Directory", command=listbox.add_rootdir_dialog)
    file.add_command(label="Select Import Directory", command=listbox.add_importdir_dialog)
    file.add_command(label="Select DB File", command=listbox.add_db_dialog)
    file.add_command(label="Quit!", command=client_exit)
    menubar.add_cascade(label="File", menu=file)

    # display the menu
    root.config(menu=menubar)
    root.mainloop()
