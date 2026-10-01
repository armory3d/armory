package armory.object;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;
import iron.object.Transform;

class TransformExtension {

	public static function overlap(t1: Transform, t2: Transform): Bool {
		return t1.worldx() + t1.dim.x / 2 > t2.worldx() - t2.dim.x / 2 && t1.worldx() - t1.dim.x / 2 < t2.worldx() + t2.dim.x / 2 &&
			   t1.worldy() + t1.dim.y / 2 > t2.worldy() - t2.dim.y / 2 && t1.worldy() - t1.dim.y / 2 < t2.worldy() + t2.dim.y / 2 &&
			   t1.worldz() + t1.dim.z / 2 > t2.worldz() - t2.dim.z / 2 && t1.worldz() - t1.dim.z / 2 < t2.worldz() + t2.dim.z / 2;
	
	/**
	 * OBB-aware overlap check using SAT (Separating Axis Theorem).
	 * Accounts for rotation and scale of both transforms.
	 * Minimal, conservative approximation: checks axis alignment
	 * between the two objects' world-space basis vectors.
	 */
	public static function overlap_obb(t1: Transform, t2: Transform): Bool {
		// Ensure matrices are up to date
		t1.update();
		t2.update();

		// Half-dimensions in world space (already include scale via computeDim)
		var h1x = t1.dim.x / 2.0;
		var h1y = t1.dim.y / 2.0;
		var h1z = t1.dim.z / 2.0;
		var h2x = t2.dim.x / 2.0;
		var h2y = t2.dim.y / 2.0;
		var h2z = t2.dim.z / 2.0;

		// World positions
		var p1x = t1.worldx(); var p1y = t1.worldy(); var p1z = t1.worldz();
		var p2x = t2.worldx(); var p2y = t2.worldy(); var p2z = t2.worldz();

		// World-space basis vectors (right=local X, up=local Z in Iron, look=local Y)
		var r1 = t1.right();
		var u1 = t1.up();
		var l1 = t1.look();
		var r2 = t2.right();
		var u2 = t2.up();
		var l2 = t2.look();

		// Vector between centers
		var dx = p2x - p1x;
		var dy = p2y - p1y;
		var dz = p2z - p1z;

		// Helper: project half-extent onto an axis
		inline function proj1(ax: iron.math.Vec4): Float {
			return h1x * Math.Abs(ax.dot(r1)) + h1y * Math.Abs(ax.dot(u1)) + h1z * Math.Abs(ax.dot(l1));
		}
		inline function proj2(ax: iron.math.Vec4): Float {
			return h2x * Math.Abs(ax.dot(r2)) + h2y * Math.Abs(ax.dot(u2)) + h2z * Math.Abs(ax.dot(l2));
		}

		// Test 9 separating axes: 3 from each box
		var rad = dx * r1.x + dy * r1.y + dz * r1.z;
		if (Math.Abs(rad) > proj1(r1) + proj2(r1)) return false;

		rad = dx * u1.x + dy * u1.y + dz * u1.z;
		if (Math.Abs(rad) > proj1(u1) + proj2(u1)) return false;

		rad = dx * l1.x + dy * l1.y + dz * l1.z;
		if (Math.Abs(rad) > proj1(l1) + proj2(l1)) return false;

		rad = dx * r2.x + dy * r2.y + dz * r2.z;
		if (Math.Abs(rad) > proj1(r2) + proj2(r2)) return false;

		rad = dx * u2.x + dy * u2.y + dz * u2.z;
		if (Math.Abs(rad) > proj1(u2) + proj2(u2)) return false;

		rad = dx * l2.x + dy * l2.y + dz * l2.z;
		if (Math.Abs(rad) > proj1(l2) + proj2(l2)) return false;

		// Cross product axes
		var cr = iron.math.Vec4.crossvecs(r1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		return true;
	}
}

	/**
	 * Returns the world (global) position.
	 * @return Vec4
	 */
	public static inline function getWorldPosition(t: Transform): Vec4 {
		return new Vec4(t.worldx(), t.worldy(), t.worldz(), 1.0);
	
	/**
	 * OBB-aware overlap check using SAT (Separating Axis Theorem).
	 * Accounts for rotation and scale of both transforms.
	 * Minimal, conservative approximation: checks axis alignment
	 * between the two objects' world-space basis vectors.
	 */
	public static function overlap_obb(t1: Transform, t2: Transform): Bool {
		// Ensure matrices are up to date
		t1.update();
		t2.update();

		// Half-dimensions in world space (already include scale via computeDim)
		var h1x = t1.dim.x / 2.0;
		var h1y = t1.dim.y / 2.0;
		var h1z = t1.dim.z / 2.0;
		var h2x = t2.dim.x / 2.0;
		var h2y = t2.dim.y / 2.0;
		var h2z = t2.dim.z / 2.0;

		// World positions
		var p1x = t1.worldx(); var p1y = t1.worldy(); var p1z = t1.worldz();
		var p2x = t2.worldx(); var p2y = t2.worldy(); var p2z = t2.worldz();

		// World-space basis vectors (right=local X, up=local Z in Iron, look=local Y)
		var r1 = t1.right();
		var u1 = t1.up();
		var l1 = t1.look();
		var r2 = t2.right();
		var u2 = t2.up();
		var l2 = t2.look();

		// Vector between centers
		var dx = p2x - p1x;
		var dy = p2y - p1y;
		var dz = p2z - p1z;

		// Helper: project half-extent onto an axis
		inline function proj1(ax: iron.math.Vec4): Float {
			return h1x * Math.Abs(ax.dot(r1)) + h1y * Math.Abs(ax.dot(u1)) + h1z * Math.Abs(ax.dot(l1));
		}
		inline function proj2(ax: iron.math.Vec4): Float {
			return h2x * Math.Abs(ax.dot(r2)) + h2y * Math.Abs(ax.dot(u2)) + h2z * Math.Abs(ax.dot(l2));
		}

		// Test 9 separating axes: 3 from each box
		var rad = dx * r1.x + dy * r1.y + dz * r1.z;
		if (Math.Abs(rad) > proj1(r1) + proj2(r1)) return false;

		rad = dx * u1.x + dy * u1.y + dz * u1.z;
		if (Math.Abs(rad) > proj1(u1) + proj2(u1)) return false;

		rad = dx * l1.x + dy * l1.y + dz * l1.z;
		if (Math.Abs(rad) > proj1(l1) + proj2(l1)) return false;

		rad = dx * r2.x + dy * r2.y + dz * r2.z;
		if (Math.Abs(rad) > proj1(r2) + proj2(r2)) return false;

		rad = dx * u2.x + dy * u2.y + dz * u2.z;
		if (Math.Abs(rad) > proj1(u2) + proj2(u2)) return false;

		rad = dx * l2.x + dy * l2.y + dz * l2.z;
		if (Math.Abs(rad) > proj1(l2) + proj2(l2)) return false;

		// Cross product axes
		var cr = iron.math.Vec4.crossvecs(r1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		return true;
	}
}

	/**
	 * Returns the given local vector in world coordinates
	 * @param localVec
	 * @return Vec4
	 */
	public static inline function getWorldVecFromLocal(t: Transform, localVec: Vec4): Vec4 {
		return localVec.clone().applymat4(t.worldUnpack);
	
	/**
	 * OBB-aware overlap check using SAT (Separating Axis Theorem).
	 * Accounts for rotation and scale of both transforms.
	 * Minimal, conservative approximation: checks axis alignment
	 * between the two objects' world-space basis vectors.
	 */
	public static function overlap_obb(t1: Transform, t2: Transform): Bool {
		// Ensure matrices are up to date
		t1.update();
		t2.update();

		// Half-dimensions in world space (already include scale via computeDim)
		var h1x = t1.dim.x / 2.0;
		var h1y = t1.dim.y / 2.0;
		var h1z = t1.dim.z / 2.0;
		var h2x = t2.dim.x / 2.0;
		var h2y = t2.dim.y / 2.0;
		var h2z = t2.dim.z / 2.0;

		// World positions
		var p1x = t1.worldx(); var p1y = t1.worldy(); var p1z = t1.worldz();
		var p2x = t2.worldx(); var p2y = t2.worldy(); var p2z = t2.worldz();

		// World-space basis vectors (right=local X, up=local Z in Iron, look=local Y)
		var r1 = t1.right();
		var u1 = t1.up();
		var l1 = t1.look();
		var r2 = t2.right();
		var u2 = t2.up();
		var l2 = t2.look();

		// Vector between centers
		var dx = p2x - p1x;
		var dy = p2y - p1y;
		var dz = p2z - p1z;

		// Helper: project half-extent onto an axis
		inline function proj1(ax: iron.math.Vec4): Float {
			return h1x * Math.Abs(ax.dot(r1)) + h1y * Math.Abs(ax.dot(u1)) + h1z * Math.Abs(ax.dot(l1));
		}
		inline function proj2(ax: iron.math.Vec4): Float {
			return h2x * Math.Abs(ax.dot(r2)) + h2y * Math.Abs(ax.dot(u2)) + h2z * Math.Abs(ax.dot(l2));
		}

		// Test 9 separating axes: 3 from each box
		var rad = dx * r1.x + dy * r1.y + dz * r1.z;
		if (Math.Abs(rad) > proj1(r1) + proj2(r1)) return false;

		rad = dx * u1.x + dy * u1.y + dz * u1.z;
		if (Math.Abs(rad) > proj1(u1) + proj2(u1)) return false;

		rad = dx * l1.x + dy * l1.y + dz * l1.z;
		if (Math.Abs(rad) > proj1(l1) + proj2(l1)) return false;

		rad = dx * r2.x + dy * r2.y + dz * r2.z;
		if (Math.Abs(rad) > proj1(r2) + proj2(r2)) return false;

		rad = dx * u2.x + dy * u2.y + dz * u2.z;
		if (Math.Abs(rad) > proj1(u2) + proj2(u2)) return false;

		rad = dx * l2.x + dy * l2.y + dz * l2.z;
		if (Math.Abs(rad) > proj1(l2) + proj2(l2)) return false;

		// Cross product axes
		var cr = iron.math.Vec4.crossvecs(r1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		return true;
	}
}
	/**
	 * Returns the given world vector in local coordinates
	 * @param worldVec
	 * @return Vec4
	 */
	public static inline function getLocalVecFromWorld(t: Transform, worldVec: Vec4): Vec4 {
		return worldVec.clone().applymat4(Mat4.identity().getInverse(t.worldUnpack));
	
	/**
	 * OBB-aware overlap check using SAT (Separating Axis Theorem).
	 * Accounts for rotation and scale of both transforms.
	 * Minimal, conservative approximation: checks axis alignment
	 * between the two objects' world-space basis vectors.
	 */
	public static function overlap_obb(t1: Transform, t2: Transform): Bool {
		// Ensure matrices are up to date
		t1.update();
		t2.update();

		// Half-dimensions in world space (already include scale via computeDim)
		var h1x = t1.dim.x / 2.0;
		var h1y = t1.dim.y / 2.0;
		var h1z = t1.dim.z / 2.0;
		var h2x = t2.dim.x / 2.0;
		var h2y = t2.dim.y / 2.0;
		var h2z = t2.dim.z / 2.0;

		// World positions
		var p1x = t1.worldx(); var p1y = t1.worldy(); var p1z = t1.worldz();
		var p2x = t2.worldx(); var p2y = t2.worldy(); var p2z = t2.worldz();

		// World-space basis vectors (right=local X, up=local Z in Iron, look=local Y)
		var r1 = t1.right();
		var u1 = t1.up();
		var l1 = t1.look();
		var r2 = t2.right();
		var u2 = t2.up();
		var l2 = t2.look();

		// Vector between centers
		var dx = p2x - p1x;
		var dy = p2y - p1y;
		var dz = p2z - p1z;

		// Helper: project half-extent onto an axis
		inline function proj1(ax: iron.math.Vec4): Float {
			return h1x * Math.Abs(ax.dot(r1)) + h1y * Math.Abs(ax.dot(u1)) + h1z * Math.Abs(ax.dot(l1));
		}
		inline function proj2(ax: iron.math.Vec4): Float {
			return h2x * Math.Abs(ax.dot(r2)) + h2y * Math.Abs(ax.dot(u2)) + h2z * Math.Abs(ax.dot(l2));
		}

		// Test 9 separating axes: 3 from each box
		var rad = dx * r1.x + dy * r1.y + dz * r1.z;
		if (Math.Abs(rad) > proj1(r1) + proj2(r1)) return false;

		rad = dx * u1.x + dy * u1.y + dz * u1.z;
		if (Math.Abs(rad) > proj1(u1) + proj2(u1)) return false;

		rad = dx * l1.x + dy * l1.y + dz * l1.z;
		if (Math.Abs(rad) > proj1(l1) + proj2(l1)) return false;

		rad = dx * r2.x + dy * r2.y + dz * r2.z;
		if (Math.Abs(rad) > proj1(r2) + proj2(r2)) return false;

		rad = dx * u2.x + dy * u2.y + dz * u2.z;
		if (Math.Abs(rad) > proj1(u2) + proj2(u2)) return false;

		rad = dx * l2.x + dy * l2.y + dz * l2.z;
		if (Math.Abs(rad) > proj1(l2) + proj2(l2)) return false;

		// Cross product axes
		var cr = iron.math.Vec4.crossvecs(r1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		return true;
	}
}
	/**
	* Returns the given world vector in transform orientation
	* @param worldVec
	* @return Vec4
	**/
	public static inline function worldVecToOrientation(t: Transform, worldVec: Vec4): Vec4 {
		var right = t.right().normalize();
		right.mult(worldVec.x);

		var look = t.look().normalize();
		look.mult(worldVec.y);

		var up = t.up().normalize();
		up.mult(worldVec.z);
		
		return new Vec4().add(right).add(look).add(up);
	
	/**
	 * OBB-aware overlap check using SAT (Separating Axis Theorem).
	 * Accounts for rotation and scale of both transforms.
	 * Minimal, conservative approximation: checks axis alignment
	 * between the two objects' world-space basis vectors.
	 */
	public static function overlap_obb(t1: Transform, t2: Transform): Bool {
		// Ensure matrices are up to date
		t1.update();
		t2.update();

		// Half-dimensions in world space (already include scale via computeDim)
		var h1x = t1.dim.x / 2.0;
		var h1y = t1.dim.y / 2.0;
		var h1z = t1.dim.z / 2.0;
		var h2x = t2.dim.x / 2.0;
		var h2y = t2.dim.y / 2.0;
		var h2z = t2.dim.z / 2.0;

		// World positions
		var p1x = t1.worldx(); var p1y = t1.worldy(); var p1z = t1.worldz();
		var p2x = t2.worldx(); var p2y = t2.worldy(); var p2z = t2.worldz();

		// World-space basis vectors (right=local X, up=local Z in Iron, look=local Y)
		var r1 = t1.right();
		var u1 = t1.up();
		var l1 = t1.look();
		var r2 = t2.right();
		var u2 = t2.up();
		var l2 = t2.look();

		// Vector between centers
		var dx = p2x - p1x;
		var dy = p2y - p1y;
		var dz = p2z - p1z;

		// Helper: project half-extent onto an axis
		inline function proj1(ax: iron.math.Vec4): Float {
			return h1x * Math.Abs(ax.dot(r1)) + h1y * Math.Abs(ax.dot(u1)) + h1z * Math.Abs(ax.dot(l1));
		}
		inline function proj2(ax: iron.math.Vec4): Float {
			return h2x * Math.Abs(ax.dot(r2)) + h2y * Math.Abs(ax.dot(u2)) + h2z * Math.Abs(ax.dot(l2));
		}

		// Test 9 separating axes: 3 from each box
		var rad = dx * r1.x + dy * r1.y + dz * r1.z;
		if (Math.Abs(rad) > proj1(r1) + proj2(r1)) return false;

		rad = dx * u1.x + dy * u1.y + dz * u1.z;
		if (Math.Abs(rad) > proj1(u1) + proj2(u1)) return false;

		rad = dx * l1.x + dy * l1.y + dz * l1.z;
		if (Math.Abs(rad) > proj1(l1) + proj2(l1)) return false;

		rad = dx * r2.x + dy * r2.y + dz * r2.z;
		if (Math.Abs(rad) > proj1(r2) + proj2(r2)) return false;

		rad = dx * u2.x + dy * u2.y + dz * u2.z;
		if (Math.Abs(rad) > proj1(u2) + proj2(u2)) return false;

		rad = dx * l2.x + dy * l2.y + dz * l2.z;
		if (Math.Abs(rad) > proj1(l2) + proj2(l2)) return false;

		// Cross product axes
		var cr = iron.math.Vec4.crossvecs(r1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		return true;
	}
}

	/**
	* Returns the given world vector in local orientation
	* @param worldVec Vector in world orientation
	* @return Local vector
	**/
	public static inline function getWorldVectorAlongLocalAxis(t: Transform, worldVec: Vec4): Vec4 {

		var localVec = new Vec4();
		localVec.x = worldVec.dot(t.right().normalize());
		localVec.y = worldVec.dot(t.look().normalize());
		localVec.z = worldVec.dot(t.up().normalize());

		return localVec;
	
	/**
	 * OBB-aware overlap check using SAT (Separating Axis Theorem).
	 * Accounts for rotation and scale of both transforms.
	 * Minimal, conservative approximation: checks axis alignment
	 * between the two objects' world-space basis vectors.
	 */
	public static function overlap_obb(t1: Transform, t2: Transform): Bool {
		// Ensure matrices are up to date
		t1.update();
		t2.update();

		// Half-dimensions in world space (already include scale via computeDim)
		var h1x = t1.dim.x / 2.0;
		var h1y = t1.dim.y / 2.0;
		var h1z = t1.dim.z / 2.0;
		var h2x = t2.dim.x / 2.0;
		var h2y = t2.dim.y / 2.0;
		var h2z = t2.dim.z / 2.0;

		// World positions
		var p1x = t1.worldx(); var p1y = t1.worldy(); var p1z = t1.worldz();
		var p2x = t2.worldx(); var p2y = t2.worldy(); var p2z = t2.worldz();

		// World-space basis vectors (right=local X, up=local Z in Iron, look=local Y)
		var r1 = t1.right();
		var u1 = t1.up();
		var l1 = t1.look();
		var r2 = t2.right();
		var u2 = t2.up();
		var l2 = t2.look();

		// Vector between centers
		var dx = p2x - p1x;
		var dy = p2y - p1y;
		var dz = p2z - p1z;

		// Helper: project half-extent onto an axis
		inline function proj1(ax: iron.math.Vec4): Float {
			return h1x * Math.Abs(ax.dot(r1)) + h1y * Math.Abs(ax.dot(u1)) + h1z * Math.Abs(ax.dot(l1));
		}
		inline function proj2(ax: iron.math.Vec4): Float {
			return h2x * Math.Abs(ax.dot(r2)) + h2y * Math.Abs(ax.dot(u2)) + h2z * Math.Abs(ax.dot(l2));
		}

		// Test 9 separating axes: 3 from each box
		var rad = dx * r1.x + dy * r1.y + dz * r1.z;
		if (Math.Abs(rad) > proj1(r1) + proj2(r1)) return false;

		rad = dx * u1.x + dy * u1.y + dz * u1.z;
		if (Math.Abs(rad) > proj1(u1) + proj2(u1)) return false;

		rad = dx * l1.x + dy * l1.y + dz * l1.z;
		if (Math.Abs(rad) > proj1(l1) + proj2(l1)) return false;

		rad = dx * r2.x + dy * r2.y + dz * r2.z;
		if (Math.Abs(rad) > proj1(r2) + proj2(r2)) return false;

		rad = dx * u2.x + dy * u2.y + dz * u2.z;
		if (Math.Abs(rad) > proj1(u2) + proj2(u2)) return false;

		rad = dx * l2.x + dy * l2.y + dz * l2.z;
		if (Math.Abs(rad) > proj1(l2) + proj2(l2)) return false;

		// Cross product axes
		var cr = iron.math.Vec4.crossvecs(r1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		return true;
	}
}

	/**
	 * OBB-aware overlap check using SAT (Separating Axis Theorem).
	 * Accounts for rotation and scale of both transforms.
	 * Minimal, conservative approximation: checks axis alignment
	 * between the two objects' world-space basis vectors.
	 */
	public static function overlap_obb(t1: Transform, t2: Transform): Bool {
		// Ensure matrices are up to date
		t1.update();
		t2.update();

		// Half-dimensions in world space (already include scale via computeDim)
		var h1x = t1.dim.x / 2.0;
		var h1y = t1.dim.y / 2.0;
		var h1z = t1.dim.z / 2.0;
		var h2x = t2.dim.x / 2.0;
		var h2y = t2.dim.y / 2.0;
		var h2z = t2.dim.z / 2.0;

		// World positions
		var p1x = t1.worldx(); var p1y = t1.worldy(); var p1z = t1.worldz();
		var p2x = t2.worldx(); var p2y = t2.worldy(); var p2z = t2.worldz();

		// World-space basis vectors (right=local X, up=local Z in Iron, look=local Y)
		var r1 = t1.right();
		var u1 = t1.up();
		var l1 = t1.look();
		var r2 = t2.right();
		var u2 = t2.up();
		var l2 = t2.look();

		// Vector between centers
		var dx = p2x - p1x;
		var dy = p2y - p1y;
		var dz = p2z - p1z;

		// Helper: project half-extent onto an axis
		inline function proj1(ax: iron.math.Vec4): Float {
			return h1x * Math.Abs(ax.dot(r1)) + h1y * Math.Abs(ax.dot(u1)) + h1z * Math.Abs(ax.dot(l1));
		}
		inline function proj2(ax: iron.math.Vec4): Float {
			return h2x * Math.Abs(ax.dot(r2)) + h2y * Math.Abs(ax.dot(u2)) + h2z * Math.Abs(ax.dot(l2));
		}

		// Test 9 separating axes: 3 from each box
		var rad = dx * r1.x + dy * r1.y + dz * r1.z;
		if (Math.Abs(rad) > proj1(r1) + proj2(r1)) return false;

		rad = dx * u1.x + dy * u1.y + dz * u1.z;
		if (Math.Abs(rad) > proj1(u1) + proj2(u1)) return false;

		rad = dx * l1.x + dy * l1.y + dz * l1.z;
		if (Math.Abs(rad) > proj1(l1) + proj2(l1)) return false;

		rad = dx * r2.x + dy * r2.y + dz * r2.z;
		if (Math.Abs(rad) > proj1(r2) + proj2(r2)) return false;

		rad = dx * u2.x + dy * u2.y + dz * u2.z;
		if (Math.Abs(rad) > proj1(u2) + proj2(u2)) return false;

		rad = dx * l2.x + dy * l2.y + dz * l2.z;
		if (Math.Abs(rad) > proj1(l2) + proj2(l2)) return false;

		// Cross product axes
		var cr = iron.math.Vec4.crossvecs(r1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(r1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(u1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, r2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, u2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		cr = iron.math.Vec4.crossvecs(l1, l2);
		if (cr.lengthSq() > 0.0001) {
			cr.normalize();
			var rad2 = dx * cr.x + dy * cr.y + dz * cr.z;
			if (Math.Abs(rad2) > proj1(cr) + proj2(cr)) return false;
		}

		return true;
	}
}

