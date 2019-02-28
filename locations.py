# -*- coding: utf-8 -*-

import re
from os import path
import traceback
import codecs
import json
from imp import load_source
PlayerInfoAPI = load_source('PlayerInfoAPI','./plugins/PlayerInfoAPI.py')

'''
MC一般指令染色规则
找不到、报错、数值后缀（L/b/d/f）：§c，红色
坐标、数值、字符串：§a，绿色
数据：§6，金色
括号、玩家、物品或结构名称：§f，白色
属性名称：§b，水色
'''

helpmsg = '''---------MCD 路标插件---------
命令帮助如下:
!!loc help -显示帮助消息
!!loc add <独特名字> <x> <y> <z> <地狱：-1，主世界：0，末地：1> - 加入一个路标
名字不能为 add, del, help
tips:为方便搜索，可以加入别名，尽量使用全称，如“僵尸猪人塔/僵尸猪人农场/刷金塔”，而不仅是“猪人塔”
!!loc add <独特名字> here - 加入自己所处位置、维度的路标
!!loc del <独特关键词> - 删除路标，要求全字匹配
!!loc <名字> - 搜索坐标，返回所有匹配项
!!loc - 列出所有坐标
--------------------------------'''

locations = []

if path.exists('locations.json'):
    with codecs.open('locations.json', 'r', encoding='utf-8') as jfile:
        locations = json.load(jfile)
else:
    with codecs.open('locations.json', 'w', encoding='utf-8') as jfile:
        jfile.write('[]')

dimName = {'0': u'主世界', '1': u'末地', '-1': u'地狱'}

def jsonFormatPosition(loc):
    return {
        'text': u'§a[' + str(loc['pos']['x']) + u', ' + str(loc['pos']['y']) + u', ' + str(loc['pos']['z']) + u']§r ', 
        'clickEvent': {'action': 'run_command', 'value': '/tp @p ' + str(loc['pos']['x']) + ' ' + str(loc['pos']['y']) + ' ' + str(loc['pos']['z'])}, 
        'hoverEvent': {'action': 'show_text',   'value': u'点击以传送到坐标处'}
    }

def tellComplexed(server, selector, content):
    server.execute('tellraw ' + selector + ' ' + json.dumps(content, ensure_ascii=False, encoding='utf-8').encode('utf-8'))

def posConvert(loc, dim):
    if dim == loc['dim'] or loc['dim'] == 1:
        return loc
    if loc['dim'] == 0 and dim == -1:
        newLoc = {'name': loc['name'], 'pos': {'x': int(loc['pos']['x'] / 8), 'y': int(loc['pos']['y'] / 8), 'z': int(loc['pos']['z'] / 8)}, 'dim': -1}
        return newLoc
    if loc['dim'] == -1 and dim == 0:
        newLoc = {'name': loc['name'], 'pos': {'x': int(loc['pos']['x'] * 8), 'y': int(loc['pos']['y'] * 8), 'z': int(loc['pos']['z'] * 8)}, 'dim': 0}
        return newLoc
    
def highlight(string, kwrd):
    lowerIndex = string.find(kwrd)
    upperIndex = lowerIndex + len(kwrd)
    newStr = string[:upperIndex] + u'§r' + string[upperIndex:]
    newStr = newStr[:lowerIndex] + u'§c' + newStr[lowerIndex:]
    return newStr

def update():
    with codecs.open('locations.json', 'w', encoding='utf-8') as jfile:
        json.dump(locations, jfile, ensure_ascii=False, encoding='utf-8', sort_keys=True, indent=2, separators=(',', ': '))

def printHelp(server, info):
    for line in helpmsg.splitlines():
        server.tell(info.player, line)

def add(server, info):
    args = unicode(info.content, encoding='utf-8').split(' ')
    for loc in locations:
        if args[2] == loc['name']:
            server.tell(info.player, '§c已存在同名的路标§r')
            server.tell(info.player, locToStr(loc).encode('utf-8'))
            return
    newLoc = {
    'name': args[2],
    'pos': {
        'x': int(args[3]),
        'y': int(args[4]),
        'z': int(args[5])
    },
    'dim': int(args[6])
    }
    locations.append(newLoc)
    tellComplexed(server, '@a', [
        {'text': u'添加了路标 ' + newLoc['name'] + ' '}, 
        jsonFormatPosition(newLoc),
        {'text': u'§a' + dimName[str(newLoc['dim'])] + u'§r'}
        ])
    
def addHere(server, info):
    args = unicode(info.content, encoding='utf-8').split(' ')
    for loc in locations:
        if args[2] == loc['name']:
            server.tell(info.player, '§c已存在同名的路标§r')
            server.tell(info.player, locToStr(loc).encode('utf-8'))
            return
    player_info = PlayerInfoAPI.getPlayerInfo(server, info.player)
    newLoc = {
    'name': args[2], 
    'pos': {
        'x': player_info['Pos'][0],
        'y': player_info['Pos'][1],
        'z': player_info['Pos'][2]
    },
    'dim': player_info['Dimension']
    }
    locations.append(newLoc)
    tellComplexed(server, '@a', [
        {'text': u'添加了路标 ' + newLoc['name'] + ' '}, 
        jsonFormatPosition(newLoc),
        {'text': u'§a' + dimName[str(newLoc['dim'])] + u'§r'}
        ])

def delete(server, info):
    args = unicode(info.content, encoding='utf-8').split(' ')
    for loc in locations:
        if args[2] == loc['name']:
            locations.remove(loc)
            tellComplexed(server, '@a', [
                {'text': info.player + u' 删除了路标 ' + loc['name'] + ' '},
                jsonFormatPosition(loc),
                {'text': u'§a' + dimName[str(loc['dim'])] + u'§r'}
                ])
            return
    server.tell(info.player, '§c找不到名称匹配的路标，请使用§r !!loc §c查看所有路标！§r')

def get(server, info):
    args = unicode(info.content, encoding='utf-8').split(' ')
    kwrd = args[1]
    count = 0
    for loc in locations:
        if loc['name'].find(kwrd) > -1:
            tellComplexed(server, info.player, [
                {'text': highlight(loc['name'],kwrd) + ' '},
                jsonFormatPosition(loc),
                {'text': u'§a' + dimName[str(loc['dim'])] + u'§r'}
                ])
            count = count + 1
    if count == 0:
        server.tell(info.player, '§c找不到名称匹配的路标，请使用§r !!loc §c查看所有路标！§r')
    else:
        server.tell(info.player, '共找到了 §a' + str(count) + ' 个匹配路标')

def getAll(server, info):
    count = 0
    for loc in locations:
        tellComplexed(server, info.player, [
            {'text': loc['name'] + ' '},
            jsonFormatPosition(loc),
            {'text': u'§a' + dimName[str(loc['dim'])] + u'§r'}
            ])
        count = count + 1
    server.tell(info.player, '共有 §a' + str(count) + ' 个路标')

def onServerInfo(server, info):
  if info.isPlayer == 1:
    if info.content.startswith('!!loc'):
      try:
        if re.match("^!!loc help$",info.content):
          printHelp(server, info)
        elif re.match("^!!loc add \S+ -?\d+ -?\d+ -?\d+ (-1|0|1)$",info.content):
          add(server, info)
          update()
        elif re.match("^!!loc add \S+ here$",info.content):
          addHere(server, info)
          update()
        elif re.match("^!!loc del \S+$",info.content):
          delete(server, info)
          update()
        elif re.match("^!!loc \S+$",info.content):
          get(server, info)
        elif re.match("^!!loc$",info.content):
          getAll(server, info)
        else:
          server.tell(info.player, '§c输入无效，使用§r !!loc help §c查看帮助信息§r')
      except:
        lines = traceback.format_exc().splitlines()
        for l in lines:
          server.say(l)
