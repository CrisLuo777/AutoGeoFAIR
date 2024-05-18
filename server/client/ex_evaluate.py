#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser as ConfigParser
import json
import os
import tracemalloc
from pathlib import Path
from fuji_server.controllers.fair_check import FAIRCheck
from fuji_server.helper.catalogue_helper_google_datasearch import MetaDataCatalogueGoogleDataSearch
from fuji_server.helper.preprocessor import Preprocessor
import gc
import csv
import re

# os
#os.environ['TIKA_SERVER_JAR'] = 'file://Program Files\tika\tika-server-1.24.1.jar'

identifier = 'https://doi.org/10.1594/PANGAEA.902845'
#identifier='https://doi.org/10.26050/WDCC/MOMERGOMBSCMAQ'
#oai_pmh = 'http://ws.pangaea.de/oai/'
debug = True

muchotestpids = [   #多测试进程
    '10.15493/DEFF.10000003', 'https://phaidra.cab.unipd.it/view/o:267291', 'https://jyx.jyu.fi/handle/123456789/39205',
    'https://linked.bodc.ac.uk/sparql/?query=describe+%3Chttp%3A%2F%2Flinked.bodc.ac.uk%2Fseries%2F65425%2F%3E&output=text&stylesheet=',
    'https://linkedsystems.uk/erddap/tabledap/Public_Compressed_RAW_Glider_Data_1112.htmlTable?fileType&distinct()'
]



muchotestpids.sort()
testpids = sorted(set(muchotestpids))

#testpids = [testpids[-1]]

startpid = ''

#FTP landing site
#10.6092/84cb588d-97e5-4c64-91bb-ba6109dfa530
#testpids=['https://doi.org/10.5066/f7q81b46']
#MODS
#10.7925/drs1.duchas_4759592
#DDI StudyUnit Study

#google_registry_helper = MetaDataCatalogueGoogleDataSearch()
#testpids = google_registry_helper.random_sample(500)
testpids = {'https://static-content.springer.com/esm/art%3A10.1186%2Fs40729-019-0191-5/MediaObjects/40729_2019_191_MOESM2_ESM.docx','https://doi.org/10.5281/zenodo.3332055','https://www.ncbi.nlm.nih.gov/bioproject/?term=PRJNA559766','https://figshare.com/articles/dataset/Additional_file_1_of_Differential_expression_of_matrix_metalloproteinases_and_miRNAs_in_the_metastasis_of_oral_squamous_cell_carcinoma'}
testpids = []
#testpids=list(testpids)
testpids.extend(list(muchotestpids))
#testpids.extend(list(fujipids))

testpids.sort()
testpids = sorted(set(testpids))

testpids=['https://s11.no/2022/a2a-fair-metrics/02-html-full/']

testpids=['https://doi.pangaea.de/10.1594/PANGAEA.908011']


comparepids={
    # 'https://zenodo.org/record/6535133#.Yn5tLHVBxHc':79.17,
    # 'https://zenodo.org/record/6481639#.Yn5uBXUzZHc':75,
    # 'https://inveniordm.web.cern.ch/records/0pdgk-t7157':10.42,
    # 'https://ecat.ga.gov.au/geonetwork/srv/api/records/c692fb4b-4d67-719d-e044-00144fdd4fa6/formatters/xml?approved=true':33.33,
    # '10.4225/25/552B5AAD0C34A':45.83,
    # '10.5281/zenodo.5499840':79.17,
    '10.48804/V5CGMS':54.17,
    'https://doi.pangaea.de/10.1594/PANGAEA.908011':1,
    # '10.48804/BTMCFO':62.5
}


#读取数据########
testpids=comparepids.keys()
column_values = []
with open('input.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        column_values.append(row[0])  # 假设要读取的列是第一列

testpids=column_values





#testpids=['https://www.ebi.ac.uk/biosamples/samples/SAMN14168013']
#testpids=['https://doi.pangaea.de/10.1594/PANGAEA.846774']
#testpids=['http://localhost/fuji_net/test/ucmm_dataset.owl']
#testpids=['https://ecat.ga.gov.au/geonetwork/srv/api/records/c692fb4b-4d67-719d-e044-00144fdd4fa6/formatters/xml?approved=true']
#testpids=['https://data.neotomadb.org/49263']
#testpids=['http://urn.fi/urn:nbn:fi:lb-2018060621']
#testpids=['https://hal.archives-ouvertes.fr/hal-01683842/']
#testpids = ['https://geofon.gfz-potsdam.de/waveform/archive/inspire.php?doi=10.14470/TR560404']
#testpids=['http://doi.org/10.22033/ESGF/CMIP6.4397']
compare_scores = []
#testpids=muchotestpids
print(len(testpids))
startpid=''
metadata_service_endpoint = ''
metadata_service_type = ''
oaipmh_endpoint = ''


def effectivehandlers(logger):
    handlers = logger.handlers
    while True:
        logger = logger.parent
        handlers.extend(logger.handlers)
        if not (logger.parent and logger.propagate):
            break
    return handlers


def main():
    config = ConfigParser.ConfigParser() #创建一个ConfigParser对象，用于解析配置文件
    my_path = Path(__file__).parent.parent #获取当前文件的父目录的父目录，并将其赋值给my_path变量。
    ini_path = os.path.join(my_path, 'config', 'server.ini') #使用os.path.join函数将my_path和配置文件的路径拼接起来，得到配置文件的完整路径，并将其赋值给ini_path变量
    config.read(ini_path)
    YAML_DIR = config['SERVICE']['yaml_directory'] #从配置文件中获取目录yaml_directory:yaml
    METRIC_YAML = config['SERVICE']['metrics_yaml'] #和metrics_yaml:metrics_v0.5.yaml的值，并将其分别赋值给YAML_DIR和METRIC_YAML变量。
    METRIC_YML_PATH = os.path.join(my_path, YAML_DIR, METRIC_YAML)
    SPDX_URL = config['EXTERNAL']['spdx_license_github'] #它存储了用于访问SPDX（Software Package Data Exchange）许可证的GitHub页面的URL地址。SPDX是一个开放的标准，用于标识和共享软件包的许可证信息。通过访问SPDX许可证的GitHub页面，我们可以获取各种软件包的许可证信息，包括许可证的名称、版本、内容和使用条件等。
    DATACITE_API_REPO = config['EXTERNAL']['datacite_api_repo']
    RE3DATA_API = config['EXTERNAL']['re3data_api'] #。re3data是一个研究数据存储库注册表，它提供了一个集中的平台，用于查找、浏览和比较各种研究数据存储库的信息。通过访问re3data的API，我们可以获取存储库的详细信息，如存储库的名称、主题领域、数据类型、访问方式、许可证要求等。这些信息可以帮助研究人员找到适合自己需求的数据存储库，并了解这些存储库的特点和要求。
    METADATACATALOG_API = config['EXTERNAL']['metadata_catalog']
    # 将debug_mode设置为 true 以避免在线下载外部文件（在开发过程中）
    # 触发远程日志记录的 URI 所有其他 F-UJI 服务器请求都被忽略
    isDebug = config.getboolean('SERVICE', 'debug_mode')
    data_files_limit = int(config['SERVICE']['data_files_limit'])  #5
    metric_specification = config['SERVICE']['metric_specification'] #https://doi.org/10.5281/zenodo.4081213 FUJI的指标
    remote_log_host = config['SERVICE'].get('remote_log_host')
    remote_log_path = config['SERVICE'].get('remote_log_path')

    preproc = Preprocessor()
    preproc.retrieve_metrics_yaml(METRIC_YML_PATH, data_files_limit, metric_specification)
    print(f'定义的总指标: {preproc.get_total_metrics()}')   #获取yaml里指标的个数

    isDebug = config.getboolean('SERVICE', 'debug_mode')
    preproc.retrieve_licenses(SPDX_URL, isDebug)
    preproc.retrieve_datacite_re3repos(RE3DATA_API, DATACITE_API_REPO, isDebug)
    preproc.retrieve_metadata_standards(METADATACATALOG_API, isDebug)
    preproc.retrieve_science_file_formats(isDebug)
    preproc.retrieve_long_term_file_formats(isDebug)
    preproc.set_remote_log_info(config['SERVICE'].get('remote_log_host'), config['SERVICE'].get('remote_log_path'))
    preproc.set_max_content_size(config['SERVICE']['max_content_size'])
    print(f'Total SPDX licenses : {preproc.get_total_licenses()}')
    print(f'Total re3repositories found from datacite api : {len(preproc.getRE3repositories())}')
    print(f'Total subjects area of imported metadata standards : {len(preproc.metadata_standards)}')
    start = False
    usedatacite = True
    n = 1
    for identifier in testpids:
        results = []
        ft = None
        tracemalloc.start() #启动Python的内存分配跟踪器
        print(identifier)
        print(n)
        n += 1
        if identifier == startpid or not startpid:
            start = True
        if start:
            ft = FAIRCheck(uid=identifier,
                           test_debug=debug,
                           metadata_service_url=metadata_service_endpoint,
                           metadata_service_type=metadata_service_type,
                           use_datacite=usedatacite,
                           oaipmh_endpoint=oaipmh_endpoint)

            #ft = FAIRCheck(uid=identifier,  test_debug=True, use_datacite=usedatacite)
            #set target for remote logging
            #if remote_log_host and remote_log_path:
            #    ft.set_remote_logging_target(remote_log_host, remote_log_path)

            uid_result, pid_result = ft.check_unique_persistent()
            ft.retrieve_metadata_embedded()
            if ft.repeat_pid_check:
                uid_result, pid_result = ft.check_unique_persistent()
            include_embedded = True
            ft.retrieve_metadata_external()
            if ft.repeat_pid_check:
                uid_result, pid_result = ft.check_unique_persistent()
            core_metadata_result = ft.check_minimal_metatadata()
            content_identifier_included_result = ft.check_content_identifier_included()
            access_level_result = ft.check_data_access_level()
            license_result = ft.check_license()
            related_resources_result = ft.check_relatedresources()
            check_searchable_result = ft.check_searchable()
            data_content_result = ft.check_data_content_metadata()
            data_file_format_result = ft.check_data_file_format()
            community_standards_result = ft.check_community_metadatastandards()
            data_provenance_result = ft.check_data_provenance()
            formal_metadata_result = ft.check_formal_metadata()
            semantic_vocab_result = ft.check_semantic_vocabulary()
            metadata_preserved_result = ft.check_metadata_preservation()
            standard_protocol_data_result = ft.check_standardised_protocol_data()
            standard_protocol_metadata_result = ft.check_standardised_protocol_metadata()

            results.append(uid_result)
            results.append(pid_result)
            results.append(core_metadata_result)
            results.append(content_identifier_included_result)
            results.append(check_searchable_result)
            results.append(access_level_result)
            results.append(formal_metadata_result)
            results.append(semantic_vocab_result)
            results.append(related_resources_result)
            results.append(data_content_result)
            results.append(license_result)
            results.append(data_provenance_result)
            results.append(community_standards_result)
            results.append(data_file_format_result)
            results.append(standard_protocol_data_result)
            results.append(standard_protocol_metadata_result)
            #print(ft.metadata_merged)
            debug_messages = ft.get_log_messages_dict()
            #ft.logger_message_stream.flush()
            summary = ft.get_assessment_summary(results)   #把总分加起来的函数
            #
            print(summary)
            print('score: ', summary.get('score_percent').get('FAIR'))
            compare_scores.append(summary.get('score_percent').get('FAIR'))
            for res_k, res_v in enumerate(results):
                if ft.isDebug:
                    debug_list = debug_messages.get(res_v['metric_identifier'])
                    #debug_list= ft.msg_filter.getMessage(res_v['metric_identifier'])
                    if debug_list is not None:
                        results[res_k]['test_debug'] = debug_messages.get(res_v['metric_identifier'])
                    else:
                        results[res_k]['test_debug'] = ['INFO: No debug messages received']
                else:
                    results[res_k]['test_debug'] = ['INFO: Debugging disabled']
                    debug_messages = {}
            print(json.dumps(results, indent=4, sort_keys=True)) #将 Python 对象转换为 JSON 字符串
            #print(json.dumps([core_metadata_result], indent=4, sort_keys=True))
            #remove unused logger handlers and filters to avoid memory leaks
            ft.logger.handlers = [ft.logger.handlers[-1]]
            #ft.logger.filters = [ft.logger.filters]
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB") #打印当前和峰值的内存使用情况
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('traceback')

            # pick the biggest memory block
            stat = top_stats[0]
            print("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
            for line in stat.traceback.format():
                print(line)

            #for i, stat in enumerate(snapshot.statistics('filename')[:5], 1):
            #     print(i,  str(stat))

            with open('output.csv', 'a', newline='') as csv_file:
                # 写入CSV文件的表头

                writer = csv.writer(csv_file)
                file_exists = os.path.isfile('output.csv')  # 检查文件是否存在
                if not file_exists:
                    headers = ['标识符', '总分数', '指标1','指标2','指标3','指标4','指标5','指标6']
                    writer.writerow(headers)
                # 写入字典
                rows=[]
                rows.append(identifier)

                def match_string_in_dict(pattern, dictionary):
                        # 遍历字典的键和值
                    for key, value in dictionary.items():
                            # 在键中进行匹配
                        re.search(pattern, str(key))
                        return key
                            # 在值中进行匹配

                rows.append(summary.get('score_percent').get('FAIR'))
                # for row in results:
                #     metric_match = match_string_in_dict(r'^FsF-(([FAIR])[0-9](\.[0-9])?)-[0-9].',row['metric_tests'])
                #
                #     try:
                #         if row['metric_tests'][metric_match]['metric_test_maturity'] is None:
                #             row['metric_tests'][metric_match]['metric_test_maturity']=0
                #         rows.append(row['metric_tests'][metric_match]['metric_test_maturity'])
                #     except:
                #         pass
                for key,value in summary.get('score_percent').items():
                    if key!='FAIR':
                        rows.append(value)
                    else:
                        pass
                writer.writerow(rows)
            results=[]
            #preproc.logger.
            gc.collect()
        tracemalloc.stop()
    print(compare_scores)
    print(comparepids.values())





if __name__ == '__main__':
    main()
