package armory.logicnode;

import iron.data.MaterialData;

class MaterialNode extends LogicNode {

	public var property0: String;
	public var value: MaterialData = null;

	public function new(tree: LogicTree) {
		super(tree);

		iron.Scene.active.notifyOnInit(function() {
			get(0);
		});
	}

	override function get(from: Int): Dynamic {
		if (property0 != null) {
			iron.data.Data.getMaterial(iron.Scene.active.raw.name, property0, function(mat: MaterialData) {
				value = mat;
			});
		}

		return value;
	}

	override function set(value: Dynamic) {
		this.value = value;
	}
}
