package armory.system;

/**
	Detailed documentation of the event system:
	[Armory Wiki: Events](https://github.com/armory3d/armory/wiki/events).
**/
class Event {

	static var events = new Map<String, Array<TEvent>>();

	/**
		Send an event with the given name to all corresponding listeners. This
		function directly executes the `onEvent` callbacks of those listeners.

		For an explanation of the `mask` value, please refer to the
		[wiki](https://github.com/armory3d/armory/wiki/events#event-masks).
	**/
	public static function send(name: String, mask = -1) {
		var entries = get(name);
		if (entries != null) for (e in entries) if (mask == -1 || mask == e.mask ) e.onEvent();
	}

	/**
		Return the array of event listeners registered for events with the
		given name.

		The return value is `null` if no listener with the given name was ever
		registered or `remove()` was called for the given name.
	**/
	public static function get(name: String): Array<TEvent> {
		return events.get(name);
	}

	/**
		Add a listener to the event with the given name and return the
		corresponding listener object. The `onEvent` callback will be called
		when a matching event is sent.

		For an explanation of the `mask` value, please refer to the
		[wiki](https://github.com/armory3d/armory/wiki/events#event-masks).
	**/
	public static function add(name: String, onEvent: Void->Void, mask = -1): TEvent {
		var e: TEvent = { name: name, onEvent: onEvent, mask: mask };
		var entries = events.get(name);
		if (entries != null) entries.push(e);
		else events.set(name, [e]);
		return e;
	}

	/**
		Remove _all_ listeners that listen to events with the given `name`.
	**/
	public static function remove(name: String) {
		events.remove(name);
	}

	/**
		Remove a specific listener. If the listener is not registered/added,
		this function does nothing.
	**/
	public static function removeListener(event: TEvent) {
		var entries = events.get(event.name);
		if (entries != null) entries.remove(event);
	}
}

/**
	Represents an event listener.

	@see `armory.system.Event`
**/
typedef TEvent = {
	/** The name of the events this listener is listening to. **/
	var name: String;

	/** The callback function that is called when a matching event is sent. **/
	var onEvent: Void->Void;

	/** The mask of the events this listener is listening to. **/
	var mask: Int;
}
