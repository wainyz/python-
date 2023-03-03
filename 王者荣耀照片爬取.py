# -*- coding:utf-8 _*-
"""
============================
@author:笨磁
@time:2023/1/16:14:27
@email:Player_simple@163.com
@IDE:PyCharm
============================
"""

import re
import requests
import os
import asyncio
import aiofiles
import aiohttp
import time
from multiprocessing import Pool
from functools import partial

def get_namelist(url,headers):
    response = requests.get(url,headers)
    assert response.status_code < 300, 'main response erro'
    #print(response.text)
    response.encoding='utf-8'
    name_find = re.compile(r'"ename": (\d+?),[^.]\W*?"cname": "(\w+?)"')
    # tips:这个正则表达式我调试了很久,最后原因是复制粘贴也会出错,最好先看响应文件原格式,并且不认\n需要用[^.]表示
    name_list = name_find.findall(response.text)
    assert len(name_list) != 0,'find name erro'
    return name_list

def guss_name_url(ename):
    url = f'https://pvp.qq.com/web201605/herodetail/{ename}.shtml'
    return url

async def download_img(one_one,one,headers,i):
    if os.path.exists(f'./王者荣耀照片皮肤图片/{one[0] + one[1]}/{str(i) + one_one}.jpg'):
        return
    pf_url = f'http://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{one[0]}/{one[0]}-bigskin-{i}.jpg'
    async with aiohttp.ClientSession() as client:
        async with await client.get(pf_url,headers=headers) as img:
            assert img.status < 300, f'{one_one} 请求失败 status_code:{img.status}'
            data = await img.read()
            async with aiofiles.open(f'./王者荣耀照片皮肤图片/{one[0] + one[1]}/{str(i) + one_one}.jpg', 'wb') as file:
                await file.write(data)
            print(f'{one_one}下载完毕!')

async def download_imgs(one,headers):
    if os.path.exists(f'./王者荣耀照片皮肤图片/{one[0] + one[1]}') == False:
        os.mkdir(f'./王者荣耀照片皮肤图片/{one[0] + one[1]}')
    async with aiohttp.ClientSession as client_:
        async with await client_.get(guss_name_url(one[0]), headers=headers) as response:
            assert response.status < 300, 'guss_url response erro'
            ## 3. 分析html,解析出该英雄的皮肤名称和皮肤图片url地址
            # print(response.text)
            pf_finder = re.compile(r'["|]?([^"|]+?)&\d*?["|]')
            data_ = await response.text(encoding='gbk')
            pf_name_url_list = pf_finder.findall(data_)
            assert len(pf_name_url_list) > 0, 'pf find erro'
            # print(pf_name_url_list)
            print(f"正在下载{one[1]}皮肤... ...")
            i = 1
            ## 4. 遍历所有皮肤地址,判断该皮肤是否已经下载,否则下
            tasks = []
            for one_one in pf_name_url_list:
                c = download_img(one_one, one, headers, i)
                task = asyncio.ensure_future(c)
                tasks.append(task)
                i += 1
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            print(f'{one[1]}皮肤全部下载完毕! 当前进度:{len(os.listdir("./王者荣耀照片皮肤图片"))}/{len(name_list)}')

def pool_down_name_list(len_name_list,headers,one):
    if os.path.exists(f'./王者荣耀照片皮肤图片/{one[0] + one[1]}') == False:
        os.mkdir(f'./王者荣耀照片皮肤图片/{one[0] + one[1]}')
    #headers = {
    #        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.52"
    #}
    response = requests.get(guss_name_url(one[0]), headers)
    assert response.status_code < 300, 'guss_url response erro'
    response.encoding = 'gbk'
    ## 3. 分析html,解析出该英雄的皮肤名称和皮肤图片url地址
    # print(response.text)
    pf_finder = re.compile(r'["|]?([^"|]+?)&\d*?["|]')
    pf_name_url_list = pf_finder.findall(response.text)
    assert len(pf_name_url_list) > 0, 'pf find erro'
    # print(pf_name_url_list)
    print(f"正在下载{one[1]}皮肤... ...")
    i = 1
    ## 4. 遍历所有皮肤地址,判断该皮肤是否已经下载,否则下载
    """ 同步操作
    for one_one in pf_name_url_list:            
        if os.path.exists(f'./王者荣耀照片皮肤图片/{one[0]+one[1]}/{str(i)+one_one}.jpg'):
            continue
        pf_url = f'http://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{one[0]}/{one[0]}-bigskin-{i}.jpg'
        img = requests.get(pf_url,headers)
        assert img.status_code < 300,f'{one_one} 请求失败 status_code:{img.status_code}'
        with open(f'./王者荣耀照片皮肤图片/{one[0]+one[1]}/{str(i)+one_one}.jpg','wb') as file:
            file.write(img.content)
            file.close()
        i += 1
        print(f'{one_one}下载完毕!')
    print(f'{one[1]}皮肤全部下载完毕! 当前进度:{len(os.listdir("./王者荣耀照片皮肤图片"))}/{len(name_list)}')
    """
    tasks = []
    for one_one in pf_name_url_list:
        c = download_img(one_one, one, headers, i)
        task = asyncio.ensure_future(c)
        tasks.append(task)
        i += 1
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    print(f'{one[1]}皮肤全部下载完毕! 当前进度:{len(os.listdir("./王者荣耀照片皮肤图片"))}/{len_name_list}')

if __name__=='__main__':
    #获取英雄名list
    start_time = time.time()
    url = 'https://pvp.qq.com/web201605/herodetail/544.shtml'
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.52"}
    """
    # 测试代码
    response = requests.get(url,headers=headers)
    response.encoding = 'gbk'
    assert response.status_code < 300 ,'response erro'
    print(response.text)
    """

    main_url = 'https://pvp.qq.com/web201605/js/herolist.json'
    # 1. 先得英雄名字列表,从json文件中获取
    name_list = get_namelist(main_url,headers)
    #print(name_list)
    ## 1. 创建图片总文件夹 ./王者荣耀照片皮肤图片
    if os.path.exists('./王者荣耀照片皮肤图片') == False:
        os.mkdir('./王者荣耀照片皮肤图片')
    ## 2. 根据英雄找到对应的英雄界面url并发送get请求解码得到html数据
    partials = partial(pool_down_name_list,len(name_list),headers)
    pool = Pool(4)
    pool.map(partials,name_list)
    pool.close()
    pool.join()
    """
    for one in name_list:
        if os.path.exists(f'./王者荣耀照片皮肤图片/{one[0]+one[1]}') ==False:
            os.mkdir(f'./王者荣耀照片皮肤图片/{one[0]+one[1]}')
        response = requests.get(guss_name_url(one[0]),headers)
        assert response.status_code<300,'guss_url response erro'
        response.encoding='gbk'
        ## 3. 分析html,解析出该英雄的皮肤名称和皮肤图片url地址
        #print(response.text)
        pf_finder = re.compile(r'["|]?([^"|]+?)&\d*?["|]')
        pf_name_url_list = pf_finder.findall(response.text)
        assert len(pf_name_url_list)>0 ,'pf find erro'
        #print(pf_name_url_list)
        print(f"正在下载{one[1]}皮肤... ...")
        i = 1
        ## 4. 遍历所有皮肤地址,判断该皮肤是否已经下载,否则下载
        \""" 同步操作
        for one_one in pf_name_url_list:            
            if os.path.exists(f'./王者荣耀照片皮肤图片/{one[0]+one[1]}/{str(i)+one_one}.jpg'):
                continue
            pf_url = f'http://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{one[0]}/{one[0]}-bigskin-{i}.jpg'
            img = requests.get(pf_url,headers)
            assert img.status_code < 300,f'{one_one} 请求失败 status_code:{img.status_code}'
            with open(f'./王者荣耀照片皮肤图片/{one[0]+one[1]}/{str(i)+one_one}.jpg','wb') as file:
                file.write(img.content)
                file.close()
            i += 1
            print(f'{one_one}下载完毕!')
        print(f'{one[1]}皮肤全部下载完毕! 当前进度:{len(os.listdir("./王者荣耀照片皮肤图片"))}/{len(name_list)}')
        \"""
        tasks= []
        for one_one in pf_name_url_list:
            c = download_img(one_one,one,headers,i)
            task = asyncio.ensure_future(c)
            tasks.append(task)
            i += 1
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        print(f'{one[1]}皮肤全部下载完毕! 当前进度:{len(os.listdir("./王者荣耀照片皮肤图片"))}/{len(name_list)}')
        """
    print(f'皮肤全部下载完毕! 总共耗时:{time.time()-start_time} s')