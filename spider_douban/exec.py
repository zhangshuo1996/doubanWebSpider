import os
import json
import requests
import pandas as pd
from lxml import etree


def xls():
    pd.read_xml()


def get_book_list():
    """
    获取书名列表
    :return:
    """
    cur_path = get_cur_path()
    xls_file_path = os.path.join(cur_path, '..', 'xls_file/', 'book_list.xlsx')

    # 读取工作簿和工作簿中的工作表
    data_frame = pd.read_excel(xls_file_path,
                               sheet_name='book')
    mat = data_frame.values
    book_list = []
    for row in mat:
        book_list.append(row[1])
    # print(book_list)
    return book_list


def get_cur_path():
    """
    获取当前路径
    :return:
    """
    # print(os.path.dirname(os.path.abspath("__file__")))
    # print(os.path.pardir)
    # print(os.path.join(os.path.dirname("__file__"), os.path.pardir))
    # print(os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir)))
    return os.path.dirname(os.path.abspath("__file__"))


def spider_douban(blst):
    """

    :param blst:
    :return:
    """
    rlst = []
    for bn in blst:
        res = {}
        r = requests.get('https://book.douban.com/j/subject_suggest?q={0}'.format(bn))
        rj = json.loads(r.text)
        # 对rj进行一下验证和筛选
        html = requests.get(rj[0]['url'])  # 之后再考虑多个返回值的验证
        con = etree.HTML(html.text)
        bname = con.xpath('//*[@id="wrapper"]/h1/span/text()')[0]  # 和bn比较
        res['bname_sq'] = bn
        res['bname'] = bname
        res['dbid'] = rj[0]['id']  # 不需要存url，存id就够了
        # 这部分取到info就够了，之后再用高级方法去匹配需要的元素，目前对应不对
        binfo = con.xpath('//*[@id="info"]')
        cc = con.xpath('//*[@id="info"]/text()')
        res.update(getBookInfo(binfo, cc))  # 调用上面的函数处理binfo
        bmark = con.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()')[0]
        if bmark == '  ':
            bits = con.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/text()')[0]
            if bits == '评价人数不足':
                res['评分'] = ''
                res['评价人数'] = '评价人数不足'
            else:
                res['评分'] = ''
                res['评价人数'] = ''
        else:
            res['评分'] = bmark.replace(' ', '')
            bmnum = con.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/span/text()')[0]
            res['评价人数'] = bmnum
        rlst.append(res)
    return rlst


def getBookInfo(binfo, cc):
    """

    :param binfo:
    :param cc:
    :return:
    """
    i = 0
    rss = {}
    k = ''
    v = ''
    f = 0
    clw = []
    for c in cc:
        if '\n' in c:
            if '\xa0' in c:
                clw.append(c)
        else:
            clw.append(c)

    for m in binfo[0]:
        if m.tag == 'span':
            mlst = m.getchildren()
            if len(mlst) == 0:
                k = m.text.replace(':', '')
                if '\xa0' in clw[i]:
                    f = 1  # 需要m.tag=='a'下的值
                else:
                    v = clw[i].replace('\n', '').replace(' ', '')
                i += 1
            elif len(mlst) > 0:  # 下面有子span 一种判断是m.attrib=={} 不够精确
                for n in mlst:
                    if n.tag == 'span':
                        k = n.text.replace('\n', '').replace(' ', '')  # 不至于下面还有span，懒得用递归了
                    elif n.tag == 'a':
                        v = n.text.replace('\n', '').replace(' ', '')

        elif m.tag == 'a':
            if f == 1:  # 是否可以不用这个if
                v = m.text.replace('\n', '').replace(' ', '')
                f = 0
        elif m.tag == 'br':
            if k == '':
                print(i, 'err')
            else:
                rss[k] = v
        else:
            print(m.tag, i)
    return rss


if __name__ == '__main__':
    book_list = get_book_list()
    spider_douban(book_list)
