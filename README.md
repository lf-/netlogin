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

  `netlogin [-h] [--network NETWORK] [--verbose]`
  
  If run by itself, it registers a DBus listener on NetworkManager so it can log into networks automagically.
  
  If the -n argument is provided along with a network, no event listener is set and the network is logged into immediately.

##Installation

  python3 setup.py install

You're done!
