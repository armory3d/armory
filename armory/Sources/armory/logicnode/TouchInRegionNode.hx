package armory.logicnode;

import iron.math.Vec2;

class TouchInRegionNode extends LogicNode {

	public var property0: String;

	var lastInside: Null<Bool> = null;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var touch = iron.system.Input.getSurface();
		final center = new Vec2(inputs[0].get(), inputs[1].get());
		final size = new Vec2(inputs[2].get(), inputs[3].get());
		final angle: Float = inputs[4].get();
		final lastPoint = new Vec2(touch.lastX, touch.lastY);
		final point = new Vec2(touch.x, touch.y);

		switch (property0) {
			case "rectangle":
				if(lastInside == null) {
					lastInside = detectPointInRectangle(center, size, angle, lastPoint);
				}
				final inside = detectPointInRectangle(center, size, angle, point);

				//On Enter
				if(!lastInside && inside) runOutput(0);

				//On Exit
				if(lastInside && !inside) runOutput(1);

				lastInside = inside;

			case "ellipse":
				if(lastInside == null) {
					lastInside = detectPointInEllipse(center, size, angle, lastPoint);
				}
				final inside = detectPointInEllipse(center, size, angle, point);

				//On Enter
				if(!lastInside && inside) runOutput(0);

				//On Exit
				if(lastInside && !inside) runOutput(1);

				lastInside = inside;
		}
	}

	override function get(from: Int): Dynamic {
		var touch = iron.system.Input.getSurface();

		if(from == 2) {
			final center = new Vec2(inputs[0].get(), inputs[1].get());
			final size = new Vec2(inputs[2].get(), inputs[3].get());
			final angle = inputs[4].get();
			final point = new Vec2(touch.x, touch.y);

			switch (property0) {
				case "rectangle":
					return detectPointInRectangle(center, size, angle, point);
				case "ellipse":
					return detectPointInEllipse(center, size, angle, point);
			}
		}

		return null;
	}

	//Rotate touch location and calculate relative location to shape center
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

	function detectPointInEllipse(center: Vec2, size: Vec2, angle: Float, point: Vec2): Bool {
		final relativePoint = alignRotatePoint(point, center, -angle);
		final magX = (relativePoint.x * relativePoint.x) / (0.25 * size.x * size.x);
		final magY = (relativePoint.y * relativePoint.y) / (0.25 * size.y * size.y);
		if(magX + magY <= 1.0){
			return true;
		}

		return false;
	}
}

