import heapq


class Frontier():
    def __init__(self):     
        self.data = []
        heapq.heapify(self.data)
   
    
    def empty(self):
        return len(self.data) == 0
    

    def push(self, elem):
        heapq.heappush(self.data, elem)


    def pop(self):
        return heapq.heappop(self.data)
