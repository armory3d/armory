package armory.logicnode;

import iron.math.Vec4;
import iron.system.Tween;

class TweenVectorNode extends LogicNode {

	public var property0:String;

	public var anim: TAnim;
	public var fromValue:Vec4 = new Vec4();
	public var toValue:Vec4 = new Vec4();
	public var duration:Float = 1.0;

	public function new(tree:LogicTree) {
		super(tree);
		tree.notifyOnRemove(onRemove);
	}

	override function run(from:Int) {

		if(from == 0){

			if(anim != null){
				Tween.stop(anim);
			}

			fromValue.setFrom(inputs[2].get());
			toValue.setFrom(inputs[3].get());
			duration = inputs[4].get();
			var type:Dynamic = Linear;

			switch (property0) {
			case "Linear":
				type = Linear;
			case "SineIn":
				type = SineIn;
			case "SineOut":
				type = SineOut;			
			case "SineInOut":
				type = SineInOut;
			case "QuadIn":
				type = QuadIn;
			case "QuadOut":
				type = QuadOut;
			case "QuadInOut":
				type = QuadInOut;
			case "CubicIn":
				type = CubicIn;
			case "CubicOut":
				type = CubicOut;
			case "CubicInOut":
				type = CubicInOut;
			case "QuartIn":
				type = QuartIn;
			case "QuartOut":
				type = QuartOut;
			case "QuartInOut":
				type = QuartInOut;
			case "QuintIn":
				type = QuintIn;
			case "QuintOut":
				type = QuintOut;
			case "QuintInOut":
				type = QuintInOut;
			case "ExpoIn":
				type = ExpoIn;
			case "ExpoOut":
				type = ExpoOut;
			case "ExpoInOut":
				type = ExpoInOut;
			case "CircIn":
				type = CircIn;
			case "CircOut":
				type = CircOut;
			case "CircInOut":
				type = CircInOut;
			case "BackIn":
				type = BackIn;
			case "BackOut":
				type = BackOut;
			case "BackInOut":
				type = BackInOut;
			}		

			anim = Tween.to({
				target: this,
				props: { fromValue: toValue },
				duration: duration,
				ease: type,
				tick: update,
				done: done
			});
		}
		else{
			if(anim != null){
				Tween.stop(anim);
			}
			
		}

		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		if(from == 3) return fromValue;
		return null;
	}

	function update() {
		runOutput(1);	
	}

	function done() {
		runOutput(2);		
	}

	function onRemove() {
		if(anim != null){
			Tween.stop(anim);
		}
	}
}