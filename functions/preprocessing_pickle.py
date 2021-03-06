import os
import os.path
import cv2
import pickle
import numpy as np

file_path = '/'.join(os.path.realpath(__file__).split("/")[:-2])

'''
Function: 
	1) Preprocessing of Celeb_A Datase
		- cropping into square
		- resizing to 64x64
		- convert to grayscale
		- mapping them to interval [-1,1]
		- expanding their dimensions by an "empty" third dimension
	2) Dumps Images into a pickle 

Usage:
	- Provide path of the folder with the images to bepreprocessed
	- Provide path in which the pickle will dump
	- Provide Name of the file the pickled-file
'''

def preprocessing(pic_folder_path=file_path+'/data/unprocessed_images', 
	
	pickle_path=file_path+'/data/pickle', pickle_name="celeba_pickle.dat"):
	
	print('[*] Preprocessing started. This may take a while...')

	# list, where we save our pictures so we can dump them later
	IMG_LIST = []

	# list with all file_names
	file_list = os.listdir(pic_folder_path)

	# 
	file_list = [f for f in file_list if (f.endswith(".jpg") or f.endswith(".png"))]

	# iterate through every element in the directory
	for counter in range(len(file_list)):	

		#read img
		img = cv2.imread(pic_folder_path + '/' + file_list[counter])	#
		
		# check whether its a picture
		# apply cropping
		img = img[20:198,:]
		
		# resize img to 64x64
		img = cv2.resize(img, (64, 64)) 
		
		# convert to greyscale
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		
		# bring to range -1 to 1
		img = (img/255.0-0.5)*2.0
		
		# expand dimensions so its compatible with placeholder function
		img = np.expand_dims(img,-1)


		# append to "IMG_LIST"
		IMG_LIST.append(img)

		# print
		if counter%np.floor((len(file_list)/100))==0 or counter==len(file_list)-1:
			print(str(counter) + ' of ' + str(len(file_list)) + ' images processed')

	# dump the img list into a file
	with open(pickle_path+'/'+pickle_name, 'wb') as f:
		pickle.dump(IMG_LIST, f)

	# positive feedback
	print('\t[+] Preprocessing finished. Your pickle is saved in ' \
		+ pickle_path + '/' + pickle_name)

if __name__=='__main__':
	preprocessing()
