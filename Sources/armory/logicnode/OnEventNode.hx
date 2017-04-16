package armory.logicnode;

class OnEventNode extends LogicNode {

	var _property0:String;
	public var property0(get, set):String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	function get_property0():String {
		return _property0;
	}

	function set_property0(s:String):String {
		armory.system.Event.add(s, onEvent, tree.object.uid);
		return _property0 = s;
	}

	function onEvent() {
		run();
	}
}
