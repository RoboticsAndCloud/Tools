#!/noah/bin/python2.7
# -*- coding: UTF-8 -*-
"""
*eventbus* 提供eventbus功能

"""
################################################################################
#
# Copyright (c) 2016 Baidu.com, Inc. All Rights Reserved
#
################################################################################
#std
import sys
try:
    sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)
except TypeError:
    reload(sys)
    sys.setdefaultencoding('utf-8')
import os
import httplib
import urllib
import json
import time
import datetime
import socket
import itertools
import logging
import traceback
import threading

from sdkcache import ExpiringDict
import time
from threading import Thread

DEFAULT_SIZE_FILTER_CACHE = 1000
DEFAULT_TTL_FILTER_CACHE = 20
SIZE_FILTER_THREADSHOLD = 3
SECONDS_FILTER_THREADSHOLD = 3


#3rd package
if __name__ == "__main__":
    __workdir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append("%s/.." % __workdir)

from inner import stomp
from inner.stomp import exception
import md5

#local package
from inner import config

#
__logger_name = "eventbus-sdk-python"
log = logging.getLogger(__logger_name)

def get_logger_name():
    """
    get_logger_name()
    """
    return __logger_name


class FilterCacheWorker(Thread):
    def __init__(self, cache, size_filter_threadshold, seconds_filter_threadshold):
        Thread.__init__(self)
        self.cache = cache
        self.size_filter_threadshold = size_filter_threadshold
        self.seconds_filter_threadshold = seconds_filter_threadshold

    def run(self):
        # for x in range(180):
        #     print(x)
       while True:
            # Get the work from the queue and expand the tuple
            time.sleep(self.seconds_filter_threadshold)

            if self.cache.__len__() > self.size_filter_threadshold:
                log.debug('FilterCacheWorker : self.cache.__len__()=%d, size_filter_threadshold=%d'
% (self.cache.__len__(), self.size_filter_threadshold))
                keys = self.cache.keys()
                for key in keys:
                    self.cache.ttl(key)

# 消息侦听器
class MQListener(object):
    """
    mqlistener

    """

    def __init__(self, a_filter_cache=None):
        self.eventbus = None
        self.user_on_message = None
        self.user_on_error = None
        self.filter_list_oo = {}
        self.userdata = None
        self.tstampms_last_heartbeat = 0
        self.tstampms_last_message   = 0
        self.thr_keeper = None
        self.b_connected = False

        self.filter_map_state = {}
        self.on_disconnected = self.cb_on_disconnected
        if a_filter_cache is not None:
            self.filter_cache = a_filter_cache
        else:
            try:
                self.filter_cache = ExpiringDict(DEFAULT_SIZE_FILTER_CACHE, DEFAULT_TTL_FILTER_CACHE)
            except Exception as e:
                print('error%s' % (str(e)))
        log.debug('filterCache.max_age:%d' %(self.filter_cache.max_age))
        log.debug('filterCache.max_len:%d' %(self.filter_cache.max_len))


    def on_error(self, headers, message):
        """
        mqlistener on_error cb

        """
        log.debug('on_error() received an error %s' % message)
        if self.user_on_error is not None:
            self.user_on_error(self.userdata)

        return None

    def on_message(self, headers, message):
        """
        mqlistener on_message cb

        """
        b_exist = False
        js_tmp = None
        self.tstampms_last_message = time.time() * 1000
        log.debug('on_message() : headers[%s] message[%s]' % (headers, message.decode('utf-8')))
        log.debug('on_message() : self.filter_list_oo [%s]' % (str(self.filter_list_oo)))

        if self.user_on_message is not None:
            try:
                js_tmp = json.loads(message)
                if len(self.filter_list_oo) > 0:
                    if "opObject" not in js_tmp:
                        return None
                    for it in js_tmp["opObject"]:
                        if "name" not in it:
                            continue
                        elif it["name"] in self.filter_list_oo:
                            b_exist = True
                    if "impactedOpObject" in js_tmp:
                        for it in js_tmp["impactedOpObject"]:
                            if "name" not in it:
                                continue
                            elif it["name"] in self.filter_list_oo:
                                b_exist = True
                    if b_exist == False:
                        return None
                if len(self.filter_map_state) > 0:
                    if "state" in js_tmp and js_tmp["state"] not in self.filter_map_state:
                        return None
            except Exception as e:
                log.warning("on_message(): [%s]" % (str(e)))
                return None
            log.debug('user_on_message() : headers[%s] message[%s]' % (headers,
                message.decode('utf-8')))

            # construce message_key for filter
            message_key = ""
            if "uid" in js_tmp:
                message_key += js_tmp["uid"]
            if "state" in js_tmp:
                message_key += "_" + js_tmp["state"]
            if message_key.strip() == "":
                return None

            if self.filter_cache.get(message_key) is not None:
                log.debug('message duplicate got, filterCacheLen: %d, message_key %s, value: %s' %
(self.filter_cache.__len__(),  message_key, self.filter_cache.get(message_key)))

                return None

            self.filter_cache.__setitem__(message_key, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            self.user_on_message(headers, message, self.userdata)
        return None

    def on_connected(self, headers, message):
        """
        mqlistener on_connected cb

        """
        log.debug("on_connected(): headers[%s] message[%s]" % (headers, message))
        self.eventbus.lock_conn.acquire()
        self.b_connected = True
        self.tstampms_last_heartbeat = time.time() * 1000
        self.eventbus.lock_conn.release()

        return None

#    def on_send(self, headers, message):
    def on_send(self, headers):
        """
        mqlistener on_send cb

        """
#        log.debug("on_send(): headers[%s] message[]" % (str(headers)))
        return None

    def cb_on_disconnected(self):
        """ cb_on_disconnected """
        log.warning("on_disconnected()")
#        self.eventbus.lock_conn.acquire()
        self.b_connected = False
#        self.eventbus.lock_conn.release()

    def on_heartbeat(self):
        """
        on_heartbeat
        """
        log.debug("on_heartbeat()")
#        self.eventbus.lock_conn.acquire()
        self.tstampms_last_heartbeat = time.time() * 1000
#        self.eventbus.lock_conn.release()
        return

    def on_heartbeat_timeout(self):
        """
        on_heartbeat_timeout
        """
        log.warning("on_heartbeat_timeout()")


class ThreadingMQConnection(threading.Thread):
    def __init__(self, ebus):
        threading.Thread.__init__(self)
        self.ebus = ebus
        self.running_flag = True

    def run(self):
        count_sleep = 0
        while (self.running_flag is True) and (count_sleep < 100):
            time.sleep(.05)
            count_sleep += 1
        while self.running_flag is True:
#            b_reconnect = True #TODO debug
            b_reconnect = False
            tstampms_now = time.time() * 1000

            log.debug("before lock acquire")
            self.ebus.lock_conn.acquire()
            log.debug("after  lock acquire")

            log.debug("[ebus.conn.is_connected() = %s]\n"
                    "[heartbeat_delta = %s]\n"
                    "[mqlistener.b_connected = %s]\n"
                    "[tstampms_now - self.ebus.mqlistener.tstampms_last_message = %s]"
                    %
                    (
                     str(self.ebus.conn.is_connected()),
                     str(tstampms_now - self.ebus.mqlistener.tstampms_last_heartbeat),
                     str(self.ebus.mqlistener.b_connected),
                     str(tstampms_now - self.ebus.mqlistener.tstampms_last_message)
                    )
                    )

            if self.ebus.conn.is_connected() is not True or \
                    tstampms_now - self.ebus.mqlistener.tstampms_last_heartbeat > \
                    self.ebus.heartbeat * 20 or \
                    self.ebus.mqlistener.b_connected is False or \
                    tstampms_now - self.ebus.mqlistener.tstampms_last_message > \
                    self.ebus.heartbeat * 12:
                    b_reconnect = True
                    log.debug("[ebus.conn.is_connected() = %s]\n"
                            "[heartbeat_delta = %s]\n"
                            "[mqlistener.b_connected = %s]\n" %
                            (
                                str(self.ebus.conn.is_connected()),
                                str(tstampms_now - self.ebus.mqlistener.tstampms_last_heartbeat),
                                str(self.ebus.mqlistener.b_connected),
                                )
                            )
            log.debug("before lock release")
            self.ebus.lock_conn.release()
            log.debug("after  lock release")

            if b_reconnect:
                try:
                    log.debug("before reconnect")
                    self.ebus.reconnect()
                    log.debug("after reconnect")
                    log.debug("before resubscribe")
                    self.ebus.resubscribe()
                    log.debug("after resubscribe")
                except Exception as e:
                    log.warning("reconnect/resubscribe failed. err=[%s] traceback:[%s]" % (str(e),
                                traceback.format_exc()))

            time.sleep(.05) #50ms

    def stop(self):
        self.running_flag = False
        self.join()

class EventbusDisasterTolerance(object):
    def __init__(self, default_config=None, default_config_backup=None):
        """
        :return:

        """
        self.size_filter_cache = DEFAULT_SIZE_FILTER_CACHE
        self.ttl_filter_cache = DEFAULT_TTL_FILTER_CACHE
        self.size_filter_threadshold = SIZE_FILTER_THREADSHOLD
        self.seconds_filter_threadshold = SECONDS_FILTER_THREADSHOLD
        self.default_config = config.default_config
        self.default_config_backup = config.default_config_backup

        if config.filter_cache_default_config is not None:
            self.size_filter_cache = config.filter_cache_default_config["size_filter_cache"]
            # message in filter_cache default ttl 
            self.ttl_filter_cache = config.filter_cache_default_config["ttl_filter_cache"]
            # filter_cache threadshold size, to clear the expire message from filter_cache    
            self.size_filter_threadshold = config.filter_cache_default_config["size_filter_threadshold"]
            # cycle of clearing the filter_cache        
            self.seconds_filter_threadshold = config.filter_cache_default_config["seconds_filter_threadshold"]
        if default_config is not None:
            self.default_config = default_config
        if default_config_backup is not None:
            self.default_config_backup = default_config_backup

        try:
            self.filter_cache = ExpiringDict(self.size_filter_cache, self.ttl_filter_cache)
        except Exception as e:
            print('error%s' % (str(e)))


        self.worker = FilterCacheWorker(self.filter_cache, self.size_filter_threadshold,
self.seconds_filter_threadshold)
        self.worker.daemon = True
        self.worker.start()
            
    def subscribe(self, filter=None, on_message=None, userdata=None, on_error=None):
        self.ev1 = Eventbus(self.default_config, self.filter_cache) 
        self.ev_backup = Eventbus(self.default_config_backup, self.filter_cache)
        self.ev1.subscribe(filter, on_message, userdata, on_error)
        self.ev_backup.subscribe(filter, on_message, userdata, on_error)
    def unsubscribe(self):
        self.ev1.unsubscribe()
        self.ev_backup.unsubscribe()


class Eventbus(object):
    """
    eventbus的客户端lib

    """

    #entityType/transType
    EVENTBUS_OO_TYPE_STR_APP        =   "app"
    EVENTBUS_OO_TYPE_STR_SERVICE    =   "service"
    EVENTBUS_OO_TYPE_STR_INSTANCE   =   "instance"
    EVENTBUS_OO_TYPE_STR_HOST       =   "host"

    #eType
    EVENTBUS_EVENT_TYPE_STR_WARNING =   "warning"
    EVENTBUS_EVENT_TYPE_STR_ALERT   =   "alert"
    EVENTBUS_EVENT_TYPE_STR_NORMAL  =   "normal"
    EVENTBUS_EVENT_TYPE_STR_ABNORMAL=   "abnormal"

    EVENTBUS_OO_TYPE_STRS = (EVENTBUS_OO_TYPE_STR_APP,
                             EVENTBUS_OO_TYPE_STR_SERVICE,
                             EVENTBUS_OO_TYPE_STR_INSTANCE,
                             EVENTBUS_OO_TYPE_STR_HOST,
                             )

    EVENTBUS_EVENT_TYPE_STRS = (EVENTBUS_EVENT_TYPE_STR_WARNING,
                                EVENTBUS_EVENT_TYPE_STR_ALERT,
                                EVENTBUS_EVENT_TYPE_STR_NORMAL,
                                EVENTBUS_EVENT_TYPE_STR_ABNORMAL,)

    def __init__(self, a_config=None, filter_cache=None):
        """
        :return:

        """
        self.b_subscribed = False
        self.heartbeat = 5000   #TODO for debug
        self.b_first_subscribe = False
#        self.list_subscribed = []
        self.heartbeats = (self.heartbeat, self.heartbeat)
        hb = None
        self.conf = {}
        self.lock_conn = threading.Lock()
        self.thr_keeper = ThreadingMQConnection(self)
        self.filter = None

        try:
            self.conf = config.default_config

            if filter_cache is not None:
                self.mqlistener = MQListener(filter_cache)
            else:
                self.mqlistener = MQListener()

            self.mqlistener.eventbus = self

            if a_config is not None:
                self.conf = a_config

            self.conn = stomp.Connection(self.conf["servers_activemq"], heartbeats=self.heartbeats,
                    reconnect_attempts_max = 30)
#            self.conn = stomp.Connection(self.conf)
#            hb = stomp.utils.calculate_heartbeats(('1000', '1000'), (1000, 1000))
#            log.debug("calculate_heartbeats() = %s" % str(hb))

            # 设置消息侦听器
            self.conn.set_listener('', self.mqlistener)
            # 启动连接
            self.conn.start()
            ret = self.conn.connect(wait = True)

#            print("connect()=%s" % (str(ret)));

            if 0 > 0:
                ret = self.conn.subscribe(destination='/queue/foo', id=2, ack='auto')
#                ret = self.conn.send("/queue/foo", "abcdefg")
                time.sleep(3)
        except Exception as e:
            raise e

        try:
            log.debug("before thr_keeper start")
            self.thr_keeper.start()
            log.debug("after thr_keeper start")
        except Exception as e:
            raise e

        return None

    def resubscribe(self):
        """
        resubscribe
        """
#        self.list_subscribed[:] = []
#        if self.b_subscribed is True:
        log.debug("[self.filter=%s] [self.conn.is_connected()=%d]" % (self.filter,
            self.conn.is_connected()))
        try:
            if self.conn.is_connected():
                self.subscribe(self.filter, self.on_message, self.userdata)
                log.debug("resubscribe() successed.")
        except:
            pass

    def reconnect(self):
        try:
            log.debug("before lock acquire")
            self.lock_conn.acquire()
            log.debug("after  lock acquire")
            self.__reconnect()
        except Exception as e:
            raise e
        except socket.error as e:
            raise Exception(str(e))
        finally:
            log.debug("before lock release")
            self.lock_conn.release()
            log.debug("after  lock acquire")

    def __reconnect(self):
        """
        reconnect
        """
        try:
            self.mqlistener.on_disconnected = None
            try:
                self.conn.unsubscribe(id=2)
            except stomp.exception.NotConnectedException as e:
                pass
            try:
                self.conn.disconnect()
            except stomp.exception.NotConnectedException as e:
                pass
            try:
                self.conn.stop()
            except stomp.exception.NotConnectedException as e:
                pass
            log.debug("stop() successed.")
        except Exception as e:
            log.warning("__reconnect() error: %s" % (str(e)))
            return None
            pass
        time.sleep(.8)
        self.mqlistener.on_disconnected = self.mqlistener.cb_on_disconnected
        log.debug(".")
        self.conn.set_listener('', self.mqlistener)
        log.debug(".")
        self.conn.start()
        log.debug(".")
        try:
            self.conn.connect(wait = False)
            time.sleep(.8)
        except stomp.exception.ConnectFailedException:
            log.debug("reconnect() connect() failed. retry.")
            pass

        log.debug("reconnect() successed.")


#    """ fn_publish
#        publish message in many way
#
#        :param ev <class Eventbus>: Eventbus item
#        :param hit_item:
#        :param event_type: 
#        :param event_type_in_url: 
#        :param ev_ids <dict>: 
#            identifier list, for duplicate
#        :param int_epoch <int>: 
#            unused
#        :param push_mode <int>: 
#            0: post to amq
#            1: post to iqproxy
#        :param push_fn: 
#        :param userdata: 
#        :param s_map: 
#    """
#    def fn_publish(self, ev, hit_item, event_type, event_type_in_url, ev_ids, int_epoch, push_mode,
#            push_fn, userdata, s_map):
#        """ fn """
#        hits_count = 0
#        identifier = ""
#        log.debug("hit_item=%s" % str(hit_item))
#        if "_id" not in hit_item:
#            raise Exception("hit dropped, no '_id' in msg: %s" %
#                    json.dumps(hit_item, ensure_ascii=False))
#        if "_source" not in hit_item or "startTime" not in hit_item["_source"]:
#            raise Exception("hit dropped, no '_source': [startTime] %s" %
#                    (json.dumps(hit_item, ensure_ascii=False)))
#        identifier = hit_item["_id"] + \
#            str(hit_item["_source"]["endTime"]) if "endTime" in hit_item["_source"] else ""
#        if identifier in ev_ids:
#            raise Exception("hit dropped, duplicate 'identifier': _id: (%s,%s)" % 
#                (json.dumps(hit_item, ensure_ascii=False),
#                    json.dumps(ev_ids[identifier], ensure_ascii=False)))
#        msg_output = hit_item["_source"]
#        start_time = (int)(msg_output["startTime"])
#        ev_ids[identifier] = hit_item
#        msg_output["eventId"] = hit_item["_id"]
#    
#        if push_mode == 0 or push_mode == 2:
#            oo_type = None
#            oo_name = None
#            if "nameSpace" in msg_output:
#                msg_output["occurredObject"] = msg_output["nameSpace"]
#                msg_output["ooName"] = msg_output["nameSpace"]
#                msg_output["entityName"] = msg_output["nameSpace"]
#                oo_name = msg_output["entityName"]
#                                                                              
#            if "ruleName" in msg_output and len(msg_output["ruleName"]) > 0:
#                strs_tmp = msg_output["ruleName"].split(':')
#                msg_output["ooType"] = strs_tmp[1]
#                msg_output["entityType"] = strs_tmp[1]
#                oo_type = msg_output["entityType"]
#                log.log(logging.DEBUG, "entityType in ruleName=%s" % msg_output["entityType"])
#            if oo_type is not None and oo_name is not None:
#                msg_output["__oriEntityName__"] = oo_name
#                msg_output["__oriEntityType__"] = oo_type
#                if oo_type == u"cluster":
#                    if "map_cluster_app" in s_map and \
#                        oo_name in s_map["map_cluster_app"]:
#                        msg_output["entityName"] = \
#                            s_map["map_cluster_app"][oo_name]
#                        msg_output["entityType"] = "app"
#                        msg_output["__comment__"] = \
#                            "converted_cluster_to_app"
#                if oo_type == u"group":
#                    if "map_group_app" in s_map and \
#                        oo_name in s_map["map_group_app"]:
#                        msg_output["entityName"] = \
#                            s_map["map_group_app"][oo_name]
#                        msg_output["entityType"] = "app"
#                        msg_output["__comment__"] = \
#                            "converted_group_to_app"
#                if oo_type == u"service":
#                    if "map_bns_okb_service" in s_map and \
#                        oo_name in s_map["map_bns_okb_service"]:
#                        msg_output["entityName"] = \
#                            s_map["map_bns_okb_service"][oo_name]
#                        msg_output["entityType"] = "service"
#                        msg_output["__comment__"] = \
#                            "converted_bns_to_okb"
#            msg_output["eventType"] = event_type
#            msg_output["messageType"] = event_type
#            msg_output["state"] = "begin" if (int)(msg_output["endTime"]) == 2147483647 else "end"
#        msg_output["__dataFrom__"] = "ebus-remover" + "_" + os.getenv("HOSTNAME")
#        #publish
#        if push_mode == 0:
#            #post to amq
#            try:
#                ev.publish_to_amq(msg_output)
#            except (stomp.exception.ConnectionClosedException, 
#                    stomp.exception.NotConnectedException, stomp.exception.ConnectFailedException,
#                    stomp.exception.InterruptedException) as e:
#                log.warning("connection error: %s" % str(e))
#                ev.reconnect()
#        elif push_mode == 1:
#            #post to iqproxy
#            url = "http://host/data/%s/" % it_event_type[0]
#            str_json = json.dumps(msg_output, ensure_ascii=False)
#            params = urllib.quote(str_json)
#            conn = httplib.HTTPConnection(config.IQPROXY_DOMAIN, config.IQPROXY_PORT)
#            conn.request('POST', url, str_json)
#            resp = conn.getresponse()
#            resp_data = resp.read()
#            resp_code = resp.status
#            log.log(logging.DEBUG, "resp[%s]: %s" % (str(resp_code), resp_data))
#        elif push_mode == 2:
#            push_fn("", json.dumps(msg_output, ensure_ascii=False), userdata)
#        log.log(logging.DEBUG, "[%s] messageType:[%s] entityType:[%s] entityName:[%s]" % (
#            time.strftime("%Y-%m-%d %H:%M:%S"), msg_output["messageType"],
#            msg_output["entityType"], msg_output["entityType"],
#            ))
#        log.log(logging.DEBUG, "publish: %s" % (json.dumps(msg_output, ensure_ascii=False)))
#        hits_count += 1
#        if len(ev_ids) > 10000:
#            ev_ids.clear()
#        return (0, hits_count)

    def publish_to_amq(self, msg):
        """
        :return:

        """

        #vars
        list_oo = None
        ev_otype = None
        ev_oo    = None
        ev_ttype = None
        ev_etype = None

        ev_otype_arr = [""]
        ev_oo_arr    = [""]
        ev_ttype_arr = [""]
        ev_etype_arr = [""]

        queue_names = []
        queue_name = None
        queue_arr = []

        msg_json = json.dumps(msg, ensure_ascii=False)

# schema v1.0
#        elif "" in msg:
#            ev_oo = msg["entityName"]
#            ev_oo_arr.append(ev_oo)    #TODO 由于使用运维对象名, 消耗activemq资源相当大。

#        if "entityType" in msg:
#            ev_otype = msg["entityType"]
#            ev_otype_arr.append(ev_otype)

# schema v2.x
        if "type" in msg:
            ev_etype = msg["type"]
            ev_etype_arr.append(ev_etype)
            #TODO

        if "opObject" in msg:
            list_oo = msg["opObject"]
            #msg checking
            if len(list_oo) != 1:
                raise Exception("len(msg['opObject']) != 1")
            for oo in list_oo:
                if "name" not in oo:
                    raise Exception("msg['opObject']['name'] is required.")
                if "type" not in oo:
                    raise Exception("msg['opObject']['type'] is required.")

            for oo in list_oo:
                ev_otype_arr.append(oo["type"])
#                ev_oo_arr.append(oo["name"])

        if "impactedObject" in msg:
            pass

        ev_ttype_arr.append(self.EVENTBUS_OO_TYPE_STR_APP)
        ev_ttype_arr.append(self.EVENTBUS_OO_TYPE_STR_SERVICE)
        ev_ttype_arr.append(self.EVENTBUS_OO_TYPE_STR_INSTANCE)
        ev_ttype_arr.append(self.EVENTBUS_OO_TYPE_STR_HOST)

        queue_arr = itertools.product(ev_otype_arr, ev_oo_arr, ev_ttype_arr, ev_etype_arr)
        for queue_item in queue_arr:
            queue_name = ""
            for item in queue_item:
                queue_name += item
                queue_name += "."
            queue_names.append(queue_name[0:-1])

        for queue_name in queue_names:
            try:
                log.debug("before lock acquire")
                self.lock_conn.acquire()    #lock
                log.debug("after  lock acquire")
                ret = self.conn.send(destination="/topic/" + queue_name, body=json.dumps(msg))
            except Exception as e:
                raise e
            except socket.error as e:
                raise Exception(str(e))
            finally:
                log.debug("before lock release")
                self.lock_conn.release()    #unlock
                log.debug("after  lock release")

        return True
    
#    def publish_to_iqproxy(self, msg):
#        #post to iqproxy
#        url = self.conf["iqproxy_url"]
#        str_json = json.dumps(msg, ensure_ascii=False)
#        params = urllib.quote(str_json)
#        conn = httplib.HTTPConnection(self.conf["iqproxy_domain"], self.conf["iqproxy_port"])
#        conn.request('POST', url, str_json)
#        resp = conn.getresponse()
#        resp_data = resp.read()
#        resp_code = resp.status
#        log.log(logging.DEBUG, "resp[%s]: %s" % (str(resp_code), resp_data))

    def publish_to_qmacs(self, msg):
        ''' '''
        #"http://eamaster.noah.baidu.com/warning-20170502/Warning/uid"
        #                              tolower(<type>)-%Y%m%d/<type>/uid   
        dict_db = {
                "Remedy":"common",
                "Oncall":"oncall",
                "Warning":"warning",
                "rootCauseEvent":"online",
                "RootCause":"online",
                }

        str_date = time.strftime("%Y%m%d")

        if "uid" not in msg:
            raise Exception("invalid msg. missing 'uid' field")
        if "type" not in msg:
            raise Exception("invalid msg. missing 'type' field")
        if msg["type"] not in dict_db.keys():
            raise Exception("invalid msg. invalid type:[%s]" % msg["type"])

        str_json = json.dumps(msg, ensure_ascii=False).encode("utf-8")
        url = "%s/%s-%s/%s/%s" % (
                self.conf["iqproxy_url"],
                dict_db[msg["type"]],
                str_date, 
                msg["type"],
                msg['uid']
                )

        conn = httplib.HTTPConnection(self.conf["iqproxy_domain"], self.conf["iqproxy_port"])
        conn.request('POST', url, str_json)
        resp = conn.getresponse()
        resp_data = resp.read()
        resp_code = resp.status
        log.log(logging.DEBUG, "resp[%s]: %s" % (str(resp_code), resp_data))

    def publish(self, msg):

#        self.publish_to_iqproxy(msg)
        self.publish_to_qmacs(msg)

    def first_subscribe(self, list_entities=None, on_message=None, userdata=None):
        """ first_subscribe """
        if self.b_first_subscribe is not True:
            return
        self.b_first_subscribe = False
        if list_entities is None or len(list_entities) <= 0:
            return
        if on_message is None:
            return

        #vars
        log.debug("first_subscribe()")
        ev_ids = {}
        event_types = [["warningEvent", "warning", 0], ["abnormalEvent", "abnormal", 0]]
        for it_event_type in event_types:
            try:
                str_date = time.strftime("%Y%m%d")
                int_epoch = (int)(time.strftime("%s"))
                log.log(logging.DEBUG, "epoch:%d" % (int_epoch))

                request = "/online-%s/%s/_search" % (str_date, it_event_type[0])
                param = {"query": {"bool": {"must": [{"terms": {"nameSpace": list_entities}},
                    {"range": {"endTime": {"gte": int_epoch}}}]}}}

                log.log(logging.DEBUG, "request:%s param:%s" % (request, str(param)))
                
                params = json.dumps(param, ensure_ascii=False)
                conn = httplib.HTTPConnection(config.esmaster_domain, config.esmaster_port)
                url =  "%s" % request 
                conn.request('POST', url, params)
                resp = conn.getresponse()
                data = resp.read()
                retjson = json.loads(data)
                log.log(logging.DEBUG, "retjson=%s" % str(retjson))

                if "hits" in retjson and "hits" in retjson["hits"]:
                    hits_count = 0
                    for hit_item in retjson["hits"]["hits"]:
                        try:
                            ret, hits_count = self.fn_publish(None, hit_item, it_event_type[1],\
                                it_event_type[0], ev_ids, int_epoch, 2, on_message, userdata, {})
                            log.debug("fn_publish() = %d" % ret)
                        except Exception as e:
                            log.log(logging.WARNING, "error0:[%s] traceback:%s" % (str(e),
                                        traceback.format_exc()))
                    log.log(logging.DEBUG, "hits=%d send_count=%d" % 
                            (len(retjson["hits"]["hits"]), hits_count))
            except Exception as e:
                log.log(logging.WARNING, "error:[%s] trace:[%s]" % (str(e), traceback.format_exc()))
        pass

    def subscribe(self, filter=None, on_message=None, userdata=None, on_error=None):
        """
        根据filter描述的事件属性从对应的队列订阅事件
        :param filter: <json>
                { "entityType": 运维对象类型
                  "occurredObject"/"entityName":   运维对象名
                  "messageType":事件类型 }
        :param on_message:
        :param userdata:
        :return true/false
        """
        #vars
        res = False
        str_schema_version = None

        list_ev_oo = None
        list_ev_ttype = None
        list_ev_etype = None

        ev_otype = None
        ev_oo    = None
        ev_ttype = None
        ev_etype = None
        ev_otype_arr = [""]
        ev_oo_arr    = [""]
        ev_ttype_arr = [""]
        ev_etype_arr = [""]
        queue_name = ""

        log.debug("[filter=%s]" % (filter))

        if filter is not None:
            if type(filter) is not type({}):
                #TODO error
                pass

            # v1.x & v2.x

            #schema version
            if "entityType" in filter or \
            "occurredObject" in filter or \
            "entityName" in filter or \
            "transType" in filter:
                if str_schema_version is not None:
                    raise Exception("schema error. version:%s already exists!" %
(str_schema_version))
                str_schema_version = "v1.x"

            if "opObject" in filter or \
            "expectedType" in filter:
                if str_schema_version is not None:
                    raise Exception("schema error. version:%s already exists!" %
(str_schema_version))
                str_schema_version = "v2.x"

            if str_schema_version is None:
                str_schema_version = "v2.x"

            if str_schema_version == "v1.x":
#                if "messageType" in filter:
#                    ev_etype = filter["messageType"]
#                    if type(ev_etype) is not type([]):
#                        ev_etype_arr = [ev_etype]
#                    else:
#                        ev_etype_arr = ev_etype
#
#                if "state" in filter:
#                    if type(filter["state"]) is not type([]):
#                        self.mqlistener.filter_map_state[filter["state"]] = True
#                    else:
#                        for obj in filter["state"]:
#                            self.mqlistener.filter_map_state[obj] = True
#
#                if "entityType" in filter:
#                    ev_otype = filter["entityType"]
#                    if type(ev_otype) is not type([]):
#                        ev_otype_arr = [ev_otype]
#                    else:
#                        ev_otype_arr = ev_otype
#
#                if "occurredObject" in filter:
#                    ev_oo = filter["occurredObject"]
#                elif "entityName" in filter:
#                    ev_oo = filter["entityName"]
#
#                if ev_oo is not None:
#                    if type(ev_oo) is not type([]):
#                        self.mqlistener.filter_list_oo[ev_oo] = True
#                    else:
#                        for obj in ev_oo:
#                            self.mqlistener.filter_list_oo[obj] = True
#
#                if "transType" in filter:
#                    ev_ttype = filter["transType"]
#                    if type(ev_ttype) is not type([]):
#                        ev_ttype_arr = [ev_ttype]
#                    else:
#                        ev_ttype_arr = ev_ttype
                pass

            elif str_schema_version == "v2.x":
                #opObject
                if "opObject" in filter:
                    ev_otype_arr = []
                    if type(filter["opObject"]) is type([]):
                        list_ev_oo = filter["opObject"]
                    elif type(filter["opObject"]) is type({}):
                        list_ev_oo = [filter["opObject"]]

                    #opObject format checking
                    if len(list_ev_oo) != 1:
                        raise Exception("len(filter['opObject']) != 1")
                    for ev_oo in list_ev_oo:
                        if "name" not in ev_oo:
                            raise Exception("filter['opObject']['name'] is required.")
                        if "type" not in ev_oo:
                            raise Exception("filter['opObject']['type'] is required.")
                        if type(ev_oo["name"]) is not type(""):
                            raise Exception("type(filter['opObject']['name']) is not string")
                        if type(ev_oo["type"]) is not type(""):
                            raise Exception("type(filter['opObject']['type']) is not string")
                    #char escape
                    for ev_oo in list_ev_oo:
                        if ev_oo["name"] == "*":
                            ev_oo["name"] = ""
                        if ev_oo["type"] == "*":
                            ev_oo["type"] = ""

                        ev_otype_arr.append(ev_oo["type"])
                        if ev_oo["name"] != "":
                            self.mqlistener.filter_list_oo[ev_oo["name"]] = True

                #expectedType
                if "expectedType" in filter:
                    ev_ttype_arr = []
                    list_ev_ttype = filter["expectedType"]
                    if type(list_ev_ttype) is not type([]):
                        list_tmp = [list_ev_ttype]
                    else:
                        list_tmp = list_ev_ttype
                    for ev_ttype in list_tmp:
                        if ev_ttype == "*":
                            ev_ttype = ""
                        ev_ttype_arr.append(ev_ttype)

                #messageType
                if "messageType" in filter:
                    ev_etype_arr = []
                    list_ev_etype = filter["messageType"]
                    if type(list_ev_etype) is not type([]):
                        list_tmp = [list_ev_etype]
                    else:
                        list_tmp = list_ev_etype

                    for it in list_tmp:
                        if it == "*":
                            it = ""
                        ev_etype_arr.append(it)

                if "state" in filter:
                    if type(filter["state"]) is not type([]):
                        self.mqlistener.filter_map_state[filter["state"]] = True
                    else:
                        for obj in filter["state"]:
                            self.mqlistener.filter_map_state[obj] = True
            #v2.x end

            queue_arr = itertools.product(ev_otype_arr, ev_oo_arr, ev_ttype_arr, ev_etype_arr)

            queue_names = []
            for queue_item in queue_arr:
                queue_name = ""
                for item in queue_item:
                    queue_name += item
                    queue_name += "."
                queue_names.append(queue_name[0:-1])

        log.debug("subscribe() queue_names=[%s]" % str(queue_names))
        self.first_subscribe(list(self.mqlistener.filter_list_oo.keys()), on_message, userdata)
        self.mqlistener.user_on_message = on_message
        self.mqlistener.user_on_error = on_error

        log.debug("[filter=%s]" % (filter))

        for queue_name in queue_names:
            try:
                self.lock_conn.acquire()
                ret = self.conn.subscribe(destination="/topic/" + queue_name, id=2, ack='auto')
                self.mqlistener.userdata = userdata
                self.on_message = on_message
                self.on_error = on_error
                self.userdata = userdata
                self.filter = filter
                self.b_subscribed = True
            except Exception as e:
                raise e
            except socket.error as e:
                raise Exception(str(e))
            finally:
                self.lock_conn.release()#            self.list_subscribed.append(queue_name)

        log.debug("[self.filter=%s]" % (self.filter))

        res = True
        return res

    def unsubscribe(self):
        """
        detach from bus

        :return: True/False

        """
        self.thr_keeper.stop()
        try:
            self.lock_conn.acquire()    #lock
            self.mqlistener.on_disconnected = None
            try:
                self.conn.disconnect()
            except:
                pass
            try:
                self.conn.stop()
            except:
                pass
            self.b_subscribed = False
        except Exception as e:
            raise e
        except socket.error as e:
            raise Exception(str(e))
        finally:
            self.lock_conn.release()    #unlock

        return True

    def destroy(self):
        """
        destroy Eventbus instance

        """
        self.unsubscribe()

def __user_on_message1(header, message, userdata):
    """
    fn user_on_message(), for testing.

    """
#    print('[%s] __user_on_message1: headers[%d] message[%s]' % (time.strftime("%Y-%m-%d %H:%M:%S"),
#        len(header), message))
    userdata["msgcount"] += 1
#    print("msgcount = %d" % (userdata["msgcount"]))
    
    strmd5 = md5.md5(message).hexdigest()
    if strmd5 in userdata:
        print("COLLISION!!!")
        userdata["collision"] += 1
    else:
        userdata[strmd5] = True


if __name__ == "__main__":
    print("%s" % str(config))
    userdata = {}
    userdata["collision"] = 0
    userdata["msgcount"] = 0

#    ev1 = Eventbus()
    ev1 = EventbusDisasterTolerance()

    
    filter = {}
#    filter["entityType"] = "app"
    filter["messageType"] = ["abnormal", "Warning"]
    filter["state"] = []
#    filter["entityType"] = "service"
#    filter["occurredObject"] = ["cas.baidu.com", "cap.baidu.com"]
    filter = {"opObject": {"type":"Service", "name": "SDK"},"messageType": "Warning","expectedType":"*","state":"END"}

    ev1.subscribe(filter, __user_on_message1, userdata)

#    ev2 = Eventbus()
#    filter = {}
#    filter["messageType"] = "warning"
#    ev2.subscribe(filter, __user_on_message2)

#    evp = Eventbus()
#    print("eventbus connected")
#    for i in range(1,10):
#        msg = {}
#        msg["entityType"] = "app"
#        msg["occurredObject"] = "obj%02d" % i
#        msg["messageType"] = "warning"
#        evp.publish((msg))
#        print("msg=[%s]" % (json.dumps(msg)))
    print("start")
    while True:
        time.sleep(1)
#        print("collision=%d" % (userdata["collision"]))
    pass

# vim: set expandtab ts=4 sw=4 sts=4 tw=100:


