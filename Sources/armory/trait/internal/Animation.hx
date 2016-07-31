package armory.trait.internal;

import iron.Trait;
import iron.Eg;
import iron.resource.Resource;

class Animation extends Trait {

    var startTrack:String;
    var names:Array<String>;
    var starts:Array<Int>;
    var ends:Array<Int>;
    var speeds:Array<Float>;
    var loops:Array<Bool>;
    var reflects:Array<Bool>;

    public function new(startTrack:String, names:Array<String>, starts:Array<Int>, ends:Array<Int>, speeds:Array<Float>, loops:Array<Bool>, reflects:Array<Bool>) {
        super();
        
        this.startTrack = startTrack;
        this.names = names;
        this.starts = starts;
        this.ends = ends;
        this.speeds = speeds;
        this.loops = loops;
        this.reflects = reflects;

        notifyOnAdd(add);
        notifyOnUpdate(update);
    }

    function add() {
        Eg.setupAnimation(node, startTrack, names, starts, ends, speeds, loops, reflects);
    }

    function update() {
        Eg.setAnimationParams(node, iron.sys.Time.delta);
    }

    public function play(trackName:String, onTrackComplete:Void->Void = null) {
        node.animation.player.play(trackName, onTrackComplete);
    }

    public function pause() {
        node.animation.player.pause();
    }
}
