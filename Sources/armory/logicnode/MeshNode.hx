package armory.logicnode;

import armory.data.MeshData;

class MeshNode extends LogicNode {

	public var property0:String;
	public var value:MeshData = null;

	public function new(tree:LogicTree) {
		super(tree);

		armory.Scene.active.notifyOnInit(function() {
			get(0);
		});
	}

	override function get(from:Int):Dynamic { 
		armory.data.Data.getMesh("mesh_" + property0, property0, null, function(mesh:MeshData) {
			value = mesh;
		});

		return value;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
