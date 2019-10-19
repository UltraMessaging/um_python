# lbmrcv.py - simple um receiver program.
#
# Copyright (c) 2019 Informatica Corporation. All Rights Reserved.
# Permission is granted to licensees to use
# or alter this software for any purpose, including commercial applications,
# according to the terms laid out in the Software License Agreement.
#
# This source code example is provided by Informatica for educational
# and evaluation purposes only.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND INFORMATICA DISCLAIMS ALL WARRANTIES
# EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF
# NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR
# PURPOSE.  INFORMATICA DOES NOT WARRANT THAT USE OF THE SOFTWARE WILL BE
# UNINTERRUPTED OR ERROR-FREE.  INFORMATICA SHALL NOT, UNDER ANY CIRCUMSTANCES,
# BE LIABLE TO LICENSEE FOR LOST PROFITS, CONSEQUENTIAL, INCIDENTAL, SPECIAL OR
# INDIRECT DAMAGES ARISING OUT OF OR RELATED TO THIS AGREEMENT OR THE
# TRANSACTIONS CONTEMPLATED HEREUNDER, EVEN IF INFORMATICA HAS BEEN APPRISED OF
# THE LIKELIHOOD OF SUCH DAMAGES.

import os,sys,time
from _lbm_cffi import ffi,lib

done = 0

#receiver event callback
@ffi.def_extern()
def rcv_handle_msg(rcv, msg, clientd):
	if msg.type == lib.LBM_MSG_DATA:
		data = ffi.string(ffi.cast("char *",msg.data))
		topic_name = ffi.string(ffi.cast("char *",msg.topic_name))
		src = ffi.string(ffi.cast("char *",msg.source))
		seq_num = "%d" % msg.sequence_number
		print("Data msg:" + data + "[" + topic_name + ":" + src + ":" + seq_num + "]")

	#elif msg.type == lib.LBM_SRC_EVENT_DISCONNECT:
	#	clientname = ffi.string(ffi.cast("const char *",ed))
	#	print("Receiver disconnect ["+clientname+"]")

	return 0

#application logging callback
@ffi.def_extern()
def lbm_log_msg(level,message,clientd):
	print(ffi.string(message))
	return 0

#Setup logging callback
if lib.lbm_log(lib.lbm_log_msg,ffi.NULL) == lib.LBM_FAILURE:
	print("failed in lbm_log: " + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#create the context attribute
p_cattr = ffi.new("lbm_context_attr_t **")
if lib.lbm_context_attr_create(p_cattr) == lib.LBM_FAILURE:
	print("failed in lbm_context_attr_create: " + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the attribute pointer
cattr = p_cattr[0]

#create the context
p_ctx = ffi.new("lbm_context_t **")
if lib.lbm_context_create(p_ctx,cattr,ffi.NULL,ffi.NULL) == lib.LBM_FAILURE:
	print("failed in lbm_context_create: " + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the context pointer
ctx = p_ctx[0]

#delete the context attribute
lib.lbm_context_attr_delete(cattr)

#create the topic attribute
p_tattr = ffi.new("lbm_rcv_topic_attr_t **")
if lib.lbm_rcv_topic_attr_create(p_tattr) == lib.LBM_FAILURE:
	print("failed in lbm_rcv_topic_attr_create: " + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the attribute pointer
tattr = p_tattr[0]

#lookup for the topic
p_topic = ffi.new("lbm_topic_t **")
if lib.lbm_rcv_topic_lookup(p_topic,ctx, "test", tattr) == lib.LBM_FAILURE:
	print("failed in lbm_rcv_topic_lookup" + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the topic object
topic = p_topic[0]

#create the receiver
p_rcv = ffi.new("lbm_rcv_t **")
if lib.lbm_rcv_create(p_rcv, ctx, topic, lib.rcv_handle_msg, ffi.NULL, ffi.NULL) == lib.LBM_FAILURE:
	print("failed in lbm_rcv_create" + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the receiver object
rcv = p_rcv[0]
print("Receiver created for test topic")

#run forever till done
while True:
	if done == 1:
		break

#cleanup
print("Deleting receiver")
lib.lbm_rcv_delete(rcv)
print("Deleting context")
lib.lbm_context_delete(ctx)
