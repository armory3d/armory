package armory.trait;

import iron.Trait;
import iron.object.Object;
import iron.object.CameraObject;
import iron.object.Transform;
import iron.sys.Time;
import armory.trait.internal.PhysicsWorld;
#if WITH_PHYSICS
import haxebullet.Bullet;
#end

class VehicleBody extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

	var physics:PhysicsWorld;
    var transform:Transform;
	var camera:CameraObject;

	// Wheels
	var wheels:Array<Object> = [];
	var wheelNames:Array<String>;

    var vehicle:BtRaycastVehiclePointer = null;
    var carChassis:BtRigidBodyPointer;
	
	var engineForce = 0.0;
	var breakingForce = 0.0;
	var vehicleSteering = 0.0;

	var maxEngineForce = 3000.0;
	var maxBreakingForce = 100.0;

	public function new(wheelName1:String, wheelName2:String, wheelName3:String, wheelName4:String) {
		super();

		wheelNames = [wheelName1, wheelName2, wheelName3, wheelName4];

		notifyOnInit(init);
		notifyOnUpdate(update);
		
		kha.input.Keyboard.get().notify(onKeyDown, onKeyUp);
	}
	
	var up = false;
	var down = false;
	var left = false;
	var right = false;
	var space = false;
	function onKeyDown(key:kha.Key, char:String) {
		if (key == kha.Key.UP) up = true;
		else if (key == kha.Key.DOWN) down = true;
		else if (key == kha.Key.LEFT) left = true;
		else if (key == kha.Key.RIGHT) right = true;
		else if (char == ' ') space = true;
	}

	function onKeyUp(key:kha.Key, char:String) {
		if (key == kha.Key.UP) up = false;
		else if (key == kha.Key.DOWN) down = false;
		else if (key == kha.Key.LEFT) left = false;
		else if (key == kha.Key.RIGHT) right = false;
		else if (char == ' ') space = false;
	}

    function init() {
    	physics = armory.trait.internal.PhysicsWorld.active;
    	transform = object.transform;
    	camera = iron.Scene.active.camera;

    	for (n in wheelNames) {
			wheels.push(iron.Scene.active.root.getChild(n));
		}

    	var rightIndex = 0; 
		var upIndex = 2; 
		var forwardIndex = 1;

		var wheelDirectionCS0 = BtVector3.create(0, 0, -1).value;
		var wheelAxleCS = BtVector3.create(1, 0, 0).value;

		var wheelFriction = 1000;
		var suspensionStiffness = 20.0;
		var suspensionDamping = 2.3;
		var suspensionCompression = 4.4;
		var suspensionRestLength = 0.6;
		var rollInfluence = 0.1;

		var chassisShape = BtBoxShape.create(BtVector3.create(
				transform.size.x / 2,
				transform.size.y / 2,
				transform.size.z / 2).value);

		var compound = BtCompoundShape.create();
		
		var localTrans = BtTransform.create();
		localTrans.value.setIdentity();
		localTrans.value.setOrigin(BtVector3.create(0, 0, 1).value);

		#if js
		compound.addChildShape(localTrans, chassisShape);
		#elseif cpp
		compound.value.addChildShape(localTrans.value, chassisShape);
		#end

		carChassis = createRigidBody(500, compound);

		// Create vehicle
		var tuning = BtVehicleTuning.create();
		var vehicleRayCaster = BtDefaultVehicleRaycaster.create(physics.world);
		vehicle = BtRaycastVehicle.create(tuning.value, carChassis, vehicleRayCaster);

		// Never deactivate the vehicle
		carChassis.ptr.setActivationState(BtCollisionObject.DISABLE_DEACTIVATION);

		// Choose coordinate system
		vehicle.ptr.setCoordinateSystem(rightIndex, upIndex, forwardIndex);

		// Add wheels
		for (i in 0...wheels.length) {
			var vehicleWheel = new VehicleWheel(i, wheels[i].transform, object.transform);
			vehicle.ptr.addWheel(
					vehicleWheel.getConnectionPoint(),
					wheelDirectionCS0,
					wheelAxleCS,
					suspensionRestLength,
					vehicleWheel.wheelRadius,
					tuning.value,
					vehicleWheel.isFrontWheel);
		}

		// Setup wheels
		for (i in 0...vehicle.ptr.getNumWheels()){
			var wheel = vehicle.ptr.getWheelInfo(i);
			wheel.m_suspensionStiffness = suspensionStiffness;
			wheel.m_wheelsDampingRelaxation = suspensionDamping;
			wheel.m_wheelsDampingCompression = suspensionCompression;
			wheel.m_frictionSlip = wheelFriction;
			wheel.m_rollInfluence = rollInfluence;
		}

		physics.world.ptr.addAction(vehicle);
    }

	function update() {

		if (vehicle == null) return;

		if (up) {
			engineForce = maxEngineForce;
		}
		else if (down) {
			engineForce = -maxEngineForce;
		}
		else if (space) {
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

		vehicle.ptr.applyEngineForce(engineForce, 2);
		vehicle.ptr.setBrake(breakingForce, 2);
		vehicle.ptr.applyEngineForce(engineForce, 3);
		vehicle.ptr.setBrake(breakingForce, 3);
		vehicle.ptr.setSteeringValue(vehicleSteering, 0);
		vehicle.ptr.setSteeringValue(vehicleSteering, 1);

		for (i in 0...vehicle.ptr.getNumWheels()) {
			// Synchronize the wheels with the chassis worldtransform
			vehicle.ptr.updateWheelTransform(i, true);
			
			// Update wheels transforms
			var trans = vehicle.ptr.getWheelTransformWS(i);
			var p = trans.getOrigin();
			var q = trans.getRotation();
			wheels[i].transform.localOnly = true;
			wheels[i].transform.loc.set(p.x(), p.y(), p.z());
			wheels[i].transform.rot.set(q.x(), q.y(), q.z(), q.w());
			wheels[i].transform.dirty = true;
		}

		var trans = carChassis.ptr.getWorldTransform();
		var p = trans.getOrigin();
		var q = trans.getRotation();
		transform.loc.set(p.x(), p.y(), p.z());
		transform.rot.set(q.x(), q.y(), q.z(), q.w());
		var up = transform.matrix.up();
		transform.loc.add(up);
		transform.dirty = true;

		camera.updateMatrix();
	}

	function createRigidBody(mass:Float, shape:BtCompoundShapePointer):BtRigidBodyPointer {
		
		var localInertia = BtVector3.create(0, 0, 0);
		shape.ptr.calculateLocalInertia(mass, localInertia.value);

		var centerOfMassOffset = BtTransform.create();
		centerOfMassOffset.value.setIdentity();
		
		var startTransform = BtTransform.create();
		startTransform.value.setIdentity();
		startTransform.value.setOrigin(BtVector3.create(
			transform.loc.x,
			transform.loc.y,
			transform.loc.z).value);
		startTransform.value.setRotation(BtQuaternion.create(
			transform.rot.x,
			transform.rot.y,
			transform.rot.z,
			transform.rot.w).value);

		var myMotionState = BtDefaultMotionState.create(startTransform.value, centerOfMassOffset.value);
		var cInfo = BtRigidBodyConstructionInfo.create(mass, myMotionState, shape, localInertia.value).value;
			
		var body = BtRigidBody.create(cInfo);
		body.ptr.setLinearVelocity(BtVector3.create(0, 0, 0).value);
		body.ptr.setAngularVelocity(BtVector3.create(0, 0, 0).value);
		physics.world.ptr.addRigidBody(body);

		return body;
	}
#end
}

class VehicleWheel {

#if (!WITH_PHYSICS)
	public function new() { }
#else

	public var isFrontWheel:Bool;
	public var wheelRadius:Float;
	public var wheelWidth:Float;

	var locX:Float;
	var locY:Float;
	var locZ:Float;

	public function new(id:Int, transform:Transform, vehicleTransform:Transform) {
		wheelRadius = transform.size.z / 2;
		wheelWidth = transform.size.x > transform.size.y ? transform.size.y : transform.size.x;

		locX = transform.loc.x;
		locY = transform.loc.y;
		locZ = vehicleTransform.size.z / 2 + transform.loc.z;
	}

	public function getConnectionPoint():BtVector3 {
		return BtVector3.create(locX, locY, locZ).value;
	}
#end
}
