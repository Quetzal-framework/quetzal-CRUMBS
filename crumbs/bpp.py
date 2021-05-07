import re

def extract_probabilities(bpp_output):
    p = re.compile('P\[(\d)\] = (\d+\.\d+)')
    iterator = p.finditer(bpp_output)
    p1, p2 = float, float
    for match in iterator:
        if(match.group(1) == "1"):
            p1 = float(match.group(2))
        elif(match.group(1) == "2"):
            p2 = float(match.group(2))
        else:
            raise ValueError("Number of species should be 1 or 2")
    return p1, p2
