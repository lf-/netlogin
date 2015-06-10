# netlogin
Easy login for captive portal networks

##Configuration
By default, configuration is in /etc/netlogin/networks.json and json files in /etc/netlogin/networks.d.

###Format:

	{
		"$network": {
			"url": "http://1.1.1.1/login.html",
			"method": "POST",
			"data": {
				"buttonClicked": 4,
				"redirectUrl": "http://gstatic.com/generate_204",
				"err_flag": 0
			}
		}
	}

##Usage:

  `netlogin [-h] [--network NETWORK] [--listen] [--verbose]`
  
  If run by itself, it finds the connected SSID using NetworkManager's DBus, then tries the config for it. The end result being that you can simply run `netlogin` and it will log into whatever network you're connected to if that's configured.
  
  If the -n argument is provided along with a network, no DBus is used and the network is logged into immediately.
  
  Finally, if --listen is passed, this will set an event listener for network changed and automagically log into whatever shows up.

##Installation

  python3 setup.py install

You're done!
