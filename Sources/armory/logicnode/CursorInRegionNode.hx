package armory.logicnode;

import iron.math.Vec2;

class CursorInRegionNode extends LogicNode {

	public var property0: String;

	var lastInside: Null<Bool> = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	function update() {
		var mouse = iron.system.Input.getMouse();
		var b = false;

		switch (property0) {
			case "rectangle":
				runOutput(0);
			case "ellipse":
				runOutput(0);
		}
	}

	override function get(from: Int): Dynamic {
		var mouse = iron.system.Input.getMouse();

		if(from == 2) {
			var center = new Vec2(inputs[0].get(), inputs[1].get());
			var size = new Vec2(inputs[2].get(), inputs[3].get());
			var angle = inputs[4].get();
			var point = new Vec2(mouse.x, mouse.y);

			return detectPointInRectangle(center, size, angle, point);
		}

		return null;
	}

	inline function alignRotatePoint(point: Vec2, center: Vec2, angle: Float): Vec2 {
		var relativePoint = point.clone();
		relativePoint.sub(center);

		final sin = Math.sin(angle);
		final cos = Math.cos(angle);

		final xnew = relativePoint.x * cos - relativePoint.y * sin;
		final ynew = relativePoint.x * sin + relativePoint.y * cos;

		relativePoint.x = xnew;
		relativePoint.y = ynew;

		return relativePoint;
	}

	function detectPointInRectangle(center: Vec2, size: Vec2, angle: Float, point: Vec2): Bool {
		final relativePoint = alignRotatePoint(point, center, -angle);
		final magX = Math.abs(relativePoint.x);
		final magY = Math.abs(relativePoint.y);
		if(magX <= size.x/2 && magY <= size.y/2){
			return true;
		}

		return false;
	}
}

