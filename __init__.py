import os
import sqlite3

import bpy
from bpy.props import StringProperty

import bpy.utils.previews

from .THPreference import TH_Preference, updateDatabaseOperator
from .THPreference import get_preferences
from .THPanel import TH_Panel

from .THOperator import TH_OT_MaterialOperator
from .THOperator import TH_OT_MaterialBuildOp

bl_info = {
    "name": "Texture Haven",
    "description": "Browse and download TextureHaven materials",
    "author": "Kangjian-Hua",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Material",
    "wiki_url": "https://texturehaven.com/",
    "category": "Development"
}

## 类别缩略图
def get_category_item(self, context):
    pr = get_preferences(context)
    db_path = pr.CatchDir + "/Thumbails/TextureHavenDataSet.db"
    categs = {}   # 所有categ的名称

    categ_item = []  ## categ的缩略图

    # context如果为空，则返回空
    if context is None:
        return categ_item

    # 判断之前是否已经读取
    pcoll = thumb_collection["category"]
    if pcoll.categ_name == "category":
        return pcoll.categ_preview

    # 如果之前没有读取，连接数据库开始读取
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    command = "SELECT categ_tag, categ_path from TEXTUREHAVEN"
    d = cur.execute(command)

    # 汇总所有categ名称
    for row in d:
        categs[row[0]] = pr.CatchDir + row[1]
    conn.close()

    ## 为每个列别都新建一个preview
    for c in categs:
        apcoll = bpy.utils.previews.new()
        apcoll.categ_name = ""
        apcoll.categ_preview = ()

        thumb_collection[c] = apcoll

    i = 0
    for c in categs:
        categ_name = c
        categ_path = categs[c]

        # 读取缩略图
        categ_icon = pcoll.load(categ_name, categ_path, "IMAGE")

        categ_item.append((categ_name, categ_name, categ_name, categ_icon.icon_id, i))
        i += 1
    # 应用缩略图
    pcoll.categ_preview = categ_item
    pcoll.categ_name = "category"

    return pcoll.categ_preview

## 获取每个material的缩略图
def get_material_item(self, context):
    wm = context.window_manager
    categ_name = wm.th_categ

    # 每种材质的缩略图
    material_item = []

    material_thum = {}

    if categ_name not in thumb_collection:
        return ()
    
    pcoll = thumb_collection[categ_name]
    if pcoll.categ_name == categ_name:
        return pcoll.categ_preview
    
    pr = get_preferences(context)
    db_path = pr.CatchDir + "/Thumbails/TextureHavenDataSet.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    command = "SELECT textu_tag, textu_path FROM TEXTUREHAVEN WHERE categ_tag LIKE '%s'" % categ_name

    d = cur.execute(command)

    for row in d:
        material_thum[row[0]] = pr.CatchDir + row[1]
    conn.close()

    i = 0
    for m in material_thum:
        material_name = m
        material_path = material_thum[m]

        material_icon = pcoll.load(material_name, material_path, "IMAGE")

        material_item.append((material_name, material_name, material_name, material_icon.icon_id, i))
        i += 1
    pcoll.categ_preview = material_item
    pcoll.categ_name = categ_name

    return pcoll.categ_preview


def selectNewTexture(self, context):
    wm = context.window_manager
    wm.th_isNewTexture = True

thumb_collection = {}

def register():
    from bpy.types import WindowManager
    from bpy.props import EnumProperty
    from bpy.props import BoolProperty
    from bpy.props import FloatProperty

    pcoll = bpy.utils.previews.new()
    pcoll.categ_name = ""
    pcoll.categ_preview = ()
    thumb_collection["category"] = pcoll

    WindowManager.th_categ = EnumProperty(
        items = get_category_item,
        name = "Category",
        update = selectNewTexture,
    )

    WindowManager.th_matrial = EnumProperty(
        items = get_material_item,
        name = "Material",
        update = selectNewTexture,
    )

    # 分辨率

    WindowManager.th_isDownloading = BoolProperty(
        default = False,
    )

    WindowManager.th_DownloadProcess= FloatProperty(
        default = 0,
        min = 0.0,
        max = 100.0,
        soft_min = 0.0,
        soft_max = 100.0,
        name = "Downloading..."
    )

    WindowManager.th_isNewTexture = BoolProperty(
        default = True,
    )

    bpy.utils.register_class(TH_Preference)
    bpy.utils.register_class(updateDatabaseOperator)
    bpy.utils.register_class(TH_OT_MaterialOperator)
    bpy.utils.register_class(TH_OT_MaterialBuildOp)
    bpy.utils.register_class(TH_Panel)


def unregister():
    from bpy.types import WindowManager

    del WindowManager.th_categ
    del WindowManager.th_matrial

    for pcoll in thumb_collection.values():
        bpy.utils.previews.remove(pcoll)
    thumb_collection.clear()


    bpy.utils.unregister_class(TH_Preference)
    bpy.utils.unregister_class(updateDatabaseOperator)
    bpy.utils.unregister_class(TH_OT_MaterialOperator)
    bpy.utils.unregister_class(TH_OT_MaterialBuildOp)
    bpy.utils.unregister_class(TH_Panel)
