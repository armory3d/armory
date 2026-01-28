package armory.n64;

/**
 * Marker interface for N64 autoload classes.
 *
 * Classes implementing this interface will automatically have the N64AutoloadMacro
 * applied via @:autoBuild. This provides global singleton-like access in C code.
 *
 * Usage:
 *   @:n64autoload(order=0)  // Optional: control initialization order (lower = earlier)
 *   class GameEvents implements N64Autoload {
 *       public static var sceneLoaded:Signal = new Signal();
 *       public static var score:Int = 0;
 *
 *       public static function init():Void {
 *           // Called at engine startup, before scenes load
 *       }
 *
 *       public static function resetScore():Void {
 *           score = 0;
 *       }
 *   }
 *
 * Generated C code:
 *   // gameevents.h
 *   extern ArmSignal gameevents_sceneLoaded;
 *   extern int32_t gameevents_score;
 *   void gameevents_resetScore(void);
 *   void gameevents_init(void);
 *
 * Accessing from traits:
 *   GameEvents.score         -> gameevents_score
 *   GameEvents.resetScore()  -> gameevents_resetScore()
 */
@:autoBuild(armory.n64.N64AutoloadMacro.build())
interface N64Autoload {}
