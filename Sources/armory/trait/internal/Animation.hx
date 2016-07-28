package armory.trait.internal;

import iron.Trait;
import iron.Eg;
import iron.resource.Resource;
import iron.node.ModelNode;

class Animation extends Trait {

    var model:ModelNode;

    var startTrack:String;
    var names:Array<String>;
    var starts:Array<Int>;
    var ends:Array<Int>;

    public function new(startTrack:String, names:Array<String>, starts:Array<Int>, ends:Array<Int>) {
        super();
        
        this.startTrack = startTrack;
        this.names = names;
        this.starts = starts;
        this.ends = ends;

        notifyOnAdd(add);
        notifyOnUpdate(update);
    }

    function add() {
        model = cast(node, ModelNode);
        Eg.setupAnimation(model, startTrack, names, starts, ends);
    }

    function update() {
        Eg.setAnimationParams(model, iron.sys.Time.delta);
    }

    public function play(trackName:String, loop = true, speed = 1.0, onTrackComplete:Void->Void = null) {
        model.animation.player.play(trackName, loop, speed, onTrackComplete);
    }

    public function pause() {
        model.animation.player.pause();
    }
}
