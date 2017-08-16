package armory.logicnode;

class WriteStorageNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var key:String = inputs[1].get();
		var value:Dynamic = inputs[2].get();

		var data = iron.system.Storage.data;
		Reflect.setField(data, key, value);
		iron.system.Storage.save();

		super.run();
	}
}
