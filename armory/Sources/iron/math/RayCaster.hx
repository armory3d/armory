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
