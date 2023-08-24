package armory.trait.physics.bullet;

#if arm_bullet
import iron.Scene;
import haxe.ds.Vector;
import kha.arrays.ByteArray;
import bullet.Bt.Vector3;
import bullet.Bt.CollisionObjectActivationState;
import iron.math.Vec4;
import iron.math.Mat4;
import iron.Trait;
import iron.object.MeshObject;
import iron.data.Geometry;
import iron.data.MeshData;
import iron.data.SceneFormat;
import kha.arrays.Uint32Array;
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

	var vertexIndexMap: Map<Int, Array<Int>>;

	public function new(shape = SoftShape.Cloth, bend = 0.5, mass = 1.0, margin = 0.04) {
		super();
		this.shape = shape;
		this.bend = bend;
		this.mass = mass;
		this.margin = margin;

		//notifyOnAdd(init);
		//The above line works as well, but the object transforms are not set
		//properly, so the positions are not accurate
		notifyOnInit(init);
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

	function generateVertexIndexMap(ind: haxe.ds.Vector<Int>, vert: haxe.ds.Vector<Int>) {
		if (vertexIndexMap == null) vertexIndexMap = new Map();
		for (i in 0...ind.length) {
			var currentVertex = vert[i];
			var currentIndex = ind[i];

			var mapping = vertexIndexMap.get(currentVertex);
			if (mapping == null) {
				vertexIndexMap.set(currentVertex, [currentIndex]);
			}
			else {
				if(! mapping.contains(currentIndex)) mapping.push(currentIndex);
			}
		}
	}

	function init() {
		var mo = cast(object, MeshObject);
		//Set new mesh data for this object
		new MeshData(mo.data.raw, function (data) {
			mo.setData(data);
			//Init soft body after setting new data
			initSoftBody();
			//If the above line is commented out, the program becomes unresponsive with white screen
			//and no errors.
		});
	}

	var v = new Vec4();
	function initSoftBody() {
		if (ready) return;
		ready = true;

		if (physics == null) physics = armory.trait.physics.PhysicsWorld.active;

		var mo = cast(object, MeshObject);
		mo.frustumCulling = false;
		var geom = mo.data.geom;
		var rawData = mo.data.raw;
		var vertexMap: Array<Uint32Array> = [];
		for (ind in rawData.index_arrays) {
			if (ind.vertex_map == null) return;
			vertexMap.push(ind.vertex_map);
		}

		var vecind = fromU32(geom.indices);
		var vertexMapArray = fromU32(vertexMap);

		generateVertexIndexMap(vecind, vertexMapArray);

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

		var numtri = 0;
		for (ar in geom.indices) numtri += Std.int(ar.length / 3);

		if (!helpersCreated) {
			helpers = new bullet.Bt.SoftBodyHelpers();
			worldInfo = physics.world.getWorldInfo();
			helpersCreated = true;
			#if hl
			//world info is passed as value and not as a reference, need to set gravity again in HL.
			worldInfo.m_gravity = physics.world.getGravity();
			#end
		}

		var vertsLength = 0;
		for (key in vertexIndexMap.keys()) vertsLength++;
		var positionsVector: haxe.ds.Vector<Float> = new haxe.ds.Vector<Float>(vertsLength * 3);
		for (key in 0...vertsLength){
			var i = vertexIndexMap.get(key)[0];
			positionsVector.set(key * 3    , positions[i * 3    ]);
			positionsVector.set(key * 3 + 1, positions[i * 3 + 1]);
			positionsVector.set(key * 3 + 2, positions[i * 3 + 2]);
		}

		var indexMax: Int = 0;
		var vecindVector: haxe.ds.Vector<Int> = new haxe.ds.Vector<Int>(vertexMapArray.length);
		for (i in 0...vecindVector.length){
			var idx = vertexMapArray.get(i);
			vecindVector.set(i, idx);
			indexMax = indexMax > idx ? indexMax : idx;
		}

		#if js
		body = helpers.CreateFromTriMesh(worldInfo, positionsVector, vecindVector, numtri);
		#else
		//Create helper float array
		var floatArray = new bullet.Bt.FloatArray(positionsVector.length);
		for (i in 0...positionsVector.length){
			floatArray.set(i, positionsVector[i]);
		}
		//Create helper int array
		var intArray = new bullet.Bt.IntArray(vecindVector.length);
		for (i in 0...vecindVector.length){
			intArray.set(i, vecindVector[i]);
		}
		//Create soft body
		body = helpers.CreateFromTriMesh(worldInfo, floatArray.raw, intArray.raw, numtri, false);

		floatArray.delete();
		intArray.delete();
		#end
		// body.generateClusters(4);

		#if js
		var cfg = body.get_m_cfg();
		cfg.set_viterations(physics.solverIterations);
		cfg.set_piterations(physics.solverIterations);
		// cfg.set_collisions(0x0001 + 0x0020 + 0x0040); // self collision
		cfg.set_collisions(0x11); // Soft-rigid, soft-soft
		if (shape == SoftShape.Volume) {
			cfg.set_kDF(0.1);
			cfg.set_kDP(0.01);
			cfg.set_kPR(bend);
		}
		#else
		//Not passed as refernece
		var cfg = body.m_cfg;
		cfg.viterations = physics.solverIterations;
		cfg.piterations = physics.solverIterations;
		// body.m_cfg.collisions = 0x0001 + 0x0020 + 0x0040;
		cfg.collisions = 0x11; // Soft-rigid, soft-soft
		if (shape == SoftShape.Volume) {
			cfg.kDF = 0.1;
			cfg.kDP = 0.01;
			cfg.kPR = bend;
		}
		//Set config again in HL
		body.m_cfg = cfg;
		#end

		body.setTotalMass(mass, false);
		body.getCollisionShape().setMargin(margin);

		physics.world.addSoftBody(body, 1, -1);
		body.setActivationState(CollisionObjectActivationState.DISABLE_DEACTIVATION);

		#if hl
		cfg.delete();
		#end

		notifyOnRemove(removeFromWorld);
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
		var v: ByteArray = geom.vertexBuffers[0].buffer.lock();
		var n: ByteArray = geom.vertexBuffers[1].buffer.lock();
		#else
		var v:ByteArray = geom.vertexBuffer.lock();
		var vbPos = geom.vertexBufferMap.get("pos");
		var v2 = vbPos != null ? vbPos.lock() : null; // For shadows
		var l = geom.structLength;
		#end

		#if js
		var nodes = body.get_m_nodes();
		#else
		var nodes = body.m_nodes;
		#end
		var numNodes = nodes.size();

		//Finding the mean position of vertices in world space
		vertOffsetX = 0.0;
		vertOffsetY = 0.0;
		vertOffsetZ = 0.0;
		for (i in 0...numNodes) {
			var node = nodes.at(i);
			#if js
			var nodePos = node.get_m_x();
			#else
			var nodePos = node.m_x;
			#end
			var mx = nodePos.x();
			var my = nodePos.y();
			var mz = nodePos.z();
			vertOffsetX += mx;
			vertOffsetY += my;
			vertOffsetZ += mz;

			#if hl
			node.delete();
			nodePos.delete();
			#end
		}
		vertOffsetX /= numNodes;
		vertOffsetY /= numNodes;
		vertOffsetZ /= numNodes;
		
		//Setting the mean position as object local location
		mo.transform.scale.set(1, 1, 1);
		mo.transform.loc.set(vertOffsetX, vertOffsetY, vertOffsetZ);
		mo.transform.rot.set(0, 0, 0, 1);

		//Checking maximum dimension for scalePos
		var scalePos = 1.0;
		for (i in 0...numNodes) {
			var node = nodes.at(i);
			#if js
			var nodePos = node.get_m_x();
			#else
			var nodePos = node.m_x;
			#end
			var mx = nodePos.x() - vertOffsetX;
			var my = nodePos.y() - vertOffsetY;
			var mz = nodePos.z() - vertOffsetZ;
			if (Math.abs(mx * 2) > scalePos) scalePos = Math.abs(mx * 2);
			if (Math.abs(my * 2) > scalePos) scalePos = Math.abs(my * 2);
			if (Math.abs(mz * 2) > scalePos) scalePos = Math.abs(mz * 2);

			#if hl
			node.delete();
			nodePos.delete();
			#end
		}
		//Set scalePos and buildMatrix
		mo.data.scalePos = scalePos;
		mo.transform.scaleWorld = scalePos;
		mo.transform.buildMatrix();

		//Set vertices with location offset
		for (i in 0...nodes.size()) {
			var node = nodes.at(i);
			var indices = vertexIndexMap.get(i);
			#if js
			var nodePos = node.get_m_x();
			var nodeNor = node.get_m_n();
			#else
			var nodePos = node.m_x;
			var nodeNor = node.m_n;
			#end
			var mx = nodePos.x() - vertOffsetX;
			var my = nodePos.y() - vertOffsetY;
			var mz = nodePos.z() - vertOffsetZ;
			
			var nx = nodeNor.x();
			var ny = nodeNor.y();
			var nz = nodeNor.z();

			for (idx in indices){
				#if arm_deinterleaved
				v.setInt16(idx * 8    , Std.int(mx * 32767 * (1 / scalePos)));
				v.setInt16(idx * 8 + 2, Std.int(my * 32767 * (1 / scalePos)));
				v.setInt16(idx * 8 + 4, Std.int(mz * 32767 * (1 / scalePos)));
				n.setInt16(idx * 4    , Std.int(nx * 32767));
				n.setInt16(idx * 4 + 2, Std.int(ny * 32767));
				v.setInt16(idx * 8 + 6, Std.int(nz * 32767));
				#else
				var vertIndex = idx * l * 2;
				v.setInt16(vertIndex    , Std.int(mx * 32767 * (1 / scalePos)));
				v.setInt16(vertIndex + 2, Std.int(my * 32767 * (1 / scalePos)));
				v.setInt16(vertIndex + 4, Std.int(mz * 32767 * (1 / scalePos)));
				if (vbPos != null) {
					v2.setInt16(idx * 8    , v.getInt16(vertIndex    ));
					v2.setInt16(idx * 8 + 2, v.getInt16(vertIndex + 2));
					v2.setInt16(idx * 8 + 4, v.getInt16(vertIndex + 4));
				}
				v.setInt16(vertIndex + 6,  Std.int(nx * 32767));
				v.setInt16(vertIndex + 8,  Std.int(ny * 32767));
				v.setInt16(vertIndex + 10, Std.int(nz * 32767));
				#end
			}

			#if hl
			node.delete();
			nodePos.delete();
			nodeNor.delete();
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
		geom.vertexBuffers[0].buffer.unlock();
		geom.vertexBuffers[1].buffer.unlock();
		#else
		geom.vertexBuffer.unlock();
		if (vbPos != null) vbPos.unlock();
		#end
		#if hl
		nodes.delete();
		#end
	}

	function removeFromWorld() {
		physics.world.removeSoftBody(body);
		#if js
		bullet.Bt.Ammo.destroy(body);
		#else
		body.delete();
		#end
	}

#end
}

@:enum abstract SoftShape(Int) from Int {
	var Cloth = 0;
	var Volume = 1;
}

#end
