package armory.trait;

import iron.Trait;
import iron.node.Node;
import iron.node.CameraNode;
import iron.node.Transform;
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
	var camera:CameraNode;

	// Wheels
	var wheels:Array<Node> = [];
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
	function onKeyDown(key:kha.Key, char:String) {
		if (key == kha.Key.UP) up = true;
		else if (key == kha.Key.DOWN) down = true;
		else if (key == kha.Key.LEFT) left = true;
		else if (key == kha.Key.RIGHT) right = true;
	}

	function onKeyUp(key:kha.Key, char:String) {
		if (key == kha.Key.UP) up = false;
		else if (key == kha.Key.DOWN) down = false;
		else if (key == kha.Key.LEFT) left = false;
		else if (key == kha.Key.RIGHT) right = false;
	}

    function init() {
    	physics = armory.Root.physics;
    	transform = node.transform;
    	camera = iron.Root.cameras[0];

    	for (n in wheelNames) {
			wheels.push(iron.Root.root.getChild(n));
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
			var vehicleWheel = new VehicleWheel(i, wheels[i].transform, node.transform);
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
		else {
			engineForce = 0;
			breakingForce = 20;
		}

		if (left) {
			vehicleSteering = 0.3;
		}
		else if (right) {
			vehicleSteering = -0.3;
		}
		else {
			vehicleSteering = 0;
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
			wheels[i].transform.pos.set(p.x(), p.y(), p.z());
			wheels[i].transform.rot.set(q.x(), q.y(), q.z(), q.w());
			wheels[i].transform.dirty = true;
		}

		var trans = carChassis.ptr.getWorldTransform();
		var p = trans.getOrigin();
		var q = trans.getRotation();
		transform.pos.set(p.x(), p.y(), p.z());
		transform.rot.set(q.x(), q.y(), q.z(), q.w());
		var up = transform.matrix.up();
		transform.pos.add(up);
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
			transform.pos.x,
			transform.pos.y,
			transform.pos.z).value);
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

	var posX:Float;
	var posY:Float;
	var posZ:Float;

	public function new(id:Int, transform:Transform, vehicleTransform:Transform) {
		wheelRadius = transform.size.z / 2;
		wheelWidth = transform.size.x > transform.size.y ? transform.size.y : transform.size.x;

		posX = transform.pos.x;
		posY = transform.pos.y;
		posZ = vehicleTransform.size.z / 2 + transform.pos.z;
	}

	public function getConnectionPoint():BtVector3 {
		return BtVector3.create(posX, posY, posZ).value;
	}
#end
}
