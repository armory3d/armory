package armory.logicnode;

import armory.system.Event;

class OnEventNode extends LogicNode {

	public var property1: String; // Init, Update, Custom
	var value: String;
	var listener: TEvent = null;
	var oldValue: String;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnInit(init_main);
		tree.notifyOnRemove(onRemove);
	}

	function init_main() {
		switch (property1) {
		case "init": tree.notifyOnInit(init);
		case "update": tree.notifyOnUpdate(update);
		}
	}

	function init() {
		value = inputs[0].get();
		listener = Event.add(value, onEvent, tree.object.uid);
	}

	function update() {
		value = inputs[0].get();
		if (value != oldValue) {
			onRemove();
			listener = Event.add(value, onEvent, tree.object.uid);
			oldValue = value;
		}
	}

	override function run(from: Int) {
		value = inputs[1].get();
		if (value != oldValue) {
			onRemove();
			listener = Event.add(value, onEvent, tree.object.uid);
			oldValue = value;
		}
	}

	function onEvent() {
		runOutput(0);
	}

	function onRemove() {
		if (listener != null) Event.removeListener(listener);
	}
}
