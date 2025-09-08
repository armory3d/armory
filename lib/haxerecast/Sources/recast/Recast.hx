// Recast Navigation for Haxe
// https://github.com/recastnavigation/recastnavigation

package recast;

#if hl
typedef Recast = haxe.macro.MacroType<[webidl.Module.build({ idlFile : "Sources/recast/recast.idl", autoGC : false, nativeLib : "recast" })]>;
#else

@:native('Recast.rcConfig')
extern class RcConfig {
	public function new():Void;

	/// The width of the field along the x-axis. [Limit: >= 0] [Units: vx]
	public var width:Int;

	/// The height of the field along the z-axis. [Limit: >= 0] [Units: vx]
	public var height:Int;
	
	/// The width/height size of tile's on the xz-plane. [Limit: >= 0] [Units: vx]
	public var tileSize:Int;
	
	/// The size of the non-navigable border around the heightfield. [Limit: >=0] [Units: vx]
	public var borderSize:Int;

	/// The xz-plane cell size to use for fields. [Limit: > 0] [Units: wu] 
	public var cs:Float;

	/// The y-axis cell size to use for fields. [Limit: > 0] [Units: wu]
	public var ch:Float;

	/// The minimum bounds of the field's AABB. [(x, y, z)] [Units: wu]
	//public var bmin:haxe.ds.Vector<Float>; 

	/// The maximum bounds of the field's AABB. [(x, y, z)] [Units: wu]
	//public var bmax:haxe.ds.Vector<Float>;

	/// The maximum slope that is considered walkable. [Limits: 0 <= value < 90] [Units: Degrees] 
	public var walkableSlopeAngle:Float;

	/// Minimum floor to 'ceiling' height that will still allow the floor area to 
	/// be considered walkable. [Limit: >= 3] [Units: vx] 
	public var walkableHeight:Int;
	
	/// Maximum ledge height that is considered to still be traversable. [Limit: >=0] [Units: vx] 
	public var walkableClimb:Int;
	
	/// The distance to erode/shrink the walkable area of the heightfield away from 
	/// obstructions.  [Limit: >=0] [Units: vx] 
	public var walkableRadius:Int;
	
	/// The maximum allowed length for contour edges along the border of the mesh. [Limit: >=0] [Units: vx] 
	public var maxEdgeLen:Int;
	
	/// The maximum distance a simplfied contour's border edges should deviate 
	/// the original raw contour. [Limit: >=0] [Units: vx]
	public var maxSimplificationError:Float;
	
	/// The minimum number of cells allowed to form isolated island areas. [Limit: >=0] [Units: vx] 
	public var minRegionArea:Int;
	
	/// Any regions with a span count smaller than this value will, if possible, 
	/// be merged with larger regions. [Limit: >=0] [Units: vx] 
	public var mergeRegionArea:Int;
	
	/// The maximum number of vertices allowed for polygons generated during the 
	/// contour to polygon conversion process. [Limit: >= 3] 
	public var maxVertsPerPoly:Int;
	
	/// Sets the sampling distance to use when generating the detail mesh.
	/// (For height detail only.) [Limits: 0 or >= 0.9] [Units: wu] 
	public var detailSampleDist:Float;
	
	/// The maximum distance the detail mesh surface should deviate from heightfield
	/// data. (For height detail only.) [Limit: >=0] [Units: wu] 
	public var detailSampleMaxError:Float;
}

@:native('Recast.Vec3')
extern class Vec3 {
	public function new(x:Float, y:Float, z:Float):Void;
	public var x:Float;
	public var y:Float;
	public var z:Float;
}

@:native('Recast.Triangle')
extern class Triangle {
	public function new():Void;
	public function getPoint(n:Int):Vec3;
}

@:native('Recast.DebugNavMesh')
extern class DebugNavMesh {
	public function new():Void;
	public function getTriangleCount():Int;
	public function getTriangle(n:Int):Triangle;
}

@:native('Recast.dtNavMesh')
extern class DtNavMesh {

}

@:native('Recast.NavmeshData')
extern class NavmeshData {
    public function new():Void;
    public var dataPointer:Dynamic;
    public var size:Int;
}

@:native('Recast.NavPath')
extern class NavPath {
    public function getPointCount():Int;
    public function getPoint(n:Int):Vec3;
}

@:native('Recast.dtObstacleRef')
extern class DtObstacleRef {
	
}

@:native('Recast.dtCrowdAgentParams')
extern class DtCrowdAgentParams {
    public function new():Void;
	///< Agent radius. [Limit: >= 0]
    public var  radius:Float;
	///< Agent height. [Limit: > 0]
    public var  height:Float;
	///< Maximum allowed acceleration. [Limit: >= 0]
    public var  maxAcceleration:Float;
	///< Maximum allowed speed. [Limit: >= 0]
    public var  maxSpeed:Float;

    /// Defines how close a collision element must be before it is considered for steering behaviors. [Limits: > 0]
    public var  collisionQueryRange:Float;

	///< The path visibility optimization range. [Limit: > 0]
    public var  pathOptimizationRange:Float;

    /// How aggresive the agent manager should be at avoiding collisions with this agent. [Limit: >= 0]
    public var  separationWeight:Float;

    /// Flags that impact steering behavior. (See: #UpdateFlags)
    public var updateFlags:Int;

    /// The index of the avoidance configuration to use for the agent. 
    /// [Limits: 0 <= value <= #DT_CROWD_MAX_OBSTAVOIDANCE_PARAMS]
    public var obstacleAvoidanceType:Int;

    /// The index of the query filter used by this agent.
    public var queryFilterType:Int;

    /// User defined data attached to the agent.
    //public var VoidPtr userData;
}

@:native('Recast.NavMesh')
extern class NavMesh {
	public function new():Void;
	public function destroy():Void;
	public function build(positions:haxe.ds.Vector<Float>, positionCount:Int, indices:haxe.ds.Vector<Int>, indexCount:Int, config: RcConfig):Void;
	public function buildFromNavmeshData(data:NavmeshData):Void;
	public function getNavmeshData():NavmeshData;
	public function freeNavmeshData(data:NavmeshData):Void;
	public function getDebugNavMesh():DebugNavMesh;
	public function getClosestPoint(position:Vec3):Vec3;
	public function getRandomPointAround(position:Vec3, maxRadius:Float):Vec3;
	public function moveAlong(position:Vec3, destination:Vec3):Vec3;
	public function getNavMesh():DtNavMesh;
	public function computePath(start:Vec3, end:Vec3):NavPath;
	public function setDefaultQueryExtent(extent:Vec3):Void;
	public function getDefaultQueryExtent():Vec3;
	
	public function addCylinderObstacle(position:Vec3, radius:Float, height:Float):DtObstacleRef;
	public function addBoxObstacle(position:Vec3, extent:Vec3, angle:Float):DtObstacleRef;
	public function removeObstacle(obstacle:DtObstacleRef):Void;
	public function update():Void;
}

@:native('Recast.Crowd')
extern class Crowd {
    public function new(maxAgents:Int, maxAgentRadius:Float, nav:DtNavMesh);
    public function destroy():Void;
    public function addAgent(position:Vec3, params:DtCrowdAgentParams):Int;
    public function removeAgent(idx:Int):Void;
    public function update(dt:Float):Void;
    public function getAgentVelocity(idx:Int):Vec3;
    public function getAgentNextTargetPath(idx:Int):Vec3;
    public function getAgentPosition(idx:Int):Vec3;
    public function getAgentState(idx:Int):Int;
    public function overOffmeshConnection(idx:Int):Bool;
    public function agentGoto(idx:Int, destination:Vec3):Void;
    public function agentTeleport(idx:Int, destination:Vec3):Void;
    public function getAgentParameters(idx:Int):DtCrowdAgentParams;
    public function setAgentParameters(idx:Int, params:DtCrowdAgentParams):Void;
    public function setDefaultQueryExtent(extent:Vec3):Void;
    public function getDefaultQueryExtent():Vec3;
    public function getCorners(idx:Int):NavPath;
}

@:native('Recast.RecastConfigHelper')
extern class RecastConfigHelper {
	public function new():Void;
	public function setBMAX(config:RcConfig, x: Float, y:Float, z:Float):Void;
	public function getBMAX(config:RcConfig):Vec3;
	public function setBMIN(config:RcConfig, x: Float, y:Float, z:Float):Void;
	public function getBMIN(config:RcConfig):Vec3;
}

@:native('Recast.rcIntArray')
extern class RcIntArray {
	public function new(num:Int):Void;
	public function get_raw():Dynamic;
	public function size():Int;
	public function at(n:Int):Int;
	public function set(n:Int, value:Int):Void;
}

@:native('Recast.rcFloatArray')
extern class RcFloatArray {
	public function new(num:Int):Void;
	public function get_raw():Dynamic;
	public function set_raw(raw:Dynamic):Void;
	public function size():Int;
	public function at(n:Int):Float;
	public function set(n:Int, value:Float):Void;
}

#end