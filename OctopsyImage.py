import exifread
import datetime
import GPSConverter

class OctopsyImage:
    def __init__(self, Path):
        self.Path = Path
        self.ShortName = self.setShortName(self.Path)
        self.ListIndividualAnomalies = []
        self.setInitialEXIF()
        self.setEXIF()
        self.findIndividualAnomalies()

    # Main Function
    def setInitialEXIF(self):
        self.setModel("null")
        self.setMake("null")
        self.setDateTimeOriginal("null")
        self.setGPSLongitudeRef("null")
        self.setGPSLatitudeRef("null")
        self.setGPSLongitude("null")
        self.setGPSLatitude("null")
        self.setISOSpeedRatings("null")
        self.setFlash(-1)
        self.setDigitalZoomRatio(-1)

    # Get EXIF from the picture
    def setEXIF(self):
        File = open(self.Path, 'rb')
        tags = exifread.process_file(File)

        for Key in tags.keys():
            #if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            #print("Key: %s, value %s" % (Key, tags[Key]))

            if (Key == "Image Model"):
                self.setModel(tags[Key])
            elif (Key == "Image Make"):
                self.setMake(tags[Key])
            elif (Key == "EXIF DateTimeOriginal"):
                self.setDateTimeOriginal(tags[Key])
            elif (Key == "GPS GPSLongitudeRef"):
                self.setGPSLongitudeRef(tags[Key])
            elif (Key == "GPS GPSLatitudeRef"):
                self.setGPSLatitudeRef(tags[Key])
            elif (Key == "GPS GPSLongitude"):
                self.setGPSLongitude(tags[Key])
            elif (Key == "GPS GPSLatitude"):
                self.setGPSLatitude(tags[Key])
            elif (Key == "EXIF ISOSpeedRatings"):
                self.setISOSpeedRatings(tags[Key])
            elif (Key == "EXIF Flash"):
                Substring = "Flash did not fire"
                TheString = str(tags[Key])
                if (Substring in TheString):
                    self.setFlash(0)
                else:
                    self.setFlash(1)
            elif (Key=="EXIF DigitalZoomRatio"):
                self.setDigitalZoomRatio(self.convertFloat(str(tags[Key])))

    # Find all individual anomalies in the image
    def findIndividualAnomalies(self):
        # First Anomaly: Flash vs Daylight
        # If the flash was fired in daylight: probably the photo was taken from inside a room
        # Similarly, if the flash was not fired at night: probably the photo was taken from inside a room
        # ListAnomalies = 1 if the photo was taken from inside a room
        FlashValue = self.getFlash()
        DayValue = self.isDay(self.getDateTimeOriginal())
        if((FlashValue!="null") and (DayValue!="null") and (DayValue != -1)):
            if((FlashValue == 1) and (DayValue == 1)):
                self.ListIndividualAnomalies.append(1)
            elif((FlashValue == 0) and (DayValue == 0)):
                self.ListIndividualAnomalies.append(1)
            else:
                self.ListIndividualAnomalies.append(0)
        else:
            self.ListIndividualAnomalies.append(-1)

        # Second Anomaly: Incomplete EXIF -> case from Facebook, Twitter, WhatsApp
        # If EXIF is incomplete (See the Make information), probably, it was taken from other social media
        # Can be improved: add other parameters to make the anomaly detection more robust
        if(self.getMake() == "null"):
            self.ListIndividualAnomalies.append(1)
        else:
            self.ListIndividualAnomalies.append(0)

        # Fourth Anomaly: Compare zoom to physical distance
        # Do it in range -> short, medium, long
        # From 1 to 2: short
        # From 2 to 3: medium
        # From 3 to 4: long
        # ListAnomalies: 0 is short, 1 is medium, 2 is long
        ZoomValue = self.getDigitalZoomRatio()
        if(ZoomValue != -1):
            if((ZoomValue >= 1) and (ZoomValue <= 2)):
                self.ListIndividualAnomalies.append(0)
            elif(ZoomValue <= 3):
                self.ListIndividualAnomalies.append(1)
            else:
                self.ListIndividualAnomalies.append(2)
        else:
            self.ListIndividualAnomalies.append(-1)

    # Convert GPS format from Degrees, Minutes, Seconds, and Direction to Decimal
    def convertGPS(self, Degrees, Minutes, Seconds, Direction):
        dd = GPSConverter.dms2dd(Degrees, Minutes, Seconds, Direction)
        return dd

    def convertFloat(self, Value):
        Slash = "/"
        if(Slash not in Value):
            return float(Value)
        else:
            Numerator = float(Value.split('/')[0])
            Denominator = float(Value.split('/')[1])
            return float(Numerator/Denominator)

    def isDay(self, Date):
        if(Date != "null"):
            # Assumption: sunrise at 6.30 am and sunset at 8:06 pm for April 22, 2017
            # Refence: https://www.timeanddate.com/sun/usa/pittsburgh
            SunriseTime = datetime.time(hour=6, minute=30, second=0)
            SunsetTime = datetime.time(hour=20, minute=6, second=0)

            # Parse StringDate
            StringDate = str(Date)
            ListTemp1 = StringDate.split(' ')
            ListTemp2 = ListTemp1[1].split(':')
            ImageTime = datetime.time(hour=int(ListTemp2[0]), minute=int(ListTemp2[1]), second=int(ListTemp2[2]))

            # Comparison
            if(ImageTime < SunriseTime):
                return 0
            else:
                if(ImageTime < SunsetTime):
                    return 1
                else:
                    return 0
        else:
            return -1

    def getListIndividualAnomalies(self):
        return self.ListIndividualAnomalies

    def getPath(self):
        return self.Path

    def getShortName(self):
        return self.ShortName

    def setShortName(self, Path):
        ListShort = Path.split('\\')
        return ListShort[len(ListShort)-1]

    # General Information
    def getModel(self):
        return self.Model

    def setModel(self, Model):
        self.Model = Model

    def getMake(self): #a.k.a Vendor
        return self.Make

    def setMake(self, Make):
        self.Make = Make

    def getDateTimeOriginal(self):
        return self.DateTimeOriginal

    def setDateTimeOriginal(self, DateTimeOriginal):
        self.DateTimeOriginal = DateTimeOriginal


    # GPS
    def getGPSLongitudeRef(self):
        return self.GPSLongitudeRef

    def setGPSLongitudeRef(self, GPSLongitudeRef):
        self.GPSLongitudeRef = GPSLongitudeRef

    def getGPSLatitudeRef(self):
        return self.GPSLatitudeRef

    def setGPSLatitudeRef(self, GPSLatitudeRef):
        self.GPSLatitudeRef = GPSLatitudeRef

    def getGPSLongitude(self):
        return self.GPSLongitude

    def setGPSLongitude(self, GPSLongitude):
        self.GPSLongitude = GPSLongitude

    def getGPSLatitude(self):
        return self.GPSLatitude

    def setGPSLatitude(self, GPSLatitude):
        self.GPSLatitude = GPSLatitude


    # EXIF
    def getISOSpeedRatings(self):
        return self.ISOSpeedRatings

    def setISOSpeedRatings(self, ISOSpeedRatings):
        self.ISOSpeedRatings = ISOSpeedRatings

    def getFlash(self):
        return self.Flash

    def setFlash(self, Flash):
        self.Flash = Flash

    def getDigitalZoomRatio(self):
        return self.DigitalZoomRatio

    def setDigitalZoomRatio(self, DigitalZoomRatio):
        self.DigitalZoomRatio = DigitalZoomRatio