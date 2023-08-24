package armory.logicnode;

import iron.data.MeshData;

class MeshNode extends LogicNode {

	public var property0: String;
	public var value: MeshData = null;

	public function new(tree: LogicTree) {
		super(tree);

		iron.Scene.active.notifyOnInit(function() {
			get(0);
		});
	}

	override function get(from: Int): Dynamic {
		iron.data.Data.getMesh("mesh_" + property0, property0, function(mesh: MeshData) {
			value = mesh;
		});

		return value;
	}

	override function set(value: Dynamic) {
		this.value = value;
	}
}
