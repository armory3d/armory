if [[ $OSTYPE == linux-gnu* ]]; then
	arch=$(uname -m)
	if [[ "$arch" == "aarch64" ]]; then
		cp "$( dirname "${BASH_SOURCE[0]}" )"/node-linuxaarch64 "$( dirname "${BASH_SOURCE[0]}" )"/node
	elif [[ "$arch" == "x86_64" ]]; then
		cp "$( dirname "${BASH_SOURCE[0]}" )"/node-linux64 "$( dirname "${BASH_SOURCE[0]}" )"/node
	else  # Assume 32-bit ARM
		cp "$( dirname "${BASH_SOURCE[0]}" )"/node-linuxarm "$( dirname "${BASH_SOURCE[0]}" )"/node
	fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
	cp "$( dirname "${BASH_SOURCE[0]}" )"/node-osx "$( dirname "${BASH_SOURCE[0]}" )"/node
fi

