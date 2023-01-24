import graphviz
import requests
from graphviz import Graph

# python-dataanalytics
project_name = "python-dataanalytics"

# 意図的に除外したいページ名
exceptpages = ["Go RonYan", "Scrapboxの使い方", "Top", "戦術"]

# scrapboxのページからタイトル一覧をとる
title_list = requests.get(
    "https://scrapbox.io/api/pages/{}/search/titles".format(project_name),
)

# 今あるページのリストを作成
titles = [
    page["title"] for page in title_list.json() if not page["title"] in exceptpages
]

# タイトルをもとにScrapboxのURL取得
hrefs = ["https://scrapbox.io/{0}/{1}".format(project_name, t) for t in titles]

# 各ページのリンクのリストを作成
links = set(
    [
        l
        for page in title_list.json()
        if not page["title"] in exceptpages
        for l in page["links"]
    ]
)

# ハッシュタグを取得
import re

# #をクエリで検索。%23が#のこと
hash_res = requests.get(
    "https://scrapbox.io/api/pages/{}/search/query?q=%23".format(project_name)
)

hashtags = [
    (r["title"], l)
    for r in hash_res.json()["pages"]
    if not r["title"] in exceptpages
    for l in r["lines"]
    if l[1:] in links
]

# edgesを作成
edges = [
    (page["title"], l)
    for page in title_list.json()
    if not page["title"] in exceptpages
    for l in page["links"]
    if l in titles and not "#{}".format(l) in [h[1] for h in hashtags]
]

# notExistEdgesを作成
notExistEdges = [
    (page["title"], l)
    for page in title_list.json()
    if not page["title"] in exceptpages
    for l in page["links"]
    if not l in titles and not "#{}".format(l) in [h[1] for h in hashtags]
]

# edgeを作成するfunctionを定義
def create_edges(edges, cname, w):
    for f, t in edges:
        dot.edge(f, t, color=cname, weight=str(w), penwidth="2.5")


# DOT形式で記述してくれるオブジェクトを宣言
# node , edgeをpropertyに記述していけばDOT形式に変換してくれるし、jupyter上で表示してくれる。
dot = graphviz.Graph(
    filename=project_name,
    comment=project_name,
    format="svg",
    strict=True,
    engine="fdp",
    graph_attr={"splines": "polyline"},
    node_attr={"color": "pink", "style": "filled", "shape": "rect"},
    edge_attr={"arrowhead": "dot", "arrowtail": "dot"},
)

dot.attr(rankdir="LR", stylesheet="graph.css")
dot.attr("node", {"class": "selectable"})
dot.attr("edge", {"class": "selectableLine"})


# nodeを描画
for t, l in zip(titles, hrefs):
    dot.node(t, target=l, href=l, level="max", color="lightblue")

# ハッシュタグを描画　ついでにグループも一緒にしておく（dotの時に有効)
for t, h in hashtags:
    dot.node(
        h,
        level="min",
        group=h,
        color="gold",
        shape="ellipse",
        href="https://scrapbox.io/{0}/{1}".format(project_name, h.replace("#", "")),
        target="https://scrapbox.io/{0}/{1}".format(project_name, h.replace("#", "")),
    )
    dot.node(t, group=h)

# 未作成のページを描画
for t, n in notExistEdges:
    dot.node(
        n,
        href="https://scrapbox.io/{0}/{1}".format(project_name, n.replace("#", "")),
        target="https://scrapbox.io/{0}/{1}".format(project_name, n.replace("#", "")),
    )

# []リンクのedgeを描画
create_edges(edges, "royalblue", 9)

# #リンクのedgeを描画
create_edges(hashtags, "orange", 5)

# 未作成ページのedgeを描画
create_edges(notExistEdges, "tomato", 1)

# render
# dot.render()

dot