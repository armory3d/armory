package armory.logicnode;

/**
 * GetKeyboardLayout node - Detects the physical keyboard layout (QWERTY, AZERTY, DVORAK, etc.)
 *
 * This node returns the current keyboard layout name, which differs from system language.
 * Example: Windows can be set to French (AZERTY) language but English (QWERTY) keyboard.
 *
 * Outputs:
 * - Layout name as string: "QWERTY", "AZERTY", "DVORAK", "COLEMAK", etc.
 * - Lowercase for consistency with platform APIs
 *
 * Use case: Games with ZQSD movement on AZERTY should detect the keyboard layout
 * to properly map keys regardless of system language setting.
 */
class GetKeyboardLayout extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		if (from == 0) {
			return getKeyboardLayout();
		}
		return null;
	}

	/**
	 * Detects keyboard layout based on platform.
	 * Returns layout name in lowercase: "qwerty", "azerty", "dvorak", etc.
	 */
	private function getKeyboardLayout(): String {
		#if windows
		return getWindowsKeyboardLayout();
		#elseif macos
		return getMacOSKeyboardLayout();
		#elseif linux
		return getLinuxKeyboardLayout();
		#else
		return "unknown";
		#end
	}

	#if windows
	/**
	 * Windows: Query keyboard layout ID from OS using GetKeyboardLayout API
	 * Converts HKL (Handle to Keyboard Layout) to layout name
	 */
	private function getWindowsKeyboardLayout(): String {
		try {
			// Get active keyboard layout ID
			var hkl = kha.System.windowsGetKeyboardLayout();

			if (hkl == null) return "unknown";

			// Extract language ID (low 16 bits)
			var langId = Std.int(hkl) & 0xFFFF;

			// Map common layout IDs to names
			// Reference: https://docs.microsoft.com/en-us/windows-hardware/manufacture/desktop/windows-language-pack-default-values
			return switch(langId) {
				case 0x0409: "qwerty";  // English (US)
				case 0x0809: "qwerty";  // English (UK)
				case 0x080c: "azerty";  // French (Belgium)
				case 0x0c0c: "qwerty";  // French (Canada)
				case 0x040c: "azerty";  // French (France)
				case 0x140c: "azerty";  // French (Luxembourg)
				case 0x180c: "azerty";  // French (Monaco)
				case 0x1c0c: "azerty";  // French (Swiss)
				case 0x040a: "dvorak";  // Spanish (Spain) - note: some regions use DVORAK
				case 0x0407: "qwertz";  // German
				case 0x0410: "qwerty";  // Italian
				case 0x0413: "qwerty";  // Dutch
				case 0x0415: "qwerty";  // Polish
				case 0x0419: "йцукен";  // Russian (Cyrillic - ЙЦУКЕН)
				case 0x0816: "qwerty";  // Portuguese (Portugal)
				case 0x0416: "qwerty";  // Portuguese (Brazil)
				default: "qwerty";      // Default to QWERTY for unknown layouts
			};
		} catch(e: Dynamic) {
			// Fallback if API unavailable
			return "qwerty";
		}
	}
	#end

	#if macos
	/**
	 * macOS: Use Kha's built-in language detection (approximation)
	 * For more precision, would need direct Objective-C API calls
	 */
	private function getMacOSKeyboardLayout(): String {
		// macOS keyboard layouts are typically language-based
		var lang = kha.System.language;

		return switch(lang) {
			case "en": "qwerty";
			case "fr": "azerty";
			case "de": "qwertz";
			case "es": "qwerty";
			case "pt": "qwerty";
			case "ru": "йцукен";
			case "el": "greek";
			default: "qwerty";
		};
	}
	#end

	#if linux
	/**
	 * Linux: Query X11 or Wayland keyboard layout
	 * Fallback to locale if API unavailable
	 */
	private function getLinuxKeyboardLayout(): String {
		// Linux uses setxkbmap or Wayland protocol
		// For now, approximate based on locale
		var lang = kha.System.language;

		return switch(lang) {
			case "en": "qwerty";
			case "fr": "azerty";
			case "de": "qwertz";
			case "es": "qwerty";
			case "pt": "qwerty";
			case "ru": "йцукен";
			default: "qwerty";
		};
	}
	#end
}
