package armory.node;

import armory.trait.NodeExecutor;

class TimeNode extends FloatNode {

	public static inline var _startTime = 0; // Float
	public static inline var _stopTime = 1; // Float
	public static inline var _scale = 2; // Float
	public static inline var _enabled = 3; // Bool
	public static inline var _loop = 4; // Bool
	public static inline var _reflect = 5; // Bool

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);

		f = inputs[_startTime].f;

		executor.registerUpdate(update);
	}

	function update() {
		
		if (inputs[_enabled].b) {
			f += iron.sys.Time.delta * inputs[_scale].f;

			// Time out
			if (inputs[_stopTime].f > 0) {
				if (inputs[_scale].f > 0 && f >= inputs[_stopTime].f ||
					inputs[_scale].f < 0 && f <= inputs[_startTime].f) {
					
					// Loop
					if (inputs[_loop].b) {

						// Reflect
						if (inputs[_reflect].b) {
							if (inputs[_scale].f > 0) {
								f = inputs[_stopTime].f;
							}
							else {
								f = inputs[_startTime].f;
							}

							inputs[_scale].f *= -1;
						}
						// Reset
						else {
							f = inputs[_startTime].f;
						}
					}
					// Stop
					else {
						f = inputs[_stopTime].f;
						inputs[_enabled].b = false;
					}
				}
			}

			inputChanged();
		}
	}

	public static function create(startTime:Float, stopTime:Float, enabled:Bool, loop:Bool, reflect:Bool) {
		var n = new TimeNode();
		n.inputs.push(FloatNode.create(startTime));
		n.inputs.push(FloatNode.create(stopTime));
		n.inputs.push(BoolNode.create(enabled));
		n.inputs.push(BoolNode.create(loop));
		n.inputs.push(BoolNode.create(reflect));
		return n;
	}
}
