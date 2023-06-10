package armory.trait.physics.bullet;

import kha.arrays.ByteArray;
#if arm_bullet

import iron.math.Vec4;
import iron.math.Mat4;
import iron.Trait;
import iron.object.MeshObject;
import iron.data.Geometry;
import iron.data.MeshData;
import iron.data.SceneFormat;
#if arm_physics_soft
import armory.trait.physics.RigidBody;
import armory.trait.physics.PhysicsWorld;
#end

class SoftBody extends Trait {
#if (!arm_physics_soft)
	public function new() { super(); }
#else

	static var physics: PhysicsWorld = null;

	public var ready = false;
	var shape: SoftShape;
	var bend: Float;
	var mass: Float;
	var margin: Float;

	public var vertOffsetX = 0.0;
	public var vertOffsetY = 0.0;
	public var vertOffsetZ = 0.0;

	public var body: bullet.Bt.SoftBody;

	static var helpers: bullet.Bt.SoftBodyHelpers;
	static var helpersCreated = false;
	static var worldInfo: bullet.Bt.SoftBodyWorldInfo;

	public function new(shape = SoftShape.Cloth, bend = 0.5, mass = 1.0, margin = 0.04) {
		super();
		this.shape = shape;
		this.bend = bend;
		this.mass = mass;
		this.margin = margin;

		iron.Scene.active.notifyOnInit(function() {
			notifyOnInit(init);
		});
	}

	function fromI16(ar: kha.arrays.Int16Array, scalePos: Float): haxe.ds.Vector<Float> {
		var vals = new haxe.ds.Vector<Float>(Std.int(ar.length / 4) * 3);
		for (i in 0...Std.int(vals.length / 3)) {
			vals[i * 3    ] = (ar[i * 4    ] / 32767) * scalePos;
			vals[i * 3 + 1] = (ar[i * 4 + 1] / 32767) * scalePos;
			vals[i * 3 + 2] = (ar[i * 4 + 2] / 32767) * scalePos;
		}
		return vals;
	}

	function fromU32(ars: Array<kha.arrays.Uint32Array>): haxe.ds.Vector<Int> {
		var len = 0;
		for (ar in ars) len += ar.length;
		var vals = new haxe.ds.Vector<Int>(len);
		var i = 0;
		for (ar in ars) {
			for (j in 0...ar.length) {
				vals[i] = ar[j];
				i++;
			}
		}
		return vals;
	}

	var v = new Vec4();
	function init() {
		if (ready) return;
		ready = true;

		if (physics == null) physics = armory.trait.physics.PhysicsWorld.active;

		var mo = cast(object, MeshObject);
		mo.frustumCulling = false;
		var geom = mo.data.geom;

		// Parented soft body - clear parent location
		if (object.parent != null && object.parent.name != "") {
			object.transform.loc.x += object.parent.transform.worldx();
			object.transform.loc.y += object.parent.transform.worldy();
			object.transform.loc.z += object.parent.transform.worldz();
			object.transform.localOnly = true;
			object.transform.buildMatrix();
		}

		var positions = fromI16(geom.positions.values, mo.data.scalePos);
		for (i in 0...Std.int(positions.length / 3)) {
			v.set(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]);
			v.applyQuat(object.transform.rot);
			v.x *= object.transform.scale.x;
			v.y *= object.transform.scale.y;
			v.z *= object.transform.scale.z;
			v.addf(object.transform.worldx(), object.transform.worldy(), object.transform.worldz());
			positions[i * 3    ] = v.x;
			positions[i * 3 + 1] = v.y;
			positions[i * 3 + 2] = v.z;
		}
		vertOffsetX = object.transform.worldx();
		vertOffsetY = object.transform.worldy();
		vertOffsetZ = object.transform.worldz();

		object.transform.scale.set(1, 1, 1);
		object.transform.loc.set(0, 0, 0);
		object.transform.rot.set(0, 0, 0, 1);
		object.transform.buildMatrix();

		var vecind = fromU32(geom.indices);
		var numtri = 0;
		for (ar in geom.indices) numtri += Std.int(ar.length / 3);

		if (!helpersCreated) {
			helpers = new bullet.Bt.SoftBodyHelpers();
			worldInfo = physics.world.getWorldInfo();
			helpersCreated = true;
		}

		var positionsVector: haxe.ds.Vector<Float> = new haxe.ds.Vector<Float>(positions.length);
		for(i in 0...positions.length){
			positionsVector.set(i, positions.get(i));
		}

		var vecindVector: haxe.ds.Vector<Int> = new haxe.ds.Vector<Int>(vecind.length);
		for(i in 0...vecind.length){
			vecindVector.set(i, vecind.get(i));
		}

		#if js
		body = helpers.CreateFromTriMesh(worldInfo, positions, vecind, numtri);
		#elseif cpp
		untyped __cpp__("body = helpers.CreateFromTriMesh(worldInfo, positions->self.data, (int*)vecind->self.data, numtri);");
		#end

		// body.generateClusters(4);

		#if js
		var cfg = body.get_m_cfg();
		cfg.set_viterations(physics.solverIterations);
		cfg.set_piterations(physics.solverIterations);
		// cfg.set_collisions(0x0001 + 0x0020 + 0x0040); // self collision
		// cfg.set_collisions(0x11); // Soft-rigid, soft-soft
		if (shape == SoftShape.Volume) {
			cfg.set_kDF(0.1);
			cfg.set_kDP(0.01);
			cfg.set_kPR(bend);
		}

		#elseif cpp
		body.m_cfg.viterations = physics.solverIterations;
		body.m_cfg.piterations = physics.solverIterations;
		// body.m_cfg.collisions = 0x0001 + 0x0020 + 0x0040;
		if (shape == SoftShape.Volume) {
			body.m_cfg.kDF = 0.1;
			body.m_cfg.kDP = 0.01;
			body.m_cfg.kPR = bend;
		}
		#end

		body.setTotalMass(mass, false);
		body.getCollisionShape().setMargin(margin);

		physics.world.addSoftBody(body, 1, -1);
		body.setActivationState(bullet.Bt.CollisionObject.DISABLE_DEACTIVATION);

		notifyOnUpdate(update);
	}

	var va = new Vec4();
	var vb = new Vec4();
	var vc = new Vec4();
	var cb = new Vec4();
	var ab = new Vec4();
	function update() {
		var mo = cast(object, MeshObject);
		var geom = mo.data.geom;
		#if arm_deinterleaved
		var v = geom.vertexBuffers[0].lock();
		var n = geom.vertexBuffers[1].lock();
		#else
		var v:ByteArray = geom.vertexBuffer.lock();
		var vbPos = geom.vertexBufferMap.get("pos");
		var v2 = vbPos != null ? vbPos.lock() : null; // For shadows
		var l = geom.structLength;
		#end
		var numVerts = geom.getVerticesCount();

		#if js
		var nodes = body.get_m_nodes();
		#elseif cpp
		var nodes = body.m_nodes;
		#end

		var scalePos = 1.0;
		for (i in 0...numVerts) {
			var node = nodes.at(i);
			#if js
			var nodePos = node.get_m_x();
			#elseif cpp
			var nodePos = node.m_x;
			#end
			if (Math.abs(nodePos.x()) > scalePos) scalePos = Math.abs(nodePos.x());
			if (Math.abs(nodePos.y()) > scalePos) scalePos = Math.abs(nodePos.y());
			if (Math.abs(nodePos.z()) > scalePos) scalePos = Math.abs(nodePos.z());
		}
		mo.data.scalePos = scalePos;
		mo.transform.scaleWorld = scalePos;
		mo.transform.buildMatrix();

		for (i in 0...numVerts) {
			var node = nodes.at(i);
			var vertIndex = i * l * 2;
			#if js
			var nodePos = node.get_m_x();
			var nodeNor = node.get_m_n();
			#elseif cpp
			var nodePos = node.m_x;
			var nodeNor = node.m_n;
			#end
			#if arm_deinterleaved
			v.set(i * 4    , Std.int(nodePos.x() * 32767 * (1 / scalePos)));
			v.set(i * 4 + 1, Std.int(nodePos.y() * 32767 * (1 / scalePos)));
			v.set(i * 4 + 2, Std.int(nodePos.z() * 32767 * (1 / scalePos)));
			n.set(i * 2    , Std.int(nodeNor.x() * 32767));
			n.set(i * 2 + 1, Std.int(nodeNor.y() * 32767));
			v.set(i * 4 + 3, Std.int(nodeNor.z() * 32767));
			#else
			//trace(i);
			v.setInt16(vertIndex        , Std.int(nodePos.x() * 32767 * (1 / scalePos)));
			v.setInt16(vertIndex + 2, Std.int(nodePos.y() * 32767 * (1 / scalePos)));
			v.setInt16(vertIndex + 4, Std.int(nodePos.z() * 32767 * (1 / scalePos)));
			if (vbPos != null) {
				v2.setInt16(i * 8    , v.getInt16(vertIndex    ));
				v2.setInt16(i * 8 + 2, v.getInt16(vertIndex + 2));
				v2.setInt16(i * 8 + 4, v.getInt16(vertIndex + 4));
			}
			v.setInt16(vertIndex + 6, Std.int(nodeNor.z() * 32767));
			v.setInt16(vertIndex + 8, Std.int(nodeNor.x() * 32767));
			v.setInt16(vertIndex + 10, Std.int(nodeNor.y() * 32767));
			#end
		}
		// for (i in 0...Std.int(geom.indices[0].length / 3)) {
		// 	var a = geom.indices[0][i * 3];
		// 	var b = geom.indices[0][i * 3 + 1];
		// 	var c = geom.indices[0][i * 3 + 2];
		// 	va.set(v.get(a * l), v.get(a * l + 1), v.get(a * l + 2));
		// 	vb.set(v.get(b * l), v.get(b * l + 1), v.get(b * l + 2));
		// 	vc.set(v.get(c * l), v.get(c * l + 1), v.get(c * l + 2));
		// 	cb.subvecs(vc, vb);
		// 	ab.subvecs(va, vb);
		// 	cb.cross(ab);
		// 	cb.normalize();
		// 	v.set(a * l + 3, cb.x);
		// 	v.set(a * l + 4, cb.y);
		// 	v.set(a * l + 5, cb.z);
		// 	v.set(b * l + 3, cb.x);
		// 	v.set(b * l + 4, cb.y);
		// 	v.set(b * l + 5, cb.z);
		// 	v.set(c * l + 3, cb.x);
		// 	v.set(c * l + 4, cb.y);
		// 	v.set(c * l + 5, cb.z);
		// }
		#if arm_deinterleaved
		geom.vertexBuffers[0].unlock();
		geom.vertexBuffers[1].unlock();
		#else
		geom.vertexBuffer.unlock();
		if (vbPos != null) vbPos.unlock();
		#end
	}

#end
}

@:enum abstract SoftShape(Int) from Int {
	var Cloth = 0;
	var Volume = 1;
}

#end
