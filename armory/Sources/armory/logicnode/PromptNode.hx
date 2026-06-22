package armory.logicnode;

class PromptNode extends LogicNode {

	var input: String = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if kha_html5
		input = js.Browser.window.prompt(inputs[1].get(), inputs[2].get());
		
		runOutput(0);
		#end

	}

	override function get(from: Int): Dynamic {
		return input;
	}
}
