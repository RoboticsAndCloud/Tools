#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
猎鹰 api-service 模块 api 接口业务监控
"""

import logging
import logging.handlers
import os
import locale
import json
import traceback
import urllib
import urllib2
import time

logger = ''

loggerErr = ''

# 非本机监控HOST
HOST = 'falcon.xx.com'

FALCON_HOST = 'api.mt.noah.xx.com:8557'

# 本机监控HOST
# HOST='127.0.0.1:8868'

current_time = int(time.time())

base_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))

token_id = 'b58cf781-16bb-4738-8320-335afb7ff4f0'

sla_product = 'rd:noah'
sla_namespace = 'group.lf.noah.all'
#sla_namespace = 'lieying.noah.all'

pv_total_metric = 'pvTotal'
pv_lost_metric = 'pvLost'


def init_logger(log_file):
    """
    初始化日志
    """
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] \
    %(levelname)s %(message)s')
    handler=logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 60, backupCount=2)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    global loggerErr
    loggerErr = logging.getLogger("error")
    loggerErr.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] \
    %(levelname)s %(message)s')
    handler=logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 60, backupCount=2)
    handler.setFormatter(formatter)
    loggerErr.addHandler(handler)


def json_decode(json_str):
    """
    字符串转换为 json 对象
    """
    global logger
    try:
        json_data = json.loads(json_str)
        return json_data
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'


def json_encode(json_data):
    """
    json 对象转换为字符串
    """
    global logger
    try:
        json_str = json.dumps(json_data)
        return json_str
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'


def http_get(url, data=None):
    """
    http get 请求
    """
    global logger
    try:
        if data is not None:
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
        else:
            req = urllib2.Request(url)

        response = urllib2.urlopen(req, timeout=20)
        if response.getcode() == 200:
            return response.read().decode('utf-8')
        else:
            logger.error("curl " + url + " failed with http code " + str(response.getcode()))
            return 'err'
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'


def http_post(url, data):
    """
    http post 请求
    """
    global logger
    try:
        data = json_encode(data)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req, timeout=20)
        if response.getcode() == 200:
            return response.read().decode('utf-8')
        else:
            logger.error("curl " + url + ":" + json_encode(data) + " failed with http code "\
                         + str(response.getcode()))
            return 'err'
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        return 'err'


def handle_result(argus_item, ret_code):
    """
    处理结果
    """
    print("%s: %d" % (argus_item, ret_code))
    push_sla_data(argus_item, ret_code)


def push_sla_data(item, status):
    """
    推送sla数据
    """
    global pv_total_metric
    global pv_lost_metric
    pv_total = 1
    pv_lost = 0
    if status == 1:
        pv_lost = 1

    url = 'http://api.tsdb.noah.xx.com/data/tsdb?aggr=true'
    data = {
        "data": [
            {
                "product": sla_product,
                "namespace": sla_namespace,
                "timestamp": current_time,
                "tags": [
                    {
                        "name": "item",
                        "value": item
                    }
                ],
                "metrics": [
                    {
                        "metric": pv_total_metric,
                        "cycleInSecond": 60,
                        "value": pv_total
                    },
                    {
                        "metric": pv_lost_metric,
                        "cycleInSecond": 60,
                        "value": pv_lost
                    }
                ]
            }
        ]
    }
    ret = http_post(url, data)
    #print ret


def status_domainListWithProduct():
    """
    domainListWithProduct接口，获取产品线域名列表接口
    """
    global logger
    url = 'http://%s/api/v1/domain/domainListWithProduct' % (HOST)
    logger.info(url)
    argus_item = 'falcon_domainListWithProduct_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'result' not in result_obj or result_obj['result'] is None \
            or len(result_obj['result']) == 0:
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_idcEvents():
    """
    idcEvents接口，获取IDC故障列表接口
    """
    global logger
    url = 'http://%s/api/v1/events/idcEvents' % (HOST)
    logger.info(url)
    argus_item = 'falcon_idcEvents_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'page' not in result_obj or result_obj['page'] is None or len(result_obj['page']) == 0:
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_provinceEvents():
    """
    provinceEvents接口，获取省份运营商故障列表接口
    """
    global logger
    url = 'http://%s/api/v1/events/provinceEvents' % (HOST)
    logger.info(url)
    argus_item = 'falcon_provinceEvents_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'page' not in result_obj or result_obj['page'] is None or len(result_obj['page']) == 0:
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_vipEvents():
    """
    vipEvents 接口，获取vip故障列表接口
    """
    global logger
    url = 'http://%s/api/v1/events/vipEvents' % (HOST)
    logger.info(url)
    argus_item = 'falcon_vipEvents_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'page' not in result_obj or result_obj['page'] is None or len(result_obj['page']) == 0:
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_dnsEvents():
    """
        dnsEvents 接口，获取DNS劫持故障列表接口
    """
    global logger
    url = 'http://%s/api/v1/events/dnsEvents' % (HOST)
    logger.info(url)
    argus_item = 'falcon_dnsEvents_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'page' not in result_obj or result_obj['page'] is None or len(result_obj['page']) == 0:
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_ispAndZoneIdcSet():
    """
    ispAndZoneIdcSet接口，获取机房列表接口
    """
    global logger
    url = 'http://%s/api/v1/idc/ispAndZoneIdcSet' % (HOST)
    logger.info(url)
    argus_item = 'falcon_ispAndZoneIdcSet_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'result' not in result_obj or result_obj['result'] is None \
            or len(result_obj['result']) == 0:
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_thirdPartyTaskWithCategory():
    """
    thirdPartyTaskWithCategory接口，获取第三方监测任务列表接口
    """
    global logger
    url = 'http://%s/api/v1/thirdParty/thirdPartyTaskWithCategory' % (HOST)
    logger.info(url)
    argus_item = 'falcon_thirdPartyTaskWithCategory_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'result' not in result_obj or result_obj['result'] is None \
            or len(result_obj['result']) == 0:
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_thirdPartyMapStatus():
    """
    thirdPartyMapStatus，获取第三方监控地图数据
    """
    global logger
    url = 'http://%s/api/v1/thirdPartyMapStatus' % (HOST)
    logger.info(url)
    argus_item = 'falcon_thirdPartyMapStatus_status'

    condition = {
        "taskKey": "domain_www.suning.com",
        "endTime": base_time,
        "metric": ["single_check_ok_rate",
                   "single_check_res_time"
                   ],
        "ispList": ["CHINANET"]
    }
    condition_str = json_encode(condition)
    data = {
        "conditionString": condition_str
    }
    try:
        result = http_get(url, data)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'result' not in result_obj or result_obj['result'] is None \
            or len(result_obj['result']) == 0:
            handle_result(argus_item, 1)
            return

        # 地图数据为空
        data = result_obj['result']
        # 电信连通性数据
        isp_data = data['CHINANET']
        if isp_data is None:
            handle_result(argus_item, 1)
            return

        provinces_data = isp_data.values()
        if provinces_data is None:
            handle_result(argus_item, 1)
            return

        has_data = False
        for province_data in provinces_data:
            if 'check_pv' in province_data and province_data['check_pv'] != "-":
                has_data = True
                break
            if 'check_res_time' in province_data and province_data['check_res_time'] != "-":
                has_data = True
                break

        if has_data == False:
            handle_result(argus_item, 1)
            return

    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_getIdcArea():
    """
    getIdcArea接口，获取内网连通性IDC列表接口
    """
    global logger
    url = 'http://%s/api/v1/innerIdc/getIdcArea?type=dest' % (HOST)
    logger.info(url)
    argus_item = 'falcon_getIdcArea_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'result' not in result_obj or result_obj['result'] is None \
            or len(result_obj['result']) == 0:
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_getDomainStatus():
    """
    getDomainStatus，获取首页域名地图数据
    """
    global logger
    url = 'http://%s/api/v1/domain/getDomainStatus' % (HOST)
    logger.info(url)
    argus_item = 'falcon_getDomainStatus_status'

    try:
        result = http_get(url)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'result' not in result_obj or result_obj['result'] is None \
            or len(result_obj['result']) == 0:
            handle_result(argus_item, 1)
            return

        # 地图数据为空
        data = result_obj['result']
        # 电信连通性数据
        isp_data = data['CHINANET']
        if isp_data is None:
            handle_result(argus_item, 1)
            return

        provinces_data = isp_data.values()
        if provinces_data is None:
            handle_result(argus_item, 1)
            return
        cnt = len(provinces_data)
        if cnt == 0:
            handle_result(argus_item, 1)
            return

        provinces_data = list(set(provinces_data))
        cnt = len(provinces_data)
        # 如果地图所有省份数据都为空
        if cnt <= 1 and provinces_data[0] == "":
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)


def status_getIdcMapData():
    """
    getIdcMapStatus，获取机房地图数据接口
    """
    global logger
    condition = {
        "conditionList": [
            {
                "monitoringObjectType": "idc",
                "monitoringObjectValue": "NJ02UN",
                "source": "GXT",
                "metric": "checkPv",
                "ifOnlyServed": False,
                "ispList": ["UNICOM"],
                "endTime": base_time
            }
        ]
    }
    condition_str = json_encode(condition)
    url = 'http://%s/api/v1/statusInProvince' % (HOST)
    logger.info(url)
    argus_item = 'falcon_getIdcMapData_status'

    try:
        data = {
            'conditionListString': condition_str,
            'tokenId': token_id
        }
        result = http_get(url, data)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            handle_result(argus_item, 1)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            handle_result(argus_item, 1)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            handle_result(argus_item, 1)
            return

        # 请求数据为空
        if 'result' not in result_obj or result_obj['result'] is None \
            or len(result_obj['result']) == 0:
            handle_result(argus_item, 1)
            return

        data = result_obj['result'][0]
        if data is None or len(data) <= 0:
            handle_result(argus_item, 1)
            return

        if 'data' not in data or data['data'] is None or len(data['data']) <= 0:
            handle_result(argus_item, 1)
            return

        # 电信连通性数据
        isp_data = data['data'][0]

        if isp_data is None:
            handle_result(argus_item, 1)
            return

        provinces_data = isp_data['districtStatus']

        if provinces_data is None:
            handle_result(argus_item, 1)
            return
        cnt = len(provinces_data)
        if cnt == 0:
            handle_result(argus_item, 1)
            return

        provinces_data = list(set(provinces_data))

        cnt = len(provinces_data)
        # 如果地图所有省份数据都为空
        if cnt <= 1 and provinces_data[0] == "-":
            handle_result(argus_item, 1)
            return
    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return

    # 值为0 表示接口当前访问正常
    handle_result(argus_item, 0)

def status_getData(url):
    """
    getIdcMapStatus，获取机房地图数据接口
    """
    global logger
    condition = {
        "conditionList": [
            {
                "node_id": 1067
            }
        ]
    }
    condition_str = json_encode(condition)
    logger.info(url)
    argus_item = 'falcon_getServiceTreeHosts_status_test'

    try:
        data = {
            'node_id': 1067,   
        }
        result = http_get(url, data)
        logger.info(url + ":" + result)

        # get请求失败
        if result == 'err':
            loggerErr.error(url)
            return

        result_obj = json_decode(result)

        # 返回数据不是 json 格式
        if result_obj == 'err':
            loggerErr.error(url)
            return

        # 请求失败
        if 'success' not in result_obj or result_obj['success'] == False:
            loggerErr.error(url)
            return
       
        # 请求数据为空
        if 'data' not in result_obj or result_obj['data'] is None:
            loggerErr.error(url)
            return

        data = result_obj['data']
        print data
        if data is None or len(data) <= 0:
            loggerErr.error(url)
            return

    except Exception:
        exstr = traceback.format_exc()
        logger.error(exstr)
        handle_result(argus_item, 1)
        return


def load_urls(aggrNamesFile):
    # http://group.bcm-tsdb-query.docker.all.serv:20041/v1/products/006da024b95346209af84da43d824233/namespaces/lHyvNlxhEodCFXwKWyVnaohasKRgHdB___bj.BCM_SITE.006da024b95346209af84da43d824233/metrics/site.bcm.success/_data
    url = 'http://group.bcm-tsdb-query.docker.all.serv:20041/v1/products/%s/namespaces/%s/metrics/site.bcm.success/_data'
    with open(aggrNamesFile, 'r') as f:
        for line in f:

            line = line.replace('\n', '')
            # print line

            splitArr = line.split('"')

            # print splitArr[0], splitArr[1], splitArr[2]
            product = splitArr[0]
            namespaces = splitArr[2] + "___bj." + splitArr[1] + "." + splitArr[0]
            # print namespaces
            urlDest = url % (product, namespaces)

            status_getData(urlDest)
            print urlDest
    print '------------'



if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, locale='en_US.UTF-8')
    work_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(work_dir)
    if os.path.exists('log') == False:
        os.system('mkdir -p log')
    print work_dir
    init_logger(work_dir + '/log/falcon-api-monitor.log')
    file = '/Users/baidu/Desktop/aggrNames.txt'
    load_urls(file)


'''
    status_domainListWithProduct()
    status_provinceEvents()
    status_idcEvents()
    status_vipEvents()
    status_dnsEvents()
    status_ispAndZoneIdcSet()
    status_thirdPartyTaskWithCategory()
    status_thirdPartyMapStatus()
    status_getIdcArea()
    status_getDomainStatus()
    status_getIdcMapData()

'''