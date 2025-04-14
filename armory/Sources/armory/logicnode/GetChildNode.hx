package armory.logicnode;

import iron.object.Object;

class GetChildNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		var childName: String = inputs[1].get();

		if (object == null || childName == null) return null;

		switch (property0) {
		case "By Name":
			return object.getChild(childName);
		case "Contains":
			return contains(object, childName);
		case "Starts With":
			return startsWith(object, childName);
		case "Ends With":
			return endsWith(object, childName);
		}

		return null;
	}

	function contains(o: Object, name: String): Object {
		for (c in o.children) {
			if (c.name.indexOf(name) >= 0) return c;
		}
		return null;
	}

	function startsWith(o: Object, name: String): Object {
		for (c in o.children) {
			if (StringTools.startsWith(c.name, name)) return c;
		}
		return null;
	}

	function endsWith(o: Object, name: String): Object {
		for (c in o.children) {
			if (StringTools.endsWith(c.name, name)) return c;
		}
		return null;
	}
}
