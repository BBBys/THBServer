import logging
def setBitmap(w,h,x0,y0,buf, image): 
	# Set buffer to value of Python Imaging Library image.
	# Image must be in mode 1.
	logging.info("setBitmap funktioniert nicht")
	image_monocolor = image.convert('1') 
	imwidth, imheight = image_monocolor.size 
	#print(imwidth, imheight)
	pixels = image_monocolor.load() 
	for y in range(imheight): 
		for x in range(imwidth): 
			# Set the bits for the column of pixels at the current position.
			if pixels[x, y] == 0: 
				baddr = (int)(((x0 + x) + (y0 + y) * w) / 8) 
				buf[baddr] &= ~(0x80 >> ((x0 + x) % 8))
