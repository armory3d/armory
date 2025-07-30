package armory.logicnode;

class FunctionNode extends LogicNode {

    @:allow(armory.logicnode.LogicTree)
    var args: Array<Dynamic> = [];
    @:allow(armory.logicnode.LogicTree)
    var result: Dynamic;

    public function new(tree: LogicTree) {
        super(tree);
    }

    @:allow(armory.logicnode.LogicTree)
    override function run(from: Int) {
        runOutput(0);
    }

    override function get(from: Int): Dynamic {
        return this.args[from - 1];
    }
}
