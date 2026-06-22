# haxebullet

[Bullet 3D Physics](http://bulletphysics.org/) bindings for Haxe.

Based on the webidl approach, works for HL/C & JS:
- https://github.com/ncannasse/webidl
- https://github.com/HeapsIO/bullet
- https://github.com/bulletphysics/bullet3
- https://github.com/kripken/ammo.js

## Usage

[Reference](http://bulletphysics.org/mediawiki-1.5.8/index.php/Hello_World)

In order to get HL/C build to work you need to add `haxebullet/bullet` and `haxebullet/hl` directories into your build process so the compiler is able to find bullet sources.

In order to get JS build to work you need to add `haxebullet/ammo/ammo.js` script either by embedding or including it with a script tag.

``` hx
var collisionConfiguration = new bullet.Bt.DefaultCollisionConfiguration();
var dispatcher = new bullet.Bt.CollisionDispatcher(collisionConfiguration);
var broadphase = new bullet.Bt.DbvtBroadphase();
var solver = new bullet.Bt.SequentialImpulseConstraintSolver();
var dynamicsWorld = new bullet.Bt.DiscreteDynamicsWorld(dispatcher, broadphase, solver, collisionConfiguration);

var groundShape = new bullet.Bt.StaticPlaneShape(new bullet.Bt.Vector3(0, 1, 0), 1);
var groundTransform = new bullet.Bt.Transform();
groundTransform.setIdentity();
groundTransform.setOrigin(new bullet.Bt.Vector3(0, -1, 0));
var centerOfMassOffsetTransform = new bullet.Bt.Transform();
centerOfMassOffsetTransform.setIdentity();
var groundMotionState = new bullet.Bt.DefaultMotionState(groundTransform, centerOfMassOffsetTransform);

var groundRigidBodyCI = new bullet.Bt.RigidBodyConstructionInfo(0.01, groundMotionState, cast groundShape, new bullet.Bt.Vector3(0, 0, 0));
var groundRigidBody = new bullet.Bt.RigidBody(groundRigidBodyCI);
dynamicsWorld.addRigidBody(groundRigidBody);

var fallShape = new bullet.Bt.SphereShape(1);
var fallTransform = new bullet.Bt.Transform();
fallTransform.setIdentity();
fallTransform.setOrigin(new bullet.Bt.Vector3(0, 50, 0));
var centerOfMassOffsetFallTransform = new bullet.Bt.Transform();
centerOfMassOffsetFallTransform.setIdentity();
var fallMotionState = new bullet.Bt.DefaultMotionState(fallTransform, centerOfMassOffsetFallTransform);

var fallInertia = new bullet.Bt.Vector3(0, 0, 0);
// fallShape.calculateLocalInertia(1, fallInertia);
var fallRigidBodyCI = new bullet.Bt.RigidBodyConstructionInfo(1, fallMotionState, fallShape, fallInertia);
var fallRigidBody = new bullet.Bt.RigidBody(fallRigidBodyCI);
dynamicsWorld.addRigidBody(fallRigidBody);

for (i in 0...3000) {
	dynamicsWorld.stepSimulation(1 / 60);
	
	var trans = new bullet.Bt.Transform();
	var m = fallRigidBody.getMotionState();
	m.getWorldTransform(trans);
	trace(trans.getOrigin().y());
	trans.delete();
}

// ...delete();
```
