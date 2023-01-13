import cv2
import numpy as np

class SingleCamDistanceMeasure(object):
	# 1 cm = 0.39 inch, original size h x w 
	INCH = 0.39
	RefSizeDict = { 
					"person" : (160*INCH, 50*INCH), 
					"bicycle" : (98*INCH, 65*INCH),
					"motorbike" : (100*INCH, 100*INCH), # (132*INCH, 100*INCH)
					"car" : (150*INCH, 180*INCH ),
					"bus" : (319*INCH, 250*INCH), 
					"truck" : (346*INCH, 250*INCH), 
				 }

	def __init__(self, object_list=["person", "bicycle", "car", "motorbike", "bus", "truck"] ):
		self.object_list = object_list
		self.f = 100 # focal length
		self.distance_points = []

	def _isInsidePolygon(self, pt, poly):
		"""判断点在多边形范围内.

		Parameters
		----------
			pt: the object points
			poly: 为多边形区域

		Return
		------
			total number of all feature vector.
		"""
		c = False
		i = -1
		l = len(poly)
		j = l - 1
		while i < l - 1:
			i += 1
			if((poly[i][0]<=pt[0] and pt[0] < poly[j][0])or(
				poly[j][0]<=pt[0] and pt[0]<poly[i][0] )):
				if(pt[1]<(poly[j][1]-poly[i][1]) * (pt[0]-poly[i][0])/(
					poly[j][0]-poly[i][0])+poly[i][1]):
					c = not c
			j=i
		return c


	def calcDistance(self, boxes) :
		self.distance_points = []
		if ( len(boxes) != 0 )  :
			for box, _ in boxes:
				ymin, xmin, ymax, xmax, label = box
				if label in self.object_list and  ymax <= 700:
					point_x = (xmax + xmin) // 2
					point_y = ymax

					try :
						distance = (self.RefSizeDict[label][0] * self.f)/ (ymax - ymin)
						distance = distance/12*0.3048 # 1ft = 0.3048 m
						self.distance_points.append([point_x, point_y, distance])
					except :
						pass
 

	def calcCollisionPoint(self, poly):
		if ( len(self.distance_points) != 0 and len(poly) )  :
			for x, y, d in self.distance_points:
				if (self._isInsidePolygon( (x, y), np.squeeze(poly) )) :
					return [x, y, d]
		return None


	def DrawDetectedOnFrame(self, frame_show) :
		if ( len(self.distance_points) != 0 )  :
			for x, y, d in self.distance_points:
				cv2.circle(frame_show, (x, y), 4, (0, 255 , 0), thickness=-1)

				unit = 'm'
				if d < 0:
					text = ' {} {}'.format( "unknown", unit)
				else :
					text = ' {:.2f} {}'.format(d, unit)

				cv2.putText(frame_show, text, (x + 1, y + 30), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, 
							color=(0, 255 , 0), thickness=2)
