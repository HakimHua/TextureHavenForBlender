import os
import bpy
import sys

import sqlite3

from urllib.request import build_opener
from urllib.request import install_opener
from urllib.request import urlretrieve
import threading

from bpy.props import StringProperty
from bpy.props import FloatProperty
from bpy.props import BoolProperty


def get_preferences(context):
    return context.preferences.addons[__package__].preferences

class DataSet:
    def __init__(self, context, path):
        self.git_url = "https://github.com/HakimHua/TextureHavenSpider.git"
        self.gitee_url = "https://gitee.com/Huakim/TextureHavenSpider.git"

        self.context = context
        self.path = path

        self.DataFile = path + "/Thumbails/TextureHavenDataSet.db"

        self.dataInfo = []

    def download_thread(self, git_path, useGitee):
        if os.path.exists(git_path):
            cmd = ""
            if useGitee:
                cmd = "%s clone %s %s" % (git_path, self.gitee_url, self.path)
            else:
                cmd = "%s clone %s %s" % (git_path, self.git_url, self.path)
            os.system(cmd)

    def download(self, git_path, useGitee):
        download_t = threading.Thread(target=self.download_thread, args=[git_path,useGitee,])
        download_t.start()

    def getTextureCategory(self):
        categ = set()

        conn = sqlite3.connect(self.DataFile)
        cur = conn.cursor()

        command = "SELECT categ_tag from TEXTUREHAVEN"

        d = cur.execute(command)

        for row in d:
            self.dataInfo.append(row)
            categ.add(row[0])

        conn.close()
        return categ


class TH_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    CatchDir: StringProperty(
        description = "Catch Path",
        subtype = 'DIR_PATH',
        default = os.path.dirname(os.path.realpath(__file__)) + "/Database/"
    )

    useGitee: BoolProperty(
        name = "use gitee",
        description = "The database will be downloaded from gitee when checked, otherwise from github!",
        default = False
    )

    gitPath: StringProperty(
        description = "Git PATH",
        subtype = 'FILE_PATH',
        default = os.path.dirname(os.path.realpath(__file__)) + "/git/win/64/bin/git.exe"
    )

    '''if sys.platform == "win32":
        gitPath = os.path.dirname(os.path.realpath(__file__)) + "bin/64/bin/git.exe"    
    '''
    def draw(self, context):

        layout = self.layout
        
        row = layout.row()
        row.prop(self, "CatchDir")

        row = layout.row()
        row.prop(self, "useGitee")

        row.prop(self, "gitPath")

        row = layout.row()
        row.operator("th.update")

class updateDatabaseOperator(bpy.types.Operator):
    bl_idname = "th.update"
    bl_label = "Update DB"

    def execute(self, context):
        pr = get_preferences(context)

        if not os.path.exists(pr.CatchDir):
            os.mkdir(pr.CatchDir)

        data = DataSet(context, pr.CatchDir)
        data.download(pr.gitPath, pr.useGitee)

        return {'FINISHED'}
