package armory.system;

import haxe.Exception;
import haxe.PosInfos;
import haxe.exceptions.PosException;
import haxe.macro.Context;
import haxe.macro.Expr;

using haxe.macro.ExprTools;

class Assert {

	/**
		Checks whether the given expression evaluates to true. If this is not
		the case, an `ArmAssertionException` is thrown or a warning is printed
		(depending on the assertion level).

		The assert level describes the severity of the assertion. If the
		severity is lower than the level stored in the `arm_assert_level` flag,
		the assertion is omitted from the code so that it doesn't decrease the
		runtime performance.

		@param level The severity of this assertion.
		@param condition The conditional expression to test.
		@param message Optional message to display when the assertion fails.

		@see `AssertLevel`
	**/
	macro public static function assert(level: ExprOf<AssertLevel>, condition: ExprOf<Bool>, ?message: ExprOf<String>): Expr {
		final levelVal: AssertLevel = AssertLevel.fromExpr(level);
		final assertThreshold = AssertLevel.fromString(Context.definedValue("arm_assert_level"));

		if (levelVal < assertThreshold) {
			return macro {};
		}

		switch (levelVal) {
			case Warning:
				return macro {
					if (!$condition) {
						@:pos(condition.pos)
						trace(@:privateAccess armory.system.Assert.ArmAssertionException.formatMessage($v{condition.toString()}, ${message}));
					}
				}
			case Error:
				return macro {
					if (!$condition) {
						#if arm_assert_quit kha.System.stop(); #end

						@:pos(condition.pos)
						@:privateAccess armory.system.Assert.throwAssertionError($v{condition.toString()}, ${message});
					}
				}
			default:
				throw new Exception('Unsupported assert level: $levelVal');
		}
	}

	/**
		Helper function to prevent Haxe "bug" that actually throws an error
		even when using `macro throw` (inlining this method also does not work).
	**/
	static function throwAssertionError(exprString: String, message: String, ?pos: PosInfos) {
		throw new ArmAssertionException(exprString, message, pos);
	}
}

/**
	Exception that is thrown when an assertion fails.

	@see `Assert`
**/
class ArmAssertionException extends PosException {

	/**
		@param exprString The string representation of the failed assert condition.
		@param message Custom error message, use `null` to omit this.
	**/
	public inline function new(exprString: String, message: Null<String>, ?previous: Exception, ?pos: Null<PosInfos>) {
		super('\n${formatMessage(exprString, message)}', previous, pos);
	}

	static inline function formatMessage(exprString: String, message: Null<String>): String {
		final optMsg = message != null ? '\n\tMessage: $message' : "";

		return 'Failed assertion:$optMsg\n\tExpression: ($exprString)';
	}
}

enum abstract AssertLevel(Int) from Int to Int {
	/**
		Assertions with this severity don't throw exceptions and only print to
		the console.
	**/
	var Warning: AssertLevel = 0;

	/**
		Assertions with this severity throw an `ArmAssertionException` if they
		fail, and optionally quit the game if the `arm_assert_quit` flag is set.
	**/
	var Error: AssertLevel = 1;

	/**
		Completely disable assertions. Don't use this level in `assert()` calls!
	**/
	var NoAssertions: AssertLevel = 2;

	public static function fromExpr(e: ExprOf<AssertLevel>): AssertLevel {
		switch (e.expr) {
			case EConst(CIdent(v)): return fromString(v);
			default: throw new Exception('Unsupported expression: $e');
		};
	}

	/**
		Converts a string into an `AssertLevel`, the string must be spelled
		exactly as the assert level. `null` defaults to
		`AssertLevel.NoAssertions`.
	**/
	public static function fromString(s: Null<String>): AssertLevel {
		return switch (s) {
			case "Warning": Warning;
			case "Error": Error;
			case "NoAssertions" | null: NoAssertions;
			default: throw new Exception('Could not convert "$s" to AssertLevel');
		}
	}

	@:op(A < B) static function lt(a: AssertLevel, b: AssertLevel): Bool;
	@:op(A > B) static function gt(a: AssertLevel, b: AssertLevel): Bool;
}
