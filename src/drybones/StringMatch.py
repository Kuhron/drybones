# for imitating behavior of re.Match object for matches that don't use regex
# so I can use the same API in code that might get a re.Match and might get one of these
# since you can't create re.Match instances yourself


class StringMatch:
    def __init__(self, string, start_index, end_index):
        self.string = string
        self.start_index = start_index
        self.end_index = end_index

    def start(self):
        return self.start_index
    
    def end(self):
        return self.end_index
    
    def span(self):
        return (self.start_index, self.end_index)
    
    def group(self):
        return self.string[self.start_index : self.end_index]

