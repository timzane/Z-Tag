#!/usr/bin/env python

import datetime
import hashlib
import os
import os
import re
import sqlite3
import sys
import time
import timeit
from FileUtils import *
from datetime import datetime, date
from sys import platform as _platform


class DBFileListing:

    def __init__(self, dblocation=None,local=False):
        print("DBFile Listing Class Created")

        if dblocation is None:
            dblocation = self.get_db_location()

        if os.path.isfile(dblocation):
            print("File Exists Opening:", dblocation)
        else:
            print("File Does not exist", dblocation)
            if not local:
                self.create_new_db(dblocation)
                self.fill_db_tables(dblocation)
            else:
                self.create_new_db_local(dblocation)

        print("Setting DB Location to : ",dblocation)
        self.db = sqlite3.connect(dblocation)
        self.cursor = self.db.cursor()

    def update_progress(self, progress):
        bar_length = 20  # Modify this to change the length of the progress bar
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(bar_length*progress))
        text = "\rPercent: [{0}] {1}% {2}".format("="*block + " "*(bar_length-block), progress*100, status)
        sys.stdout.write(text)
        sys.stdout.flush()

# Linking table Functions  ************

    def linking_table_add(self, table_name, field1_column, field2_column, field1, field2):

        # First Check if Exist before inserting

        sql = "select * from " + table_name + " where "+field1_column+"=? AND "+field2_column+"=?"
        sqlinsert = "INSERT INTO "+table_name+"("+field1_column+","+field2_column+") VALUES (?,?)"
        conflictrows = self.cursor.execute(sql, (field1, field2))
        if conflictrows.fetchall():
            return -1
        else:
            self.cursor.execute(sqlinsert, (field1, field2))
            self.db.commit()
            return self.cursor.lastrowid

    def linking_table_remove(self, table_name, field1_column, field2_column, field1, field2):

        sql = "select * from " + table_name + " where " + field1_column + "=? AND " + field2_column + "=?"
        sqldelete = "DELETE FROM " + table_name + " WHERE ID=?"
        sqlcheckfield2 = "select * from " + table_name + " where " + field2_column + "=?"
        conflictrows = self.cursor.execute(sql, (field1, field2))
        idnum = conflictrows.fetchone()

        if idnum:
            # Found a Match, now remove
            self.cursor.execute(sqldelete, (idnum[0],))
            self.db.commit()
            # Now Check if any remaining of field2
            conflictrows = self.cursor.execute(sqlcheckfield2, (field2,))
            idnum = conflictrows.fetchone()
            if idnum:
                # Field2 still has values in linking table
                return "Exist"
            else:
                return "Last"

        else:
            # No Match found, return False
            return "NoMatch"

    def get_filterid_from_text(self, filter_text):

        sql1 = "select ID from tblTagFilters where Filter = ?"
        self.cursor.execute(sql1, (filter_text,))
        filterid = self.cursor.fetchone()
        return filterid[0]

    def updatetagfilter(self, filter_text, new_filter_text):

        filterid = self.get_filterid_from_text(filter_text)
        sql1 = "UPDATE tblTagFilters set Filter = ? WHERE ID = ?"
        self.cursor.execute(sql1, (new_filter_text, filterid))

    def remove_filter_from_tag(self, filter_2_delete, tagid):

        filterid = self.get_filterid_from_text(filter_2_delete)
        result = self.linking_table_remove("tblTag2Filter", "TagID", "FilterID", tagid, filterid)
        print("Result of Filter Remove is: ", result)
        if result == "Last":
            filterdelete = "delete from tblTagFilters where ID = ?"
            self.cursor.execute(filterdelete, (filterid,))
            self.db.commit()

    def cat2tagexist(self, main_cat_id, tag_index):

        # Check if the category contains tag, if so return True
        conflictrows = self.cursor.execute('''select * from tblCat2Tag where TagID=? AND CategoryID=?''',
                                           (tag_index, main_cat_id))
        if conflictrows.fetchall():
            return True
        else:
            return False

    def add_tag_2_db_and_link(self, tag, category_index):

        # Check if Tag exists, if not Insert Tag
        tag_id = self.tagexist(2, tag)

        if (tag_id is False) & (category_index > 0):

            # Tag Doesnt Exist Insert Tag First and Get ID

            self.cursor.execute("insert into  tblTags (TagName) Values(?)", (tag,))
            self.cursor.execute('''select TagID from tblTags where TagName = ?''', (tag,))
            result = self.cursor.fetchone()
            tag_id = result[0]
        else:
            print("Tag exists:", tag_id)

        # add Category

        if category_index > 0:
            if not self.cat2tagexist(category_index, tag_id):
                self.cursor.execute("insert into  tblCat2Tag (CategoryID,TagID) Values(?,?)", (category_index, tag_id))
        self.db.commit()

    def get_tags_from_filter(self, filterstuple):

        tagidlist = set()
        tagquery = "select TagID from tblTag2Filter where tblTag2Filter.FilterID = ?"
        for filteritem in filterstuple:

            tag_ids = self.cursor.execute(tagquery, (filteritem,))
            for tagid in tag_ids:
                tagidlist.add(tagid[0])
        return tuple(tagidlist)

    def auto_tag_full_db(self):

        fullquery = "select fileID, filename from tblfilelisting where fileID  < 5"
        result = self.cursor.execute(fullquery)
        count = 0

        for row in result:

            tag_ids = self.add_tag_from_filter(row[1])
            for tagid in tag_ids:
                did_insert = self.linking_table_add("tblfile2tag", "TagID", "FileID", tagid, row[0])
                if did_insert > 0:
                    count = count + 1

        return count

    # Add/Remove Functions

    def add_main_category(self, categoryname):

        existflag = self.tagexist(1, categoryname)
        if existflag:
                return False
        else:
                print("insert")
                self.cursor.execute('''insert into  tblMainCategory (MainCategoryName) Values(?) ''', (categoryname,))
                self.db.commit()
                return True

    def add_tag_from_filter(self, filename):

        # Searches filename for any filters and returns tuple of filter IDs
        tags = set()

        filtersquery = "select ID,Filter from tblTagFilters"
        filters = self.cursor.execute(filtersquery)
        for filteritem in filters:
            check = filteritem[1]
            flag = self.regex_filter(check, filename)
            if flag:
                # # Add Tag
                tags.add(filteritem[0])

        return self.get_tags_from_filter(tuple(tags))

    #  Table Functions

    def add_root_dir(self,rootDir):

        timestamp = datetime.now()
        sql1 = '''INSERT INTO tblRootDir (DirName) VALUES (?)'''
        self.cursor.execute(sql1, (rootDir,))
        self.db.commit()

    def logaction(self, severity, action, file_id, file_name, dry_run=False):

        if dry_run is False:
            print("Logging Action")
            self.cursor.execute('''INSERT INTO tblLogAction(Severity,Action,FileID,FileName,time) VALUES (?,?,?,?,?)''',
                                (severity, action, file_id, file_name, datetime.now()))
            self.db.commit()

    def delete_row_filelistingdb(self, file_id):

        sql1 = "delete from tblfilelisting where  fileID = ?"
        self.cursor.execute(sql1, (file_id,))
        self.db.commit()
        checksql = "select  fileID from tblfilelisting where  fileID = ?"
        self.cursor.execute(checksql, (file_id,))
        row = self.cursor.fetchall()
        print (len(row))
        if len(row)>1:
            print("File NOT removed from filelisting")
            return False
        else:
            print("File removed from filelisting")
            return True

    def add_file_to_db(self, fname, root_dir_id, localdirname, mdhashpartial, filesizef, modtimesec, ctimesec):

        timestamp = datetime.now()
        sql1 = '''INSERT INTO tblfilelisting(filename,date_entered,rootDir,filedirlocal) VALUES (?,?,?,?)'''
        self.cursor.execute(sql1, (fname, timestamp, root_dir_id, localdirname))
        self.db.commit()
        file_id = self.get_last_file_inserted(fname, timestamp)

        ctime = datetime.fromtimestamp(ctimesec).strftime('%Y-%m-%d %H:%M:%S')
        modtime = datetime.fromtimestamp(modtimesec).strftime('%Y-%m-%d %H:%M:%S')

        # self.modify_table_column(file_id,"filename",fname,False)

        self.modify_table_column(file_id, "date_entered", timestamp, False)
        self.modify_table_column(file_id, "last_checked", timestamp, False)
        self.modify_table_column(file_id, "md5hash_partial", mdhashpartial, False)
        self.modify_table_column(file_id, "filesize", filesizef, False)
        self.modify_table_column(file_id, "modtime", modtime, False)
        self.modify_table_column(file_id, "ctime", ctime, False)
        self.modify_table_column(file_id, "modtimesec", modtimesec, False)
        self.modify_table_column(file_id, "ctimesec", ctimesec, False)
        print("Added File ", fname)
        return file_id

    def modify_table_column(self,  file_id, column, updatetext, dry_run=True):

        if dry_run is False:
            sql1 = "UPDATE tblfilelisting set " + column + " = ?  WHERE fileID = ?"
            sql2 = "UPDATE tblfilelisting set last_checked = ?  WHERE fileID = ?"
            self.cursor.execute(sql1, (updatetext, file_id))
            self.cursor.execute(sql2, (datetime.now(), file_id))
            self.db.commit()
        else:
            print("Dry Run Only: Changing Column:", column, "to ", updatetext)

    def modify_table_column_new(self, db_table, row_id, column, updatetext, dry_run=True):

        if dry_run is False:
            sql1 = "UPDATE " + db_table + " set " + column + " = ?  WHERE ID = ?"
            self.cursor.execute(sql1, (updatetext, row_id))
            self.db.commit()
        else:
            print("Dry Run Only: Changing Column:", column, "to ", updatetext)

    def delete_children(self, children, tree):

        #  Recursive Function to Delete Tagged Children

        for child in children:
            itemstags = tree.item(child, "tags")
            anychildren = tree.get_children(child)
            if anychildren:
                self.delete_children(anychildren, tree)
            if "delete" in itemstags:
                self.file_delete_and_purge(child, tree)
                self.delete_all_tags(child)

    def logrename(self, olddir, oldfile, newdir, newfile, dry_run=False):

        if dry_run is False:
            print("Logging Action")
            self.cursor.execute('''INSERT INTO tblrenamelog (olddir, oldname, newdir, newname) VALUES (?,?,?,?)''',
                                (olddir, oldfile, newdir,newfile))
            self.db.commit()

    def rename_operation(self, olddir, oldfile, newdir,newfile):

        old = os.path.join(olddir,oldfile)
        new = os.path.join(newdir,newfile)

        oldflag = os.path.isfile(old)
        newflag = os.path.isfile(new)
        newdirflag = os.path.isdir(newdir)
        if oldflag and not newflag and newdirflag:
            print("Should be good to do operation")
            # First Rename File
            flag = os.rename(old, new)
            self.logrename(olddir, oldfile, newdir, newfile)
            print("result is ",flag)
            return True
        else:
            # return False
            if not oldflag:
                return "File not Found"
            elif newflag:
                return "File Exists at New Location"
            elif not newdirflag:
                return "New Dir does not exist"
            else:
                return "Error"

    def set_default_parameter(self, parameter, value):

        if self.get_default_parameter(parameter) == False:
            self.cursor.execute('''insert into  tblDefaults (Parameter,Value) Values(?,?) ''', (parameter,value))
            self.db.commit()
        else:
            sql1 = "UPDATE tblDefaults set Value = ?  WHERE Parameter = ?"
            self.cursor.execute(sql1, (value, parameter))
            self.db.commit()

    def get_default_parameter(self, parameter):

        query = '''select Value from tblDefaults where Parameter = ?'''
        rows_count = self.cursor.execute(query,(parameter,))
        result = self.cursor.fetchone()
        if result is not None:
            directory = result[0]
            return directory
        else:
            return False

    def remove_filedb_linked_tags(self,file_id):
        None

    def file_delete_and_purge(self, childtoremove, tree):

        childvalues = tree.item(childtoremove, "values")
        file_index = childvalues[0]
        filename = childvalues[1]
        directory = childvalues[2]
        recycledir = self.get_default_parameter("RecycleFolder")

        # Check to make sure file is there
        flag = self.rename_operation(directory, filename, recycledir, filename)
        if flag is True:
            print("File exists deleting.+.+")
            tree.delete(childtoremove)
            self.delete_row_filelistingdb(file_index)
            self.delete_all_tags(file_index)
                    #  Remove tags code goes here
        else:
            print("Error:", flag
                  )

    def delete_all_tags(self, file_id):

        # Delete All Tags
        query = '''select  ID from tblfile2tag where fileID = ?'''
        deletequery = '''DELETE FROM tblfile2tag WHERE ID=?'''

        self.cursor.execute(query, (file_id,))
        rows = self.cursor.fetchall()
        for row in rows:
            self.cursor.execute(deletequery, row)

        # Delete System Tags
        query = '''select ID from tblSystemTag2File where fileid = ?'''
        deletequery = '''DELETE FROM tblSystemTag2File WHERE ID=?'''
        self.cursor.execute(query, (file_id,))
        rows = self.cursor.fetchall()
        for row in rows:
            self.cursor.execute(deletequery, row)
        self.db.commit()

    def draw_progress_bar(self, percent, bar_length=20):
        sys.stdout.write("\r")
        progress = ""
        for i in range(bar_length):
            if i < int(bar_length * percent):
                progress += "="
            else:
                progress += " "
        sys.stdout.write("[ %s ] %.2f%%" % (progress, percent * 100))
        sys.stdout.flush()
    #    Basic Table Ops              #

    def is_file_missing(self, file_id):
        self.cursor.execute("select * from tblSystemTag2File where systemtag=1 AND fileid=?", (file_id,))
        flag = self.cursor.fetchall()
        if flag:
            return True
        return False

    def restore_missing_file(self, file_id):
        self.linking_table_remove("tblSystemTag2File", "fileid", "systemtag", file_id, 1)

    def refresh_file(self, file_id):

        (filedir, filename) = self.get_filename_path(file_id)
        mdhash = generate_file_md5_short(filedir, filename)
        fileandpath = filedir + filename
        if os.path.isfile(fileandpath):
            filesizef = os.path.getsize(fileandpath)
            modtimesec = os.path.getmtime(fileandpath)
            ctimesec = os.path.getctime(fileandpath)
            ctime = datetime.fromtimestamp(ctimesec).strftime('%Y-%m-%d %H:%M:%S')
            modtime = datetime.fromtimestamp(modtimesec).strftime('%Y-%m-%d %H:%M:%S')
            updatetime = datetime.now()
            self.modify_table_column(file_id,"md5hash_partial",mdhash,False)
            self.modify_table_column(file_id, "filesize", filesizef, False)
            self.modify_table_column(file_id, "modtime", modtime, False)
            self.modify_table_column(file_id, "ctime", ctime, False)
            self.modify_table_column(file_id, "last_checked", updatetime, False)
            self.modify_table_column(file_id, "modtimesec", modtimesec, False)
            self.modify_table_column(file_id, "ctimesec", ctimesec, False)
            self.restore_missing_file(file_id)
        else:
            # add code for missing file
            self.linking_table_add("tblSystemTag2File", "fileid", "systemtag", file_id, 1)

    def perform_hash_size(self, file_id, mdhashtype="partial"):

        (filedir, filename) = self.get_filename_path(file_id)
        if mdhashtype == "partial":
            mdhash = generate_file_md5_short(filedir, filename)
            sqlquery = '''UPDATE tblfilelisting set md5hash_partial = ? , filesize = ? WHERE fileID = ?'''
        else:
            mdhash = generate_file_md5(filedir, filename)
            sqlquery = '''UPDATE tblfilelisting set md5hash_full = ? , filesize = ? WHERE fileID = ?'''

        # mdhash = generate_file_md5_short(filedir, filename)
        fileandpath = filedir + filename
        filesizef = os.path.getsize(fileandpath)
        self.cursor.execute(sqlquery, (mdhash, filesizef, file_id))
        self.db.commit()

    def get_filename_path(self, file_id):

        sql1 = '''SELECT fileID, filename,(tblRootDir.DirName || filedirlocal) as filedir, filesize FROM tblfilelisting
                            inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID  WHERE fileID =?'''
        self.cursor.execute(sql1, (file_id, ))

        rowselected = self.cursor.fetchone()
        return rowselected[2], rowselected[1]

    def get_duplicate_parameter(self, file_id, duplicate_type=None):

        if duplicate_type == "filename":
            sql1 = '''select filename from tblfilelisting \
                                 WHERE fileID =?'''
        else:
            sql1 = '''select tblfilelisting.md5hash_partial from tblfilelisting \
                             WHERE fileID =?'''
        self.cursor.execute(sql1, (file_id,))
        rowselected = self.cursor.fetchone()
        return rowselected[0]

    def get_file_hash(self, file_id, hashtype=None):

        sql1 = '''select tblfilelisting.md5hash_partial from tblfilelisting \
                             WHERE fileID =?'''
        self.cursor.execute(sql1, (file_id,))
        rowselected = self.cursor.fetchone()
        return rowselected[0]

    def is_file_at_location(self, file_id):

        (filedir, filename) = self.get_filename_path(file_id)
        filenamepath = filedir + filename
        print("File name path to check is:", filenamepath)

        if os.path.isfile(filenamepath):
            print("Check for file: found")
            return True
        else:
            print("Check for file: Could not find")
            return False

    def is_file_in_db_return_suggestion(self, fname, searchdir, filesizef, mdhashpartial):

        sql1 = '''SELECT fileID FROM tblfilelisting
                        inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
                        WHERE filename=? AND filedirlocal =? AND  filesize=? AND md5hash_partial=?'''

        sql2 = '''SELECT fileID,filename FROM tblfilelisting
                        inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
                        WHERE filedirlocal =? AND  filesize=? AND md5hash_partial=?'''

        sql3 = '''SELECT fileID FROM tblfilelisting
                        inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
                        WHERE filename =? AND  filesize=? AND md5hash_partial=?'''

        sql4 = '''SELECT fileID FROM tblfilelisting
                    inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
                    WHERE md5hash_partial=? AND filesize=? '''

        sql5 = '''SELECT fileID FROM tblfilelisting
                        inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
                        WHERE filename=? AND filedirlocal =?'''

        sql6 = '''SELECT fileID FROM tblfilelisting
                    inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
                    WHERE md5hash_partial=?'''

        # Check for Exact Match
        self.cursor.execute(sql1, (fname, searchdir, filesizef, mdhashpartial))
        idnum = self.cursor.fetchone()
        if idnum is not None:
            return "Found", idnum[0]

        # Check if file exists somewhere else
        self.cursor.execute(sql2, (searchdir, filesizef, mdhashpartial))
        idnum = self.cursor.fetchone()
        if idnum is not None:
            print("Matching Hash Found for file", idnum[1])
            # Check if found file exists
            exist = self.is_file_at_location(idnum[0])
            if exist:
                # Add Duplicate
                return "Duplicate", idnum[0]
            else:
                # Rename
                return "Rename", idnum[0]

        self.cursor.execute(sql3, (fname, filesizef, mdhashpartial))
        idnum = self.cursor.fetchone()
        if idnum is not None:
            # Matching file in a different diectory rougn
            exist = self.is_file_at_location(idnum[0])
            if exist:
                return "Duplicate", idnum[0]
            else:
                print("Move")
                return "Move", idnum[0]

        self.cursor.execute(sql4, (mdhashpartial, filesizef))
        idnum = self.cursor.fetchone()
        if idnum is not None:
            exist = self.is_file_at_location(idnum[0])
            if exist:
                return "Duplicate", idnum[0]
            else:
                print("MoveRename")
                return "MoveRename", idnum[0]

        self.cursor.execute(sql5, (fname, searchdir))
        idnum = self.cursor.fetchone()
        if idnum is not None:
            print("Update")
            return "Update", idnum[0]

        self.cursor.execute(sql6, (mdhashpartial,))
        idnum = self.cursor.fetchone()
        if idnum is not None:
            print("Duplicate")
            return "Duplicate", idnum[0]

        return "Add", None

    def get_last_file_inserted(self, filename, timestamp):
        sql1 = '''SELECT fileID FROM tblfilelisting  WHERE filename=?  and  date_entered=?'''
        self.cursor.execute(sql1, (filename, timestamp))
        idnum = self.cursor.fetchone()
        if idnum is not None:
            return idnum[0]
        else:
            return -1

    def is_file_in_db(self, fname, searchdir):

        sql1 = '''SELECT fileID, filename,(tblRootDir.DirName || filedirlocal) as filedir FROM tblfilelisting
                                    inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID  
                                    WHERE filename=? AND filedir =?'''

        self.cursor.execute(sql1, (fname, searchdir))
        idnum = self.cursor.fetchone()
        if idnum is not None:
            return idnum

    # def is_file_in_db_newlocation_delete(self, filename, md5hashpartial, filesize, md5hashtype="partial"):
    #
    #     if md5hashtype == "partial":
    #         sql1 = '''SELECT fileID, filename,(tblRootDir.DirName || filedirlocal) as filedir FROM tblfilelisting
    #                             inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
    #                             WHERE filename=? AND md5hash_partial =? and filesize = ?'''
    #     else:
    #         sql1 = '''SELECT fileID, filename,(tblRootDir.DirName || filedirlocal) as filedir FROM tblfilelisting
    #                             inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
    #                             WHERE filename=? AND md5hash_full =? and filesize = ?'''
    #
    #     self.cursor.execute(sql1, (filename, md5hashpartial, filesize))
    #     idnum = self.cursor.fetchone()
    #     if idnum is not None:
    #         print("File Exists")
    #         return idnum[0]
    #     else:
    #         print("File Doesnt Exists")
    #         return False

    def get_tree_values_delete(self, file_id):

        sql1 = '''SELECT fileID, filename,(tblRootDir.DirName || filedirlocal) as filedir, filesize,
                    md5hash_partial FROM tblfilelisting
                    inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID  WHERE fileID = ?'''
        self.cursor.execute(sql1, (file_id,))
        result = self.cursor.fetchone()
        return result

    def get_file_and_directory(self, file_id):

        sql1 = '''SELECT fileID, filename,(tblRootDir.DirName || filedirlocal) as filedir, filesize FROM tblfilelisting
                                        inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID
                                        WHERE fileID =?'''
        conflictrows = self.cursor.execute(sql1, (file_id,))
        returndata = conflictrows.fetchone()
        print("Delete File", returndata[1], " in directory", returndata[2])
        return returndata[1], returndata[2]

    def get_duplicate_field(self,search):

        sql1 = '''select duplicatefield from tblSearchTypes where searchtype = ?'''
        self.cursor.execute(sql1,(search,))
        result = self.cursor.fetchone()
        return result[0]

    def get_search_combo_values(self, page="mainmenu"):
        sql1 = '''select searchtype from tblSearchTypes where ''' + page +   '''=  -1'''
        self.cursor.execute(sql1)
        result = self.cursor.fetchall()
        flatten = sum(result, ())
        return tuple(flatten)

    def get_query_from_search(self, search):

        sql1 = '''select query,searchfield from tblSearchTypes where searchtype = ?'''
        self.cursor.execute(sql1,(search,))
        (result,searchfield) = self.cursor.fetchone()
        return result,searchfield

    def tree_query(self, searchtype, search_text=None, duplicate_type=None):



        (sql,number) = self.get_query_from_search(searchtype)
        if number > 0:
            args = ['%' + search_text + '%']
            self.cursor.execute(sql, args)
        else:
            self.cursor.execute(sql)

        result = self.cursor.fetchall()

        if searchtype == 2 or searchtype == "regex":
            newtuple = ()
            for row in result:
                if self.regex_filter(search_text, row[1]):
                    newtuple = newtuple + (row, )
            return newtuple
        else:
            return result

    def filter_tag_query(self, tagid):

        sql1 = '''select tblfilelisting.fileID,tblfilelisting.filename, 
                    (tblRootDir.DirName || tblfilelisting.filedirlocal) as filedir,tblfilelisting.filesize,
                    tblfilelisting.md5hash_partial from  tblfilelisting
                    inner join  tblfile2tag on tblfilelisting.fileID = tblfile2tag.FileID 
                    inner join tblRootDir on tblRootDir.ID = tblfilelisting.rootDir
                    where tblfile2tag.TagID = ?'''
        self.cursor.execute(sql1, (tagid,))
        result = self.cursor.fetchall()
        return result

    # Tree Functions

    def values_for_tree_insert(self, file_id):

        sql1 = '''SELECT fileID, filename,(tblRootDir.DirName || filedirlocal) as filedir, filesize FROM tblfilelisting
                    inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID  WHERE fileID =?'''
        self.cursor.execute(sql1, [file_id])
        return tuple(self.cursor.fetchone())

    def query_tag_from_file_id(self, file_id, tag):

        cursorcategory = self.db.cursor()
        sql1 = '''select tblfilelisting.fileID, filename
                          from tblfilelisting inner join  tblfile2tag on  tblfilelisting.fileID = tblfile2tag.FileID
                          where   tblfile2tag.TagID = ? and  tblfilelisting.fileID = ?'''

        cursorcategory.execute(sql1, (tag, file_id))
        result = cursorcategory.fetchall()
        flag = (len(result))
        if flag == 0:
            return False
        else:
            return True

    def query_tag_tree(self, category=None):
        if category == "all":
            sql1 = 'select tblTags.TagId,TagName,tblMainCategory.MainCategoryName,count(tblTag2Filter.FilterID ) from tblTags \
                left  join  tblCat2Tag on  tblCat2Tag.TagID =  tblTags.TagID \
                left join tblTag2Filter on  tblTag2Filter.TagID = tblTags.TagID \
                left join tblTagFilters on tblTagFilters.ID = tblTag2Filter.FilterID \
                left join tblMainCategory on tblMainCategory.MainCatID	= tblCat2Tag.CategoryID \
                group by  tblTags.TagId,TagName \
                ORDER BY TagName'
            self.cursor.execute(sql1)
        else:
            sql1 = 'select tblTags.TagId,TagName,tblMainCategory.MainCategoryName,count(tblTag2Filter.FilterID ) from tblTags  \
                    left  join  tblCat2Tag on  tblCat2Tag.TagID =  tblTags.TagID \
                    left join tblTag2Filter on  tblTag2Filter.TagID = tblTags.TagID \
                    left join tblTagFilters on tblTagFilters.ID = tblTag2Filter.FilterID \
                    left join tblMainCategory on tblMainCategory.MainCatID	= tblCat2Tag.CategoryID \
                    where tblCat2Tag .CategoryID= ? \
                    group by  tblTags.TagId,TagName \
                    ORDER BY TagName'
            self.cursor.execute(sql1, (category,))
        result = self.cursor.fetchall()
        return result

    def query_leaf(self, file_id, sql):
        self.cursor.execute(sql, (file_id,))
        item = self.cursor.fetchone()
        return item

    def query_categories_return_list(self):
        # Get ALL Categories of Main List

        cursorcategory = self.db.cursor()
        categoryquery = "Select MainCatID,MainCategoryName from tblMainCategory"
        cursorcategory.execute(categoryquery)
        allcategories = cursorcategory.fetchall()

        return allcategories

    def query_tags(self, main_category_id=None):

        cursorcategory = self.db.cursor()
        if main_category_id == "All":
            categoryquery = "Select TagID,TagName from tblTags order by TagName"
            cursorcategory.execute(categoryquery)
        else:
            categoryquery = (
                "select tblTags.TagId,TagName from tblTags inner join  tblCat2Tag on  \
                 tblCat2Tag.TagID =  tblTags.TagID where tblCat2Tag .CategoryID=? order by TagName")
            cursorcategory.execute(categoryquery, (main_category_id,))
        allcategories = cursorcategory.fetchall()
        return allcategories

    def query_root_dir(self):

        rootdirquery = '''select ID,DirName from tblRootDir'''
        self.cursor.execute(rootdirquery)
        result = self.cursor.fetchall()
        return result

    def show_tagname_from_id(self, tagids):

        for tag in tagids:

            self.cursor.execute('''select TagNAme from tblTags where TagID = ?''', (tag,))
            result = self.cursor.fetchone()
            print(result[0])

    def regex_filter(self, filtertxt, string2check, lowercase=True):

        regex = filtertxt.replace('////', '//')
        compiled = re.compile(regex, re.IGNORECASE)
        result = compiled.search(string2check)

        if result:

            return True
        else:

            return False

    def filter_exists(self, filtertxt):

        conflictrows = self.cursor.execute('''select Filter from tblTagFilters where Filter = ?''', (filtertxt,))
        if (conflictrows.fetchall()):
            print("Conflict in Filter Exists")
            return True
        else:
            print("No Match")
            return False

    def add_filter_to_tag(self, filtertxt, tagid):

        if self.filter_exists(filtertxt):
            print("not adding filter")
            pass

        else:
            print("Adding filter")
            self.cursor.execute('''insert into  tblTagFilters (Filter) Values(?) ''', (filtertxt,))

        # Get ID of value filter from table

        sql = "select  ID  from tblTagFilters where Filter =?"
        self.cursor.execute(sql, (filtertxt,))
        result = self.cursor.fetchone()
        filter_id = result[0]
        print("Filter ID is ", filter_id)
        self.db.commit()

        # Add to linking table
        # self.link_filter_to_tag(tagid, filter_id)
        self.linking_table_add("tblTag2Filter", "TagID", "FilterID", tagid, filter_id)
        # self.db.commit()
        return filter_id

    def tagexist(self, search_type, tag):

        # search_type 1 is Main Category, search_type 2 is Tag

        if search_type == 1:
            # Check for Main Category
            conflictrows = self.cursor.execute("select MainCatID from tblMainCategory"
                                               " where MainCategoryName = ?", (tag,))
        elif search_type == 2:
            conflictrows = self.cursor.execute('''select TagID from tblTags where TagName = ?''', (tag,))
        else:
            conflictrows = None

        result = conflictrows.fetchone()

        if result:
            print("Conflict in Tag Exist")
            return result[0]
        else:
            return False

    def query_filter_from_tag_id(self, tag_id):

            cursorcategory = self.db.cursor()
            sql1 = ('select  tblTagFilters.Filter from tblTagFilters '
                    'Inner Join tblTag2Filter on tblTag2Filter.FilterID =tblTagFilters.ID '
                    'where tblTag2Filter.TagID=?')
            cursorcategory.execute(sql1, (tag_id,))
            result = cursorcategory.fetchall()
            return result

    def query_category_output2list(self, file_id):
            # Get Tags associated with this item from joining table
            # Returns a list of categories in format to add to tree

            cursorcategory = self.db.cursor()
            categoryquery = "Select tblTags.TagName from tblfile2tag Inner Join tblTags" \
                            " on tblfile2tag.TagID = tblTags.TagID where FileID =" + str(file_id)
            cursorcategory.execute(categoryquery)
            allcategories = cursorcategory.fetchall()
            allcats = ""
            for item123 in allcategories:
                    allcats = allcats + str(item123[0]) + ","
            allcats = allcats[:-1]

            # Do some converting from strings and stuff to get a new tuple
            tempstring = list()
            tempstring.append(allcats)

            return tempstring

    def query_maincategory_output2list(self, tag_id):

            # Get Categories associated with this item from joining table
            # Returns a list of categories in format to add to tree

            cursorcategory = self.db.cursor()
            categoryquery = "Select tblMainCategory.MainCategoryName from tblCat2Tag " \
                            "Inner Join tblMainCategory on tblCat2Tag.CategoryID = tblMainCategory.MainCatID " \
                            "where TagID = ?"
            cursorcategory.execute(categoryquery, (tag_id,))
            allcategories = cursorcategory.fetchall()

            allcats = ""
            for item in allcategories:
                    allcats = allcats + str(item[0]) + ","
            allcats = allcats[:-1]

            # Do some converting from strings and stuff to get a new tuple
            catlist = list()
            catlist.append(allcats)
            return catlist

    def query_category_output2list_of_cat_index(self, file_id):

            # Get Tags associated with this item from joining table
            # Returns a list of categories in a list of Category Indexes


            cursorcategory = self.db.cursor()
            categoryquery = ("Select tblTags.TagID from tblfile2tag Inner Join tblTags on tblfile2tag.TagID = tblTags.TagID where FileID =" + str(file_id))

            cursorcategory.execute(categoryquery)
            allcategories = cursorcategory.fetchall()

            allcats = []
            for item in allcategories:
                    print("lool", item[0])
                    temp = item[0]

                    print(type(allcats), type(temp))
                    allcats = allcats + [temp]

            print("AllCats before return", allcats)

            allcats = set(allcats)
            allcats = list(allcats)
            return allcats

    def get_platform(self):
        if _platform == "linux" or _platform == "linux2":
            print("Running on Linux...")
            return "Linux"
        elif _platform == "darwin":
            return "Darwin"
        elif _platform == "win32":
            return "Windows"

    def get_db_location(self):
        # Fix Later:  Fix so DB Location from File is smart enought
        # to know what platform I am running on (e.g. linux,windows,mac)

        platformtype = self.get_platform()

        user_db_location = read_config_file("Ztag", "dblocation")

        if user_db_location is None:

            print("DB not located in config")

            if _platform == "linux" or _platform == "linux2":
                print("Running on Linux...")
                user_db_location = os.getenv("HOME") + "/FileListing.db3"
                os.nice(20)

            elif _platform == "darwin":
                print("Running on Darwin (i.e. Mac)...")
                user_db_location = os.getenv("HOME") +  '/FileListing.db3'
            elif _platform == "win32":
                print("Running on Windows...")
                user_db_location = os.getenv("HOME") + '\FileListing.db3'

        else:
            print("DB located at:", user_db_location)

        return user_db_location

    def fix_tree_columns(self, tree_columns):
        for col in tree_columns:
            self.tree.heading(col, text=col.title(),
                              command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                             width=tkFont.Font().measure(col.title()))
        self.tree.pack()

    def check_root_dir(self, root_dir):

        sql1 = '''select * FROM tblRootDir where DirName = ?'''
        self.cursor.execute(sql1, (root_dir,))
        result = self.cursor.fetchone()
        if result:
            print(result)
            return result[0]
        else:
            print("helloaaa")
            # Doesnt exist/Add and return ID
            sql2 = '''INSERT INTO tblRootDir(DirName) VALUES(?)'''
            sql3 = '''SELECT ID from tblRootDir Where DirName =?'''

            self.cursor.execute(sql2, (root_dir,))
            self.cursor.execute(sql3, (root_dir,))
            result = self.cursor.fetchone()
            self.db.commit()
            return result[0]

    def get_root_dir_id(self,file_id):

        sql1 = '''select rootDir FROM tblfilelisting where fileID = ?'''
        self.cursor.execute(sql1, (file_id,))
        result = self.cursor.fetchone()
        if result:
            print(result)
            return result[0]
        else:
            return False

    def get_root_dir(self, root_dir_id=None):

        if root_dir_id is None:
            return ""
        sql1 = '''select DirName FROM tblRootDir where ID = ?'''
        self.cursor.execute(sql1, (root_dir_id,))
        result = self.cursor.fetchone()
        if result:
            print(result)
            return result[0]
        else:
            return False

    def get_file_info(self, dirName, fname, md5hashtype="partial"):
        fileandpath = dirName + "/" + fname

        if os.path.isfile(fileandpath):
            filesizef = os.path.getsize(fileandpath)
            modtimesec = os.path.getmtime(fileandpath)
            ctimesec = os.path.getctime(fileandpath)


            hfilesize = human_size(filesizef)
            start = timeit.timeit()
            if md5hashtype == "partial":
                #print("performing partial hash on " + fname)
                mdhash = generate_file_md5_short(dirName, fname)
            else:
                print("performing full hash")
                mdhash = generate_file_md5(dirName, fname)

            stop = timeit.timeit()
        else:
            print("File Does Not Exist")
            filesizef = -1
            mdhash = -1
            modtimesec = -1
            ctimesec = -1
        return (filesizef, mdhash, modtimesec, ctimesec)

    def import_filenames(self,  importDir, root_dir_id=None,dry_run=True,duplicate_check=True):

        # Check if rootDir is in importDir

        rootDir = self.get_root_dir(root_dir_id)
        if rootDir in (importDir + "/"):
            print("Check Good")
        else:
            print("Root Dir and importDir are not compatible")
            return False

        # Initialize Variables for statistics
        total_record_count = 0
        records_modified = 0
        records_added = 0

        # This can be set to exclude directories, not implemented yet
        # exclude = set(["ignorethisdirectory", "."])
        exclude = {"ignore_this_directoryABCD", "."}

        # Begin walking through all directories

        for dirName, subdirList, fileList in os.walk(importDir, topdown=True, followlinks=False):

            [subdirList.remove(d) for d in list(subdirList) if d in exclude]

            # searchdir = dirName + "/"
            searchdir = dirName
            print("Search Dir is: ", searchdir)
            fnamecount = 0
            for fname in fileList:
                total_record_count += 1
                localdirname = dirName[len(rootDir):] + "/"
                (filesizef, mdhashpartial, modtimesec, ctimesec) = self.get_file_info(dirName, fname)

                if duplicate_check:
                    (decision, file_id) = self.is_file_in_db_return_suggestion(fname, localdirname, filesizef,
                                                                           mdhashpartial)
                else:
                    decision = "Add"

                fnamecount += 1
                self.update_progress(fnamecount/len(fileList))
                # print("Decision and Fileid",decision," ", file_id)
                localdirname = dirName[len(rootDir):] + "/"
                if decision == "Found":
                    # print("Found..Do Nothing")
                    sys.stdout.write('#')
                    sys.stdout.flush()
                elif decision == "Rename":
                    print("Rename file: " + fname)
                    self.modify_table_column(file_id, "filename", fname, dry_run)
                    self.logaction(1, "Rename", file_id, fname, dry_run)
                    records_modified += 1
                elif decision == "Move":
                    print("Move")
                    self.modify_table_column(file_id, "filedirlocal", localdirname, dry_run)
                    self.logaction(1, "Move", file_id, fname, dry_run)
                    records_modified += 1
                elif decision == "MoveRename":
                    print("MoveRename")
                    self.modify_table_column(file_id, "filedirlocal", localdirname, dry_run)
                    self.modify_table_column(file_id, "filename", fname, dry_run)
                    self.logaction(1, "Rename", file_id, fname, dry_run)
                    records_modified += 1
                elif decision == "Update":
                    print("Update")

                else:
                    print("Add")
                    records_added += 1
                    # File is Brand New Add
                    if dry_run:
                        print("Only Dry Run: Adding File: ", fname)
                    else:
                        new_file_id = self.add_file_to_db(fname, root_dir_id, localdirname, mdhashpartial,
                                                          filesizef, modtimesec, ctimesec)
                        if decision == "Duplicate":
                            print("Add Action for duplicate")
                        self.logaction(1, "File Added", new_file_id, fname, dry_run)
                        self.db.commit()

        print("Total Files Searched:", total_record_count)
        print("Total Files Modified:", records_modified)
        print("Total Files Added:", records_added)

    def fill_db_tables(event, dblocation):

        db = sqlite3.connect(dblocation)
        cursor = db.cursor()

        search_types = (("Plain Text", "SELECT fileID FROM tblfilelisting WHERE filename like ?","1","","-1",""),
                        ("Dir","SELECT fileID FROM tblfilelisting inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID  WHERE filedir like ?","1","",-1,""),
                        ("regex","SELECT fileID FROM tblfilelisting inner join tblRootDir on tblfilelisting.rootDir = tblRootDir.ID",0,"",-1,""),
                        ("Newest","SELECT fileID FROM tblfilelisting ORDER by date_entered DESC limit 200",0,"",-1,""),
                        ("Random 100","SELECT fileID FROM tblfilelisting ORDER BY RANDOM() LIMIT 100",0,"",-1,""))

        print(search_types)

        for search, query, searchfield, duplicatefield, mainmenu, duplicatepage in search_types:

            cursor.execute("INSERT INTO tblSearchTypes (searchtype,query,searchfield,duplicatefield,"
                           "mainmenu,duplicatepage) values (?,?,?,?,?,?)", (search, query, searchfield, duplicatefield, mainmenu, duplicatepage))
            db.commit()

    def create_new_db(event, dblocation):

        db = sqlite3.connect(dblocation)
        cursor = db.cursor()

        cursor.execute("CREATE TABLE 'tblfilelisting' (	`fileID`	INTEGER NOT NULL,	`filename`	text NOT NULL,"
                       "	`date_entered`	NUMERIC,	`last_checked`	NUMERIC,	`filesize`	NUMERIC,"
                       "`md5hash_partial` TEXT,	`md5hash_full`	TEXT,"
                       " 	`filedirlocal`	TEXT NOT NULL,	`rootDir`	INTEGER NOT NULL,"
                       "	`modtime`	INTEGER,	`ctime`	INTEGER,	`modtimesec`	INTEGER,"
                       "	`ctimesec`	INTEGER,	PRIMARY KEY(fileID))")
        cursor.execute("CREATE TABLE 'tblCat2Tag' (	`ID`	INTEGER NOT NULL,	`CategoryID`	NUMERIC NOT NULL,"
                     "	`TagID`	NUMERIC NOT NULL,'timestamp' INTEGER DEFAULT current_timestamp,	PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE `tblLogAction` (`ID` INTEGER NOT NULL,	`Severity`	INTEGER NOT NULL,"
                     "	`Action`	TEXT NOT NULL,	`FileID`	INTEGER NOT NULL,	`FileName`	TEXT NOT NULL,"
                     "	`time`	INTEGER, PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE 'tblMainCategory' (	`MainCatID`	INTEGER NOT NULL,"
                     "	`MainCategoryName`	TEXT NOT NULL,	PRIMARY KEY(MainCatID))")
        cursor.execute("CREATE TABLE 'tblRootDir' (	`ID`	INTEGER NOT NULL,	`DirName`	TEXT NOT NULL,"
                     "	PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE 'tblSearchTypes' (	`ID`	INTEGER NOT NULL,	`searchtype`	TEXT NOT NULL," 
                        "`query`	REAL NOT NULL,	`searchfield`	NUMERIC NOT NULL," 
                        "	`duplicatefield`	TEXT, `mainmenu`	INTEGER," 
                        "	`duplicatepage`	INTEGER,	PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE 'tblSystemTag2File' (	`ID`	INTEGER NOT NULL,	`fileid`	INTEGER NOT NULL,"
                     "	`systemtag`	INTEGER NOT NULL,	PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE `tblSystemTags` (	`ID`	INTEGER NOT NULL,	`tag`	TEXT NOT NULL,"
                     "	PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE `tblTag2Filter` (	`ID`	INTEGER,	`TagID`	INTEGER NOT NULL,"
                     "	`FilterID`	INTEGER NOT NULL,	PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE 'tblTagFilters' (	`ID`	INTEGER,	`Filter`	TEXT,	PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE 'tblTags' (	`TagID`	INTEGER NOT NULL,	`TagName`	TEXT NOT NULL,"
                     "	PRIMARY KEY(TagID))")
        cursor.execute("CREATE TABLE 'tblfile2tag' (	`ID`	INTEGER NOT NULL,	`TagID`	NUMERIC,"
                     "	`FileID`	NUMERIC, 'timestamp' INTEGER DEFAULT current_timestamp,	PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE 'tblrenamelog' (`ID`	INTEGER NOT NULL,`oldname`	TEXT NOT NULL," 
                                                  "`newname`	TEXT NOT NULL,`olddir`	TEXT NOT NULL," 
                                                  "`newdir`	TEXT NOT NULL," 
                                                  "`datetimestamp`	TEXT NOT NULL DEFAULT current_timestamp," 
                                                  " PRIMARY KEY(ID))")
        cursor.execute("CREATE TABLE `tblDefaults` (ID INTEGER NOT NULL,	Parameter	TEXT NOT NULL,"
                       "	Value	TEXT NOT NULL,	PRIMARY KEY(ID))")

        db.commit()

    def create_new_db_local(event, dblocation):

        db = sqlite3.connect(dblocation)
        cursor = db.cursor()
        cursor.execute("CREATE TABLE 'tblfilelisting' (	`fileID`	INTEGER NOT NULL,	`filename`	text NOT NULL,"
                     "	`date_entered`	NUMERIC,	`last_checked`	NUMERIC, `filesize`	NUMERIC,"
                     "	`md5hash_partial`	TEXT,	`md5hash_full`	TEXT,	`filedirlocal`	TEXT NOT NULL,"
                     "	`rootDir`	INTEGER ,	`modtime`	INTEGER, `ctime`	INTEGER,"
                     "	`modtimesec`	INTEGER,	`ctimesec`	INTEGER,	PRIMARY KEY(fileID))")
        cursor.execute("CREATE TABLE `tblLogAction` (`ID` INTEGER NOT NULL,	`Severity`	INTEGER NOT NULL,"
                     "	`Action`	TEXT NOT NULL,	`FileID`	INTEGER NOT NULL,	`FileName`	TEXT NOT NULL,"
                     "	`time`	INTEGER, PRIMARY KEY(ID))")
        db.commit()
