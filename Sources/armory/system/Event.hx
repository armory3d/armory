package armory.system;

class Event {

	static var events = new Map<String, Array<TEvent>>();

	public static function send(name: String, mask = -1) {
		var entries = get(name);
		if (entries != null) for (e in entries) if (mask == -1 || mask == e.mask ) e.onEvent();
	}

	/**
		Return the array of event listeners registered for events with the
		given name, or `null` if no listener is currently registered for the event.
	**/
	public static function get(name: String): Array<TEvent> {
		return events.get(name);
	}

	public static function add(name: String, onEvent: Void->Void, mask = -1): TEvent {
		var e: TEvent = { name: name, onEvent: onEvent, mask: mask };
		var entries = events.get(name);
		if (entries != null) entries.push(e);
		else events.set(name, [e]);
		return e;
	}

	public static function remove(name: String) {
		events.remove(name);
	}

	public static function removeListener(event: TEvent) {
		var entries = events.get(event.name);
		if (entries != null) {
			entries.remove(event);
			if (entries.length == 0) {
				events.remove(event.name);
			}
		}
	}
}

typedef TEvent = {
	var name: String;
	var onEvent: Void->Void;
	var mask: Int;
}
