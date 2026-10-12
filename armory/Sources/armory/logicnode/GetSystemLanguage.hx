package armory.logicnode;

/**
 * GetSystemLanguage node - Returns the system language code
 *
 * Outputs the language setting (e.g., "en", "fr", "de")
 *
 * Note: For keyboard layout detection, use GetKeyboardLayout instead.
 * This node returns language (e.g., "en" for English) but not keyboard layout (e.g., "qwerty" vs "azerty").
 *
 * Example: Windows set to French language but QWERTY keyboard:
 * - GetSystemLanguage returns: "fr"
 * - GetKeyboardLayout returns: "qwerty"
 */
class GetSystemLanguage extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		if (from == 0) return kha.System.language;
		return null;
	}
}
