import os
import bpy
import sqlite3
import threading
import zipfile  

import urllib.request 
from urllib.request import urlretrieve

from .THPreference import get_preferences

global process
process = 0.0

def getProcess():
    return process

# 下载进度
def downloadProcess(a, b, c):
    per=100.0*a*b/c
    if per>100:
        per = 100
    global process
    process = per
    print('%.2f%%' % per)

# 下载并解压纹理
def DownloadTexture(url, path, context):
    wm = context.window_manager
    if not os.path.exists(path):
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0')]
        urllib.request.install_opener(opener)

        print("Starting download %s" % url)

        wm.th_isDownloading =True

        urlretrieve(url, filename = path, reporthook=downloadProcess)

        wm.th_isDownloading =False
        wm.th_isNewTexture = False

        print("Download finished. Result saving at: %s" % path)
    else:
        wm.th_isNewTexture = False
        print("Texture is already downloaded!")

    # 解压文件
    z = zipfile.ZipFile(path, "r")

    cur_dir = "/".join(path.split("/")[:-1])

    for f in z.namelist():
        f_path = cur_dir + "/" + f
        if not os.path.exists(f_path):
            print("Extracting %s" % f)
            z.extract(f, cur_dir)
    z.close()

# 多线程下载材质文件
def DownloadMatrial(material_name, path, db_path, context):
    # 查询数据库，找到material_name对应的下载链接
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    command = "SELECT textu_1k_url, textu_2k_url, textu_4k_url, textu_8k_url from TEXTUREHAVEN WHERE textu_tag LIKE '%s'" % material_name

    d = list(cur.execute(command))
    url_1k = d[0][0]
    url_2k = d[0][1]
    url_4k = d[0][2]
    url_8k = d[0][3]

    conn.close()

    download_t = threading.Thread(target=DownloadTexture, args = [url_1k, path, context])

    download_t.start()

class TH_OT_MaterialOperator(bpy.types.Operator):
    bl_idname = "th.download"
    bl_label = "Download Texture"

    # 下载、解压并构建材质
    def execute(self, context):
        wm = context.window_manager
        pr = get_preferences(context)

        material_name = wm.th_matrial
        material_categ = wm.th_categ
        material_path = pr.CatchDir + "Textures/" + material_categ + "/" + material_name + ".zip"

        db_path = pr.CatchDir + "/Thumbails/TextureHavenDataSet.db"

        if not os.path.exists(pr.CatchDir + "Textures/"):
            os.mkdir(pr.CatchDir + "Textures/")
        if not os.path.exists(pr.CatchDir + "Textures/" + material_categ + "/"):
            os.mkdir(pr.CatchDir + "Textures/" + material_categ + "/")

        DownloadMatrial(material_name, material_path, db_path, context)

        return {"FINISHED"}

class TH_OT_MaterialBuildOp(bpy.types.Operator):
    bl_idname = "th.build"
    bl_label= "Build Material"

    def execute(self, context):
        wm = context.window_manager
        pr = get_preferences(context)

        material_name = wm.th_matrial
        material_categ = wm.th_categ
        material_path = pr.CatchDir + "Textures/" + material_categ + "/" + material_name + ".zip"

        AO_path = ""
        bump_path = ""
        diff_path = ""
        Disp_path = ""
        nor_path = ""
        rough_path = ""
        spec_path = ""

        AO_texture_name = ""
        bump_texture_name = ""
        diff_texture_name = ""
        disp_texture_name = ""
        norm_texture_name = ""
        roug_texture_name = ""
        spec_texture_name = ""

        # 通过zip文件查询各路径
        z = zipfile.ZipFile(material_path, "r")
        for f in z.namelist():
            if "_AO_" in f:
                AO_path = pr.CatchDir + "Textures/" + material_categ + "/" + f
                AO_texture_name = f
                bpy.ops.image.open(filepath = AO_path, directory = pr.CatchDir + "Textures/" + material_categ + "/", files = [{"name": AO_texture_name}, {"name": AO_texture_name}], relative_path = True, show_multiview = False)
            elif "_bump_" in f:
                bump_path = pr.CatchDir + "Textures/" + material_categ + "/" + f
                bump_texture_name = f
                bpy.ops.image.open(filepath = bump_path, directory = pr.CatchDir + "Textures/" + material_categ + "/", files = [{"name": bump_texture_name}, {"name": bump_texture_name}], relative_path = True, show_multiview = False)
            elif "_diff_" in f:
                diff_path = pr.CatchDir + "Textures/" + material_categ + "/" + f
                diff_texture_name = f
                bpy.ops.image.open(filepath = diff_path, directory = pr.CatchDir + "Textures/" + material_categ + "/", files = [{"name": diff_texture_name}, {"name": diff_texture_name}], relative_path = True, show_multiview = False)
            elif "_Disp_" in f:
                Disp_path = pr.CatchDir + "Textures/" + material_categ + "/" + f
                disp_texture_name = f
                bpy.ops.image.open(filepath = Disp_path, directory = pr.CatchDir + "Textures/" + material_categ + "/", files = [{"name": disp_texture_name}, {"name": disp_texture_name}], relative_path = True, show_multiview = False)
            elif "_Nor_" in f or "_nor_" in f:
                nor_path = pr.CatchDir + "Textures/" + material_categ + "/" + f
                norm_texture_name = f
                bpy.ops.image.open(filepath = nor_path, directory = pr.CatchDir + "Textures/" + material_categ + "/", files = [{"name": norm_texture_name}, {"name": norm_texture_name}], relative_path = True, show_multiview = False)
            elif "_rough_" in f:
                rough_path = pr.CatchDir + "Textures/" + material_categ + "/" + f
                roug_texture_name = f
                bpy.ops.image.open(filepath = rough_path, directory = pr.CatchDir + "Textures/" + material_categ + "/", files = [{"name": roug_texture_name}, {"name": roug_texture_name}], relative_path = True, show_multiview = False)
            elif "_spec_" in f:
                spec_path = pr.CatchDir + "Textures/" + material_categ + "/" + f
                spec_texture_name = f
                bpy.ops.image.open(filepath = spec_path, directory = pr.CatchDir + "Textures/" + material_categ + "/", files = [{"name": spec_texture_name}, {"name": spec_texture_name}], relative_path = True, show_multiview = False)
        z.close()

        # 创建新材质
        material = bpy.data.materials.new(name = material_name)

        material.use_nodes = True
        # 删除原有的shader

        priciple_node = material.node_tree.nodes["Principled BSDF"]
        output_node = material.node_tree.nodes["Material Output"]

        AO_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        AO_texture_node.location = (-1070, 400)
        AO_texture_node.name = AO_texture_name

        diff_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        diff_texture_node.location = (-669, 387)
        diff_texture_node.name = diff_texture_name

        disp_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        disp_texture_node.location = (-1070, -135)
        disp_texture_node.name = disp_texture_name

        norm_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        norm_texture_node.location = (-679, -388)
        norm_texture_node.name = norm_texture_name

        rogh_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        rogh_texture_node.location = (-681, -130)
        rogh_texture_node.name = roug_texture_name

        spec_texture_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        spec_texture_node.location = (-673, 135)
        spec_texture_node.name = spec_texture_name

        ValToRGB_node = material.node_tree.nodes.new("ShaderNodeValToRGB")
        ValToRGB_node.location = (-672, 627)

        MixRGB_node = material.node_tree.nodes.new("ShaderNodeMixRGB")
        MixRGB_node.location = (-343, 559)

        NormapMap_node = material.node_tree.nodes.new("ShaderNodeNormalMap")
        NormapMap_node.location = (-327, -262)

        if AO_texture_name:
            AO_texture_node.image = bpy.data.images[AO_texture_name]
        
        if diff_texture_name:
            diff_texture_node.image = bpy.data.images[diff_texture_name]

        if disp_texture_name:
            disp_texture_node.image = bpy.data.images[disp_texture_name]
        
        if norm_texture_name:
            norm_texture_node.image = bpy.data.images[norm_texture_name]
        
        if roug_texture_name:
            rogh_texture_node.image = bpy.data.images[roug_texture_name]

        if spec_texture_name:
            spec_texture_node.image = bpy.data.images[spec_texture_name]

        material.node_tree.links.new(AO_texture_node.outputs[0], ValToRGB_node.inputs[0])
        material.node_tree.links.new(ValToRGB_node.outputs[0], MixRGB_node.inputs[1])
        material.node_tree.links.new(diff_texture_node.outputs[0], MixRGB_node.inputs[2])
        material.node_tree.links.new(MixRGB_node.outputs[0], priciple_node.inputs[0])
        material.node_tree.links.new(spec_texture_node.outputs[0], priciple_node.inputs[5])
        material.node_tree.links.new(rogh_texture_node.outputs[0], priciple_node.inputs[7])
        material.node_tree.links.new(norm_texture_node.outputs[0], NormapMap_node.inputs[1])
        material.node_tree.links.new(NormapMap_node.outputs[0], priciple_node.inputs[19])

        bpy.context.object.material_slots[0].material = material

        return {"FINISHED"}