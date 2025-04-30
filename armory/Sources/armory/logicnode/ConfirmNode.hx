package armory.logicnode;

class ConfirmNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		
		#if kha_html5
		var answer: Bool = js.Browser.window.confirm(inputs[1].get());
		if(answer)
			return runOutput(0);
		else
			return runOutput(1);
		#end

	}
}
