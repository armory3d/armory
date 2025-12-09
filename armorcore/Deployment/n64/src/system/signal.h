/**
 * Signal System Header
 * ====================
 *
 * Per-instance signals for event-driven communication between traits.
 * Similar to Godot's signal system.
 *
 * Usage in Haxe traits:
 *   var onDeath:Signal;                    // Declare signal
 *   @:n64MaxSubs(8) var onHit:Signal;      // Custom max subscribers (default 16)
 *
 *   onDeath.connect(myCallback);           // Subscribe
 *   onDeath.disconnect(myCallback);        // Unsubscribe
 *   onDeath.emit(damage, attacker);        // Emit with args (max 4)
 */

#pragma once

#include "../types.h"

// Functions are declared in types.h since ArmSignal is defined there
// This header is for documentation and potential future extensions
