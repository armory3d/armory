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
		var children: Bool = inputs[3].get();

		if (object == null) return;

		var objectChildren: Array<Object> = object.children;

		switch (property0) {
		case "Object":
			object.visible = visible;
			if (children == true) for (child in objectChildren) {
        	child.visible = visible;
        	}

		case "Mesh":
			object.visibleMesh = visible;
			if (children == true) for (child in objectChildren) {
			child.visibleMesh = visible;
			}

		case "Shadow":
			object.visibleShadow = visible;
			if (children == true) for (child in objectChildren) {
			child.visibleShadow = visible;
			}
		}

		runOutput(0);
	}
}
