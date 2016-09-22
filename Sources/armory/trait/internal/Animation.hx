package armory.trait.internal;

import iron.Trait;

class Animation extends Trait {

    var startTrack:String;
    var names:Array<String>;
    var starts:Array<Int>;
    var ends:Array<Int>;
    var speeds:Array<Float>;
    var loops:Array<Bool>;
    var reflects:Array<Bool>;
    static var maxBones:Int;

    public function new(startTrack:String, names:Array<String>, starts:Array<Int>, ends:Array<Int>, speeds:Array<Float>, loops:Array<Bool>, reflects:Array<Bool>, _maxBones:Int) {
        super();
        
        this.startTrack = startTrack;
        this.names = names;
        this.starts = starts;
        this.ends = ends;
        this.speeds = speeds;
        this.loops = loops;
        this.reflects = reflects;
        maxBones = _maxBones;

        notifyOnAdd(add);
        notifyOnUpdate(update);
    }

    function add() {
        object.setupAnimation(startTrack, names, starts, ends, speeds, loops, reflects, maxBones);
    }

    function update() {
        object.setAnimationParams(iron.system.Time.delta);
    }

    public function play(trackName:String, onTrackComplete:Void->Void = null) {
        object.animation.player.play(trackName, onTrackComplete);
    }

    public function pause() {
        object.animation.player.pause();
    }
}
