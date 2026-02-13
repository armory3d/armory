#pragma once

// position_correction_algorithm.h
// 1:1 port from OimoPhysics PositionCorrectionAlgorithm.hx

// Baumgarte stabilization - fastest but introduces extra energy
#define OIMO_POSITION_CORRECTION_BAUMGARTE 0

// Split impulse - fast, doesn't introduce extra energy, but somewhat unstable for joints
#define OIMO_POSITION_CORRECTION_SPLIT_IMPULSE 1

// Nonlinear Gauss-Seidel - slow but stable
#define OIMO_POSITION_CORRECTION_NGS 2
