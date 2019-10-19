import os,sys,time
from _lbm_cffi import ffi,lib

#source event callback
@ffi.def_extern()
def handle_src_event(src,event,ed,cd):
	if event == lib.LBM_SRC_EVENT_CONNECT:
		clientname = ffi.string(ffi.cast("const char *",ed))
		print("Receiver connect ["+clientname+"]")

	elif event == lib.LBM_SRC_EVENT_DISCONNECT:
		clientname = ffi.string(ffi.cast("const char *",ed))
		print("Receiver disconnect ["+clientname+"]")

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

#read the config file
if lib.lbm_config("um.cfg") == lib.LBM_FAILURE:
	print("Note, failed to read config file um.cfg: " + ffi.string(lib.lbm_errmsg()))

#create the context attribute
p_cattr = ffi.new("lbm_context_attr_t **")
if lib.lbm_context_attr_create(p_cattr) == lib.LBM_FAILURE:
	print("failed iin lbm_context_attr_create: " + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the attribute pointer
cattr = p_cattr[0]

#create the topic attribute
p_tattr = ffi.new("lbm_src_topic_attr_t **")
if lib.lbm_src_topic_attr_create(p_tattr) == lib.LBM_FAILURE:
	print("failed in lbm_src_topic_attr_create: " + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the attribute pointer
tattr = p_tattr[0]


#create the context
p_ctx = ffi.new("lbm_context_t **")
if lib.lbm_context_create(p_ctx,cattr,ffi.NULL,ffi.NULL) == lib.LBM_FAILURE:
	print("failed in lbm_context_create: " + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the context pointer
ctx = p_ctx[0]

#delete the context attribute
lib.lbm_context_attr_delete(cattr)

#Allocate the desired topic
p_topic = ffi.new("lbm_topic_t **")
if lib.lbm_src_topic_alloc(p_topic, ctx, "test", tattr) == lib.LBM_FAILURE:
	print("failed in lbm_src_topic_alloc" + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the topic object
topic = p_topic[0]

#create the source
p_src = ffi.new("lbm_src_t **")
if lib.lbm_src_create(p_src, ctx, topic, lib.handle_src_event, ffi.NULL, ffi.NULL) == lib.LBM_FAILURE:
	print("failed in lbm_src_create" + ffi.string(lib.lbm_errmsg()))
	sys.exit(1)

#get the source object
src = p_src[0]

#send messages
message = ffi.new("char [2000]","")

#let topic res complete
time.sleep(1)

for i in range(100000):
	message = "message%d" % i
	err = lib.lbm_src_send(src,message,2000,lib.LBM_SRC_NONBLOCK)
	if err == lib.LBM_FAILURE:
		print("failed in lbm_src_send: " + ffi.string(lib.lbm_errmsg()))
		sys.exit(1)

#cleanup
print("Deleting source")
lib.lbm_src_delete(src)
print("Deleting context")
lib.lbm_context_delete(ctx)
