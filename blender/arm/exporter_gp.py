def export_grease_pencils(self):
    gpRef = self.scene.grease_pencil
    if gpRef == None or self.scene.arm_gp_export == False:
        return

    # ArmoryExporter.option_mesh_per_file # Currently always exports to separate file
    fp = self.get_greasepencils_file_path('greasepencil_' + gpRef.name, compressed=self.is_compress(gpRef))
    assets.add(fp)
    ext = ''
    if self.is_compress(gpRef):
        ext = '.zip'
    self.output['grease_pencil_ref'] = 'greasepencil_' + gpRef.name + ext + '/' + gpRef.name

    assets.add_shader_data(arm.utils.build_dir() + '/compiled/Shaders/grease_pencil/grease_pencil.arm')
    assets.add_shader(arm.utils.build_dir() + '/compiled/Shaders/grease_pencil/grease_pencil.frag.glsl')
    assets.add_shader(arm.utils.build_dir() + '/compiled/Shaders/grease_pencil/grease_pencil.vert.glsl')
    assets.add_shader(arm.utils.build_dir() + '/compiled/Shaders/grease_pencil/grease_pencil_shadows.frag.glsl')
    assets.add_shader(arm.utils.build_dir() + '/compiled/Shaders/grease_pencil/grease_pencil_shadows.vert.glsl')

    if gpRef.arm_cached == True and os.path.exists(fp):
        return

    gpo = self.post_export_grease_pencil(gpRef)
    gp_obj = {}
    gp_obj['grease_pencil_datas'] = [gpo]
    arm.utils.write_arm(fp, gp_obj)
    gpRef.arm_cached = True

def get_greasepencils_file_path(self, object_id, compressed=False):
    index = self.filepath.rfind('/')
    gp_fp = self.filepath[:(index + 1)] + 'greasepencils/'
    if not os.path.exists(gp_fp):
        os.makedirs(gp_fp)
    ext = '.zip' if compressed else '.arm'
    return gp_fp + object_id + ext

def post_export_grease_pencil(self, gp):
    o = {}
    o['name'] = gp.name
    o['layers'] = []
    for layer in gp.layers:
        o['layers'].append(self.export_grease_pencil_layer(layer))
    # o['palettes'] = []
    # for palette in gp.palettes:
        # o['palettes'].append(self.export_grease_pencil_palette(palette))
    o['shader'] = 'grease_pencil/grease_pencil'
    return o

def export_grease_pencil_layer(self, layer):
    lo = {}
    lo['name'] = layer.info
    lo['opacity'] = layer.opacity
    lo['frames'] = []
    for frame in layer.frames:
        if frame.frame_number > self.scene.frame_end:
            break
        # TODO: load GP frame data
        # self.scene.frame_set(frame.frame_number)
        lo['frames'].append(self.export_grease_pencil_frame(frame))
    return lo

def export_grease_pencil_frame(self, frame):
    va = []
    cola = []
    colfilla = []
    indices = []
    num_stroke_points = []
    index_offset = 0
    for stroke in frame.strokes:
        for point in stroke.points:
            va.append(point.co[0])
            va.append(point.co[1])
            va.append(point.co[2])
            # TODO: store index to color pallete only, this is extremely wasteful
            if stroke.color != None:
                cola.append(stroke.color.color[0])
                cola.append(stroke.color.color[1])
                cola.append(stroke.color.color[2])
                cola.append(stroke.color.alpha)
                colfilla.append(stroke.color.fill_color[0])
                colfilla.append(stroke.color.fill_color[1])
                colfilla.append(stroke.color.fill_color[2])
                colfilla.append(stroke.color.fill_alpha)
            else:
                cola.append(0.0)
                cola.append(0.0)
                cola.append(0.0)
                cola.append(0.0)
                colfilla.append(0.0)
                colfilla.append(0.0)
                colfilla.append(0.0)
                colfilla.append(0.0)
        for triangle in stroke.triangles:
            indices.append(triangle.v1 + index_offset)
            indices.append(triangle.v2 + index_offset)
            indices.append(triangle.v3 + index_offset)
        num_stroke_points.append(len(stroke.points))
        index_offset += len(stroke.points)
    fo = {}
    # TODO: merge into array of vertex arrays
    fo['vertex_array'] = {}
    fo['vertex_array']['attrib'] = 'pos'
    fo['vertex_array']['size'] = 3
    fo['vertex_array']['values'] = va
    fo['col_array'] = {}
    fo['col_array']['attrib'] = 'col'
    fo['col_array']['size'] = 4
    fo['col_array']['values'] = cola
    fo['colfill_array'] = {}
    fo['colfill_array']['attrib'] = 'colfill'
    fo['colfill_array']['size'] = 4
    fo['colfill_array']['values'] = colfilla
    fo['index_array'] = {}
    fo['index_array']['material'] = 0
    fo['index_array']['size'] = 3
    fo['index_array']['values'] = indices
    fo['num_stroke_points'] = num_stroke_points
    fo['frame_number'] = frame.frame_number
    return fo

def export_grease_pencil_palette(self, palette):
    po = {}
    po['name'] = palette.info
    po['colors'] = []
    for color in palette.colors:
        po['colors'].append(self.export_grease_pencil_palette_color(color))
    return po

def export_grease_pencil_palette_color(self, color):
    co = {}
    co['name'] = color.name
    co['color'] = [color.color[0], color.color[1], color.color[2]]
    co['alpha'] = color.alpha
    co['fill_color'] = [color.fill_color[0], color.fill_color[1], color.fill_color[2]]
    co['fill_alpha'] = color.fill_alpha
    return co
