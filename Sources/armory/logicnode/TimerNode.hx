package armory.logicnode;

class TimerNode extends LogicNode {

	var duration = 0.0;
	var initialDuration = 0.0;
	var repeat = 0;
	var pause = false;
	public var running:Bool = false;
	public var secondsPassed:Int = 0;
	public var secondsLeft:Int = 0;
	public var normalized:Float = 0.0;

	public function new(tree:LogicTree) {
		super(tree);
	}

	function update() {
		if (pause == false) {
			super.run();
			if (repeat > 0) {
				this.running = true;
				if (this.running == true) {
					duration -= iron.system.Time.delta;
					this.secondsPassed = Std.int(initialDuration - duration);
					this.secondsLeft = Std.int(duration+1);
					this.normalized = Math.min(Math.max(0.0, 1 - (duration / initialDuration)), 1.0);
					
					if (duration < 0.0) {
						repeat -= 1;
						duration = initialDuration;
						this.running = false;
					}
				}
			}
			else {
				this.running = false;
				tree.removeUpdate(update);
			}
		}
	}
	
	override function run() {
		duration = inputs[1].get();
		initialDuration = inputs[1].get();
		repeat = inputs[2].get();
		pause = inputs[3].get();
		
		this.running = true;

		if (pause == false) {
			tree.notifyOnUpdate(update);
		}
	}

	override function get(from:Int):Dynamic {
		if (from == 1) return this.running;
		else if (from == 2) return this.secondsPassed;
		else if (from == 3) return this.secondsLeft;
		else return this.normalized;
	}

}
