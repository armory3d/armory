package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;
import iron.system.Tween;

class TweenTransformNode extends LogicNode {

	public var property0:String;

	public var anim: TAnim;
	public var fromValue:Mat4 = Mat4.identity();
	public var toValue:Mat4 = Mat4.identity();
	public var duration:Float = 1.0;
	public var floc: Vec4 = new Vec4();
	public var frot: Quat = new Quat();
	public var fscl: Vec4 = new Vec4();
	public var tloc: Vec4 = new Vec4();
	public var trot: Quat = new Quat();
	public var tscl: Vec4 = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

		if(from == 0){

			if(anim != null){
				Tween.stop(anim);
			}

			fromValue.setFrom(inputs[2].get());
			toValue.setFrom(inputs[3].get());
			
			fromValue.decompose(floc, frot, fscl);
			toValue.decompose(tloc, trot, tscl);		
			
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
				props: { floc: tloc, frot: trot, fscl: tscl, },
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
		if(from == 3) return fromValue.compose(floc, frot, fscl);
		return null;
	}

	function update() {
		runOutput(1);	
	}

	function done() {
		runOutput(2);		
	}	
}