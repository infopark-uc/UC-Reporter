import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 2
bind = 'unix:ucreceiver.sock'
#umask = 0o007
umask = 777
reload = True

#logging
accesslog = '-'
errorlog = '-'