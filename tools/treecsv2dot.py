#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2014 speirs <vvebmaster _at_ codereading.com>
# Copyright 2010-2012 Shin-ya Murakami <murashin _at_ gfd-dennou.org>
#
# ツリー構造を表現したcsvファイルからdotファイルを構成するスクリプト.
# Python バージョン.
#
# ver 0.1
# 
#
# dotファイルはDOT言語で書かれたファイルのこと. 
# graphvizがこれを解釈し, グラフに変換する. 
# graphvizおよびDOT言語に関しては以下のURLを参照のこと.
#    - 公式サイト http://www.graphviz.org/
#    - 日本語チュートリアル http://homepage3.nifty.com/kaku-chan/graphviz/
#
# csvファイルの形式:
#    - 値がコンマを含む場合は値を""で囲む.
#      このときコンマと値の間に空白を入れないこと
#    - 値は"を含まないと仮定する.
#    - csvファイルはUTF-8である
#    - 先頭に # はコメント行を表す
#    - 空白のみの行は読み飛ばされる
#    - ある位置から行末まで, 空要素が続く場合は読み飛ばされる
#    - ファイル先頭から見て, 最初のゼロでない最前列要素をタイトルとみなす.
#
# 例:
#   ----ここから----
#   テスト              <- タイトル
#   
#   a,b,c,d
#    , , ,e
#    , ,f,g
#    ,h,i
#   j,k
#    ,l,m
#   ----ここまで----
# これは, 次のようなツリー構造を表す
#
#    a -- b -- c -- d
#          \    \
#           \    -- e
#            - f -- g
#    j -- k
#     \
#      -- l -- m
#

import csv
import sys

# 設定
id_prefix = 'id' # nodeのシンボルのprefix
id_digits = 4    # nodeの数の桁数

# 値に現れる " のエスケープ
def escape_dq(s):
   return s.replace('"','\"')
#end def escape_dq

# nodeのシンボルを定義
def id(nid):
   global id_prefix, id_digits
   return "%s%s" % (id_prefix, str(nid).rjust(id_digits, '0'))
#end def id

# nodeを定義する出力
def define_node(nid, label):
#   result = "  %s [ label = \"{%s|%s\l}\" ];" % (id(nid), escape_dq(label), id(nid))
   result = "  %s [ label = \"%s\" ];" % (id(nid), escape_dq(label))
   print result
   nid += 1
   return nid
#end def define_node

# node間の関係を定義する出力
def define_relation(id_a, id_b):
    print "  %s -> %s;" % (id(id_a), id(id_b))
#end def define_relation

# ヘッダとフッタの定義
def print_header(title):
    print """digraph generated_data {
  // 全体設定 //
  graph [ // fontname = "Helvetica-Oblique",
  label = "\\n%s",
  rankdir = TB ];
  node [ shape = record ];
""" % escape_dq(title)
#end def print_header

def print_footer():
    print """
}
"""
#end def print_footer

# 引数チェック
try:
    inputfile = sys.argv[1]
except:
    print "error: need an argument of input file."
    sys.exit(1)

# メインの処理
nid = 0          # 何番のidまで使ったかを表す数
is_first_line = True

# pathは, CSVファイルの中身が表現しているtree構造において, 
# rootから, あるbranch/leafまでのnodeを順に並べた配列である. 
path = []

csv_reader = csv.reader(open(inputfile, 'rb'))

for row in csv_reader:
    # 空行の読み飛ばし
    if len(filter(None, row)) == 0:
        continue
    # コメント行の読み飛ばし
    if filter(None, row)[0]:
        if filter(None, row)[0].startswith('#'):
            continue

    # 最初に登場するゼロでない要素をタイトルとする
    if is_first_line:
       title = filter(None, row)[0]
       print_header(title)  # ヘッダを出力
       is_first_line = False
       continue
  
    cur = 0  # path配列において注目するインデックスの位置

    for col in row:
        if col and col.strip():
            col = col.strip()  # 前後の空白を除去

        if col:
            # path配列の, indexがcur以降の要素を削除
            if cur == 0:
                path = []
            else:
                path = path[0:cur]
            path.append(nid) # pathの末尾にnidを追加
            nid = define_node(nid, col) # ノードの定義
            if len(path) > 1:
                # path配列の要素が2個以上の場合は, 関係を定義
                define_relation(path[-2], path[-1])
        cur += 1 # 現在位置更新

print_footer()
