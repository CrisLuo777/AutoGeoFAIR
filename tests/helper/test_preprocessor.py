# -*- coding: utf-8 -*-
"""
在这里，我们测试为服务器提供参考数据的预处理器类

对此的评论：
预处理器是一个单顿，因此我们需要正确地上下拆解它。

isDebug=True 读取 fuji_server/data 中的文件
isDebug=False，运行收集代码

所有 CI 测试都应使用 isDebug=True 运行，以便不调用收割机代码
替代方案必须模拟服务器响应才能不进行真正的调用。

为了测试收获是否仍然有效，可以使用 -noCI 和 -manual 进行测试
标记。这些测试可以在发布之前手动运行。
他们模拟fuji_server/数据路径，以免覆盖富士服务器下的文件

"""
isDebug = True
fuji_server_dir = './data_test/'


def test_preprocessor_licences(test_config, temp_preprocessor):
    """Test preprocessor if retrieve_licences works"""

    SPDX_URL = test_config['EXTERNAL']['spdx_license_github']
    assert temp_preprocessor.total_licenses == 0

    temp_preprocessor.retrieve_licenses(SPDX_URL, isDebug)
    assert temp_preprocessor.total_licenses > 0
    assert len(temp_preprocessor.all_licenses) == temp_preprocessor.total_licenses


def test_preprocessor_re3repos(test_config, temp_preprocessor):
    """Test preprocessor if retrieve_re3repos works"""

    DATACITE_API_REPO = test_config['EXTERNAL']['datacite_api_repo']
    RE3DATA_API = test_config['EXTERNAL']['re3data_api']

    assert len(temp_preprocessor.re3repositories.keys()) == 0  # this is initialized why?

    temp_preprocessor.retrieve_datacite_re3repos(RE3DATA_API, DATACITE_API_REPO, isDebug)

    assert temp_preprocessor.re3repositories
    assert len(temp_preprocessor.re3repositories.keys()) > 10
    #print(len(temp_preprocessor.re3repositories.keys()))


def test_preprocessor_metadata_standards(test_config, temp_preprocessor):
    """Test preprocessor if retrieve_metadata_standards works"""

    METADATACATALOG_API = test_config['EXTERNAL']['metadata_catalog']

    assert not temp_preprocessor.metadata_standards

    temp_preprocessor.retrieve_metadata_standards(METADATACATALOG_API, isDebug)

    assert temp_preprocessor.metadata_standards
    print(temp_preprocessor.metadata_standards)
    assert len(temp_preprocessor.metadata_standards.keys()) > 10


def test_preprocessor_retrieve_linkedvocabs(test_config, temp_preprocessor):
    """Test preprocessor if retrieve_linkedvocabs works"""

    LOV_API = test_config['EXTERNAL']['lov_api']
    LOD_CLOUDNET = test_config['EXTERNAL']['lod_cloudnet']
    assert not temp_preprocessor.linked_vocabs

    temp_preprocessor.retrieve_linkedvocabs(lov_api=LOV_API, lodcloud_api=LOD_CLOUDNET, isDebugMode=isDebug)

    assert temp_preprocessor.linked_vocabs
    assert len(temp_preprocessor.linked_vocabs) > 10


def test_preprocessor_rest(test_config, temp_preprocessor):
    """Test preprocessor if others works"""

    METADATACATALOG_API = test_config['EXTERNAL']['metadata_catalog']

    assert not temp_preprocessor.default_namespaces

    temp_preprocessor.retrieve_default_namespaces()
    assert len(temp_preprocessor.default_namespaces) > 10
