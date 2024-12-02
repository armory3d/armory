from arm.logicnode.arm_nodes import *

class GetObjectGeomNode(ArmLogicTreeNode):
    """Returns the vertex geometry info of the given object and the vertex groups info.
    
    @input Object: object geometry to retrieve.

    @output Vertices Positions: an array with the vertices positions.
    @output Vertices Normals: an array with vertices normals directions.
    @output Vertices Indices: an array with vertices indices.
    @output Vertices Material Indices: an array with material indices per vertex.
    @output Vertices Vertices Face Indices: an array with face index per vertex.
    @output Vertex Groups Maps: maps with vertex group names and vertices positions.
    @output Vertex Groups Names: an array with the names of the vertex gruops.

    """

    bl_idname = 'LNGetObjectGeomNode'
    bl_label = 'Get Object Geometry Node'
    arm_section = 'relations'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmNodeSocketArray', 'Vertices Positions')
        self.add_output('ArmNodeSocketArray', 'Vertices Normals')
        self.add_output('ArmNodeSocketArray', 'Vertices Indices')
        self.add_output('ArmNodeSocketArray', 'Vertices Material Indices')
        self.add_output('ArmNodeSocketArray', 'Vertices Face Indices')
        self.add_output('ArmDynamicSocket', 'Vertex Groups Maps')
        self.add_output('ArmNodeSocketArray', 'Vertex Groups Names')