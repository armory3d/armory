package armory.logicnode;

class MathNode extends LogicNode {

	public var property0: String; // Operation
	public var property1: Bool; // Clamp

	public function new(tree: LogicTree) {
		super(tree);
	}
	
	public static function round(number:Float, ?precision=2): Float{
		precision = Math.round(Math.abs(precision));
		number *= Math.pow(10, precision);
		return Math.round(number) / Math.pow(10, precision);
	}

	public function fract(a: Float): Float {
		return a - Math.floor(a);
	}

	public function pingpong(a: Float, b: Float): Float {
		if (b == 0.0) {
			return 0.0;
		} else {
			return Math.abs(fract((a - b) / (b * 2.0)) * b * 2.0 - b);
		}
	}  

	override function get(from: Int): Dynamic {
		var r = 0.0;
		switch (property0) {
			case "Sine":
				r = Math.sin(inputs[0].get());
			case "Cosine":
				r = Math.cos(inputs[0].get());
			case "Abs":
				r = Math.abs(inputs[0].get());
			case "Tangent":
				r = Math.tan(inputs[0].get());
			case "Arcsine":
				r = Math.asin(inputs[0].get());
			case "Arccosine":
				r = Math.acos(inputs[0].get());
			case "Arctangent":
				r = Math.atan(inputs[0].get());
			case "Logarithm":
				r = Math.log(inputs[0].get());
			case "Round":
				r = round(inputs[0].get(), inputs[1].get());
			case "Floor":
				r = Math.floor(inputs[0].get());
			case "Ceil":
				r = Math.ceil(inputs[0].get());
			case "Fract":
				var v = inputs[0].get();
				r = v - Std.int(v);
			case "Square Root":
				r = Math.sqrt(inputs[0].get());
			case "Exp":
				r = Math.exp(inputs[0].get());
			case "Max":
				r = Math.max(inputs[0].get(), inputs[1].get());
			case "Min":
				r = Math.min(inputs[0].get(), inputs[1].get());
			case "Power":
				r = Math.pow(inputs[0].get(), inputs[1].get());
			case "Less Than":
				r = inputs[0].get() < inputs[1].get() ? 1.0 : 0.0;
			case "Greater Than":
				r = inputs[0].get() > inputs[1].get() ? 1.0 : 0.0;
			case "Modulo":
				r = inputs[0].get() % inputs[1].get();
			case "Arctan2":
				r = Math.atan2(inputs[0].get(), inputs[1].get());
			case "Add":
				for (inp in inputs) r += inp.get();
			case "Multiply":
				r = inputs[0].get();
				var i = 1;
				while (i < inputs.length) {
					r *= inputs[i].get();
					i++;
				}
			case "Subtract":
				r = inputs[0].get();
				var i = 1;
				while (i < inputs.length) {
					r -= inputs[i].get();
					i++;
				}
			case "Divide":
				r = inputs[0].get();
				var i = 1;
				while (i < inputs.length) {
					r /= inputs[i].get();
					i++;
				}
			case "Ping-Pong":
				r = pingpong(inputs[0].get(), inputs[1].get());
			}
		// Clamp
		if (property1) r = r < 0.0 ? 0.0 : (r > 1.0 ? 1.0 : r);

		return r;
	}
}
