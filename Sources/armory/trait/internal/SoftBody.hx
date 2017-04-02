package armory.trait.internal;

import iron.math.Vec4;
import iron.math.Mat4;
import iron.Trait;
import iron.object.MeshObject;
import iron.data.MeshData;
import iron.data.SceneFormat;
#if arm_physics_soft
import armory.trait.internal.RigidBody;
import armory.trait.internal.PhysicsWorld;
import haxebullet.Bullet;
#end

@:keep
class SoftBody extends Trait {
#if (!arm_physics_soft)
	public function new() { super(); }
#else

	static var physics:PhysicsWorld = null;

	public var ready = false;
	var shape:SoftShape;
	var bend:Float;
	var mass:Float;
	var margin:Float;

	public var vertOffsetX = 0.0;
	public var vertOffsetY = 0.0;
	public var vertOffsetZ = 0.0;

	public var body:BtSoftBodyPointer;

	public function new(shape = SoftShape.Cloth, bend = 0.5, mass = 1.0, margin = 0.04) {
		super();
		this.shape = shape;
		this.bend = bend;
		this.mass = mass;
		this.margin = margin;

		Scene.active.notifyOnInit(function() {
			notifyOnInit(init);
		});
	}

	function init() {
		if (ready) return;
		ready = true;

		if (physics == null) physics = armory.trait.internal.PhysicsWorld.active;

		var softBodyHelpers = BtSoftBodyHelpers.create();
		var mo = cast(object, MeshObject);
		mo.frustumCulling = false;
		var mesh = mo.data.mesh;

		// Parented soft body - clear parent location
		if (object.parent != null && object.parent.name != "") {
			object.transform.loc.x += object.parent.transform.absx();
			object.transform.loc.y += object.parent.transform.absy();
			object.transform.loc.z += object.parent.transform.absz();
			object.transform.localOnly = true;
			object.transform.buildMatrix();
		}

		var positions:haxe.ds.Vector<kha.FastFloat> = cast haxe.ds.Vector.fromData(mesh.positions.copy());
		for (i in 0...Std.int(positions.length / 3)) {
			positions[i * 3] *= object.transform.scale.x;
			positions[i * 3 + 1] *= object.transform.scale.y;
			positions[i * 3 + 2] *= object.transform.scale.z;
			positions[i * 3] += object.transform.absx();
			positions[i * 3 + 1] += object.transform.absy();
			positions[i * 3 + 2] += object.transform.absz();
		}
		vertOffsetX = object.transform.absx();
		vertOffsetY = object.transform.absy();
		vertOffsetZ = object.transform.absz();

		object.transform.scale.set(1, 1, 1);
		object.transform.loc.set(0, 0, 0);
		object.transform.buildMatrix();

		var wrdinfo = physics.world.getWorldInfo();
		var vecind = haxe.ds.Vector.fromData(mesh.indices[0]);
		var numtri = Std.int(mesh.indices[0].length / 3);
#if js
		body = softBodyHelpers.CreateFromTriMesh(wrdinfo, positions, vecind, numtri);
#elseif cpp
		untyped __cpp__("body = softBodyHelpers.CreateFromTriMesh(wrdinfo, positions->Pointer(), vecind->Pointer(), numtri);");
#end

		// body.generateClusters(4);
#if js
		var cfg = body.get_m_cfg();
		cfg.set_viterations(10);
		cfg.set_piterations(10);
		// cfg.set_collisions(0x0001 + 0x0020 + 0x0040); // self collision
		// cfg.set_collisions(0x11); // Soft-rigid, soft-soft

		if (shape == SoftShape.Volume) {
			cfg.set_kDF(0.1);
			cfg.set_kDP(0.01);
			cfg.set_kPR(bend);
		}
#elseif cpp
		var cfg = body.m_cfg;
		cfg.viterations = 10;
		cfg.piterations = 10;
		// cfg.collisions = 0x0001 + 0x0020 + 0x0040;

		if (shape == SoftShape.Volume) {
			cfg.kDF = 0.1;
			cfg.kDP = 0.01;
			cfg.kPR = bend;
		}
#end
		body.setTotalMass(mass, false);
		
		body.getCollisionShape().setMargin(margin);

		physics.world.addSoftBody(body, 1, -1);
		body.setActivationState(BtCollisionObject.DISABLE_DEACTIVATION);

		notifyOnUpdate(update);
	}

	var va = new Vec4();
	var vb = new Vec4();
	var vc = new Vec4();
	var cb = new Vec4();
	var ab = new Vec4();
	function update() {
		var mesh = cast(object, MeshObject).data.mesh;
		
		var v = mesh.vertexBuffer.lock();
		var l = mesh.structLength;
		var numVerts = Std.int(v.length / l);

#if js
		var nodes = body.get_m_nodes();
#elseif cpp
		var nodes = body.m_nodes;
#end

		for (i in 0...numVerts) {
			var node = nodes.at(i);
			#if js
			var nodePos = node.get_m_x();
			var nodeNor = node.get_m_n();
			#elseif cpp
			var nodePos = node.m_x;
			var nodeNor = node.m_n;
			#end
			v.set(i * l, nodePos.x());
			v.set(i * l + 1, nodePos.y());
			v.set(i * l + 2, nodePos.z());
			v.set(i * l + 3, nodeNor.x());
			v.set(i * l + 4, nodeNor.y());
			v.set(i * l + 5, nodeNor.z());
		}
		// for (i in 0...Std.int(mesh.indices[0].length / 3)) {
		// 	var a = mesh.indices[0][i * 3];
		// 	var b = mesh.indices[0][i * 3 + 1];
		// 	var c = mesh.indices[0][i * 3 + 2];
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
		mesh.vertexBuffer.unlock();
	}

#end
}

@:enum abstract SoftShape(Int) from Int {
	var Cloth = 0;
	var Volume = 1;
}
