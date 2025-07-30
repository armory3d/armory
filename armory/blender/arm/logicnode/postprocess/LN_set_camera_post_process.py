from arm.logicnode.arm_nodes import *

class CameraSetNode(ArmLogicTreeNode):
    """Set the post-processing effects of a camera."""
    bl_idname = 'LNCameraSetNode'
    bl_label = 'Set Camera Post Process'
    arm_version = 6

    def remove_extra_inputs(self, context):
        while len(self.inputs) > 1:
                self.inputs.remove(self.inputs[-1])
        if self.property0 == 'F-stop':
            self.add_input('ArmFloatSocket', 'F-stop', default_value=1.0)#0
        if self.property0 == 'Shutter Time':
            self.add_input('ArmFloatSocket', 'Shutter Time', default_value=2.8333)#1
        if self.property0 == 'ISO':           
            self.add_input('ArmFloatSocket', 'ISO', default_value=100.0)#2
        if self.property0 == 'Exposure Compensation':           
            self.add_input('ArmFloatSocket', 'Exposure Compensation', default_value=0.0)#3
        if self.property0 == 'Fisheye Distortion':           
            self.add_input('ArmFloatSocket', 'Fisheye Distortion', default_value=0.01)#4
        if self.property0 == 'Auto Focus':
            self.add_input('ArmBoolSocket', 'Auto Focus', default_value=True)#5
        if self.property0 == 'DoF Distance':
            self.add_input('ArmFloatSocket', 'DoF Distance', default_value=10.0)#6
        if self.property0 == 'DoF Length': 
            self.add_input('ArmFloatSocket', 'DoF Length', default_value=160.0)#7
        if self.property0 == 'DoF F-Stop':    
            self.add_input('ArmFloatSocket', 'DoF F-Stop', default_value=128.0)#8
        if self.property0 == 'Tonemapping':   
            self.add_input('ArmIntSocket', 'Tonemapping', default_value=0)#9
        if self.property0 == 'Distort':    
            self.add_input('ArmFloatSocket', 'Distort', default_value=2.0)#10
        if self.property0 == 'Film Grain':    
            self.add_input('ArmFloatSocket', 'Film Grain', default_value=2.0)#11
        if self.property0 == 'Sharpen':    
            self.add_input('ArmFloatSocket', 'Sharpen', default_value=0.25)#12
        if self.property0 == 'Vignette':    
            self.add_input('ArmFloatSocket', 'Vignette', default_value=0.7)#13
        if self.property0 == 'Exposure':    
            self.add_input('ArmFloatSocket', 'Exposure', default_value=1)#14


    property0: HaxeEnumProperty(
    'property0',
    items = [('F-stop', 'F-stop', 'F-stop'),
             ('Shutter Time', 'Shutter Time', 'Shutter Time'),
             ('ISO', 'ISO', 'ISO'),
             ('Exposure Compensation', 'Exposure Compensation', 'Exposure Compensation'),
             ('Fisheye Distortion', 'Fisheye Distortion', 'Fisheye Distortion'),
             ('Auto Focus', 'Auto Focus', 'Auto Focus'),
             ('DoF Distance', 'DoF Distance', 'DoF Distance'),
             ('DoF Length', 'DoF Length', 'DoF Length'),
             ('DoF F-Stop', 'DoF F-Stop', 'DoF F-Stop'),
             ('Tonemapping', 'Tonemapping', 'Tonemapping'),
             ('Distort', 'Distort', 'Distort'),
             ('Film Grain', 'Film Grain', 'Film Grain'),
             ('Sharpen', 'Sharpen', 'Sharpen'),
             ('Vignette', 'Vignette', 'Vignette'),
             ('Exposure', 'Exposure', 'Exposure')],
    name='', default='F-stop', update=remove_extra_inputs)


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'F-stop', default_value=1.0)#0

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        if self.property0 == 'Tonemapping':
            layout.label(text="0: Filmic")
            layout.label(text="1: Filmic2")
            layout.label(text="2: Reinhard")
            layout.label(text="3: Uncharted2")
            layout.label(text="5: None")

        layout.prop(self, 'property0')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in range(0, 4):
            raise LookupError()
        elif self.arm_version == 1:
            newnode = node_tree.nodes.new('LNCameraSetNode')

            for link in self.inputs[10].links:
                node_tree.links.new(newnode.inputs[10], link.to_socket)

            return newnode
        else:
            return NodeReplacement.Identity(self)