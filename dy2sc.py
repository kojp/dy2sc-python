import sys
import re
import pyperclip
import webbrowser
import urllib.request

###出力のしかたを3つのうちから選択###
#クリップボードに自動でコピーする=0
#コンソールに表示する=1
#自動でブラウザを開いて、自動でScrapboxに記入する=2
output=0

###Scrapboxのページタイトルとなる文字列にMarkdown／数式記法が含まれているとき、
###それらをScrapbox記法に置換せずに取り除くかどうかを選択
#取り除く=0 取り除かない=1
firstline=0

###ブラウザにてScrapboxの新規ページ（空白ページ）を自動で開くかどうかを選択###
#開かない=0 開く=1
browseropen=1

###プロジェクトURLの指定###
#上掲の行で output=2 としたり browseropen=1 としている場合は必須。
project_url='YOUR_PROJECT_URL'

###標準入力から文字列を取得###
lines = sys.stdin.readlines()

###出力方法として「ブラウザで自動で書き込む」（output=2）を選択しているときに、
###ページタイトルになる部分（＝配列linesの先頭要素）に半角アンダーバーが含まれる場合は、
###ページタイトルを空白に置き換える。
###本来のページタイトルは1行後ろ（＝Scrapboxの本文の1行目の位置）へ移る。
###（ページタイトル内のアンダーバーを半角スペースに置換するScrapboxの仕様への対処）
if '_' in lines[0]:
	if output==2:
		title='new'
	#output=2でなく且つアンダーバーある場合は、
	#Dynalistからエクスポートした内容の1行目をページタイトルとし、
	#それをコンテンツ部分から除く
	else:
		title=lines[0].replace('\n','')	
		lines.pop(0)
else:
	#ページタイトルに半角アンダーバーが含まれない場合は
	#Dynalistからエクスポートした内容の1行目をページタイトルとし、
	#それをコンテンツ部分から除く
	title=lines[0].replace('\n','')	
	lines.pop(0)

###ページタイトルにハイパーリンクor画像記法が含まれる場合に置換
#[リンクテキスト／画像タイトル]の中が0文字である場合
title=re.sub(r'!?\[\]\((https?://[\w/:%#\$&\?\(\)~\.=\+\-]+)\)',r'[\1]',title)
#[リンクテキスト／画像タイトル]の中が1文字以上ある場合
title=re.sub(r'!?\[([^\]]*)\]\((https?://[\w/:%#\$&\?\(\)~\.=\+\-]+)\)',r'[\1 \2]',title)

###ページタイトルに含まれるハッシュタグを置換
# @や#が行頭にある場合
title=re.sub(r'(^@|^#)','#',title)
# @や#がスペースの後ろにある場合
title=re.sub(r'([ 　])[@#]',r'\1#',title)

###ページタイトルに含まれる半角記号を置換。
###Scrapboxへの記入を自動で行う場合のみ。
if output==2:
	title=title.replace('%','%25')
	title=title.replace('#','%23')
	title=title.replace('^','%5E')
	title=title.replace('\\','%5c')  #バックスラッシュ
	title=title.replace('|','%7c')
	title=title.replace('`','%60')
	title=title.replace('[','%5B')
	title=title.replace(']','%5D')
	title=title.replace('{','%7B')
	title=title.replace('}','%7D')
	title=title.replace(';','%3B')	
	title=title.replace(':','%3A')
	title=title.replace(',','%2C')
	title=title.replace('?','%3F')
	title=title.replace('/','%2F')
	title=title.replace(' ','_')  #半角スペース

###ページタイトルにMarkdown／数式が含まれているとき、
###それらをScrapbox記法に置換せずに取り除く。
if firstline==0:
	#強調（**hoge**）を除去
	title=re.sub(r'\*\*(\*+|[^*]+)\*\*',r'\1',title)
	#イタリック（__hoge__）を除去
	title=re.sub(r'\_\_(\_+|[^_]+)\_\_',r'\1',title)
	#取り消し線（~~hoge~~）を除去
	title=re.sub(r'\~\~(\~+|[^~]+)\~\~',r'\1',title)
	#数式記法（$$〜$$）を除去
	title=re.sub(r'\$\$([^$$]+)\$\$',r'\1',title)

####ページタイトルにMarkdown／数式が含まれているとき、
###それらをScrapbox記法に置換する
if firstline==1:
	#強調（**hoge**）をScrapbox記法の太字（[* hoge]）へ置換
	title=re.sub(r'\*\*(\*+|[^*]+)\*\*',r'[* \1]',title)
	#イタリック（__hoge__）をScrapbox記法へ置換
	title=re.sub(r'\_\_(\_+|[^_]+)\_\_',r'[/ \1]',title)
	#取り消し線（~~hoge~~）をScrapbox記法へ置換
	title=re.sub(r'\~\~(\~+|[^~]+)\~\~',r'[- \1]',title)
	#数式記法（$$〜$$）をScrapbox記法へ置換
	title=re.sub(r'\$\$([^$$]+)\$\$',r'[$ \1]',title)

###ページタイトル内の日時記法は常に置換する
title=re.sub(r'\!\(([0-9]{4}\-[0-9]{2}\-[0-9]{2}( [0-9]{2}:[0-9]{2})*)\)',r'\1',title)

###コンテンツを格納した配列を文字列に変換
content='|||'.join(lines)   #区切りは|||

###コンテンツ部分の処理
#ハイパーリンクと画像記法の置換
#[リンクテキスト／画像タイトル]の中が0文字である場合
content=re.sub(r'!?\[\]\((https?://[\w/:%#\$&\?\(\)~\.=\+\-]+)\)',r'[\1]',content)
#[リンクテキスト／画像タイトル]の中が1文字以上ある場合
content=re.sub(r'!?\[([^\]]*)\]\((https?://[\w/:%#\$&\?\(\)~\.=\+\-]+)\)',r'[\1 \2]',content)

#強調（**hoge**）をScrapbox記法の太字（[* hoge]）へ置換
content=re.sub(r'\*\*(\*+|[^*]+)\*\*',r'[* \1]',content)

#イタリック（__hoge__）をScrapbox記法へ置換
content=re.sub(r'\_\_(\_+|[^_]+)\_\_',r'[/ \1]',content)

#取り消し線（~~hoge~~）をScrapbox記法へ置換
content=re.sub(r'\~\~(\~+|[^~]+)\~\~',r'[- \1]',content)

#日時記法の置換
content=re.sub(r'\!\(([0-9]{4}\-[0-9]{2}\-[0-9]{2}( [0-9]{2}:[0-9]{2})*)\)',r'\1',content)

#ハッシュタグ用の @を #へ置換
content=re.sub(r'(\|\|\|)*(\s*)@',r'\1\2#',content)  #「@」が各行の行頭にある場合
content=re.sub(r'([ 　])@',r'\1#',content)  #「@」がスペースの後ろにある場合

#数式記法（$$〜$$）をScrapbox記法へ置換
content=re.sub(r'\$\$([^$$]+)\$\$',r'[$ \1]',content)

#Dynalistの余分なインデントを除去
content=re.sub(r'\s{4}',' ',content)

###区切りを除去###
content=content.replace('|||','')

###出力###
#クリップボードへ自動でコピーする
if output==0:
	content=title + '\n' + content
	pyperclip.copy(content)
	print('【置換してクリップボードへコピーしました】')

#置換済みのテキストをコンソールに表示する
if output==1:
	print('===== 置換済みテキスト START =====')
	print(title)
	print(content)
	print('===== END =====')

#ブラウザを開いて、Scrapboxに自動で記入する
if output==2:
	webbrowser.open('https://scrapbox.io/'+project_url+'/' + title + '?body=' + urllib.parse.quote(content))
	#ブラウザで新規ページを開く機能はこの場合は余分なので開かないようにする
	browseropen=0

#ブラウザで新規ページを開く
if browseropen==1:
	webbrowser.open('https://scrapbox.io/'+project_url+'/new')
