// position_correction_algorithm.h
// 1:1 port from OimoPhysics PositionCorrectionAlgorithm.hx
#ifndef OIMO_DYNAMICS_CONSTRAINT_POSITION_CORRECTION_ALGORITHM_H
#define OIMO_DYNAMICS_CONSTRAINT_POSITION_CORRECTION_ALGORITHM_H

// Baumgarte stabilization - fastest but introduces extra energy
#define OIMO_POSITION_CORRECTION_BAUMGARTE 0

// Split impulse - fast, doesn't introduce extra energy, but somewhat unstable for joints
#define OIMO_POSITION_CORRECTION_SPLIT_IMPULSE 1

// Nonlinear Gauss-Seidel - slow but stable
#define OIMO_POSITION_CORRECTION_NGS 2

#endif // OIMO_DYNAMICS_CONSTRAINT_POSITION_CORRECTION_ALGORITHM_H
