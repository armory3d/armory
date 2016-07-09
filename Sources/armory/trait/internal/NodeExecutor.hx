package armory.trait.internal;

import iron.Trait;

class NodeExecutor extends Trait {

    var baseNode:armory.node.Node;
    var nodeUpdates:Array<Void->Void> = [];

    public function new() {
        super();

        notifyOnUpdate(update);
    }

    public function start(baseNode:armory.node.Node) {
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
