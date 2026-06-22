package armory.logicnode;

class AlertNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		#if kha_html5
		js.Browser.window.alert(inputs[1].get());
		#end

		runOutput(0);
	}
}
