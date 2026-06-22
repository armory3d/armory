package arm2d.tools;

// Kha
import kha.math.Vector2;

// Zui
import zui.Zui;
import armory.ui.Canvas.TCanvas;
import armory.ui.Canvas.TElement;

class Math {

    public static inline function toDegrees(radians:Float):Float { return radians * 57.29578; }
	public static inline function toRadians(degrees:Float):Float { return degrees * 0.0174532924; }

	/**
	 * Calculates if the mouse is in the given hitbox rectangle.
	 *
	 * @param ui The Zui object of which this function should take the mouse position
	 * @param x The x position of the hitbox
	 * @param y The y position of the hitbox
	 * @param w The width of the hitbox
	 * @param h The height of the hitbox
	 * @param rotation The rotation of the hitbox in radians, default = 0.0
	 * @param center (Optional) The [x, y] coordinates of the center of rotation. If not given or null, use the center of the rectangle given by (x, y, w, h)
	 * @return Bool
	 */
    public static function hitbox(ui: Zui, x: Float, y: Float, w: Float, h: Float, rotation: Float = 0.0, ?center: Array<Float>):Bool {
		if (center != null && center.length != 2) {
			throw "arm2d.tools.Math.hitbox(): 'center' argument must consist of two values!";
		}

		if (center == null) center = [x + w / 2, y + h / 2];

		var rotatedInput:Vector2 = rotatePoint(ui.inputX, ui.inputY, center[0], center[1], -rotation);
		return rotatedInput.x > x && rotatedInput.x < x + w && rotatedInput.y > y && rotatedInput.y < y + h;
	}

    public static function absx(canvas:TCanvas, e:TElement):Float {
		if (e == null) return 0;
		return e.x + absx(canvas, CanvasTools.elemById(canvas, e.parent));
	}

	public static function absy(canvas:TCanvas, e:TElement):Float {
		if (e == null) return 0;
		return e.y + absy(canvas, CanvasTools.elemById(canvas, e.parent));
	}

	public static function roundPrecision(v:Float, ?precision=0):Float {
		v *= std.Math.pow(10, precision);

		v = Std.int(v) * 1.0;
		v /= std.Math.pow(10, precision);

		return v;
	}

	public static function rotatePoint(pointX: Float, pointY: Float, centerX: Float, centerY: Float, angle:Float): Vector2 {
		pointX -= centerX;
		pointY -= centerY;

		var x = pointX * std.Math.cos(angle) - pointY * std.Math.sin(angle);
		var y = pointX * std.Math.sin(angle) + pointY * std.Math.cos(angle);

		return new Vector2(centerX + x, centerY + y);
	}

	public static function calculateTransformDelta(ui:Zui, gSP:Bool, gUR:Bool, gS:Int, value:Float, ?offset=0.0):Float {
		var precisionMode = ui.isKeyDown && ui.key == Main.prefs.keyMap.slowMovement;
		var enabled = gSP != (ui.isKeyDown && (ui.key == Main.prefs.keyMap.gridInvert));
		var useOffset = gUR != (ui.isKeyDown && (ui.key == Main.prefs.keyMap.gridInvertRelative));

		if (!enabled) return precisionMode ? value / 2 : value;

		// Round the delta value to steps of gridSize
		value = std.Math.round(value / gS) * gS;

		if (precisionMode) value /= 2;

		// Apply an offset
		if (useOffset && offset != 0) {
			offset = offset % gS;

			// Round to nearest grid position instead of rounding off
			if (offset > gS / 2) {
				offset = -(gS - offset);
			}

			value -= offset;
		}
		return value;
	}

}