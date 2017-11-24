class Room:
    roomIdx = 0
    item = None
    endTime = None

    # constructor for room instance
    def __init__(self, roomIdx, endTime, item):
        self.roomIdx = roomIdx
        self.endTime = endTime
        self.item = item