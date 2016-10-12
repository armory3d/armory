package armory.trait.internal;

import iron.Trait;

@:keep
class NodeExecutor extends Trait {

    var baseNode:armory.logicnode.Node;
    var nodeInits:Array<Void->Void> = [];
    var nodeUpdates:Array<Void->Void> = [];

    public function new() {
        super();

        notifyOnUpdate(update);
    }

    public function start(baseNode:armory.logicnode.Node) {
        this.baseNode = baseNode;
        baseNode.start(this);
    }

    function update() {
        if (nodeInits.length > 0) {
            for (f in nodeInits) { if (nodeInits.length == 0) break; f(); f = null; }
            nodeInits.splice(0, nodeInits.length);     
        }
        for (f in nodeUpdates) f();
    }

    public function notifyOnNodeInit(f:Void->Void) {
        nodeInits.push(f);
    }

    public function notifyOnNodeUpdate(f:Void->Void) {
        nodeUpdates.push(f);
    }
}
