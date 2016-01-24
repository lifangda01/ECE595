import Queue

Qs = {}
Qs['one'] = Queue.Queue()
Qs['one'].put('111111111')

Qs['two'] = Queue.Queue()
Qs['two'].put('222222222')

for Q in Qs:
	print Q
	print Qs[Q].get()