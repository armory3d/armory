package armory.logicnode;

class RegularExpressionNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var RegExp: EReg = new EReg(inputs[0].get(), inputs[1].get());
		var str: String = inputs[2].get();

		switch (property0) {
			case "Match":
				var mch: Bool = RegExp.match(str);
				
				if (from == 0) 
					return mch;

				var mched: Array<String> = [];
				
				if (mch){
					var lng: Int = inputs[0].get().split('(').length;
					for(i in 1...lng) mched.push(RegExp.matched(i));
				}
					
				return mched;

			case "Split":
				return RegExp.split(str);
			case "Replace":
				return RegExp.replace(str, inputs[3].get());

		}
	
		return null;

	}
}
