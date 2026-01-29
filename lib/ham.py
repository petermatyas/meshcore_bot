



def isMaidenhead(locator):
    locator = locator.lower()
    if not locator[0].isalpha() or \
        not locator[1].isalpha() or \
        not locator[0] in [chr(i) for i in range(ord('a'),ord('r')+1)] or \
        not locator[1] in [chr(i) for i in range(ord('a'),ord('r')+1)]:
        return False
    if not locator[2].isdigit() or not locator[3].isdigit():
        return False
    if len(locator) == 4:
        return True
    if not locator[4].isalpha() or not locator[5].isalpha():
        return False
    if len(locator) == 6:   
        return True
    if not locator[2].isdigit() or not locator[3].isdigit():
        return False
    if len(locator) == 8:
        return True
    return True

def maidenheadToLatLon(locator):
    locator = locator.lower()
    if not isMaidenhead(locator):
        return None

    lon = (ord(locator[0]) - ord('a')) * 20 - 180
    lat = (ord(locator[1]) - ord('a')) * 10 - 90

    lon += int(locator[2]) * 2
    lat += int(locator[3]) * 1

    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord('a')) * (5/60)
        lat += (ord(locator[5]) - ord('a')) * (2.5/60)

    if len(locator) == 8:
        lon += int(locator[6]) * (5/600)
        lat += int(locator[7]) * (2.5/600)

    # Return the center of the square
    if len(locator) == 2:
        lon += 10
        lat += 5
    elif len(locator) == 4:
        lon += 1
        lat += 0.5
    elif len(locator) == 6:
        lon += (5/120)
        lat += (2.5/120)
    elif len(locator) == 8:
        lon += (5/1200)
        lat += (2.5/1200)

    return lat, lon