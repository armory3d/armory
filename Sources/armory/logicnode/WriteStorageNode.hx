package armory.logicnode;

class WriteStorageNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var key: String = inputs[1].get();
		var value: Dynamic = inputs[2].get();

		var data = iron.system.Storage.data;
		if (data == null) return;

		Reflect.setField(data, key, value);
		iron.system.Storage.save();

		runOutput(0);
	}
}
