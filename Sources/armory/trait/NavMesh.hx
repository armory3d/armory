package armory.trait;

#if arm_navigation
import armory.trait.navigation.Navigation;
import haxerecast.Recast;
#end

import iron.Trait;
import iron.data.Data;
import iron.math.Vec4;

class NavMesh extends Trait {

#if (!arm_navigation)
	public function new() { super(); }
#else

	// recast config:
	@prop
	public var cellSize: Float = 0.3; // voxelization cell size 
	@prop
	public var cellHeight: Float = 0.2; // voxelization cell height
	@prop
	public var agentHeight: Float = 2.0; // agent capsule height
	@prop
	public var agentRadius: Float = 0.4; // agent capsule radius
	@prop
	public var agentMaxClimb: Float = 0.9; // how high steps agents can climb, in voxels
	@prop
	public var agentMaxSlope: Float = 45.0; // maximum slope angle, in degrees

	var recast: Recast = null;
	var ready = false;

	public function new() {
		super();

		notifyOnInit(init);
	}

	function init() {
		Navigation.active.navMeshes.push(this);

		// Load navmesh
		var name = "nav_" + cast(object, iron.object.MeshObject).data.name + ".arm";
		Data.getBlob(name, function(b: kha.Blob) {

			recast = Navigation.active.recast;
			recast.OBJDataLoader(b.toString(), function() {
				var settings = [
					"cellSize" => cellSize,
					"cellHeight" => cellHeight,
					"agentHeight" => agentHeight,
					"agentRadius" => agentRadius,
					"agentMaxClimb" => agentMaxClimb,
					"agentMaxSlope" => agentMaxSlope,
				];
				recast.settings(settings);

				recast.buildSolo();
				ready = true;
			});
		});
	}

	public function findPath(from: Vec4, to: Vec4, done: Array<Vec4>->Void) {
		if (!ready) return;
		recast.findPath(from.x, from.z, from.y, to.x, to.z, to.y, 200, function(path: Array<RecastWaypoint>) {
			var ar: Array<Vec4> = [];
			for (p in path) ar.push(new Vec4(p.x, p.z, p.y - cellHeight));
			done(ar);
		});
	}

	public function getRandomPoint(done: Vec4->Void) {
		if (!ready) return;
		recast.getRandomPoint(function(x: Float, y: Float, z: Float) {
			done(new Vec4(x, z, -y));
		});
	}

#end
}
