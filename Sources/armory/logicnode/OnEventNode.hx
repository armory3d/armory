package armory.logicnode;

import armory.system.Event;

class OnEventNode extends LogicNode {

	var _property0:String;
	public var property0(get, set):String;
	var listener:TEvent = null;

	public function new(tree:LogicTree) {
		super(tree);
		tree.notifyOnRemove(onRemove);
	}

	function get_property0():String {
		return _property0;
	}

	function set_property0(s:String):String {
		listener = Event.add(s, onEvent, tree.object.uid);
		return _property0 = s;
	}

	function onEvent() {
		runOutput(0);
	}

	function onRemove() {
		if (listener != null) Event.removeListener(listener);
	}
}
