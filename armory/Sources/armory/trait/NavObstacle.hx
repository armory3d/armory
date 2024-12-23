package armory.trait;

#if arm_navigation
import iron.math.Vec4;
import armory.trait.navigation.Navigation;
#end
import iron.Trait;

class NavObstacle extends Trait {

	#if !arm_navigation
	public function new() { super(); }
	#else

	@prop
	public var radius: Float = 1.0;

	@prop
	public var height: Float = 1.0;

	var obstacleID: Int = -1;

	public var obstacleReady (default, null) = false;

	var activeNavMesh: NavMesh = null;

	var initialPosition: Vec4 = new Vec4();

	public function new() {
		super();
		notifyOnUpdate(addObstacle);
		notifyOnRemove(removeObstacle);
	}

	function addObstacle() {

		if(Navigation.active.navMeshes.length < 1) return;

		if(! Navigation.active.navMeshes[0].ready) return;

		activeNavMesh = Navigation.active.navMeshes[0];

		initialPosition = object.transform.world.getLoc();
		obstacleID = activeNavMesh.addCylinderObstacle(this, initialPosition, radius, height);

		notifyOnUpdate(updateObstaclePosition);
		removeUpdate(addObstacle);
		obstacleReady = true;
	}

	function removeObstacle() {
		activeNavMesh.removeTempObstacle(obstacleID);
	}

	function updateObstaclePosition() {
		object.transform.loc.setFrom(initialPosition);
		object.transform.buildMatrix();
	}
	#end
}