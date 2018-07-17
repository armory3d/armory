package armory.logicnode;

class ExpressionNode extends LogicNode {

	public var property0:String;
	var result:Dynamic;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(node:LogicNode) {
		var values : Array<Dynamic> = [for (i in inputs.slice(2)) i.get()];
		#if arm_hscript
		var expr = inputs[1].get();
		var parser = new hscript.Parser();
		var ast = parser.parseString(expr);
		var interp = new hscript.Interp();
		for (i in 0...values)	interp.variables.set("v"+i,value[i]);
		result = interp.execute(ast);
		#end

		runOutputs(0);
	}

	override function get(from:Int):Dynamic {
		return result;
	}
}
