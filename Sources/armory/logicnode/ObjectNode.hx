package armory.logicnode;

import iron.object.Object;

class ObjectNode extends LogicNode {

	public var objectName:String;
	public var value:Object;

	public function new(tree:LogicTree, objectName:String = "") {
		this.objectName = objectName;
		super(tree);
	}

	override function get(from:Int):Dynamic {
		if (inputs.length > 0) return inputs[0].get();
		value = objectName != "" ? iron.Scene.active.getChild(objectName) : tree.object;
		return value;
	}

	override function set(value:Dynamic) {
		if (inputs.length > 0) inputs[0].set(value);
		else {
			objectName = value.name;
			this.value = value;
		}
	}
}
