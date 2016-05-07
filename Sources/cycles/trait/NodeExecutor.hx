package cycles.trait;

import lue.Trait;

class NodeExecutor extends Trait {

    var baseNode:cycles.node.Node;
    var nodeUpdates:Array<Void->Void> = [];

    public function new() {
        super();

        requestUpdate(update);
    }

    public function start(baseNode:cycles.node.Node) {
        this.baseNode = baseNode;
        baseNode.start(this);
    }

    function update() {
        for (f in nodeUpdates) {
            f();
        }
    }

    public function registerUpdate(f:Void->Void) {
        nodeUpdates.push(f);
    }
}
