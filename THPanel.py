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
from bpy.props import EnumProperty

from .THPreference import get_preferences

from .THOperator import getProcess

class TH_Panel(bpy.types.Panel):
    bl_label = "Texture Haven"
    bl_idname = "OBJECT_PT_texturehaven"
    bl_category = "TextureHaven"
    bl_space_type = 'PROPERTIES'
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        
        row = layout.row()
        row.prop(wm, "th_categ", text = "Category")

        row = layout.row()
        row.template_icon_view(wm, "th_matrial")

        row = layout.row()
        row.operator("th.download")

        wm.th_DownloadProcess = getProcess()
        
        if wm.th_isDownloading:
            row = layout.row()
            row.prop(wm, "th_DownloadProcess", slider = True)

        if not wm.th_isNewTexture:
            row = layout.row()
            row.operator("th.build")