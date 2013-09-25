clean:
	find . -name "*~" -delete -o -name "*.pyc" -delete

upload:
	ssh pi@192.168.1.136 "mkdir ~/curses"
	scp -r * pi@192.168.1.136:~/curses/
