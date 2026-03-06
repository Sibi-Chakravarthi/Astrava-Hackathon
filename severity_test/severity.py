from PIL import Image

image_name=r"c:\Users\karthik\OneDrive\Desktop\chumma\coord.jpeg"
boxes=[]
with open(r'c:\Users\karthik\OneDrive\Desktop\chumma\coord.txt') as t:
    for line in t.readlines():              
        line = line.strip()                 
        if line:                            
            parts = line.split(',')         
            cls, x, y, w, h = float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            boxes.append((x, y, w, h))

    