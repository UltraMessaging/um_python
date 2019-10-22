# lbmtst.py - simple um receiver program.
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

import time
from _lbm_cffi import ffi, lib


class LbmRcvCallback(object):
    'Helper class to allow a single cffi wrapper for any application.'
    def __init__(self, app_rcv_callback, app_clientd):
        'Instantiate a callback object.'
        self.app_rcv_callback = app_rcv_callback
        self.app_clientd = app_clientd

    def lbm_rcv_deliver(self, rcv, msg):
        'Called by pylbm_rcv_cb_proc to invoke application callback.'
        self.app_rcv_callback(rcv, msg, self.app_clientd)


@ffi.def_extern()
def pylbm_rcv_cb_proc(rcv, msg, clientd):
    'Callback from wrapper. clientd is LbmRcvCallback object'
    lbm_rcv_callback = ffi.from_handle(clientd)
    lbm_rcv_callback.lbm_rcv_deliver(rcv, msg)
    return 0


def app_on_receive_event(rcv, msg, app_state):
    'Application receiver event callback.'
    if msg.type == lib.LBM_MSG_DATA:
        data = ffi.string(ffi.cast('char *', msg.data))
        topic_name = ffi.string(ffi.cast('char *', msg.topic_name))
        src = ffi.string(ffi.cast('char *', msg.source))
        print('Msg:' + data.decode('utf-8') + '[' + topic_name.decode('utf-8') +
              ':' + src.decode('utf-8') + ':' + str(msg.sequence_number) +
              '], state=' + str(app_state))


@ffi.def_extern()
def pylbm_src_cb_proc(src, event, event_data, clientd):
    'UM source event application callback.'
    if event == lib.LBM_SRC_EVENT_CONNECT:
        clientname = ffi.string(ffi.cast('const char *', event_data))
        print('Receiver connect ['+clientname.decode('utf-8')+']')

    elif event == lib.LBM_SRC_EVENT_DISCONNECT:
        clientname = ffi.string(ffi.cast('const char *', event_data))
        print('Receiver disconnect ['+clientname.decode('utf-8')+']')

    return 0


@ffi.def_extern()
def pylbm_log_cb_proc(level, message, clientd):
    'UM logger application callback.'
    print(ffi.string(message).decode('utf-8'))
    return 0


def lbmerr(err):
    'Very simple, programmer-friendly (user-hostile) error checker.'
    assert err != lib.LBM_FAILURE, ffi.string(lib.lbm_errmsg())


def main():
    'Put "main" program in a function to allow callable.'
    # Setup logging callback.
    lbmerr(lib.lbm_log(lib.pylbm_log_cb_proc, ffi.NULL))

    # Read the config file.
    err = lib.lbm_config(b'um.cfg')
    if err == lib.LBM_FAILURE:
        print("Warning, lbm_config 'um.cfg' error: " +
              str(ffi.string(lib.lbm_errmsg())))

    # Create the context attribute.
    p_cattr = ffi.new('lbm_context_attr_t **')
    lbmerr(lib.lbm_context_attr_create(p_cattr))
    # Get the attribute pointer.
    cattr = p_cattr[0]

    # Create the context.
    p_ctx = ffi.new('lbm_context_t **')
    lbmerr(lib.lbm_context_create(p_ctx, cattr, ffi.NULL, ffi.NULL))
    #get the context pointer
    ctx = p_ctx[0]

    # Delete the context attribute.
    lib.lbm_context_attr_delete(cattr)

    # Create the receiver topic attribute.
    p_rcv_tattr = ffi.new('lbm_rcv_topic_attr_t **')
    lbmerr(lib.lbm_rcv_topic_attr_create(p_rcv_tattr))
    # Get the attribute pointer.
    rcv_tattr = p_rcv_tattr[0]

    # Lookup for the receiver topic.
    p_topic = ffi.new('lbm_topic_t **')
    lbmerr(lib.lbm_rcv_topic_lookup(p_topic, ctx, b'lbmtst.py', rcv_tattr))
    # Get the topic object.
    topic = p_topic[0]

    # Set some application state.
    app_state = {'abc':123}
    main.app_state_handle = ffi.new_handle(app_state)

    # Create the callback object.
    lbm_rcv_callback = LbmRcvCallback(app_on_receive_event, app_state)
    callback_handle = ffi.new_handle(lbm_rcv_callback)

    # Create the receiver.
    p_rcv = ffi.new('lbm_rcv_t **')
    lbmerr(lib.lbm_rcv_create(p_rcv, ctx, topic, lib.pylbm_rcv_cb_proc,
                              callback_handle, ffi.NULL))
    # Get the receiver object.
    rcv = p_rcv[0]
    print('Receiver created for lbmtst.py topic')

    # Delete the topic attribute.
    lib.lbm_rcv_topic_attr_delete(rcv_tattr)

    # Create the source topic attribute.
    p_src_tattr = ffi.new('lbm_src_topic_attr_t **')
    lbmerr(lib.lbm_src_topic_attr_create(p_src_tattr))
    # Get the attribute pointer.
    src_tattr = p_src_tattr[0]
    print('source topic created')

    # Allocate the desired source topic.
    p_topic = ffi.new('lbm_topic_t **')
    lbmerr(lib.lbm_src_topic_alloc(p_topic, ctx, b'lbmtst.py', src_tattr))
    # Get the topic object.
    topic = p_topic[0]

    # Create the source.
    p_src = ffi.new('lbm_src_t **')
    lbmerr(lib.lbm_src_create(p_src, ctx, topic, lib.pylbm_src_cb_proc,
                              ffi.NULL, ffi.NULL))
    # Get the source object.
    src = p_src[0]
    print('source created')

    # Delete the topic attribute.
    lib.lbm_src_topic_attr_delete(src_tattr)

    # Let topic res complete.
    time.sleep(1)
    print('TR complete')

    # Publish 50 messages.
    for i in range(50):
        message = ('message%d' % i).encode('utf-8')
        lbmerr(lib.lbm_src_send(src, message, len(message), lib.LBM_SRC_BLOCK))

    # Let messages be delivered.
    time.sleep(1)

    # Cleanup.
    print('Deleting receiver')
    lbmerr(lib.lbm_rcv_delete(rcv))

    print('Deleting source')
    lbmerr(lib.lbm_src_delete(src))

    print('Deleting context')
    lbmerr(lib.lbm_context_delete(ctx))


# Make this program importable. Only run it if it is executed directly.
if __name__ == '__main__':
    main()
