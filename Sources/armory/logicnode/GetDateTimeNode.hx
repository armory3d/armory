package armory.logicnode;

class GetDateTimeNode extends LogicNode {
	public var property0: String;
	public var value: Int;
	public var timeStamp: Float;
	public var timezoneOffset: Int;
	public var weekDay: Int;
	public var day: Int;
	public var month: Int;
	public var year: Int;
	public var hours: Int;
	public var minutes: Int;
	public var seconds: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var dateTime = Date.now();
		timeStamp = dateTime.getTime();
		timezoneOffset = dateTime.getTimezoneOffset();
		weekDay = dateTime.getDay();
		day = dateTime.getDate();
		month = dateTime.getMonth();
		year = dateTime.getFullYear();
		hours = dateTime.getHours();
		minutes = dateTime.getMinutes();
		seconds = dateTime.getSeconds();
		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		if(property0 == "all"){
			return switch (from) {
				case 1: timeStamp;
				case 2: timezoneOffset;
				case 3: weekDay;
				case 4: day;
				case 5: month;
				case 6: year;
				case 7: hours;
				case 8: minutes;
				case 9: seconds;
				default: null;
			}		
		} else if (property0 == "formatted"){
			return DateTools.format(Date.now(), inputs[0].get());
		} else {
			var dateTime = Date.now();
			return switch (property0) {
				case "now": dateTime;
				case "timestamp": dateTime.getTime();
				case "timezoneOffset": dateTime.getTimezoneOffset();
				case "weekDay": dateTime.getDay();
				case "day": dateTime.getDate();
				case "month": dateTime.getMonth();
				case "year": dateTime.getFullYear();
				case "hours": dateTime.getHours();
				case "minutes": dateTime.getMinutes();
				case "seconds": dateTime.getSeconds();
				default: null;
			}		
		}
	}
}
