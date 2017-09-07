package armory.trait;

#if arm_navigation
import armory.trait.internal.Navigation;
import haxerecast.Recast;
#end

import iron.Trait;
import iron.data.Data;
import iron.math.Vec4;

class NavMesh extends Trait {

#if (!arm_navigation)
	public function new() { super(); }
#else

	var recast:Recast = null;
	var ready = false;

	public function new() {
		super();

		notifyOnInit(init);
	}

	function init() {
		Navigation.active.navMeshes.push(this);

		// Load navmesh
		var name = "nav_" + cast(object, iron.object.MeshObject).data.name + ".arm";
		Data.getBlob(name, function(b:kha.Blob) {

			recast = Navigation.active.recast;
			recast.OBJDataLoader(b.toString(), function() {
				recast.buildSolo();
				ready = true;
			});
		});
	}

	public function findPath(from:Vec4, to:Vec4, done:Array<Vec4>->Void) {
		if (!ready) return;
		recast.findPath(from.x, from.z, from.y, to.x, to.z, to.y, 200, function(path:Array<RecastWaypoint>) {
			var ar:Array<Vec4> = [];
			for (p in path) ar.push(new Vec4(p.x, p.z, -p.y));
			done(ar);
		});
	}

	public function getRandomPoint(done:Vec4->Void) {
		if (!ready) return;
		recast.getRandomPoint(function(x:Float, y:Float, z:Float) {
			done(new Vec4(x, z, -y));
		});
	}

#end
}
