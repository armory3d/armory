package cycles.trait;

import lue.trait.Trait;
import lue.Eg;
import lue.resource.Resource;
import lue.node.ModelNode;

class Animation extends Trait {

    var model:ModelNode;

    //public function new(startTrack:String, names:Array<String>, starts:Array<Int>, ends:Array<Int>) {
    public function new() {
        super();

        var modelRes = Resource.getModel("Scene", "lamp_body");
        var materialRes = Resource.getMaterial("Scene", "bob_head");

        model = Eg.addModelNode(modelRes, [materialRes]);
        Eg.setupAnimation(model, "idle", ["idle"], [0], [140]);
        trace("AAAAA");
        requestUpdate(update);
    }

    function update() {
        Eg.setAnimationParams(model, lue.sys.Time.delta);
    }
}
