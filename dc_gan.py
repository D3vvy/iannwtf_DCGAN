
# TODO ÜBERSCHIRFT; AUTOREN BLA BLA




# ##################################################################
# ##################### Imports and Setting ########################
# ##################################################################

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import random 					
#TODO: One of those two can be removed FLEM
import os
import os.path

from functions.auxiliary_functions import merge_and_save
from functions.celeba_input import CelebA

# ####################################
# ######## Training Parameters #######
# ####################################
Z_size = 100
batch_size = 32
n_batches = 5000
restore_weights = True

# ####################################
# ############ Directories ########### 
# ####################################
# Path, where to save sample-images
sample_dir = './save/figs'
if not os.path.exists(sample_dir):
	os.makedirs(sample_dir)

# Path, where to save trained model
model_dir = './save/models'
if not os.path.exists(model_dir):
	os.makedirs(model_dir)

# ####################################
# ########### Print-Setting ##########
# ####################################
printFreq = np.round(2*1000/batch_size)
sampleFreq = np.round(20*1000/batch_size)
saveFreq = np.round(50*1000/batch_size)
print_varnames = True

# ####################################
# ### Creation of Sample-Supplier ####
# ####################################
sampleGen = CelebA()


# ##################################################################
# ##################### Auxiliary Functions ######################## #todo change???
# ##################################################################

# leaky rectified linear unit
def lrelu(x, leak=0.2, name="lrelu"):
	with tf.variable_scope(name):
		f1 = 0.5 * (1 + leak)
		f2 = 0.5 * (1 - leak)
		return f1 * x + f2 * abs(x)

# TODO
def check_update(fake_acc, real_acc, thresh1, thresh2):
	D_opt = True
	G_opt = True
	if fake_acc < thresh2 or real_acc < thresh2:
		D_opt = True
		G_opt = False
	if ((fake_acc + real_acc) / 2) > thresh1:
		D_opt = False
		G_opt = True
	return D_opt,G_opt 

# ##################################################################
# ################ Definition of Network Elements ##################
# ##################################################################

# Todo add comments


# ####################################
# #### Function for Dense_Layers #####
# ####################################
def dense_layer(layer_input, W_shape, b_shape=[-1], activation=tf.nn.tanh, bias_init=0.1, batch_norm=False, norm_before_act=False, reuse=False, varscope=None, namescope=None):
	with tf.name_scope(namescope):
		with tf.variable_scope(varscope, reuse=reuse):
			if b_shape == [-1]:
				b_shape = [W_shape[-1]]
			W = tf.get_variable('weights', W_shape, initializer=tf.truncated_normal_initializer(stddev=0.1))
			b = tf.get_variable('biases', b_shape, initializer=tf.constant_initializer(bias_init))
			iState = tf.matmul(layer_input, W)
			if b_shape != [0]:
				iState += b
			if batch_norm and norm_before_act:
				iState = tf.nn.l2_normalize(iState, 0)
			iState = activation(iState)
			if batch_norm and not norm_before_act:
				iState = tf.nn.l2_normalize(iState, 0)
			return iState

# ####################################
# #### Function for Convolution ######
# ####################################
def conv2d_layer(layer_input, W_shape, b_shape=[-1], strides=[1,1,1,1], padding='SAME', activation=tf.nn.relu, bias_init=0.1, batch_norm=False, reuse=False, varscope=None, namescope=None):
	with tf.name_scope(namescope):
		with tf.variable_scope(varscope, reuse=reuse):
			if b_shape == [-1]:
				b_shape = [W_shape[-1]]
			W = tf.get_variable('weights', W_shape, initializer=tf.truncated_normal_initializer(stddev=0.1))
			b = tf.get_variable('biases', b_shape, initializer=tf.constant_initializer(bias_init))
			iState = tf.nn.conv2d(layer_input, W, strides, padding)
			if b_shape != [0]:
				iState += b
			if batch_norm:
				iState = tf.nn.l2_normalize(iState, 0)
			return activation(iState)

# ####################################
# #### Function for Trans-Conv ######
# ####################################
def trans2d_layer(layer_input, W_shape, output_shape, b_shape=[-2], strides=[1,1,1,1], padding='SAME', activation=tf.nn.relu, bias_init=0.1, batch_norm=False, reuse=False, varscope=None, namescope=None):
	with tf.name_scope(namescope):
		with tf.variable_scope(varscope, reuse=reuse):
			if b_shape == [-2]:
				b_shape = [W_shape[-2]]
			W = tf.get_variable('weights', W_shape, initializer=tf.truncated_normal_initializer(stddev=0.1))
			b = tf.get_variable('biases', b_shape, initializer=tf.constant_initializer(bias_init))
			iState = tf.nn.conv2d_transpose(layer_input, W, output_shape, strides)
			if b_shape != [0]:
				iState += b
			if batch_norm:
				iState = tf.nn.l2_normalize(iState, 0)
			return activation(iState)

#todo add comments

# ####################################
# ######### Generator Setup ##########
# ####################################
def generator(Z, reuse=False):
	state = dense_layer(Z, W_shape=[Z_size,512*4*4], activation=tf.nn.relu, batch_norm=True, norm_before_act=True, reuse=reuse, varscope='g_fc1', namescope='generator')
	state = tf.reshape(state, [batch_size,4,4,512])
	state = trans2d_layer(layer_input=state, W_shape=[5,5,256,512], output_shape=[batch_size,8,8,256], strides=[1,2,2,1], batch_norm=True, reuse=reuse, varscope='g_trans1', namescope='generator')
	state = trans2d_layer(layer_input=state, W_shape=[5,5,128,256], output_shape=[batch_size,16,16,128], strides=[1,2,2,1], batch_norm=True, reuse=reuse, varscope='g_trans2',namescope='generator')
	# state = tf.nn.dropout(state,drop[1])
	state = trans2d_layer(layer_input=state, W_shape=[5,5,32,128], output_shape=[batch_size,32,32,32], strides=[1,2,2,1], batch_norm=True, reuse=reuse, varscope='g_trans3',namescope='generator')
	state = trans2d_layer(layer_input=state, W_shape=[5,5,16,32], output_shape=[batch_size,64,64,16], strides=[1,2,2,1], batch_norm=True, reuse=reuse, varscope='g_trans4',namescope='generator')
	state = trans2d_layer(layer_input=state, W_shape=[5,5,1,16], b_shape=[0], output_shape=[batch_size,64,64,1], strides=[1,1,1,1], activation=tf.nn.tanh, batch_norm=False, reuse=reuse, varscope='g_trans5',namescope='generator')
	return state

# ####################################
# ####### Distinguisher Setup ########
# ####################################
def distinguisher(X, reuse=False):
	state = conv2d_layer(layer_input=X, W_shape=[6,6,1,64], b_shape=[0], strides=[1,2,2,1], activation=lrelu, reuse=reuse, varscope='d_conv1', namescope='distinguisher') # ==> ?
	state = conv2d_layer(layer_input=state, W_shape=[4,4,64,64], strides=[1,2,2,1], activation=lrelu, batch_norm=False, reuse=reuse, varscope='d_conv2', namescope='distinguisher') # ==> ?
	state = tf.nn.dropout(state,drop[0])
	state = conv2d_layer(layer_input=state, W_shape=[4,4,64,128], strides=[1,2,2,1], activation=lrelu, batch_norm=False, reuse=reuse, varscope='d_conv3', namescope='distinguisher') 
	state = tf.nn.max_pool(state, ksize=[1,2,2,1], strides=[1,2,2,1], padding="SAME")
	state = tf.reshape(state, [batch_size,128*4*4])
	state = tf.nn.dropout(state,drop[0])
	state = dense_layer(state, [128*4*4,1], activation=tf.nn.sigmoid, reuse=reuse, varscope='d_fc2', namescope='distinguisher')
	return state

# ##################################################################
# ################ Definition of Data Flow Graph ###################
# ##################################################################

#todo add comm
tf.reset_default_graph()
initializer = tf.truncated_normal_initializer(stddev=0.02)

# # define placeholders for input
Z = tf.placeholder(dtype=tf.float32, shape=[None,Z_size])
X = tf.placeholder(dtype=tf.float32, shape=[None,64,64,1])
drop = tf.placeholder(dtype=tf.float32,shape=[2])

# define instances of data flow
Gz = generator(Z) # generates images from Z
Dx = distinguisher(X) # produces probabilities for real images
Dg = distinguisher(Gz, reuse=True) # produces probabilities for generator images

# ####################################
# ########## Training Setup ##########
# ####################################

D_lossfun = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=tf.squeeze(Dx), labels=tf.ones(batch_size,1)) \
						 + tf.nn.sigmoid_cross_entropy_with_logits(logits=tf.squeeze(Dg), labels=tf.zeros(batch_size,1)))
G_lossfun = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=tf.squeeze(Dg), labels=tf.ones(batch_size,1)))

#G_perf = tf.reduce_mean(tf.equal(tf.round(Dg),tf.ones(batch_size,1)))
Dx_perf = tf.reduce_mean(tf.cast(tf.equal(tf.round(Dx),tf.ones(batch_size,1)),"float"))
Dg_perf = tf.reduce_mean(tf.cast(tf.equal(tf.round(Dg),tf.zeros(batch_size,1)),"float"))

# define which variables to optimize
train_vars = tf.trainable_variables()
D_vars = [var for var in train_vars if 'd_' in var.name]
G_vars = [var for var in train_vars if 'g_' in var.name]

# define optimizer
D_optimizer = tf.train.AdamOptimizer(learning_rate=0.0002,beta1=0.5)
G_optimizer = tf.train.AdamOptimizer(learning_rate=0.0002,beta1=0.5)
 
# compute gradients
D_gradients = D_optimizer.compute_gradients(D_lossfun,D_vars) #Only update the weights for the distinguisher network.
G_gradients = G_optimizer.compute_gradients(G_lossfun,G_vars) #Only update the weights for the generator network.

# apply gradients
D_update = D_optimizer.apply_gradients(D_gradients)
G_update = G_optimizer.apply_gradients(G_gradients)


# ##################################################################
# ##################### Training of Network ########################
# ##################################################################

if print_varnames:
	print('\nVARIABLE NAMES:\n----------------------------------------------------\n')
	print([v.name for v in tf.trainable_variables()])

init = tf.global_variables_initializer()
saver = tf.train.Saver(max_to_keep=10, keep_checkpoint_every_n_hours=1.0, write_version=tf.train.SaverDef.V1)
with tf.Session() as sess:  
	sess.run(init)

	print('')
	print('TRAINING:')
	print('-----------------------------------------------------------------------')
	
	if restore_weights:
		if os.path.isfile(model_dir+'/model.ckpt'): # model name needs to be changed manually
			saver.restore(sess, model_dir+'/model.ckpt')
			print('')
			print(' ==> model restored from file')
	
	G_loss_history = []
	D_loss_history = []

	D_fake_history = []
	D_real_history = []

	D_update_history = []
	G_update_history = []
	
	D_optimize = True
	G_optimize = True

	# first dis dropout, second gen dropout
	dropout = np.array([0.5,0.5])

	z_sample = np.random.uniform(-1.0,1.0, size=[batch_size,Z_size]).astype(np.float32) # generate a z batch

	dis_up = 0
	gen_up = 0

	for i in range(n_batches):

		tf.reset_default_graph()
		tf.set_random_seed(1)

		# create inputs
		z_in = np.random.uniform(-1.0, 1.0, size=[batch_size,Z_size]).astype(np.float32)
		x_in = sampleGen.get_batch(batch_size) # Devrim Changed this

		# update distinguisher and generator
		if D_optimize:
			dis_up = dis_up + 1
			_,D_loss = sess.run([D_update,D_lossfun],feed_dict={Z: z_in, X: x_in, drop: dropout})
		
		D_fake,D_real = sess.run([Dg_perf,Dx_perf],feed_dict={Z: z_in, X: x_in, drop: np.array([1.0,1.0])})
		D_optimize, G_optimize = check_update(D_fake,D_real,0.8,0.5)

		if G_optimize:
			gen_up = gen_up + 1
			_,G_loss = sess.run([G_update,G_lossfun],feed_dict={Z: z_in, drop: dropout})
			z_in = np.random.uniform(-1.0, 1.0, size=[batch_size,Z_size]).astype(np.float32)
			_,G_loss = sess.run([G_update,G_lossfun],feed_dict={Z: z_in, drop: dropout})

		# print progress after n=printFreq batches
		if (i+1)%printFreq == 0 or (i+1) == n_batches:
			print('batch '+str(i+1)+'/'+str(n_batches))
			print('   gen loss: ' + str(G_loss) + '\n   dis loss: ' + str(D_loss))
			print('   dis acc fake: ' + str(D_fake) + '\n   dis acc real: ' + str(D_real))
			print("dis updates: %.1f" % ((dis_up/(printFreq))*100))
			print("gen updates: %.1f" % ((gen_up/(printFreq))*100))

			G_loss_history.append(G_loss)
			D_loss_history.append(D_loss)

			D_fake_history.append(D_fake)
			D_real_history.append(D_real)

			D_update_history.append((dis_up/(printFreq))*100)
			G_update_history.append((gen_up/(printFreq))*100)

			dis_up = 0
			gen_up = 0

		# save samples documenting progress after n=sampleFreq batches
		if (i+1)%sampleFreq == 0 or (i+1) == n_batches:
			# z_sample = np.random.uniform(-1.0,1.0, size=[batch_size,Z_size]).astype(np.float32) # generate another z batch
			Gz_sample = sess.run(Gz, feed_dict={Z: z_sample, drop: np.array([1.0,1.0])}) # use new z to get sample images from generator
			if i==0:
				print(Gz_sample.shape)
			merge_and_save(np.reshape(Gz_sample[0:36],[36,64,64]),[6,6],sample_dir+'/fig'+str(i)+'.png')

		# save model weights after n=saveFreq batches
		if (i+1)%saveFreq == 0 or (i+1) == n_batches:
			saver.save(sess,model_dir+'/model.ckpt', global_step=i)
			print(' ==> model saved (b'+str(i+1)+')')

	print('')

# ##################################################################
# ######################## Training Plots ##########################
# ##################################################################

plt.figure()
plt.subplot(311)
plt.plot(np.array(G_loss_history),label="gen loss")
plt.plot(np.array(D_loss_history),label="dis loss")
plt.legend()
plt.subplot(312)
plt.plot(np.array(D_fake_history),label="dis fake acc")
plt.plot(np.array(D_real_history),label="dis real acc")
plt.legend()
plt.subplot(313)
plt.plot(np.array(D_update_history),label="% dis update")
plt.plot(np.array(G_update_history),label="% gen update")
plt.legend()
if not os.path.exists(sample_dir):
	os.makedirs(sample_dir)
plt.savefig(sample_dir+'/0_stats.png')

# # ########################
# # ### IMAGE GENERATION ###
# # ########################

# init = tf.global_variables_initializer()
# saver = tf.train.Saver()
# with tf.Session() as sess:  
# 	sess.run(init)

# 	print('')
# 	print('IMAGE GENERATION:')
# 	print('-----------------------------------------------------------------------')

# 	# restore latest weights
# 	ckpt = tf.train.get_checkpoint_state(model_dir)
# 	saver.restore(sess,ckpt.model_checkpoint_path)

# 	# generate one batch of samples
# 	z_sample = np.random.uniform(-1.0,1.0, size=[batch_size,Z_size]).astype(np.float32) # generate another z batch
# 	Gz_sample = sess.run(Gz, feed_dict={Z: z_sample}) # use new z to get sample images from generator
# 	if not os.path.exists(sample_dir):
# 		os.makedirs(sample_dir)
# 	save_images(np.reshape(Gz_sample[0:36],[36,32,32]),[6,6],sample_dir+'/fig'+str(i)+'.png')
			
# 	print('done')

# print('')

# ############
# ### INFO ###
# ############

# output layer size for transposed convolution:
# a := extra padding (for transposed conv), a = (i+2p-k)%s
# o := output size (non-transposed), o = ceil((i+2p-k+1)/s) [confirm?]
# o':= output size (transposed), o'=i, o'= s(i'-1)+k-2p+a
# i := input size (non-transposed), user-defined
# i':= input size (transposed), i'=o
# k := kernel size (non-transposed), user-defined
# k':= kernel size (transposed), k'=k
# s := stride (non-transposed)
# s':= stride (transposed), 's'=1/s'
# p := padding (in pixels, non-transposed), user-defined
# p':= padding (transposed), p'=k-p-1
# half (same) padding => p = floor(k/2)

# check weights
# if i == 1:
# 	weights7, biases7 = session.run(['layer7/weights:0', 'layer7/biases:0'])
# 	weights = np.squeeze(weights7)
# 	print(weights.shape)
# 	print(weights[:,:,5,8])