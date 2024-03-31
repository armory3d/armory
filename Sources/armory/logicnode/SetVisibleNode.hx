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
		var recursive: Bool = inputs[4].get();

		if (object == null) return;

		switch (property0) {
			case "object":
				object.visible = visible;
			case "mesh":
				object.visibleMesh = visible;
			case "shadow":
				object.visibleShadow = visible;
			}
			
		if (children) setVisisbleRecursive(property0, object, visible, recursive);

		runOutput(0);
	}

	function setVisisbleRecursive(property: String, object: Object, visible: Bool, recursive: Bool) {
		var objectChildren: Array<Object> = object.children;
		switch (property) {
			case "object":
				for (child in objectChildren) {
				child.visible = visible;
				if (recursive) setVisisbleRecursive(property, child, visible, recursive);
				}
	
			case "mesh":
				for (child in objectChildren) {
				child.visibleMesh = visible;
				if (recursive) setVisisbleRecursive(property, child, visible, recursive);
				}
	
			case "shadow":
				for (child in objectChildren) {
				child.visibleShadow = visible;
				if (recursive) setVisisbleRecursive(property, child, visible, recursive);
				}
			}
	}
}
