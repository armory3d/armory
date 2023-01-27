package armory.network;

class HttpRequest {
	public var method:String = null;
	public var uri:String = null;
	public var httpVersion:String = null;

	public var headers:Map<String, String> = new Map<String, String>();

	public function new() {}

	public function addLine(line:String) {
		if (method == null) {
			var parts = line.split(" ");
			method = parts[0];
			uri = parts[1];
			httpVersion = StringTools.trim(parts[2]);
		} else {
			var n = line.indexOf(":");
			var name = line.substr(0, n);
			var value = line.substr(n + 1, line.length);
			headers.set(StringTools.trim(name), StringTools.trim(value));
		}
	}

	public function build():String {
		var sb = new StringBuf();

		sb.add(method);
		sb.add(" ");
		if (uri != null) {
			sb.add(uri);
			sb.add(" ");
		}
		sb.add(httpVersion);
		sb.add("\r\n");

		for (header in headers.keys()) {
			sb.add(header);
			sb.add(": ");
			sb.add(headers.get(header));
			sb.add("\r\n");
		}

		sb.add("\r\n");
		return sb.toString();
	}

	public function toString():String {
		return build();
	}
}
