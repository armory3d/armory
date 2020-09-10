package armory.logicnode;

import iron.object.Object;

class SetVisibleNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var visible: Bool = inputs[2].get();

		if (object == null) return;

		switch (property0) {
		case "Object":
			object.visible = visible;
		case "Mesh":
			object.visibleMesh = visible;
		case "Shadow":
			object.visibleShadow = visible;
		}

		runOutput(0);
	}
}
