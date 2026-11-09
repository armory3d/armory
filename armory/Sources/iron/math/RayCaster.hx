package iron.math;

import kha.FastFloat;
import iron.object.CameraObject;
import iron.object.MeshObject;
import iron.object.Transform;
import iron.object.Object;
import iron.math.Ray;

class RayCaster {

	static var VPInv = Mat4.identity();
	static var PInv = Mat4.identity();
	static var VInv = Mat4.identity();

	static var loc = new Vec4();
	static var nor = new Vec4();
	static var m = Mat4.identity();

	// Scratch data for oriented bounding box / exact mesh ray tests
	static var invWorld = Mat4.identity();
	static var localOrigin = new Vec4();

	/**
		World space hit location of the last `closestObbIntersectObject()` call,
		or `null` if nothing was hit.
	**/
	public static var lastHit: Vec4 = null;

	public static function getRay(inputX: FastFloat, inputY: FastFloat, camera: CameraObject): Ray {
		var start = new Vec4();
		var end = new Vec4();
		getDirection(start, end, inputX, inputY, camera);

		// Find direction from start to end
		end.sub(start);
		end.normalize();
		end.x *= camera.data.raw.far_plane;
		end.y *= camera.data.raw.far_plane;
		end.z *= camera.data.raw.far_plane;

		return new Ray(start, end);
	}

	public static function getDirection(start: Vec4, end: Vec4, inputX: FastFloat, inputY: FastFloat, camera: CameraObject) {
		// Get 3D point form screen coords
		// Set two vectors with opposing z values
		start.x = (inputX / iron.App.w()) * 2.0 - 1.0;
		start.y = -((inputY / iron.App.h()) * 2.0 - 1.0);
		start.z = -1.0;
		end.x = start.x;
		end.y = start.y;
		end.z = 1.0;

		PInv.getInverse(camera.P);
		VInv.getInverse(camera.V);
		VPInv.multmats(VInv, PInv);
		start.applyproj(VPInv);
		end.applyproj(VPInv);
	}

	public static function boxIntersect(transform: Transform, inputX: FastFloat, inputY: FastFloat, camera: CameraObject): Vec4 {
		var ray = getRay(inputX, inputY, camera);

		var t = transform;
		var c = new Vec4(t.worldx(), t.worldy(), t.worldz());
		var s = new Vec4(t.dim.x, t.dim.y, t.dim.z);
		return ray.intersectBox(c, s);
	}
	
	public static function boxIntersectObject(o: Object, inputX: FastFloat, inputY: FastFloat, camera: CameraObject): Vec4 {
		var ray = getRay(inputX, inputY, camera);

		var t = o.transform;
		var c = new Vec4(t.worldx(), t.worldy(), t.worldz());
		var s = new Vec4(t.dim.x, t.dim.y, t.dim.z);
		return ray.intersectBox(c, s);
	}

	public static function closestBoxIntersect(transforms: Array<Transform>, inputX: FastFloat, inputY: FastFloat, camera: CameraObject): Transform {
		var intersects: Array<Transform> = [];

		// Get intersects
		for (t in transforms) {
			var intersect = boxIntersect(t, inputX, inputY, camera);
			if (intersect != null) intersects.push(t);
		}

		// No intersects
		if (intersects.length == 0) return null;

		// Get closest intersect
		var closest: Transform = null;
		var minDist = Math.POSITIVE_INFINITY;
		for (t in intersects) {
			var dist = Vec4.distance(t.loc, camera.transform.loc);
			if (dist < minDist) {
				minDist = dist;
				closest = t;
			}
		}

		return closest;
	}

	public static function closestBoxIntersectObject(objects: Array<Object>, inputX: FastFloat, inputY: FastFloat, camera: CameraObject): Object {
		var intersects: Array<Object> = [];

		// Get intersects
		for (o in objects) {
			var intersect = boxIntersectObject(o, inputX, inputY, camera);
			if (intersect != null) intersects.push(o);
		}

		// No intersects
		if (intersects.length == 0) return null;

		// Get closest intersect
		var closest: Object = null;
		var minDist = Math.POSITIVE_INFINITY;
		for (t in intersects) {
			var dist = Vec4.distance(t.transform.loc, camera.transform.loc);
			if (dist < minDist) {
				minDist = dist;
				closest = t;
			}
		}

		return closest;
	}

	/**
		Cast a ray from the given screen coordinates and test it against the
		oriented bounding box (OBB) of the object. The ray is transformed into
		the object's local space, so rotation and (parent) scale are respected.
		@param	exactMesh If `true` and the object is a non-skinned `MeshObject`,
				the triangles of the mesh are tested after the OBB broad-phase
				check passes. Skinned (and morphed) meshes fall back to the OBB.
		@return	The world space hit location, or `null` if there is no hit.
	**/
	public static function obbIntersectObject(o: Object, inputX: FastFloat, inputY: FastFloat, camera: CameraObject, exactMesh = false): Vec4 {
		if (o == null || camera == null) return null;

		var ray = getRay(inputX, inputY, camera);
		var dist = rayObjectDistance(ray, o, exactMesh);
		return dist < 0 ? null : ray.at(dist);
	}

	/**
		Like `obbIntersectObject()`, but returns the object with the nearest
		hit along the ray. The hit location is stored in `RayCaster.lastHit`.
		@return	The closest hit object, or `null` if no object was hit.
	**/
	public static function closestObbIntersectObject(objects: Array<Object>, inputX: FastFloat, inputY: FastFloat, camera: CameraObject, exactMesh = false): Object {
		lastHit = null;
		if (objects == null || camera == null) return null;

		var ray = getRay(inputX, inputY, camera);
		var closest: Object = null;
		var minDist = Math.POSITIVE_INFINITY;

		for (o in objects) {
			if (o == null) continue;
			var dist = rayObjectDistance(ray, o, exactMesh);
			if (dist >= 0 && dist < minDist) {
				minDist = dist;
				closest = o;
			}
		}

		if (closest != null) lastHit = ray.at(minDist);
		return closest;
	}

	/**
		Test a world space ray against an object's oriented bounding box and,
		optionally, against its mesh triangles.
		@return	The ray parameter `t` of the hit (world hit = `ray.at(t)`),
				or `-1` if there is no hit.
	**/
	public static function rayObjectDistance(ray: Ray, o: Object, exactMesh = false): Float {
		if (ray == null || o == null) return -1;

		var tr = o.transform;
		var sx: Float = tr.scale.x;
		var sy: Float = tr.scale.y;
		var sz: Float = tr.scale.z;
		if (sx == 0 || sy == 0 || sz == 0) return -1;

		// World -> local space. Affine mapping, so the ray parameter `t` is preserved
		invWorld.getInverse(tr.world);
		localOrigin.setFrom(ray.origin);
		localOrigin.applymat(invWorld);
		var ox: Float = localOrigin.x;
		var oy: Float = localOrigin.y;
		var oz: Float = localOrigin.z;

		// Direction: rotation / scale only, no translation
		var wd = ray.direction;
		var iw = invWorld;
		var dx: Float = iw._00 * wd.x + iw._10 * wd.y + iw._20 * wd.z;
		var dy: Float = iw._01 * wd.x + iw._11 * wd.y + iw._21 * wd.z;
		var dz: Float = iw._02 * wd.x + iw._12 * wd.y + iw._22 * wd.z;

		// Local bounding box, centered at the origin (see exporter calc_aabb)
		var hx: Float = Math.abs(tr.dim.x / sx) * 0.5;
		var hy: Float = Math.abs(tr.dim.y / sy) * 0.5;
		var hz: Float = Math.abs(tr.dim.z / sz) * 0.5;

		// Broad phase
		var boxDist = rayLocalBox(ox, oy, oz, dx, dy, dz, hx, hy, hz);
		if (boxDist < 0 || !exactMesh) return boxDist;

		// Narrow phase, fall back to the OBB result when triangles are unusable
		if (!Std.isOfType(o, MeshObject)) return boxDist;
		var mo: MeshObject = cast o;
		if (mo.data == null || mo.data.geom == null || mo.data.isSkinned) return boxDist;
		#if arm_morph_target
		if (mo.morphTarget != null) return boxDist;
		#end
		var geom = mo.data.geom;
		if (geom.positions == null || geom.positions.values == null || geom.indices == null) return boxDist;

		return rayPackedMesh(mo, ox, oy, oz, dx, dy, dz);
	}

	/**
		Slab test of a local space ray against a box centered at the origin.
		@return	Distance parameter of the entry point (or of the exit point if
				the ray starts inside the box), `-1` on miss.
	**/
	static function rayLocalBox(ox: Float, oy: Float, oz: Float, dx: Float, dy: Float, dz: Float, hx: Float, hy: Float, hz: Float): Float {
		var tmin = Math.NEGATIVE_INFINITY;
		var tmax = Math.POSITIVE_INFINITY;

		// X slab
		if (dx == 0) {
			if (ox < -hx || ox > hx) return -1;
		}
		else {
			var inv = 1.0 / dx;
			var t1 = (-hx - ox) * inv;
			var t2 = (hx - ox) * inv;
			if (t1 > t2) { var tmp = t1; t1 = t2; t2 = tmp; }
			if (t1 > tmin) tmin = t1;
			if (t2 < tmax) tmax = t2;
			if (tmin > tmax) return -1;
		}

		// Y slab
		if (dy == 0) {
			if (oy < -hy || oy > hy) return -1;
		}
		else {
			var inv = 1.0 / dy;
			var t1 = (-hy - oy) * inv;
			var t2 = (hy - oy) * inv;
			if (t1 > t2) { var tmp = t1; t1 = t2; t2 = tmp; }
			if (t1 > tmin) tmin = t1;
			if (t2 < tmax) tmax = t2;
			if (tmin > tmax) return -1;
		}

		// Z slab
		if (dz == 0) {
			if (oz < -hz || oz > hz) return -1;
		}
		else {
			var inv = 1.0 / dz;
			var t1 = (-hz - oz) * inv;
			var t2 = (hz - oz) * inv;
			if (t1 > t2) { var tmp = t1; t1 = t2; t2 = tmp; }
			if (t1 > tmin) tmin = t1;
			if (t2 < tmax) tmax = t2;
			if (tmin > tmax) return -1;
		}

		// Box is behind the ray
		if (tmax < 0) return -1;

		return tmin >= 0 ? tmin : tmax;
	}

	/**
		Möller–Trumbore test of a local space ray against all triangles of a
		mesh. Positions are tested in their packed int16 form; the ray is
		scaled into that space instead, which leaves `t` unchanged.
		Back faces are not culled.
		@return	Distance parameter of the nearest hit, `-1` on miss.
	**/
	static function rayPackedMesh(mo: MeshObject, ox: Float, oy: Float, oz: Float, dx: Float, dy: Float, dz: Float): Float {
		var geom = mo.data.geom;
		var pos = geom.positions.values;
		var size: Null<Int> = geom.positions.size;
		var stride: Int = (size != null && size >= 3) ? size : 4;

		// Local units -> packed units
		var toPacked: Float = 32767 / mo.data.scalePos;
		ox *= toPacked; oy *= toPacked; oz *= toPacked;
		dx *= toPacked; dy *= toPacked; dz *= toPacked;

		var best = Math.POSITIVE_INFINITY;

		for (ind in geom.indices) {
			if (ind == null) continue;
			var i = 0;
			var len = ind.length - 2;
			while (i < len) {
				var i0: Int = ind[i] * stride;
				var i1: Int = ind[i + 1] * stride;
				var i2: Int = ind[i + 2] * stride;
				i += 3;

				var v0x: Float = pos[i0];
				var v0y: Float = pos[i0 + 1];
				var v0z: Float = pos[i0 + 2];

				// Edges
				var e1x: Float = pos[i1] - v0x;
				var e1y: Float = pos[i1 + 1] - v0y;
				var e1z: Float = pos[i1 + 2] - v0z;
				var e2x: Float = pos[i2] - v0x;
				var e2y: Float = pos[i2 + 1] - v0y;
				var e2z: Float = pos[i2 + 2] - v0z;

				// p = d x e2
				var px = dy * e2z - dz * e2y;
				var py = dz * e2x - dx * e2z;
				var pz = dx * e2y - dy * e2x;

				var det = e1x * px + e1y * py + e1z * pz;
				if (det > -1e-12 && det < 1e-12) continue; // Parallel or degenerate
				var invDet = 1.0 / det;

				// s = o - v0
				var sx = ox - v0x;
				var sy = oy - v0y;
				var sz = oz - v0z;

				var u = (sx * px + sy * py + sz * pz) * invDet;
				if (u < 0.0 || u > 1.0) continue;

				// q = s x e1
				var qx = sy * e1z - sz * e1y;
				var qy = sz * e1x - sx * e1z;
				var qz = sx * e1y - sy * e1x;

				var v = (dx * qx + dy * qy + dz * qz) * invDet;
				if (v < 0.0 || u + v > 1.0) continue;

				var t = (e2x * qx + e2y * qy + e2z * qz) * invDet;
				if (t >= 0.0 && t < best) best = t;
			}
		}

		return best == Math.POSITIVE_INFINITY ? -1 : best;
	}
	
	public static function planeIntersect(normal: Vec4, a: Vec4, inputX: FastFloat, inputY: FastFloat, camera: CameraObject): Vec4 {
		var ray = getRay(inputX, inputY, camera);

		var plane = new Plane();
		plane.set(normal, a);

		return ray.intersectPlane(plane);
	}

	// Project screen-space point onto 3D plane
	public static function getPlaneUV(obj: MeshObject, screenX: FastFloat, screenY: FastFloat, camera: CameraObject): Vec2 {
		nor = obj.transform.up(); // Transformed normal

		// Plane intersection
		loc.set(obj.transform.worldx(), obj.transform.worldy(), obj.transform.worldz());
		var hit = RayCaster.planeIntersect(nor, loc, screenX, screenY, camera);

		// Convert to uv
		if (hit != null) {
			var normals = obj.data.geom.normals.values;
			nor.set(normals[0], normals[1], normals[2]); // Raw normal

			var a = nor.x;
			var b = nor.y;
			var c = nor.z;
			var e = 0.0001;
			var u = a >= e && b >= e ? new Vec4(b, -a, 0) : new Vec4(c, -a, 0);
			u.normalize();

			var v = nor.clone();
			v.cross(u);

			m.setFrom(obj.transform.world);
			m.getInverse(m);
			m.transpose3x3();
			m._30 = m._31 = m._32 = 0;
			u.applymat(m);
			u.normalize();
			v.applymat(m);
			v.normalize();

			hit.sub(loc); // Center
			var ucoord = u.dot(hit);
			var vcoord = v.dot(hit);

			var dim = obj.transform.dim;
			var size = dim.x > dim.y ? dim.x / 2 : dim.y / 2;

			// Screen space
			var ix = ucoord / size * -0.5 + 0.5;
			var iy = vcoord / size * -0.5 + 0.5;

			return new Vec2(ix, iy);
		}
		return null;
	}
}
