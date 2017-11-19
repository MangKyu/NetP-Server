from PIL import Image

class Item:
    seller = None
    itemName = None
    price = None
    itemDesc = None
    imgPath = None
    endTime = None

    # constructor for Item instance
    def __init__(self, seller, itemName, price, itemDesc, imgPath, endTime):
        self.seller = seller
        self.itemName = itemName
        self.price = price
        self.itemDesc = itemDesc
        self.imgPath = imgPath
        self.endTime = endTime