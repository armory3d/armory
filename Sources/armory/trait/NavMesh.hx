package armory.trait;

#if arm_navigation
import recast.Recast.RecastConfigHelper;
import haxe.ds.Vector;
import armory.trait.navigation.DebugDrawHelper;
import kha.arrays.Float32Array;
import iron.object.Object;
import armory.trait.navigation.Navigation;

import iron.data.Data;
import iron.math.Vec4;
import iron.system.Time;
import kha.arrays.Uint32Array;
import iron.object.MeshObject;
import iron.data.Geometry;
import iron.data.MeshData;
#end
import iron.Trait;

class NavMesh extends Trait {

	#if !arm_navigation
	public function new() { super(); }
	#else

	@prop
	public var debugDraw:Bool = false;

	// recast config:
	/// Also use immidiate children for nav mesh construction.
	@prop
	public var combineImmidiateChildren:Bool = true;
	/// The width of the field along the x-axis. [Limit: >= 0] [Units: vx]
	@prop
	public var width:Int = 0;

	/// The height of the field along the z-axis. [Limit: >= 0] [Units: vx]
	@prop
	public var height:Int = 0;

	/// Enable for tiled mesh and using temporary obstacles. `tileSize` will be ignored if set to false.
	@prop
	public var tiledMesh:Bool = true;
	
	/// The width/height size of tile's on the xz-plane. [Limit: >= 0] [Units: vx]
	@prop
	public var tileSize:Int = 50;
	
	/// The size of the non-navigable border around the heightfield. [Limit: >=0] [Units: vx]
	@prop
	public var borderSize:Int = 0;

	/// The xz-plane cell size to use for fields. [Limit: > 0] [Units: wu]
	@prop
	public var cellSize:Float = 0.2;

	/// The y-axis cell size to use for fields. [Limit: > 0] [Units: wu]
	@prop
	public var cellHeight:Float = 0.3;

	/// The minimum bounds of the field's AABB. [(x, y, z)] [Units: wu]
	//public var bmin:haxe.ds.Vector<Float>; 

	/// The maximum bounds of the field's AABB. [(x, y, z)] [Units: wu]
	//public var bmax:haxe.ds.Vector<Float>;

	/// The maximum slope that is considered walkable. [Limits: 0 <= value < 90] [Units: Degrees]
	@prop
	public var walkableSlopeAngle:Float = 45.0;

	/// Minimum floor to 'ceiling' height that will still allow the floor area to 
	/// be considered walkable. [Limit: >= 3] [Units: vx]
	@prop
	public var walkableHeight:Int = 3;
	
	/// Maximum ledge height that is considered to still be traversable. [Limit: >=0] [Units: vx]
	@prop
	public var walkableClimb:Int = 2;
	
	/// The distance to erode/shrink the walkable area of the heightfield away from 
	/// obstructions.  [Limit: >=0] [Units: vx]
	@prop
	public var walkableRadius:Int = 1;
	
	/// The maximum allowed length for contour edges along the border of the mesh. [Limit: >=0] [Units: vx]
	@prop
	public var maxEdgeLen:Int = 12;
	
	/// The maximum distance a simplfied contour's border edges should deviate 
	/// the original raw contour. [Limit: >=0] [Units: vx]
	@prop
	public var maxSimplificationError:Float = 1.3;
	
	/// The minimum number of cells allowed to form isolated island areas. [Limit: >=0] [Units: vx]
	@prop
	public var minRegionArea:Int = 8;
	
	/// Any regions with a span count smaller than this value will, if possible, 
	/// be merged with larger regions. [Limit: >=0] [Units: vx]
	@prop
	public var mergeRegionArea:Int = 20;
	
	/// The maximum number of vertices allowed for polygons generated during the 
	/// contour to polygon conversion process. [Limit: >= 3]
	@prop
	public var maxVertsPerPoly:Int = 6;
	
	/// Sets the sampling distance to use when generating the detail mesh.
	/// (For height detail only.) [Limits: 0 or >= 0.9] [Units: wu]
	@prop
	public var detailSampleDist:Float = 6;
	
	/// The maximum distance the detail mesh surface should deviate from heightfield
	/// data. (For height detail only.) [Limit: >=0] [Units: wu]
	@prop
	public var detailSampleMaxError:Float = 1;

	 // maximum number of crowd agents
	@prop
	public var maxCrowdAgents: Int = 50;

	 // maximum radius of crowd agents
	@prop
	public var maxCrowdAgentRadius: Float = 3.0;

	var recastNavMesh: recast.Recast.NavMesh = null;
	var recastCrowd: recast.Recast.Crowd = null;
	public var ready(default, null) = false;
	
	var crowdAgentMap: Map<Int, NavCrowd> = new Map();

	var tempObstacleCounter = 0;

	var tempObstacleMap: Map<Int, NavObstacle> = new Map();

	var recastObstacleMap: Map<Int, recast.Recast.DtObstacleRef> = new Map();

	public var navMeshDebugColor: kha.Color = Green;

	var v:Vec4 = new Vec4();

	public function new() {
		super();

		notifyOnInit(initNavMesh);
		notifyOnUpdate(updateNavMesh);
	}

	function initNavMesh() {
		if (ready) return;
		Navigation.active.navMeshes.push(this);

		if(debugDraw) Navigation.active.debugDrawHelper.setDebugMode(DrawWireframe);

		recastNavMesh = new recast.Recast.NavMesh();
		var recastConfig = new recast.Recast.RcConfig();

		recastConfig.width = width;
		recastConfig.height = height;
		if(tiledMesh) {
			recastConfig.tileSize = tileSize;
		}
		else {
			recastConfig.tileSize = 0;
		}
		recastConfig.borderSize = borderSize;
		recastConfig.cs = cellSize;
		recastConfig.ch = cellHeight;
		recastConfig.walkableSlopeAngle = walkableSlopeAngle;
		recastConfig.walkableHeight = walkableHeight;
		recastConfig.walkableClimb = walkableClimb;
		recastConfig.walkableRadius = walkableRadius;
		recastConfig.maxEdgeLen = maxEdgeLen;
		recastConfig.maxSimplificationError = maxSimplificationError;
		recastConfig.minRegionArea = minRegionArea;
		recastConfig.mergeRegionArea = mergeRegionArea;
		recastConfig.maxVertsPerPoly = maxVertsPerPoly;
		recastConfig.detailSampleDist = detailSampleDist;
		recastConfig.detailSampleMaxError = detailSampleMaxError;

		var positionsArray = new Array<Float>();
		var indexArray = new Array<Int>();

		var currentIndexOffset = 0;
		var reducedMeshData = getVerticesIndicesFromMesh(object, currentIndexOffset);
		currentIndexOffset = reducedMeshData.maxIndex + 1;
		positionsArray = positionsArray.concat(reducedMeshData.positions.toArray());
		indexArray = indexArray.concat(reducedMeshData.indices.toArray());

		if(combineImmidiateChildren) {
			for(child in object.children) {

				if(child.raw.type != "mesh_object") continue;

				reducedMeshData = getVerticesIndicesFromMesh(child, currentIndexOffset);
				currentIndexOffset = reducedMeshData.maxIndex + 1;

				positionsArray = positionsArray.concat(reducedMeshData.positions.toArray());
				indexArray = indexArray.concat(reducedMeshData.indices.toArray());
			}
		}

		#if js
		var positionsVector = Vector.fromArrayCopy(positionsArray);
		var vecindVector = Vector.fromArrayCopy(indexArray);

		recastNavMesh.build(positionsVector, positionsVector.length, vecindVector, vecindVector.length, recastConfig);
		#else
		var posLength = positionsArray.length;
		var positionsVector = new recast.Recast.RcFloatArray(posLength);
		for(i in 0...posLength) {
			positionsVector.set(i, positionsArray[i]);
		}

		var indexLength = indexArray.length;
		var vecindVector = new recast.Recast.RcIntArray(indexLength);
		for(i in 0...indexLength) {
			vecindVector.set(i, indexArray[i]);
		}

		recastNavMesh.build(positionsVector.raw, posLength, vecindVector.raw, indexLength, recastConfig);
		#end
		notifyOnUpdate(updateNavMesh);
		ready = true;
	}

	public function reconstructNavMesh() {
		removeUpdate(updateNavMesh);
		if(recastCrowd != null) {
			for(agent in crowdAgentMap.keys()) {
				removeCrowdAgent(agent);
			}
			recastCrowd.destroy();
		}
		for(obstacle in tempObstacleMap.keys()) {
			removeTempObstacle(obstacle);
		}
		ready = false;
		initNavMesh();
	}

	public function updateNavMesh() {
		if(!ready) return;
		recastNavMesh.update();
	}

	public function findPath(from: Vec4, to: Vec4, done: Array<Vec4>->Void) {
		if (!ready) return;
		var start = RecastConversions.recastVec3FromVec4(from);
		var end = RecastConversions.recastVec3FromVec4(to);
		var navPath = recastNavMesh.computePath(start, end);

		var pathVec = new Array<Vec4>();
		for(i in 0...navPath.getPointCount()) {
			pathVec.push(RecastConversions.vec4FromRecastVec3(navPath.getPoint(i)));
		}

		done(pathVec);
	}

	public function getRandomPointAround(position: Vec4, radius: Float):Vec4 {
		if (!ready) return null;
		var randomPoint = recastNavMesh.getRandomPointAround(RecastConversions.recastVec3FromVec4(position), radius);
		return RecastConversions.vec4FromRecastVec3(randomPoint);
	}

	public function initCrowd(maxAgents: Int, maxAgentRadius: Float) {
		if (!ready) return;
		recastCrowd = new recast.Recast.Crowd(maxAgents, maxAgentRadius, recastNavMesh.getNavMesh());
		notifyOnUpdate(crowdUpdate);
	}

	public function addCrowdAgent(agent: NavCrowd, position: Vec4, radius: Float, height: Float, maxAcceleration: Float, maxSpeed: Float, updateFlags: Int = 7, separationWeight: Float = 1.0, collisionQueryRange: Float = 1.0): Int {
		if(!ready) return -1;
		if(recastCrowd == null) initCrowd(maxCrowdAgents, maxCrowdAgentRadius);
		var crowdAgentParams = new recast.Recast.DtCrowdAgentParams();
		crowdAgentParams.radius = radius;
		crowdAgentParams.height = height;
		crowdAgentParams.maxAcceleration = maxAcceleration;
		crowdAgentParams.maxSpeed = maxSpeed;
		crowdAgentParams.separationWeight = separationWeight;
		crowdAgentParams.collisionQueryRange = collisionQueryRange;
		crowdAgentParams.updateFlags = updateFlags;
		crowdAgentParams.pathOptimizationRange=0;
		var crowdAgentID = recastCrowd.addAgent(RecastConversions.recastVec3FromVec4(position), crowdAgentParams);
		crowdAgentMap.set(crowdAgentID, agent);
		return crowdAgentID;
	}

	public function removeCrowdAgent(agentID: Int) {
		if(!ready) return;
		if(recastCrowd == null) return;
		crowdAgentMap.remove(agentID);
		recastCrowd.removeAgent(agentID);
	}

	public function crowdUpdate() {
		if(!ready) return;
		if(recastCrowd == null) return;
		recastCrowd.update(Time.delta);
	}

	public function crowdGetAgentPosition(agentID: Int):Vec4 {
		if(!ready) return null;
		if(recastCrowd == null) return null;
		var pos = recastCrowd.getAgentPosition(agentID);
		var armPos = RecastConversions.vec4FromRecastVec3(pos);
		#if hl
		pos.delete();
		#end
		return armPos;
	}

	public function crowdGetAgentVelocity(agentID: Int):Vec4 {
		if(!ready) return null;
		if(recastCrowd == null) return null;
		var vel = recastCrowd.getAgentVelocity(agentID);
		var armVel = RecastConversions.vec4FromRecastVec3(vel);
		#if hl
		vel.delete();
		#end
		return armVel;
	}

	public function crowdAgentGoto(agentID: Int, destination: Vec4) {
		if(!ready) return;
		if(recastCrowd == null) return;
		recastCrowd.agentGoto(agentID, RecastConversions.recastVec3FromVec4(destination));
	}

	public function crowdAgentTeleport(agentID: Int, destination: Vec4) {
		if(!ready) return;
		if(recastCrowd == null) return;
		recastCrowd.agentTeleport(agentID, RecastConversions.recastVec3FromVec4(destination));
	}

	public function addCylinderObstacle(navObstacle: NavObstacle, position: Vec4, radius: Float, height: Float): Int {
		if(!ready) return -1;
		if(!tiledMesh) return -1;
		var pos = RecastConversions.recastVec3FromVec4(position);
		var obstacle = recastNavMesh.addCylinderObstacle(pos, radius, height);
		var obstacleID = tempObstacleCounter;
		tempObstacleMap.set(obstacleID, navObstacle);
		recastObstacleMap.set(obstacleID, obstacle);
		tempObstacleCounter++;
		return obstacleID;
	}

	public function addBoxObstacle(navObstacle: NavObstacle, position: Vec4, dimensions: Vec4, angle: Float): Int {
		if(!ready) return -1;
		if(!tiledMesh) return -1;
		var pos = RecastConversions.recastVec3FromVec4(position);
		var dim = RecastConversions.recastVec3FromVec4(dimensions);
		var obstacle = recastNavMesh.addBoxObstacle(pos, dim, angle);
		var obstacleID = tempObstacleCounter;
		tempObstacleMap.set(obstacleID, navObstacle);
		recastObstacleMap.set(obstacleID, obstacle);
		tempObstacleCounter++;
		return obstacleID;
	}

	public function removeTempObstacle(obstacleID: Int) {
		if(!ready) return;
		if(!tiledMesh) return;
		tempObstacleMap.remove(obstacleID);
		var obstacleRef = recastObstacleMap.get(obstacleID);
		recastNavMesh.removeObstacle(obstacleRef);
		recastObstacleMap.remove(obstacleID);
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

	function generateVertexIndexMap(ind: haxe.ds.Vector<Int>, vert: haxe.ds.Vector<Int>):Map<Int, Array<Int>> {
		var vertexIndexMap = new Map();
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
		return vertexIndexMap;
	}

	function getVerticesIndicesFromMesh(object: Object, indexOffset:Int = 0): MeshData {

		var vertexIndexMap: Map<Int, Array<Int>>;

		var mo = cast(object, MeshObject);
		var geom = mo.data.geom;
		var rawData = mo.data.raw;
		var vertexMap: Array<Uint32Array> = [];
		for (ind in rawData.index_arrays) {
			if (ind.vertex_map == null) return null;
			vertexMap.push(ind.vertex_map);
		}

		var vecind = fromU32(geom.indices);
		var vertexMapArray = fromU32(vertexMap);

		vertexIndexMap = generateVertexIndexMap(vecind, vertexMapArray);

		// Parented object - clear parent location
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


		var vertsLength = 0;
		for (key in vertexIndexMap.keys()) vertsLength++;
		var positionsVector: haxe.ds.Vector<Float> = new haxe.ds.Vector<Float>(vertsLength * 3);
		for (key in 0...vertsLength) {
			var i = vertexIndexMap.get(key)[0];
			// Y and Z are interchanged in Recast
			positionsVector.set(key * 3    , positions[i * 3    ]);
			positionsVector.set(key * 3 + 1, positions[i * 3 + 2]);
			positionsVector.set(key * 3 + 2, positions[i * 3 + 1]);
		}

		var vecindVector: haxe.ds.Vector<Int> = new haxe.ds.Vector<Int>(vertexMapArray.length);
		var maxIndex = 0;
		for (i in 0...vecindVector.length){
			var idx = vertexMapArray.get(i);
			var idxOffset = idx + indexOffset;
			vecindVector.set(i, idxOffset);

			if(maxIndex < idxOffset) maxIndex = idxOffset;
		}

		return { positions: positionsVector, indices: vecindVector, maxIndex: maxIndex};

	}

	public function drawDebugMesh(helper: DebugDrawHelper) {
		var recastDebugNavMesh = recastNavMesh.getDebugNavMesh();
		var triangleCount = recastDebugNavMesh.getTriangleCount();
		for(index in 0...triangleCount) {
			var triangle = recastDebugNavMesh.getTriangle(index);
			var point0 = RecastConversions.vec4FromRecastVec3(triangle.getPoint(0));
			var point1 = RecastConversions.vec4FromRecastVec3(triangle.getPoint(1));
			var point2 = RecastConversions.vec4FromRecastVec3(triangle.getPoint(2));

			helper.drawLine(point0, point1, navMeshDebugColor);
			helper.drawLine(point1, point2, navMeshDebugColor);
			helper.drawLine(point2, point0, navMeshDebugColor);

		}
		#if hl
		recastDebugNavMesh.delete();
		#end
	}
	#end
}

typedef MeshData = {
	var positions: haxe.ds.Vector<Float>;
	var indices: haxe.ds.Vector<Int>;
	var maxIndex:Int;
}
