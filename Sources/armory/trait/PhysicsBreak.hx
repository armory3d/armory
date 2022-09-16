package armory.trait;

import iron.math.Vec4;
import iron.math.Mat4;
import iron.Trait;
import iron.object.MeshObject;
import iron.data.MeshData;
import iron.data.SceneFormat;
#if arm_bullet
import armory.trait.physics.bullet.RigidBody;
import armory.trait.physics.PhysicsWorld;
#end

class PhysicsBreak extends Trait {

#if (!arm_bullet)
	public function new() { super(); }
#else

	static var physics: PhysicsWorld = null;
	static var breaker: ConvexBreaker = null;

	var body: RigidBody;

	public function new() {
		super();

		if (breaker == null) breaker = new ConvexBreaker();
		notifyOnInit(init);
	}

	function init() {
		if (physics == null) physics = armory.trait.physics.PhysicsWorld.active;

		body = object.getTrait(RigidBody);
		breaker.initBreakableObject(cast object, body.mass, body.friction, new Vec4(), new Vec4(), true);

		notifyOnUpdate(update);
	}

	function update() {
		var ar = physics.getContactPairs(body);
		if (ar != null) {
			var maxImpulse = 0.0;
			var impactPoint: Vec4 = null;
			var impactNormal: Vec4 = null;
			for (p in ar) {
				if (maxImpulse < p.impulse) {
					maxImpulse = p.impulse;
					impactPoint = p.posB;
					impactNormal = p.normOnB;
				}
			}

			var fractureImpulse = 4.0;
			if (maxImpulse > fractureImpulse) {
				var radialIter = 1;
				var randIter = 1;
				var debris = breaker.subdivideByImpact(cast object, impactPoint, impactNormal, radialIter, randIter);
				// var numObjects = debris.length;
				for (o in debris) {
					var ud = breaker.userDataMap.get(cast o);
					var params: RigidBodyParams = {
						linearDamping: 0.04,
						angularDamping: 0.1,
						angularFriction: 0.1,
						linearFactorsX: 1.0,
						linearFactorsY: 1.0,
						linearFactorsZ: 1.0,
						angularFactorsX: 1.0,
						angularFactorsY: 1.0,
						angularFactorsZ: 1.0,
						collisionMargin: 0.04,
						linearDeactivationThreshold: 0.0,
						angularDeactivationThrshold: 0.0,
						deactivationTime: 0.0
					};
					o.addTrait(new RigidBody(Shape.ConvexHull, ud.mass, ud.friction, 0, 1, params));
					if (cast(o, MeshObject).data.geom.positions.values.length < 600) {
						o.addTrait(new PhysicsBreak());
					}
				}
				object.remove();
			}
		}
	}

#end
}

// Based on work by yomboprime https://github.com/yomboprime
// This class can be used to subdivide a convex geometry object into pieces
class ConvexBreaker {

	var minSizeForBreak: Float;
	var smallDelta: Float;

	var tempLine: Line3;
	var tempPlane: Plane;
	var tempPlane2: Plane;
	var tempCM1: Vec4;
	var tempCM2: Vec4;
	var tempVec4: Vec4;
	var tempVec42: Vec4;
	var tempVec43: Vec4;
	var tempCutResult: CutResult;
	var segments: Array<Bool>;

	public var userDataMap: Map<MeshObject, UserData>;

	// minSizeForBreak Min size a debris can have to break
	// smallDelta Max distance to consider that a point belongs to a plane
	public function new(minSizeForBreak = 1.4, smallDelta = 0.0001) {
		this.minSizeForBreak = minSizeForBreak;
		this.smallDelta = smallDelta;
		tempLine = new Line3();
		tempPlane = new Plane();
		tempPlane2 = new Plane();
		tempCM1 = new Vec4();
		tempCM2 = new Vec4();
		tempVec4 = new Vec4();
		tempVec42 = new Vec4();
		tempVec43 = new Vec4();
		tempCutResult = new CutResult();
		segments = new Array<Bool>();
		var n = 30 * 30;
		for (i in 0...n) segments.push(false);
		userDataMap = new Map();
	}

	public function initBreakableObject(object: MeshObject, mass: Float, friction: Float, velocity: Vec4, angularVelocity: Vec4, breakable: Bool) {
		var ar = object.data.geom.positions.values;
		var scalePos = object.data.scalePos;
		// Create vertices mark
		var sc = object.transform.scale;
		var vertices = new Array<Vec4>();
		for (i in 0...Std.int(ar.length / 4)) {
			// Use w component as mark
			vertices.push(new Vec4(
				ar[i * 4    ] * sc.x * (1 / 32767) * scalePos,
				ar[i * 4 + 1] * sc.y * (1 / 32767) * scalePos,
				ar[i * 4 + 2] * sc.z * (1 / 32767) * scalePos,
				0
			));
		}

		var ind = object.data.geom.indices[0];
		var faces = new Array<Face3>();
		for (i in 0...Std.int(ind.length / 3)) {
			var a = ind[i * 3];
			var b = ind[i * 3 + 1];
			var c = ind[i * 3 + 2];
			// Merge duplis
			for (f in faces) {
				if (vertices[a].equals(vertices[f.a])) a = f.a;
				else if (vertices[a].equals(vertices[f.b])) a = f.b;
				else if (vertices[a].equals(vertices[f.c])) a = f.c;
				if (vertices[b].equals(vertices[f.a])) b = f.a;
				else if (vertices[b].equals(vertices[f.b])) b = f.b;
				else if (vertices[b].equals(vertices[f.c])) b = f.c;
				if (vertices[c].equals(vertices[f.a])) c = f.a;
				else if (vertices[c].equals(vertices[f.b])) c = f.b;
				else if (vertices[c].equals(vertices[f.c])) c = f.c;
			}
			faces.push(new Face3(a, b, c));
		}
		// Reorder vertices
		var verts = new Array<Vec4>();
		var map = new Map<Int, Int>();
		var i = 0;
		function orderVert(fi: Int): Int {
			var val = map.get(fi);
			if (val == null) {
				verts.push(vertices[fi]);
				map.set(fi, i);
				i++;
				return i - 1;
			}
			else return val;
		}
		for (f in faces) {
			f.a = orderVert(f.a);
			f.b = orderVert(f.b);
			f.c = orderVert(f.c);
		}

		var userData = new UserData();
		userData.mass = mass;
		userData.friction = friction;
		userData.velocity = velocity.clone();
		userData.angularVelocity = angularVelocity.clone();
		userData.breakable = breakable;
		userData.vertices = verts;
		userData.faces = faces;
		userDataMap.set(object, userData);
	}

	// maxRadialIterations Iterations for radial cuts
	// maxRandomIterations Max random iterations for not-radial cuts
	public function subdivideByImpact(object: MeshObject, pointOfImpact: Vec4, normal: Vec4, maxRadialIterations: Int, maxRandomIterations: Int): Array<MeshObject> {
		var debris: Array<MeshObject> = [];

		tempVec4.addvecs(pointOfImpact, normal);
		tempPlane.setFromCoplanarPoints(pointOfImpact, object.transform.loc, tempVec4);

		var maxTotalIterations = maxRandomIterations + maxRadialIterations;
		var scope = this;

		function subdivideRadial(subObject: MeshObject, startAngle: Float, endAngle: Float, numIterations: Int) {

			if (Math.random() < numIterations * 0.05 || numIterations > maxTotalIterations) {
				debris.push(subObject);
				return;
			}

			var angle = Math.PI;
			if (numIterations == 0) {
				tempPlane2.normal.setFrom(tempPlane.normal);
				tempPlane2.constant = tempPlane.constant;
			}
			else {
				if (numIterations <= maxRadialIterations) {
					angle = (endAngle - startAngle) * (0.2 + 0.6 * Math.random()) + startAngle;

					// Rotate tempPlane2 at impact point around normal axis and the angle
					scope.tempVec42.setFrom(object.transform.loc).sub(pointOfImpact).applyAxisAngle(normal, angle).add(pointOfImpact);
					tempPlane2.setFromCoplanarPoints(pointOfImpact, scope.tempVec4, scope.tempVec42);
				}
				else {
					angle = ((0.5 * (numIterations & 1)) + 0.2 * (2 - Math.random())) * Math.PI;

					// Rotate tempPlane2 at object position around normal axis and the angle
					scope.tempVec42.setFrom(pointOfImpact).sub(subObject.transform.loc).applyAxisAngle(normal, angle).add(subObject.transform.loc);
					scope.tempVec43.setFrom(normal).add(subObject.transform.loc);
					tempPlane2.setFromCoplanarPoints(subObject.transform.loc, scope.tempVec43, scope.tempVec42);
				}
			}

			// Perform the cut
			scope.cutByPlane(subObject, tempPlane2, scope.tempCutResult);

			var object1 = scope.tempCutResult.object1;
			var object2 = scope.tempCutResult.object2;
			if (object1 != null) subdivideRadial(object1, startAngle, angle, numIterations + 1);
			if (object2 != null) subdivideRadial(object2, angle, endAngle, numIterations + 1);

			// Object was subdivided into debris
			iron.Scene.active.meshes.remove(subObject);
		}

		subdivideRadial(object, 0, 2 * Math.PI, 0);
		return debris;
	}

	function transformFreeVector(v: Vec4, m: Mat4): Vec4 {
		// Vector interpreted as a free vector
		// Mat4 orthogonal matrix (matrix without scale)
		var x = v.x, y = v.y, z = v.z;
		v.x = m._00 * x + m._10 * y + m._20 * z;
		v.y = m._01 * x + m._11 * y + m._21 * z;
		v.z = m._02 * x + m._12 * y + m._22 * z;
		return v;
	}

	function transformFreeVectorInverse(v: Vec4, m: Mat4): Vec4 {
		// Vector interpreted as a free vector
		// Mat4 orthogonal matrix (matrix without scale)
		var x = v.x, y = v.y, z = v.z;
		v.x = m._00 * x + m._01 * y + m._02 * z;
		v.y = m._10 * x + m._11 * y + m._12 * z;
		v.z = m._20 * x + m._21 * y + m._22 * z;
		return v;
	}

	function transformTiedVectorInverse(v: Vec4, m: Mat4): Vec4 {
		// Vector interpreted as a tied (ordinary) vector
		// Mat4 orthogonal matrix (matrix without scale)
		var x = v.x, y = v.y, z = v.z;
		v.x = m._00 * x + m._01 * y + m._02 * z - m._30;
		v.y = m._10 * x + m._11 * y + m._12 * z - m._31;
		v.z = m._20 * x + m._21 * y + m._22 * z - m._32;
		return v;
	};

	function transformPlaneToLocalSpace(plane: Plane, m: Mat4, resultPlane: Plane) {
		resultPlane.normal.setFrom(plane.normal);
		resultPlane.constant = plane.constant;

		var v1 = new Vec4();
		var referencePoint = transformTiedVectorInverse(plane.coplanarPoint(v1), m);
		transformFreeVectorInverse(resultPlane.normal, m);

		// Recalculate constant
		resultPlane.constant = -referencePoint.dot(resultPlane.normal);
	}

	// Returns breakable objects, the resulting 2 pieces of the cut
	// object2 can be null if the plane doesn't cut the object
	// object1 can be null only in case of error
	// Returned value is number of pieces, 0 for error
	function cutByPlane(object: MeshObject, plane: Plane, output: CutResult): Int {
		var userData = userDataMap.get(object);
		var points: Array<Vec4> = userData.vertices;
		var faces: Array<Face3> = userData.faces;

		var numPoints = points.length;
		var points1 = [];
		var points2 = [];
		var delta = smallDelta;

		// Reset vertices mark
		for (i in 0...numPoints) points[i].w = 0;

		// Reset segments mark
		var numPointPairs = numPoints * numPoints;
		for (i in 0...numPointPairs) this.segments[i] = false;

		// Iterate through the faces to mark edges shared by coplanar faces
		for (i in 0...faces.length - 1) {
			var face1 = faces[i];

			for (j in (i + 1)...faces.length) {
				var face2 = faces[j];
				var coplanar = 1 - face1.normal.dot(face2.normal) < delta;

				if (coplanar) {
					var a1 = face1.a;
					var b1 = face1.b;
					var c1 = face1.c;
					var a2 = face2.a;
					var b2 = face2.b;
					var c2 = face2.c;

					if (a1 == a2 || a1 == b2 || a1 == c2) {
						if (b1 == a2 || b1 == b2 || b1 == c2) {
							this.segments[a1 * numPoints + b1] = true;
							this.segments[b1 * numPoints + a1] = true;
						}
						else {
							this.segments[c1 * numPoints + a1] = true;
							this.segments[a1 * numPoints + c1] = true;
						}
					}
					else if (b1 == a2 || b1 == b2 || b1 == c2) {
						this.segments[c1 * numPoints + b1] = true;
						this.segments[b1 * numPoints + c1] = true;
					}
				}
			}
		}

		// Transform the plane to object local space
		var localPlane = this.tempPlane;
		object.transform.buildMatrix();
		transformPlaneToLocalSpace(plane, object.transform.world, localPlane);

		// Iterate through the faces adding points to both pieces
		for (i in 0...faces.length) {

			var face = faces[i];
			for (segment in 0...3) {
				var i0 = segment == 0 ? face.a : (segment == 1 ? face.b : face.c);
				var i1 = segment == 0 ? face.b : (segment == 1 ? face.c : face.a);

				var segmentState = this.segments[i0 * numPoints + i1];
				// The segment already has been processed in another face
				if (segmentState) continue;

				// Mark segment as processed (also inverted segment)
				this.segments[i0 * numPoints + i1] = true;
				this.segments[i1 * numPoints + i0] = true;

				var p0 = points[i0];
				var p1 = points[i1];

				if (p0.w == 0) {
					var d = localPlane.distanceToPoint(p0);

					// mark: 1 for negative side, 2 for positive side, 3 for coplanar point
					if (d > delta) {
						p0.w = 2;
						points2.push(p0);
					}
					else if (d < -delta) {
						p0.w = 1;
						points1.push(p0);
					}
					else {
						p0.w = 3;
						points1.push(p0);
						var p02 = p0.clone();
						p02.w = 3;
						points2.push(p02);
					}
				}

				if (p1.w == 0) {
					var d = localPlane.distanceToPoint(p1);

					// mark: 1 for negative side, 2 for positive side, 3 for coplanar point
					if (d > delta) {
						p1.w = 2;
						points2.push(p1);
					}
					else if (d < -delta) {
						p1.w = 1;
						points1.push(p1);
					}
					else {
						p1.w = 3;
						points1.push(p1);
						var p1_2 = p1.clone();
						p1_2.w = 3;
						points2.push(p1_2);
					}
				}

				var mark0 = p0.w;
				var mark1 = p1.w;

				if ((mark0 == 1 && mark1 == 2 ) || ( mark0 == 2 && mark1 == 1)) {
					// Intersection of segment with the plane
					tempLine.start.setFrom(p0);
					tempLine.end.setFrom(p1);
					var intersection = localPlane.intersectLine(tempLine);
					if (intersection == null) return 0;

					intersection.w = 1;
					points1.push(intersection);
					var intersection_2 = intersection.clone();
					intersection_2.w = 2;
					points2.push(intersection_2);
				}
			}
		}

		// Calculate debris mass (very fast and imprecise):
		var newMass = userData.mass * 0.5;

		// Calculate debris Center of Mass (again fast and imprecise)
		tempCM1.set(0, 0, 0);
		var radius1 = 0.0;
		var numPoints1 = points1.length;
		if (numPoints1 > 0) {
			for (i in 0...numPoints1) {
				tempCM1.add(points1[i]);
			}
			tempCM1.mult(1.0 / numPoints1);
			for (i in 0...numPoints1) {
				var p = points1[i];
				p.sub(tempCM1);
				radius1 = Math.max(Math.max(radius1, p.x), Math.max(p.y, p.z));
			}
			tempCM1.add(object.transform.loc);
		}

		tempCM2.set(0, 0, 0);
		var radius2 = 0.0;
		var numPoints2 = points2.length;
		if (numPoints2 > 0) {
			for (i in 0...numPoints2) {
				tempCM2.add(points2[i]);
			}
			tempCM2.mult(1.0 / numPoints2);
			for (i in 0...numPoints2) {
				var p = points2[i];
				p.sub(tempCM2);
				radius2 = Math.max(Math.max(radius2, p.x), Math.max(p.y, p.z));
			}
			tempCM2.add(object.transform.loc);
		}

		var object1 = null;
		var object2 = null;
		var numObjects = 0;
		if (numPoints1 > 4) {
			var data1 = makeMeshData(points1);
			object1 = new MeshObject(data1, object.materials);
			object1.transform.loc.setFrom(tempCM1);
			object1.transform.rot.setFrom(object.transform.rot);
			object1.transform.buildMatrix();
			initBreakableObject(object1, newMass, userData.friction, userData.velocity, userData.angularVelocity, 2 * radius1 > minSizeForBreak);
			numObjects++;
		}

		if (numPoints2 > 4) {
			var data2 = makeMeshData(points2);
			object2 = new MeshObject(data2, object.materials);
			object2.transform.loc.setFrom(tempCM2);
			object2.transform.rot.setFrom(object.transform.rot);
			object2.transform.buildMatrix();
			initBreakableObject(object2, newMass, userData.friction, userData.velocity, userData.angularVelocity, 2 * radius2 > minSizeForBreak);
			numObjects++;
		}

		output.object1 = object1;
		output.object2 = object2;
		return numObjects;
	}

	static var meshIndex = 0;
	function makeMeshData(points: Array<Vec4>): MeshData {
		while (points.length > 50) points.pop();
		var cm = new ConvexHull(points);

		var maxdim = 1.0;
		var pa = new Array<Float>();
		var na = new Array<Float>();
		for (p in cm.vertices) {
			pa.push(p.x);
			pa.push(p.y);
			pa.push(p.z);
			na.push(0.0);
			na.push(0.0);
			na.push(0.0);

			var ax = Math.abs(p.x);
			var ay = Math.abs(p.y);
			var az = Math.abs(p.z);
			if (ax > maxdim) maxdim = ax;
			if (ay > maxdim) maxdim = ay;
			if (az > maxdim) maxdim = az;
		}
		maxdim *= 2;

		var ind = new Array<Int>();
		function addFlatNormal(normal: Vec4, fi: Int) {
			if (na[fi * 3] != 0.0 || na[fi * 3 + 1] != 0.0 || na[fi * 3 + 2] != 0.0) {
				pa.push(pa[fi * 3    ]);
				pa.push(pa[fi * 3 + 1]);
				pa.push(pa[fi * 3 + 2]);
				na.push(normal.x);
				na.push(normal.y);
				na.push(normal.z);
				ind.push(Std.int(pa.length / 3 - 1));
			}
			else {
				na[fi * 3    ] = normal.x;
				na[fi * 3 + 1] = normal.y;
				na[fi * 3 + 2] = normal.z;
				ind.push(fi);
			}
		}
		for (f in cm.face3s) {
			// Duplicate vertex for flat normals
			addFlatNormal(f.normal, f.a);
			addFlatNormal(f.normal, f.b);
			addFlatNormal(f.normal, f.c);
		}

		// TODO:
		var n = Std.int(pa.length / 3);
		var paa = new kha.arrays.Int16Array(n * 4);
		var naa = new kha.arrays.Int16Array(n * 2);
		var invdim = 1 / maxdim;
		for (i in 0...n) {
			paa.set(i * 4    , Std.int(pa[i * 3    ] * 32767 * invdim));
			paa.set(i * 4 + 1, Std.int(pa[i * 3 + 1] * 32767 * invdim));
			paa.set(i * 4 + 2, Std.int(pa[i * 3 + 2] * 32767 * invdim));
			naa.set(i * 2    , Std.int(na[i * 3    ] * 32767 * invdim));
			naa.set(i * 2 + 1, Std.int(na[i * 3 + 1] * 32767 * invdim));
			paa.set(i * 4 + 3, Std.int(na[i * 3 + 2] * 32767 * invdim));
		}
		var inda = new kha.arrays.Uint32Array(ind.length);
		for (i in 0...ind.length) inda.set(i, ind[i]);

		var pos: TVertexArray = { attrib: "pos", values: paa, data: "short4norm" };
		var nor: TVertexArray = { attrib: "nor", values: naa, data: "short2norm" };
		var indices: TIndexArray = { material: 0, values: inda };

		var rawmesh: TMeshData = {
			name: "TempMesh" + (meshIndex++),
			vertex_arrays: [pos, nor],
			index_arrays: [indices],
			scale_pos: maxdim
		};

		// Synchronous on Krom
		var md = new MeshData(rawmesh, function(d: MeshData) {});
		md.geom.calculateAABB();
		return md;
	}
}

class UserData {

	public var mass: Float;
	public var friction: Float;
	public var velocity: Vec4;
	public var angularVelocity: Vec4;
	public var breakable: Bool;

	public var vertices: Array<Vec4>;
	public var faces: Array<Face3>;

	public function new() {}
}

class CutResult {

	public var object1: MeshObject = null;
	public var object2: MeshObject = null;
	public function new() {}
}

class Line3 {

	public var start: Vec4;
	public var end: Vec4;

	public function new() {
		start = new Vec4();
		end = new Vec4();
	}

	public function delta(result: Vec4): Vec4 {
		result.subvecs(end, start);
		return result;
	}
}

class Plane {

	public var normal = new Vec4(1.0, 0.0, 0.0);
	public var constant = 0.0;

	public function new() {}

	public function distanceToPoint(point: Vec4): Float {
		return normal.dot(point) + constant;
	}

	public function setFromCoplanarPoints(a: Vec4, b: Vec4, c: Vec4): Plane {
		var v1 = new Vec4();
		var v2 = new Vec4();
		var normal = v1.subvecs(c, b).cross(v2.subvecs(a, b)).normalize();
		set(normal, a);
		return this;
	}

	public function set(normal: Vec4, point: Vec4): Plane {
		this.normal.setFrom(normal);
		constant = -point.dot(this.normal);
		return this;
	}

	public function coplanarPoint(result: Vec4): Vec4 {
		return result.setFrom(normal).mult(-constant);
	}

	public function intersectLine(line: Line3): Vec4 {
		var v1 = new Vec4();
		var result = new Vec4();
		var direction = line.delta(v1);
		var denominator = normal.dot(direction);
		if (denominator == 0) {
			// line is coplanar, return origin
			if (distanceToPoint(line.start) == 0) {
				return result.setFrom(line.start);
			}
			// Unsure if this is the correct method to handle this case.
			return null;
		}

		var t = -(line.start.dot(this.normal) + constant) / denominator;
		if (t < 0 || t > 1) return null;
		return result.setFrom(direction).mult(t).add(line.start);
	}
}

// Based on work by qiao https://github.com/qiao
// This is a convex hull generator using the incremental method
// The complexity is O(n^2) where n is the number of vertices
class ConvexHull {

	var faces = [[0, 1, 2], [0, 2, 1]];
	public var face3s = new Array<Face3>();
	public var vertices = new Array<Vec4>();

	public function new(vertices: Array<Vec4>) {

		for (i in 3...vertices.length) addPoint(i, vertices);

		// Push vertices into array, skipping those inside the hull
		// Map from old vertex id to new id
		var id = 0;
		var newId = new Array<Int>();
		for (i in 0...vertices.length) newId.push(-1);

		for (i in 0...faces.length) {
			 var face = faces[i];
			 for (j in 0...3) {
				if (newId[face[j]] == -1) {
					newId[face[j]] = id++;
					this.vertices.push(vertices[face[j]]);
				}
				face[j] = newId[face[j]];
			 }
		}

		for (i in 0...faces.length) {
			face3s.push(new Face3(faces[i][0], faces[i][1], faces[i][2]));
		}

		computeFaceNormals();
	}

	var cb = new Vec4();
	var ab = new Vec4();
	function computeFaceNormals() {
		for (f in 0...face3s.length) {
			var face = face3s[f];
			var va = vertices[face.a];
			var vb = vertices[face.b];
			var vc = vertices[face.c];
			cb.subvecs(vc, vb);
			ab.subvecs(va, vb);
			cb.cross(ab);
			cb.normalize();
			face.normal.setFrom(cb);
		}
	}

	function addPoint(vertexId: Int, vertices: Array<Vec4>) {
		var vertex = vertices[vertexId].clone();

		var mag = vertex.length();
		vertex.x += mag * randomOffset();
		vertex.y += mag * randomOffset();
		vertex.z += mag * randomOffset();

		var hole: Array<Array<Int>> = [];
		var f = 0;
		while (f < faces.length) {
			var face = faces[f];

			// For each face, if the vertex can see it,
			// then we try to add the face's edges into the hole
			if (visible(face, vertex, vertices)) {
				for (e in 0...3) {
					var edge = [face[e], face[(e + 1) % 3]];
					var boundary = true;

					// Remove duplicated edges
					for (h in 0...hole.length) {
						if (equalEdge(hole[h], edge)) {
							hole[h] = hole[hole.length - 1];
							hole.pop();
							boundary = false;
							break;
						}
					}
					if (boundary) hole.push(edge);
				}

				faces[f] = faces[faces.length - 1];
				faces.pop();
			}
			else {
				f++;
			}
		}

		// Construct the new faces formed by the edges of the hole and the vertex
		for (h in 0...hole.length) {
			faces.push([hole[h][0], hole[h][1], vertexId]);
		}
	}

	// Whether the face is visible from the vertex
	function visible(face: Array<Int>, vertex: Vec4, vertices: Array<Vec4>): Bool {
		var va = vertices[face[0]];
		var vb = vertices[face[1]];
		var vc = vertices[face[2]];
		var n = normal(va, vb, vc);
		var dist = n.dot(va); // Distance from face to origin
		return n.dot(vertex) >= dist;
	}

	function normal(va: Vec4, vb: Vec4, vc: Vec4): Vec4 {
		var cb = new Vec4();
		var ab = new Vec4();
		cb.subvecs(vc, vb);
		ab.subvecs(va, vb);
		cb.cross(ab);
		cb.normalize();
		return cb;
	}

	function equalEdge(ea: Array<Int>, eb: Array<Int>): Bool {
		return ea[0] == eb[1] && ea[1] == eb[0];
	}

	function randomOffset(): Float {
		return (Math.random() - 0.5) * 2 * 1e-6;
	}
}

class Face3 {

	public var a: Int;
	public var b: Int;
	public var c: Int;
	public var normal: Vec4;

	public function new(a: Int, b: Int, c: Int) {
		this.a = a;
		this.b = b;
		this.c = c;
		normal = new Vec4();
	}
}
