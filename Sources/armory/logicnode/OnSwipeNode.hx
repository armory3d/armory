package armory.logicnode;
import iron.math.Vec4;
import iron.math.Vec2;

class OnSwipeNode extends LogicNode {

	var point_start = new Vec2();
	var point_end = new Vec2();
	var direction = new Vec2();
	var length = 0;
	var swipe = false;
	public var time_delta = 0.0;
	public var minimal_length = 0;
	var timer = 0.0;

	// New (constructor)
	public function new(tree: LogicTree) {
		super(tree);		
		// Set update
		tree.notifyOnUpdate(update);
	}

	// Update
	function update() {
		var surface = iron.system.Input.getSurface();
		// Check swipe end
		if (swipe == true) {
			timer += iron.system.Time.delta;
			if ((surface.released() == true) || (timer >= time_delta)) {
				swipe = false;
				point_end.x = surface.x;
				point_end.y = point_start.y; 
				point_start.y = surface.y;
				// Calc result direction
				direction.x = point_end.x - point_start.x;
				direction.y = point_end.y - point_start.y;
				// Calc length				
				length = Math.round(Math.sqrt(direction.x * direction.x + direction.y * direction.y));
				// Check minimal length
				if (length >= minimal_length) {			
					// Execute next action linked to this node
					runOutput(0);
				}
			}
		}		
		// Check swipe start
		else if ((surface.started() == true)) {
			// In parameter
			if (inputs.length > 1)
			{
				time_delta = inputs[0].get();
				minimal_length = inputs[1].get();
			}
			point_start.x = surface.x;
			point_start.y = surface.y;
			swipe = true;
			timer = 0;
			direction.x = 0;
			direction.y = 0;
			length = 0;
		}
	}

	// Calc angle (0-360)
	function calc_angle(vector: Vec2): Int {
		var ax = vector.x;
		var ay = vector.y;
		var bx = vector.x;
		var by = 0.0;
		var angle = Math.atan2(ax * by - bx * ay, ax * bx + ay * by) * 180 / Math.PI;
		// Determine the quarter
		if ((ax > 0) && (ay > 0)) {
			// I
			angle = -angle;
		} else if ((ax < 0) && (ay > 0)) {
			// II
			angle = 180.0 - angle;
		} else if ((ax < 0) && (ay < 0)) {
			// III
			angle = 180.0 - angle;
		} else if ((ax > 0) && (ay < 0)) {
			// IV
			angle = 360.0 - angle;
		}
		return Math.round(angle);
	}

	// State determination according to 4 directions
	function getStateFor4Direction(from: Int, dir: Vec2): Dynamic {
		var angle = calc_angle(dir);
		switch (from) {
			// Up
			case 1: {
				// 45 - 135
				if ((angle >= 45) && (angle < 135)) return true;
				return false;
			}
			// Down
			case 2:
				// 225 - 315
				if ((angle >= 225) && (angle < 315)) return true;
				return false;
			// Left
			case 3:
				// 135 - 225
				if ((angle >= 135) && (angle < 225)) return true;
				return false;
			// Right
			case 4:
				// 315 - 45				
				if ((angle >= 315) || (angle < 45)) return true;
				return false;
		} 
		return null;
	}

	// State determination according to 8 directions
	function getStateFor8Direction(from: Int, dir: Vec2): Dynamic {
		var angle = calc_angle(dir);
		switch (from) {
			// UP
			case 1: {
				// 68 - 112
				if ((angle >= 68) && (angle < 112)) return true;
				return false;
			}
			// DOWN
			case 2: {
				// 248 - 292
				if ((angle >= 248) && (angle < 292)) return true;
				return false;
			}
			// LEFT
			case 3: {
				// 158 - 202
				if ((angle >= 158) && (angle < 202)) return true;
				return false;
			}
			// RIGHT
			case 4: {
				// 338 - 22			
				if ((angle >= 338) || (angle < 22)) return true;
				return false;
			}
			// UP-LEFT
			case 5: {
				// 112 - 158				
				if ((angle >= 112) && (angle < 158)) return true;
				return false;
			}
			// UP-RIGHT
			case 6: {
				// 22 - 68				
				if ((angle >= 22) && (angle < 68)) return true;
				return false;
			}
			// DOWN-LEFT
			case 7: {
				// 202 - 248				
				if ((angle >= 202) && (angle < 248)) return true;
				return false;
			}
			// DOWN-RIGHT
			case 8: {				
				// 292 - 338				
				if ((angle >= 292) && (angle < 338)) return true;
				return false;
			}
		} 
		return null;
	}

	// State determination
	function getState(from: Int, dir: Vec2): Dynamic {
		// Check count outputs parameter
		if (outputs.length == 8) {
			return getStateFor4Direction(from, dir);
		} else if (outputs.length == 12) {
			return getStateFor8Direction(from, dir);
		}
		return null;
	}

	// Get - out
	override function get(from: Int): Dynamic {
		switch (from) {
			// Out value - Direction (Vector)
			case 1: { 
				direction = direction.normalize();
				return new Vec4(direction.x, direction.y, 0, 0);
			}
			// Out value - Length (px)
			case 2: return length;
			// Out value - Angle (0-360)
			case 3: return calc_angle(direction);
		} 
		// Direction State
		if (from > 3) return getState(from - 3, direction);
		return null;
	}
}