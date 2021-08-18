import bpy, blf, bgl, os, gpu
from gpu_extras.batch import batch_for_shader

class ViewportDraw:

    def __init__(self, context, text):

        bakefile = "TLM_Overlay.png"
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        bakefile_path = os.path.abspath(os.path.join(scriptDir, '..', '..', 'assets/' + bakefile))

        image_name = "TLM_Overlay.png"

        bpy.ops.image.open(filepath=bakefile_path)

        print("Self path: " + bakefile_path)

        image = bpy.data.images[image_name]

        x = 15
        y = 15
        w = 400
        h = 200

        self.shader = gpu.shader.from_builtin('2D_IMAGE')
        self.batch = batch_for_shader(
            self.shader, 'TRI_FAN',
            {
                "pos": ((x, y), (x+w, y), (x+w, y+h), (x, y+h)),
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
        )

        if image.gl_load():
            raise Exception()

        self.text = text
        self.image = image
        #self.handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_text_callback, (context,), 'WINDOW', 'POST_PIXEL')
        self.handle2 = bpy.types.SpaceView3D.draw_handler_add(self.draw_image_callback, (context,), 'WINDOW', 'POST_PIXEL')

    def draw_text_callback(self, context):

        font_id = 0
        blf.position(font_id, 15, 15, 0)
        blf.size(font_id, 20, 72)
        blf.draw(font_id, "%s" % (self.text))

    def draw_image_callback(self, context):
        
        if self.image:
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glActiveTexture(bgl.GL_TEXTURE0)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.image.bindcode)

            self.shader.bind()
            self.shader.uniform_int("image", 0)
            self.batch.draw(self.shader)
            bgl.glDisable(bgl.GL_BLEND)

    def update_text(self, text):

        self.text = text

    def remove_handle(self):
        #bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
        bpy.types.SpaceView3D.draw_handler_remove(self.handle2, 'WINDOW')