package armory.trait.physics.bullet;

import bullet.Bt.Vector3;

import kha.FastFloat;
import kha.System;

import iron.math.Vec4;

#if arm_ui
import armory.ui.Canvas;
#end

using StringTools;

class DebugDrawHelper {
	static inline var contactPointSizePx = 4;
	static inline var contactPointNormalColor = 0xffffffff;
	static inline var contactPointDrawLifetime = true;

	final physicsWorld: PhysicsWorld;
	final lines: Array<LineData> = [];
	final texts: Array<TextData> = [];
	var font: kha.Font = null;

	var debugMode: PhysicsWorld.DebugDrawMode = NoDebug;

	public function new(physicsWorld: PhysicsWorld) {
		this.physicsWorld = physicsWorld;

		#if arm_ui
		iron.data.Data.getFont(Canvas.defaultFontName, function(defaultFont: kha.Font) {
			font = defaultFont;
		});
		#end

		iron.App.notifyOnRender2D(onRender);
	}

	public function drawLine(from: bullet.Bt.Vector3, to: bullet.Bt.Vector3, color: bullet.Bt.Vector3) {
		#if js
			// https://github.com/InfiniteLee/ammo-debug-drawer/pull/1/files
			// https://emscripten.org/docs/porting/connecting_cpp_and_javascript/WebIDL-Binder.html#pointers-and-comparisons
			from = js.Syntax.code("Ammo.wrapPointer({0}, Ammo.btVector3)", from);
			to = js.Syntax.code("Ammo.wrapPointer({0}, Ammo.btVector3)", to);
			color = js.Syntax.code("Ammo.wrapPointer({0}, Ammo.btVector3)", color);
		#end

		final fromScreenSpace = worldToScreenFast(new Vec4(from.x(), from.y(), from.z(), 1.0));
		final toScreenSpace = worldToScreenFast(new Vec4(to.x(), to.y(), to.z(), 1.0));

		// For now don't draw lines if any point is outside of clip space z,
		// investigate how to clamp lines to clip space borders
		if (fromScreenSpace.w == 1 && toScreenSpace.w == 1) {
			lines.push({
				fromX: fromScreenSpace.x,
				fromY: fromScreenSpace.y,
				toX: toScreenSpace.x,
				toY: toScreenSpace.y,
				color: kha.Color.fromFloats(color.x(), color.y(), color.z(), 1.0)
			});
		}
	}

	public function drawContactPoint(pointOnB: Vector3, normalOnB: Vector3, distance: kha.FastFloat, lifeTime: Int, color: Vector3) {
		#if js
			pointOnB = js.Syntax.code("Ammo.wrapPointer({0}, Ammo.btVector3)", pointOnB);
			normalOnB = js.Syntax.code("Ammo.wrapPointer({0}, Ammo.btVector3)", normalOnB);
			color = js.Syntax.code("Ammo.wrapPointer({0}, Ammo.btVector3)", color);
		#end

		final contactPointScreenSpace = worldToScreenFast(new Vec4(pointOnB.x(), pointOnB.y(), pointOnB.z(), 1.0));
		final toScreenSpace = worldToScreenFast(new Vec4(pointOnB.x() + normalOnB.x() * distance, pointOnB.y() + normalOnB.y() * distance, pointOnB.z() + normalOnB.z() * distance, 1.0));

		if (contactPointScreenSpace.w == 1) {
			final color = kha.Color.fromFloats(color.x(), color.y(), color.z(), 1.0);

			lines.push({
				fromX: contactPointScreenSpace.x - contactPointSizePx,
				fromY: contactPointScreenSpace.y - contactPointSizePx,
				toX: contactPointScreenSpace.x + contactPointSizePx,
				toY: contactPointScreenSpace.y + contactPointSizePx,
				color: color
			});

			lines.push({
				fromX: contactPointScreenSpace.x - contactPointSizePx,
				fromY: contactPointScreenSpace.y + contactPointSizePx,
				toX: contactPointScreenSpace.x + contactPointSizePx,
				toY: contactPointScreenSpace.y - contactPointSizePx,
				color: color
			});

			if (toScreenSpace.w == 1) {
				lines.push({
					fromX: contactPointScreenSpace.x,
					fromY: contactPointScreenSpace.y,
					toX: toScreenSpace.x,
					toY: toScreenSpace.y,
					color: contactPointNormalColor
				});
			}

			if (contactPointDrawLifetime && font != null) {
				texts.push({
					x: contactPointScreenSpace.x,
					y: contactPointScreenSpace.y,
					color: color,
					text: Std.string(lifeTime), // lifeTime: number of frames the contact point existed
				});
			}
		}
	}

	public function reportErrorWarning(warningString: bullet.Bt.BulletString) {
		trace(warningString.toHaxeString().trim());
	}

	public function draw3dText(location: Vector3, textString: bullet.Bt.BulletString) {
		if (font == null) {
			return;
		}

		#if js
			location = js.Syntax.code("Ammo.wrapPointer({0}, Ammo.btVector3)", location);
		#end

		final locationScreenSpace = worldToScreenFast(new Vec4(location.x(), location.y(), location.z(), 1.0));

		texts.push({
			x: locationScreenSpace.x,
			y: locationScreenSpace.y,
			color: kha.Color.fromFloats(0.0, 0.0, 0.0, 1.0),
			text: textString.toHaxeString()
		});
	}

	public function setDebugMode(debugMode: PhysicsWorld.DebugDrawMode) {
		this.debugMode = debugMode;
	}

	public function getDebugMode(): PhysicsWorld.DebugDrawMode {
		#if js
			return debugMode;
		#elseif hl
			return physicsWorld.getDebugDrawMode();
		#else
			return NoDebug;
		#end
	}

	function onRender(g: kha.graphics2.Graphics) {
		if (getDebugMode() == NoDebug) {
			return;
		}

		// It might be a bit unusual to call this method in a render callback
		// instead of the update loop (after all it doesn't draw anything but
		// will cause Bullet to call the btIDebugDraw callbacks), but this way
		// we can ensure that--within a frame--the function will not be called
		// before some user-specific physics update, which would result in a
		// one-frame drawing delay... Ideally we would ensure that debugDrawWorld()
		// is called when all other (late) update callbacks are already executed...
		physicsWorld.world.debugDrawWorld();

		g.opacity = 1.0;

		for (line in lines) {
			g.color = line.color;
			g.drawLine(line.fromX, line.fromY, line.toX, line.toY, 1.0);
		}
		lines.resize(0);

		if (font != null) {
			g.font = font;
			g.fontSize = 12;
			for (text in texts) {
				g.color = text.color;
				g.drawString(text.text, text.x, text.y);
			}
			texts.resize(0);
		}
	}

	/**
		Transform a world coordinate vector into screen space and store the
		result in the input vector's x and y coordinates. The w coordinate is
		set to 0 if the input vector is outside the active camera's far and near
		planes, and 1 otherwise.
	**/
	inline function worldToScreenFast(loc: Vec4): Vec4 {
		final cam = iron.Scene.active.camera;
		loc.w = 1.0;
		loc.applyproj(cam.VP);

		if (loc.z < -1 || loc.z > 1) {
			loc.w = 0.0;
		}
		else {
			loc.x = (loc.x + 1) * 0.5 * System.windowWidth();
			loc.y = (1 - loc.y) * 0.5 * System.windowHeight();
			loc.w = 1.0;
		}

		return loc;
	}
}

@:structInit
class LineData {
	public var fromX: FastFloat;
	public var fromY: FastFloat;
	public var toX: FastFloat;
	public var toY: FastFloat;
	public var color: kha.Color;
}

@:structInit
class TextData {
	public var x: FastFloat;
	public var y: FastFloat;
	public var color: kha.Color;
	public var text: String;
}
