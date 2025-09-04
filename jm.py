#!/usr/bin/python3

import os,sys
import ast
import re
from datetime import datetime
import argparse
import xml.etree.ElementTree as ET
import subprocess


work_path = os.path.abspath(__file__).rsplit("/", 1)[0]
if not os.path.exists(work_path+'/JM'):
    work_path = os.path.dirname(os.path.realpath(sys.executable))
sys.path.append(sys.path[0])
sys.path[0] = work_path+'/src'

from jmcomic import *

def parse_args(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('-n',type=int,default=0, help='只下载本子的前几章')
    parser.add_argument('--not-dl', action='store_true', help='查看本子信息，不下载')
    parser.add_argument('jmid', nargs='+', help='禁漫本子的车号')
    return parser.parse_args(argv)

def get_title(title: str):
    cmd = f'{work_path}/title.sh "{title}"'
    a = subprocess.getstatusoutput(cmd)
    if a[0] == 0:
        titles = [el.strip() for el in a[1].split('/')]
        return ' '.join(titles)
    else:
        return title

def get_writer(title: str, writer: str):
    cmd = f'{work_path}/writer.sh "{title}"'
    a = subprocess.getstatusoutput(cmd)
    if a[0] == 0:
        return a[1].split('\n')
    else:
        return [writer,writer]

def write_comic_info_new(path,title,name,tags,writer,number,count,time_s,summary):

    tree = ET.parse('ComicInfo.xml')
    root = tree.getroot()

    dt = datetime.fromtimestamp(time_s)
    year = str(dt.year)
    month = str(dt.month)
    day = str(dt.day)
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="Title"]').set('default', title)
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="Series"]').set('default', name)
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="Tags"]').set('default', ','.join(tags))
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="Writer"]').set('default', writer)
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="PageCount"]').set('default', count)
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="Number"]').set('default', number)
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="Year"]').set('default', year)
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="Month"]').set('default', month)
    root.find('.//{http://www.w3.org/2001/XMLSchema}element[@name="Day"]').set('default', day)

    tree.write(path+'/ComicInfo.xml', encoding='utf-8', xml_declaration=True)

def write_comic_info(path,id,title,name,tags,writer,number,count,time_s,summary,works):
    dt = datetime.fromtimestamp(time_s)
    _year = str(dt.year)
    _month = str(dt.month)
    _day = str(dt.day)

    if '中文' in tags:
        _language = 'zh'
    elif '日文' in tags:
        _language = 'ja'
    elif '英文' in tags:
        _language = 'en'
    else:
        _language = ''

    _id = id
    _title = get_title(title)
    _local_title = get_title(name)
    _number = number
    _count = count
    _writer,_penciller = get_writer(title, writer)
    _tags = ','.join(tags)
    _summary = summary
    _works = ','.join(works)
    with open(path+'/ComicInfo.xml', "w") as f:
        f.write(f"<?xml version='1.0' encoding='utf-8'?>\n")
        f.write(f"<ComicInfo>\n")
        f.write(f"\t<Title>{_title}</Title>\n") #章节标题
        f.write(f"\t<LocalizedSeries>{_local_title}</LocalizedSeries>\n") #本地化名称
        f.write(f"\t<SeriesSort>{_id}</SeriesSort>\n") #排序名称
        f.write(f"\t<Number>{_number}</Number>\n") #章节序号
        f.write(f"\t<Count>{_number}</Count>\n") #发布状态 用卷或章节数目判断
        f.write(f"\t<Volume></Volume>\n") #卷
        f.write(f"\t<Summary>{_summary}</Summary>\n") #简介
        f.write(f"\t<Publisher>JmComic</Publisher>\n") #出版社
        f.write(f"\t<Imprint>Comic</Imprint>\n") #压印

        f.write(f"\t<Year>{_year}</Year>\n") #年
        f.write(f"\t<Month>{_month}</Month>\n") #月
        f.write(f"\t<Day>{_day}</Day>\n") #日

        f.write(f"\t<Writer>{_writer}</Writer>\n") #作者
        f.write(f"\t<Penciller>{_penciller}</Penciller>\n") #笔名
        f.write(f"\t<Inker>{_writer}</Inker>\n") #上墨师
        f.write(f"\t<Colorist>{_writer}</Colorist>\n") #上色
        f.write(f"\t<Letterer>{_writer}</Letterer>\n") #嵌字师
        f.write(f"\t<CoverArtist>{_writer}</CoverArtist>\n") #封面设计
        f.write(f"\t<Editor>{_writer}</Editor>\n") #编辑
        f.write(f"\t<Translator>{_writer}</Translator>\n") #翻译

        f.write(f"\t<Genre>色情</Genre>\n") #流派
        f.write(f"\t<Tags>{_tags}</Tags>\n") #标签
        f.write(f"\t<Web>https://18comic.vip/album/{_id}</Web>\n") #web链接
        f.write(f"\t<PageCount>{_count}</PageCount>\n") #系列数
        f.write(f"\t<LanguageISO>{_language}</LanguageISO>\n") #语言
        f.write(f"\t<Format></Format>\n") #Special
        f.write(f"\t<SeriesGroup>{_works}</SeriesGroup>\n") #系列组的集合
        f.write(f"\t<AgeRating>R18+</AgeRating>\n") #年龄分级
        f.write(f"\t<GTIN></GTIN>\n") #ISBN
        f.write(f"</ComicInfo>\n")

def dl_album(option, client, id, dl, num=0, copy_path=''):

    # 本子实体类
    album: JmAlbumDetail = client.get_album_detail(id)

    print(f'本子描述: {album.description}')
    print(f'本子推荐: {album.related_list}')
    print(f'作品: {album.works}')
    for i in range(len(album)):
        if num != 0 and i > num:
            break
        photo = album.create_photo_detail(i)
        photo = client.get_photo_detail(photo.id)
        print(f'章节ID: {photo.id}')
        print(f'章节序号: {i}')
        print(f'章节标题: {photo.name}')
        print(f'作者: {photo.author}')
        print(f'Tags: {photo.tags}')
        print(f'图片数目: {len(photo)}')
        print(f'上架日期: {photo.year}-{photo.month}-{photo.day}')

        tags = ast.literal_eval(f'{photo.tags}')
        save_dir = option.decide_image_save_dir(photo)

        write_comic_info(save_dir,
            id=f'{photo.id}',
            title=f'{album.name}',
            name=f'{photo.name}',
            tags=tags,
            writer=f'{photo.author}',
            number=f'{i+1}',
            count=f'{len(album)}',
            time_s=photo.addtime,
            summary=f'{album.description}',
            works=album.works
        )
        if not dl:
            continue

        option.download_photo(photo.id)

        name = get_title(photo.name)
        cmd=f'cd {save_dir} && rm -f ../"{name}.cbz" && zip -q -r ../"{name}.cbz" *'
        print(f'Runing: {cmd}')
        os.system(cmd)

        if copy_path != '':
            print(f"拷贝到: {copy_path}")
            new_dir=copy_path+f'/{album.id}/{photo.id}'
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            cmd=f'cp {save_dir}/../"{name}.cbz" {save_dir}/ComicInfo.xml "{new_dir}/"'
            print(f'Runing: {cmd}')
            os.system(cmd)

def main():
    print('Runing: ' + ' '.join(sys.argv))
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} album_id')
        sys.exit(1)


    args = parse_args(sys.argv[1:])
    need_download = not args.not_dl
    photo_num = args.n
    copy_path=''
    jmalbum = []
    jmalbum_len=len(args.jmid)
    if jmalbum_len > 1:
        if os.path.exists(args.jmid[len(args.jmid)-1]):
            copy_path=args.jmid[len(args.jmid)-1]
            jmalbum_len-=1

    for i in range(jmalbum_len):
        re_str1=f'^[jJ][Mm][0-9]+$'
        re_str2=f'^[0-9]+$'
        if not re.search(re_str1, args.jmid[i]) and not re.search(re_str2, args.jmid[i]):
            print(f"你的参数'{args.jmid[i]}'有误")
            sys.exit(1)

        jmalbum.append(args.jmid[i])

    option_file = work_path + "/option.yml"
    option = create_option_by_file(option_file)

    client = option.new_jm_client()

    for album in jmalbum:
        dl_album(option, client, album, need_download, photo_num, copy_path)

if __name__ == '__main__':
    sys.exit(main())
