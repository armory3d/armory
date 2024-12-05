package armory.trait;

import iron.Trait;
import iron.object.Object;
import iron.object.CameraObject;
import iron.object.Transform;
import iron.system.Time;
import armory.trait.physics.PhysicsWorld;

class VehicleBody extends Trait {

#if (!arm_bullet)
	public function new() { super(); }
#else

	@prop var wheel0Name: String = "Wheel0";
	@prop var wheel1Name: String = "Wheel1";
	@prop var wheel2Name: String = "Wheel2";
	@prop var wheel3Name: String = "Wheel3";

	var physics: PhysicsWorld;
	var transform: Transform;
	var camera: CameraObject;

	var wheels: Array<Object> = [];
	var vehicle: bullet.Bt.RaycastVehicle = null;
	var carChassis: bullet.Bt.RigidBody;

	var chassis_mass = 600.0;
	var wheelFriction = 1000;
	var suspensionStiffness = 20.0;
	var suspensionDamping = 2.3;
	var suspensionCompression = 4.4;
	var suspensionRestLength = 0.3;
	var rollInfluence = 0.1;

	var maxEngineForce = 3000.0;
	var maxBreakingForce = 500.0;

	var engineForce = 0.0;
	var breakingForce = 0.0;
	var vehicleSteering = 0.0;

	public function new() {
		super();
		iron.Scene.active.notifyOnInit(init);
	}

	function init() {
		physics = armory.trait.physics.PhysicsWorld.active;
		transform = object.transform;
		camera = iron.Scene.active.camera;

		for (n in [wheel0Name, wheel1Name, wheel2Name, wheel3Name]) {
			wheels.push(iron.Scene.active.root.getChild(n));
		}

		var wheelDirectionCS0 = new bullet.Bt.Vector3(0, 0, -1);
		var wheelAxleCS = new bullet.Bt.Vector3(1, 0, 0);

		var chassisShape = new bullet.Bt.BoxShape(new bullet.Bt.Vector3(
				transform.dim.x / 2,
				transform.dim.y / 2,
				transform.dim.z / 2));

		var compound = new bullet.Bt.CompoundShape();

		var localTrans = new bullet.Bt.Transform();
		localTrans.setIdentity();
		localTrans.setOrigin(new bullet.Bt.Vector3(0, 0, 1));

		compound.addChildShape(localTrans, chassisShape);

		carChassis = createRigidBody(chassis_mass, compound);

		// Create vehicle
		var tuning = new bullet.Bt.VehicleTuning();
		var vehicleRayCaster = new bullet.Bt.DefaultVehicleRaycaster(physics.world);
		vehicle = new bullet.Bt.RaycastVehicle(tuning, carChassis, vehicleRayCaster);

		// Never deactivate the vehicle
		carChassis.setActivationState(bullet.Bt.CollisionObjectActivationState.DISABLE_DEACTIVATION);

		// Choose coordinate system
		var rightIndex = 0;
		var upIndex = 2;
		var forwardIndex = 1;
		vehicle.setCoordinateSystem(rightIndex, upIndex, forwardIndex);

		// Add wheels
		for (i in 0...wheels.length) {
			var vehicleWheel = new VehicleWheel(i, wheels[i].transform, object.transform);
			vehicle.addWheel(
					vehicleWheel.getConnectionPoint(),
					wheelDirectionCS0,
					wheelAxleCS,
					suspensionRestLength,
					vehicleWheel.wheelRadius,
					tuning,
					vehicleWheel.isFrontWheel);
		}

		// Setup wheels
		for (i in 0...vehicle.getNumWheels()){
			var wheel = vehicle.getWheelInfo(i);
			wheel.m_suspensionStiffness = suspensionStiffness;
			wheel.m_wheelsDampingRelaxation = suspensionDamping;
			wheel.m_wheelsDampingCompression = suspensionCompression;
			wheel.m_frictionSlip = wheelFriction;
			wheel.m_rollInfluence = rollInfluence;
		}

		physics.world.addAction(vehicle);

		notifyOnUpdate(update);
	}

	function update() {
		if (vehicle == null) return;

		var keyboard = iron.system.Input.getKeyboard();
		var forward = keyboard.down(keyUp);
		var backward = keyboard.down(keyDown);
		var left = keyboard.down(keyLeft);
		var right = keyboard.down(keyRight);
		var brake = keyboard.down("space");

		if (forward) {
			engineForce = maxEngineForce;
		}
		else if (backward) {
			engineForce = -maxEngineForce;
		}
		else if (brake) {
			breakingForce = 100;
		}
		else {
			engineForce = 0;
			breakingForce = 20;
		}

		if (left) {
			if (vehicleSteering < 0.3) vehicleSteering += Time.step;
		}
		else if (right) {
			if (vehicleSteering > -0.3) vehicleSteering -= Time.step;
		}
		else if (vehicleSteering != 0) {
			var step = Math.abs(vehicleSteering) < Time.step ? Math.abs(vehicleSteering) : Time.step;
			if (vehicleSteering > 0) vehicleSteering -= step;
			else vehicleSteering += step;
		}

		vehicle.applyEngineForce(engineForce, 2);
		vehicle.setBrake(breakingForce, 2);
		vehicle.applyEngineForce(engineForce, 3);
		vehicle.setBrake(breakingForce, 3);
		vehicle.setSteeringValue(vehicleSteering, 0);
		vehicle.setSteeringValue(vehicleSteering, 1);

		for (i in 0...vehicle.getNumWheels()) {
			// Synchronize the wheels with the chassis worldtransform
			vehicle.updateWheelTransform(i, true);

			// Update wheels transforms
			var trans = vehicle.getWheelTransformWS(i);
			var p = trans.getOrigin();
			var q = trans.getRotation();
			wheels[i].transform.localOnly = true;
			wheels[i].transform.loc.set(p.x(), p.y(), p.z());
			wheels[i].transform.rot.set(q.x(), q.y(), q.z(), q.w());
			wheels[i].transform.dirty = true;
		}

		var trans = carChassis.getWorldTransform();
		var p = trans.getOrigin();
		var q = trans.getRotation();
		transform.loc.set(p.x(), p.y(), p.z());
		transform.rot.set(q.x(), q.y(), q.z(), q.w());
		var up = transform.world.up();
		transform.loc.add(up);
		transform.dirty = true;

		// TODO: fix parent matrix update
		if (camera.parent != null) camera.parent.transform.buildMatrix();
		camera.buildMatrix();
	}

	function createRigidBody(mass: Float, shape: bullet.Bt.CompoundShape): bullet.Bt.RigidBody {

		var localInertia = new bullet.Bt.Vector3(0, 0, 0);
		shape.calculateLocalInertia(mass, localInertia);

		var centerOfMassOffset = new bullet.Bt.Transform();
		centerOfMassOffset.setIdentity();

		var startTransform = new bullet.Bt.Transform();
		startTransform.setIdentity();
		startTransform.setOrigin(new bullet.Bt.Vector3(
			transform.loc.x,
			transform.loc.y,
			transform.loc.z));
		startTransform.setRotation(new bullet.Bt.Quaternion(
			transform.rot.x,
			transform.rot.y,
			transform.rot.z,
			transform.rot.w));

		var myMotionState = new bullet.Bt.DefaultMotionState(startTransform, centerOfMassOffset);
		var cInfo = new bullet.Bt.RigidBodyConstructionInfo(mass, myMotionState, shape, localInertia);

		var body = new bullet.Bt.RigidBody(cInfo);
		body.setLinearVelocity(new bullet.Bt.Vector3(0, 0, 0));
		body.setAngularVelocity(new bullet.Bt.Vector3(0, 0, 0));
		physics.world.addRigidBody(body);

		return body;
	}

	#if arm_azerty
	static inline var keyUp = "z";
	static inline var keyDown = "s";
	static inline var keyLeft = "q";
	static inline var keyRight = "d";
	static inline var keyStrafeUp = "e";
	static inline var keyStrafeDown = "a";
	#else
	static inline var keyUp = "w";
	static inline var keyDown = "s";
	static inline var keyLeft = "a";
	static inline var keyRight = "d";
	static inline var keyStrafeUp = "e";
	static inline var keyStrafeDown = "q";
	#end
#end
}

class VehicleWheel {

#if (!arm_bullet)
	public function new() {}
#else

	public var isFrontWheel: Bool;
	public var wheelRadius: Float;
	public var wheelWidth: Float;

	var locX: Float;
	var locY: Float;
	var locZ: Float;

	public function new(id: Int, transform: Transform, vehicleTransform: Transform) {
		wheelRadius = transform.dim.z / 2;
		wheelWidth = transform.dim.x > transform.dim.y ? transform.dim.y : transform.dim.x;

		locX = transform.loc.x;
		locY = transform.loc.y;
		locZ = vehicleTransform.dim.z / 2 + transform.loc.z;
	}

	public function getConnectionPoint(): bullet.Bt.Vector3 {
		return new bullet.Bt.Vector3(locX, locY, locZ);
	}
#end
}
