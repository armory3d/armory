#ifndef OIMO_DYNAMICS_RIGIDBODY_RIGID_BODY_TYPE_H
#define OIMO_DYNAMICS_RIGIDBODY_RIGID_BODY_TYPE_H

// Dynamic: finite mass, affected by gravity and constraints
#define OIMO_RIGID_BODY_DYNAMIC    0

// Static: infinite mass, zero velocity, not affected by forces
#define OIMO_RIGID_BODY_STATIC     1

// Kinematic: infinite mass, can have velocity, not affected by forces
#define OIMO_RIGID_BODY_KINEMATIC  2

#endif // OIMO_DYNAMICS_RIGIDBODY_RIGID_BODY_TYPE_H
