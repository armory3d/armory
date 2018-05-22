# Translating operators from/to Armory player
# from mathutils import Matrix
# import bpy
# import arm.utils
# import arm.make_state as state
# try:
#     import barmory
# except ImportError:
#     pass

# def parse_operator(text):
#     if text == None:
#         return
#     cmd = text.split('|')
#     # Reflect commands from Armory player in Blender
#     if cmd[0] == '__arm':
#         if cmd[1] == 'quit':
#             bpy.ops.arm.space_stop('EXEC_DEFAULT')
#             # Copy view matrix
#             if len(cmd) > 2 and bpy.data.worlds['Arm'].arm_play_camera == 'Viewport Shared':
#                 arstr = cmd[2][1:-1] # Remove []
#                 ar = arstr.split(',')
#                 mat = [float(i) for i in ar]
#                 set_view_mat(mat)

#         elif cmd[1] == 'setx':
#             bpy.context.scene.objects[cmd[2]].location.x = float(cmd[3])
#         elif cmd[1] == 'select':
#             if hasattr(bpy.context, 'object') and bpy.context.object != None:
#                 bpy.context.object.select = False
#             bpy.context.scene.objects[cmd[2]].select = True
#             bpy.context.scene.objects.active = bpy.context.scene.objects[cmd[2]]

# def send_operator(op):
#     # Try to translate operator directly to armory
#     if arm.utils.with_krom() and hasattr(bpy.context, 'object') and bpy.context.object != None:
#         objname = bpy.context.object.name
#         if op.name == 'Translate':
#             vec = bpy.context.object.location
#             js_source = 'var o = armory.Scene.active.getChild("' + objname + '"); o.transform.loc.set(' + str(vec[0]) + ', ' + str(vec[1]) + ', ' + str(vec[2]) + '); o.transform.dirty = true;'
#             barmory.call_js(js_source)
#             return True
#         elif op.name == 'Resize':
#             vec = bpy.context.object.scale
#             js_source = 'var o = armory.Scene.active.getChild("' + objname + '"); o.transform.scale.set(' + str(vec[0]) + ', ' + str(vec[1]) + ', ' + str(vec[2]) + '); o.transform.dirty = true;'
#             barmory.call_js(js_source)
#             return True
#         elif op.name == 'Rotate':
#             vec = bpy.context.object.rotation_euler.to_quaternion()
#             js_source = 'var o = armory.Scene.active.getChild("' + objname + '"); o.transform.rot.set(' + str(vec[1]) + ', ' + str(vec[2]) + ', ' + str(vec[3]) + ' ,' + str(vec[0]) + '); o.transform.dirty = true;'
#             barmory.call_js(js_source)
#             return True
#     return False

# def set_view_mat(mat):
#     if state.play_area == None:
#         return
#     for space in state.play_area.spaces:
#         if space.type == 'VIEW_3D':
#             m = Matrix()
#             m[0][0] = mat[0]
#             m[0][1] = mat[1]
#             m[0][2] = mat[2]
#             m[0][3] = mat[3]
#             m[1][0] = mat[4]
#             m[1][1] = mat[5]
#             m[1][2] = mat[6]
#             m[1][3] = mat[7]
#             m[2][0] = mat[8]
#             m[2][1] = mat[9]
#             m[2][2] = mat[10]
#             m[2][3] = mat[11]
#             m[3][0] = mat[12]
#             m[3][1] = mat[13]
#             m[3][2] = mat[14]
#             m[3][3] = mat[15]
#             space.region_3d.view_matrix = m
#             break
