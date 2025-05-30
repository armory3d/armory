package armory.logicnode;

class GetFPSNode extends LogicNode {

    public function new(tree: LogicTree) {
        super(tree);
    }

    override function get(from: Int): Dynamic {
        if (from == 0) {
            var fps = Math.round(1 / iron.system.Time.delta);
            if ((fps == Math.POSITIVE_INFINITY) || (fps == Math.NEGATIVE_INFINITY) || (Math.isNaN(fps))) {
                return 0;
            }
            return fps;
        }
        return null;
    }
}
