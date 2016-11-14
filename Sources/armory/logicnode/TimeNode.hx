package armory.logicnode;

import armory.trait.internal.NodeExecutor;

class TimeNode extends FloatNode {

	public static inline var _startTime = 0; // Float
	public static inline var _stopTime = 1; // Float
	public static inline var _enabled = 2; // Bool
	public static inline var _loop = 3; // Bool
	public static inline var _reflect = 4; // Bool

	var scale = 1.0;

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);

		val = inputs[_startTime].val;

		executor.notifyOnNodeUpdate(update);
	}

	function update() {
		
		if (inputs[_enabled].val) {
			val += iron.system.Time.delta * scale;

			// Time out
			if (inputs[_stopTime].f > 0) {
				if (scale > 0 && val >= inputs[_stopTime].val ||
					scale < 0 && val <= inputs[_startTime].val) {
					
					// Loop
					if (inputs[_loop].b) {

						// Reflect
						if (inputs[_reflect].val) {
							if (scale > 0) {
								f = inputs[_stopTime].val;
							}
							else {
								f = inputs[_startTime].val;
							}

							scale *= -1;
						}
						// Reset
						else {
							val = inputs[_startTime].val;
						}
					}
					// Stop
					else {
						f = inputs[_stopTime].val;
						inputs[_enabled].val = false;
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
